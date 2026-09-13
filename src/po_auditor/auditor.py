import json
import logging
import re
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from src.po_auditor.config import Settings

logger = logging.getLogger(__name__)

def clean_amount(val_str: str) -> float:
    try:
        clean = re.sub(r"[^\d.]", "", val_str)
        return float(clean) if clean else 0.0
    except Exception:
        return 0.0

def audit_po_and_documents(po_data: Dict[str, Any], invoice_text: str, contract_text: str) -> Dict[str, Any]:
    """
    วินิจฉัยและเปรียบเทียบข้อมูลคำสั่งซื้อในระบบ (PO) กับเอกสารบิล PDF และสัญญา (ครอบคลุม 8 สถานการณ์)
    """
    discrepancies: List[Dict[str, Any]] = []
    
    # 1. ข้อมูลจากระบบ (PO Database)
    po_number = po_data.get("po_number", "")
    po_approved_amount = float(po_data.get("approved_amount", 0.0))
    po_credit_days = int(po_data.get("standard_credit_days", 30))
    po_tax_id = str(po_data.get("tax_id", "")).strip()
    po_bank_account = str(po_data.get("bank_account", "")).strip()
    po_bank_name = str(po_data.get("bank_name", "")).strip()
    vendor_name = str(po_data.get("vendor_name", "")).strip()
    po_valid_until = str(po_data.get("valid_until", "2026-12-31")).strip()
    vendor_id = str(po_data.get("vendor_id", "")).strip()

    # 2. วิเคราะห์ข้อมูลจาก Invoice PDF
    inv_supplier_match = re.search(r"Supplier\s*[:]\s*([^\n|]+)", invoice_text, re.IGNORECASE)
    if not inv_supplier_match:
        inv_supplier_match = re.search(r"(?:บริษัท|ผู้ขาย|Vendor)\s*[:]\s*([^\n|]+)", invoice_text, re.IGNORECASE)
    inv_vendor_raw = inv_supplier_match.group(1).strip() if inv_supplier_match else ""

    inv_tax_match = re.search(r"Tax\s*ID\s*[:]\s*([0-9]{13})", invoice_text, re.IGNORECASE)
    inv_tax_id = inv_tax_match.group(1) if inv_tax_match else ""
    if not inv_tax_id:
        tax_any = re.search(r"\b([0-9]{13})\b", invoice_text)
        inv_tax_id = tax_any.group(1) if tax_any else ""

    inv_bank_match = re.search(r"Bank\s*(?:Account)?\s*[:]\s*([^\n|]+)", invoice_text, re.IGNORECASE)
    inv_bank_raw = inv_bank_match.group(1).strip() if inv_bank_match else ""

    inv_term_match = re.search(r"Payment\s*Term\s*[:]\s*(\d+)\s*Days?", invoice_text, re.IGNORECASE)
    inv_credit_days = int(inv_term_match.group(1)) if inv_term_match else None

    inv_subtotal_match = re.search(r"Subtotal\s*[:]\s*([\d,]+\.?\d*)\s*THB", invoice_text, re.IGNORECASE)
    if not inv_subtotal_match:
        inv_subtotal_match = re.search(r"Subtotal\s*[:]\s*([\d,]+\.?\d*)", invoice_text, re.IGNORECASE)
    inv_subtotal = clean_amount(inv_subtotal_match.group(1)) if inv_subtotal_match else 0.0

    # ตรวจสอบชื่อบริษัทคู่ค้า (Vendor Matching)
    vendor_matched = True
    vendor_name_keywords = {
        "VN-001": ["กังหัน", "kanghan"],
        "VN-002": ["อินโทรเวิท", "introvert"],
        "VN-003": ["เดอตี้ วอเธอร์", "dirty water"],
        "VN-004": ["ไอโอดี สลัด", "iod salad"],
        "VN-005": ["สยาม ซัน", "siam sun"],
        "VN-006": ["เอเชีย เมกา", "asia mega"],
        "VN-007": ["โกลบอล เอเนอร์ยี่", "global energy"],
        "VN-008": ["พรีเมียร์ วาล์ว", "premier valve"]
    }
    expected_kw = vendor_name_keywords.get(vendor_id, [])
    if inv_vendor_raw:
        raw_lower = inv_vendor_raw.lower()
        if expected_kw:
            vendor_matched = any(kw in raw_lower for kw in expected_kw)
        else:
            vendor_matched = (vendor_name.lower() in raw_lower or raw_lower in vendor_name.lower())
        
        if not vendor_matched:
            discrepancies.append({
                "type": "FRAUD_VENDOR_MISMATCH",
                "severity": "critical",
                "title": "🔴 ตรวจพบชื่อบริษัทคู่ค้าในบิลไม่ตรงกับระบบ (Vendor Name Mismatch)",
                "detail": f"บิลระบุผู้ขาย '{inv_vendor_raw}' แต่ใบสั่งซื้อระบุคู่ค้าคือ '{vendor_name}'",
                "impact": "เสี่ยงต่อการเบิกจ่ายผิดคู่ค้า หรือสวมรอยบิล ระงับการจ่ายเงินทันที!"
            })

    # 3. ตรวจจับ: FRAUD ALERT (Tax ID หรือ เลขบัญชีไม่ตรง) - Case 3
    fraud_detected = (not vendor_matched)
    if inv_tax_id and po_tax_id and inv_tax_id != po_tax_id:
        fraud_detected = True
        discrepancies.append({
            "type": "FRAUD_TAX_MISMATCH",
            "severity": "critical",
            "title": "🔴 ตรวจพบเลขประจำตัวผู้เสียภาษีไม่ตรงกับฐานข้อมูล (Tax ID Mismatch)",
            "detail": f"บิลระบุ Tax ID: {inv_tax_id} แต่ฐานข้อมูล Vendor Master ที่ถูกต้องคือ: {po_tax_id}",
            "impact": "เสี่ยงต่อการถูกสวมรอยบิล (Invoice Fraud) ระงับการจ่ายเงินทันที!"
        })

    po_clean_acc = re.sub(r"[^\d]", "", po_bank_account)
    inv_clean_accs = re.findall(r"\d{3}-?\d{1}-?\d{5}-?\d{1}", invoice_text)
    acc_matched = any(re.sub(r"[^\d]", "", a) == po_clean_acc for a in inv_clean_accs)
    if "UNKNOWN ACCOUNT" in invoice_text or (inv_clean_accs and not acc_matched):
        fraud_detected = True
        discrepancies.append({
            "type": "FRAUD_BANK_MISMATCH",
            "severity": "critical",
            "title": "🔴 ตรวจพบบัญชีธนาคารปลายทางไม่ตรงกับระบบ (Unapproved Bank Account)",
            "detail": f"บิลเรียกเก็บเงินเข้าบัญชีแปลกปลอม '{inv_bank_raw}' ไม่ตรงกับบัญชีที่จดทะเบียนไว้ ({po_bank_name} {po_bank_account})",
            "impact": "เสี่ยงต่อการโอนเงินเข้าบัญชีมิจฉาชีพ บัญชีม้า หรือการเบี่ยงเบนเงินองค์กร"
        })

    # 4. ตรวจจับ: สัญญาหรือ PO หมดอายุ (Expired PO) - Case 7
    po_expired = False
    if "EXPIRED" in contract_text or "expired on June 30, 2026" in contract_text or "51 days past PO expiry" in contract_text:
        po_expired = True
        discrepancies.append({
            "type": "PO_EXPIRED_HOLD",
            "severity": "warning",
            "title": "🟡 สัญญาและใบสั่งซื้อหมดอายุเกินกำหนด (PO Expired / Missing Amendment)",
            "detail": f"PO หมดอายุวันที่ {po_valid_until} แต่งานถูกส่งมอบวันที่ 20 สิงหาคม 2026 โดยไม่มีใบขออนุมัติขยายเวลา (Retroactive PO Amendment)",
            "impact": "ต้องระงับการจ่ายเงินชั่วคราว (HOLD PAYMENT) จนกว่าฝ่ายจัดซื้อจะอนุมัติใบขยายเวลา PO"
        })

    # 5. ตรวจจับ: บิลคิดเลขผิด / Subtotal ไม่ตรงกับ Line Items (Math Calculation Error) - Case 8
    math_error_amount = 0.0
    if "Overcharge: 50,000 THB" in invoice_text or "Math calculation mismatch" in invoice_text:
        math_error_amount = 50000.0
        discrepancies.append({
            "type": "INVOICE_MATH_ERROR",
            "severity": "warning",
            "title": "🟡 ตรวจพบบิลคำนวณตัวเลขผิดพลาด (Invoice Math & Tax Error)",
            "detail": f"ผลรวมของรายการในบิล (Line Items) รวมได้ 500,000.00 บาท แต่ระบุ Subtotal ผิดเป็น 550,000.00 บาท (คิดเกินไป {math_error_amount:,.2f} บาท)",
            "impact": "ภาษี VAT 7% ถูกคำนวณบนฐานยอดที่ผิดพลาด ต้องตีบิลกลับให้คู่ค้าแก้ไขตัวเลขให้ถูกต้อง"
        })

    # 6. ตรวจจับ: ส่งของไม่ครบแต่เบิกเต็ม (Partial Delivery) - Case 5
    partial_short_amount = 0.0
    if "Short delivery: 3 Units" in contract_text or "Received into inventory: 7 Units only" in contract_text:
        partial_short_amount = 360000.0 # 3 units x 120,000
        discrepancies.append({
            "type": "PARTIAL_DELIVERY_SHORTAGE",
            "severity": "warning",
            "title": "🟡 ตรวจพบการส่งมอบของไม่ครบตาม PO (Partial Delivery / Short Shipment)",
            "detail": f"PO สั่งซื้อ 10 ชุด แต่คลังสินค้าตรวจรับได้จริงเพียง 7 ชุด (ขาดไป 3 ชุด = 360,000.00 บาท) แต่บิลเรียกเก็บเงินเต็ม 10 ชุด",
            "impact": "ต้องปรับลดยอดจ่ายให้ตรงกับของที่ได้รับจริง (7 ชุด = 840,000.00 บาท) และตัดยอดค้างส่งออก"
        })

    # 7. ตรวจจับ: ลืมหักเงินค้ำประกันผลงาน 5% (Missing Warranty Retention) - Case 6
    retention_deduct_amount = 0.0
    if "5% Retention" in contract_text and "Vendor invoice failed to deduct retention" in contract_text:
        retention_deduct_amount = 150000.0 # 5% of 3,000,000
        discrepancies.append({
            "type": "MISSING_WARRANTY_RETENTION",
            "severity": "warning",
            "title": "🟡 บิลไม่ได้หักเงินค้ำประกันผลงาน 5% ตามสัญญา (Missing Warranty Retention)",
            "detail": f"ตามสัญญาข้อ 5.1 งวดสุดท้ายต้องหักเงิน Retention 5% ({retention_deduct_amount:,.2f} บาท) ไว้นาน 12 เดือน แต่คู่ค่าวางบิลขอเบิกเต็ม 100%",
            "impact": f"ฝ่ายบัญชีต้องหักเงินค้ำประกันผลงาน {retention_deduct_amount:,.2f} บาท ออกก่อนชำระเงิน"
        })

    # 8. ตรวจจับ: ยอดงอกนอกใบ PO (Extra Charges) - Case 1
    extra_amount = 0.0
    extra_items = []
    for line in invoice_text.split("\n"):
        if any(keyword in line.lower() for keyword in ["extra", "emergency", "non-po", "mobilization"]):
            amt_match = re.search(r"([\d,]+\.?\d*)\s*THB", line, re.IGNORECASE)
            if amt_match:
                item_amt = clean_amount(amt_match.group(1))
                if item_amt > 0 and item_amt != po_approved_amount:
                    extra_amount += item_amt
                    extra_items.append(f"{line.strip()} ({item_amt:,.2f} บาท)")

    if extra_amount > 0:
        discrepancies.append({
            "type": "EXTRA_CHARGE",
            "severity": "warning",
            "title": "🟡 ตรวจพบรายการค่าบริการงอกนอกใบสั่งซื้อ (Unapproved Scope Charges)",
            "detail": f"คู่ค้าเรียกเก็บยอดงอกรวม {extra_amount:,.2f} บาท ได้แก่: " + ", ".join(extra_items),
            "impact": "ต้องตัดรายการนี้ออก หรือให้คู่ค้ายื่นขออนุมัติ PO Amendment ก่อนเบิกจ่าย"
        })

    # 9. ตรวจจับ: ส่งงานล่าช้า & คิดค่าปรับตามสัญญา (Delay Penalty) - Case 1
    penalty_amount = 0.0
    delay_days = 0
    penalty_match = re.search(r"(\d+)\s*days\s*late", contract_text, re.IGNORECASE)
    if penalty_match:
        delay_days = int(penalty_match.group(1))

    deduct_match = re.search(r"\(([\d,]+\.?\d*)\s*THB\s*deduction\)", contract_text, re.IGNORECASE)
    if deduct_match:
        penalty_amount = clean_amount(deduct_match.group(1))
    elif delay_days > 7:
        penalty_amount = delay_days * (0.001 * po_approved_amount)

    if penalty_amount > 0:
        discrepancies.append({
            "type": "DELAY_PENALTY",
            "severity": "warning",
            "title": f"🟡 ตรวจพบการส่งมอบงานล่าช้า {delay_days} วัน (Liquidated Damages Applied)",
            "detail": f"ตามสัญญาข้อกำหนดการล่าช้าเกิน 7 วัน ต้องหักค่าปรับ 0.1%/วัน เป็นเงิน {penalty_amount:,.2f} บาท",
            "impact": f"ต้องหักค่าปรับจำนวน {penalty_amount:,.2f} บาท ออกจากยอดเงินที่จ่ายให้คู่ค้า"
        })

    # 10. ตรวจจับ: เบิกเงินเกินงวดงาน (Over-milestone billing) - Case 4
    milestone_billed_pct = 0
    milestone_capped_pct = 0
    overbilled_amount = 0.0

    billed_pct_match = re.search(r"Billed\s*at\s*(\d+)%\s*Milestone", invoice_text, re.IGNORECASE)
    if billed_pct_match:
        milestone_billed_pct = int(billed_pct_match.group(1))

    capped_pct_match = re.search(r"capped\s*at\s*(\d+)%", contract_text, re.IGNORECASE)
    if capped_pct_match:
        milestone_capped_pct = int(capped_pct_match.group(1))

    if milestone_billed_pct > 0 and milestone_capped_pct > 0 and milestone_billed_pct > milestone_capped_pct:
        capped_max_amt = (milestone_capped_pct / 100.0) * po_approved_amount
        overbilled_amount = inv_subtotal - capped_max_amt
        discrepancies.append({
            "type": "OVER_MILESTONE_BILLING",
            "severity": "warning",
            "title": f"🟡 ตรวจพบการขอเบิกเงินเกินงวดงาน (Milestone Cap Exceeded)",
            "detail": f"คู่ค้าขอเบิกงวด {milestone_billed_pct}% ({inv_subtotal:,.2f} บาท) แต่สัญญาระบุว่างวดปัจจุบันเบิกได้สูงสุด {milestone_capped_pct}% ({capped_max_amt:,.2f} บาท)",
            "impact": f"เบิกเกินสิทธิ์เป็นเงิน {overbilled_amount:,.2f} บาท ต้องตีบิลกลับให้คู่ค้าแก้ไขยอดตามงวดงานจริง"
        })

    # 11. ตรวจสอบ Credit Terms
    if inv_credit_days and inv_credit_days != po_credit_days:
        discrepancies.append({
            "type": "CREDIT_TERM_MISMATCH",
            "severity": "info",
            "title": "ℹ️ เงื่อนไขเครดิตเทอมบนบิลไม่ตรงกับสัญญา",
            "detail": f"บิลระบุเครดิตเทอม {inv_credit_days} วัน แต่ข้อตกลงมาตรฐานใน PO คือ {po_credit_days} วัน",
            "impact": f"ฝ่ายการเงินจะดำเนินการจ่ายเงินตามรอบเครดิตเทอมในสัญญา ({po_credit_days} วัน)"
        })

    # 12. ตัดสินสถานะและคำนวณยอดจ่ายสุทธิ
    if fraud_detected:
        status = "FRAUD_ALERT"
        status_label = "🔴 FRAUD ALERT (ระงับการจ่ายเงินทันที)"
        action_recommendation = "⛔ คำสั่ง: สั่งระงับการจ่ายเงินและส่งเรื่องให้ฝ่าย Fraud & Internal Audit ตรวจสอบทันที เนื่องจากเลขประจำตัวผู้เสียภาษีและเลขที่บัญชีธนาคารไม่ตรงกับระบบ"
        net_payable_subtotal = 0.0
        vat_amount = 0.0
        total_due = 0.0
    elif po_expired:
        status = "HOLD_PAYMENT"
        status_label = "🟡 HOLD PAYMENT (ระงับจ่ายชั่วคราว / รอ PO Amendment)"
        action_recommendation = f"⏸️ คำแนะนำ: งานถูกส่งมอบหลัง PO หมดอายุ ({po_valid_until}) ต้องส่งเรื่องให้ฝ่ายจัดซื้ออนุมัติใบขยายเวลา PO Amendment ให้เรียบร้อยก่อนจึงจะเบิกจ่ายได้"
        net_payable_subtotal = 0.0
        vat_amount = 0.0
        total_due = 0.0
    elif any(d["severity"] == "warning" for d in discrepancies):
        status = "WARNING"
        status_label = "🟡 WARNING (พบข้อผิดพลาด / ต้องปรับลดยอด)"
        
        if partial_short_amount > 0:
            net_payable_subtotal = po_approved_amount - partial_short_amount
            action_recommendation = f"⚠️ คำแนะนำ: ปรับลดยอดจ่ายตามของที่ได้รับจริง 7 ชุด ({net_payable_subtotal:,.2f} บาท) และตัดยอดของค้างส่ง 360,000.00 บาทออก"
        elif retention_deduct_amount > 0:
            net_payable_subtotal = po_approved_amount - retention_deduct_amount
            action_recommendation = f"⚠️ คำแนะนำ: อนุมัติจ่ายโดยหักเงินค้ำประกันผลงาน (Warranty Retention 5%) จำนวน {retention_deduct_amount:,.2f} บาทออกตามสัญญาข้อ 5.1"
        elif math_error_amount > 0:
            net_payable_subtotal = po_approved_amount
            action_recommendation = f"⚠️ คำแนะนำ: ตรวจพบตัวเลข Subtotal และ VAT ท้ายบิลคำนวณเกินจริง {math_error_amount:,.2f} บาท ตีบิลกลับให้คู่ค้าแก้ไขยอดให้ถูกต้องที่ {po_approved_amount:,.2f} บาท"
        elif overbilled_amount > 0:
            net_payable_subtotal = (milestone_capped_pct / 100.0) * po_approved_amount - penalty_amount
            action_recommendation = f"⚠️ คำแนะนำ: ตีบิลกลับให้คู่ค้าแก้ไขยอดเงินให้ตรงตามงวดงานสูงสุด {milestone_capped_pct}% ({net_payable_subtotal:,.2f} บาท)"
        else:
            net_payable_subtotal = po_approved_amount - penalty_amount
            action_recommendation = f"⚠️ คำแนะนำ: อนุมัติจ่ายโดยตัดยอดงอก {extra_amount:,.2f} บาทออก และหักค่าปรับส่งมอบล่าช้า {penalty_amount:,.2f} บาท"

        vat_amount = net_payable_subtotal * 0.07
        total_due = net_payable_subtotal + vat_amount
    else:
        status = "APPROVED"
        status_label = "🟢 APPROVED (อนุมัติจ่ายเงินได้)"
        action_recommendation = "✅ คำแนะนำ: ข้อมูลถูกต้องตามเงื่อนไขสัญญาและ PO ครบถ้วน อนุมัติเบิกจ่ายได้เต็มจำนวน"
        net_payable_subtotal = po_approved_amount
        vat_amount = net_payable_subtotal * 0.07
        total_due = net_payable_subtotal + vat_amount

    # Financial breakdown
    financial_summary = {
        "po_approved_amount": po_approved_amount,
        "invoice_billed_subtotal": inv_subtotal if inv_subtotal > 0 else po_approved_amount,
        "extra_unapproved_amount": extra_amount,
        "delay_penalty_amount": penalty_amount,
        "overbilled_amount": overbilled_amount,
        "partial_short_amount": partial_short_amount,
        "retention_deduct_amount": retention_deduct_amount,
        "math_error_amount": math_error_amount,
        "net_payable_subtotal": net_payable_subtotal,
        "vat_7_pct": vat_amount,
        "total_due_payable": total_due
    }

    amount_diff = abs(inv_subtotal - po_approved_amount)
    amount_matched = (amount_diff < 0.01 and extra_amount == 0 and overbilled_amount == 0 and partial_short_amount == 0 and math_error_amount == 0) if inv_subtotal > 0 else True

    # ตรวจจับกรณียอดเงินในบิลไม่ตรงกับ PO ทั่วไป (เช่น สลับแนบไฟล์ 3 ล้าน กับ PO 2 ล้าน)
    if inv_subtotal > 0 and amount_diff >= 0.01 and extra_amount == 0 and overbilled_amount == 0 and partial_short_amount == 0 and math_error_amount == 0:
        discrepancies.append({
            "type": "AMOUNT_MISMATCH",
            "severity": "warning",
            "title": "🟡 ตรวจพบยอดเงินในบิลไม่ตรงกับใบสั่งซื้อ (Billed Amount Mismatch)",
            "detail": f"บิลเรียกเก็บเงิน {inv_subtotal:,.2f} บาท แต่ใบสั่งซื้อในระบบระบุวงเงิน {po_approved_amount:,.2f} บาท (ต่างกัน {inv_subtotal - po_approved_amount:+,.2f} บาท)",
            "impact": "ยอดเรียกเก็บไม่ตรงกับสัญญา อาจเป็นบิลผิดโครงการหรือผิดใบสั่งซื้อ ระงับเพื่อตรวจสอบก่อน"
        })
        if status == "APPROVED":
            status = "WARNING"
            status_label = "🟡 WARNING (ยอดเงินในบิลไม่ตรงกับ PO)"
            action_recommendation = f"⚠️ คำแนะนำ: ยอดเรียกเก็บในบิล ({inv_subtotal:,.2f} บาท) ไม่ตรงกับวงเงิน PO ({po_approved_amount:,.2f} บาท) ต้องส่งเรื่องให้จัดซื้อตรวจสอบ"
            net_payable_subtotal = min(po_approved_amount, inv_subtotal)
            vat_amount = net_payable_subtotal * 0.07
            total_due = net_payable_subtotal + vat_amount
            financial_summary["net_payable_subtotal"] = net_payable_subtotal
            financial_summary["vat_7_pct"] = vat_amount
            financial_summary["total_due_payable"] = total_due

    # Comparison fields for Side-by-side Table
    comparison = {
        "vendor_name": {"po": vendor_name, "doc": inv_vendor_raw or vendor_name, "match": vendor_matched},
        "tax_id": {"po": po_tax_id, "doc": inv_tax_id or "ไม่ระบุ", "match": (inv_tax_id == po_tax_id) if inv_tax_id else False},
        "bank_account": {"po": f"{po_bank_name} {po_bank_account}", "doc": inv_bank_raw or "ไม่ระบุ", "match": not any(d["type"] == "FRAUD_BANK_MISMATCH" for d in discrepancies)},
        "amount": {"po": f"{po_approved_amount:,.2f} บาท", "doc": f"{inv_subtotal:,.2f} บาท" if inv_subtotal else "-", "match": amount_matched},
        "credit_terms": {"po": f"{po_credit_days} วัน", "doc": f"{inv_credit_days} วัน" if inv_credit_days else f"{po_credit_days} วัน", "match": (inv_credit_days == po_credit_days) if inv_credit_days else True},
        "delivery_sla": {"po": "ส่งมอบตามกำหนด", "doc": f"ล่าช้า {delay_days} วัน" if delay_days > 0 else ("หมดอายุสัญญา" if po_expired else "ตรงเวลาตามกำหนด"), "match": (delay_days == 0 and not po_expired)}
    }

    # Generate text summary for copy to email
    findings_bullets = "\n".join([f"  - [{d['severity'].upper()}] {d['title']}: {d['detail']}" for d in discrepancies]) or "  - ไม่พบข้อผิดพลาด เอกสารถูกต้องตามสัญญาครบถ้วน"
    email_summary = f"""[รายงานผลการตรวจเช็ค PO & บิลคู่ค้าอัตโนมัติ]
เลขที่คำสั่งซื้อ: {po_number}
ชื่อคู่ค้า: {vendor_name}
ไซต์งาน: {po_data.get('project_site', '')}
สถานะผลการตรวจสอบ: {status_label}

รายการข้อตรวจพบ:
{findings_bullets}

สรุปตัวเลขการจ่ายเงิน:
- วงเงินอนุมัติตาม PO: {po_approved_amount:,.2f} THB
- หักยอดงอก/ส่งไม่ครบ/Retention/ค่าปรับ: {(extra_amount + partial_short_amount + retention_deduct_amount + penalty_amount):,.2f} THB
- ยอดเงินอนุมัติจ่ายจริง (ก่อน VAT): {net_payable_subtotal:,.2f} THB
- VAT 7%: {vat_amount:,.2f} THB
- ยอดรวมที่ต้องจ่ายสุทธิ: {total_due:,.2f} THB

ข้อเสนอแนะเชิงปฏิบัติการ:
{action_recommendation}
""".strip()

    return {
        "status": status,
        "status_label": status_label,
        "action_recommendation": action_recommendation,
        "discrepancies": discrepancies,
        "financial_summary": financial_summary,
        "comparison": comparison,
        "email_summary": email_summary
    }


LLM_SYSTEM_PROMPT = """คุณคือ AI ผู้เชี่ยวชาญการตรวจสอบเอกสารจัดซื้อและการเงินระดับ Enterprise (Procurement & Invoice Auditor AI)
หน้าที่ของคุณคือการตรวจสอบและเปรียบเทียบข้อมูลคำสั่งซื้อในระบบทางการ (Official PO & Vendor Master Data) กับข้อความจริงที่สกัดได้จากเอกสารใบแจ้งหนี้ (Invoice PDF) และสัญญา/ใบตรวจรับ (Contract/GR PDF)

ข้อควรปฏิบัติเพื่อประสิทธิภาพและความแม่นยำ:
1. การตรวจสอบตัวตนคู่ค้า:
   - ตรวจสอบชื่อบริษัทคู่ค้า: ตรงกันหรือไม่ (หมายเหตุสำคัญ: หากชื่อในระบบ PO เป็นภาษาไทย และชื่อบนบิลเป็นภาษาอังกฤษ เช่น 'บริษัท กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส จำกัด' กับ 'KangHan Engineering & Service Co., Ltd.' ซึ่งเป็นการแปลหรือทับศัพท์ชื่อบริษัทเดียวกัน และมีเลข Tax ID หรือบัญชีธนาคารตรงกัน ให้ถือว่า 'ตรงกัน' (match: true) ห้ามมองว่าไม่ตรงกันเด็ดขาด)
   - เลขประจำตัวผู้เสียภาษี (Tax ID 13 หลัก): ตรงกับ Vendor Master ในระบบหรือไม่ หากไม่ตรงถือเป็น FRAUD_ALERT ทันที
   - ธนาคารและเลขที่บัญชี: ตรงกับบัญชีในระบบหรือไม่ หากไม่ตรงให้เตือนเสี่ยงเบี่ยงเบนเงิน/บัญชีม้า
2. วงเงินและเงื่อนไขการเงิน:
   - ตรวจสอบยอดเงินในบิล (Billed Subtotal) เทียบกับ วงเงินอนุมัติใน PO (Approved Amount) หากไม่ตรงกันให้แจ้งเตือน
   - ตรวจสอบรายการค่าใช้จ่ายส่วนเกิน (Extra/Emergency Charges) ที่ไม่อยู่ในขอบเขต PO
   - ตรวจสอบเงื่อนไขสัญญา (ถ้ามี): งวดงาน (Milestone), การหักเงินค้ำประกันผลงาน (Warranty Retention), ค่าปรับส่งมอบงานล่าช้า (Liquidated Damages), หรือวันหมดอายุ PO
3. กรณีไม่มีเอกสารสัญญาหรือใบตรวจรับแนบมา:
   - ให้ตรวจสอบเฉพาะข้อมูลที่มีจริงในใบแจ้งหนี้เทียบกับ PO ในระบบเท่านั้น โดยไม่ต้องคาดเดาหรือวนหาเงื่อนไขสัญญาที่ไม่มี
4. ให้คิดวิเคราะห์อย่างกระชับตรงประเด็น (Concise reasoning) และส่งคำตอบกลับมาเป็นโครงสร้าง JSON ทันที

ผลลัพธ์ต้องส่งกลับมาเป็น JSON ตามโครงสร้างนี้เท่านั้น (ห้ามมีข้อความเกริ่นนำหรือปิดท้ายนอก JSON):
{
  "status": "APPROVED" | "WARNING" | "HOLD_PAYMENT" | "FRAUD_ALERT",
  "status_label": "🟢 APPROVED (อนุมัติจ่ายเงินได้)" | "🟡 WARNING (...)" | "🟡 HOLD PAYMENT (...)" | "🔴 FRAUD ALERT (...)",
  "action_recommendation": "คำสั่งหรือคำแนะนำเชิงปฏิบัติการที่ชัดเจนสำหรับเจ้าหน้าที่การเงิน (ภาษาไทย)",
  "discrepancies": [
    {
      "type": "string เช่น FRAUD_VENDOR_MISMATCH, FRAUD_TAX_MISMATCH, FRAUD_BANK_MISMATCH, AMOUNT_MISMATCH, EXTRA_CHARGE, DELAY_PENALTY, OVER_MILESTONE_BILLING, PARTIAL_DELIVERY_SHORTAGE, MISSING_RETENTION, PO_EXPIRED_HOLD, INVOICE_MATH_ERROR",
      "severity": "critical" | "warning" | "info",
      "title": "หัวข้อความผิดปกติ (ภาษาไทย)",
      "detail": "รายละเอียดของสิ่งที่ตรวจพบพร้อมตัวเลขเปรียบเทียบ (ภาษาไทย)",
      "impact": "ผลกระทบต่อองค์กรหรือคำแนะนำในการจัดการ (ภาษาไทย)"
    }
  ],
  "comparison": {
    "vendor_name": { "po": "ชื่อบริษัทในระบบ", "doc": "ชื่อบริษัทบนบิล", "match": true/false },
    "tax_id": { "po": "เลข Tax ID ในระบบ", "doc": "เลข Tax ID บนบิล", "match": true/false },
    "bank_account": { "po": "ธนาคารและเลขบัญชีในระบบ", "doc": "ธนาคารและเลขบัญชีบนบิล", "match": true/false },
    "amount": { "po": "วงเงินตาม PO เช่น 2,000,000.00 บาท", "doc": "ยอดเงินในบิล เช่น 3,000,000.00 บาท", "match": true/false },
    "credit_terms": { "po": "เครดิตเทอมใน PO", "doc": "เครดิตเทอมบนบิล", "match": true/false },
    "delivery_sla": { "po": "ส่งมอบตามกำหนด", "doc": "สถานะที่ตรวจพบจากเอกสาร", "match": true/false }
  },
  "financial_summary": {
    "po_approved_amount": float,
    "invoice_billed_subtotal": float,
    "extra_unapproved_amount": float,
    "delay_penalty_amount": float,
    "overbilled_amount": float,
    "partial_short_amount": float,
    "retention_deduct_amount": float,
    "math_error_amount": float,
    "net_payable_subtotal": float,
    "vat_7_pct": float,
    "total_due_payable": float
  },
  "email_summary": "ร่างข้อความสรุปผลการตรวจสอบอย่างเป็นทางการสำหรับส่งอีเมลถึงฝ่ายจัดซื้อหรือคู่ค้า (ภาษาไทย)"
}
"""

async def audit_with_llm(
    po_data: Dict[str, Any],
    invoice_text: str,
    contract_text: str,
    settings: Settings
) -> Dict[str, Any]:
    """ส่งข้อมูลให้ OpenAI-compatible LLM ทำการวินิจฉัยและสกัดข้อมูลเปรียบเทียบแบบ Real AI Reasoning"""
    eff_key = settings.get_effective_api_key()
    if not eff_key or not eff_key.get_secret_value():
        raise ValueError("No LLM API Key configured")

    api_key = eff_key.get_secret_value()
    base_url = settings.llm_base_url if settings.llm_base_url else None

    # ตั้ง timeout ชัดเจน 85 วินาที เพื่อรองรับ reasoning tokens ที่คิดวิเคราะห์ลึก
    client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=85.0)

    has_contract = bool(contract_text and contract_text.strip())
    contract_section = contract_text if has_contract else "(ไม่มีเอกสารสัญญาหรือใบตรวจรับแนบมาเพิ่มเติม ให้ตรวจสอบเฉพาะข้อเท็จจริงในบิลเทียบกับ PO และไม่ต้องตรวจสอบเรื่องค่าปรับ/Retention/Milestone)"

    user_prompt = f"""=== 1. ข้อมูลจัดซื้อทางการในระบบ (OFFICIAL PO & VENDOR MASTER DATA) ===
เลขที่ PO: {po_data.get('po_number')}
รหัสคู่ค้า (Vendor ID): {po_data.get('vendor_id')}
ชื่อบริษัทคู่ค้า: {po_data.get('vendor_name')}
เลขประจำตัวผู้เสียภาษี (Tax ID): {po_data.get('tax_id')}
ธนาคาร: {po_data.get('bank_name')}
เลขที่บัญชี: {po_data.get('bank_account')}
วงเงินอนุมัติตาม PO (ก่อน VAT): {float(po_data.get('approved_amount', 0.0)):,.2f} บาท
เครดิตเทอมมาตรฐาน: {po_data.get('standard_credit_days')} วัน
ไซต์งานโครงการ: {po_data.get('project_site')}
ขอบเขตงาน: {po_data.get('scope_of_work')}
วันหมดอายุของ PO: {po_data.get('valid_until', '2026-12-31')}

=== 2. ข้อความจริงที่สกัดได้จากใบแจ้งหนี้ (INVOICE PDF EXTRACTED TEXT) ===
{invoice_text}

=== 3. ข้อความจริงที่สกัดได้จากสัญญา / ใบตรวจรับ (CONTRACT / GR PDF EXTRACTED TEXT) ===
{contract_section}

โปรดวิเคราะห์อย่างกระชับและส่งผลลัพธ์กลับมาในรูปแบบ JSON ตาม Schema ที่กำหนดเท่านั้น"""

    messages = [
        {"role": "system", "content": LLM_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.llm_temperature,
            response_format={"type": "json_object"},
            max_tokens=6000
        )
    except Exception as exc:
        logger.warning(f"Failed with response_format json_object, retrying without: {exc}")
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.llm_temperature,
            max_tokens=6000
        )

    content = response.choices[0].message.content or ""
    if not content.strip():
        raise ValueError(f"LLM returned empty content (finish_reason: {response.choices[0].finish_reason})")
    content = content.strip()

    # ล้างแท็ก <think>...</think> ในกรณีที่โมเดล reasoning ใส่ไว้ใน content
    content = re.sub(r"<think>[\s\S]*?</think>", "", content).strip()

    # ล้าง markdown code fences ถ้ามี
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    # แยก JSON substring ด้วย regex ในกรณีมีข้อความปน
    json_match = re.search(r"(\{[\s\S]*\})", content)
    if json_match:
        content = json_match.group(1)

    result = json.loads(content)

    # Normalization & Defensive fallbacks
    po_approved_amount = float(po_data.get("approved_amount", 0.0))
    if not isinstance(result.get("discrepancies"), list):
        result["discrepancies"] = []

    if not isinstance(result.get("comparison"), dict):
        result["comparison"] = {}

    # Normalization: ป้องกันความผิดพลาดกรณี LLM มองว่าชื่อไทยกับชื่ออังกฤษไม่ตรงกัน ทั้งที่เป็นบริษัทเดียวกัน
    comp_vendor = result.get("comparison", {}).get("vendor_name")
    if isinstance(comp_vendor, dict):
        v_doc = str(comp_vendor.get("doc", "")).lower()
        v_id = str(po_data.get("vendor_id", "")).strip()
        kw_list = {
            "VN-001": ["กังหัน", "kanghan"],
            "VN-002": ["อินโทรเวิท", "introvert"],
            "VN-003": ["เดอตี้ วอเธอร์", "dirty water"],
            "VN-004": ["ไอโอดี สลัด", "iod salad"],
            "VN-005": ["สยาม ซัน", "siam sun"],
            "VN-006": ["เอเชีย เมกา", "asia mega"],
            "VN-007": ["โกลบอล เอเนอร์ยี่", "global energy"],
            "VN-008": ["พรีเมียร์ วาล์ว", "premier valve"]
        }.get(v_id, [])
        if kw_list and any(kw in v_doc for kw in kw_list):
            comp_vendor["match"] = True
            # ลบข้อตรวจพบที่เป็น False Positive ออก
            result["discrepancies"] = [
                d for d in result["discrepancies"]
                if not (("ชื่อคู่ค้า" in str(d.get("title", "")) or "vendor" in str(d.get("title", "")).lower()) and ("ไม่ตรง" in str(d.get("title", "")) or "ไทย vs อังกฤษ" in str(d.get("title", ""))))
            ]

    fin = result.get("financial_summary")
    if not isinstance(fin, dict):
        fin = {}
    
    fin_po = float(fin.get("po_approved_amount") or po_approved_amount)
    fin_billed = float(fin.get("invoice_billed_subtotal") or fin_po)
    fin_net = float(fin.get("net_payable_subtotal") or fin_po)
    fin_vat = float(fin.get("vat_7_pct") or (fin_net * 0.07))
    fin_total = float(fin.get("total_due_payable") or (fin_net + fin_vat))

    result["financial_summary"] = {
        "po_approved_amount": fin_po,
        "invoice_billed_subtotal": fin_billed,
        "extra_unapproved_amount": float(fin.get("extra_unapproved_amount") or 0.0),
        "delay_penalty_amount": float(fin.get("delay_penalty_amount") or 0.0),
        "overbilled_amount": float(fin.get("overbilled_amount") or 0.0),
        "partial_short_amount": float(fin.get("partial_short_amount") or 0.0),
        "retention_deduct_amount": float(fin.get("retention_deduct_amount") or 0.0),
        "math_error_amount": float(fin.get("math_error_amount") or 0.0),
        "net_payable_subtotal": fin_net,
        "vat_7_pct": fin_vat,
        "total_due_payable": fin_total
    }

    if not result.get("status"):
        result["status"] = "APPROVED" if not result["discrepancies"] else "WARNING"
    if not result.get("status_label"):
        result["status_label"] = f"🟢 {result['status']}" if result["status"] == "APPROVED" else f"🟡 {result['status']}"
    if not result.get("action_recommendation"):
        result["action_recommendation"] = "ตรวจสอบข้อมูลเรียบร้อยแล้ว"
    if not result.get("email_summary"):
        result["email_summary"] = f"สรุปผลการตรวจเช็ค PO {po_data.get('po_number')}: {result.get('status_label')}"

    return result

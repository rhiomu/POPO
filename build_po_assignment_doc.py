import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Thonburi'
    normal_style.font.size = Pt(9.5)
    normal_style.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    # Title Banner Table
    t_meta = doc.add_table(rows=1, cols=1)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_meta = t_meta.rows[0].cells[0]
    set_cell_background(c_meta, "1E3A8A")
    set_cell_margins(c_meta, top=160, bottom=160, left=200, right=200)
    
    p_badge = c_meta.paragraphs[0]
    p_badge.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_badge = p_badge.add_run("โจทย์ที่ 1 : DATA FUSION & ENTERPRISE AUDIT AI\n")
    r_badge.font.size = Pt(11)
    r_badge.font.bold = True
    r_badge.font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)
    
    r_title = p_badge.add_run("Smart PO & Invoice Auditor (8 Enterprise Cases Edition)\n")
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    
    r_sub = p_badge.add_run("สร้างเว็บแอปตรวจเช็คบิลคู่ค้าอัตโนมัติด้วย AI — ดึงข้อมูล PO ชนใบแจ้งหนี้ PDF เพื่อสกัดจับยอดงอก, ค่าปรับส่งช้า, ของขาด, เงินประกัน, และความเสี่ยงโอนเงินผิดบัญชี\n\n")
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = RGBColor(0xBF, 0xDB, 0xFE)
    
    r_foot = p_badge.add_run("⏱️ เวลาโดยประมาณ: 90–120 นาที   |   🎯 เป้าหมาย: ผ่านครบ 6 requirement ขั้นต่ำ   |   💻 รูปแบบ: Vibe Coding")
    r_foot.font.size = Pt(9)
    r_foot.font.bold = True
    r_foot.font.color.rgb = RGBColor(0xFA, 0xCC, 0x15)

    doc.add_paragraph()

    # Section: เข้าใจภาพใน 30 วินาที
    h1 = doc.add_paragraph()
    r = h1.add_run("เข้าใจภาพใน 30 วินาที")
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_intro = doc.add_paragraph("นี่คือสิ่งที่เกิดขึ้นตั้งแต่ฝ่ายบัญชีเปิดระบบ เลือกเลขที่ PO จากฐานข้อมูล อัปโหลดไฟล์บิล PDF ของคู่ค้า และให้ AI วิเคราะห์เปรียบเทียบความถูกต้อง จนถึงการออกคำแนะนำว่า 'ควรจ่ายเต็มจำนวน, ปรับลดตามยอดตรวจรับจริง, หักเงินประกันผลงาน, หรือสั่งระงับการจ่ายเงินทันทีเพราะเสี่ยงทุจริต' — ทุกอย่างเกิดขึ้นแบบ Data-Driven และอัตโนมัติ")
    p_intro.paragraph_format.line_spacing = 1.15

    # 4-Step Table
    t_steps = doc.add_table(rows=2, cols=4)
    t_steps.alignment = WD_TABLE_ALIGNMENT.CENTER
    step_headers = ["❶ ดึงข้อมูล PO จาก DB", "❷ อัปโหลดบิล PDF", "❸ AI วินิจฉัย 8 มิติ", "❹ ออกคำสั่ง & Action"]
    step_descs = [
        "เชื่อมต่อ SQLite ดึงข้อมูล PO, Vendor Master, วงเงิน และเครดิตเทอม",
        "รับ Invoice & Contract PDF แล้วสกัดข้อความ (Unstructured Text) ออกมาอัตโนมัติ",
        "ตรวจยอดงอก, ค่าปรับช้า, บัญชีปลอม, งวดงาน, ส่งของขาด, Retention, วันหมดอายุ, คิดเลขผิด",
        "แสดงแถบสี 🟢 อนุมัติ / 🟡 เฝ้าระวัง / 🔴 ระงับจ่าย พร้อมปุ่ม Copy สรุปส่งอีเมล"
    ]
    for i in range(4):
        c_h = t_steps.rows[0].cells[i]
        set_cell_background(c_h, "2563EB")
        set_cell_margins(c_h, top=80, bottom=80, left=100, right=100)
        p = c_h.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(step_headers[i])
        r.font.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        c_d = t_steps.rows[1].cells[i]
        set_cell_background(c_d, "F8FAFC")
        set_cell_margins(c_d, top=80, bottom=80, left=100, right=100)
        p2 = c_d.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(step_descs[i])
        r2.font.size = Pt(8)
        r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_paragraph()

    # Section 1: โจทย์นี้ต้องการอะไร
    h2 = doc.add_paragraph()
    r = h2.add_run("1. โจทย์นี้ต้องการอะไร (Business Problem & Context)")
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_b1 = doc.add_paragraph("ในทุกสิ้นเดือน ฝ่ายจัดซื้อและฝ่ายบัญชีการเงินขององค์กรต้องเผชิญกับภาระงานมหาศาลในการเปิดหน้าจอ 2 จอสลับไปมา ระหว่าง 'ข้อมูลคำสั่งซื้อในระบบ ERP/Database (Purchase Order: PO)' กับ 'ไฟล์เอกสารใบแจ้งหนี้/ใบกำกับภาษี (Invoice PDF)' ที่คู่ค้าส่งมาเรียกเก็บเงิน")
    p_b1.paragraph_format.line_spacing = 1.15
    
    p_b2 = doc.add_paragraph("กระบวนการตรวจสอบด้วยสายตาของมนุษย์ (Manual Cross-checking) ทั้งล่าช้า ก่อให้เกิดภาวะคอขวด และมีความเสี่ยงสูงที่จะเกิดข้อผิดพลาดที่สร้างความเสียหายระดับหลายแสนถึงหลายล้านบาทต่อปี:")
    p_b2.paragraph_format.line_spacing = 1.15

    traps = [
        ("1. คู่ค้าแอบใส่ค่าบริการงอกนอกใบ PO (Unapproved Scope Charges): ", "สอดไส้ค่าบริการฉุกเฉิน ค่าเดินทาง หรือค่าวัสดุที่ไม่ได้ตกลงไว้ในสัญญาหลัก"),
        ("2. ส่งงานล่าช้ากว่ากำหนด แต่ไม่มีใครเปิดเช็คเงื่อนไขสัญญาเพื่อคิดค่าปรับ (Late Penalty): ", "คู่ค้าส่งมอบงานช้า แต่ฝ่ายตรวจรับไม่ได้คำนวณหักค่าเสียหายจากการล่าช้า (Liquidated Damages)"),
        ("3. ชื่อบริษัทคล้ายกัน แต่เลขประจำตัวผู้เสียภาษีหรือเลขบัญชีไม่ตรง (Mismatched Tax ID & Bank Account): ", "เสี่ยงต่อการถูกสวมรอยบิล (Invoice Fraud) โอนเงินเข้าบัญชีมิจฉาชีพ"),
        ("4. เบิกเงินเกินงวดงาน (Over-milestone Billing): ", "สัญญาระบุงวดที่ 1 ให้เบิกได้ 30% แต่วางบิลขอเบิก 50% เกินสิทธิ์ที่ตกลงไว้"),
        ("5. ส่งมอบของไม่ครบตามจำนวน (Partial Delivery / Short Shipment): ", "สั่ง 10 ชุด ได้รับจริงแค่ 7 ชุด แต่บิลเรียกเก็บเงินเต็ม 10 ชุด"),
        ("6. ลืมหักเงินค้ำประกันผลงาน 5% ตามสัญญา (Missing Warranty Retention): ", "สัญญาระบุงวดสุดท้ายต้องหักเงิน Retention 5% ไว้นาน 1 ปี แต่วางบิลขอเบิกเต็ม 100%"),
        ("7. ส่งงานหลัง PO หมดอายุโดยไม่มีใบขยายเวลา (Expired PO / Missing Amendment): ", "PO หมดอายุไปแล้ว ต้องระงับจ่าย (Hold) เพื่อให้จัดซื้อทำ PO Amendment ก่อน"),
        ("8. บิลคำนวณตัวเลขผิดพลาด (Invoice Math Calculation & Tax Error): ", "ผลรวมของรายการย่อย (Line Items) ไม่ตรงกับยอด Subtotal และภาษีท้ายบิล")
    ]
    for title, desc in traps:
        p_t = doc.add_paragraph(style='List Bullet')
        p_t.paragraph_format.line_spacing = 1.15
        r_t = p_t.add_run(title)
        r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)
        r_d = p_t.add_run(desc)
        r_d.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    p_sol = doc.add_paragraph()
    p_sol.paragraph_format.line_spacing = 1.15
    r_bold = p_sol.add_run("สิ่งที่นักเรียนต้องสร้าง: ")
    r_bold.font.bold = True
    r_bold.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    p_sol.add_run("เว็บแอปพลิเคชันแบบเบ็ดเสร็จ (Single-Port Monolith) บน Port 8000 ที่ให้ฝ่ายบัญชีเลือก PO จากฐานข้อมูล จากนั้นอัปโหลดไฟล์ PDF บิลและสัญญาของคู่ค้า แล้วให้ AI ช่วยสกัดข้อมูล เปรียบเทียบตารางต่อตาราง และวินิจฉัยจุดผิดปกติทั้ง 8 มิติออกมาให้เห็นชัดเจน พร้อมสรุปคำแนะนำในการอนุมัติจ่ายเงินได้ในคลิกเดียว")

    doc.add_paragraph()

    # Section 4: กฎทางธุรกิจและตารางเฉลยเคสทดสอบทั้ง 8 เคส
    h5 = doc.add_paragraph()
    r = h5.add_run("4. กฎทางธุรกิจและตารางเฉลยเคสทดสอบ (Business Rules & Ground Truth Matrix)")
    r.font.size = Pt(12.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    doc.add_paragraph("เพื่อให้ระบบทำงานได้อย่างสมบูรณ์ ระบบต้องตรวจจับจุดผิดปกติในเอกสารทดสอบทั้ง 8 ชุดใน sample_documents/ ได้อย่างแม่นยำ:")

    t_cases = doc.add_table(rows=9, cols=4)
    t_cases.alignment = WD_TABLE_ALIGNMENT.CENTER
    case_headers = ["ชุดทดสอบ", "ข้อมูลใน PO (ฐานข้อมูล)", "สภาพข้อเท็จจริงในเอกสาร PDF", "ผลการวินิจฉัย & ป้ายสถานะ"]
    for j, h in enumerate(case_headers):
        c = t_cases.rows[0].cells[j]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, top=70, bottom=70, left=90, right=90)
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    cases_data = [
        ("Case 1\nPO-2026-089", "วงเงิน 1,000,000 บาท\nเครดิตเทอม 30 วัน", "• มียอดงอก 20,000 บ. (Emergency fee)\n• ส่งงานช้า 10 วัน (ปรับ 0.1%/วัน = 10,000 บ.)\n• บิลขอเครดิตเทอม 15 วัน", "🟡 WARNING\n• ตัดยอดงอก 20,000 บ.\n• หักค่าปรับล่าช้า 10,000 บ.\n👉 ยอดอนุมัติจ่าย: 990,000 บ. (+VAT)"),
        ("Case 2\nPO-2026-090", "วงเงิน 450,000 บาท\nเครดิตเทอม 45 วัน\nธนาคาร SCB", "• ส่งมอบตรงเวลา ผ่าน QC ครบ\n• ยอดเงิน 450,000 บาท ตรงตาม PO\n• Tax ID และเลขบัญชีถูกต้อง", "🟢 APPROVED\n• ข้อมูลถูกต้องตามสัญญาทุกประการ\n• ไม่มีค่าปรับ ไม่มียอดงอก\n👉 ยอดอนุมัติจ่าย: 450,000 บ. (+VAT)"),
        ("Case 3\nPO-2026-091", "Vendor: VN-003\nTax ID: 0105562045678\nBBL: 201-0-55443-3", "• Tax ID บนบิลเป็น 0995559999999\n• ธนาคารบนบิลเป็น SCB 999-9-99999-9", "🔴 FRAUD ALERT\n• เลข Tax ID และเลขบัญชีไม่ตรงกับระบบ!\n• ตรวจพบความเสี่ยงทุจริต/สวมรอย\n👉 คำสั่ง: ระงับการจ่ายเงินทันที"),
        ("Case 4\nPO-2026-092", "วงเงินรวม 2,000,000 บาท\nเครดิตเทอม 30 วัน", "• บิลขอเบิกงวด 50% = 1,000,000 บาท\n• สัญญาระบุงวดที่ 1 เบิกได้สูงสุด 30% (600,000 บาท)", "🟡 WARNING\n• เบิกเงินเกินงวดงานไป 400,000 บ.\n• งวดที่ 1 จ่ายได้สูงสุด 600,000 บ.\n👉 คำแนะนำ: ให้คู่ค้าแก้ยอดตามงวด"),
        ("Case 5\nPO-2026-093", "ซื้อ 10 ชุด (1.2 ล้านบ.)\nชุดละ 120,000 บาท", "• คลังสินค้าตรวจรับได้จริงแค่ 7 ชุด (840k)\n• อีก 3 ชุดของขาด (Backorder)\n• แต่บิลเรียกเก็บเงินเต็ม 10 ชุด (1.2 ล้าน)", "🟡 WARNING\n• ปรับลดยอดจ่ายตามของที่ได้รับจริง 7 ชุด\n• ตัดยอดของค้างส่ง 360,000 บ. ออก\n👉 ยอดอนุมัติจ่าย: 840,000 บ. (+VAT)"),
        ("Case 6\nPO-2026-094", "วงเงิน 3,000,000 บาท\nงวดสุดท้าย (Final 100%)", "• สัญญาระบุต้องหักเงินค้ำประกันผลงาน (Retention) 5% = 150,000 บ. ไว้นาน 1 ปี\n• แต่บิลวางขอเบิกเต็ม 3,000,000 บ.", "🟡 WARNING\n• หัก Retention 5% (150,000 บ.) ตามสัญญา\n• ค้างจ่ายไว้รอครบระยะรับประกัน 1 ปี\n👉 ยอดอนุมัติจ่าย: 2,850,000 บ. (+VAT)"),
        ("Case 7\nPO-2026-095", "วงเงิน 650,000 บาท\nPO หมดอายุ: 30 มิ.ย. 2026", "• ส่งมอบงานจริงวันที่ 20 ส.ค. 2026 (หลัง PO หมดอายุ 51 วัน)\n• ไม่มีใบขอขยายเวลา PO Amendment", "🟡 HOLD PAYMENT\n• ระงับการจ่ายเงินชั่วคราว (Hold)\n• ต้องให้จัดซื้อทำ PO Amendment ขยายเวลาก่อน"),
        ("Case 8\nPO-2026-096", "วงเงิน 500,000 บาท\n(200k + 180k + 120k)", "• รายการย่อย 3 ชิ้น รวมได้ 500,000 บ.\n• แต่บิลคิดเลขผิดระบุ Subtotal เป็น 550,000 บ. (คิดเงินเกินจริง 50,000 บ.)", "🟡 WARNING\n• ตรวจพบบิลคิดเลขผิดเกินไป 50,000 บ.\n• ภาษี VAT 7% คำนวณบนฐานที่ผิด\n👉 คำแนะนำ: ตีบิลกลับแก้ไขยอด")
    ]
    for i, row_data in enumerate(cases_data, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row_data):
            c = t_cases.rows[i].cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=60, bottom=60, left=80, right=80)
            p = c.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8)
            if "APPROVED" in val:
                r.font.color.rgb = RGBColor(0x15, 0x80, 0x3D)
            elif "WARNING" in val or "HOLD" in val:
                r.font.color.rgb = RGBColor(0xB4, 0x53, 0x09)
            elif "FRAUD" in val:
                r.font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C)

    doc.save("po_vibe_coding_assignment.docx")
    print(" Successfully updated po_vibe_coding_assignment.docx with 8 cases")

if __name__ == "__main__":
    create_document()

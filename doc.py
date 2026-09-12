# generate_sample_docs.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.makedirs("sample_documents", exist_ok=True)

def generate_invoice_pdf():
    pdf_path = "sample_documents/Invoice_INV2026_001.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "INVOICE / TAX INVOICE (ORIGINAL)")
    c.setLineWidth(1)
    c.line(50, height - 55, width - 50, height - 55)

    # Vendor Info (จุดดัก: ชื่อหัวบิลเขียนสั้นลง ไม่ตรงเป๊ะ แต่ Tax ID ตรง)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 75, "Supplier / Vendor:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 90, "Siam Engineering & Service Co., Ltd.")
    c.drawString(50, height - 105, "Tax ID: 0105556098711")
    c.drawString(50, height - 120, "Bank Account: Kasikorn Bank (045-2-12345-6)")

    # Customer & Ref Info
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, height - 75, "Billed To:")
    c.setFont("Helvetica", 10)
    c.drawString(350, height - 90, "B.Grimm Power Plant (Amata Nakorn)")
    c.drawString(350, height - 105, "Invoice No: INV-2026-001")
    c.drawString(350, height - 120, "PO Reference: PO-2026-089")
    c.drawString(350, height - 135, "Payment Term: 15 Days")  # จุดดัก: ขอ 15 วัน ทั้งที่ PO ให้ 30 วัน

    # Line Items Header
    y = height - 170
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawString(450, y, "Amount (THB)")
    c.line(50, y - 5, width - 50, y - 5)

    # Line Items (จุดดัก: มียอดงอก 20,000 บาท)
    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "1. Periodic Maintenance & Gas Turbine Filter Replacement")
    c.drawRightString(width - 50, y, "1,000,000.00")

    y -= 20
    c.drawString(50, y, "2. Emergency On-site Mobilization Fee (Non-PO Item)")
    c.drawRightString(width - 50, y, "20,000.00")

    # Summary
    y -= 30
    c.line(350, y, width - 50, y)
    y -= 15
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y, "Subtotal:")
    c.drawRightString(width - 50, y, "1,020,000.00")

    y -= 15
    c.drawString(350, y, "VAT (7%):")
    c.drawRightString(width - 50, y, "71,400.00")

    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "Total Due:")
    c.drawRightString(width - 50, y, "1,091,400.00")

    c.save()
    print(f" Created: {pdf_path}")

def generate_contract_pdf():
    pdf_path = "sample_documents/Contract_PO2026_089_Summary.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, "ANNEXURE: TERMS & SERVICE AGREEMENT")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 68, "Reference Contract: PO-2026-089 / Siam Engineering")
    c.line(50, height - 75, width - 50, height - 75)

    text_lines = [
        "1. SCOPE OF SERVICES:",
        "The contractor shall perform maintenance on gas turbine units as specified in site schedule.",
        "",
        "2. PAYMENT TERMS & DISBURSEMENT:",
        "- Approved contract value: 1,000,000 THB (exclusive of VAT).",
        "- Standard credit terms: 30 days upon submission of full completion certificate.",
        "- Any extra charges outside scope require formal PO amendment prior to billing.",
        "",
        "3. PENALTY & DELAY CLAUSE (CRITICAL):",
        "- Scheduled completion deadline: August 15, 2026.",
        "- Actual completion date recorded: August 25, 2026 (10 days delayed).",
        "- Clause 3.2: Delay exceeding 7 days incurs liquidated damages at 0.1% per day of total PO value.",
        "- Delay penalty calculation: 10 days x 0.1% = 1.0% deduction (10,000 THB).",
        "",
        "4. COMPLIANCE & BANKING:",
        "- Remittance strictly to registered entity Siam Engineering & Service Co., Ltd. only.",
        "- Registered Tax ID: 0105556098711."
    ]

    y = height - 100
    for line in text_lines:
        if "CRITICAL" in line or "SCOPE" in line or "PAYMENT TERMS" in line or "COMPLIANCE" in line:
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 9)
        c.drawString(50, y, line)
        y -= 18

    c.save()
    print(f" Created: {pdf_path}")

if __name__ == "__main__":
    generate_invoice_pdf()
    generate_contract_pdf()
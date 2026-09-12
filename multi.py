# multi.py - Setup Enterprise Database & 8 Test Case Documents
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.makedirs("sample_documents", exist_ok=True)

def setup_database():
    conn = sqlite3.connect("enterprise.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS purchase_orders")
    cursor.execute("DROP TABLE IF EXISTS vendor_master")

    cursor.execute("""
        CREATE TABLE vendor_master (
            vendor_id TEXT PRIMARY KEY,
            tax_id TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            bank_name TEXT NOT NULL,
            bank_account TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE purchase_orders (
            po_number TEXT PRIMARY KEY,
            vendor_id TEXT NOT NULL,
            project_site TEXT NOT NULL,
            scope_of_work TEXT NOT NULL,
            approved_amount REAL NOT NULL,
            standard_credit_days INTEGER NOT NULL,
            valid_until TEXT NOT NULL DEFAULT '2026-12-31',
            FOREIGN KEY (vendor_id) REFERENCES vendor_master(vendor_id)
        )
    """)

    vendors = [
        ("VN-001", "0105556098711", "บริษัท กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส จำกัด", "ธนาคารกสิกรไทย", "045-2-12345-6"),
        ("VN-002", "0105549012345", "บริษัท อินโทรเวิท เทค ซัพพลาย จำกัด", "ธนาคารไทยพาณิชย์", "112-3-98765-4"),
        ("VN-003", "0105562045678", "บริษัท เดอตี้ วอเธอร์ โซลูชั่นส์ จำกัด", "ธนาคารกรุงเทพ", "201-0-55443-3"),
        ("VN-004", "0105531089922", "บริษัท ไอโอดี สลัด เพาเวอร์ จำกัด", "ธนาคารกรุงไทย", "003-1-77889-0"),
        ("VN-005", "0105558012399", "บริษัท สยาม ซัน พาวเวอร์ อีควิปเมนท์ จำกัด", "ธนาคารกสิกรไทย", "029-1-88776-5"),
        ("VN-006", "0105547089112", "บริษัท เอเชีย เมกา คอนสตรัคชั่น จำกัด", "ธนาคารไทยพาณิชย์", "049-2-33445-5"),
        ("VN-007", "0105551022445", "บริษัท โกลบอล เอเนอร์ยี่ ซิสเต็มส์ จำกัด", "ธนาคารกรุงเทพ", "142-0-99881-2"),
        ("VN-008", "0105539077123", "บริษัท พรีเมียร์ วาล์ว แอนด์ ไปป์ จำกัด", "ธนาคารกรุงไทย", "015-1-66554-3")
    ]

    pos = [
        ("PO-2026-089", "VN-001", "G.Brimm Power", "งานซ่อมบำรุงกังหันก๊าซ", 1000000.00, 30, "2026-12-31"),
        ("PO-2026-090", "VN-002", "G.Brimm Solar", "จัดซื้ออินเวอร์เตอร์โซลาร์ 20 ชุด", 450000.00, 45, "2026-12-31"),
        ("PO-2026-091", "VN-003", "G.Brimm Biomass", "ติดตั้งระบบบำบัดน้ำเสีย", 800000.00, 30, "2026-12-31"),
        ("PO-2026-092", "VN-004", "Headquarter (Bangkok)", "โครงการพัฒนาระบบประหยัดพลังงาน", 2000000.00, 30, "2026-12-31"),
        ("PO-2026-093", "VN-005", "Amata City Solar", "จัดซื้อ Switchgear และ Inverter 10 ชุด", 1200000.00, 30, "2026-12-31"),
        ("PO-2026-094", "VN-006", "Laem Chabang Floating Solar", "ติดตั้งโครงสร้างโซลาร์ลอยน้ำ (งวดสุดท้าย)", 3000000.00, 30, "2026-12-31"),
        ("PO-2026-095", "VN-007", "Substation Rayong", "ซ่อมบำรุงหม้อแปลงไฟฟ้าแรงสูง", 650000.00, 30, "2026-06-30"),
        ("PO-2026-096", "VN-008", "Gas Plant Map Ta Phut", "จัดซื้อวาล์วและท่อก๊าซทนแรงดันสูง 3 รายการ", 500000.00, 30, "2026-12-31")
    ]

    cursor.executemany("INSERT INTO vendor_master VALUES (?, ?, ?, ?, ?)", vendors)
    cursor.executemany("INSERT INTO purchase_orders VALUES (?, ?, ?, ?, ?, ?, ?)", pos)
    conn.commit()
    conn.close()
    print("✅ Database ready: enterprise.db (8 Vendors, 8 POs)")

def create_pdf(filename, title, lines):
    path = os.path.join("sample_documents", filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, title)
    c.setLineWidth(1)
    c.line(50, height - 55, width - 50, height - 55)

    y = height - 85
    c.setFont("Helvetica", 9)
    for line in lines:
        if line.startswith("[H]"):
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y, line[3:])
        else:
            c.setFont("Helvetica", 9)
            c.drawString(50, y, line)
        y -= 16
    c.save()
    print(f" Created: {path}")

def generate_all_pdfs():
    # --- Case 1: ยอดงอก + ค่าปรับส่งช้า ---
    create_pdf("Case1_Invoice_PO089.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: KangHan Engineering & Service Co., Ltd.",
        "Tax ID: 0105556098711 | Bank: Kasikorn 045-2-12345-6",
        "PO Ref: PO-2026-089 | Payment Term: 15 Days",
        "",
        "[H]Line Items:",
        "- Gas turbine maintenance: 1,000,000.00 THB",
        "- Emergency mobilization fee: 20,000.00 THB (Extra)",
        "Subtotal: 1,020,000.00 THB | VAT 7%: 71,400.00 THB",
        "[H]Total Due: 1,091,400.00 THB"
    ])
    create_pdf("Case1_Contract_PO089.pdf", "CONTRACT ANNEX & WORK COMPLETION", [
        "[H]Reference: PO-2026-089 (KangHan Engineering)",
        "Contract Value: 1,000,000.00 THB (Excl. VAT) | Credit Term: 30 Days",
        "",
        "[H]Completion Status:",
        "Scheduled Deadline: Aug 15, 2026 | Actual Completion: Aug 25, 2026 (10 days late)",
        "[H]Penalty Clause:",
        "Delay > 7 days incurs 0.1% per day liquidated damages.",
        "Deduction required: 10 days x 0.1% = 1.0% (10,000.00 THB deduction)."
    ])

    # --- Case 2: เคสตรงเป๊ะ (Clean Approval) ---
    create_pdf("Case2_Invoice_PO090.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: Introvert Tech Supply Co., Ltd.",
        "Tax ID: 0105549012345 | Bank: SCB 112-3-98765-4",
        "PO Ref: PO-2026-090 | Payment Term: 45 Days",
        "",
        "[H]Line Items:",
        "- 20x Solar Inverters as per specs: 450,000.00 THB",
        "Subtotal: 450,000.00 THB | VAT 7%: 31,500.00 THB",
        "[H]Total Due: 481,500.00 THB"
    ])
    create_pdf("Case2_Contract_PO090.pdf", "GOODS RECEIPT & INSPECTION CERTIFICATE", [
        "[H]Reference: PO-2026-090 (Introvert Tech Supply)",
        "Approved PO Amount: 450,000.00 THB | Term: 45 Days",
        "",
        "[H]Inspection Result:",
        "Delivered on time (Aug 10, 2026). All 20 units pass QC check.",
        "Status: Fully Approved for payment without deductions."
    ])

    # --- Case 3: เคสเสี่ยงทุจริต / เลขบัญชีและ Tax ID ปลอม ---
    create_pdf("Case3_Invoice_PO091.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: Dirty Water (Thailand) Co., Ltd.",
        "Tax ID: 0995559999999 (MISMATCH!) | Bank: SCB 999-9-99999-9 (UNKNOWN ACCOUNT)",
        "PO Ref: PO-2026-091 | Payment Term: 30 Days",
        "",
        "[H]Line Items:",
        "- Wastewater treatment installation: 800,000.00 THB",
        "Subtotal: 800,000.00 THB | VAT 7%: 56,000.00 THB",
        "[H]Total Due: 856,000.00 THB"
    ])
    create_pdf("Case3_Contract_PO091.pdf", "PROJECT AGREEMENT & VENDOR DATA", [
        "[H]Reference: PO-2026-091",
        "Registered Vendor: Dirty Water Co., Ltd. (Vendor ID: VN-003)",
        "Official Registered Tax ID: 0105562045678",
        "Official Registered Bank: Bangkok Bank 201-0-55443-3",
        "[H]Security Alert:",
        "Payments diverted to alternative accounts without CFO signature are strictly void."
    ])

    # --- Case 4: เบิกเงินเกินงวดงาน (Over-milestone billing) ---
    create_pdf("Case4_Invoice_PO092.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: IOD Salad Power Co., Ltd.",
        "Tax ID: 0105531089922 | Bank: KTB 003-1-77889-0",
        "PO Ref: PO-2026-092 | Payment Term: 30 Days",
        "",
        "[H]Line Items:",
        "- Energy Efficiency Project (Billed at 50% Milestone): 1,000,000.00 THB",
        "Subtotal: 1,000,000.00 THB | VAT 7%: 70,000.00 THB",
        "[H]Total Due: 1,070,000.00 THB"
    ])
    create_pdf("Case4_Contract_PO092.pdf", "MILESTONE PAYMENT SCHEDULE AGREEMENT", [
        "[H]Reference: PO-2026-092 (Total Project Value: 2,000,000.00 THB)",
        "",
        "[H]Agreed Milestone Schedule:",
        "- Milestone 1 (Design & Site Prep): 30% of contract = 600,000.00 THB",
        "- Milestone 2 (Installation): 40% of contract = 800,000.00 THB",
        "- Milestone 3 (Final Testing): 30% of contract = 600,000.00 THB",
        "[H]Audit Condition:",
        "Milestone 1 is currently in progress. Billing is strictly capped at 30% (600,000 THB)."
    ])

    # --- Case 5: ส่งของไม่ครบแต่เก็บเงินเต็ม 100% (Partial Delivery) ---
    create_pdf("Case5_Invoice_PO093.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: Siam Sun Power Equipment Co., Ltd.",
        "Tax ID: 0105558012399 | Bank: Kasikorn 029-1-88776-5",
        "PO Ref: PO-2026-093 | Payment Term: 30 Days",
        "",
        "[H]Line Items:",
        "- 10x Switchgear & Industrial Inverter Units (120,000 THB/unit): 1,200,000.00 THB",
        "Subtotal: 1,200,000.00 THB | VAT 7%: 84,000.00 THB",
        "[H]Total Due: 1,284,000.00 THB"
    ])
    create_pdf("Case5_Contract_PO093.pdf", "GOODS RECEIPT & WAREHOUSE DISCREPANCY NOTE", [
        "[H]Reference: PO-2026-093 (Siam Sun Power)",
        "Ordered Quantity: 10 Units @ 120,000.00 THB = 1,200,000.00 THB",
        "",
        "[H]Warehouse Inbound Inspection:",
        "- Received into inventory: 7 Units only (Passed physical inspection).",
        "- Short delivery: 3 Units pending manufacturer backorder.",
        "[H]Receiving Officer Note:",
        "Certified delivered value: 7 Units x 120,000.00 = 840,000.00 THB.",
        "Billing must be adjusted to 840,000.00 THB. Do NOT approve full 10 units."
    ])

    # --- Case 6: ลืมหักเงินค้ำประกันผลงาน 5% (Missing Retention) ---
    create_pdf("Case6_Invoice_PO094.pdf", "INVOICE / TAX INVOICE (FINAL BILLING)", [
        "[H]Supplier: Asia Mega Construction Co., Ltd.",
        "Tax ID: 0105547089112 | Bank: SCB 049-2-33445-5",
        "PO Ref: PO-2026-094 | Payment Term: 30 Days",
        "",
        "[H]Line Items:",
        "- Floating Solar Mounting & Anchoring (100% Final Completion): 3,000,000.00 THB",
        "Subtotal: 3,000,000.00 THB | VAT 7%: 210,000.00 THB",
        "[H]Total Due: 3,210,000.00 THB"
    ])
    create_pdf("Case6_Contract_PO094.pdf", "FINAL COMPLETION CERTIFICATE & WARRANTY AGREEMENT", [
        "[H]Reference: PO-2026-094 (Asia Mega Construction)",
        "Contract Total: 3,000,000.00 THB (Excl. VAT)",
        "",
        "[H]Project Sign-off:",
        "Floating solar installation is 100% physically completed and operational.",
        "[H]Mandatory Warranty Retention Clause 5.1:",
        "- 5% Retention (150,000.00 THB) must be withheld for 12 months defects liability.",
        "- Maximum payable amount for final invoice is 95% = 2,850,000.00 THB.",
        "- Vendor invoice failed to deduct retention. Audit must deduct 150,000 THB."
    ])

    # --- Case 7: สัญญาและ PO หมดอายุเกินกำหนด (Expired PO / Required Amendment) ---
    create_pdf("Case7_Invoice_PO095.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: Global Energy Systems Co., Ltd.",
        "Tax ID: 0105551022445 | Bank: Bangkok Bank 142-0-99881-2",
        "PO Ref: PO-2026-095 | Invoice Date: August 25, 2026",
        "",
        "[H]Line Items:",
        "- High-voltage transformer overhaul service: 650,000.00 THB",
        "Subtotal: 650,000.00 THB | VAT 7%: 45,500.00 THB",
        "[H]Total Due: 695,500.00 THB"
    ])
    create_pdf("Case7_Contract_PO095.pdf", "SITE WORK ORDER & COMPLIANCE RECORD", [
        "[H]Reference: PO-2026-095 (Global Energy Systems)",
        "PO Effective Period: January 01, 2026 to June 30, 2026 (EXPIRED)",
        "",
        "[H]Execution Audit Finding:",
        "- Service was executed and signed off on August 20, 2026 (51 days past PO expiry).",
        "- No formal PO Amendment or time extension was approved by VP of Procurement.",
        "[H]Audit Ruling:",
        "Status: HOLD PAYMENT. Require approved retroactive PO Amendment before payment."
    ])

    # --- Case 8: บิลคิดเลขผิด / Subtotal ไม่ตรงกับ Line Items (Invoice Math Error) ---
    create_pdf("Case8_Invoice_PO096.pdf", "INVOICE / TAX INVOICE", [
        "[H]Supplier: Premier Valve & Pipe Co., Ltd.",
        "Tax ID: 0105539077123 | Bank: KTB 015-1-66554-3",
        "PO Ref: PO-2026-096 | Payment Term: 30 Days",
        "",
        "[H]Line Items:",
        "1. High-pressure control valves (DN150): 200,000.00 THB",
        "2. Seamless alloy gas pipes (Schedule 80): 180,000.00 THB",
        "3. Flange fittings & stainless fasteners: 120,000.00 THB",
        "",
        "[H]Summary (NOTE: Math calculation mismatch!):",
        "Subtotal: 550,000.00 THB (WRONG! Sum of items is 500,000 THB) | Overcharge: 50,000 THB",
        "VAT (7%): 38,500.00 THB (Calculated on wrong subtotal)",
        "[H]Total Due: 588,500.00 THB"
    ])
    create_pdf("Case8_Contract_PO096.pdf", "GOODS RECEIPT SLIP & PO SPECIFICATION", [
        "[H]Reference: PO-2026-096 (Premier Valve & Pipe)",
        "Approved PO Total: 500,000.00 THB (Item 1: 200k, Item 2: 180k, Item 3: 120k)",
        "",
        "[H]Receiving Report:",
        "All materials received in good order. Total agreed cost: 500,000.00 THB.",
        "[H]Accounting Audit Instruction:",
        "Discrepancy detected: Invoice subtotal shows 550,000 THB instead of 500,000 THB.",
        "Return invoice to vendor for mathematical correction before disbursement."
    ])

if __name__ == "__main__":
    setup_database()
    generate_all_pdfs()

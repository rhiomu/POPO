import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

font_path = "/System/Library/Fonts/Supplemental/Sathu.ttf"
pdfmetrics.registerFont(TTFont("Sathu", font_path))

def build_pdf():
    pdf_filename = "03_smart_po_invoice_auditor.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    title_badge_style = ParagraphStyle('TitleBadge', fontName='Sathu', fontSize=9.5, leading=13, textColor=colors.HexColor('#93C5FD'), alignment=1)
    title_main_style = ParagraphStyle('TitleMain', fontName='Sathu', fontSize=16, leading=20, textColor=colors.white, alignment=1)
    title_sub_style = ParagraphStyle('TitleSub', fontName='Sathu', fontSize=8.5, leading=12, textColor=colors.HexColor('#BFDBFE'), alignment=1)
    title_foot_style = ParagraphStyle('TitleFoot', fontName='Sathu', fontSize=8, leading=11, textColor=colors.HexColor('#FACC15'), alignment=1)

    h1_style = ParagraphStyle('Heading1_Custom', fontName='Sathu', fontSize=11, leading=15, textColor=colors.HexColor('#1E3A8A'), spaceAfter=4)
    body_style = ParagraphStyle('Body_Custom', fontName='Sathu', fontSize=8, leading=11.5, textColor=colors.HexColor('#1F2937'), spaceAfter=3)
    bullet_style = ParagraphStyle('Bullet_Custom', fontName='Sathu', fontSize=8, leading=11.5, textColor=colors.HexColor('#1F2937'), leftIndent=12, spaceAfter=2)
    table_cell_style = ParagraphStyle('TableCell', fontName='Sathu', fontSize=7, leading=9.5, textColor=colors.HexColor('#1F2937'))
    table_header_style = ParagraphStyle('TableHeader', fontName='Sathu', fontSize=7.5, leading=10.5, textColor=colors.white, alignment=1)

    story = []

    # Banner
    banner_content = [
        Paragraph("โจทย์ที่ 1 : DATA FUSION & ENTERPRISE AUDIT AI", title_badge_style),
        Spacer(1, 2),
        Paragraph("Smart PO & Invoice Auditor (8 Enterprise Cases Edition)", title_main_style),
        Spacer(1, 2),
        Paragraph("สร้างเว็บแอปตรวจเช็คบิลคู่ค้าอัตโนมัติด้วย AI — ดึงข้อมูล PO ชนใบแจ้งหนี้ PDF เพื่อสกัดจับยอดงอก, ค่าปรับส่งช้า, ของขาด, เงินประกัน, และความเสี่ยงโอนเงินผิดบัญชี", title_sub_style),
        Spacer(1, 3),
        Paragraph("⏱️ เวลาโดยประมาณ: 90–120 นาที   |   🎯 เป้าหมาย: ผ่านครบ 6 requirement ขั้นต่ำ   |   💻 รูปแบบ: Vibe Coding", title_foot_style)
    ]
    t_banner = Table([[banner_content]], colWidths=[552])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1E3A8A')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 8))

    # 4-Step Table
    step_headers = [
        Paragraph("❶ ดึงข้อมูล PO จาก DB", table_header_style),
        Paragraph("❷ อัปโหลดบิล PDF", table_header_style),
        Paragraph("❸ AI วินิจฉัย 8 มิติ", table_header_style),
        Paragraph("❹ ออกคำสั่ง & Action", table_header_style)
    ]
    step_bodies = [
        Paragraph("เชื่อมต่อ SQLite ดึงข้อมูล PO, Vendor, วงเงิน และเครดิตเทอม", table_cell_style),
        Paragraph("รับ Invoice & Contract PDF แล้วสกัดข้อความอัตโนมัติ", table_cell_style),
        Paragraph("ตรวจจับ 8 จุดดัก: ยอดงอก, ส่งช้า, บัญชีปลอม, งวดงาน, ส่งของขาด, Retention, วันหมดอายุ, คิดเลขผิด", table_cell_style),
        Paragraph("แสดงแถบสี 🟢 อนุมัติ / 🟡 เฝ้าระวัง / 🔴 ระงับจ่าย พร้อมปุ่ม Copy สรุปส่งอีเมล", table_cell_style)
    ]
    t_steps = Table([step_headers, step_bodies], colWidths=[138, 138, 138, 138])
    t_steps.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563EB')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t_steps)
    story.append(Spacer(1, 8))

    # Ground Truth Table (8 Cases)
    story.append(Paragraph("ตารางเฉลยเคสทดสอบทั้ง 8 สถานการณ์ (Ground Truth Test Matrix)", h1_style))
    
    case_headers = [
        Paragraph("ชุดทดสอบ", table_header_style),
        Paragraph("ข้อมูลใน PO (ระบบ)", table_header_style),
        Paragraph("ข้อเท็จจริงในบิล PDF", table_header_style),
        Paragraph("ผลการวินิจฉัย & ป้ายสถานะ", table_header_style)
    ]
    case_rows = [
        [Paragraph("<b>Case 1</b><br/>PO-2026-089", table_cell_style),
         Paragraph("1,000,000 บาท<br/>เทอม 30 วัน", table_cell_style),
         Paragraph("• ยอดงอก Emergency fee 20,000 บ.<br/>• ส่งงานช้า 10 วัน (ปรับ 10,000 บ.)<br/>• บิลขอเทอม 15 วัน", table_cell_style),
         Paragraph("<font color='#B45309'><b>🟡 WARNING</b></font><br/>• ตัดยอดงอก 20k<br/>• หักปรับช้า 10k<br/>👉 <b>ยอดจ่าย: 990,000 บ. (+VAT)</b>", table_cell_style)],
        
        [Paragraph("<b>Case 2</b><br/>PO-2026-090", table_cell_style),
         Paragraph("450,000 บาท<br/>เทอม 45 วัน", table_cell_style),
         Paragraph("• ส่งมอบตรงเวลา ผ่าน QC ครบ<br/>• ยอดเงิน 450,000 บ. ตรงตาม PO<br/>• Tax ID & เลขบัญชีถูกต้อง", table_cell_style),
         Paragraph("<font color='#15803D'><b>🟢 APPROVED</b></font><br/>• เอกสารถูกต้องครบถ้วน<br/>• ไม่มีค่าปรับ ไม่มียอดงอก<br/>👉 <b>ยอดจ่าย: 450,000 บ. (+VAT)</b>", table_cell_style)],
        
        [Paragraph("<b>Case 3</b><br/>PO-2026-091", table_cell_style),
         Paragraph("Vendor: VN-003<br/>Tax: 0105562045678<br/>BBL: 201-0-55443-3", table_cell_style),
         Paragraph("• Tax ID บนบิลเป็น 0995559999999<br/>• ธนาคารบนบิลระบุ SCB 999-9-99999-9", table_cell_style),
         Paragraph("<font color='#B91C1C'><b>🔴 FRAUD ALERT</b></font><br/>• Tax ID และบัญชีไม่ตรงระบบ!<br/>• เสี่ยงถูกสวมรอยบิล/ทุจริต<br/>👉 <b>คำสั่ง: ระงับจ่ายทันที!</b>", table_cell_style)],
        
        [Paragraph("<b>Case 4</b><br/>PO-2026-092", table_cell_style),
         Paragraph("2,000,000 บาท<br/>เทอม 30 วัน", table_cell_style),
         Paragraph("• บิลขอเบิกงวด 50% = 1,000,000 บ.<br/>• สัญญาระบุงวดที่ 1 เบิกได้แค่ 30%", table_cell_style),
         Paragraph("<font color='#B45309'><b>🟡 WARNING</b></font><br/>• เบิกเกินงวดงานไป 400,000 บ.<br/>• งวดที่ 1 จ่ายได้สูงสุด 600,000 บ.<br/>👉 <b>คำแนะนำ: ตีบิลกลับแก้ไข</b>", table_cell_style)],

        [Paragraph("<b>Case 5</b><br/>PO-2026-093", table_cell_style),
         Paragraph("ซื้อ 10 ชุด (1.2 ล้านบ.)<br/>ชุดละ 120,000 บาท", table_cell_style),
         Paragraph("• ตรวจรับได้จริงแค่ 7 ชุด (840k)<br/>• ขาด 3 ชุด (Backorder)<br/>• บิลเรียกเก็บเงินเต็ม 10 ชุด", table_cell_style),
         Paragraph("<font color='#B45309'><b>🟡 WARNING (Partial)</b></font><br/>• ปรับลดยอดตามของจริง 7 ชุด<br/>• ตัดยอดค้างส่ง 360k ออก<br/>👉 <b>ยอดจ่าย: 840,000 บ. (+VAT)</b>", table_cell_style)],

        [Paragraph("<b>Case 6</b><br/>PO-2026-094", table_cell_style),
         Paragraph("3,000,000 บาท<br/>งวดสุดท้าย (100%)", table_cell_style),
         Paragraph("• สัญญาระบุหัก Retention 5% ไว้นาน 1 ปี<br/>• แต่บิลวางขอเบิกเต็ม 3,000,000 บ.", table_cell_style),
         Paragraph("<font color='#B45309'><b>🟡 WARNING (Retention)</b></font><br/>• หัก Retention 5% (150k) ตามสัญญา<br/>• ค้างจ่ายรอครบประกัน 1 ปี<br/>👉 <b>ยอดจ่าย: 2,850,000 บ. (+VAT)</b>", table_cell_style)],

        [Paragraph("<b>Case 7</b><br/>PO-2026-095", table_cell_style),
         Paragraph("650,000 บาท<br/>PO หมดอายุ: 30 มิ.ย.", table_cell_style),
         Paragraph("• ส่งงานจริง 20 ส.ค. 2026 (หลัง PO Expire)<br/>• ไม่มีใบขอขยายเวลา PO Amendment", table_cell_style),
         Paragraph("<font color='#D97706'><b>⏸️ HOLD PAYMENT</b></font><br/>• ระงับจ่ายชั่วคราว (Hold)<br/>• ต้องให้จัดซื้อทำ PO Amendment ก่อน<br/>👉 <b>ยอดจ่าย: 0 บ. (รอเอกสาร)</b>", table_cell_style)],

        [Paragraph("<b>Case 8</b><br/>PO-2026-096", table_cell_style),
         Paragraph("500,000 บาท<br/>(3 รายการย่อย)", table_cell_style),
         Paragraph("• รวม Line Items ได้ 500,000 บ.<br/>• แต่บิลพิมพ์ Subtotal เป็น 550,000 บ.<br/>• คิดเงินเกินจริงไป 50,000 บ.", table_cell_style),
         Paragraph("<font color='#B45309'><b>🟡 WARNING (Math Error)</b></font><br/>• ตัวเลข Subtotal และ VAT คำนวณเกินจริง<br/>• ตีบิลกลับให้แก้ไขยอดที่ 500,000 บ.<br/>👉 <b>คำแนะนำ: ตีบิลกลับแก้ไข</b>", table_cell_style)]
    ]
    t_cases = Table([case_headers] + case_rows, colWidths=[72, 110, 185, 185])
    t_cases.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_cases)

    doc.build(story)
    print(f" Successfully created {pdf_filename} (8 cases)")

if __name__ == "__main__":
    build_pdf()

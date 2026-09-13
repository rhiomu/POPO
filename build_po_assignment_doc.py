import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
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

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'w:top': top, 'w:bottom': bottom, 'w:left': left, 'w:right': right}
    for border_name, border_style in borders.items():
        if border_style:
            node = OxmlElement(border_name)
            node.set(qn('w:val'), border_style.get('val', 'single'))
            node.set(qn('w:sz'), str(border_style.get('sz', 4)))
            node.set(qn('w:space'), '0')
            node.set(qn('w:color'), border_style.get('color', 'auto'))
            tcBorders.append(node)
        else:
            node = OxmlElement(border_name)
            node.set(qn('w:val'), 'nil')
            tcBorders.append(node)
    tcPr.append(tcBorders)

def set_table_borders(table, color="CBD5E1", sz="4"):
    """กำหนดเส้นขอบตารางแบบ Horizontal Dividers สไตล์ Executive Report"""
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:left w:val="none"/>
            <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(tblBorders)

def apply_table_header_and_cantsplit(table, col_widths=None):
    """
    ตั้งค่า tblHeader (ทำซ้ำหัวตารางข้ามหน้า) และ cantSplit (ป้องกันแถวขาดข้ามหน้า) ตามมาตรฐาน Word
    พร้อมตั้งค่าความกว้างคอลัมน์แบบแม่นยำ (Explicit Column Widths)
    """
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        if i == 0:
            trPr.append(OxmlElement('w:tblHeader'))
        if col_widths:
            for j, w in enumerate(col_widths):
                if j < len(row.cells):
                    row.cells[j].width = w

def set_run_font(run, font_name="Thonburi", size_pt=8.5, bold=False, italic=False, color_rgb=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb
    
    # Set complex script font for Thai support
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
    rPr.append(rFonts)

def add_heading_styled(doc, text, level=1):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(11)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    if level == 1:
        set_run_font(r, "Thonburi", size_pt=12.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))
    elif level == 2:
        set_run_font(r, "Thonburi", size_pt=10, bold=True, color_rgb=RGBColor(0x1E, 0x3A, 0x8A))
    else:
        set_run_font(r, "Thonburi", size_pt=9, bold=True, color_rgb=RGBColor(0x33, 0x41, 0x55))
    return h

def build_word_document():
    doc = Document()
    
    # Page setup (A4, Margins: Top/Bottom 0.55 in, Left/Right 0.6 in)
    for section in doc.sections:
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.6)
        section.right_margin = Inches(0.6)
        
        # Header
        header = section.header
        h_p = header.paragraphs[0]
        h_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        h_run = h_p.add_run("โจทย์: Smart PO & Invoice Auditor | สื่อการสอน Vibe Coding")
        set_run_font(h_run, "Thonburi", size_pt=7.5, color_rgb=RGBColor(0x94, 0xA3, 0xB8))

        # Footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run("โจทย์: Smart PO & Invoice Auditor | สื่อการสอน Vibe Coding")
        set_run_font(f_run, "Thonburi", size_pt=7.5, color_rgb=RGBColor(0x94, 0xA3, 0xB8))

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Thonburi'
    normal_style.font.size = Pt(8.5)
    normal_style.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)

    # =============================================================
    # PAGE 1: COVER BANNER + 30-SEC OVERVIEW + 2x2 DIAGRAM + 4 STEPS
    # =============================================================
    
    # Header Banner Table (Executive Forest Green #1B4D3E)
    t_banner = doc.add_table(rows=1, cols=1)
    t_banner.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_banner = t_banner.rows[0].cells[0]
    set_cell_background(c_banner, "1B4D3E")
    set_cell_margins(c_banner, top=130, bottom=130, left=180, right=180)
    
    p_b = c_banner.paragraphs[0]
    p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_b.paragraph_format.line_spacing = 1.15
    
    # Tag Badge
    r_badge = p_b.add_run("  โจทย์ที่ 3 : DATA FUSION & ENTERPRISE AUDIT AI  \n")
    set_run_font(r_badge, "Thonburi", size_pt=9.5, bold=True, color_rgb=RGBColor(0x6E, 0xEE, 0xB4))
    
    # Title
    r_title = p_b.add_run("Smart PO & Invoice Auditor\n")
    set_run_font(r_title, "Arial", size_pt=17.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))
    
    # Subtitle
    r_sub = p_b.add_run("สร้างเว็บแอปตรวจเช็คบิลคู่ค้าอัตโนมัติด้วย AI — ดึงข้อมูล PO ชนใบแจ้งหนี้ PDF เพื่อสกัดจับยอดงอก, ค่าปรับส่งช้า, ของขาด, เงินประกัน, และความเสี่ยงโอนเงินผิดบัญชี\n\n")
    set_run_font(r_sub, "Thonburi", size_pt=8.5, color_rgb=RGBColor(0xD1, 0xFA, 0xE5))
    
    # Meta bar
    r_meta = p_b.add_run("⏱ เวลาโดยประมาณ: 90–120 นาที   |   🎯 เป้าหมาย: ผ่านครบ 6 requirement ขั้นต่ำ   |   💻 รูปแบบ: Vibe Coding")
    set_run_font(r_meta, "Thonburi", size_pt=8.5, bold=True, color_rgb=RGBColor(0xFA, 0xCC, 0x15))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # 2. เข้าใจภาพใน 30 วินาที
    add_heading_styled(doc, "เข้าใจภาพใน 30 วินาที", level=1)

    # Callout Box (Thick Forest Green left border)
    t_callout = doc.add_table(rows=1, cols=1)
    t_callout.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_callout = t_callout.rows[0].cells[0]
    set_cell_background(c_callout, "F4F9F6")
    set_cell_margins(c_callout, top=70, bottom=70, left=140, right=140)
    set_cell_borders(c_callout, left={'val': 'single', 'sz': 24, 'color': '1B4D3E'})
    p_c = c_callout.paragraphs[0]
    p_c.paragraph_format.line_spacing = 1.15
    r_c = p_c.add_run("นี่คือสิ่งที่เกิดขึ้นตั้งแต่ฝ่ายบัญชีเปิดระบบ เลือกเลขที่ PO จากฐานข้อมูล อัปโหลดไฟล์บิล PDF ของคู่ค้า และให้ AI วิเคราะห์เปรียบเทียบความถูกต้อง จนถึงการออกคำแนะนำว่า 'ควรจ่ายเต็มจำนวน, ปรับลดตามยอดตรวจรับจริง, หักเงินประกันผลงาน, หรือสั่งระงับการจ่ายเงินทันทีเพราะเสี่ยงทุจริต' — ทุกอย่างเกิดขึ้นแบบ Data-Driven และอัตโนมัติ")
    set_run_font(r_c, "Thonburi", size_pt=8, color_rgb=RGBColor(0x1F, 0x29, 0x37))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Embed 2x2 Flow Diagram Image (Figure 1)
    if os.path.exists("assets/diagram_30s.png"):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(1)
        run_img = p_img.add_run()
        run_img.add_picture("assets/diagram_30s.png", width=Inches(6.5))

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(3)
        r_cap = p_cap.add_run("Figure 1: ตัวอย่างจริง แสดงขั้นตอนการดึง PO จาก Database, สกัดบิล PDF, AI ตรวจจับ 8 มิติ และหน้าแจ้งเตือน Action")
        set_run_font(r_cap, "Thonburi", size_pt=7, italic=True, color_rgb=RGBColor(0x64, 0x74, 0x8B))

    # 4-Step Summary Table (With tblHeader and cantSplit)
    t_steps = doc.add_table(rows=2, cols=4)
    t_steps.alignment = WD_TABLE_ALIGNMENT.CENTER
    step_widths = [Inches(1.65), Inches(1.65), Inches(1.65), Inches(1.65)]
    step_headers = ["❶ ดึงข้อมูล PO จาก DB", "❷ สกัดข้อความบิล PDF", "❸ AI วินิจฉัย 8 มิติ", "❹ ออกคำสั่ง & Action"]
    step_descs = [
        "เชื่อมต่อ SQLite ดึงข้อมูล PO, Vendor Master, วงเงินอนุมัติ, เครดิตเทอม",
        "รับ Invoice & Contract PDF สกัดข้อความภาษาไทย/อังกฤษออกมาอัตโนมัติ",
        "ตรวจยอดงอก, ค่าปรับส่งช้า, บัญชีปลอม, งวดงาน, ส่งของขาด, Retention, วันหมดอายุ, เลขผิด",
        "แสดงสถานะ [APPROVED] / [WARNING] / [HOLD] / [FRAUD ALERT] พร้อมปุ่ม Copy สรุปส่งอีเมล"
    ]
    for i in range(4):
        c_h = t_steps.rows[0].cells[i]
        set_cell_background(c_h, "1B4D3E")
        set_cell_margins(c_h, top=50, bottom=50, left=55, right=55)
        p = c_h.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(step_headers[i])
        set_run_font(r, "Thonburi", size_pt=8, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

        c_d = t_steps.rows[1].cells[i]
        set_cell_background(c_d, "F8FAFC")
        set_cell_margins(c_d, top=45, bottom=45, left=55, right=55)
        p2 = c_d.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(step_descs[i])
        set_run_font(r2, "Thonburi", size_pt=7, color_rgb=RGBColor(0x33, 0x41, 0x55))

    set_table_borders(t_steps, color="CBD5E1")
    apply_table_header_and_cantsplit(t_steps, step_widths)

    # END OF PAGE 1 -> PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # PAGE 2: 1. BUSINESS PROBLEM & CONTEXT + 2. DATA SPECIFICATIONS
    # =============================================================
    add_heading_styled(doc, "1. โจทย์นี้ต้องการอะไร (Business Problem & Context)", level=1)
    
    p_prob = doc.add_paragraph("ในทุกสิ้นเดือน ฝ่ายจัดซื้อและฝ่ายบัญชีการเงินขององค์กรต้องเผชิญกับภาระงานมหาศาลในการเปิดหน้าจอ 2 จอสลับไปมา ระหว่าง 'ข้อมูลคำสั่งซื้อในระบบ ERP/Database (Purchase Order: PO)' กับ 'ไฟล์เอกสารใบแจ้งหนี้/ใบกำกับภาษี (Invoice PDF)' ที่คู่ค้าส่งมาเรียกเก็บเงิน")
    p_prob.paragraph_format.line_spacing = 1.15

    p_why = doc.add_paragraph("ทำไมเรื่องนี้ถึงต้องใช้ระบบ AI ช่วยตัดสินใจ?")
    p_why.paragraph_format.line_spacing = 1.15
    p_why.paragraph_format.space_before = Pt(3)
    r_why = p_why.runs[0]
    set_run_font(r_why, "Thonburi", size_pt=8.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))

    reasons = [
        ("1. ลืมคิดค่าปรับ / ไม่ตรวจยอดงอก = ขาดทุนทันที: ", "คู่ค้าส่งมอบงานล่าช้า หรือแอบสอดไส้ค่าบริการฉุกเฉินนอกสัญญาหลัก หากพนักงานตรวจผ่านไปโดยไม่ทักท้วง องค์กรจะสูญเงินฟรีหลักหมื่นถึงหลักแสนบาท"),
        ("2. สวมรอยบิล / เลขบัญชีไม่ตรง = เสียหายหนัก: ", "มิจฉาชีพสร้างบิลปลอมโดยใช้ชื่อบริษัทคล้ายกัน แต่เปลี่ยนเลขประจำตัวผู้เสียภาษีและเลขบัญชีธนาคาร หากไม่มีระบบ Cross-check อัตโนมัติ อาจเกิดความเสียหายระดับหลายล้านบาท"),
        ("3. เอกสารหนา ตรวจสอบด้วยคนช้ามาก: ", "แต่ละโครงการมีสัญญาแนบท้ายหลายหน้า พนักงานมนุษย์ต้องใช้เวลาเปิดอ่านทีละข้อ ทำให้เกิดคอขวดในกระบวนการเบิกจ่ายสิ้นเดือน")
    ]
    for title, desc in reasons:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.line_spacing = 1.15
        p_r.paragraph_format.left_indent = Inches(0.2)
        r_t = p_r.add_run(title)
        set_run_font(r_t, "Thonburi", size_pt=8, bold=True, color_rgb=RGBColor(0x99, 0x1B, 0x1B))
        r_d = p_r.add_run(desc)
        set_run_font(r_d, "Thonburi", size_pt=8, color_rgb=RGBColor(0x1F, 0x29, 0x37))

    # 8 Traps in Business Reality
    p_traps_head = doc.add_paragraph("8 จุดดักในชีวิตจริงที่ระบบต้องสกัดจับ (The 8 Real-World Enterprise Traps):")
    p_traps_head.paragraph_format.space_before = Pt(3)
    p_traps_head.paragraph_format.space_after = Pt(2)
    set_run_font(p_traps_head.runs[0], "Thonburi", size_pt=8.5, bold=True, color_rgb=RGBColor(0x1E, 0x3A, 0x8A))

    traps = [
        ("1. ยอดงอกนอกใบ PO (Unapproved Scope Charges): ", "คู่ค้าสอดไส้ค่าบริการฉุกเฉิน ค่าเดินทาง หรือค่าวัสดุที่ไม่ได้ตกลงไว้ในสัญญาหลัก"),
        ("2. ส่งงานล่าช้ากว่ากำหนด (Late Delivery Penalty): ", "คู่ค้าส่งมอบงานช้า แต่ไม่มีการคำนวณหักค่าเสียหายจากการล่าช้า (Liquidated Damages 0.1%/วัน)"),
        ("3. ความเสี่ยงทุจริต/สวมรอยบิล (Fraud & Diversion Risk): ", "เลขประจำตัวผู้เสียภาษี 13 หลัก หรือเลขบัญชีธนาคารไม่ตรงกับ Vendor Master"),
        ("4. เบิกเงินเกินงวดงาน (Over-milestone Billing): ", "สัญญากำหนดแคปงวดที่ 1 ไว้ 30% แต่วางบิลขอเบิก 50% เกินสิทธิ์"),
        ("5. ตรวจรับของไม่ครบ (Partial Delivery & Backorder): ", "สั่ง 10 ชุด ได้รับจริง 7 ชุด ของขาด 3 ชุด แต่วางบิลเรียกเก็บเงินเต็ม 10 ชุด"),
        ("6. การหักเงินค้ำประกันผลงาน (Warranty Retention 5%): ", "สัญญาระบุงวดสุดท้ายต้องหัก Retention 5% ไว้นาน 1 ปี แต่วางบิลขอเบิกเต็ม 100%"),
        ("7. PO หมดอายุสัญญา (Expired PO / Missing Amendment): ", "ส่งมอบงานหลังวันสิ้นสุดสัญญาโดยไม่มีใบขอขยายเวลา PO Amendment"),
        ("8. ข้อผิดพลาดทางคณิตศาสตร์ (Line Items vs Subtotal Error): ", "ผลรวมของรายการย่อยไม่ตรงกับยอด Subtotal และภาษี VAT ท้ายบิล")
    ]
    for title, desc in traps:
        p_t = doc.add_paragraph(style='List Bullet')
        p_t.paragraph_format.line_spacing = 1.12
        p_t.paragraph_format.left_indent = Inches(0.2)
        r_t = p_t.add_run(title)
        set_run_font(r_t, "Thonburi", size_pt=7.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))
        r_d = p_t.add_run(desc)
        set_run_font(r_d, "Thonburi", size_pt=7.5, color_rgb=RGBColor(0x33, 0x41, 0x55))

    p_sol = doc.add_paragraph()
    p_sol.paragraph_format.line_spacing = 1.15
    p_sol.paragraph_format.space_before = Pt(3)
    r_sol_lbl = p_sol.add_run("สิ่งที่ผู้เรียนต้องสร้าง: ")
    set_run_font(r_sol_lbl, "Thonburi", size_pt=8.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))
    r_sol_txt = p_sol.add_run("เว็บแอปพลิเคชัน Operations & Audit Dashboard แบบ Single-Port บน Port 8000 ที่เชื่อมต่อกับ SQLite Database เพื่อดึงข้อมูล PO และอัปโหลดบิล Invoice & Contract PDF พร้อมระบบ AI ที่ช่วยวิเคราะห์และแจ้งเตือนทันทีว่า: 'บิลใบนี้อนุมัติจ่ายได้หรือไม่? ต้องปรับลดยอดเท่าไหร่? หรือต้องสั่งระงับการจ่ายเงินทันทีเพราะเสี่ยงทุจริต?'")
    set_run_font(r_sol_txt, "Thonburi", size_pt=8, color_rgb=RGBColor(0x1F, 0x29, 0x37))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # 2. สิ่งที่คุณได้รับ
    add_heading_styled(doc, "2. สิ่งที่คุณได้รับ (Data Specifications & Mock Documents)", level=1)
    
    # Note callout: NO API Provided, build everything via Vibe Coding
    t_no_api = doc.add_table(rows=1, cols=1)
    t_no_api.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_na = t_no_api.rows[0].cells[0]
    set_cell_background(c_na, "EFF6FF")
    set_cell_margins(c_na, top=50, bottom=50, left=100, right=100)
    set_cell_borders(c_na, left={'val': 'single', 'sz': 18, 'color': '1E3A8A'})
    p_na = c_na.paragraphs[0]
    r_na_b = p_na.add_run("📌 ข้อความสำคัญ: ")
    set_run_font(r_na_b, "Thonburi", size_pt=8, bold=True, color_rgb=RGBColor(0x1E, 0x3A, 0x8A))
    r_na_t = p_na.add_run("ในโจทย์ข้อนี้ 'ไม่มี Endpoint สำเร็จรูปให้ใช้งาน' สิ่งที่ผู้เรียนจะได้รับคือ 1. ไฟล์เอกสารโจทย์ฉบับนี้ 2. ไฟล์ฐานข้อมูล SQLite enterprise.db และ 3. ไฟล์เอกสาร PDF จำลองใน sample_documents/ โดยผู้เรียนจะใช้การ Vibe Coding สร้างระบบ Backend, Frontend, และ Audit Engine ขึ้นมาเองทั้งหมด!")
    set_run_font(r_na_t, "Thonburi", size_pt=8, color_rgb=RGBColor(0x1E, 0x29, 0x3B))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    add_heading_styled(doc, "2.1 ฐานข้อมูลจำลอง: enterprise.db (SQLite)", level=2)

    # Table 1: vendor_master
    p_t1 = doc.add_paragraph("ตารางที่ 1: vendor_master (ฐานข้อมูลคู่ค้าที่ผ่านการรับรอง):")
    set_run_font(p_t1.runs[0], "Thonburi", size_pt=8, bold=True, color_rgb=RGBColor(0x1E, 0x3A, 0x8A))

    t_vm = doc.add_table(rows=6, cols=4)
    t_vm.alignment = WD_TABLE_ALIGNMENT.CENTER
    vm_widths = [Inches(1.2), Inches(0.9), Inches(1.9), Inches(2.6)]
    vm_headers = ["ชื่อฟิลด์ (Column)", "ชนิดข้อมูล", "ตัวอย่างข้อมูล", "ความหมายและการนำไปใช้งาน"]
    for j, h in enumerate(vm_headers):
        c = t_vm.rows[0].cells[j]
        set_cell_background(c, "1B4D3E")
        set_cell_margins(c, top=40, bottom=40, left=55, right=55)
        p = c.paragraphs[0]
        r = p.add_run(h)
        set_run_font(r, "Thonburi", size_pt=7.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

    vm_data = [
        ("vendor_id", "TEXT (PK)", "'VN-001' ถึง 'VN-008'", "รหัสประจำตัวคู่ค้าในระบบ ERP"),
        ("tax_id", "TEXT", "'0105556098711'", "เลขประจำตัวผู้เสียภาษี 13 หลัก (ใช้ตรวจจับบิลปลอม)"),
        ("vendor_name", "TEXT", "'บริษัท กังหัน เอ็นจิเนียริ่ง...'", "ชื่อบริษัทคู่ค้าที่จดทะเบียนทางการ"),
        ("bank_name", "TEXT", "'ธนาคารกสิกรไทย'", "ชื่อธนาคารบัญชีทางการของคู่ค้า"),
        ("bank_account", "TEXT", "'045-2-12345-6'", "เลขที่บัญชีธนาคารทางการ (ตรวจจับความเสี่ยง Fraud)")
    ]
    for i, row in enumerate(vm_data, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t_vm.rows[i].cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=30, bottom=30, left=50, right=50)
            p = c.paragraphs[0]
            r = p.add_run(val)
            set_run_font(r, "Thonburi", size_pt=7.5)

    set_table_borders(t_vm, color="CBD5E1")
    apply_table_header_and_cantsplit(t_vm, vm_widths)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Table 2: purchase_orders
    p_t2 = doc.add_paragraph("ตารางที่ 2: purchase_orders (ข้อมูลใบสั่งซื้อที่อนุมัติแล้ว):")
    set_run_font(p_t2.runs[0], "Thonburi", size_pt=8, bold=True, color_rgb=RGBColor(0x1E, 0x3A, 0x8A))

    t_po = doc.add_table(rows=8, cols=4)
    t_po.alignment = WD_TABLE_ALIGNMENT.CENTER
    po_widths = [Inches(1.3), Inches(0.9), Inches(1.4), Inches(3.0)]
    po_headers = ["ชื่อฟิลด์ (Column)", "ชนิดข้อมูล", "ตัวอย่างข้อมูล", "ความหมายและการนำไปใช้งาน"]
    for j, h in enumerate(po_headers):
        c = t_po.rows[0].cells[j]
        set_cell_background(c, "1B4D3E")
        set_cell_margins(c, top=40, bottom=40, left=55, right=55)
        p = c.paragraphs[0]
        r = p.add_run(h)
        set_run_font(r, "Thonburi", size_pt=7.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

    po_data = [
        ("po_number", "TEXT (PK)", "'PO-2026-089'", "เลขที่ใบสั่งซื้อหลัก"),
        ("vendor_id", "TEXT (FK)", "'VN-001'", "รหัสคู่ค้า เชื่อมโยงกับ vendor_master"),
        ("project_site", "TEXT", "'G.Brimm Power'", "ชื่อโครงการ / ไซต์โรงไฟฟ้าหรือโรงงาน"),
        ("scope_of_work", "TEXT", "'งานซ่อมบำรุงกังหันก๊าซ'", "ขอบเขตงานที่ได้รับอนุมัติให้จัดซื้อ"),
        ("approved_amount", "REAL", "1000000.00", "วงเงินงบประมาณที่อนุมัติ (บาท ก่อน VAT)"),
        ("standard_credit_days", "INTEGER", "30", "เครดิตเทอมมาตรฐานที่ตกลงไว้ (วัน)"),
        ("valid_until", "TEXT", "'2026-12-31'", "วันสิ้นสุดอายุสัญญา PO (ตรวจจับ Expired PO)")
    ]
    for i, row in enumerate(po_data, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t_po.rows[i].cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=30, bottom=30, left=50, right=50)
            p = c.paragraphs[0]
            r = p.add_run(val)
            set_run_font(r, "Thonburi", size_pt=7.5)

    set_table_borders(t_po, color="CBD5E1")
    apply_table_header_and_cantsplit(t_po, po_widths)

    # END OF PAGE 2 -> PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # PAGE 3: 2.2 SAMPLE DOCS + 2.3 OUTPUT SPEC + 3. CORE REQUIREMENTS + MOCKUP
    # =============================================================
    add_heading_styled(doc, "2.2 โฟลเดอร์เอกสารคู่ค้า: sample_documents/ (8 เคส รวม 16 ไฟล์)", level=2)
    p_sd = doc.add_paragraph("ในโฟลเดอร์ sample_documents/ ประกอบด้วยไฟล์ PDF จำลอง 8 ชุดสถานการณ์ แต่ละชุดมี 2 ไฟล์ ได้แก่ Invoice (บิลเรียกเก็บเงิน) และ Contract (สัญญาแนบท้าย/ใบตรวจรับงาน) ตัวอย่างข้อความที่สกัดได้จริงจากเอกสาร:")
    p_sd.paragraph_format.line_spacing = 1.12

    # Code Snippet Example from PDF Text Extraction
    t_snippet = doc.add_table(rows=1, cols=1)
    t_snippet.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_sn = t_snippet.rows[0].cells[0]
    set_cell_background(c_sn, "1E293B")
    set_cell_margins(c_sn, top=55, bottom=55, left=90, right=90)
    p_sn = c_sn.paragraphs[0]
    code_text = """[Case1_Invoice_PO089.pdf]
Supplier: KangHan Engineering & Service Co., Ltd.
Tax ID: 0105556098711 | Bank: Kasikorn 045-2-12345-6 | PO Ref: PO-2026-089 | Payment Term: 15 Days
Line Items:
  - Gas turbine maintenance: 1,000,000.00 THB
  - Emergency mobilization fee: 20,000.00 THB (Extra Scope Charge)
Subtotal: 1,020,000.00 THB | VAT 7%: 71,400.00 THB | Total Due: 1,091,400.00 THB

[Case1_Contract_PO089.pdf]
TERMS & SERVICE AGREEMENT: Ref PO-2026-089 | Standard Credit: 30 days
Penalty Clause: Scheduled deadline Aug 15, 2026. Actual completion Aug 25, 2026 (10 days delayed).
Delay exceeding 7 days incurs liquidated damages at 0.1%/day (10 days x 0.1% = 10,000 THB deduction)."""
    r_sn = p_sn.add_run(code_text)
    set_run_font(r_sn, "Courier New", size_pt=7, color_rgb=RGBColor(0x93, 0xC5, 0xFD))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    add_heading_styled(doc, "2.3 โครงสร้างผลลัพธ์ที่ระบบของคุณต้องออกแบบส่งมอบ (Expected Output Specifications)", level=2)
    p_out = doc.add_paragraph("เมื่อผู้เรียนพัฒนาเว็บแอปพลิเคชันขึ้นมา ระบบต้องประมวลผลและส่งมอบผลลัพธ์การวินิจฉัย 5 ส่วนสำคัญบนหน้าจอ:")
    p_out.paragraph_format.line_spacing = 1.12

    out_items = [
        ("1. Decision Status Badge: ", "ป้ายสถานะผลการวินิจฉัยหลัก ([APPROVED] / [WARNING] / [HOLD PAYMENT] / [FRAUD ALERT]) พร้อมสีเด่นชัด"),
        ("2. Discrepancies Findings List: ", "รายการข้อตรวจพบความผิดปกติ แสดงหัวข้อ, รายละเอียดตัวเลข, และผลกระทบต่อองค์กร"),
        ("3. Side-by-Side Comparison Matrix: ", "ตารางเปรียบเทียบข้อมูลคู่ขนาน (ข้อมูลใน PO vs ข้อมูลที่อ่านได้จริงจากบิล PDF)"),
        ("4. Financial Breakdown: ", "สรุปตัวเลขทางการเงิน (วงเงิน PO, ยอดงอก, ค่าปรับ, ของขาด, Retention, ยอดสุทธิก่อน VAT, VAT 7%, ยอดจ่ายรวม)"),
        ("5. Executive Email Summary: ", "กล่องข้อความสรุปทางการ พร้อมปุ่มคัดลอก (Copy) สำหรับส่งต่อทาง Email หรือ ERP")
    ]
    for ot, od in out_items:
        p_oi = doc.add_paragraph(style='List Bullet')
        p_oi.paragraph_format.line_spacing = 1.1
        p_oi.paragraph_format.left_indent = Inches(0.2)
        r_ot = p_oi.add_run(ot)
        set_run_font(r_ot, "Thonburi", size_pt=7.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))
        r_od = p_oi.add_run(od)
        set_run_font(r_od, "Thonburi", size_pt=7.5, color_rgb=RGBColor(0x33, 0x41, 0x55))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # 3. ข้อกำหนดขั้นต่ำ (Core Requirements)
    add_heading_styled(doc, "3. ข้อกำหนดขั้นต่ำ (Core Requirements Checklist)", level=1)
    doc.add_paragraph("เพื่อให้ระบบทำงานได้อย่างสมบูรณ์ ผู้เรียนต้องพัฒนาเว็บแอปพลิเคชันให้ผ่านเกณฑ์ทั้ง 6 ข้อดังนี้:")

    reqs = [
        ("Requirement 1: PO Selector & Database Lookup", "มี Dropdown ให้เลือกเลขที่ PO จากฐานข้อมูล SQLite enterprise.db เมื่อเลือกแล้วระบบต้องดึงข้อมูลจริง (เลขที่ PO, ชื่อคู่ค้า, ไซต์งาน, วงเงินอนุมัติ, เครดิตเทอม, Tax ID) มาแสดงในการ์ดอย่างถูกต้อง"),
        ("Requirement 2: PDF Upload & Text Extractor", "มีช่องให้อัปโหลดไฟล์ PDF 2 ไฟล์ (Invoice และ Contract) และมีระบบสกัดข้อความ (Text Extraction) ออกมาจาก PDF โดยรองรับภาษาไทยและอังกฤษ"),
        ("Requirement 3: Side-by-Side Comparison Matrix", "แสดงตารางหรือการ์ดเปรียบเทียบข้อมูลสำคัญแบบคู่ขนาน (ข้อมูลในระบบ PO vs ข้อมูลที่อ่านได้จากบิล PDF) เพื่อให้เจ้าหน้าที่มองเห็นความแตกต่างได้ทันที"),
        ("Requirement 4: Smart AI Audit & Anomaly Detection", "มีสมองกล AI ตรวจจับจุดผิดปกติทั้ง 8 มิติ: 1) ยอดงอก 2) ค่าปรับส่งช้า 3) Tax ID/บัญชีปลอม 4) เบิกเกินงวด 5) ส่งของไม่ครบ 6) ลืมหัก Retention 7) PO หมดอายุ 8) บิลคิดเลขผิด"),
        ("Requirement 5: Action Recommendation & Status Badges", "แสดงป้ายสถานะและคำแนะนำการจ่ายเงินที่เด่นชัด: [APPROVED] (อนุมัติจ่าย) / [WARNING] (ปรับลดยอดจ่าย) / [HOLD PAYMENT] (ระงับชั่วคราว) / [FRAUD ALERT] (ระงับทันที) พร้อมระบุยอดสุทธิ"),
        ("Requirement 6: Email / Audit Summary Copy Generator", "มีปุ่มกด 'คัดลอกผลสรุปการตรวจเช็ค' ที่จัดรูปแบบข้อความสรุปทางการ สำหรับนำไปส่งต่อทาง Email หรือ ERP ให้ผู้บริหารลงนามได้ทันที")
    ]
    for r_title, r_desc in reqs:
        p_req = doc.add_paragraph()
        p_req.paragraph_format.line_spacing = 1.12
        p_req.paragraph_format.space_before = Pt(2)
        p_req.paragraph_format.space_after = Pt(1)
        
        # Checkbox symbol U+2610
        r_box = p_req.add_run("☐   " + r_title + "\n")
        set_run_font(r_box, "Thonburi", size_pt=8.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))
        
        r_d = p_req.add_run("      " + r_desc)
        set_run_font(r_d, "Thonburi", size_pt=7.5, color_rgb=RGBColor(0x47, 0x55, 0x69))

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Embed Dashboard UI Mockup (Figure 2)
    if os.path.exists("assets/dashboard_mockup.png"):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.paragraph_format.space_before = Pt(2)
        p_img2.paragraph_format.space_after = Pt(1)
        run_img2 = p_img2.add_run()
        run_img2.add_picture("assets/dashboard_mockup.png", width=Inches(6.0))

        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(2)
        r_cap2 = p_cap2.add_run("Figure 2: ตัวอย่างหน้าจอ Operations & Audit Dashboard ที่ผู้เรียนต้องพัฒนา (Single-Port บน Port 8000)")
        set_run_font(r_cap2, "Thonburi", size_pt=7, italic=True, color_rgb=RGBColor(0x64, 0x74, 0x8B))

    # END OF PAGE 3 -> PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # PAGE 4: 4. BUSINESS LOGIC & FORMULAS + GROUND TRUTH MATRIX
    # =============================================================
    add_heading_styled(doc, "4. สูตรคำนวณและเกณฑ์ทางธุรกิจ (Business Logic & Ground Truth)", level=1)

    # Table of Formulas (With tblHeader and cantSplit)
    t_form = doc.add_table(rows=6, cols=3)
    t_form.alignment = WD_TABLE_ALIGNMENT.CENTER
    form_widths = [Inches(1.8), Inches(2.0), Inches(2.8)]
    form_headers = ["ชื่อสูตร / ตัวชี้วัด", "สมการคำนวณ (Formula)", "คำอธิบายทางธุรกิจและข้อกำหนด"]
    for j, h in enumerate(form_headers):
        c = t_form.rows[0].cells[j]
        set_cell_background(c, "1B4D3E")
        set_cell_margins(c, top=35, bottom=35, left=50, right=50)
        p = c.paragraphs[0]
        r = p.add_run(h)
        set_run_font(r, "Thonburi", size_pt=7.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

    form_data = [
        ("1. Liquidated Damages\n(ค่าปรับส่งมอบงานล่าช้า)", "วันล่าช้า × 0.1% × วงเงิน PO\n(หากล่าช้าเกิน 7 วันตามสัญญา)", "คำนวณหักค่าเสียหายจากการส่งมอบงานล่าช้าตามสัญญา (เช่น ช้า 10 วัน หัก 10,000 บ.)"),
        ("2. Unapproved Scope Deduction\n(ตัดยอดงอกนอกสัญญา)", "ยอดบิลเรียกเก็บ - วงเงิน PO\n(เฉพาะรายการที่ไม่มีใน PO)", "สอดไส้ค่าบริการฉุกเฉิน/ค่าเดินทาง ต้องตัดทิ้งทั้งจำนวน ไม่อนุมัติเบิกจ่าย"),
        ("3. Partial Delivery Adjustment\n(หักยอดของค้างส่ง)", "ราคาต่อหน่วย × จำนวนชิ้นที่ขาด\n(120,000 บ. × 3 ชุด = 360,000 บ.)", "กรณีคลังตรวจรับได้จริงไม่ครบตาม PO ให้จ่ายเฉพาะยอดของที่ได้รับตรวจรับจริง"),
        ("4. Warranty Retention (5%)\n(เงินค้ำประกันผลงาน)", "วงเงินงวดสุดท้าย × 5%\n(3,000,000 บ. × 5% = 150,000 บ.)", "หักเงินประกันผลงาน 5% ไว้จ่ายหลังสิ้นสุดระยะเวลารับประกัน 1 ปี"),
        ("5. Net Payable Amount\n(ยอดเงินอนุมัติจ่ายสุทธิ)", "ยอดที่อนุมัติ - ค่าปรับ - ของขาด - Retention\n(+ VAT 7% ของยอดสุทธิ)", "ยอดเงินที่ฝ่ายบัญชีต้องโอนให้คู่ค้าจริง (พร้อมคำนวณ VAT 7% ให้ถูกต้อง)")
    ]
    for i, row in enumerate(form_data, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t_form.rows[i].cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=25, bottom=25, left=45, right=45)
            p = c.paragraphs[0]
            r = p.add_run(val)
            set_run_font(r, "Thonburi", size_pt=7)

    set_table_borders(t_form, color="CBD5E1")
    apply_table_header_and_cantsplit(t_form, form_widths)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # Ground Truth Test Matrix (8 Cases)
    add_heading_styled(doc, "ตารางเฉลยเคสทดสอบทั้ง 8 เคส (Ground Truth Matrix)", level=2)

    t_gt = doc.add_table(rows=9, cols=4)
    t_gt.alignment = WD_TABLE_ALIGNMENT.CENTER
    gt_widths = [Inches(1.1), Inches(1.6), Inches(2.1), Inches(1.8)]
    gt_headers = ["ชุดทดสอบ", "ข้อมูลใน PO (ฐานข้อมูล)", "สภาพข้อเท็จจริงในเอกสาร PDF", "ผลการวินิจฉัย & ป้ายสถานะ"]
    for j, h in enumerate(gt_headers):
        c = t_gt.rows[0].cells[j]
        set_cell_background(c, "1B4D3E")
        set_cell_margins(c, top=35, bottom=35, left=50, right=50)
        p = c.paragraphs[0]
        r = p.add_run(h)
        set_run_font(r, "Thonburi", size_pt=7.5, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

    gt_data = [
        ("Case 1\nPO-2026-089", "วงเงิน 1,000,000 บาท\nเครดิตเทอม 30 วัน", "• มียอดงอก 20,000 บ. (Emergency Fee)\n• ส่งงานช้า 10 วัน (ปรับ 0.1%/วัน = 10,000 บ.)\n• บิลขอเครดิตเทอม 15 วัน", "[WARNING]\n• ตัดยอดงอก 20,000 บ.\n• หักค่าปรับล่าช้า 10,000 บ.\n-> ยอดจ่ายสุทธิ: 990,000 บ. (+VAT)"),
        ("Case 2\nPO-2026-090", "วงเงิน 450,000 บาท\nเครดิตเทอม 45 วัน\nธนาคาร SCB", "• ส่งมอบตรงเวลา ผ่าน QC ครบ 100%\n• ยอดเงิน 450,000 บาท ตรงตาม PO เป๊ะ\n• Tax ID และเลขบัญชีถูกต้องครบถ้วน", "[APPROVED]\n• ข้อมูลถูกต้องตามสัญญาทุกประการ\n• ไม่มีค่าปรับ ไม่มียอดงอก\n-> ยอดจ่ายสุทธิ: 450,000 บ. (+VAT)"),
        ("Case 3\nPO-2026-091", "Vendor: VN-003\nTax ID: 0105562045678\nBBL: 201-0-55443-3", "• Tax ID บนบิลเป็น 0995559999999 (ไม่ตรง!)\n• ธนาคารบนบิลระบุ SCB 999-9-99999-9 (ไม่ตรง!)", "[FRAUD ALERT]\n• ตรวจพบความเสี่ยงทุจริตสวมรอยบิล!\n• Tax ID และเลขบัญชีไม่ตรงกับระบบ\n-> คำสั่ง: ระงับการจ่ายเงินทันที"),
        ("Case 4\nPO-2026-092", "วงเงินรวม 2,000,000 บาท\nเครดิตเทอม 30 วัน", "• บิลขอเบิกงวด 50% = 1,000,000 บาท\n• สัญญาระบุงวดที่ 1 เบิกได้สูงสุด 30% (600,000 บาท)", "[WARNING]\n• เบิกเงินเกินงวดงานไป 400,000 บ.\n• งวดที่ 1 จ่ายได้สูงสุด 600,000 บ.\n-> คำแนะนำ: ให้คู่ค้าแก้ไขยอดตามงวด"),
        ("Case 5\nPO-2026-093", "ซื้อ 10 ชุด (1,200,000 บ.)\nชุดละ 120,000 บาท", "• ตรวจรับจริงได้ 7 ชุด (840,000 บ.) ขาด 3 ชุด\n• แต่บิลเรียกเก็บเงินเต็ม 10 ชุด (1.2 ล้านบ.)", "[WARNING]\n• ปรับลดยอดตามของจริง 7 ชุด\n• ตัดยอดของค้างส่ง 360,000 บ. ออก\n-> ยอดจ่ายสุทธิ: 840,000 บ. (+VAT)"),
        ("Case 6\nPO-2026-094", "วงเงิน 3,000,000 บาท\nงวดสุดท้าย (Final 100%)", "• สัญญาระบุหักเงินค้ำประกันผลงาน 5% (150,000 บ.)\n• แต่บิลขอเบิกเต็ม 3 ล้าน ไม่ยอมหักเงินประกัน", "[WARNING]\n• หัก Retention 5% (150,000 บ.) ตามสัญญา\n• ค้างจ่ายไว้รอครบระยะรับประกัน 1 ปี\n-> ยอดจ่ายสุทธิ: 2,850,000 บ. (+VAT)"),
        ("Case 7\nPO-2026-095", "วงเงิน 650,000 บาท\nPO หมดอายุ: 30 มิ.ย. 2026", "• ส่งมอบงานจริงวันที่ 20 ส.ค. 2026 (ส่งหลัง PO หมดอายุ)\n• ไม่มีเอกสารใบขอขยายสัญญา PO Amendment", "[HOLD PAYMENT]\n• ระงับการจ่ายเงินชั่วคราว (Hold)\n• ต้องให้จัดซื้อทำ PO Amendment ขยายเวลาก่อน"),
        ("Case 8\nPO-2026-096", "วงเงิน 500,000 บาท\n(200k + 180k + 120k)", "• รายการย่อย 3 รายการรวมได้ 500,000 บาท\n• แต่บิลคิดเลขผิดระบุ Subtotal 550,000 บ. (เกิน 50k)", "[WARNING]\n• ตรวจพบบิลคิดเลขผิดเกินไป 50,000 บ.\n• ภาษี VAT 7% คำนวณบนฐานที่ผิด\n-> คำแนะนำ: ตีบิลกลับให้แก้ไขยอด")
    ]
    for i, row in enumerate(gt_data, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t_gt.rows[i].cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=25, bottom=25, left=45, right=45)
            p = c.paragraphs[0]
            r = p.add_run(val)
            set_run_font(r, "Thonburi", size_pt=7)
            if "[APPROVED]" in val:
                r.font.color.rgb = RGBColor(0x15, 0x80, 0x3D)
            elif "[WARNING]" in val:
                r.font.color.rgb = RGBColor(0xB4, 0x53, 0x09)
            elif "[HOLD PAYMENT]" in val:
                r.font.color.rgb = RGBColor(0xD9, 0x77, 0x06)
            elif "[FRAUD ALERT]" in val:
                r.font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C)

    set_table_borders(t_gt, color="CBD5E1")
    apply_table_header_and_cantsplit(t_gt, gt_widths)

    # END OF PAGE 4 -> PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # PAGE 5: 5. AI PROMPT GUIDE (3 MAIN RHYTHMS + 2 EXTENSIONS)
    # =============================================================
    add_heading_styled(doc, "5. แนวทางการ Prompt 3 จังหวะสำหรับนักเรียน Vibe Coding (AI Guide)", level=1)
    doc.add_paragraph("เพื่อให้การสั่งงาน AI ได้ผลลัพธ์ที่แม่นยำ ไม่หลงทาง และปฏิบัติตามกฎ AGENTS.md อย่างเคร่งครัด แนะนำให้แบ่งจังหวะการ Prompt เป็น 3 จังหวะหลัก (พร้อม 2 จังหวะเสริมสำหรับระบบที่สมบูรณ์แบบ):")

    prompt_steps = [
        ("💡 จังหวะที่ 1: วางรากฐานและสถาปัตยกรรม (Foundation & Database Ingestion)",
         "เป้าหมาย: เชื่อมต่อ SQLite enterprise.db และแสดงผลตาราง PO บนหน้าเว็บ FastAPI แบบ Single-Port Port 8000",
         """สร้างโปรเจกต์ชื่อ "po-auditor" ในโฟลเดอร์ปัจจุบัน โดยทำตามกฎ @AGENTS.md อย่างเคร่งครัด
ฉันต้องการให้ app นี้:
1. จัดการการตั้งค่าระบบผ่าน pydantic-settings จากไฟล์ .env และ print ค่า config แบบ Mask Secrets ก่อนรัน
2. เป็น Single-Port Web Application ด้วย FastAPI ผูกบน host 0.0.0.0 และ port 8000 พอร์ตเดียวเท่านั้น
3. เชื่อมต่อฐานข้อมูล SQLite "enterprise.db" ดึงรายการใบสั่งซื้อจากตาราง purchase_orders และข้อมูลคู่ค้าจาก vendor_master มาแสดงใน Dropdown บนหน้าเว็บสไตล์ Modern Clean ด้วย Tailwind CSS
4. หน้าบ้านเรียก API ด้วย Relative Path เสมอ (ห้ามมี / นำหน้า)
5. สร้าง run.sh สำหรับรันระบบด้วย uv
ช่วยตรวจสอบและเริ่มพัฒนาทีละขั้นตอน หากสงสัยตรงไหนให้ถามฉันก่อน"""),

        ("💡 จังหวะที่ 2: ระบบอัปโหลดเอกสารและสกัดข้อความ (PDF Parser & Side-by-Side UI)",
         "เป้าหมาย: เพิ่มช่องอัปโหลดบิล Invoice และสัญญา PDF พร้อมสกัดข้อความออกมาแสดงเปรียบเทียบ",
         """เพิ่มระบบอัปโหลดไฟล์ PDF 2 ช่องบนหน้าเว็บ:
1. ไฟล์ใบแจ้งหนี้คู่ค้า (Invoice PDF)
2. ไฟล์สัญญาแนบท้าย / ใบตรวจรับงาน (Contract PDF)
โดยใช้ไลบรารี pypdf ทำการสกัดข้อความภาษาไทยและอังกฤษออกมา และแสดงการ์ดเปรียบเทียบ Side-by-Side ระหว่าง:
- ข้อมูลจัดซื้อในระบบ (PO Number, Vendor Name, วงเงิน, เครดิตเทอม, Tax ID, เลขบัญชี)
- ข้อมูลที่สกัดได้จากเอกสาร PDF (ยอดรวม, Tax ID, เลขบัญชี, วันส่งมอบ, เครดิตเทอม)"""),

        ("💡 จังหวะที่ 3: สมองกลตรวจจับความผิดปกติ 8 มิติ (AI Audit & Anomaly Detection)",
         "เป้าหมาย: ตรวจสอบความถูกต้องและสกัดจับจุดดักทั้ง 8 เคสตาม Ground Truth Matrix",
         """สร้าง Audit Engine ตรวจสอบความสอดคล้องระหว่างข้อมูลใน Database กับข้อความใน PDF ครอบคลุม 8 มิติ:
1. ยอดงอกนอกใบ PO (ถ้ามีให้ตัดยอดออก)
2. วันส่งมอบงานเทียบกำหนดสัญญา (หากช้าเกิน 7 วัน ให้คิดค่าปรับ 0.1%/วัน ของวงเงิน PO)
3. ตรวจสอบ Tax ID 13 หลัก และเลขบัญชีธนาคาร เทียบกับ vendor_master (หากไม่ตรง ให้ขึ้นเตือน FRAUD ALERT ระงับจ่ายทันที)
4. การเบิกเงินตามงวดงาน (ห้ามเกินแคปของงวด เช่น งวด 1 ห้ามเกิน 30%)
5. จำนวนของที่ได้รับตรวจรับจริง (หากของขาด ให้จ่ายเฉพาะของจริง)
6. การหักเงินประกันผลงาน Warranty Retention 5% ในงวดสุดท้าย
7. ตรวจสอบวันหมดอายุสัญญา PO (หากส่งงานหลัง PO หมดอายุ ให้ขึ้นเตือน HOLD PAYMENT)
8. ตรวจสอบความถูกต้องทางคณิตศาสตร์ของบิล (ผลรวมรายการย่อยตรงกับ Subtotal หรือไม่)
พร้อมคำนวณยอดเงินสุทธิที่ต้องจ่ายจริง (รวม VAT 7%) และแสดงป้ายสถานะ [APPROVED] / [WARNING] / [HOLD PAYMENT] / [FRAUD ALERT]"""),

        ("💡 ส่วนเสริม 1: สรุปผลทางการและปุ่มคัดลอกอีเมล (Executive Actions & Summary Generator)",
         "เป้าหมาย: สร้างปุ่มกดคัดลอกข้อความสรุปผลการตรวจสอบ สำหรับส่งต่อทาง Email/ERP",
         """เพิ่มกล่องข้อความ Executive Summary และปุ่มกด 'คัดลอกผลสรุปการตรวจเช็ค (Copy Audit Summary)'
เมื่อกดแล้วให้คัดลอกข้อความสรุปทางการสำหรับส่งอีเมลถึงฝ่ายการเงินและผู้บริหาร โดยระบุ:
- เลขที่ PO, ชื่อโครงการ, ชื่อคู่ค้า
- ผลการวินิจฉัยและป้ายสถานะ
- รายละเอียดจุดผิดปกติที่ตรวจพบ
- ยอดเงินเดิม, ยอดหักค่าปรับ/ของขาด/Retention, และยอดสุทธิที่อนุมัติจ่ายจริง"""),

        ("💡 ส่วนเสริม 2: พรีเซ็ตทดสอบ 8 เคสในคลิกเดียว (Bonus: One-Click Test Presets)",
         "เป้าหมาย: เพิ่มปุ่มลัดให้ผู้ตรวจกดคลิกเดียว โหลดข้อมูล Case 1 ถึง Case 8 มาทดสอบได้ทันที",
         """เพิ่มปุ่ม Preset สำหรับทดสอบทั้ง 8 เคสบนหน้าจอ (เช่น ปุ่ม Case 1 ถึง Case 8)
เมื่อผู้ใช้งานคลิกปุ่มใดปุ่มหนึ่ง ให้ระบบเลือกเลขที่ PO และโหลดไฟล์ PDF ที่ตรงกันจากโฟลเดอร์ sample_documents/ มาทำการวิเคราะห์ให้อัตโนมัติทันที โดยไม่ต้องเลือกและอัปโหลดไฟล์ด้วยตนเองทีละไฟล์""")
    ]

    for title, goal, prompt_text in prompt_steps:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_before = Pt(3)
        p_st.paragraph_format.space_after = Pt(1)
        r_st = p_st.add_run(title + "\n")
        set_run_font(r_st, "Thonburi", size_pt=8.5, bold=True, color_rgb=RGBColor(0x1B, 0x4D, 0x3E))
        r_g = p_st.add_run("↳ " + goal)
        set_run_font(r_g, "Thonburi", size_pt=7.5, italic=True, color_rgb=RGBColor(0x64, 0x74, 0x8B))

        t_pbox = doc.add_table(rows=1, cols=1)
        t_pbox.alignment = WD_TABLE_ALIGNMENT.CENTER
        c_pb = t_pbox.rows[0].cells[0]
        set_cell_background(c_pb, "F8FAFC")
        set_cell_margins(c_pb, top=40, bottom=40, left=65, right=65)
        set_cell_borders(c_pb, left={'val': 'single', 'sz': 18, 'color': '1B4D3E'})
        p_pr = c_pb.paragraphs[0]
        r_pr = p_pr.add_run(prompt_text)
        set_run_font(r_pr, "Thonburi", size_pt=7, color_rgb=RGBColor(0x1E, 0x29, 0x3B))

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # END OF PAGE 5 -> PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # PAGE 6: 6. EVALUATION RUBRIC (100 POINTS)
    # =============================================================
    add_heading_styled(doc, "6. เกณฑ์การประเมินและการส่งงาน (Rubric)", level=1)
    doc.add_paragraph("เกณฑ์การประเมินผลการเรียนรู้และการส่งมอบชิ้นงาน Vibe Coding รวม 100 คะแนนเต็ม:")

    t_rubric = doc.add_table(rows=5, cols=3)
    t_rubric.alignment = WD_TABLE_ALIGNMENT.CENTER
    rub_widths = [Inches(1.6), Inches(3.8), Inches(1.2)]
    rub_headers = ["หมวดการประเมิน", "เกณฑ์การพิจารณา", "คะแนนเต็ม"]
    for j, h in enumerate(rub_headers):
        c = t_rubric.rows[0].cells[j]
        set_cell_background(c, "1B4D3E")
        set_cell_margins(c, top=40, bottom=40, left=60, right=60)
        p = c.paragraphs[0]
        r = p.add_run(h)
        set_run_font(r, "Thonburi", size_pt=8, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))

    rub_data = [
        ("1. Core Requirements", "ผ่านครบทั้ง 6 ข้อตาม Checklist (เลือก PO จาก DB ได้, อัปโหลด PDF ได้, วินิจฉัยถูกต้องครบทั้ง 8 เคสตาม Ground Truth Matrix)", "60 คะแนน"),
        ("2. Business Value & UX", "หน้าจอออกแบบสวยงาม อ่านง่าย แยกสีสถานะเขียว/เหลือง/ส้ม/แดงเด่นชัด ฝ่ายบัญชีมองเห็นผลวินิจฉัยและยอดเงินสุทธิได้ใน 5 วินาที", "20 คะแนน"),
        ("3. Architecture & Port Rule", "ระบบทำงานแบบ Single-Port บน Port 8000 ได้อย่างราบรื่น ไม่มีปัญหา Port ซ้ำซ้อน และเรียก API แบบ Relative Path ตามกฎ AGENTS.md", "20 คะแนน"),
        ("🌟 Bonus Challenge", "มีระบบจำลองคลิกเลือกไฟล์ตัวอย่างจาก sample_documents/ แบบ One-Click Preset ทั้ง 8 เคสเพื่อความสะดวกรวดเร็วในการทดสอบ", "+10 คะแนนพิเศษ")
    ]
    for i, row in enumerate(rub_data, start=1):
        bg = "FFFFFF" if i % 2 == 1 else "F8FAFC"
        for j, val in enumerate(row):
            c = t_rubric.rows[i].cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, top=35, bottom=35, left=55, right=55)
            p = c.paragraphs[0]
            r = p.add_run(val)
            set_run_font(r, "Thonburi", size_pt=7.5)
            if j == 2:
                r.font.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    set_table_borders(t_rubric, color="CBD5E1")
    apply_table_header_and_cantsplit(t_rubric, rub_widths)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Closing sign-off box
    t_close = doc.add_table(rows=1, cols=1)
    t_close.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cl = t_close.rows[0].cells[0]
    set_cell_background(c_cl, "F1F5F9")
    set_cell_margins(c_cl, top=60, bottom=60, left=100, right=100)
    p_cl = c_cl.paragraphs[0]
    p_cl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cl = p_cl.add_run("ขอให้ผู้เรียนทุกท่านสนุกกับการ Vibe Coding ระบบ Enterprise AI Auditor!\nหากมีข้อสงสัยเกี่ยวกับ Business Logic สามารถตรวจสอบได้จากตาราง Ground Truth Matrix ในหมวดที่ 4")
    set_run_font(r_cl, "Thonburi", size_pt=8, italic=True, color_rgb=RGBColor(0x47, 0x55, 0x69))

    output_path = "03_smart_po_invoice_auditor.docx"
    doc.save(output_path)
    print(f"Successfully generated perfected docx at: {output_path}")

if __name__ == "__main__":
    build_word_document()

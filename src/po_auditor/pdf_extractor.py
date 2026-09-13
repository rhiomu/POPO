import base64
import io
import os
import re
from typing import Union, Optional, Dict, Any, List
import pypdf
import pymupdf

def extract_text_from_pdf(pdf_source: Union[str, bytes]) -> str:
    """สกัดข้อความทั้งหมดจากไฟล์ PDF (รองรับทั้ง path และ bytes)"""
    try:
        if isinstance(pdf_source, bytes):
            reader = pypdf.PdfReader(io.BytesIO(pdf_source))
        else:
            reader = pypdf.PdfReader(pdf_source)
            
        full_text = []
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            full_text.append(text)
            
        return "\n".join(full_text).strip()
    except Exception as e:
        return f"[PDF Extraction Error: {str(e)}]"

def open_as_pymupdf_doc(source: Union[str, bytes], filename: Optional[str] = None) -> pymupdf.Document:
    """
    แปลงเอกสารทุกรูปแบบ (PDF, Word, Excel, CSV, Image, Text) 
    ให้กลายเป็น pymupdf.Document ในหน่วยความจำเพื่อใช้เรนเดอร์ภาพและไฮไลท์
    """
    from src.po_auditor.document_extractor import (
        detect_doc_type,
        extract_text_from_docx,
        extract_text_from_excel,
        extract_text_from_csv,
        extract_text_from_plain
    )
    
    raw_bytes = source if isinstance(source, bytes) else open(source, "rb").read()
    doc_kind = detect_doc_type(filename=filename, file_bytes=raw_bytes)
    
    if doc_kind == "image":
        ext = os.path.splitext(filename.lower())[1].lstrip(".") if filename else "png"
        if ext not in ["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"]:
            ext = "png"
        img_doc = pymupdf.open(stream=raw_bytes, filetype=ext)
        pdf_bytes = img_doc.convert_to_pdf()
        return pymupdf.open("pdf", pdf_bytes)
        
    elif doc_kind == "word":
        text = extract_text_from_docx(raw_bytes)
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842) # A4 Portrait
        header = f"DOCX DOCUMENT: {filename or 'Contract Document'}\n" + ("=" * 55) + "\n\n"
        page.insert_textbox(pymupdf.Rect(40, 40, 555, 802), header + text, fontsize=11, fontname="helv")
        return doc
        
    elif doc_kind in ["excel", "csv"]:
        text = extract_text_from_excel(raw_bytes) if doc_kind == "excel" else extract_text_from_csv(raw_bytes)
        doc = pymupdf.open()
        page = doc.new_page(width=842, height=595) # A4 Landscape for tables
        header = f"SPREADSHEET: {filename or 'Excel Sheet'}\n" + ("=" * 70) + "\n\n"
        page.insert_textbox(pymupdf.Rect(35, 35, 807, 560), header + text, fontsize=9.5, fontname="helv")
        return doc
        
    elif doc_kind == "text":
        text = extract_text_from_plain(raw_bytes)
        doc = pymupdf.open()
        page = doc.new_page(width=595, height=842)
        page.insert_textbox(pymupdf.Rect(40, 40, 555, 802), text, fontsize=10.5, fontname="helv")
        return doc
        
    else:  # Default PDF
        return pymupdf.open(stream=raw_bytes, filetype="pdf")

def _generate_search_candidates(
    query: str,
    doc_type: str = "invoice",
    alternate_query: Optional[str] = None
) -> List[str]:
    """สร้างคำค้นหาที่อาจปรากฏในเอกสาร PDF/เอกสาร จากค่าที่แสดงในตาราง"""
    if not query and not alternate_query:
        return []
        
    def _extract_single(q_str: str) -> List[str]:
        if not q_str:
            return []
        q = q_str.strip()
        local_cands = [q]
        
        # ทำความสะอาดช่องว่างซ้ำซ้อน
        q_norm = " ".join(q.split())
        if q_norm != q:
            local_cands.append(q_norm)
        
        # 1. เลข Tax ID 13 หลักตรงๆ
        if re.fullmatch(r"\d{13}", q):
            return [q]
            
        # 2. เลขที่บัญชีธนาคารที่มีขีด
        if "-" in q:
            acc_matches = re.findall(r"\d{3}-\d{1}-\d{5}-\d{1}", q)
            if acc_matches:
                local_cands.extend(acc_matches)
            acc_short = re.findall(r"\d{3}-\d{1}-\d{4,5}", q)
            if acc_short:
                local_cands.extend(acc_short)
                
        # 3. Tax ID ในข้อความ
        tax_matches = re.findall(r"\b\d{13}\b", q)
        if tax_matches:
            local_cands.extend(tax_matches)
            
        # 4. ตัวเลขจำนวนเงิน เช่น 3,000,000.00 บาท -> 3,000,000.00, 3,000,000
        money_matches = re.findall(r"\b\d{1,3}(?:,\d{3})+(?:\.\d{2})?\b", q)
        for m in money_matches:
            local_cands.append(m)
            if "." in m:
                local_cands.append(m.split(".")[0])
            clean_m = m.replace(",", "")
            local_cands.append(clean_m)
            if "." in clean_m:
                local_cands.append(clean_m.split(".")[0])

        # ถ้าส่งมาเป็นตัวเลขไม่มีจุลภาค เช่น 990000 ให้เพิ่ม 990,000 และ 990,000.00
        num_plain = re.sub(r"[^\d.]", "", q)
        if num_plain and (num_plain.isdigit() or (num_plain.count(".") == 1 and num_plain.replace(".", "").isdigit())):
            try:
                val = float(num_plain)
                local_cands.append(f"{val:,.2f}")
                local_cands.append(f"{int(val):,}")
            except Exception:
                pass
                
        # 5. เครดิตเทอม เช่น 30 วัน -> 30 Days, Payment Term
        day_matches = re.findall(r"(\d+)\s*(?:วัน|Days?)", q, re.IGNORECASE)
        for d in day_matches:
            local_cands.append(f"{d} Days")
            local_cands.append(f"{d} Day")
            local_cands.append(f"{d} days")
            local_cands.append(f"{d} day")
            local_cands.append(d)
            local_cands.append("Payment Term")
            
        # 6. คำค้นหาชื่อบริษัท (รองรับทั้งภาษาไทยและภาษาอังกฤษ + รูปแบบเครื่องหมายวรรคตอน)
        is_company = any(k in q.lower() for k in [
            "co.", "ltd", "inc", "corp", "company", "limited", "part", "supplier", "vendor",
            "บริษัท", "จำกัด", "หจก", "ห้างหุ้นส่วน"
        ]) or len(q.split()) >= 2

        if is_company:
            # ความแปรผันของเครื่องหมายวรรคตอน
            if q.endswith("."):
                local_cands.append(q.rstrip("."))
            local_cands.append(re.sub(r",\s+", ",", q))
            local_cands.append(re.sub(r",\s+", ",", q).rstrip("."))
            local_cands.append(re.sub(r"[.,]", "", q))
            
            # ถอดคำลงท้ายนิติบุคคลภาษาอังกฤษออกเพื่อเอาแกนชื่อบริษัท (e.g. KangHan Engineering & Service)
            stem_en = re.sub(r"(?i)\b(co\.?|ltd\.?|inc\.?|corp\.?|company|limited|partnership|part\.?)\b", "", q)
            stem_en = re.sub(r"[.,]", "", stem_en).strip()
            stem_en = re.sub(r"\s+", " ", stem_en).strip()
            if stem_en and stem_en != q:
                local_cands.append(stem_en)
                words = stem_en.split()
                if len(words) >= 3:
                    local_cands.append(" ".join(words[:3]))
                if len(words) >= 2:
                    local_cands.append(" ".join(words[:2]))
                if len(words) >= 1 and len(words[0]) >= 3:
                    local_cands.append(words[0])
                    
            # ถอดคำหน้า/หลังนิติบุคคลภาษาไทยออก (e.g. กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส)
            stem_th = re.sub(r"(?i)\b(บริษัท|จำกัด|มหาชน|ห้างหุ้นส่วนจำกัด|หจก\.?)\b", "", q).strip()
            stem_th = re.sub(r"\s+", " ", stem_th).strip()
            if stem_th and stem_th != q:
                local_cands.append(stem_th)
                th_words = stem_th.split()
                if len(th_words) >= 3:
                    local_cands.append(" ".join(th_words[:3]))
                if len(th_words) >= 2:
                    local_cands.append(" ".join(th_words[:2]))
                if len(th_words) >= 1:
                    local_cands.append(th_words[0])
                    
            # คำสำคัญภาษาอังกฤษที่มีความยาว >= 4 อักษร
            eng_tokens = re.findall(r"[A-Za-z0-9]{3,}", q)
            for w in eng_tokens:
                if len(w) >= 4 and w.lower() not in ["company", "limited", "service", "supply"]:
                    local_cands.append(w)
                    
        # 7. เงื่อนไขในสัญญา/ใบส่งของ
        if doc_type == "contract":
            local_cands.extend([
                "Scheduled Deadline", "Actual Completion", "late",
                "Inspection Result", "Delivered on time", "QC check",
                "Milestone", "Retention", "Warranty", "Clause",
                "Short delivery", "Received into inventory",
                "EXPIRED", "expiry", "Receiving Report"
            ])
            
        return local_cands

    candidates = _extract_single(query) if query else []
    if alternate_query:
        candidates.extend(_extract_single(alternate_query))
        
    # ป้ายบอกประเภทคู่ค้า (ใช้เป็น Fallback ลำดับสุดท้ายจริงๆ หากไม่พบชื่อบริษัท)
    has_company = any(
        any(k in x.lower() for k in ["co.", "ltd", "inc", "corp", "company", "limited", "part", "บริษัท", "จำกัด", "หจก"])
        for x in [query or "", alternate_query or ""]
    )
    if has_company:
        candidates.extend(["Supplier:", "Supplier", "Vendor:", "Vendor"])
        
    # คัดกรองตัวซ้ำโดยยังคงลำดับความสำคัญจากเจาะจงมากไปหาน้อย
    seen = set()
    result = []
    for c in candidates:
        c_clean = c.strip()
        if c_clean and len(c_clean) >= 2 and c_clean not in seen:
            seen.add(c_clean)
            result.append(c_clean)
            
    return result

def render_pdf_page_with_highlight(
    pdf_source: Union[str, bytes],
    query: Optional[str] = None,
    page_idx: int = 0,
    doc_type: str = "invoice",
    dpi: int = 140,
    filename: Optional[str] = None,
    alternate_query: Optional[str] = None
) -> Dict[str, Any]:
    """
    เรนเดอร์หน้าเอกสาร (PDF, Word, Excel, CSV, Image) เป็นรูปภาพ PNG พร้อมตีกรอบไฮไลท์ตำแหน่งข้อความที่สกัดมา
    """
    try:
        doc = open_as_pymupdf_doc(pdf_source, filename=filename)
            
        total_pages = len(doc)
        if total_pages == 0:
            return {"success": False, "error": "เอกสารไม่มีหน้าเนื้อหา"}
            
        matched_str = ""
        matching_rects = []
        target_page_idx = min(max(0, page_idx), total_pages - 1)
        
        # แคช Page และ TextPage สำหรับหน้าที่ไม่มี Text Layer (เช่น ไฟล์รูปภาพ หรือเอกสารสแกน)
        pages_cache: Dict[int, Any] = {}
        ocr_textpages: Dict[int, Any] = {}
        def get_page_and_textpage(p_num: int):
            if p_num not in pages_cache:
                pages_cache[p_num] = doc[p_num]
            p = pages_cache[p_num]
            if p_num not in ocr_textpages:
                # หากหน้านี้ไม่มีเวกเตอร์ข้อความเลย ให้สร้าง OCR TextPage
                if not (p.get_text() or "").strip():
                    try:
                        ocr_textpages[p_num] = p.get_textpage_ocr(language="eng", dpi=150)
                    except Exception:
                        ocr_textpages[p_num] = None
                else:
                    ocr_textpages[p_num] = None
            return p, ocr_textpages[p_num]

        # ค้นหาคำที่ต้องการไฮไลท์
        if (query and query.strip()) or (alternate_query and alternate_query.strip()):
            candidates = _generate_search_candidates(query or "", doc_type=doc_type, alternate_query=alternate_query)
            found_candidate = False
            
            # ค้นหาในหน้าที่ระบุก่อน
            p_target, tp_target = get_page_and_textpage(target_page_idx)
            for cand in candidates:
                r = p_target.search_for(cand, textpage=tp_target) if tp_target else p_target.search_for(cand)
                if r:
                    matching_rects = list(r)
                    matched_str = cand
                    found_candidate = True
                    
                    # ถ้าเจอคำหลักที่เป็นชื่อสั้นๆ เช่น "KangHan" ให้ลองไฮไลท์คำต่อท้ายเช่น "Engineering" บนหน้านี้ด้วย
                    check_q = query or alternate_query or ""
                    if len(cand.split()) == 1 and len(check_q.split()) > 1:
                        next_words = [w for w in re.findall(r"[A-Za-z0-9]{4,}", check_q) if w.lower() != cand.lower()]
                        for nw in next_words[:2]:
                            extra_r = p_target.search_for(nw, textpage=tp_target) if tp_target else p_target.search_for(nw)
                            if extra_r:
                                matching_rects.extend(extra_r)
                    break
                    
            # ถ้าไม่พบบนหน้าแรก ค้นหาในหน้าอื่นทั้งหมด
            if not found_candidate:
                for p_i in range(total_pages):
                    if p_i == target_page_idx:
                        continue
                    p_obj, tp_i = get_page_and_textpage(p_i)
                    for cand in candidates:
                        r = p_obj.search_for(cand, textpage=tp_i) if tp_i else p_obj.search_for(cand)
                        if r:
                            matching_rects = list(r)
                            matched_str = cand
                            target_page_idx = p_i
                            found_candidate = True
                            break
                    if found_candidate:
                        break
                        
        page = doc[target_page_idx]
        
        # วาดกล่องไฮไลท์สีเหลืองขอบแดงโปร่งแสง
        if matching_rects:
            pad = 2
            for r in matching_rects:
                outer = pymupdf.Rect(r.x0 - pad, r.y0 - pad, r.x1 + pad, r.y1 + pad)
                shape = page.new_shape()
                shape.draw_rect(outer)
                shape.finish(
                    color=(0.85, 0.15, 0.15),   # ขอบแดงสะดุดตา
                    fill=(1.0, 0.94, 0.20),     # ไฮไลท์สีเหลืองใส (Translucent Yellow)
                    fill_opacity=0.45,
                    width=2.0
                )
                shape.commit()
                
        pix = page.get_pixmap(dpi=dpi)
        png_bytes = pix.tobytes("png")
        b64_str = base64.b64encode(png_bytes).decode("utf-8")
        
        return {
            "success": True,
            "page_idx": target_page_idx,
            "total_pages": total_pages,
            "found": bool(matching_rects),
            "is_scanned_image": not bool(page.get_text().strip()),
            "matched_query": matched_str or query,
            "match_count": len(matching_rects),
            "image_base64": f"data:image/png;base64,{b64_str}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"เกิดข้อผิดพลาดในการประมวลผล PDF: {str(e)}"
        }

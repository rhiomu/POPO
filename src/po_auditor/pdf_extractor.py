import base64
import io
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

def _generate_search_candidates(query: str, doc_type: str = "invoice") -> List[str]:
    """สร้างคำค้นหาที่อาจปรากฏในเอกสาร PDF จากค่าที่แสดงในตาราง"""
    if not query:
        return []
        
    q = query.strip()
    candidates = [q]
    
    # 1. เลข Tax ID 13 หลักตรงๆ
    if re.fullmatch(r"\d{13}", q):
        return [q]
        
    # 2. เลขที่บัญชีธนาคารที่มีขีด
    if "-" in q:
        acc_matches = re.findall(r"\d{3}-\d{1}-\d{5}-\d{1}", q)
        if acc_matches:
            candidates.extend(acc_matches)
        acc_short = re.findall(r"\d{3}-\d{1}-\d{4,5}", q)
        if acc_short:
            candidates.extend(acc_short)
            
    # 3. Tax ID ในข้อความ
    tax_matches = re.findall(r"\b\d{13}\b", q)
    if tax_matches:
        candidates.extend(tax_matches)
        
    # 4. ตัวเลขจำนวนเงิน เช่น 3,000,000.00 บาท -> 3,000,000.00, 3,000,000
    money_matches = re.findall(r"\b\d{1,3}(?:,\d{3})+(?:\.\d{2})?\b", q)
    for m in money_matches:
        candidates.append(m)
        if "." in m:
            candidates.append(m.split(".")[0])
        clean_m = m.replace(",", "")
        candidates.append(clean_m)
        if "." in clean_m:
            candidates.append(clean_m.split(".")[0])
            
    # 5. เครดิตเทอม เช่น 30 วัน -> 30 Days, Payment Term
    day_matches = re.findall(r"(\d+)\s*(?:วัน|Days?)", q, re.IGNORECASE)
    for d in day_matches:
        candidates.append(f"{d} Days")
        candidates.append(f"{d} day")
        candidates.append(d)
        candidates.append("Payment Term")
        
    # 6. คำค้นหาชื่อบริษัท
    if "บริษัท" in q or "จำกัด" in q:
        candidates.append("Supplier:")
        candidates.append("Supplier")
        eng = re.findall(r"[A-Za-z]{3,}", q)
        if eng:
            candidates.append(" ".join(eng[:3]))
            for w in eng:
                candidates.append(w)
                
    # 7. เงื่อนไขในสัญญา/ใบส่งของ
    if doc_type == "contract":
        candidates.extend([
            "Scheduled Deadline", "Actual Completion", "late",
            "Inspection Result", "Delivered on time", "QC check",
            "Milestone", "Retention", "Warranty", "Clause",
            "Short delivery", "Received into inventory",
            "EXPIRED", "expiry", "Receiving Report"
        ])
        
    # คัดกรองตัวซ้ำ
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
    dpi: int = 140
) -> Dict[str, Any]:
    """
    เรนเดอร์หน้าเอกสาร PDF เป็นรูปภาพ PNG พร้อมตีกรอบไฮไลท์ตำแหน่งข้อความที่สกัดมา
    """
    try:
        if isinstance(pdf_source, bytes):
            doc = pymupdf.open(stream=pdf_source, filetype="pdf")
        else:
            doc = pymupdf.open(pdf_source)
            
        total_pages = len(doc)
        if total_pages == 0:
            return {"success": False, "error": "เอกสารไม่มีหน้าเนื้อหา"}
            
        matched_str = ""
        matching_rects = []
        target_page_idx = min(max(0, page_idx), total_pages - 1)
        
        # ค้นหาคำที่ต้องการไฮไลท์
        if query and query.strip():
            candidates = _generate_search_candidates(query, doc_type=doc_type)
            found_candidate = False
            
            # ค้นหาในหน้าที่ระบุก่อน
            for cand in candidates:
                r = doc[target_page_idx].search_for(cand)
                if r:
                    matching_rects = r
                    matched_str = cand
                    found_candidate = True
                    break
                    
            # ถ้าไม่พบบนหน้าแรก ค้นหาในหน้าอื่นทั้งหมด
            if not found_candidate:
                for p_i in range(total_pages):
                    if p_i == target_page_idx:
                        continue
                    for cand in candidates:
                        r = doc[p_i].search_for(cand)
                        if r:
                            matching_rects = r
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
            "matched_query": matched_str or query,
            "match_count": len(matching_rects),
            "image_base64": f"data:image/png;base64,{b64_str}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"เกิดข้อผิดพลาดในการประมวลผล PDF: {str(e)}"
        }

import io
import os
import re
import csv
import base64
import logging
from typing import Union, Optional, Dict, Any, List

logger = logging.getLogger(__name__)

def detect_doc_type(filename: Optional[str] = None, file_bytes: Optional[bytes] = None) -> str:
    """
    ตรวจสอบประเภทเอกสารจากนามสกุลไฟล์หรือ Magic Bytes
    คืนค่า: 'pdf' | 'word' | 'excel' | 'csv' | 'image' | 'text' | 'unknown'
    """
    ext = ""
    if filename:
        ext = os.path.splitext(filename.lower())[1]

    if ext in [".pdf"]:
        return "pdf"
    if ext in [".docx", ".doc"]:
        return "word"
    if ext in [".xlsx", ".xls"]:
        return "excel"
    if ext in [".csv"]:
        return "csv"
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"]:
        return "image"
    if ext in [".txt", ".md", ".json"]:
        return "text"

    # ตรวจสอบจาก Magic Bytes หากไม่มีนามสกุล
    if file_bytes:
        if file_bytes.startswith(b"%PDF"):
            return "pdf"
        if file_bytes.startswith(b"PK\x03\x04"):
            # ZIP container: อาจเป็น docx หรือ xlsx
            if filename and ("sheet" in filename.lower() or "excel" in filename.lower()):
                return "excel"
            return "word"
        if file_bytes.startswith(b"\x89PNG\r\n\x1a\n") or file_bytes.startswith(b"\xff\xd8\xff"):
            return "image"

    return "pdf"  # ค่าเริ่มต้นหากไม่ทราบ

def extract_text_from_pdf(pdf_source: Union[str, bytes]) -> str:
    """สกัดข้อความทั้งหมดจากไฟล์ PDF ด้วย PyMuPDF (เร็วและแม่นยำกว่า pypdf)"""
    try:
        import pymupdf
        if isinstance(pdf_source, bytes):
            doc = pymupdf.open(stream=pdf_source, filetype="pdf")
        else:
            doc = pymupdf.open(pdf_source)

        pages_text = []
        for page in doc:
            t = page.get_text() or ""
            if t.strip():
                pages_text.append(t.strip())

        if pages_text:
            return "\n\n--- Page Break ---\n\n".join(pages_text)

        # Fallback กรณี PDF หน้าเปล่าหรือเป็นภาพสแกน
        import pypdf
        if isinstance(pdf_source, bytes):
            reader = pypdf.PdfReader(io.BytesIO(pdf_source))
        else:
            reader = pypdf.PdfReader(pdf_source)
        alt_text = [p.extract_text() or "" for p in reader.pages]
        return "\n".join(alt_text).strip()
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return f"[PDF Extraction Error: {str(e)}]"

def extract_text_from_docx(docx_source: Union[str, bytes]) -> str:
    """สกัดข้อความ ย่อหน้า และโครงสร้างตารางจาก Microsoft Word (.docx)"""
    try:
        import docx
        if isinstance(docx_source, bytes):
            doc = docx.Document(io.BytesIO(docx_source))
        else:
            doc = docx.Document(docx_source)

        lines: List[str] = []

        # 1. สกัดย่อหน้าและหัวข้อ
        for para in doc.paragraphs:
            txt = para.text.strip()
            if txt:
                lines.append(txt)

        # 2. สกัดตาราง (สัญญาและใบวางบิลมักใส่ในตาราง)
        for t_idx, table in enumerate(doc.tables):
            lines.append(f"\n[Table {t_idx + 1}]")
            for row in table.rows:
                row_cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                # ลบเซลล์ซ้ำที่เกิดจากการ merge
                dedup_cells = []
                for c in row_cells:
                    if not dedup_cells or c != dedup_cells[-1]:
                        dedup_cells.append(c)
                if any(dedup_cells):
                    lines.append(" | ".join(dedup_cells))

        return "\n".join(lines).strip()
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
        return f"[DOCX Extraction Error: {str(e)}]"

def extract_text_from_excel(excel_source: Union[str, bytes]) -> str:
    """สกัดข้อมูลทุกเซลล์และทุกชีตจาก Microsoft Excel (.xlsx)"""
    try:
        import openpyxl
        if isinstance(excel_source, bytes):
            wb = openpyxl.load_workbook(io.BytesIO(excel_source), data_only=True)
        else:
            wb = openpyxl.load_workbook(excel_source, data_only=True)

        lines: List[str] = []
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            lines.append(f"=== Sheet: {sheet_name} ===")
            for row in sheet.iter_rows(values_only=True):
                # ตรวจว่าแถวนี้มีข้อมูลหรือไม่
                if row and any(cell is not None and str(cell).strip() != "" for cell in row):
                    formatted_cells = [str(c).strip() if c is not None else "" for c in row]
                    lines.append(" | ".join(formatted_cells))
            lines.append("")

        return "\n".join(lines).strip()
    except Exception as e:
        logger.error(f"Error extracting Excel: {e}")
        return f"[Excel Extraction Error: {str(e)}]"

def extract_text_from_csv(csv_source: Union[str, bytes]) -> str:
    """สกัดข้อมูลจากไฟล์ CSV รองรับทั้ง UTF-8, UTF-8-BOM และ Windows CP874 (ภาษาไทย)"""
    try:
        raw_text = ""
        if isinstance(csv_source, bytes):
            for encoding in ["utf-8-sig", "utf-8", "cp874", "tis-620", "latin-1"]:
                try:
                    raw_text = csv_source.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
        else:
            with open(csv_source, "r", encoding="utf-8-sig", errors="replace") as f:
                raw_text = f.read()

        lines: List[str] = []
        reader = csv.reader(io.StringIO(raw_text))
        for row in reader:
            if row and any(c.strip() for c in row):
                lines.append(" | ".join(c.strip() for c in row))

        return "\n".join(lines).strip()
    except Exception as e:
        logger.error(f"Error extracting CSV: {e}")
        return f"[CSV Extraction Error: {str(e)}]"

def extract_text_from_image(image_source: Union[str, bytes], settings=None) -> str:
    """
    สกัดข้อความจากรูปภาพบิล/ใบเสร็จ (PNG, JPG, WEBP)
    ลำดับขั้น:
    1. หากมี OpenAI-Compatible LLM และโมเดล Vision -> ส่งเข้า Vision OCR
    2. ใช้ PyMuPDF / Tesseract OCR
    3. ส่งคืนคำอธิบายภาพสำหรับ Audit Engine
    """
    raw_bytes = image_source if isinstance(image_source, bytes) else open(image_source, "rb").read()
    b64_img = base64.b64encode(raw_bytes).decode("utf-8")

    # ขั้นที่ 1: ลองใช้ LLM Vision หากมีการตั้งค่า API
    if settings:
        try:
            eff_key = settings.get_effective_api_key()
            if eff_key and eff_key.get_secret_value() and settings.llm_base_url:
                from openai import OpenAI
                client = OpenAI(
                    base_url=settings.llm_base_url,
                    api_key=eff_key.get_secret_value(),
                    timeout=25.0
                )
                
                # ตรวจสอบโมเดลที่เหมาะกับ Vision OCR
                vision_model = getattr(settings, "llm_vision_model", None) or "Qwen/Qwen2.5-VL-72B-Instruct"
                if "typhoon" in str(settings.llm_model).lower() or "vl" in str(settings.llm_model).lower():
                    vision_model = settings.llm_model

                prompt = (
                    "คุณคือระบบ OCR อ่านเอกสารจัดซื้อและใบแจ้งหนี้ กรุณาสกัดข้อความทั้งหมดในภาพอย่างละเอียด "
                    "ระบุชื่อคู่ค้า, เลขประจำตัวผู้เสียภาษี (Tax ID), เลขที่บัญชีธนาคาร, วันที่, ยอดเงินรวม (Subtotal/Total), "
                    "และรายการสินค้า/งวดงานทุกรายการอย่างครบถ้วน ไม่ต้องเกริ่นนำ"
                )

                resp = client.chat.completions.create(
                    model=vision_model,
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                        ]
                    }],
                    max_tokens=1500,
                    temperature=0.0
                )
                content = resp.choices[0].message.content or ""
                if content.strip():
                    logger.info(f"Successfully extracted text from image via Vision Model: {vision_model}")
                    return content.strip()
        except Exception as e:
            logger.warning(f"Vision OCR failed, falling back to PyMuPDF OCR: {e}")

    # ขั้นที่ 2: PyMuPDF OCR
    try:
        import pymupdf
        img_doc = pymupdf.open(stream=raw_bytes, filetype="png")
        pdf_bytes = img_doc.convert_to_pdf()
        pdf_doc = pymupdf.open("pdf", pdf_bytes)
        page = pdf_doc[0]
        
        # ลองภาษาไทยและอังกฤษ
        for lang in ["tha+eng", "eng"]:
            try:
                tp = page.get_textpage_ocr(language=lang, dpi=150)
                text = page.get_text(textpage=tp)
                if text and text.strip():
                    return text.strip()
            except Exception:
                continue
    except Exception as e:
        logger.warning(f"PyMuPDF OCR failed: {e}")

    # ขั้นที่ 3: กรณีไม่มี OCR พร้อมใช้งาน
    return "[Image Document Uploaded: รูปภาพใบเสร็จ/บิลคู่ค้าถูกแนบเรียบร้อย สามารถเปิดตรวจสอบภาพต้นฉบับได้ที่หน้าต่าง Document Visual Grounding]"

def extract_text_from_plain(text_source: Union[str, bytes]) -> str:
    """สกัดข้อความจากไฟล์ Plain Text (.txt, .md, .json)"""
    if isinstance(text_source, str):
        return text_source
    for encoding in ["utf-8-sig", "utf-8", "cp874", "tis-620", "latin-1"]:
        try:
            return text_source.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return text_source.decode("utf-8", errors="replace").strip()

def extract_document_text(
    doc_source: Union[str, bytes],
    filename: Optional[str] = None,
    settings: Optional[Any] = None
) -> str:
    """
    ฟังก์ชันกลาง Unified Document Extractor:
    ตรวจจับประเภทไฟล์อัตโนมัติ และสกัดข้อความออกมาพร้อมสำหรับการ Audit
    """
    doc_type = detect_doc_type(filename=filename, file_bytes=doc_source if isinstance(doc_source, bytes) else None)
    
    if doc_type == "pdf":
        return extract_text_from_pdf(doc_source)
    elif doc_type == "word":
        return extract_text_from_docx(doc_source)
    elif doc_type == "excel":
        return extract_text_from_excel(doc_source)
    elif doc_type == "csv":
        return extract_text_from_csv(doc_source)
    elif doc_type == "image":
        return extract_text_from_image(doc_source, settings=settings)
    elif doc_type == "text":
        return extract_text_from_plain(doc_source)
    else:
        # ลองอ่านเป็น PDF ก่อน ถ้าล้มเหลวให้อ่านเป็น Text
        try:
            return extract_text_from_pdf(doc_source)
        except Exception:
            return extract_text_from_plain(doc_source)

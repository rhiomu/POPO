import os
import uuid
import time
import asyncio
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.po_auditor.config import load_and_print_config
from src.po_auditor.db import (
    get_all_pos,
    get_po_detail,
    compute_cache_key,
    get_cached_audit,
    save_cached_audit,
    get_audit_history,
    get_audit_by_cache_key,
    delete_audit_history
)
from src.po_auditor.pdf_extractor import extract_text_from_pdf, render_pdf_page_with_highlight
from src.po_auditor.auditor import audit_po_and_documents, audit_with_llm

settings = load_and_print_config()

app = FastAPI(
    title="Smart PO & Invoice Auditor",
    description="ระบบตรวจเช็ค PO และบิลคู่ค้าอัตโนมัติด้วย AI",
    version="1.0.0"
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Session memory storage for uploaded documents
SESSION_UPLOADS: Dict[str, Dict[str, Any]] = {}
LATEST_SESSION: Dict[str, Any] = {"preset_key": "case6", "session_id": None}

# Preset map for all 8 test cases
PRESET_MAP = {
    "case1": {
        "po_number": "PO-2026-089",
        "label": "Case 1: ยอดงอก + ค่าปรับส่งช้า 10 วัน",
        "invoice_pdf": "sample_documents/Case1_Invoice_PO089.pdf",
        "contract_pdf": "sample_documents/Case1_Contract_PO089.pdf"
    },
    "case2": {
        "po_number": "PO-2026-090",
        "label": "Case 2: เอกสารตรงตามสัญญาครบถ้วน (Clean Approved)",
        "invoice_pdf": "sample_documents/Case2_Invoice_PO090.pdf",
        "contract_pdf": "sample_documents/Case2_Contract_PO090.pdf"
    },
    "case3": {
        "po_number": "PO-2026-091",
        "label": "Case 3: เลขประจำตัวผู้เสียภาษี & บัญชีปลอม (Fraud Alert)",
        "invoice_pdf": "sample_documents/Case3_Invoice_PO091.pdf",
        "contract_pdf": "sample_documents/Case3_Contract_PO091.pdf"
    },
    "case4": {
        "po_number": "PO-2026-092",
        "label": "Case 4: ขอเบิกเกินงวดงาน 50% vs Cap 30%",
        "invoice_pdf": "sample_documents/Case4_Invoice_PO092.pdf",
        "contract_pdf": "sample_documents/Case4_Contract_PO092.pdf"
    },
    "case5": {
        "po_number": "PO-2026-093",
        "label": "Case 5: ส่งของไม่ครบ 7/10 ชุด แต่บิลเก็บเต็ม 100%",
        "invoice_pdf": "sample_documents/Case5_Invoice_PO093.pdf",
        "contract_pdf": "sample_documents/Case5_Contract_PO093.pdf"
    },
    "case6": {
        "po_number": "PO-2026-094",
        "label": "Case 6: ลืมหักเงินประกันผลงาน (Warranty Retention 5%)",
        "invoice_pdf": "sample_documents/Case6_Invoice_PO094.pdf",
        "contract_pdf": "sample_documents/Case6_Contract_PO094.pdf"
    },
    "case7": {
        "po_number": "PO-2026-095",
        "label": "Case 7: งานส่งมอบหลัง PO หมดอายุ (Hold รอ Amendment)",
        "invoice_pdf": "sample_documents/Case7_Invoice_PO095.pdf",
        "contract_pdf": "sample_documents/Case7_Contract_PO095.pdf"
    },
    "case8": {
        "po_number": "PO-2026-096",
        "label": "Case 8: บิลคิดเลขผิด Subtotal ไม่ตรงกับ Line Items",
        "invoice_pdf": "sample_documents/Case8_Invoice_PO096.pdf",
        "contract_pdf": "sample_documents/Case8_Contract_PO096.pdf"
    }
}

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/pos")
async def api_get_pos():
    pos = get_all_pos(settings.db_path)
    return JSONResponse(content={"pos": pos})

@app.get("/api/pos/{po_number}")
async def api_get_po_detail(po_number: str):
    po = get_po_detail(po_number, settings.db_path)
    if not po:
        raise HTTPException(status_code=404, detail=f"ไม่พบเลขที่ PO {po_number}")
    return JSONResponse(content={"po": po})

@app.get("/api/presets")
async def api_get_presets():
    summary = []
    for k, v in PRESET_MAP.items():
        summary.append({
            "key": k,
            "po_number": v["po_number"],
            "label": v["label"]
        })
    return JSONResponse(content={"presets": summary})

@app.post("/api/audit")
async def api_run_audit(
    po_number: str = Form(...),
    preset_key: Optional[str] = Form(None),
    force_reaudit: bool = Form(False),
    invoice_file: Optional[UploadFile] = File(None),
    contract_file: Optional[UploadFile] = File(None)
):
    po_data = get_po_detail(po_number, settings.db_path)
    if not po_data:
        raise HTTPException(status_code=404, detail=f"ไม่พบเลขที่ PO {po_number} ในฐานข้อมูล")

    invoice_text = ""
    contract_text = ""
    session_id = None
    raw_inv_bytes = None
    raw_con_bytes = None

    if preset_key and preset_key in PRESET_MAP:
        preset = PRESET_MAP[preset_key]
        if os.path.exists(preset["invoice_pdf"]):
            with open(preset["invoice_pdf"], "rb") as f:
                raw_inv_bytes = f.read()
            invoice_text = extract_text_from_pdf(raw_inv_bytes)
        if os.path.exists(preset["contract_pdf"]):
            with open(preset["contract_pdf"], "rb") as f:
                raw_con_bytes = f.read()
            contract_text = extract_text_from_pdf(raw_con_bytes)
        LATEST_SESSION["preset_key"] = preset_key
        LATEST_SESSION["session_id"] = None
    else:
        inv_bytes = None
        con_bytes = None
        inv_name = "invoice.pdf"
        con_name = "contract.pdf"
        if invoice_file and invoice_file.filename:
            inv_bytes = await invoice_file.read()
            inv_name = invoice_file.filename
            invoice_text = extract_text_from_pdf(inv_bytes)
            raw_inv_bytes = inv_bytes
        if contract_file and contract_file.filename:
            con_bytes = await contract_file.read()
            con_name = contract_file.filename
            contract_text = extract_text_from_pdf(con_bytes)
            raw_con_bytes = con_bytes

        session_id = uuid.uuid4().hex[:8]
        SESSION_UPLOADS[session_id] = {
            "invoice_bytes": inv_bytes,
            "invoice_name": inv_name,
            "contract_bytes": con_bytes,
            "contract_name": con_name
        }
        LATEST_SESSION["preset_key"] = None
        LATEST_SESSION["session_id"] = session_id

    if not invoice_text:
        raise HTTPException(status_code=400, detail="ไม่พบข้อมูลในไฟล์ใบแจ้งหนี้ (Invoice PDF)")

    eff_key = settings.get_effective_api_key()
    audit_engine = "Built-in Local Audit Engine"
    audit_result = None

    t_start = time.time()
    po_no = po_data.get("po_number", "")
    active_model = settings.llm_model if (eff_key and eff_key.get_secret_value()) else "builtin-local-engine"

    # คำนวณ SHA-256 Fingerprint ของ PO + เอกสารจริง + โมเดล
    cache_meta = compute_cache_key(po_data, raw_inv_bytes or b"", raw_con_bytes, active_model)
    cache_key = cache_meta["cache_key"]

    print(f"\n🚀 [API /api/audit] เริ่มการตรวจสอบ PO: {po_no} (Preset: {preset_key or 'None (Manual Upload)'})")
    print(f"🔑 [Content Fingerprint] Cache Key: {cache_key[:12]}... (Force: {force_reaudit})")

    # ตรวจสอบ Cache (หากไม่ได้บังคับให้ตรวจใหม่)
    if not force_reaudit:
        cached = get_cached_audit(cache_key, settings.db_path)
        if cached:
            cached_engine = f"{cached['audit_engine']} [⚡ Cached Result]"
            print(f"⚡ [Cache Hit] พบผลตรวจใน Cache สำหรับ PO: {po_no} -> ตอบกลับทันทีใน {time.time()-t_start:.3f} วินาที!")
            return JSONResponse(content={
                "success": True,
                "po_data": po_data,
                "audit": cached["audit"],
                "audit_engine": cached_engine,
                "preset_key": preset_key,
                "session_id": session_id,
                "cached": True,
                "cached_at": cached["created_at"]
            })

    if eff_key and eff_key.get_secret_value():
        try:
            print(f"🤖 [API /api/audit] กำลังส่งคำขอให้ LLM ({settings.llm_model} @ {settings.llm_base_url or 'OpenAI'})...")
            audit_result = await asyncio.wait_for(
                audit_with_llm(po_data, invoice_text, contract_text, settings),
                timeout=85.0
            )
            audit_engine = f"OpenAI-Compatible LLM ({settings.llm_model})"
            print(f"✅ [API /api/audit] AI Audit สำเร็จในเวลา {time.time()-t_start:.2f} วินาที (Status: {audit_result.get('status')})")
        except Exception as exc:
            print(f"⚠️ [API /api/audit] การเรียก LLM ล้มเหลวหรือหมดเวลา ({exc}) ในเวลา {time.time()-t_start:.2f} วินาที -> สลับไปใช้ Built-in Local Engine อัตโนมัติ")
            audit_result = audit_po_and_documents(po_data, invoice_text, contract_text)
            audit_engine = f"Built-in Local Engine (LLM Fallback: {type(exc).__name__})"
    else:
        print(f"⚙️ [API /api/audit] ไม่ได้ตั้งค่า LLM API Key -> ดำเนินการผ่าน Built-in Local Engine")
        audit_result = audit_po_and_documents(po_data, invoice_text, contract_text)
        audit_engine = "Built-in Local Audit Engine"

    # บันทึกผลลัพธ์ลง Cache เพื่อใช้ซ้ำในครั้งต่อไป
    try:
        save_cached_audit(
            cache_key=cache_key,
            po_number=po_no,
            invoice_hash=cache_meta["invoice_hash"],
            contract_hash=cache_meta["contract_hash"],
            model_name=active_model,
            audit_result=audit_result,
            audit_engine=audit_engine,
            db_path=settings.db_path
        )
        print(f"💾 [Cache Saved] บันทึกผลตรวจลง Cache เรียบร้อยแล้ว (Key: {cache_key[:12]}...)")
    except Exception as save_err:
        print(f"⚠️ [Cache Warning] บันทึก Cache ไม่สำเร็จ: {save_err}")
    
    return JSONResponse(content={
        "success": True,
        "po_data": po_data,
        "audit": audit_result,
        "audit_engine": audit_engine,
        "preset_key": preset_key,
        "session_id": session_id,
        "cached": False
    })


@app.get("/api/document/preview")
async def api_preview_document(
    doc_type: str = "invoice",
    query: Optional[str] = None,
    preset_key: Optional[str] = None,
    session_id: Optional[str] = None,
    page: int = 0
):
    """เรนเดอร์ภาพหน้าเอกสาร PDF พร้อมไฮไลท์ข้อความที่สกัดมา"""
    active_preset = preset_key or (LATEST_SESSION.get("preset_key") if not session_id else None)
    active_session = session_id or LATEST_SESSION.get("session_id")
    
    pdf_source = None
    filename = ""

    if active_preset and active_preset in PRESET_MAP:
        preset = PRESET_MAP[active_preset]
        pdf_path = preset["invoice_pdf"] if doc_type == "invoice" else preset["contract_pdf"]
        if os.path.exists(pdf_path):
            pdf_source = pdf_path
            filename = os.path.basename(pdf_path)
    elif active_session and active_session in SESSION_UPLOADS:
        sess = SESSION_UPLOADS[active_session]
        if doc_type == "invoice" and sess.get("invoice_bytes"):
            pdf_source = sess["invoice_bytes"]
            filename = sess.get("invoice_name", "invoice.pdf")
        elif doc_type == "contract" and sess.get("contract_bytes"):
            pdf_source = sess["contract_bytes"]
            filename = sess.get("contract_name", "contract.pdf")

    # Fallback to Case 6 if nothing specified
    if not pdf_source:
        fallback_preset = PRESET_MAP["case6"]
        fallback_path = fallback_preset["invoice_pdf"] if doc_type == "invoice" else fallback_preset["contract_pdf"]
        if os.path.exists(fallback_path):
            pdf_source = fallback_path
            filename = os.path.basename(fallback_path)

    if not pdf_source:
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์เอกสาร PDF สำหรับแสดงตัวอย่าง")

    res = render_pdf_page_with_highlight(
        pdf_source=pdf_source,
        query=query,
        page_idx=page,
        doc_type=doc_type
    )
    res["filename"] = filename
    res["doc_type"] = doc_type
    return JSONResponse(content=res)


@app.get("/api/history")
async def api_get_history():
    """ดึงรายการประวัติการตรวจสอบทั้งหมด"""
    try:
        history = get_audit_history(settings.db_path)
        return JSONResponse(content={"success": True, "history": history, "total": len(history)})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาดในการโหลดประวัติ: {str(exc)}")


@app.get("/api/history/{cache_key}")
async def api_get_history_detail(cache_key: str):
    """ดึงรายละเอียดผลการตรวจสอบฉบับเต็มของรายการประวัติ"""
    record = get_audit_by_cache_key(cache_key, settings.db_path)
    if not record:
        raise HTTPException(status_code=404, detail="ไม่พบประวัติการตรวจสอบนี้ในระบบ")
    return JSONResponse(content={"success": True, **record})


@app.delete("/api/history/{cache_key}")
async def api_delete_history_item(cache_key: str):
    """ลบประวัติการตรวจรายการเดียว"""
    success = delete_audit_history(cache_key, settings.db_path)
    return JSONResponse(content={"success": success, "message": "ลบรายการประวัติเรียบร้อยแล้ว"})


@app.delete("/api/history")
async def api_clear_all_history():
    """ล้างประวัติการตรวจทั้งหมด"""
    success = delete_audit_history(None, settings.db_path)
    return JSONResponse(content={"success": success, "message": "ล้างประวัติทั้งหมดเรียบร้อยแล้ว"})

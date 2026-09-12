import sqlite3
import hashlib
import json
from typing import List, Dict, Any, Optional

def get_db_connection(db_path: str = "enterprise.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_cache_table(db_path: str = "enterprise.db") -> None:
    """สร้างตาราง audit_cache สำหรับเก็บผลการตรวจสอบเอกสารด้วย Content Hash (SHA-256)"""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_cache (
            cache_key TEXT PRIMARY KEY,
            po_number TEXT NOT NULL,
            invoice_hash TEXT NOT NULL,
            contract_hash TEXT,
            model_name TEXT NOT NULL,
            audit_result TEXT NOT NULL,
            audit_engine TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def compute_hash(data: bytes) -> str:
    """คำนวณ SHA-256 Fingerprint จากเนื้อหาไบนารีของไฟล์"""
    return hashlib.sha256(data).hexdigest()

def compute_cache_key(
    po_data: Dict[str, Any],
    invoice_bytes: bytes,
    contract_bytes: Optional[bytes],
    model_name: str
) -> Dict[str, str]:
    """สร้าง Composite Cache Key จากรอยนิ้วมือของ PO, Invoice, Contract และ Model Name"""
    # 1. รอยนิ้วมือข้อมูล PO ในระบบ
    po_canonical = (
        f"{po_data.get('po_number')}|{po_data.get('vendor_id')}|"
        f"{po_data.get('approved_amount')}|{po_data.get('tax_id')}|"
        f"{po_data.get('bank_account')}|{po_data.get('standard_credit_days')}"
    )
    po_hash = hashlib.sha256(po_canonical.encode("utf-8")).hexdigest()
    
    # 2. รอยนิ้วมือไบนารีไฟล์จริง
    inv_hash = compute_hash(invoice_bytes) if invoice_bytes else ""
    con_hash = compute_hash(contract_bytes) if contract_bytes else ""
    
    # 3. รวมเป็น Cache Key ก้อนเดียว (Composite Fingerprint)
    composite_raw = f"{po_hash}:{inv_hash}:{con_hash}:{model_name.strip()}"
    cache_key = hashlib.sha256(composite_raw.encode("utf-8")).hexdigest()
    
    return {
        "cache_key": cache_key,
        "po_hash": po_hash,
        "invoice_hash": inv_hash,
        "contract_hash": con_hash,
        "model_name": model_name
    }

def get_cached_audit(cache_key: str, db_path: str = "enterprise.db") -> Optional[Dict[str, Any]]:
    """ค้นหาผลการตรวจสอบจาก Cache ในฐานข้อมูล"""
    init_cache_table(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT audit_result, audit_engine, created_at
        FROM audit_cache
        WHERE cache_key = ?
    """, (cache_key,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE audit_cache SET last_accessed_at = CURRENT_TIMESTAMP WHERE cache_key = ?", (cache_key,))
        conn.commit()
        conn.close()
        try:
            audit_data = json.loads(row["audit_result"])
            return {
                "audit": audit_data,
                "audit_engine": row["audit_engine"],
                "created_at": row["created_at"]
            }
        except Exception:
            return None
    conn.close()
    return None

def save_cached_audit(
    cache_key: str,
    po_number: str,
    invoice_hash: str,
    contract_hash: Optional[str],
    model_name: str,
    audit_result: Dict[str, Any],
    audit_engine: str,
    db_path: str = "enterprise.db"
) -> None:
    """บันทึกผลการตรวจสอบลง Cache เพื่อใช้ซ้ำในครั้งต่อไป"""
    init_cache_table(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    audit_json = json.dumps(audit_result, ensure_ascii=False)
    cursor.execute("""
        INSERT INTO audit_cache (
            cache_key, po_number, invoice_hash, contract_hash, model_name, audit_result, audit_engine, created_at, last_accessed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ON CONFLICT(cache_key) DO UPDATE SET
            audit_result = excluded.audit_result,
            audit_engine = excluded.audit_engine,
            last_accessed_at = CURRENT_TIMESTAMP
    """, (cache_key, po_number, invoice_hash, contract_hash or "", model_name, audit_json, audit_engine))
    conn.commit()
    conn.close()

def get_all_pos(db_path: str = "enterprise.db") -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    query = """
        SELECT 
            p.po_number,
            p.vendor_id,
            p.project_site,
            p.scope_of_work,
            p.approved_amount,
            p.standard_credit_days,
            v.vendor_name,
            v.tax_id,
            v.bank_name,
            v.bank_account
        FROM purchase_orders p
        JOIN vendor_master v ON p.vendor_id = v.vendor_id
        ORDER BY p.po_number ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_po_detail(po_number: str, db_path: str = "enterprise.db") -> Optional[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    query = """
        SELECT 
            p.po_number,
            p.vendor_id,
            p.project_site,
            p.scope_of_work,
            p.approved_amount,
            p.standard_credit_days,
            v.vendor_name,
            v.tax_id,
            v.bank_name,
            v.bank_account
        FROM purchase_orders p
        JOIN vendor_master v ON p.vendor_id = v.vendor_id
        WHERE p.po_number = ?
    """
    cursor.execute(query, (po_number,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_audit_history(db_path: str = "enterprise.db") -> List[Dict[str, Any]]:
    """ดึงรายการประวัติการตรวจสอบย้อนหลังทั้งหมด พร้อมข้อมูล PO และ Vendor"""
    init_cache_table(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    query = """
        SELECT 
            c.cache_key,
            c.po_number,
            c.model_name,
            c.audit_engine,
            c.audit_result,
            c.created_at,
            c.last_accessed_at,
            p.project_site,
            p.approved_amount,
            v.vendor_name
        FROM audit_cache c
        LEFT JOIN purchase_orders p ON c.po_number = p.po_number
        LEFT JOIN vendor_master v ON p.vendor_id = v.vendor_id
        ORDER BY c.created_at DESC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    history = []
    for r in rows:
        row_dict = dict(r)
        status = "UNKNOWN"
        status_label = ""
        findings_count = 0
        final_payable_amount = None
        action_recommendation = ""
        try:
            audit_data = json.loads(row_dict["audit_result"])
            status = audit_data.get("status", "UNKNOWN")
            status_label = audit_data.get("status_label", "")
            findings_count = len(audit_data.get("discrepancies", []))
            fin_sum = audit_data.get("financial_summary") or {}
            final_payable_amount = fin_sum.get("final_payable_amount")
            action_recommendation = audit_data.get("action_recommendation", "")
        except Exception:
            pass

        history.append({
            "cache_key": row_dict["cache_key"],
            "po_number": row_dict["po_number"],
            "vendor_name": row_dict.get("vendor_name") or "ไม่ระบุคู่ค้า",
            "project_site": row_dict.get("project_site") or "ไม่ระบุโครงการ",
            "approved_amount": row_dict.get("approved_amount"),
            "status": status,
            "status_label": status_label,
            "findings_count": findings_count,
            "final_payable_amount": final_payable_amount,
            "action_recommendation": action_recommendation,
            "audit_engine": row_dict["audit_engine"],
            "model_name": row_dict["model_name"],
            "created_at": row_dict["created_at"],
            "last_accessed_at": row_dict["last_accessed_at"],
        })
    return history


def get_audit_by_cache_key(cache_key: str, db_path: str = "enterprise.db") -> Optional[Dict[str, Any]]:
    """ดึงข้อมูลผลการตรวจสอบฉบับเต็มของประวัติรายการที่เลือก พร้อมข้อมูล PO"""
    init_cache_table(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cache_key, po_number, audit_result, audit_engine, created_at, last_accessed_at
        FROM audit_cache
        WHERE cache_key = ?
    """, (cache_key,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    po_data = get_po_detail(row["po_number"], db_path)
    try:
        audit_data = json.loads(row["audit_result"])
    except Exception:
        audit_data = {}

    return {
        "cache_key": row["cache_key"],
        "po_number": row["po_number"],
        "po_data": po_data,
        "audit": audit_data,
        "audit_engine": row["audit_engine"],
        "created_at": row["created_at"],
        "last_accessed_at": row["last_accessed_at"],
    }


def delete_audit_history(cache_key: Optional[str] = None, db_path: str = "enterprise.db") -> bool:
    """ลบประวัติการตรวจรายการเดียว หรือลบทั้งหมดหากไม่ระบุ cache_key"""
    init_cache_table(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    if cache_key:
        cursor.execute("DELETE FROM audit_cache WHERE cache_key = ?", (cache_key,))
    else:
        cursor.execute("DELETE FROM audit_cache")
    conn.commit()
    conn.close()
    return True

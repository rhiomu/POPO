# Smart PO & Invoice Auditor ⚖️
### Automated Purchase Order & Invoice Reconciliation Dashboard
**ระบบตรวจเช็ค PO และบิลคู่ค้าอัตโนมัติด้วย AI สำหรับการเรียนการสอน Vibe Coding**

---

## 📌 ภาพรวมโปรเจกต์ (Project Overview)
โปรเจกต์นี้เป็นชุดสื่อการสอนและระบบต้นแบบ (Teaching Kit & Reference Solution) สำหรับสอนผู้เรียนสร้าง Web Application ตรวจสอบความถูกต้องระหว่าง **"คำสั่งซื้อในระบบจัดซื้อ (PO ใน SQLite Database)"** กับ **"บิลเรียกเก็บเงินของคู่ค้า (Invoice PDF & Contract PDF)"** เพื่อสกัดจับจุดผิดปกติ 8 มิติสำคัญ:
1. **ยอดงอกนอกใบ PO (Unapproved Scope Charges):** คู่ค้าสอดไส้ค่าบริการฉุกเฉินหรือค่าเดินทาง
2. **ส่งมอบงานล่าช้า (Late Delivery Penalty):** คำนวณหักค่าเสียหายจากการล่าช้า (Liquidated Damages) ตามสัญญา
3. **ความเสี่ยงทุจริต/สวมรอยบิล (Fraud & Diversion Risk):** เลขประจำตัวผู้เสียภาษี 13 หลัก หรือเลขบัญชีธนาคารไม่ตรงกับ Vendor Master
4. **เบิกเงินเกินงวดงาน (Over-milestone Billing):** สัญญากำหนดแคปงวดงานไว้ แต่วางบิลขอเบิกเกินสิทธิ์
5. **ตรวจรับของไม่ครบ (Partial Delivery & Backorder):** สั่ง 10 ได้ 7 ชิ้น แต่วางบิลเต็มจำนวน
6. **การหักเงินค้ำประกันผลงาน (Warranty Retention 5%):** ไม่ยอมหักเงินประกันตามสัญญา
7. **PO หมดอายุสัญญา (Expired PO / Missing Amendment):** ส่งมอบหลังวันสิ้นสุดสัญญาโดยไม่มีใบแก้ไขสัญญา
8. **ข้อผิดพลาดทางคณิตศาสตร์ (Line Items vs Subtotal Math Error):** ผลรวมรายการย่อยไม่ตรงกับ Subtotal บนบิล

---

## 📂 โครงสร้างไฟล์ในชุดการสอน (Directory Structure)

```
PO/
├── AGENTS.md                         # กฎเหล็กสภาพแวดล้อม Cloud Coder มาตรฐานกลางสำหรับ AI Assistant
├── po_vibe_coding_assignment.pdf     # 📄 เอกสารโจทย์ฉบับสมบูรณ์ (PDF พร้อมแจกนักเรียน - รองรับ 8 เคส)
├── po_vibe_coding_assignment.docx    # 📝 เอกสารโจทย์ฉบับ Word (แก้ไขปรับแต่งได้)
├── po_vibe_coding_assignment.md      # 📑 เอกสารโจทย์ฉบับ Markdown
├── prompt_template_cheat_sheet.txt   # 💡 คัมภีร์ Prompt แบบ Step-by-Step สำหรับผู้เรียน Vibe Coding
│
├── enterprise.db                     # 📦 ฐานข้อมูล SQLite (vendor_master 8 ราย + purchase_orders 8 รายการ)
├── sample_documents/                 # 📄 โฟลเดอร์ไฟล์ PDF จำลอง 8 ชุดสถานการณ์ (Case 1 - 8 รวม 16 ไฟล์)
│   ├── Case1_Invoice_PO089.pdf       #   - บิล Case 1: มียอดงอก 20,000 บ.
│   ├── Case1_Contract_PO089.pdf      #   - สัญญา Case 1: ส่งงานช้า 10 วัน (ปรับ 10,000 บ.)
│   ├── Case2_Invoice_PO090.pdf       #   - บิล Case 2: Clean Approval 450,000 บ.
│   ├── Case2_Contract_PO090.pdf      #   - สัญญา Case 2: ตรวจรับผ่าน 100%
│   ├── Case3_Invoice_PO091.pdf       #   - บิล Case 3: Tax ID และเลขบัญชีธนาคารปลอม
│   ├── Case3_Contract_PO091.pdf      #   - สัญญา Case 3: บัญชีทางการของคู่ค้า
│   ├── Case4_Invoice_PO092.pdf       #   - บิล Case 4: ขอเบิก 50% = 1,000,000 บ.
│   ├── Case4_Contract_PO092.pdf      #   - สัญญา Case 4: แคปงวดที่ 1 เบิกได้สูงสุด 30%
│   ├── Case5_Invoice_PO093.pdf       #   - บิล Case 5: เก็บเงินเต็ม 10 ชุด แต่รับจริง 7 ชุด
│   ├── Case5_Contract_PO093.pdf      #   - สัญญา Case 5: ตรวจรับจริงได้ 7 ชุด (Backorder 3 ชุด)
│   ├── Case6_Invoice_PO094.pdf       #   - บิล Case 6: ขอเบิกเต็ม 3 ล้าน ไม่ยอมหัก Retention 5%
│   ├── Case6_Contract_PO094.pdf      #   - สัญญา Case 6: สัญญาระบุหัก Retention 5% ค้ำประกัน 1 ปี
│   ├── Case7_Invoice_PO095.pdf       #   - บิล Case 7: ส่งงานหลัง PO หมดอายุเกือบ 2 เดือน
│   ├── Case7_Contract_PO095.pdf      #   - สัญญา Case 7: PO หมดอายุ 30 มิ.ย. 2026 (ไม่มีใบ Amendment)
│   ├── Case8_Invoice_PO096.pdf       #   - บิล Case 8: รวมรายการได้ 500,000 บ. แต่ Subtotal เขียน 550,000 บ.
│   └── Case8_Contract_PO096.pdf      #   - สัญญา Case 8: สัญญาสั่งซื้อ 3 รายการย่อย รวม 500,000 บ.
│
├── reset_data.py                     # 🔄 สคริปต์คำสั่งเดียวสำหรับ Reset ฐานข้อมูลและ PDF เริ่มต้น 8 เคส
├── pyproject.toml                    # ⚙️ uv project configuration
├── run.sh                            # 🚀 Shell script สำหรับรันแอปพลิเคชัน
├── run.py                            # 🚀 Python entrypoint
├── templates/
│   └── index.html                    # 🎨 หน้าจอ Modern Enterprise Dashboard (Tailwind CSS รองรับ 8 เคส)
└── src/
    └── po_auditor/
        ├── config.py                 # Pydantic Settings + Mask Secret Keys
        ├── db.py                     # ฟังก์ชันเชื่อมต่อ SQLite enterprise.db
        ├── pdf_extractor.py          # ตัวสกัดข้อความภาษาไทย/อังกฤษจาก PDF ด้วย pypdf
        ├── auditor.py                # สมองกลตรวจจับ 8 จุดดัก และคำนวณยอดเงินสุทธิ
        └── app.py                    # FastAPI Backend + Template Routes
```

---

## 🚀 วิธีการรันระบบตัวอย่าง (How to Run Reference Web App)

### 1. ติดตั้ง Dependencies (ใช้ `uv`)
```bash
uv sync
```

### 2. รันระบบ (ผูกบน Port 8000 แบบ Single-Port)
```bash
./run.sh
# หรือรันผ่าน uv
uv run python run.py
```

### 3. เปิดใช้งานบน Browser
* **Local Machine:** เปิด [http://localhost:8000](http://localhost:8000)
* **Cloud Coder (Proxy Mode):** เปิดผ่าน Subpath URL ที่องค์กรกำหนด เช่น:  
  `https://<host>/@<user>/<workspace>/apps/code-server/proxy/8000/`

---

## 🧪 ตารางเคสทดสอบและผลวินิจฉัย (Ground Truth Test Matrix)

| ชุดทดสอบ | รหัส PO | จุดดักในเอกสาร PDF | ผลการวินิจฉัยของระบบ | สถานะ & สี |
|:---|:---:|:---|:---|:---:|
| **Case 1** | `PO-2026-089` | • ยอดงอก 20,000 บ. (Emergency Fee)<br>• ส่งงานล่าช้า 10 วัน (ปรับ 10,000 บ.)<br>• บิลขอเครดิตเทอม 15 วัน (PO ระบุ 30 วัน) | • ตัดยอดงอก 20,000 บ.<br>• หักค่าปรับส่งช้า 10,000 บ.<br>👉 ยอดจ่ายสุทธิ: 990,000 บ. (+VAT) | 🟡 **WARNING** |
| **Case 2** | `PO-2026-090` | • เอกสารถูกต้อง ยอด 450,000 บ. ตรงเป๊ะ<br>• ส่งมอบตรงเวลา ผ่าน QC ครบ | • อนุมัติเบิกจ่ายได้เต็มจำนวน<br>👉 ยอดจ่ายสุทธิ: 450,000 บ. (+VAT) | 🟢 **APPROVED** |
| **Case 3** | `PO-2026-091` | • Tax ID บนบิลเป็น 0995559999999 (ไม่ตรง)<br>• ธนาคารบนบิลระบุ SCB 999-9-99999-9 (ไม่ตรง) | • **ตรวจพบความเสี่ยงทุจริตสวมรอยบิล!**<br>👉 คำสั่ง: ระงับการจ่ายเงินทันที | 🔴 **FRAUD ALERT** |
| **Case 4** | `PO-2026-092` | • บิลขอเบิกงวด 50% = 1,000,000 บ.<br>• สัญญาระบุงวดที่ 1 เบิกได้สูงสุด 30% | • เบิกเงินเกินงวดงานไป 400,000 บ.<br>👉 แนะนำ: ตีบิลกลับให้แก้ไขยอด | 🟡 **WARNING** |
| **Case 5** | `PO-2026-093` | • สั่ง 10 ชุด (1.2 ล้านบ.) แต่ตรวจรับจริงได้ 7 ชุด (840k)<br>• ของขาด 3 ชุด แต่วางบิลเรียกเก็บเงินเต็ม 10 ชุด | • ตรวจจับ Partial Delivery<br>• ปรับลดยอดตามของจริง 7 ชุด (ตัด 360,000 บ.)<br>👉 ยอดจ่ายสุทธิ: 840,000 บ. (+VAT) | 🟡 **WARNING** |
| **Case 6** | `PO-2026-094` | • ส่งมอบงวดสุดท้าย วงเงิน 3 ล้านบ.<br>• สัญญาให้หัก Retention 5% (150,000 บ.) แต่บิลเบิกเต็ม | • ตรวจพบสัญญาให้หักเงินประกันผลงาน 5%<br>• หักเงินค้ำไว้จ่ายหลังครบ 1 ปี<br>👉 ยอดจ่ายสุทธิ: 2,850,000 บ. (+VAT) | 🟡 **WARNING** |
| **Case 7** | `PO-2026-095` | • PO หมดอายุวันที่ 30 มิ.ย. 2026<br>• ส่งมอบจริง 20 ส.ค. 2026 โดยไม่มีใบขยายสัญญา | • PO หมดอายุสัญญาโดยไม่มีใบขอขยายเวลา<br>👉 คำสั่ง: ระงับจ่ายชั่วคราว (Hold Payment) | ⏸️ **HOLD PAYMENT** |
| **Case 8** | `PO-2026-096` | • รายการย่อย 3 รายการรวมได้ 500,000 บ.<br>• แต่ Subtotal และ VAT คำนวณจากยอด 550,000 บ. | • ตรวจพบข้อผิดพลาดคำนวณเลขในบิล (Math Error)<br>👉 แนะนำ: ตีบิลกลับให้คู่ค้าแก้ไขยอด | 🟡 **WARNING** |

---

## 🔄 คำสั่งสำหรับ Reset ข้อมูล (Reset Database & PDFs)
หากผู้เรียนเผลอแก้ไขฐานข้อมูลหรือไฟล์ PDF เสียหาย สามารถรันคำสั่งนี้เพื่อคืนค่าเริ่มต้นได้ทันที:
```bash
uv run python reset_data.py
```


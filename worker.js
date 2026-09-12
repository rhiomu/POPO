// Cloudflare Worker for Smart PO & Invoice Auditor Demo
// Automatically generated for Cloudflare Workers deployment

const HTML_CONTENT = "<!DOCTYPE html>\n<html lang=\"th\">\n<head>\n  <meta charset=\"UTF-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n  <title>Smart PO & Invoice Auditor — ตรวจเช็คบิลคู่ค้าอัตโนมัติด้วย AI</title>\n  <script src=\"https://cdn.tailwindcss.com\"></script>\n  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n  <link href=\"https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600;700&family=Inter:wght@400;500;600;700&display=swap\" rel=\"stylesheet\">\n  <style>\n    body { font-family: 'Prompt', 'Inter', sans-serif; }\n    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }\n\n    /* เมื่อแสดงผลจากประวัติย้อนหลัง: พื้นหลังเทา + ดรอปสีการ์ดให้หม่นลง 1 เฉด */\n    .history-mode-active {\n      background-color: #f1f5f9 !important; /* พื้นหลังเทา Slate-100 */\n      padding: 1.5rem !important;\n      border-radius: 1.5rem !important;\n      border: 2px dashed #cbd5e1 !important; /* ขอบประวัติ Slate-300 */\n      transition: all 0.3s ease;\n    }\n    .history-mode-active .bg-white {\n      background-color: #f8fafc !important; /* ดรอปสีขาวสว่างลง 1 เฉด เป็น Slate-50 */\n      border-color: #cbd5e1 !important; /* ขอบเข้มขึ้นเป็น Slate-300 */\n      box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.04) !important;\n    }\n    .history-mode-active #statusBanner {\n      filter: saturate(0.55) brightness(0.92); /* ดรอปสีแบนเนอร์ให้หม่นลง 1 เฉด */\n      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05) !important;\n    }\n    .history-mode-active #findingsList > div {\n      filter: saturate(0.60) brightness(0.94); /* ดรอปสีการ์ดรายการให้หม่นลง */\n    }\n    .history-mode-active table thead {\n      background-color: #e2e8f0 !important; /* หัวตารางหม่นลง */\n    }\n    .history-mode-active .bg-slate-50 {\n      background-color: #e2e8f0 !important; /* กล่องย่อยหม่นลง */\n    }\n  </style>\n</head>\n<body class=\"bg-slate-50 text-slate-800 min-h-screen flex flex-col\">\n\n  <!-- Navigation Bar -->\n  <header class=\"bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md\">\n    <div class=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between\">\n      <div class=\"flex items-center space-x-3\">\n        <div class=\"w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/30\">\n          ⚖️\n        </div>\n        <div>\n          <div class=\"flex items-center space-x-2\">\n            <h1 class=\"font-bold text-lg tracking-tight\">Smart PO & Invoice Auditor</h1>\n            <span class=\"text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2 py-0.5 rounded-full font-medium\">Enterprise 8-Cases Edition</span>\n          </div>\n          <p class=\"text-xs text-slate-400\">ระบบตรวจสอบคำสั่งซื้อชนบิลคู่ค้า และตรวจจับความผิดปกติด้วย AI</p>\n        </div>\n      </div>\n      <div class=\"flex items-center space-x-3 text-xs\">\n        <button onclick=\"openHistoryModal()\" type=\"button\" class=\"flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 hover:border-slate-600 px-3.5 py-1.5 rounded-xl font-medium transition cursor-pointer shadow-sm\">\n          <span>📜 ประวัติการวิเคราะห์</span>\n          <span id=\"historyHeaderCount\" class=\"bg-blue-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full\">0</span>\n        </button>\n        <div class=\"flex items-center space-x-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-medium\">\n          <span class=\"w-2 h-2 rounded-full bg-emerald-500 animate-pulse\"></span>\n          <span>Port 8000 (Monolith Ready)</span>\n        </div>\n      </div>\n    </div>\n  </header>\n\n  <!-- Main Container -->\n  <main class=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6\">\n\n    <!-- Input Control Card -->\n    <div class=\"bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-6\">\n      <div class=\"border-b border-slate-100 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2\">\n        <div>\n          <h2 class=\"text-base font-bold text-slate-900 flex items-center space-x-2\">\n            <span>⚙️</span>\n            <span>ขั้นตอนที่ 1 & 2: เลือกใบสั่งซื้อและอัปโหลดเอกสารคู่ค้า</span>\n          </h2>\n          <p class=\"text-xs text-slate-500 mt-0.5\">เชื่อมต่อฐานข้อมูล SQLite (<code class=\"mono text-blue-600\">enterprise.db</code>) ชนเอกสาร PDF</p>\n        </div>\n      </div>\n\n      <div class=\"grid grid-cols-1 md:grid-cols-3 gap-6\">\n        <!-- Step 1: PO Selector -->\n        <div class=\"space-y-2\">\n          <label class=\"block text-xs font-bold text-slate-700 uppercase tracking-wider\">\n            1. เลือกเลขที่ใบสั่งซื้อ (PO from Database)\n          </label>\n          <div class=\"relative\">\n            <select id=\"poSelect\" onchange=\"onPoSelected()\" class=\"w-full bg-slate-50 border border-slate-300 rounded-xl px-3.5 py-2.5 text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:outline-none transition\">\n              <option value=\"\">-- กำลังโหลดรายการ PO... --</option>\n            </select>\n          </div>\n          <p class=\"text-[11px] text-slate-400\">ดึงข้อมูลจริงจากตาราง <span class=\"mono\">purchase_orders</span> (มีทั้งหมด 8 รายการ)</p>\n        </div>\n\n        <!-- Step 2: Invoice Upload -->\n        <div class=\"space-y-2\">\n          <label class=\"block text-xs font-bold text-slate-700 uppercase tracking-wider\">\n            2. แนบไฟล์ใบแจ้งหนี้ (Invoice PDF)\n          </label>\n          <input type=\"file\" id=\"invoiceFile\" onchange=\"clearPreset()\" accept=\".pdf\" class=\"block w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3.5 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-slate-200 rounded-xl bg-slate-50 cursor-pointer\">\n          <p id=\"invoiceStatusHint\" class=\"text-[11px] text-slate-400\">รองรับไฟล์ .pdf จากคู่ค้า</p>\n        </div>\n\n        <!-- Step 3: Contract Upload -->\n        <div class=\"space-y-2\">\n          <label class=\"block text-xs font-bold text-slate-700 uppercase tracking-wider\">\n            3. แนบสัญญา/ใบตรวจรับ (Contract/GR PDF)\n          </label>\n          <input type=\"file\" id=\"contractFile\" onchange=\"clearPreset()\" accept=\".pdf\" class=\"block w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3.5 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 border border-slate-200 rounded-xl bg-slate-50 cursor-pointer\">\n          <p id=\"contractStatusHint\" class=\"text-[11px] text-slate-400\">เอกสารเงื่อนไขค่าปรับหรืองวดงาน</p>\n        </div>\n      </div>\n\n      <div class=\"pt-2 flex flex-col sm:flex-row items-center justify-between gap-4\">\n        <div id=\"activePresetBadge\" class=\"hidden text-xs bg-amber-50 text-amber-800 border border-amber-200 px-3 py-1.5 rounded-xl font-medium items-center space-x-1.5\">\n          <span>⚡ ใช้ข้อมูลจำลอง:</span>\n          <span id=\"presetLabel\" class=\"font-bold\"></span>\n          <button onclick=\"clearPreset()\" class=\"text-slate-400 hover:text-slate-600 ml-1\">✕</button>\n        </div>\n        <div class=\"flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto ml-auto justify-end\">\n          <label class=\"inline-flex items-center space-x-2 text-xs text-slate-600 cursor-pointer bg-slate-50 hover:bg-slate-100 border border-slate-200 px-3 py-2.5 rounded-xl transition select-none\" title=\"ติ๊กเพื่อข้าม Cache และส่ง AI ประมวลผลใหม่สดๆ ทุกครั้ง\">\n            <input type=\"checkbox\" id=\"forceReauditCheckbox\" class=\"rounded border-slate-300 text-blue-600 focus:ring-blue-500 cursor-pointer\">\n            <span class=\"font-medium\">🔄 ตรวจสดใหม่ (ไม่ใช้ Cache)</span>\n          </label>\n          <button onclick=\"openHistoryModal()\" id=\"historyBtn\" type=\"button\" class=\"w-full sm:w-auto px-4 py-2.5 rounded-xl border border-blue-200 bg-blue-50/80 hover:bg-blue-100 text-blue-700 font-semibold text-sm flex items-center justify-center space-x-2 transition shadow-sm cursor-pointer\">\n            <span>📜 ประวัติการวิเคราะห์</span>\n            <span id=\"historyActionCount\" class=\"bg-blue-600 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full\">0</span>\n          </button>\n          <button onclick=\"clearAll()\" id=\"clearBtn\" type=\"button\" class=\"w-full sm:w-auto px-5 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 font-semibold text-sm flex items-center justify-center space-x-2 transition shadow-sm hover:border-slate-400 cursor-pointer\">\n            <span>🔄 ล้างข้อมูล (Clear)</span>\n          </button>\n          <button onclick=\"runAudit()\" id=\"runBtn\" class=\"w-full sm:w-auto bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold text-sm px-6 py-2.5 rounded-xl shadow-lg shadow-blue-500/25 flex items-center justify-center space-x-2 transition disabled:opacity-50\">\n            <span>⚡ ตรวจสอบเอกสารด้วย AI (Run AI Audit)</span>\n          </button>\n        </div>\n      </div>\n    </div>\n\n    <!-- PO Details Card (Loaded from DB) -->\n    <div id=\"poDetailCard\" class=\"hidden bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4\">\n      <div class=\"flex items-center justify-between border-b border-slate-100 pb-3\">\n        <h3 class=\"text-sm font-bold text-slate-800 flex items-center space-x-2\">\n          <span>🏢</span>\n          <span>ข้อมูลจัดซื้อในระบบทางการ (Official PO & Vendor Master Data)</span>\n        </h3>\n        <span id=\"poBadgeSite\" class=\"text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-lg font-medium\"></span>\n      </div>\n      <div class=\"grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-xs\">\n        <div class=\"bg-slate-50 p-3 rounded-xl border border-slate-100\">\n          <span class=\"text-slate-400 block mb-0.5\">เลขที่ PO</span>\n          <span id=\"poNoView\" class=\"font-bold text-slate-900 mono text-sm\"></span>\n        </div>\n        <div class=\"bg-slate-50 p-3 rounded-xl border border-slate-100 lg:col-span-2\">\n          <span class=\"text-slate-400 block mb-0.5\">ชื่อบริษัทคู่ค้า (Vendor Name)</span>\n          <span id=\"vendorNameView\" class=\"font-bold text-slate-900 truncate block\"></span>\n        </div>\n        <div class=\"bg-slate-50 p-3 rounded-xl border border-slate-100\">\n          <span class=\"text-slate-400 block mb-0.5\">เลข Tax ID (13 หลัก)</span>\n          <span id=\"taxIdView\" class=\"font-bold text-slate-900 mono\"></span>\n        </div>\n        <div class=\"bg-slate-50 p-3 rounded-xl border border-slate-100\">\n          <span class=\"text-slate-400 block mb-0.5\">วงเงินอนุมัติ (ก่อน VAT)</span>\n          <span id=\"amountView\" class=\"font-bold text-blue-700 text-sm\"></span>\n        </div>\n        <div class=\"bg-slate-50 p-3 rounded-xl border border-slate-100\">\n          <span class=\"text-slate-400 block mb-0.5\">เครดิตเทอมมาตรฐาน</span>\n          <span id=\"creditDaysView\" class=\"font-bold text-slate-900\"></span>\n        </div>\n      </div>\n      <div class=\"bg-slate-50 p-3 rounded-xl border border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2\">\n        <div>\n          <span class=\"text-slate-400\">บัญชีธนาคารทางการ: </span>\n          <span id=\"bankAccountView\" class=\"font-bold text-slate-800 mono\"></span>\n        </div>\n        <div>\n          <span class=\"text-slate-400\">ขอบเขตงาน: </span>\n          <span id=\"scopeView\" class=\"font-medium text-slate-700\"></span>\n        </div>\n      </div>\n    </div>\n\n    <!-- Audit Results Section -->\n    <div id=\"resultsSection\" class=\"hidden space-y-6\">\n\n      <!-- Historical Archive Notice Banner -->\n      <div id=\"historyNoticeBanner\" class=\"hidden p-3.5 bg-slate-200/90 border border-slate-300/90 text-slate-700 rounded-2xl text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2 shadow-xs transition\">\n        <div class=\"flex items-center space-x-2.5\">\n          <span class=\"text-base\">📜</span>\n          <div>\n            <span class=\"font-bold text-slate-800\">กำลังแสดงผลวิเคราะห์จากประวัติ (Historical Archive View)</span>\n            <span id=\"historyNoticeDate\" class=\"text-slate-500 ml-1\"></span>\n          </div>\n        </div>\n        <div class=\"flex items-center space-x-3\">\n          <span class=\"text-[11px] bg-slate-300 text-slate-800 font-semibold px-2.5 py-0.5 rounded-full\">โหมดดูประวัติย้อนหลัง</span>\n          <button type=\"button\" onclick=\"document.getElementById('forceReauditCheckbox').checked = true; runAudit();\" class=\"text-blue-700 hover:text-blue-900 font-bold hover:underline text-xs flex items-center space-x-1 cursor-pointer\">\n            <span>🔄 ตรวจสดใหม่ด้วย AI</span>\n          </button>\n        </div>\n      </div>\n\n      <!-- Status Banner -->\n      <div id=\"statusBanner\" class=\"rounded-2xl p-6 shadow-lg border text-white transition\">\n        <div class=\"flex flex-col md:flex-row md:items-center justify-between gap-4\">\n          <div class=\"space-y-1\">\n            <div class=\"flex items-center space-x-2 flex-wrap gap-y-1\">\n              <span id=\"statusIcon\" class=\"text-2xl\"></span>\n              <span id=\"statusTitle\" class=\"text-xl font-bold tracking-tight\"></span>\n              <span id=\"engineBadge\" class=\"text-[11px] bg-white/20 border border-white/30 px-2.5 py-0.5 rounded-full font-medium\"></span>\n            </div>\n            <p id=\"statusAction\" class=\"text-sm opacity-90 leading-relaxed\"></p>\n          </div>\n          <button onclick=\"copySummary()\" class=\"bg-white/20 hover:bg-white/30 text-white text-xs font-semibold px-4 py-2.5 rounded-xl border border-white/30 flex items-center space-x-2 transition self-start md:self-center shadow\">\n            <span>📋</span>\n            <span>คัดลอกผลสรุปส่งอีเมล</span>\n          </button>\n        </div>\n      </div>\n\n      <!-- Discrepancy Findings -->\n      <div id=\"findingsCard\" class=\"bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4\">\n        <h3 class=\"text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3\">\n          <span>🔍</span>\n          <span>รายการข้อตรวจพบความผิดปกติ (Audit Findings & Anomaly Breakdown)</span>\n        </h3>\n        <div id=\"findingsList\" class=\"space-y-3\"></div>\n      </div>\n\n      <!-- Side-by-Side Comparison Matrix -->\n      <div class=\"bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4\">\n        <div class=\"flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 pb-3 gap-2\">\n          <h3 class=\"text-sm font-bold text-slate-900 flex items-center space-x-2\">\n            <span>⚖️</span>\n            <span>ตารางเปรียบเทียบข้อมูลระบบ VS ข้อมูลบิลคู่ค้า (Side-by-Side Comparison Matrix)</span>\n          </h3>\n          <div class=\"flex items-center space-x-2\">\n            <button type=\"button\" onclick=\"openDocumentModal('invoice', '', 'ภาพเอกสารใบแจ้งหนี้')\" class=\"px-3 py-1.5 rounded-xl border border-blue-200 bg-blue-50/80 hover:bg-blue-100 text-blue-700 font-semibold text-xs flex items-center space-x-1.5 transition cursor-pointer shadow-xs\">\n              <span>📄 ดูใบแจ้งหนี้ (Invoice PDF)</span>\n            </button>\n            <button type=\"button\" onclick=\"openDocumentModal('contract', '', 'ภาพเอกสารสัญญา/ใบตรวจรับ')\" class=\"px-3 py-1.5 rounded-xl border border-indigo-200 bg-indigo-50/80 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs flex items-center space-x-1.5 transition cursor-pointer shadow-xs\">\n              <span>📑 ดูสัญญา/GR (Contract PDF)</span>\n            </button>\n          </div>\n        </div>\n        <p class=\"text-[11px] text-slate-600 bg-blue-50/60 p-2.5 rounded-xl border border-blue-100 flex items-center space-x-2\">\n          <span class=\"text-sm\">💡</span>\n          <span><strong>ทิป:</strong> คลิกที่ตัวเลขหรือข้อความในคอลัมน์ <em>\"ข้อมูลที่สกัดได้จากบิล PDF\"</em> (เช่น เลข Tax ID <span class=\"mono font-bold text-blue-700\">0105547089112</span>, เลขบัญชี, ยอดเงิน) เพื่อเปิดดูภาพเอกสารจริงและไฮไลท์จุดที่ AI อ่านค่ามาได้ทันที</span>\n        </p>\n        <div class=\"overflow-x-auto\">\n          <table class=\"w-full text-xs text-left\">\n            <thead class=\"bg-slate-100 text-slate-600 font-bold uppercase tracking-wider border-b border-slate-200\">\n              <tr>\n                <th class=\"py-3 px-4\">หัวข้อตรวจสอบ</th>\n                <th class=\"py-3 px-4\">ข้อมูลจัดซื้อในระบบ (PO Database)</th>\n                <th class=\"py-3 px-4\">ข้อมูลที่สกัดได้จากบิล PDF</th>\n                <th class=\"py-3 px-4 text-center\">สถานะความสอดคล้อง</th>\n              </tr>\n            </thead>\n            <tbody id=\"comparisonTableBody\" class=\"divide-y divide-slate-100\"></tbody>\n          </table>\n        </div>\n      </div>\n\n      <!-- Financial Settlement Table -->\n      <div class=\"bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4\">\n        <h3 class=\"text-sm font-bold text-slate-900 flex items-center space-x-2 border-b border-slate-100 pb-3\">\n          <span>💰</span>\n          <span>สรุปตัวเลขการจ่ายเงิน (Financial Settlement & Reconciliation)</span>\n        </h3>\n        <div class=\"grid grid-cols-1 md:grid-cols-2 gap-6\">\n          <!-- Breakdown List -->\n          <div class=\"space-y-2.5 text-xs\">\n            <div class=\"flex justify-between py-1.5 border-b border-slate-100\">\n              <span class=\"text-slate-500\">วงเงินอนุมัติตาม PO (Base Budget):</span>\n              <span id=\"finPoBase\" class=\"font-bold text-slate-800 mono\"></span>\n            </div>\n            <div class=\"flex justify-between py-1.5 border-b border-slate-100\">\n              <span class=\"text-slate-500\">ยอดที่คู่ค้าเรียกเก็บบนบิล (Billed Subtotal):</span>\n              <span id=\"finBilledSubtotal\" class=\"font-medium text-slate-700 mono\"></span>\n            </div>\n            <div class=\"flex justify-between py-1.5 border-b border-slate-100 text-amber-700\">\n              <span>(-) หักยอดงอก / ของไม่ครบ / หัก Retention / ค่าปรับ:</span>\n              <span id=\"finExtraDeduct\" class=\"font-bold mono\"></span>\n            </div>\n          </div>\n\n          <!-- Total Due Box -->\n          <div class=\"bg-slate-50 rounded-xl p-5 border border-slate-200 flex flex-col justify-between space-y-4\">\n            <div class=\"space-y-2 text-xs\">\n              <div class=\"flex justify-between text-slate-600\">\n                <span>ยอดเงินอนุมัติจ่ายจริง (ก่อน VAT):</span>\n                <span id=\"finNetSubtotal\" class=\"font-bold mono text-sm text-slate-900\"></span>\n              </div>\n              <div class=\"flex justify-between text-slate-600\">\n                <span>ภาษีมูลค่าเพิ่ม (VAT 7%):</span>\n                <span id=\"finVat\" class=\"font-medium mono text-slate-700\"></span>\n              </div>\n            </div>\n            <div class=\"pt-3 border-t border-slate-200 flex justify-between items-center\">\n              <div>\n                <span class=\"text-xs font-bold text-slate-500 uppercase tracking-wider block\">ยอดจ่ายสุทธิที่แนะนำ (Total Due)</span>\n                <span class=\"text-[10px] text-slate-400\">รวม VAT 7% สุทธิแล้ว</span>\n              </div>\n              <span id=\"finTotalDue\" class=\"text-xl font-black text-blue-700 mono\"></span>\n            </div>\n          </div>\n        </div>\n      </div>\n\n    </div>\n\n  <!-- Audit History Modal -->\n  <div id=\"historyModal\" onclick=\"if(event.target === this) closeHistoryModal()\" class=\"hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 transition-all duration-200\">\n    <div class=\"bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150\">\n      \n      <!-- Modal Header -->\n      <div class=\"px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800\">\n        <div class=\"flex items-center space-x-3\">\n          <div class=\"w-9 h-9 rounded-xl bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-lg text-blue-400\">\n            📜\n          </div>\n          <div>\n            <h3 class=\"text-sm font-bold flex items-center space-x-2\">\n              <span>ประวัติการตรวจสอบย้อนหลัง (Audit History Archive)</span>\n              <span id=\"historyModalCountBadge\" class=\"text-[11px] bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-0.5 rounded-full font-semibold\">0 รายการ</span>\n            </h3>\n            <p class=\"text-[11px] text-slate-400\">คลิกที่รายการเพื่อเปิดดูผลการวิเคราะห์และข้อตรวจพบฉบับเต็มได้ทันที</p>\n          </div>\n        </div>\n        <div class=\"flex items-center space-x-2\">\n          <button type=\"button\" onclick=\"clearAllHistory()\" class=\"text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/20 border border-transparent hover:border-rose-500/30 px-3 py-1.5 rounded-lg transition cursor-pointer\" title=\"ล้างประวัติการตรวจทั้งหมด\">\n            🗑️ ล้างทั้งหมด\n          </button>\n          <button type=\"button\" onclick=\"closeHistoryModal()\" class=\"w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm transition cursor-pointer\" title=\"ปิด (ESC)\">\n            ✕\n          </button>\n        </div>\n      </div>\n\n      <!-- Toolbar: Search & Filter Pills -->\n      <div class=\"px-6 py-3 border-b border-slate-200 bg-slate-50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs\">\n        <div class=\"relative w-full sm:w-72\">\n          <span class=\"absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400\">🔍</span>\n          <input type=\"text\" id=\"historySearchInput\" oninput=\"filterHistoryList()\" placeholder=\"ค้นหาเลข PO, ชื่อคู่ค้า, โครงการ...\" class=\"w-full pl-8 pr-3 py-1.5 bg-white border border-slate-300 rounded-xl text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none transition\">\n        </div>\n        <div class=\"flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0\" id=\"historyStatusFilters\">\n          <button type=\"button\" onclick=\"setHistoryFilter('ALL')\" id=\"filterBtnALL\" class=\"history-filter-btn px-2.5 py-1 rounded-lg font-semibold bg-slate-800 text-white transition cursor-pointer\">ทั้งหมด</button>\n          <button type=\"button\" onclick=\"setHistoryFilter('APPROVED')\" id=\"filterBtnAPPROVED\" class=\"history-filter-btn px-2.5 py-1 rounded-lg font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition cursor-pointer\">🟢 ผ่าน</button>\n          <button type=\"button\" onclick=\"setHistoryFilter('WARNING')\" id=\"filterBtnWARNING\" class=\"history-filter-btn px-2.5 py-1 rounded-lg font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition cursor-pointer\">🟡 เตือน</button>\n          <button type=\"button\" onclick=\"setHistoryFilter('HOLD_PAYMENT')\" id=\"filterBtnHOLD_PAYMENT\" class=\"history-filter-btn px-2.5 py-1 rounded-lg font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition cursor-pointer\">⏸️ ระงับชั่วคราว</button>\n          <button type=\"button\" onclick=\"setHistoryFilter('FRAUD_ALERT')\" id=\"filterBtnFRAUD_ALERT\" class=\"history-filter-btn px-2.5 py-1 rounded-lg font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition cursor-pointer\">🔴 ทุจริต</button>\n        </div>\n      </div>\n\n      <!-- History Items Container -->\n      <div id=\"historyListContainer\" class=\"p-6 overflow-y-auto max-h-[60vh] space-y-3 flex-1 bg-slate-50/60\">\n        <!-- Dynamic history cards inserted here -->\n      </div>\n\n      <!-- Modal Footer -->\n      <div class=\"px-6 py-3 bg-white border-t border-slate-200 flex items-center justify-between text-xs text-slate-500\">\n        <span>💡 ผลการตรวจที่ดึงจากประวัติจะไม่เสียโควตาและไม่ต้องรอ AI ประมวลผลใหม่</span>\n        <button type=\"button\" onclick=\"closeHistoryModal()\" class=\"px-4 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 font-medium transition cursor-pointer\">\n          ปิดหน้าต่าง\n        </button>\n      </div>\n    </div>\n  </div>\n\n  <!-- Document Viewer & Highlighting Modal -->\n  <div id=\"docModal\" onclick=\"if(event.target === this) closeDocumentModal()\" class=\"hidden fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 transition-all duration-200\">\n    <div class=\"bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-5xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150\">\n      \n      <!-- Modal Header -->\n      <div class=\"px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800\">\n        <div class=\"flex items-center space-x-3\">\n          <div class=\"w-9 h-9 rounded-xl bg-blue-600/30 border border-blue-500/40 flex items-center justify-center text-lg text-blue-400\">\n            📄\n          </div>\n          <div>\n            <h3 class=\"text-sm font-bold flex items-center space-x-2\">\n              <span>ภาพเอกสารต้นฉบับและการตรวจสอบตำแหน่ง (Document Visual Grounding)</span>\n            </h3>\n            <p class=\"text-[11px] text-slate-400\">ตรวจสอบจุดที่ AI สกัดข้อความมาเปรียบเทียบ พร้อมไฮไลท์กรอบสีเหลือง-แดง</p>\n          </div>\n        </div>\n        <button type=\"button\" onclick=\"closeDocumentModal()\" class=\"w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm transition cursor-pointer\" title=\"ปิด (ESC)\">\n          ✕\n        </button>\n      </div>\n\n      <!-- Control Toolbar -->\n      <div class=\"px-6 py-3 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs\">\n        \n        <!-- Document Tabs -->\n        <div class=\"flex items-center space-x-1.5 bg-slate-200/80 p-1 rounded-xl\">\n          <button type=\"button\" id=\"tabInvoice\" onclick=\"switchDocType('invoice')\" class=\"px-3 py-1.5 rounded-lg font-bold transition flex items-center space-x-1 bg-white text-blue-700 shadow-sm cursor-pointer\">\n            <span>📄 ใบแจ้งหนี้ (Invoice PDF)</span>\n          </button>\n          <button type=\"button\" id=\"tabContract\" onclick=\"switchDocType('contract')\" class=\"px-3 py-1.5 rounded-lg font-medium text-slate-600 hover:text-slate-900 transition flex items-center space-x-1 cursor-pointer\">\n            <span>📑 สัญญา/ใบตรวจรับ (Contract PDF)</span>\n          </button>\n        </div>\n\n        <!-- Search & Highlight in Doc -->\n        <div class=\"flex items-center space-x-2 flex-1 max-w-md\">\n          <div class=\"relative w-full\">\n            <input type=\"text\" id=\"modalSearchInput\" onkeydown=\"if(event.key==='Enter') applyModalSearch()\" placeholder=\"พิมพ์คำที่ต้องการค้นหาและไฮไลท์ในเอกสาร...\" class=\"w-full bg-white border border-slate-300 rounded-xl px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500\">\n          </div>\n          <button type=\"button\" onclick=\"applyModalSearch()\" class=\"px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition shadow-sm cursor-pointer whitespace-nowrap\">\n            🎯 ไฮไลท์\n          </button>\n        </div>\n\n        <!-- Zoom Controls -->\n        <div class=\"flex items-center space-x-2 text-slate-600\">\n          <button type=\"button\" onclick=\"changeZoom(-0.15)\" class=\"w-7 h-7 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 flex items-center justify-center font-bold transition cursor-pointer\" title=\"ย่อ\">-</button>\n          <span id=\"zoomLevelText\" class=\"font-mono text-[11px] w-12 text-center\">100%</span>\n          <button type=\"button\" onclick=\"changeZoom(0.15)\" class=\"w-7 h-7 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 flex items-center justify-center font-bold transition cursor-pointer\" title=\"ขยาย\">+</button>\n          <button type=\"button\" onclick=\"resetZoom()\" class=\"px-2 py-1 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 text-[11px] transition cursor-pointer\" title=\"ขนาดปกติ\">100%</button>\n        </div>\n\n      </div>\n\n      <!-- Match Info Status Banner -->\n      <div id=\"modalStatusBanner\" class=\"px-6 py-2 bg-amber-50/90 border-b border-amber-200/60 flex items-center justify-between text-xs text-amber-900\">\n        <div class=\"flex items-center space-x-2\">\n          <span id=\"modalStatusIcon\">🎯</span>\n          <span id=\"modalStatusText\" class=\"font-medium\">กำลังโหลดเอกสาร...</span>\n        </div>\n        <div class=\"flex items-center space-x-2 text-[11px] text-slate-500\">\n          <span id=\"modalDocFilename\" class=\"mono font-semibold text-slate-700\"></span>\n          <span id=\"modalPageIndicator\" class=\"bg-white px-2 py-0.5 rounded border border-slate-200\"></span>\n        </div>\n      </div>\n\n      <!-- Modal Body (Image Container) -->\n      <div class=\"flex-1 overflow-auto p-6 bg-slate-100/80 flex items-start justify-center min-h-[460px] relative\">\n        <!-- Loading Spinner -->\n        <div id=\"modalLoading\" class=\"hidden absolute inset-0 bg-white/70 backdrop-blur-xs flex flex-col items-center justify-center z-10 space-y-2\">\n          <div class=\"w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin\"></div>\n          <span class=\"text-xs font-semibold text-slate-700\">กำลังเรนเดอร์เอกสารและไฮไลท์ตำแหน่ง...</span>\n        </div>\n\n        <!-- Document Image Wrapper -->\n        <div id=\"modalImgWrapper\" class=\"transition-transform duration-150 origin-top shadow-xl rounded-lg bg-white overflow-hidden border border-slate-200\">\n          <img id=\"modalDocImg\" src=\"\" alt=\"Document Preview\" class=\"max-w-full block select-none\">\n        </div>\n      </div>\n\n      <!-- Modal Footer -->\n      <div class=\"px-6 py-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs\">\n        <div class=\"text-slate-500 flex items-center space-x-1.5\">\n          <span>💡 สามารถเลื่อน Scroll หรือใช้ปุ่ม +/- เพื่อซูมขยายตรวจสอบข้อความต้นฉบับได้ชัดเจน</span>\n        </div>\n        <div class=\"flex items-center space-x-2\">\n          <button type=\"button\" onclick=\"closeDocumentModal()\" class=\"px-4 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 font-semibold transition cursor-pointer\">\n            ปิดหน้าต่าง (Close)\n          </button>\n        </div>\n      </div>\n\n    </div>\n  </div>\n\n  <!-- Toast Notification -->\n  <div id=\"toast\" class=\"fixed bottom-6 right-6 bg-slate-900 text-white text-xs px-4 py-3 rounded-xl shadow-2xl flex items-center space-x-2 transform translate-y-20 opacity-0 transition duration-300 pointer-events-none z-50\">\n    <span class=\"text-emerald-400\">✓</span>\n    <span id=\"toastMsg\">คัดลอกข้อมูลเรียบร้อยแล้ว</span>\n  </div>\n\n  <!-- JavaScript -->\n  <script>\n    let currentSelectedPreset = null;\n    let currentEmailSummaryText = \"\";\n    let poCache = {};\n    let currentHistoryList = [];\n    let activeHistoryFilter = 'ALL';\n\n    const presetMap = {\n      'case1': { po: 'PO-2026-089', label: 'Case 1: ยอดงอก + ค่าปรับส่งช้า 10 วัน' },\n      'case2': { po: 'PO-2026-090', label: 'Case 2: เอกสารตรงตามสัญญาครบถ้วน (Clean Approved)' },\n      'case3': { po: 'PO-2026-091', label: 'Case 3: เลขประจำตัวผู้เสียภาษี & บัญชีปลอม (Fraud Alert)' },\n      'case4': { po: 'PO-2026-092', label: 'Case 4: ขอเบิกเกินงวดงาน 50% vs Cap 30%' },\n      'case5': { po: 'PO-2026-093', label: 'Case 5: ส่งของไม่ครบ 7/10 ชุด แต่บิลเก็บเต็ม 100%' },\n      'case6': { po: 'PO-2026-094', label: 'Case 6: ลืมหักเงินประกันผลงาน (Retention 5%)' },\n      'case7': { po: 'PO-2026-095', label: 'Case 7: งานส่งมอบหลัง PO หมดอายุ (Hold รอ Amendment)' },\n      'case8': { po: 'PO-2026-096', label: 'Case 8: บิลคิดเลขผิด Subtotal ไม่ตรงกับ Line Items' }\n    };\n\n    async function init() {\n      try {\n        const res = await fetch('./api/pos');\n        const data = await res.json();\n        const select = document.getElementById('poSelect');\n        select.innerHTML = '<option value=\"\">-- กรุณาเลือกเลขที่ PO --</option>';\n        data.pos.forEach(po => {\n          poCache[po.po_number] = po;\n          const opt = document.createElement('option');\n          opt.value = po.po_number;\n          opt.textContent = `${po.po_number} | ${po.vendor_name} (${Number(po.approved_amount).toLocaleString()} บ.)`;\n          select.appendChild(opt);\n        });\n      } catch (err) {\n        console.error('Error fetching POs:', err);\n      }\n      loadHistory();\n    }\n\n    // ==========================================\n    // ประวัติการตรวจสอบย้อนหลัง (Audit History)\n    // ==========================================\n    async function loadHistory() {\n      try {\n        const res = await fetch('./api/history');\n        const data = await res.json();\n        if (data.success && Array.isArray(data.history)) {\n          currentHistoryList = data.history;\n          const count = currentHistoryList.length;\n\n          const headerBadge = document.getElementById('historyHeaderCount');\n          if (headerBadge) headerBadge.textContent = count;\n\n          const actionBadge = document.getElementById('historyActionCount');\n          if (actionBadge) actionBadge.textContent = count;\n\n          const modalBadge = document.getElementById('historyModalCountBadge');\n          if (modalBadge) modalBadge.textContent = `${count} รายการ`;\n\n          renderHistoryList();\n        }\n      } catch (err) {\n        console.error('Error loading history:', err);\n      }\n    }\n\n    function openHistoryModal() {\n      const modal = document.getElementById('historyModal');\n      if (modal) {\n        modal.classList.remove('hidden');\n        loadHistory();\n      }\n    }\n\n    function closeHistoryModal() {\n      const modal = document.getElementById('historyModal');\n      if (modal) {\n        modal.classList.add('hidden');\n      }\n    }\n\n    function setHistoryFilter(filter) {\n      activeHistoryFilter = filter;\n      const buttons = document.querySelectorAll('.history-filter-btn');\n      buttons.forEach(btn => {\n        btn.classList.remove('bg-slate-800', 'text-white');\n        btn.classList.add('bg-white', 'border', 'border-slate-200', 'text-slate-700');\n      });\n      const activeBtn = document.getElementById(`filterBtn${filter}`);\n      if (activeBtn) {\n        activeBtn.classList.remove('bg-white', 'border', 'border-slate-200', 'text-slate-700');\n        activeBtn.classList.add('bg-slate-800', 'text-white');\n      }\n      renderHistoryList();\n    }\n\n    function filterHistoryList() {\n      renderHistoryList();\n    }\n\n    function renderHistoryList() {\n      const container = document.getElementById('historyListContainer');\n      if (!container) return;\n\n      const searchKeyword = (document.getElementById('historySearchInput')?.value || '').trim().toLowerCase();\n\n      const filtered = currentHistoryList.filter(item => {\n        if (activeHistoryFilter !== 'ALL' && item.status !== activeHistoryFilter) {\n          return false;\n        }\n        if (searchKeyword) {\n          const textToSearch = `${item.po_number} ${item.vendor_name} ${item.project_site} ${item.status_label || ''} ${item.action_recommendation || ''}`.toLowerCase();\n          if (!textToSearch.includes(searchKeyword)) {\n            return false;\n          }\n        }\n        return true;\n      });\n\n      if (filtered.length === 0) {\n        container.innerHTML = `\n          <div class=\"text-center py-12 px-4 bg-white rounded-2xl border border-dashed border-slate-200 text-slate-400\">\n            <span class=\"text-3xl block mb-2\">📭</span>\n            <p class=\"text-sm font-semibold text-slate-700\">ไม่พบข้อมูลประวัติการวิเคราะห์</p>\n            <p class=\"text-xs text-slate-400 mt-1\">${searchKeyword || activeHistoryFilter !== 'ALL' ? 'ลองปรับคำค้นหาหรือเปลี่ยนตัวกรองใหม่อีกครั้ง' : 'เมื่อทำการตรวจสอบเอกสาร PO ระบบจะบันทึกผลการตรวจลงประวัติให้อัตโนมัติ'}</p>\n          </div>\n        `;\n        return;\n      }\n\n      const getStatusBadge = (status) => {\n        if (status === 'APPROVED') {\n          return `<span class=\"px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200\">🟢 ผ่าน (Approved)</span>`;\n        } else if (status === 'WARNING') {\n          return `<span class=\"px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-50 text-amber-700 border border-amber-200\">🟡 เตือน (Warning)</span>`;\n        } else if (status === 'HOLD_PAYMENT') {\n          return `<span class=\"px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-orange-50 text-orange-700 border border-orange-200\">⏸️ ระงับชั่วคราว (Hold)</span>`;\n        } else {\n          return `<span class=\"px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-50 text-rose-700 border border-rose-200\">🔴 ทุจริต (Fraud Alert)</span>`;\n        }\n      };\n\n      container.innerHTML = filtered.map(item => {\n        const timeStr = item.created_at || item.last_accessed_at || '-';\n        const payableFormatted = item.final_payable_amount != null \n          ? Number(item.final_payable_amount).toLocaleString() + ' ฿' \n          : 'ไม่ระบุ';\n\n        return `\n          <div class=\"bg-white rounded-2xl p-4 border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300 transition flex flex-col sm:flex-row sm:items-center justify-between gap-4\">\n            <div class=\"space-y-1.5 flex-1 min-w-0\">\n              <div class=\"flex items-center space-x-2 flex-wrap gap-y-1\">\n                <span class=\"font-black text-sm mono text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-lg border border-blue-100\">${item.po_number}</span>\n                ${getStatusBadge(item.status)}\n                <span class=\"text-[11px] text-slate-400\">📅 ${timeStr}</span>\n              </div>\n              <div class=\"text-xs text-slate-800 font-semibold truncate\">\n                🏢 ${item.vendor_name} <span class=\"font-normal text-slate-500\">• ${item.project_site}</span>\n              </div>\n              <div class=\"flex items-center space-x-3 text-[11px] text-slate-600 flex-wrap gap-y-1\">\n                <span>💰 ยอดจ่ายสุทธิ: <strong class=\"text-slate-900\">${payableFormatted}</strong></span>\n                <span class=\"text-slate-300\">•</span>\n                <span class=\"text-amber-700 font-medium\">⚠️ ข้อตรวจพบ: ${item.findings_count} รายการ</span>\n                <span class=\"text-slate-300\">•</span>\n                <span class=\"text-slate-400 truncate max-w-[200px]\" title=\"${item.audit_engine || ''}\">🤖 ${item.audit_engine || 'AI Engine'}</span>\n              </div>\n            </div>\n            <div class=\"flex items-center space-x-2 self-end sm:self-center shrink-0\">\n              <button onclick=\"viewHistoricalAudit('${item.cache_key}')\" class=\"px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold text-xs rounded-xl shadow-md shadow-blue-500/20 flex items-center space-x-1.5 transition cursor-pointer\">\n                <span>👁️</span>\n                <span>เปิดดูผลวิเคราะห์</span>\n              </button>\n              <button onclick=\"deleteHistoryItem('${item.cache_key}', event)\" class=\"p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition cursor-pointer\" title=\"ลบประวัติตัวนี้\">\n                🗑️\n              </button>\n            </div>\n          </div>\n        `;\n      }).join('');\n    }\n\n    async function viewHistoricalAudit(cacheKey) {\n      try {\n        const res = await fetch(`./api/history/${cacheKey}`);\n        const data = await res.json();\n        if (!res.ok) {\n          alert('ไม่สามารถโหลดประวัติได้: ' + (data.detail || ''));\n          return;\n        }\n\n        // 1. ตั้งค่าเลขที่ PO ใน dropdown\n        const poSelect = document.getElementById('poSelect');\n        if (poSelect) {\n          poSelect.value = data.po_number;\n        }\n\n        // 2. เรนเดอร์ข้อมูล PO Master\n        if (data.po_data) {\n          const po = data.po_data;\n          document.getElementById('poNoView').textContent = po.po_number;\n          document.getElementById('vendorNameView').textContent = po.vendor_name;\n          document.getElementById('taxIdView').textContent = po.tax_id;\n          document.getElementById('amountView').textContent = Number(po.approved_amount).toLocaleString() + ' ฿';\n          document.getElementById('creditDaysView').textContent = po.standard_credit_days + ' วัน';\n          document.getElementById('bankAccountView').textContent = `${po.bank_name} (${po.bank_account})`;\n          document.getElementById('scopeView').textContent = po.scope_of_work;\n          document.getElementById('poBadgeSite').textContent = po.project_site;\n          document.getElementById('poDetailCard').classList.remove('hidden');\n        }\n\n        // 3. เรนเดอร์ผลการตรวจสอบ (Audit Results)\n        renderAuditResults(data.audit, data.audit_engine, true, data.created_at, true);\n\n        // 4. ปิดหน้าต่างประวัติ\n        closeHistoryModal();\n\n        // 5. เลื่อนหน้าจอไปที่ส่วนผลการตรวจอย่างนุ่มนวล\n        const resultsSection = document.getElementById('resultsSection');\n        if (resultsSection) {\n          resultsSection.scrollIntoView({ behavior: 'smooth' });\n        }\n\n        // 6. แจ้งเตือน Toast\n        showToast(`📜 เปิดดูผลวิเคราะห์ย้อนหลังของ ${data.po_number} เรียบร้อยแล้ว`);\n      } catch (err) {\n        console.error('Error viewing history:', err);\n        alert('เกิดข้อผิดพลาดในการโหลดผลการวิเคราะห์: ' + err.message);\n      }\n    }\n\n    async function deleteHistoryItem(cacheKey, event) {\n      if (event) event.stopPropagation();\n      if (!confirm('คุณต้องการลบประวัติการตรวจรายการนี้ใช่หรือไม่?')) return;\n\n      try {\n        const res = await fetch(`./api/history/${cacheKey}`, { method: 'DELETE' });\n        const data = await res.json();\n        if (data.success) {\n          showToast('ลบรายการประวัติเรียบร้อยแล้ว');\n          loadHistory();\n        } else {\n          alert('ลบรายการไม่สำเร็จ: ' + (data.message || ''));\n        }\n      } catch (err) {\n        console.error('Error deleting history item:', err);\n        alert('เกิดข้อผิดพลาดในการลบรายการ: ' + err.message);\n      }\n    }\n\n    async function clearAllHistory() {\n      if (!confirm('⚠️ คำเตือน: คุณต้องการล้างประวัติการตรวจสอบย้อนหลังทั้งหมดใช่หรือไม่?\\n(ผลวิเคราะห์เดิมและ Cache จะถูกล้างทั้งหมด)')) {\n        return;\n      }\n\n      try {\n        const res = await fetch('./api/history', { method: 'DELETE' });\n        const data = await res.json();\n        if (data.success) {\n          showToast('ล้างประวัติการตรวจสอบทั้งหมดเรียบร้อยแล้ว');\n          loadHistory();\n        } else {\n          alert('ไม่สามารถล้างประวัติได้: ' + (data.message || ''));\n        }\n      } catch (err) {\n        console.error('Error clearing history:', err);\n        alert('เกิดข้อผิดพลาดในการล้างประวัติ: ' + err.message);\n      }\n    }\n\n    async function onPoSelected() {\n      const poNo = document.getElementById('poSelect').value;\n      const card = document.getElementById('poDetailCard');\n      if (!poNo) {\n        card.classList.add('hidden');\n        return;\n      }\n\n      try {\n        const res = await fetch(`./api/pos/${poNo}`);\n        const data = await res.json();\n        const po = data.po;\n\n        document.getElementById('poNoView').textContent = po.po_number;\n        document.getElementById('vendorNameView').textContent = po.vendor_name;\n        document.getElementById('taxIdView').textContent = po.tax_id;\n        document.getElementById('amountView').textContent = Number(po.approved_amount).toLocaleString() + ' ฿';\n        document.getElementById('creditDaysView').textContent = po.standard_credit_days + ' วัน';\n        document.getElementById('bankAccountView').textContent = `${po.bank_name} (${po.bank_account})`;\n        document.getElementById('scopeView').textContent = po.scope_of_work;\n        document.getElementById('poBadgeSite').textContent = po.project_site;\n\n        card.classList.remove('hidden');\n      } catch (err) {\n        console.error('Error fetching PO detail:', err);\n      }\n    }\n\n    function loadPreset(caseKey) {\n      currentSelectedPreset = caseKey;\n      const p = presetMap[caseKey];\n      if (p) {\n        document.getElementById('poSelect').value = p.po;\n        onPoSelected();\n        document.getElementById('presetLabel').textContent = p.label;\n        document.getElementById('activePresetBadge').classList.remove('hidden');\n        document.getElementById('activePresetBadge').classList.add('inline-flex');\n        runAudit();\n      }\n    }\n\n    function clearPreset() {\n      currentSelectedPreset = null;\n      document.getElementById('activePresetBadge').classList.add('hidden');\n      document.getElementById('activePresetBadge').classList.remove('inline-flex');\n    }\n\n    function clearAll() {\n      // 1. ล้างค่ารายการ PO ที่เลือก\n      const poSelect = document.getElementById('poSelect');\n      if (poSelect) poSelect.value = '';\n\n      // 2. ล้างไฟล์แนบทั้ง 2 ช่อง\n      const invInput = document.getElementById('invoiceFile');\n      if (invInput) invInput.value = '';\n      const conInput = document.getElementById('contractFile');\n      if (conInput) conInput.value = '';\n\n      // 3. ยกเลิกพรีเซ็ตจำลอง\n      clearPreset();\n\n      // 4. ซ่อนการ์ดข้อมูล PO จากฐานข้อมูล\n      const poCard = document.getElementById('poDetailCard');\n      if (poCard) poCard.classList.add('hidden');\n\n      // 5. ซ่อนส่วนผลการตรวจสอบ (Audit Results)\n      const resultsSection = document.getElementById('resultsSection');\n      if (resultsSection) {\n        resultsSection.classList.add('hidden');\n        resultsSection.classList.remove('history-mode-active');\n      }\n      const historyNotice = document.getElementById('historyNoticeBanner');\n      if (historyNotice) historyNotice.classList.add('hidden');\n\n      // 6. ล้างข้อความสรุปและเซสชันเอกสาร\n      currentEmailSummaryText = '';\n      currentAuditSessionId = null;\n      closeDocumentModal();\n\n      // 7. รีเซ็ตปุ่ม force reaudit\n      const forceReaudit = document.getElementById('forceReauditCheckbox');\n      if (forceReaudit) forceReaudit.checked = false;\n\n      // 8. แจ้งเตือน Toast\n      showToast('ล้างข้อมูลและผลการตรวจสอบเรียบร้อยแล้ว');\n    }\n\n    async function runAudit() {\n      const poNo = document.getElementById('poSelect').value;\n      if (!poNo) {\n        alert('กรุณาเลือกเลขที่ PO ก่อนเริ่มตรวจสอบ');\n        return;\n      }\n\n      const runBtn = document.getElementById('runBtn');\n      runBtn.disabled = true;\n\n      let elapsedSeconds = 0;\n      const updateButtonText = () => {\n        if (elapsedSeconds < 3) {\n          runBtn.innerHTML = `<span>⏳ กำลังอ่านและดึงข้อมูลจากเอกสาร PDF (${elapsedSeconds}s)...</span>`;\n        } else if (elapsedSeconds < 65) {\n          runBtn.innerHTML = `<span>🤖 AI กำลังคิดวิเคราะห์ (Reasoning & Cross-Check ${elapsedSeconds}s)...</span>`;\n        } else {\n          runBtn.innerHTML = `<span>📊 กำลังประมวลผลตัวเลขและจัดทำรายงาน (${elapsedSeconds}s)...</span>`;\n        }\n      };\n      updateButtonText();\n      const stageInterval = setInterval(() => {\n        elapsedSeconds++;\n        updateButtonText();\n      }, 1000);\n\n      const controller = new AbortController();\n      const timeoutId = setTimeout(() => controller.abort(), 95000);\n\n      try {\n        const formData = new FormData();\n        formData.append('po_number', poNo);\n\n        const forceReaudit = document.getElementById('forceReauditCheckbox')?.checked || false;\n        formData.append('force_reaudit', forceReaudit ? 'true' : 'false');\n\n        if (currentSelectedPreset) {\n          formData.append('preset_key', currentSelectedPreset);\n        } else {\n          const invFile = document.getElementById('invoiceFile').files[0];\n          const conFile = document.getElementById('contractFile').files[0];\n          if (invFile) formData.append('invoice_file', invFile);\n          if (conFile) formData.append('contract_file', conFile);\n        }\n\n        const res = await fetch('./api/audit', {\n          method: 'POST',\n          body: formData,\n          signal: controller.signal\n        });\n\n        clearTimeout(timeoutId);\n\n        const data = await res.json();\n        if (!res.ok) {\n          alert('เกิดข้อผิดพลาด: ' + (data.detail || 'ไม่สามารถตรวจสอบเอกสารได้'));\n          return;\n        }\n\n        currentAuditSessionId = data.session_id || null;\n        if (data.preset_key) currentSelectedPreset = data.preset_key;\n\n        renderAuditResults(data.audit, data.audit_engine, data.cached, data.cached_at);\n        loadHistory();\n        if (data.cached) {\n          showToast('⚡ ดึงผลลัพธ์จาก Smart Cache ทันที (0.01s • ประหยัดโควตา Token 100%)');\n        }\n      } catch (err) {\n        clearTimeout(timeoutId);\n        console.error('Audit error:', err);\n        if (err.name === 'AbortError') {\n          alert('การตรวจสอบใช้เวลานานเกินกำหนด (Timeout) กรุณาลองใหม่อีกครั้ง');\n        } else {\n          alert('เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์: ' + err.message);\n        }\n      } finally {\n        clearInterval(stageInterval);\n        runBtn.disabled = false;\n        runBtn.innerHTML = '<span>⚡ ตรวจสอบเอกสารด้วย AI (Run AI Audit)</span>';\n      }\n    }\n\n    function renderAuditResults(audit, engineName, isCached, cachedAt, isFromHistory = false) {\n      if (!audit) return;\n      const resultsSection = document.getElementById('resultsSection');\n      resultsSection.classList.remove('hidden');\n\n      const noticeBanner = document.getElementById('historyNoticeBanner');\n      const noticeDate = document.getElementById('historyNoticeDate');\n\n      if (isFromHistory) {\n        resultsSection.classList.add('history-mode-active');\n        if (noticeBanner) noticeBanner.classList.remove('hidden');\n        if (noticeDate) noticeDate.textContent = cachedAt ? `• บันทึกเมื่อ ${cachedAt}` : '';\n      } else {\n        resultsSection.classList.remove('history-mode-active');\n        if (noticeBanner) noticeBanner.classList.add('hidden');\n      }\n\n      const banner = document.getElementById('statusBanner');\n      const icon = document.getElementById('statusIcon');\n      const title = document.getElementById('statusTitle');\n      const action = document.getElementById('statusAction');\n      const engineBadge = document.getElementById('engineBadge');\n\n      if (engineBadge) {\n        if (isFromHistory) {\n          const cleanEngine = (engineName || '').replace(' [⚡ Cached Result]', '');\n          engineBadge.innerHTML = `📜 <span>ประวัติย้อนหลัง · ${cleanEngine}</span>`;\n          engineBadge.className = 'text-[11px] bg-slate-700/70 text-slate-200 border border-slate-500/60 px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1 shadow-sm';\n          engineBadge.title = `ผลวิเคราะห์นี้ดึงมาจากประวัติการตรวจสอบย้อนหลัง (บันทึกเมื่อ ${cachedAt || 'ก่อนหน้า'})`;\n        } else if (isCached || (engineName && engineName.includes('Cached Result'))) {\n          const cleanEngine = (engineName || '').replace(' [⚡ Cached Result]', '');\n          engineBadge.innerHTML = `⚡ <span>Cached (0.01s) · ${cleanEngine}</span>`;\n          engineBadge.className = 'text-[11px] bg-emerald-500/30 text-emerald-100 border border-emerald-300/40 px-2.5 py-0.5 rounded-full font-medium inline-flex items-center gap-1 shadow-sm';\n          engineBadge.title = `ผลลัพธ์ดึงมาจาก Smart Cache ในเครื่อง ไม่ส่งซ้ำไป API ประหยัดโควตา 100% (บันทึกเมื่อ ${cachedAt || 'ก่อนหน้า'})`;\n        } else {\n          engineBadge.textContent = engineName ? `⚙️ ${engineName}` : '';\n          engineBadge.className = 'text-[11px] bg-white/20 border border-white/30 px-2.5 py-0.5 rounded-full font-medium';\n          engineBadge.title = '';\n        }\n      }\n\n      const status = audit.status || 'WARNING';\n      if (status === 'APPROVED') {\n        banner.className = 'rounded-2xl p-6 shadow-lg border text-white transition bg-gradient-to-r from-emerald-600 to-teal-700 border-emerald-500';\n        icon.textContent = '🟢';\n        title.textContent = audit.status_label || '🟢 APPROVED (อนุมัติจ่ายเงินได้)';\n      } else if (status === 'WARNING') {\n        banner.className = 'rounded-2xl p-6 shadow-lg border text-white transition bg-gradient-to-r from-amber-600 to-yellow-600 border-amber-500';\n        icon.textContent = '🟡';\n        title.textContent = audit.status_label || '🟡 WARNING (พบข้อผิดพลาด / ต้องปรับลดยอด)';\n      } else if (status === 'HOLD_PAYMENT') {\n        banner.className = 'rounded-2xl p-6 shadow-lg border text-white transition bg-gradient-to-r from-orange-600 to-amber-700 border-orange-500';\n        icon.textContent = '⏸️';\n        title.textContent = audit.status_label || '🟡 HOLD PAYMENT (ระงับจ่ายชั่วคราว)';\n      } else {\n        banner.className = 'rounded-2xl p-6 shadow-lg border text-white transition bg-gradient-to-r from-rose-700 to-red-800 border-rose-600';\n        icon.textContent = '🔴';\n        title.textContent = audit.status_label || '🔴 FRAUD ALERT (ระงับการจ่ายเงินทันที)';\n      }\n      action.textContent = audit.action_recommendation || 'ตรวจสอบเอกสารเรียบร้อยแล้ว';\n\n      const findingsList = document.getElementById('findingsList');\n      findingsList.innerHTML = '';\n      const discrepancies = audit.discrepancies || [];\n      if (discrepancies.length === 0) {\n        findingsList.innerHTML = `\n          <div class=\"p-3.5 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-xs flex items-center space-x-2\">\n            <span>✓</span>\n            <span class=\"font-medium\">ไม่พบข้อผิดปกติ เอกสารและตัวเลขสอดคล้องกับสัญญาครบถ้วน 100%</span>\n          </div>\n        `;\n      } else {\n        discrepancies.forEach(d => {\n          let badgeColor = 'bg-amber-50 text-amber-900 border-amber-200';\n          if (d.severity === 'critical') badgeColor = 'bg-rose-50 text-rose-900 border-rose-200';\n          if (d.severity === 'info') badgeColor = 'bg-blue-50 text-blue-900 border-blue-200';\n\n          const item = document.createElement('div');\n          item.className = `p-3.5 rounded-xl border text-xs space-y-1 ${badgeColor}`;\n          item.innerHTML = `\n            <div class=\"font-bold flex items-center justify-between\">\n              <span>${d.title || 'ข้อตรวจพบ'}</span>\n              <span class=\"uppercase text-[10px] px-2 py-0.5 rounded-full font-bold bg-white/60\">${d.severity || 'warning'}</span>\n            </div>\n            <p class=\"text-slate-700\">${d.detail || ''}</p>\n            <p class=\"text-[11px] font-semibold opacity-90\">👉 ${d.impact || ''}</p>\n          `;\n          findingsList.appendChild(item);\n        });\n      }\n\n      const compBody = document.getElementById('comparisonTableBody');\n      compBody.innerHTML = '';\n      const compLabels = {\n        vendor_name: { label: 'บริษัทคู่ค้า', docType: 'invoice' },\n        tax_id: { label: 'เลขประจำตัวผู้เสียภาษี (Tax ID)', docType: 'invoice' },\n        bank_account: { label: 'ธนาคารและเลขที่บัญชี', docType: 'invoice' },\n        amount: { label: 'วงเงินตามใบสั่งซื้อ / เรียกเก็บ', docType: 'invoice' },\n        credit_terms: { label: 'เครดิตเทอมการชำระเงิน', docType: 'invoice' },\n        delivery_sla: { label: 'สถานะการส่งมอบงาน / SLA', docType: 'contract' }\n      };\n\n      const comp = audit.comparison || {};\n      for (const [key, cfg] of Object.entries(compLabels)) {\n        const item = comp[key] || { po: '-', doc: '-', match: true };\n        const tr = document.createElement('tr');\n        tr.className = 'hover:bg-slate-50 transition';\n        const matchBadge = item.match \n          ? `<span class=\"bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold text-[11px]\">✓ ตรงกัน</span>`\n          : `<span class=\"bg-rose-100 text-rose-800 px-2 py-0.5 rounded-full font-bold text-[11px]\">✕ ไม่ตรงกัน</span>`;\n\n        const isClickable = item.doc && item.doc !== '-' && item.doc !== 'ไม่ระบุ';\n        const docDisplay = isClickable\n          ? `<button type=\"button\" onclick=\"openDocumentModal('${cfg.docType}', '${encodeURIComponent(item.doc)}', '${cfg.label}')\" class=\"inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 hover:text-blue-900 border border-blue-200/80 hover:border-blue-300 font-semibold transition group cursor-pointer text-left\" title=\"คลิกเพื่อดูภาพเอกสารจริงและไฮไลท์ตำแหน่งที่สกัดมา\">\n              <span class=\"mono\">${item.doc}</span>\n              <span class=\"text-[10px] bg-blue-200/70 text-blue-800 px-1.5 py-0.5 rounded font-semibold group-hover:bg-blue-300 transition\">🔍 ดูเอกสาร</span>\n            </button>`\n          : `<span class=\"mono text-slate-700\">${item.doc}</span>`;\n\n        tr.innerHTML = `\n          <td class=\"py-3 px-4 font-medium text-slate-900\">${cfg.label}</td>\n          <td class=\"py-3 px-4 mono text-slate-700\">${item.po || '-'}</td>\n          <td class=\"py-3 px-4\">${docDisplay}</td>\n          <td class=\"py-3 px-4 text-center\">${matchBadge}</td>\n        `;\n        compBody.appendChild(tr);\n      }\n\n      const fin = audit.financial_summary || {};\n      const totalDeductions = Number((fin.extra_unapproved_amount || 0) + (fin.partial_short_amount || 0) + (fin.retention_deduct_amount || 0) + (fin.delay_penalty_amount || 0));\n\n      document.getElementById('finPoBase').textContent = Number(fin.po_approved_amount || 0).toLocaleString() + ' ฿';\n      document.getElementById('finBilledSubtotal').textContent = Number(fin.invoice_billed_subtotal || 0).toLocaleString() + ' ฿';\n      document.getElementById('finExtraDeduct').textContent = totalDeductions > 0 ? `-${totalDeductions.toLocaleString()} ฿` : '0.00 ฿';\n      document.getElementById('finNetSubtotal').textContent = Number(fin.net_payable_subtotal || 0).toLocaleString() + ' ฿';\n      document.getElementById('finVat').textContent = Number(fin.vat_7_pct || 0).toLocaleString() + ' ฿';\n      document.getElementById('finTotalDue').textContent = Number(fin.total_due_payable || 0).toLocaleString() + ' ฿';\n\n      currentEmailSummaryText = audit.email_summary || '';\n      resultsSection.scrollIntoView({ behavior: 'smooth' });\n    }\n\n    function copySummary() {\n      if (!currentEmailSummaryText) return;\n      navigator.clipboard.writeText(currentEmailSummaryText).then(() => {\n        showToast('คัดลอกผลสรุปการตรวจเช็คเข้า Clipboard เรียบร้อยแล้ว');\n      });\n    }\n\n    function showToast(msg) {\n      const toast = document.getElementById('toast');\n      document.getElementById('toastMsg').textContent = msg;\n      toast.classList.remove('translate-y-20', 'opacity-0');\n      setTimeout(() => {\n        toast.classList.add('translate-y-20', 'opacity-0');\n      }, 3000);\n    }\n\n    // --- Document Viewer Modal Functions ---\n    let currentModalDocType = 'invoice';\n    let currentModalQuery = '';\n    let currentModalPage = 0;\n    let currentModalZoom = 1.0;\n\n    function openDocumentModal(docType, query, label) {\n      currentModalDocType = docType || 'invoice';\n      currentModalQuery = query ? decodeURIComponent(query) : '';\n      currentModalPage = 0;\n      currentModalZoom = 1.0;\n\n      // ถ้ายังไม่มี preset ที่เลือก ให้ลองดูจากช่อง poSelect\n      if (!currentSelectedPreset && !currentAuditSessionId) {\n        const poVal = document.getElementById('poSelect').value;\n        for (const [k, v] of Object.entries(presetMap)) {\n          if (v.po === poVal) {\n            currentSelectedPreset = k;\n            break;\n          }\n        }\n      }\n\n      const modal = document.getElementById('docModal');\n      modal.classList.remove('hidden');\n\n      document.getElementById('modalSearchInput').value = currentModalQuery;\n      updateModalTabs();\n      loadModalDocument();\n    }\n\n    function closeDocumentModal() {\n      const modal = document.getElementById('docModal');\n      if (modal) modal.classList.add('hidden');\n    }\n\n    function switchDocType(type) {\n      if (currentModalDocType === type) return;\n      currentModalDocType = type;\n      currentModalPage = 0;\n      updateModalTabs();\n      loadModalDocument();\n    }\n\n    function updateModalTabs() {\n      const tabInv = document.getElementById('tabInvoice');\n      const tabCon = document.getElementById('tabContract');\n      if (!tabInv || !tabCon) return;\n\n      if (currentModalDocType === 'invoice') {\n        tabInv.className = 'px-3 py-1.5 rounded-lg font-bold transition flex items-center space-x-1 bg-white text-blue-700 shadow-sm cursor-pointer';\n        tabCon.className = 'px-3 py-1.5 rounded-lg font-medium text-slate-600 hover:text-slate-900 transition flex items-center space-x-1 cursor-pointer';\n      } else {\n        tabInv.className = 'px-3 py-1.5 rounded-lg font-medium text-slate-600 hover:text-slate-900 transition flex items-center space-x-1 cursor-pointer';\n        tabCon.className = 'px-3 py-1.5 rounded-lg font-bold transition flex items-center space-x-1 bg-white text-blue-700 shadow-sm cursor-pointer';\n      }\n    }\n\n    function applyModalSearch() {\n      currentModalQuery = document.getElementById('modalSearchInput').value.trim();\n      currentModalPage = 0;\n      loadModalDocument();\n    }\n\n    function changeZoom(delta) {\n      currentModalZoom = Math.min(Math.max(0.5, currentModalZoom + delta), 2.2);\n      applyZoom();\n    }\n\n    function resetZoom() {\n      currentModalZoom = 1.0;\n      applyZoom();\n    }\n\n    function applyZoom() {\n      const wrapper = document.getElementById('modalImgWrapper');\n      if (wrapper) {\n        wrapper.style.transform = `scale(${currentModalZoom})`;\n      }\n      const zoomText = document.getElementById('zoomLevelText');\n      if (zoomText) {\n        zoomText.textContent = `${Math.round(currentModalZoom * 100)}%`;\n      }\n    }\n\n    async function loadModalDocument() {\n      const loading = document.getElementById('modalLoading');\n      if (loading) loading.classList.remove('hidden');\n\n      try {\n        const params = new URLSearchParams();\n        params.append('doc_type', currentModalDocType);\n        if (currentModalQuery) params.append('query', currentModalQuery);\n        if (currentSelectedPreset) params.append('preset_key', currentSelectedPreset);\n        if (currentAuditSessionId) params.append('session_id', currentAuditSessionId);\n        params.append('page', currentModalPage);\n\n        const res = await fetch(`./api/document/preview?${params.toString()}`);\n        const data = await res.json();\n\n        if (!res.ok || !data.success) {\n          alert('ไม่สามารถโหลดภาพเอกสารได้: ' + (data.detail || data.error || 'เกิดข้อผิดพลาด'));\n          return;\n        }\n\n        const img = document.getElementById('modalDocImg');\n        img.src = data.image_base64;\n\n        document.getElementById('modalDocFilename').textContent = data.filename || '';\n        document.getElementById('modalPageIndicator').textContent = `หน้า ${data.page_idx + 1} / ${data.total_pages}`;\n\n        const statusIcon = document.getElementById('modalStatusIcon');\n        const statusText = document.getElementById('modalStatusText');\n\n        if (data.found) {\n          statusIcon.textContent = '🎯';\n          statusText.innerHTML = `ตรวจพบและตีกรอบไฮไลท์ข้อความ: <span class=\"font-bold underline text-amber-700 bg-amber-100/80 px-1.5 py-0.5 rounded\">${data.matched_query}</span> (${data.match_count} จุด)`;\n        } else if (currentModalQuery) {\n          statusIcon.textContent = 'ℹ️';\n          statusText.innerHTML = `ไม่พบคำว่า \"${currentModalQuery}\" ในหน้านี้ (กำลังแสดงเอกสารเต็ม)`;\n        } else {\n          statusIcon.textContent = '📄';\n          statusText.innerHTML = `แสดงภาพเอกสารต้นฉบับฉบับเต็ม`;\n        }\n\n        applyZoom();\n      } catch (err) {\n        console.error('Error loading document preview:', err);\n        alert('เกิดข้อผิดพลาดในการโหลดตัวอย่างเอกสาร');\n      } finally {\n        if (loading) loading.classList.add('hidden');\n      }\n    }\n\n    document.addEventListener('keydown', (e) => {\n      if (e.key === 'Escape') {\n        closeDocumentModal();\n        closeHistoryModal();\n      }\n    });\n\n    window.onload = init;\n  </script>\n</body>\n</html>\n";
const PO_DATA = [
  {
    "po_number": "PO-2026-089",
    "vendor_id": "VN-001",
    "project_site": "G.Brimm Power",
    "scope_of_work": "งานซ่อมบำรุงกังหันก๊าซ",
    "approved_amount": 1000000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส จำกัด",
    "tax_id": "0105556098711",
    "bank_name": "ธนาคารกสิกรไทย",
    "bank_account": "045-2-12345-6"
  },
  {
    "po_number": "PO-2026-090",
    "vendor_id": "VN-002",
    "project_site": "G.Brimm Solar",
    "scope_of_work": "จัดซื้ออินเวอร์เตอร์โซลาร์ 20 ชุด",
    "approved_amount": 450000.0,
    "standard_credit_days": 45,
    "vendor_name": "บริษัท อินโทรเวิท เทค ซัพพลาย จำกัด",
    "tax_id": "0105549012345",
    "bank_name": "ธนาคารไทยพาณิชย์",
    "bank_account": "112-3-98765-4"
  },
  {
    "po_number": "PO-2026-091",
    "vendor_id": "VN-003",
    "project_site": "G.Brimm Biomass",
    "scope_of_work": "ติดตั้งระบบบำบัดน้ำเสีย",
    "approved_amount": 800000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท เดอตี้ วอเธอร์ โซลูชั่นส์ จำกัด",
    "tax_id": "0105562045678",
    "bank_name": "ธนาคารกรุงเทพ",
    "bank_account": "201-0-55443-3"
  },
  {
    "po_number": "PO-2026-092",
    "vendor_id": "VN-004",
    "project_site": "Headquarter (Bangkok)",
    "scope_of_work": "โครงการพัฒนาระบบประหยัดพลังงาน",
    "approved_amount": 2000000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท ไอโอดี สลัด เพาเวอร์ จำกัด",
    "tax_id": "0105531089922",
    "bank_name": "ธนาคารกรุงไทย",
    "bank_account": "003-1-77889-0"
  },
  {
    "po_number": "PO-2026-093",
    "vendor_id": "VN-005",
    "project_site": "Amata City Solar",
    "scope_of_work": "จัดซื้อ Switchgear และ Inverter 10 ชุด",
    "approved_amount": 1200000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท สยาม ซัน พาวเวอร์ อีควิปเมนท์ จำกัด",
    "tax_id": "0105558012399",
    "bank_name": "ธนาคารกสิกรไทย",
    "bank_account": "029-1-88776-5"
  },
  {
    "po_number": "PO-2026-094",
    "vendor_id": "VN-006",
    "project_site": "Laem Chabang Floating Solar",
    "scope_of_work": "ติดตั้งโครงสร้างโซลาร์ลอยน้ำ (งวดสุดท้าย)",
    "approved_amount": 3000000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท เอเชีย เมกา คอนสตรัคชั่น จำกัด",
    "tax_id": "0105547089112",
    "bank_name": "ธนาคารไทยพาณิชย์",
    "bank_account": "049-2-33445-5"
  },
  {
    "po_number": "PO-2026-095",
    "vendor_id": "VN-007",
    "project_site": "Substation Rayong",
    "scope_of_work": "ซ่อมบำรุงหม้อแปลงไฟฟ้าแรงสูง",
    "approved_amount": 650000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท โกลบอล เอเนอร์ยี่ ซิสเต็มส์ จำกัด",
    "tax_id": "0105551022445",
    "bank_name": "ธนาคารกรุงเทพ",
    "bank_account": "142-0-99881-2"
  },
  {
    "po_number": "PO-2026-096",
    "vendor_id": "VN-008",
    "project_site": "Gas Plant Map Ta Phut",
    "scope_of_work": "จัดซื้อวาล์วและท่อก๊าซทนแรงดันสูง 3 รายการ",
    "approved_amount": 500000.0,
    "standard_credit_days": 30,
    "vendor_name": "บริษัท พรีเมียร์ วาล์ว แอนด์ ไปป์ จำกัด",
    "tax_id": "0105539077123",
    "bank_name": "ธนาคารกรุงไทย",
    "bank_account": "015-1-66554-3"
  }
];
let AUDIT_RECORDS = {
  "PO-TEST": {
    "cache_key": "00fbf6ee947aed8bbb8d150e69761f818455ba2598db2c270a2679ab45ed25f4",
    "po_number": "PO-TEST",
    "audit": {
      "status": "APPROVED",
      "test": 123
    },
    "audit_engine": "Test Engine",
    "created_at": "2026-09-12 16:49:02"
  },
  "PO-2026-089": {
    "cache_key": "742c510f26ebbc5d542fba6c30dfab31fb3c1843c1ada3e2369f7476be9ba1cd",
    "po_number": "PO-2026-089",
    "audit": {
      "status": "HOLD_PAYMENT",
      "status_label": "🟡 HOLD PAYMENT (พบความคลาดเคลื่อนวงเงิน, เงื่อนไขการชำระเงิน, และค่าปรับล่าช้า)",
      "action_recommendation": "ระงับการชำระเงินทันที 1. ติดต่อผู้ขายเพื่อชี้แจงเรื่อง 'Emergency mobilization fee' จำนวน 20,000 บาท ที่ไม่อยู่ในขอบเขต PO และขอใบเปลี่ยนคำสั่งซื้อ (Change Order) หากจำเป็น 2. แก้ไขเงื่อนไขการชำระเงินในใบแจ้งหนี้จาก 15 วัน เป็น 30 วัน ตามสัญญา 3. หักค่าปรับล่าช้า (Liquidated Damages) จำนวน 10,000 บาท ออกจากยอดจ่ายสุทธิ 4. ออกใบแจ้งหนี้แก้ไข (Credit Note/Debit Note) ก่อนดำเนินการจ่ายเงิน",
      "discrepancies": [
        {
          "type": "EXTRA_CHARGE",
          "severity": "warning",
          "title": "พบรายการค่าใช้จ่ายเกินวงเงินอนุมัติ",
          "detail": "พบรายการ 'Emergency mobilization fee' จำนวน 20,000.00 บาท ซึ่งไม่ปรากฏในขอบเขตงานหรือวงเงินอนุมัติของ PO-2026-089 (วงเงินคงเหลือ 0 บาท)",
          "impact": "การจ่ายยอดนี้โดยไม่มีการอนุมัติเพิ่มเติมถือว่าผิดระเบียบจัดซื้อ อาจทำให้ยอดรวมเกินงบประมาณโครงการ"
        },
        {
          "type": "AMOUNT_MISMATCH",
          "severity": "warning",
          "title": "ยอดเงินในใบแจ้งหนี้เกินวงเงิน PO",
          "detail": "ยอดรวมก่อน VAT ในใบแจ้งหนี้คือ 1,020,000.00 บาท แต่วงเงินอนุมัติใน PO คือ 1,000,000.00 บาท (เกิน 20,000.00 บาท หรือ 2%)",
          "impact": "ระบบการเงินอาจปฏิเสธการเบิกจ่ายเนื่องจากยอดเกินวงเงินควบคุม (Budget Control Exceeded)"
        },
        {
          "type": "CREDIT_TERM_MISMATCH",
          "severity": "info",
          "title": "เงื่อนไขการชำระเงินไม่ตรงตามสัญญา",
          "detail": "ใบแจ้งหนี้ระบุเงื่อนไขการชำระเงินเป็น 15 วัน ในขณะที่ PO และสัญญาระบุไว้ที่ 30 วัน",
          "impact": "หากชำระตามบิลจะสูญเสียสภาพคล่องและผิดเงื่อนไขสัญญาที่ตกลงไว้ ควรแก้ไขเป็น 30 วัน"
        },
        {
          "type": "DELAY_PENALTY",
          "severity": "critical",
          "title": "ตรวจพบค่าปรับส่งมอบงานล่าช้าที่ยังไม่ได้หัก",
          "detail": "งานส่งมอบล่าช้า 10 วัน (เกินเกณฑ์ 7 วัน) ต้องถูกหักค่าปรับ 0.1% ต่อวัน รวมเป็น 1.0% หรือ 10,000.00 บาท แต่ใบแจ้งหนี้ไม่ได้ทำการหักจำนวนนี้",
          "impact": "องค์กรจะเสียหายทางการเงินหากจ่ายเต็มจำนวนโดยไม่หักค่าปรับตามสัญญา (Liquidated Damages)"
        }
      ],
      "comparison": {
        "vendor_name": {
          "po": "บริษัท กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส จำกัด",
          "doc": "KangHan Engineering & Service Co., Ltd.",
          "match": true
        },
        "tax_id": {
          "po": "0105556098711",
          "doc": "0105556098711",
          "match": true
        },
        "bank_account": {
          "po": "ธนาคารกสิกรไทย 045-2-12345-6",
          "doc": "Kasikorn 045-2-12345-6",
          "match": true
        },
        "amount": {
          "po": "1,000,000.00 บาท",
          "doc": "1,020,000.00 บาท",
          "match": false
        },
        "credit_terms": {
          "po": "30 วัน",
          "doc": "15 วัน",
          "match": false
        },
        "delivery_sla": {
          "po": "ส่งมอบภายในกำหนด",
          "doc": "ล่าช้า 10 วัน",
          "match": false
        }
      },
      "financial_summary": {
        "po_approved_amount": 1000000.0,
        "invoice_billed_subtotal": 1020000.0,
        "extra_unapproved_amount": 20000.0,
        "delay_penalty_amount": 10000.0,
        "overbilled_amount": 20000.0,
        "partial_short_amount": 0.0,
        "retention_deduct_amount": 0.0,
        "math_error_amount": 0.0,
        "net_payable_subtotal": 1010000.0,
        "vat_7_pct": 70700.0,
        "total_due_payable": 1080700.0
      },
      "email_summary": "เรียน ฝ่ายจัดซื้อและบริษัท กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส จำกัด,\n\nผลการตรวจสอบใบแจ้งหนี้เลขที่อ้างอิง PO-2026-089 พบข้อขัดข้องดังนี้:\n1. มียอดเรียกเก็บเกิน (Emergency fee) 20,000 บาท ซึ่งไม่อยู่ในขอบเขต PO\n2. เงื่อนไขการชำระเงินระบุ 15 วัน ไม่ตรงตามสัญญา (30 วัน)\n3. ไม่ได้หักค่าปรับล่าช้า (Delay Penalty) จำนวน 10,000 บาท จากการส่งมอบงานล่าช้า 10 วัน\n\nจึงใคร่ขอให้ท่านออกใบแจ้งหนี้แก้ไข (Revised Invoice) โดยตัดรายการที่ไม่ได้รับอนุมัติ แก้ไขเครดิตเทอมเป็น 30 วัน และหักค่าปรับล่าช้าก่อนดำเนินการชำระเงิน ยอดสุทธิที่ถูกต้องควรเป็น 1,080,700.00 บาท (รวม VAT หลังหักค่าปรับ)\n\nขอแสดงความนับถือ,\nฝ่ายตรวจสอบบัญชีและจัดซื้อ"
    },
    "audit_engine": "OpenAI-Compatible LLM (Qwen/Qwen3.5-397B-A17B-non_thinking)",
    "created_at": "2026-09-12 16:53:05"
  },
  "PO-2026-094": {
    "cache_key": "71b8d7383c80ebf0dea78d15c33e2af2fcd95b4a5090558350de76270f5ec31a",
    "po_number": "PO-2026-094",
    "audit": {
      "status": "FRAUD_ALERT",
      "status_label": "🔴 FRAUD ALERT (พบการสวมสิทธิ์คู่ค้าและข้อมูลบัญชีไม่ตรงกัน)",
      "action_recommendation": "ระงับการชำระเงินทันที แจ้งเตือนฝ่ายจัดซื้อและกฎหมาย ตรวจสอบกรณีใบแจ้งหนี้ปลอมหรือการสวมสิทธิ์คู่ค้า (Vendor Impersonation) เนื่องจากชื่อบริษัท เลขผู้เสียภาษี และบัญชีธนาคารในใบแจ้งหนี้ไม่ตรงกับข้อมูลในระบบ PO-2026-094 เลย",
      "discrepancies": [
        {
          "type": "FRAUD_VENDOR_MISMATCH",
          "severity": "critical",
          "title": "ชื่อบริษัทคู่ค้าไม่ตรงกัน (เสี่ยงสวมสิทธิ์)",
          "detail": "ในระบบระบุ 'บริษัท เอเชีย เมกา คอนสตรัคชั่น จำกัด' แต่ในใบแจ้งหนี้ระบุ 'Premier Valve & Pipe Co., Ltd.' ซึ่งเป็นคนละบริษัทกันโดยสิ้นเชิง",
          "impact": "ความเสี่ยงสูงมากที่เป็นการออกใบแจ้งหนี้ปลอมเพื่อเบี่ยงเบนเงิน หรือความผิดพลาดร้ายแรงในการออกเอกสาร"
        },
        {
          "type": "FRAUD_TAX_MISMATCH",
          "severity": "critical",
          "title": "เลขประจำตัวผู้เสียภาษีไม่ตรงกัน",
          "detail": "ในระบบ: 0105547089112 vs ในใบแจ้งหนี้: 0105539077123",
          "impact": "ยืนยันว่าไม่ใช่คู่ค้ารายเดิม เสี่ยงต่อการทุจริตทางภาษีและการจ่ายเงินผิดบุคคล"
        },
        {
          "type": "FRAUD_BANK_MISMATCH",
          "severity": "critical",
          "title": "ข้อมูลธนาคารและเลขบัญชีไม่ตรงกัน",
          "detail": "ในระบบ: SCB 049-2-33445-5 vs ในใบแจ้งหนี้: KTB 015-1-66554-3",
          "impact": "เสี่ยงต่อการถูกโจรกรรมเงินเข้าสู่บัญชีม้า หากทำการโอนเงินตามใบแจ้งหนี้นี้"
        },
        {
          "type": "INVOICE_MATH_ERROR",
          "severity": "critical",
          "title": "ยอดรวมในใบแจ้งหนี้คำนวณผิดพลาด",
          "detail": "ผลรวมรายการจริงคือ 500,000.00 บาท (200k+180k+120k) แต่ใบแจ้งหนี้ระบุ Subtotal 550,000.00 บาท (เกินมา 50,000.00 บาท)",
          "impact": "ความน่าเชื่อถือของเอกสารต่ำมาก และทำให้ยอด VAT และยอดรวมสุดท้ายผิดพลาดตามไปด้วย"
        },
        {
          "type": "MISSING_RETENTION",
          "severity": "warning",
          "title": "ไม่มีการหักเงินค้ำประกันผลงาน (Retention)",
          "detail": "ตามสัญญาต้องหัก 5% (150,000.00 บาท) จากยอด 3,000,000.00 บาท เหลือจ่ายจริง 2,850,000.00 บาท แต่ใบแจ้งหนี้ไม่ได้ทำการหักดังกล่าว",
          "impact": "หากจ่ายเงินเต็มจำนวน จะสูญเสียสิทธิในการยึดเงินประกันกรณีงานมีข้อบกพร่องในช่วง 12 เดือน"
        },
        {
          "type": "PO_REFERENCE_MISMATCH",
          "severity": "critical",
          "title": "เลขที่ PO ในใบแจ้งหนี้ไม่ตรงกับเอกสารแนบ",
          "detail": "ใบแจ้งหนี้อ้างอิง PO-2026-096 แต่เอกสารระบบและใบตรวจรับเป็นของ PO-2026-094",
          "impact": "เอกสารไม่สอดคล้องกัน ไม่สามารถนำมาจับคู่เบิกจ่ายได้"
        }
      ],
      "comparison": {
        "vendor_name": {
          "po": "บริษัท เอเชีย เมกา คอนสตรัคชั่น จำกัด",
          "doc": "Premier Valve & Pipe Co., Ltd.",
          "match": false
        },
        "tax_id": {
          "po": "0105547089112",
          "doc": "0105539077123",
          "match": false
        },
        "bank_account": {
          "po": "ธนาคารไทยพาณิชย์ 049-2-33445-5",
          "doc": "KTB 015-1-66554-3",
          "match": false
        },
        "amount": {
          "po": "3,000,000.00 บาท",
          "doc": "550,000.00 บาท (คำนวณผิด)",
          "match": false
        },
        "credit_terms": {
          "po": "30 วัน",
          "doc": "30 Days",
          "match": true
        },
        "delivery_sla": {
          "po": "งวดสุดท้าย (100%)",
          "doc": "ไม่ระบุสถานะชัดเจนในบิล (แต่ระบุ PO คนละฉบับ)",
          "match": false
        }
      },
      "financial_summary": {
        "po_approved_amount": 3000000.0,
        "invoice_billed_subtotal": 550000.0,
        "extra_unapproved_amount": 50000.0,
        "delay_penalty_amount": 0.0,
        "overbilled_amount": 50000.0,
        "partial_short_amount": 0.0,
        "retention_deduct_amount": 150000.0,
        "math_error_amount": 50000.0,
        "net_payable_subtotal": 3000000.0,
        "vat_7_pct": 210000.00000000003,
        "total_due_payable": 3210000.0
      },
      "email_summary": "เรียน ฝ่ายจัดซื้อและผู้จัดการโครงการ,\n\nผลการตรวจสอบใบแจ้งหนี้สำหรับ PO-2026-094 พบสถานะ FRAUD ALERT อย่างร้ายแรง ดังนี้:\n1. ข้อมูลคู่ค้าไม่ตรงกันทั้งชื่อบริษัท เลขผู้เสียภาษี และบัญชีธนาคาร (ระบบ: เอเชีย เมกาฯ vs บิล: Premier Valveฯ)\n2. เลขที่ PO ในใบแจ้งหนี้ (PO-2026-096) ไม่ตรงกับเอกสารโครงการ (PO-2026-094)\n3. พบข้อผิดพลาดในการคำนวณยอดเงิน (เกินมา 50,000 บาท)\n4. ไม่มีการหักเงินค้ำประกันผลงาน 5% ตามสัญญา\n\nคำแนะนำ: ห้ามดำเนินการชำระเงินเด็ดขาด ให้ส่งเรื่องให้ฝ่ายตรวจสอบภายในและกฎหมายดำเนินการสืบสวนแหล่งที่มาของใบแจ้งหนี้นี้ทันที และติดต่อคู่ค้าจริง (Asia Mega Construction) เพื่อยืนยันความถูกต้อง\n\nเรียนมาเพื่อโปรดดำเนินการ,\nระบบตรวจสอบเอกสารอัตโนมัติ (Procurement Auditor AI)"
    },
    "audit_engine": "OpenAI-Compatible LLM (Qwen/Qwen3.5-397B-A17B-non_thinking)",
    "created_at": "2026-09-12 17:00:51"
  }
};
let HISTORY_DATA = [
  {
    "cache_key": "00fbf6ee947aed8bbb8d150e69761f818455ba2598db2c270a2679ab45ed25f4",
    "po_number": "PO-TEST",
    "vendor_name": "ไม่ระบุ",
    "project_site": "ไม่ระบุ",
    "approved_amount": null,
    "status": "APPROVED",
    "status_label": "",
    "findings_count": 0,
    "final_payable_amount": null,
    "action_recommendation": "",
    "audit_engine": "Test Engine",
    "created_at": "2026-09-12 16:49:02"
  },
  {
    "cache_key": "742c510f26ebbc5d542fba6c30dfab31fb3c1843c1ada3e2369f7476be9ba1cd",
    "po_number": "PO-2026-089",
    "vendor_name": "บริษัท กังหัน เอ็นจิเนียริ่ง แอนด์ เซอร์วิส จำกัด",
    "project_site": "G.Brimm Power",
    "approved_amount": 1000000.0,
    "status": "HOLD_PAYMENT",
    "status_label": "🟡 HOLD PAYMENT (พบความคลาดเคลื่อนวงเงิน, เงื่อนไขการชำระเงิน, และค่าปรับล่าช้า)",
    "findings_count": 4,
    "final_payable_amount": null,
    "action_recommendation": "ระงับการชำระเงินทันที 1. ติดต่อผู้ขายเพื่อชี้แจงเรื่อง 'Emergency mobilization fee' จำนวน 20,000 บาท ที่ไม่อยู่ในขอบเขต PO และขอใบเปลี่ยนคำสั่งซื้อ (Change Order) หากจำเป็น 2. แก้ไขเงื่อนไขการชำระเงินในใบแจ้งหนี้จาก 15 วัน เป็น 30 วัน ตามสัญญา 3. หักค่าปรับล่าช้า (Liquidated Damages) จำนวน 10,000 บาท ออกจากยอดจ่ายสุทธิ 4. ออกใบแจ้งหนี้แก้ไข (Credit Note/Debit Note) ก่อนดำเนินการจ่ายเงิน",
    "audit_engine": "OpenAI-Compatible LLM (Qwen/Qwen3.5-397B-A17B-non_thinking)",
    "created_at": "2026-09-12 16:53:05"
  },
  {
    "cache_key": "a2dba2a0ada87382845c27c11f25fa468ce16557c99ddf4c6f9a160f5ed60170",
    "po_number": "PO-2026-094",
    "vendor_name": "บริษัท เอเชีย เมกา คอนสตรัคชั่น จำกัด",
    "project_site": "Laem Chabang Floating Solar",
    "approved_amount": 3000000.0,
    "status": "WARNING",
    "status_label": "🟡 WARNING (ตรวจพบข้อผิดพลาดการคำนวณเงินค้ำประกันผลงาน)",
    "findings_count": 1,
    "final_payable_amount": null,
    "action_recommendation": "อนุมัติการจ่ายเงินเฉพาะยอดสุทธิหลังหักเงินค้ำประกัน (2,850,000.00 บาท + VAT) เท่านั้น ห้ามจ่ายตามยอดรวมในใบแจ้งหนี้ ให้ส่งคืนเอกสารให้คู่ค้าแก้ไขหรือทำการปรับลดยอดจ่ายในระบบบัญชีทันทีตามเงื่อนไขสัญญาข้อ 5.1",
    "audit_engine": "OpenAI-Compatible LLM (Qwen/Qwen3.5-397B-A17B-non_thinking)",
    "created_at": "2026-09-12 17:00:08"
  },
  {
    "cache_key": "71b8d7383c80ebf0dea78d15c33e2af2fcd95b4a5090558350de76270f5ec31a",
    "po_number": "PO-2026-094",
    "vendor_name": "บริษัท เอเชีย เมกา คอนสตรัคชั่น จำกัด",
    "project_site": "Laem Chabang Floating Solar",
    "approved_amount": 3000000.0,
    "status": "FRAUD_ALERT",
    "status_label": "🔴 FRAUD ALERT (พบการสวมสิทธิ์คู่ค้าและข้อมูลบัญชีไม่ตรงกัน)",
    "findings_count": 6,
    "final_payable_amount": null,
    "action_recommendation": "ระงับการชำระเงินทันที แจ้งเตือนฝ่ายจัดซื้อและกฎหมาย ตรวจสอบกรณีใบแจ้งหนี้ปลอมหรือการสวมสิทธิ์คู่ค้า (Vendor Impersonation) เนื่องจากชื่อบริษัท เลขผู้เสียภาษี และบัญชีธนาคารในใบแจ้งหนี้ไม่ตรงกับข้อมูลในระบบ PO-2026-094 เลย",
    "audit_engine": "OpenAI-Compatible LLM (Qwen/Qwen3.5-397B-A17B-non_thinking)",
    "created_at": "2026-09-12 17:00:51"
  }
];

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS Headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // 1. Serve HTML Web UI
    if (path === '/' || path === '/index.html') {
      return new Response(HTML_CONTENT, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Cache-Control': 'no-cache',
          ...corsHeaders
        }
      });
    }

    // 2. API: Get all POs
    if (path === '/api/pos') {
      return new Response(JSON.stringify({ success: true, pos: PO_DATA }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // 3. API: Get PO Detail
    if (path.startsWith('/api/pos/')) {
      const poNo = decodeURIComponent(path.replace('/api/pos/', ''));
      const po = PO_DATA.find(p => p.po_number === poNo);
      if (po) {
        return new Response(JSON.stringify({ success: true, po }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
      return new Response(JSON.stringify({ error: 'PO not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // 4. API: Run Audit
    if (path === '/api/audit' && request.method === 'POST') {
      let poNumber = '';
      try {
        const formData = await request.formData();
        poNumber = formData.get('po_number') || 'PO-2026-089';
      } catch (e) {
        poNumber = 'PO-2026-089';
      }

      const po = PO_DATA.find(p => p.po_number === poNumber) || PO_DATA[0];
      const record = AUDIT_RECORDS[poNumber] || Object.values(AUDIT_RECORDS)[0];

      return new Response(JSON.stringify({
        success: true,
        po_data: po,
        audit: record ? record.audit : {
          status: 'APPROVED',
          status_label: '🟢 APPROVED (อนุมัติจ่ายเงินได้)',
          action_recommendation: 'เอกสารและตัวเลขถูกต้องครบถ้วน',
          discrepancies: []
        },
        audit_engine: record ? record.audit_engine + ' [⚡ Cloudflare Demo Engine]' : 'Built-in Demo Engine',
        cached: true,
        cached_at: new Date().toISOString()
      }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // 5. API: Get Audit History
    if (path === '/api/history') {
      if (request.method === 'DELETE') {
        HISTORY_DATA = [];
        return new Response(JSON.stringify({ success: true, message: 'Cleared' }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
      return new Response(JSON.stringify({ success: true, history: HISTORY_DATA, total: HISTORY_DATA.length }), {
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // 6. API: Get History Detail
    if (path.startsWith('/api/history/')) {
      const key = path.replace('/api/history/', '');
      if (request.method === 'DELETE') {
        HISTORY_DATA = HISTORY_DATA.filter(h => h.cache_key !== key);
        return new Response(JSON.stringify({ success: true }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
      const hist = HISTORY_DATA.find(h => h.cache_key === key);
      const record = hist ? AUDIT_RECORDS[hist.po_number] : null;
      if (record) {
        const po = PO_DATA.find(p => p.po_number === hist.po_number);
        return new Response(JSON.stringify({
          success: true,
          cache_key: key,
          po_number: hist.po_number,
          po_data: po,
          audit: record.audit,
          audit_engine: record.audit_engine,
          created_at: hist.created_at
        }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }
      return new Response(JSON.stringify({ error: 'History not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders }
      });
    }

    // Default 404
    return new Response('Not Found', { status: 404, headers: corsHeaders });
  }
};

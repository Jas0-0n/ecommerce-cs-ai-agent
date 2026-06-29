# 🛒 電商客服 AI Agent

> 一個整合 FAQ 知識庫問答與客訴處理的 AI 客服助手，可作為電商網站、LINE/Telegram Bot 的後端引擎。

---

## 📋 專案簡介

本專案實作了一個**領域特定（Domain-Specific）的 AI Agent**，專注於電商客服場景。系統能夠：

- 📖 **自動回答 FAQ**：透過 RAG（檢索增強生成）從知識庫中查找官方回答
- ⚠️ **智慧處理客訴**：情緒分析 → 分級判定 → 自動回覆或轉接人工
- 🔀 **智能分流**：自動判斷用戶輸入屬於 FAQ、客訴、還是需要轉接人工
- 🔌 **多渠道支援**：內建 CLI、FastAPI、LINE Bot、Telegram Bot 整合

專案從零手寫，不依賴 LangChain / AutoGen 等框架，便於理解和客製化。

---

## 🧱 Tech Stack

| 元件 | 技術 | 說明 |
|------|------|------|
| **語言** | Python 3.11+ | |
| **LLM SDK** | OpenAI SDK | 支援任何 OpenAI-compatible API（含 Ollama / DeepSeek / vLLM） |
| **向量資料庫** | ChromaDB | 本地持久化儲存，無需額外服務 |
| **Embedding** | sentence-transformers | `all-MiniLM-L6-v2` 模型 |
| **API 層** | FastAPI | RESTful API，自動生成 Swagger 文檔 |
| **CLI** | Rich | 彩色互動式命令列介面 |
| **測試** | pytest + pytest-asyncio | 22 個測試案例，含 Mock 模式 |

---

## 🔄 Workflow

![系統架構圖](https://excalidraw.com/#json=yidd-zmd1iQ1kjbfbmFTt,O60o5HpEWLt4AradRAPdkw)

> 📌 點擊上方 Excalidraw 圖示可放大/編輯流程圖

### 流程說明

```
使用者輸入
    │
    ▼
┌──────────────────────┐
│  ① Dispatcher 分流    │  ← 用 LLM 判斷意圖 + 情緒分析雙重確認
│  (FAQ / 客訴 / 人工)   │
└──────┬───────┬───────┘
       │       │
       ▼       ▼
┌─────────┐ ┌───────────┐
│ FAQ     │ │ 客訴處理   │
│ Agent   │ │ Agent     │
│  │      │ │  │        │
│  ▼      │ │  ▼        │
│ RAG 查詢 │ │ 情緒分析   │
│ 知識庫   │ │ 分級判定   │
│         │ │ 升級判斷   │
└────┬────┘ └──┬───┬────┘
     │         │   │
     │    ⚠️ 升級│   ✅ 自動回覆
     │         │   │
     ▼         ▼   ▼
┌──────────────────────┐
│  ② Response 輸出      │
│  - FAQ 回答            │
│  - 客訴回覆 + 案件編號  │
│  - 轉接人工通知         │
└──────────────────────┘
```

---

## 🚀 安裝步驟

### 前置需求

- Python 3.11+
- pip

### 安裝

```bash
# 1. 克隆專案
git clone https://github.com/Jas0-0n/ecommerce-cs-ai-agent.git
cd ecommerce-cs-ai-agent

# 2. 建立虛擬環境（可選但建議）
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定 LLM API Key（可選，沒設會自動進入 Fake Mode）
echo 'LLM_API_KEY=your-api-key-here' > .env
# 如果使用 proxy（例如台灣地區）：
echo 'LLM_BASE_URL=https://your-proxy-url/v1' >> .env

# 5. 匯入 FAQ 知識庫
python scripts/ingest_kb.py
```

---

## 🎮 操作步驟

### 選項 A：CLI 互動模式（推薦快速測試）

```bash
python cli.py
```

然後輸入問題測試：

```
🛒 電商客服 AI Agent

顧客: 退貨需要什麼條件？
┌──────────────┐
│ 📖 FAQ 問答   │
└──────────────┘
**AI:** 收到商品 7 天鑑賞期內，保持商品全新未拆封...

顧客: 你們送貨太慢了，我等了五天了！
┌──────────────┐
│ ⚠️ 客訴處理   │
└──────────────┘
**AI回覆:** 很抱歉讓您有這樣的體驗...
案件編號: CASE-A1B2C3D4

顧客: 叫你們主管出來
┌──────────────┐
│ 👤 轉接人工   │
└──────────────┘
我將為您轉接人工客服專員，請稍候...

顧客: quit   ← 離開
```

### 選項 B：API 模式

```bash
python main.py
# 訪問 http://localhost:8000/docs 查看 Swagger API 文檔
```

```bash
# 測試 API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "如何查詢訂單狀態？"}'
```

### 選項 C：Fake Mode（無 API Key 開發）

系統會自動偵測 `.env` 中有無有效的 API Key。若無效，自動啟用 **Fake Mode**：

- Dispatcher 根據關鍵字規則分流
- Sentiment 根據關鍵字給分數
- LLM 回覆以模擬文字替代

Fake Mode 下所有流程（分流 → 情緒分析 → 升級判斷 → 回覆）都能正常運作，適合開發和展示。

---

## ✅ 最終成果

### 測試驗證

```bash
python -m pytest tests/ -v
```

```
22 passed in 19.56s
```

| 測試類別 | 數量 | 說明 |
|----------|------|------|
| Unit Tests | 5 | Message、ToolDef、split_markdown 等 |
| Integration Tests | 5 | LLM client、Sentiment、Knowledge Base |
| Agent Tests | 4 | FAQ Agent、Complaint Agent（含 escalate） |
| Dispatcher Tests | 3 | FAQ/客訴/人工 分流 |
| API Tests | 3 | FastAPI health + chat endpoints |
| E2E Tests | 7 | 完整流程（訂單查詢、退貨政策、客訴等） |

### 知識庫內容

| 文件 | 段落數 | 主題 |
|------|--------|------|
| `faq_orders.md` | 4 | 訂單查詢、修改、合併、未到貨 |
| `faq_shipping.md` | 4 | 配送方式、運費、離島 |
| `faq_returns.md` | 4 | 退換貨政策、退貨流程、退款 |
| `faq_payment.md` | 4 | 付款方式、分期、發票 |
| `policy_complaint.md` | 3 | 客訴處理時效、渠道、升級 |
| `faq_jd_aftersales.md` | 8 | 京東售後（取件費、總則、7天退貨、發錯貨等） |
| **合計** | **27** | |

### 專案結構

```
ecommerce-agent/
├── cli.py                    # 互動式 CLI 測試
├── main.py                   # FastAPI 入口
├── requirements.txt
├── .env.example
├── assets/
│   └── architecture.excalidraw
├── scripts/
│   ├── setup.py              # 一鍵初始化
│   └── ingest_kb.py          # 知識庫匯入腳本
├── data/
│   ├── knowledge/            # 知識文件（Markdown）
│   └── chroma_db/            # 自動生成（向量庫）
├── src/
│   ├── config.py             # 設定管理（Pydantic）
│   ├── llm_client.py         # LLM 客戶端（含 Fake Mode）
│   ├── knowledge_base.py     # RAG 知識庫（ChromaDB）
│   ├── sentiment.py          # 情緒分析模組
│   ├── tools.py              # 工具定義（search_faq）
│   ├── agent.py              # FAQ Agent + Complain Agent
│   ├── complaint_prompts.py  # 客訴提示詞
│   ├── complaint_workflow.py # 客訴工作流
│   ├── dispatcher.py         # 主調度器（分流）
│   ├── models.py             # Pydantic schemas
│   ├── api.py                # FastAPI 服務
│   ├── monitoring.py         # 日誌與監控
│   ├── bot_line.py           # LINE Bot 整合（選用）
│   └── bot_telegram.py       # Telegram Bot 整合（選用）
└── tests/
    ├── test_llm_client.py
    ├── test_knowledge_base.py
    ├── test_sentiment.py
    ├── test_agent_faq.py
    ├── test_complaint_agent.py
    ├── test_dispatcher.py
    ├── test_api.py
    └── test_e2e.py
```

---

## 📝 License

MIT

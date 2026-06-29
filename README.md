# 🛒 E-commerce Customer Service AI Agent

> An AI customer service assistant integrating FAQ knowledge base Q&A and complaint handling, usable as a backend engine for e-commerce websites, LINE/Telegram Bots.

---

## 📋 Project Overview

This project implements a **Domain-Specific AI Agent** focused on e-commerce customer service scenarios. The system can:

- 📖 **Auto-answer FAQs**: Uses RAG (Retrieval-Augmented Generation) to find official answers from the knowledge base
- ⚠️ **Smart Complaint Handling**: Sentiment analysis → Triage → Auto-reply or transfer to human
- 🔀 **Intelligent Routing**: Automatically determines whether user input is FAQ, complaint, or needs human transfer
- 🔌 **Multi-Channel Support**: Built-in CLI, FastAPI, LINE Bot, Telegram Bot integration

The project is written from scratch without relying on LangChain / AutoGen frameworks, making it easy to understand and customize.

---

## 🧱 Tech Stack

| Component | Technology | Description |
|-----------|-----------|-------------|
| **Language** | Python 3.11+ | |
| **LLM SDK** | OpenAI SDK | Supports any OpenAI-compatible API (including Ollama / DeepSeek / vLLM) |
| **Vector DB** | ChromaDB | Local persistent storage, no additional services needed |
| **Embedding** | sentence-transformers | `all-MiniLM-L6-v2` model |
| **API Layer** | FastAPI | RESTful API with auto-generated Swagger docs |
| **CLI** | Rich | Colored interactive command-line interface |
| **Testing** | pytest + pytest-asyncio | 22 test cases, including Mock mode |

---

## 🔄 Workflow

![System Architecture](assets/workflow.svg)

> 📌 System flow: User Input → Dispatcher Routing → FAQ Agent or Complaint Agent → Response to User

### Process Flow

```
User Input
    │
    ▼
┌──────────────────────┐
│  ① Dispatcher         │  ← Intent classification by LLM + Sentiment double-check
│  (FAQ / Complaint /   │
│   Human Transfer)     │
└──────┬───────┬───────┘
       │       │
       ▼       ▼
┌─────────┐ ┌───────────┐
│ FAQ     │ │ Complaint │
│ Agent   │ │ Agent     │
│  │      │ │  │        │
│  ▼      │ │  ▼        │
│ RAG     │ │ Sentiment │
│ Search  │ │ Triage    │
│ KB      │ │ Escalate? │
└────┬────┘ └──┬───┬────┘
     │         │   │
     │    ⚠️ Yes│   ✅ Auto
     │         │   Reply
     ▼         ▼   ▼
┌──────────────────────┐
│  ② Response Output    │
│  - FAQ Answer          │
│  - Complaint Reply + Case ID │
│  - Human Transfer Notice     │
└──────────────────────┘
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# 1. Clone the project
git clone https://github.com/Jas0-0n/ecommerce-cs-ai-agent.git
cd ecommerce-cs-ai-agent

# 2. Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set LLM API Key (optional, enters Fake Mode automatically if not set)
echo 'LLM_API_KEY=your-api-key-here' > .env
# If using a proxy (e.g., in restricted regions):
echo 'LLM_BASE_URL=https://your-proxy-url/v1' >> .env

# 5. Import FAQ knowledge base
python scripts/ingest_kb.py
```

---

## 🎮 Usage

### Option A: CLI Interactive Mode (Recommended for quick testing)

```bash
python cli.py
```

Then enter questions to test:

```
🛒 E-commerce CS AI Agent

Customer: What are the conditions for returns?
┌──────────────┐
│ 📖 FAQ       │
└──────────────┘
**AI:** Within 7 days of receiving the item, keep it brand new and unopened...

Customer: Your delivery is too slow, I've been waiting five days!
┌──────────────┐
│ ⚠️ Complaint │
└──────────────┘
**AI Reply:** We apologize for your experience...
Case ID: CASE-A1B2C3D4

Customer: Let me speak to your manager
┌──────────────┐
│ 👤 Human     │
└──────────────┘
I will transfer you to a human agent, please wait...

Customer: quit   ← Exit
```

### Option B: API Mode

```bash
python main.py
# Visit http://localhost:8000/docs to see Swagger API docs
```

```bash
# Test API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I check my order status?"}'
```

### Option C: Fake Mode (Development without API Key)

The system automatically detects whether a valid API Key exists in `.env`. If invalid, it automatically activates **Fake Mode**:

- Dispatcher routes based on keyword rules
- Sentiment scoring based on keywords
- LLM responses replaced with simulated text

All processes (routing → sentiment analysis → escalation decision → response) work normally in Fake Mode, making it suitable for development and demos.

---

## ✅ Results

### Test Verification

```bash
python -m pytest tests/ -v
```

```
22 passed in 19.56s
```

| Test Category | Count | Description |
|--------------|-------|-------------|
| Unit Tests | 5 | Message, ToolDef, split_markdown, etc. |
| Integration Tests | 5 | LLM client, Sentiment, Knowledge Base |
| Agent Tests | 4 | FAQ Agent, Complaint Agent (incl. escalate) |
| Dispatcher Tests | 3 | FAQ/Complaint/Human routing |
| API Tests | 3 | FastAPI health + chat endpoints |
| E2E Tests | 7 | Full flow (order inquiry, return policy, complaints, etc.) |

### Knowledge Base Contents

| File | Paragraphs | Topic |
|------|-----------|-------|
| `faq_orders.md` | 4 | Order inquiry, modification, combining, non-delivery |
| `faq_shipping.md` | 4 | Shipping methods, fees, outlying islands |
| `faq_returns.md` | 4 | Return/exchange policy, process, refunds |
| `faq_payment.md` | 4 | Payment methods, installments, invoices |
| `policy_complaint.md` | 3 | Complaint handling timeline, channels, escalation |
| `faq_jd_aftersales.md` | 8 | JD.com after-sales (pickup fees, policy, 7-day returns, wrong items, etc.) |
| **Total** | **27** | |

### Project Structure

```
ecommerce-agent/
├── cli.py                    # Interactive CLI test
├── main.py                   # FastAPI entry point
├── requirements.txt
├── .env.example
├── assets/
│   └── architecture.excalidraw
├── scripts/
│   ├── setup.py              # One-click initialization
│   └── ingest_kb.py          # Knowledge base import script
├── data/
│   ├── knowledge/            # Knowledge documents (Markdown)
│   └── chroma_db/            # Auto-generated (vector store)
├── src/
│   ├── config.py             # Settings management (Pydantic)
│   ├── llm_client.py         # LLM client (incl. Fake Mode)
│   ├── knowledge_base.py     # RAG knowledge base (ChromaDB)
│   ├── sentiment.py          # Sentiment analysis module
│   ├── tools.py              # Tool definitions (search_faq)
│   ├── agent.py              # FAQ Agent + Complaint Agent
│   ├── complaint_prompts.py  # Complaint prompts
│   ├── complaint_workflow.py # Complaint workflow
│   ├── dispatcher.py         # Main dispatcher (routing)
│   ├── models.py             # Pydantic schemas
│   ├── api.py                # FastAPI service
│   ├── monitoring.py         # Logging and monitoring
│   ├── bot_line.py           # LINE Bot integration (optional)
│   └── bot_telegram.py       # Telegram Bot integration (optional)
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

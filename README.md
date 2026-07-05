# 🤖 Weekend AI Agents

A collection of production-minded, multi-agent AI systems built over weekends — each one exploring a different real-world use case: content generation, self-improving document extraction, and agentic RAG.

All agents are built on **Google Gemini**, use **CrewAI / LangGraph** for orchestration, and ship with the things that make agents actually usable in production: input/output **guardrails**, **observability** (Langfuse), versioned **prompts**, and **memory**.

---

## 📦 What's Inside

| Agent | What it does | Stack |
|-------|--------------|-------|
| [🖊️ LinkedIn Post Generator](#-linkedin-post-generator) | Multi-agent pipeline that researches a topic and writes a human-sounding LinkedIn post | CrewAI · Gemini · Tavily · Langfuse |
| [🔁 Self-Reflection Extractor](#-self-reflection-document-extractor) | Extracts structured data from paystub PDFs and *learns from its own mistakes* across runs | CrewAI · Gemini · PyPDF2 |
| [📚 Agentic RAG](#-agentic-rag-work-in-progress) | Retrieval-augmented agent with memory, self-critique, and a vector store | LangGraph · Gemini · FAISS · FastEmbed |

---

## 🖊️ LinkedIn Post Generator

A three-agent CrewAI pipeline that turns a topic into a polished, on-brand LinkedIn post.

**How it works — three specialists hand off to each other:**

1. **Research Agent** — surfaces credible, recent facts and the single most compelling hook (via Tavily web search).
2. **Writer Agent** — turns the research brief into a post that reads like a real person wrote it (no "in today's fast-paced world").
3. **Validator Agent** — fact-checks every claim against the research and flags any "AI tell" before the post ships.

**Features**
- 🎯 Configurable **tone** (`professional`, `casual`, `thought-leader`) and **post type** (`story`, `hot-take`, `announcement`, `lesson-learned`)
- 🛡️ Input & output **guardrails** ([guardrails.py](linkedin_generator_agent/guardrails.py))
- 🗂️ **Versioned prompts** so you can iterate without touching code ([prompts/](linkedin_generator_agent/prompts/))
- 📊 Optional **Langfuse** tracing
- 🔁 Retry logic with structured JSON parsing ([utils.py](linkedin_generator_agent/utils.py))

**Run it**
```bash
cd linkedin_generator_agent
pip install -r requirements.txt
python linkedin_agent.py
```

---

## 🔁 Self-Reflection Document Extractor

A CrewAI agent that extracts structured fields from **paystub PDFs** — and gets better over time by remembering its own corrections.

**How it works — an extract → validate → reflect loop:**

1. **Extraction Agent** — pulls structured JSON (employee name, pay period, gross/net pay, deductions, YTD…) from the PDF.
2. **Validation Agent** — checks the extraction for errors and inconsistencies.
3. **Reflection Agent** — when something goes wrong, it writes a **correction rule** to persistent memory (`memory.json`), which is fed back into future extractions.

The result: the agent accumulates learnings across runs instead of repeating the same mistakes.

**Run it**
```bash
cd "self reflection"
pip install -r requirements.txt
python self_reflection.py   # processes file.pdf by default
```

---

## 📚 Agentic RAG *(work in progress)*

A production-oriented agentic RAG system, currently being built out. See [RAG_AGENT_CODE/info.txt](RAG_AGENT_CODE/info.txt) for the planned architecture.

**Design**
- 🧠 **LangGraph** agent for retrieval + reasoning
- 🔍 **FAISS** vector store with open-source **BGE** embeddings (FastEmbed) — no embedding API costs
- 💬 **Memory layer** for conversation history
- 🛡️ **Guardrails** for safe RAG
- 🔎 **Self-critique** second LLM pass to catch weak answers
- ⚙️ Typed config via `pydantic-settings` ([config.py](RAG_AGENT_CODE/config.py))

---

## 🚀 Getting Started

Each agent is self-contained. In general:

```bash
# 1. Clone
git clone https://github.com/parthsharma1011/weekend_ai_agents.git
cd weekend_ai_agents

# 2. Pick an agent and install its deps
cd linkedin_generator_agent
pip install -r requirements.txt

# 3. Configure your keys
cp ../.env.example .env   # then fill in your keys
```

### Environment variables

Copy [.env.example](.env.example) into the agent folder as `.env` and fill in:

| Key | Purpose |
|-----|---------|
| `GEMINI_API_KEY` | Google Gemini — the LLM behind every agent |
| `TAVILY_API_KEY` | Web search (LinkedIn generator) |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | Optional observability & tracing |

> 🔒 **Never commit your `.env`.** It's already in [.gitignore](.gitignore) — only `.env.example` is tracked.

---

## 🧰 Tech Stack

- **LLM:** Google Gemini (`gemini-2.5-flash` / `gemini-2.0-flash`)
- **Orchestration:** CrewAI, LangGraph
- **Search:** Tavily
- **Vectors:** FAISS + BGE embeddings (FastEmbed)
- **Observability:** Langfuse
- **Config:** pydantic-settings, python-dotenv

---

## ⭐ Like this repo?

If these agents helped you learn something, saved you time, or gave you an idea for your own weekend build —

**⭐ Star the repo** to support the work, and **🍴 fork it** to make it your own.
Every star and fork genuinely helps and keeps me building more of these in the open. Thank you! 🙏

> Built on weekends, one agent at a time. Contributions, issues, and ideas are always welcome.

---
title: SHL Recommender API
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# SHL Conversational Assessment Recommender

A conversational recommendation service that helps hiring managers select the right SHL assessments from the product catalog. Built using **FastAPI**, **Chroma DB** (vector database), the **Groq LLM API** (`llama-3.1-8b-instant`), and a **Streamlit** user interface.

---

## 🚀 Key Features

1. **Chroma DB Semantic Search**:
   - Switched from simple TF-IDF to an in-memory vector database using `chromadb`.
   - On startup, the server cleans and parses the catalog, embeds the description/keywords for all 377 assessments, and registers them in a temporary vector collection.
   - Queries fetch the top 25 context-specific matches in under 5ms.

2. **Stateless Conversation Tracking & Constraint Refinement**:
   - The backend operates statelessly. For every turn, it parses the incoming message history to reconstruct previously recommended assessments using link matching.
   - Reconstructed previous recommendations are appended to the semantic context of the latest search query and added to the validation set.
   - This ensures constraints added mid-conversation (e.g., *"add personality tests"*, *"drop Java"*) persist and refine the shortlist rather than starting over.

3. **Anti-Hallucination Guardrail**:
   - Discards any suggested IDs from the LLM that do not exist within the union of the latest query's top 25 Chroma search results and the previously recommended products.

4. **Strict Scope Control**:
   - Refuses off-topic questions (e.g. general hiring/interview advice, legal questions like HIPAA requirements, or programming scripts) and keeps recommendations empty during refusal.

5. **Turn Capping (8-Turn Limit)**:
   - Tracks turn numbers and notifies the LLM. On Turn 7 or 8, the LLM forces its final shortlist recommendation and terminates the conversation.

---

## 🛠️ Project Structure

- `main.py`: FastAPI server exposing the endpoints (`GET /health`, `POST /chat`), parsing state, and validating recommendations.
- `search_engine.py`: Pre-processes dirty catalog JSON and initializes the in-memory Chroma DB collection for vector retrieval.
- `llm_agent.py`: Formats prompts with TURN context, previous shortlists, and search results to query the Groq LLM.
- `models.py`: Pydantic request and response schemas.
- `app.py`: Streamlit dashboard client for interactive human testing.
- `benchmark.py`: Local evaluator test suite to verify constraints.
- `catalog.json`: Cleaned, formatted assessment catalog database on disk.

---

## ⚙️ Setup & Execution

### 1. Set the API Key
Create a `.env` file in the project root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Install Dependencies
This project uses virtual environment isolation managed by `uv`. Install dependencies into the virtual environment:
```bash
uv pip install -r requirements.txt --python .venv
```

### 3. Run the FastAPI Backend
Start the FastAPI server directly from the virtual environment:
```bash
.venv/bin/python main.py
```
*The server will index the catalog items on startup and listen on `http://127.0.0.1:8000`.*

### 4. Run the Streamlit Frontend Client
In a new terminal window, start the interactive interface:
```bash
.venv/bin/streamlit run app.py
```

### 5. Run the Automated Benchmark
To run the automated tests against your local backend server:
```bash
python3 benchmark.py
```

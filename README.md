# ScholarRAG 📚

A research-paper question-answering app that retrieves evidence from uploaded PDFs and uses Gemini to generate answers with numbered references.

Built with Streamlit, Sentence Transformers, FAISS, BM25, and PyMuPDF.

## Features

- Upload one or multiple research-paper PDFs.
- Ask questions about methods, findings, and limitations.
- Choose semantic (Dense), keyword (BM25), or Hybrid retrieval.
- Adjust the number of retrieved passages from 1 to 10 (default: 5).
- Inspect retrieved passages with their source filenames and page numbers.
- Generate answers with references such as `[1]` and `[2]`.

## How it works

1. PyMuPDF extracts text page by page.
2. Each page is split into 900-character chunks with 150-character overlap.
3. `all-MiniLM-L6-v2` creates normalized embeddings, indexed by FAISS.
4. BM25 indexes tokenized passages for keyword search.
5. Dense search, BM25, or a combination retrieves passages relevant to the question.
6. Gemini receives the question and retrieved passages, with instructions to answer only from the evidence.
7. Streamlit displays the answer and expandable evidence passages.

Hybrid retrieval combines up to 20 candidates from each search method using Reciprocal Rank Fusion, with a rank constant of 60. It returns the selected number of highest-ranked passages.

This project uses Retrieval-Augmented Generation (RAG); it does not train or fine-tune the language model.

## Technology stack

| Component | Technology |
|---|---|
| Interface | Streamlit |
| PDF text extraction | PyMuPDF |
| Embeddings | Sentence Transformers: `all-MiniLM-L6-v2` |
| Semantic search | FAISS, normalized inner-product similarity |
| Keyword search | BM25 (`rank-bm25`) |
| Rank fusion | Reciprocal Rank Fusion |
| Answer generation | Gemini API |
| API client | OpenAI Python SDK through Google's compatible endpoint |
| Configuration | python-dotenv |

The OpenAI SDK is used as an HTTP client for Gemini. Generation requests go to Google, and do not use OpenAI API credits.

## Project structure

```text
ScholarRAG/
├── app.py
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py
│   ├── embeddings.py
│   ├── retriever.py
│   └── generator.py
├── data/
│   └── uploads/
└── tests/
```

Create `.env` locally from `.env.example`. The `data/uploads/` and `tests/` folders are currently placeholders; uploaded PDFs are processed in memory.

## Setup on Windows

Python 3.11 is recommended for this project's setup.

### 1. Open the project

Download or clone this repository, then open the `ScholarRAG` folder in VS Code. Run the following commands from the folder containing `app.py`.

### 2. Create a virtual environment

```cmd
py -3.11 -m venv .venv
```

Activate in Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Or activate in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

### 4. Configure Gemini

Create an API key in [Google AI Studio](https://aistudio.google.com/apikey).

Create `.env` beside `app.py`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Replace the key placeholder with your own key. Model access, free-tier eligibility, quotas, and billing depend on your Google project. If this model is unavailable, use a supported text model accessible to your project.

Ensure `src/generator.py` loads `.env` from the project root and reads `GEMINI_API_KEY` and `GEMINI_MODEL`. Its client endpoint must be:

```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

See [Google's OpenAI compatibility guide](https://ai.google.dev/gemini-api/docs/openai) and [Gemini billing guidance](https://ai.google.dev/gemini-api/docs/billing).

### 5. Run the app

```cmd
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Internet access is needed for the initial embedding-model download and Gemini answer generation.

## Usage

1. Upload one or more text-based PDFs in the sidebar.
2. Wait for document indexing to finish.
3. Select `Hybrid`, `Dense`, or `BM25` retrieval.
4. Select the number of retrieved chunks.
5. Enter a question and click **Generate Answer**.
6. Review the answer and open its evidence passages to check the sources.

Example questions:

- What problem does this paper address?
- What methodology does the proposed system use?
- What limitations do the authors discuss?
- Which datasets and evaluation metrics are reported?
- How do the methods in these uploaded papers differ?

Answers depend on the passages retrieved; cross-paper comparisons may omit a paper if its passages are not selected.

## Security and data handling

- Keep `.env`, virtual environments, and cache files out of Git using `.gitignore`.
- Commit only placeholder credentials in `.env.example`.
- If an API key is exposed or committed, revoke it and create a replacement.
- PDF extraction, embeddings, and retrieval run locally. Your question and selected paper passages are sent to Google for generation.
- Review Google's data-use terms for your tier before processing confidential papers.

## Troubleshooting

| Error | What to check |
|---|---|
| `Set a valid GEMINI_API_KEY in .env` | Confirm `.env` is beside `app.py`, the variable name is correct, and the key is saved. Restart Streamlit. |
| Key exists but is not loaded | Check the filename is not `.env.txt`; use `encoding="utf-8-sig"` in `load_dotenv` if the file contains a UTF-8 BOM. |
| `401` or `403` | Check the API key and project permissions. |
| `404` / model unavailable | Set `GEMINI_MODEL` to a model available to your project. |
| `402` / prepaid credits depleted | Check Google project billing. A prepaid account requires credits; use eligible free-tier access if available. |
| `429` | Check rate limits, quota, and the provider's error details. |
| No extractable PDF text | Try a text-based PDF; OCR is not implemented. |

Restart the app after changing `.env`.

## Current limitations

- Scanned image-only PDFs require OCR, which is not implemented.
- Tables, equations, and multi-column layouts may lose structure during extraction.
- Chunking uses character windows within pages rather than semantic sections.
- Retrieval has no relevance threshold, so weakly related passages may still be returned.
- Citations are model-generated and are not automatically verified.
- Documents and indexes are held in session memory and are not persisted.
- The app does not retain conversation history.
- No benchmark results or automated evaluation suite are currently included.

## Possible improvements

- OCR for scanned documents.
- Section-aware chunking and better handling of tables.
- Persistent document storage and indexes.
- Retrieval relevance thresholds and reranking.
- Citation validation and answer-quality evaluation.
- Chat history and follow-up questions.
- A local language-model option for offline generation.

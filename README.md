    # HealthPay Backend Developer Assignment - Claim Document Processor

## Overview

This project implements a simplified backend pipeline to process medical insurance claim documents using AI tools and agent orchestration frameworks. It is built with FastAPI and modular AI agents that classify, extract, process, and validate claim documents.

## Architecture & Logic

- **FastAPI Backend:** Provides an async `/process-claim` endpoint accepting multiple PDF files.
- **Modular AI Agents:** Separate classes handle document classification, text extraction, document-specific processing (e.g., BillAgent, DischargeAgent), and validation.
- **Agent Orchestration:** The main endpoint orchestrates the agents to process each uploaded document and aggregate results.
- **Validation & Claim Decision:** Validates presence and consistency of required fields and returns an approval or rejection decision with reasons.
- **Pydantic Schemas:** Define structured JSON output for documents, validation results, and claim decision.

## AI Tools Usage

- **Cursor.ai:** Used as AI coding assistant for scaffolding, debugging, and architecture decisions.
- **OpenAI GPT (gpt-4o-mini):** Used for:
  - Document classification based on filename and content snippet.
  - Text extraction from document content.
  - Structured data extraction from text for bills and discharge summaries.
  - Validation logic is implemented in code but can be extended with LLMs.

## Prompt Examples

### Document Classification Prompt

```
Classify the following document based on filename and content snippet:
Filename: bill.pdf
Content snippet: [first 500 characters of file content]
Possible types: bill, discharge_summary, id_card, unknown
Return only the type.
```

### Text Extraction Prompt

```
Extract the main text content from the following document snippet:
[document content snippet]
```

### Bill Processing Prompt

```
Extract the following fields from the medical bill text: hospital_name, total_amount, date_of_service (ISO format). Return as JSON.
Text:
[extracted text]
```

### Discharge Summary Processing Prompt

```
Extract the following fields from the discharge summary text: patient_name, diagnosis, admission_date (ISO format), discharge_date (ISO format). Return as JSON.
Text:
[extracted text]
```

## Running the Project

1. Create a virtual environment and install dependencies from `requirements.txt`.
2. Set the environment variable `OPENAI_API_KEY` with your OpenAI API key.
3. Run the FastAPI app with `uvicorn main:app --reload`.
4. Use the `/process-claim` endpoint to upload PDF files for processing.

## Bonus

- Dockerfile can be added for containerization.
- Redis/PostgreSQL or vector store integration can be added for state management or enhanced AI workflows.

## Tradeoffs & Limitations

- Current AI integrations use OpenAI GPT as an example; other LLMs like Claude or Gemini can be integrated similarly.
- Text extraction assumes content is text-based; OCR integration may be needed for scanned PDFs.
- Validation logic is basic and can be extended with more complex cross-checks or LLM-based validation.

---

*This project demonstrates agentic workflows, modular design, and effective use of AI tools in backend development.*

# 🏥 HealthPay – FastAPI Backend for Medical Claim Processing System 

This backend system automates the processing of medical insurance claim documents using **FastAPI**, **modular AI agents**, and **asynchronous orchestration**. Designed for high extensibility and maintainability, it simulates real-world AI-enhanced workflows for insurance claim automation. 

## 🔧 Tech Stack
- **Backend:** FastAPI, Python (3.10+)  
- **Async / Worker:** Celery, Redis  
- **Database:** PostgreSQL  
- **AI:** OpenAI API (modular agent wrappers)  
- **Schemas & Validation:** Pydantic  
- **Auth:** JWT (PyJWT / jose)  
- **Containerization:** Docker & Docker Compose  
- **Testing:** Pytest, HTTPX (async tests)
## 🚀 FastAPI-Powered Architecture

- **Framework:** FastAPI (async-first design for high-performance APIs)
- **Endpoint:** `/process-claim` – accepts and processes multiple medical PDFs
- **Schema Models:** Uses Pydantic for strict and clean data modeling
- **Agent-Oriented Design:** Each document step (classification, extraction, processing, validation) is handled by dedicated agent classes

## 📄 Endpoint Overview
 
### `POST /process-claim`

- Accepts multiple PDF files
- Processes each file via a pipeline of AI-powered agents 
- Returns a unified claim validation decision and structured output

## ⚙️ Processing Pipeline

1. **PDF Validation**
   - Ensures all uploaded files are valid PDFs.

2. **Document Classification (Agent)**
   - Classifies documents (`bill`, `discharge_summary`, `id_card`, or `unknown`) based on filename and content snippet.
   - Prompt-based classification using GPT-4o-mini.

3. **Text Extraction (Agent)**
   - Extracts the main text from PDF content (plain text; OCR not implemented).

4. **Document-Specific Parsing (Agents)**
   - **BillAgent**: Extracts fields like `hospital_name`, `total_amount`, `date_of_service`.
   - **DischargeAgent**: Extracts `patient_name`, `diagnosis`, `admission_date`, `discharge_date`.

5. **Validation Agent**
   - Checks presence and consistency of fields.
   - Returns a `claim_decision`: `approved` or `rejected` with reasons.

## 📦 Modular AI Agent Design

Each processing step is encapsulated as a class-based async agent:
- `DocumentClassifierAgent`
- `TextExtractionAgent`
- `BillAgent`
- `DischargeAgent`
- `ValidationAgent`

This design ensures the system is:
- Scalable (easy to add new document types)
- Testable (each agent can be unit tested independently)
- Maintainable (loose coupling of logic)

## 🧠 Example Prompts Used

> These are simplified for LLM interactions (via OpenAI GPT-4o-mini):

### Classification Prompt
\`\`\`
Classify this document:
Filename: discharge.pdf
Content: [first 500 chars]
Types: bill, discharge_summary, id_card, unknown
Return: only the type
\`\`\`

### Bill Extraction Prompt
\`\`\`
Extract: hospital_name, total_amount, date_of_service
Text: [extracted text]
Return: JSON
\`\`\`

### Discharge Summary Prompt
\`\`\`
Extract: patient_name, diagnosis, admission_date, discharge_date
Text: [extracted text]
Return: JSON
\`\`\`


# Run the FastAPI app
uvicorn main:app --reload
\`\`\`

### 🧪 Test the Endpoint

Use Postman or \`curl\` to test:

\`\`\`bash
curl -X POST http://localhost:8000/process-claim \
  -F "files=@./bill.pdf" \
  -F "files=@./discharge.pdf"
\`\`\`

## 📁 Project Structure

```
.
├── agents/               # Modular AI agent classes
├── schemas.py            # Pydantic models for API and internal use
├── utils.py              # File reading, PDF validation helpers
├── main.py               # FastAPI app with /process-claim route
├── requirements.txt
└── README.md
```


---

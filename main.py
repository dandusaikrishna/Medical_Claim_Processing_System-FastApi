from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import asyncio

from agents import DocumentClassifierAgent, TextExtractionAgent, BillAgent, DischargeAgent, ValidationAgent
from schemas import ClaimResponse, Document
from utils import read_file_content, validate_pdf_files

app = FastAPI()

@app.post("/process-claim", response_model=ClaimResponse)
async def process_claim(files: List[UploadFile] = File(...)):
    """
    Endpoint to process multiple medical insurance claim documents.
    Accepts multiple PDF files, processes them using AI agents, and returns structured JSON.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if not validate_pdf_files(files):
        raise HTTPException(status_code=400, detail="All files must be PDFs")

    classifier = DocumentClassifierAgent()
    extractor = TextExtractionAgent()
    bill_agent = BillAgent()
    discharge_agent = DischargeAgent()
    validator = ValidationAgent()

    documents = []

    for file in files:
        content = await read_file_content(file)
        doc_type = await classifier.classify(content, file.filename)
        text = await extractor.extract_text(content)

        if doc_type == "bill":
            processed = await bill_agent.process(text)
        elif doc_type == "discharge_summary":
            processed = await discharge_agent.process(text)
        else:
            # For unknown or other types, just create a generic document entry
            processed = {
                "type": doc_type,
                "patient_name": None,
                "diagnosis": None,
                "admission_date": None,
                "discharge_date": None,
                "id_number": None,
                "hospital_name": None,
                "total_amount": None,
                "date_of_service": None,
                "content": text
            }

        documents.append(Document(**processed))

    validation_result = await validator.validate({"documents": [doc.model_dump() for doc in documents]})

    response = ClaimResponse(
        documents=documents,
        validation=validation_result,
        claim_decision=validation_result.get("claim_decision")
    )

    return response

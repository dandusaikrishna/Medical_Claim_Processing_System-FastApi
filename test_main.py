import pytest
from fastapi.testclient import TestClient
from main import app
from io import BytesIO
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_process_claim_no_files():
    response = client.post("/process-claim")
    assert response.status_code == 422  # FastAPI returns 422 for missing required files

def test_process_claim_non_pdf_file():
    files = [("files", ("test.txt", BytesIO(b"dummy content"), "text/plain"))]
    response = client.post("/process-claim", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "All files must be PDFs"}

@patch("agents.DocumentClassifierAgent.classify", new_callable=AsyncMock)
@patch("agents.TextExtractionAgent.extract_text", new_callable=AsyncMock)
@patch("agents.BillAgent.process", new_callable=AsyncMock)
@patch("agents.DischargeAgent.process", new_callable=AsyncMock)
@patch("agents.ValidationAgent.validate", new_callable=AsyncMock)
def test_process_claim_valid_pdf_files(mock_validate, mock_discharge_process, mock_bill_process, mock_extract_text, mock_classify):
    # Setup mocks
    mock_classify.side_effect = ["bill", "discharge_summary"]
    mock_extract_text.side_effect = ["Bill text content", "Discharge summary text content"]
    mock_bill_process.return_value = {
        "type": "bill",
        "hospital_name": "Mock Hospital",
        "total_amount": 1234,
        "date_of_service": "2024-01-01"
    }
    mock_discharge_process.return_value = {
        "type": "discharge_summary",
        "patient_name": "John Doe",
        "diagnosis": "Fracture",
        "admission_date": "2024-01-01",
        "discharge_date": "2024-01-10"
    }
    mock_validate.return_value = {
        "missing_documents": [],
        "discrepancies": [],
        "claim_decision": {
            "status": "approved",
            "reason": "All required documents present and data is consistent"
        }
    }

    dummy_pdf_content = b"%PDF-1.4 dummy pdf content"
    files = [
        ("files", ("bill.pdf", BytesIO(dummy_pdf_content), "application/pdf")),
        ("files", ("discharge_summary.pdf", BytesIO(dummy_pdf_content), "application/pdf"))
    ]
    response = client.post("/process-claim", files=files)
    assert response.status_code == 200
    json_response = response.json()
    assert "documents" in json_response
    assert "validation" in json_response
    assert "claim_decision" in json_response
    assert len(json_response["documents"]) == 2
    types = [doc["type"] for doc in json_response["documents"]]
    assert "bill" in types
    assert "discharge_summary" in types

from agents import ValidationAgent
import asyncio

@pytest.mark.asyncio
async def test_validation_missing_fields():
    validator = ValidationAgent()
    documents = [
        {
            "type": "bill",
            "hospital_name": "",
            "total_amount": 1000,
            "date_of_service": "2024-01-01"
        },
        {
            "type": "discharge_summary",
            "patient_name": "John Doe",
            "diagnosis": "",
            "admission_date": "2024-01-01",
            "discharge_date": "2024-01-10"
        }
    ]
    result = await validator.validate({"documents": documents})
    assert "bill missing hospital_name" in result["missing_documents"]
    assert "discharge_summary missing diagnosis" in result["missing_documents"]
    assert result["claim_decision"]["status"] == "rejected"

@pytest.mark.asyncio
async def test_validation_discrepancies():
    validator = ValidationAgent()
    documents = [
        {
            "type": "bill",
            "hospital_name": "ABC Hospital",
            "total_amount": 1000,
            "date_of_service": "2024-02-01"
        },
        {
            "type": "discharge_summary",
            "patient_name": "John Doe",
            "diagnosis": "Fracture",
            "admission_date": "2024-01-01",
            "discharge_date": "2024-01-10"
        }
    ]
    result = await validator.validate({"documents": documents})
    assert any("Bill date" in d for d in result["discrepancies"])
    assert result["claim_decision"]["status"] == "rejected"

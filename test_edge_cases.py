import pytest
from fastapi.testclient import TestClient
from main import app
from io import BytesIO
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@patch("agents.DocumentClassifierAgent.classify", new_callable=AsyncMock)
@patch("agents.TextExtractionAgent.extract_text", new_callable=AsyncMock)
@patch("agents.BillAgent.process", new_callable=AsyncMock)
@patch("agents.DischargeAgent.process", new_callable=AsyncMock)
@patch("agents.ValidationAgent.validate", new_callable=AsyncMock)
def test_edge_case_unknown_document_type(mock_validate, mock_discharge_process, mock_bill_process, mock_extract_text, mock_classify):
    mock_classify.return_value = "unknown"
    mock_extract_text.return_value = "Some unknown document text"
    mock_validate.return_value = {
        "missing_documents": [],
        "discrepancies": [],
        "claim_decision": {
            "status": "approved",
            "reason": "All required documents present and data is consistent"
        }
    }

    dummy_pdf_content = b"%PDF-1.4 dummy pdf content"
    files = [("files", ("unknown.pdf", BytesIO(dummy_pdf_content), "application/pdf"))]

    response = client.post("/process-claim", files=files)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["documents"][0]["type"] == "unknown"
    assert "content" in json_response["documents"][0]

@patch("agents.DocumentClassifierAgent.classify", new_callable=AsyncMock)
@patch("agents.TextExtractionAgent.extract_text", new_callable=AsyncMock)
@patch("agents.BillAgent.process", new_callable=AsyncMock)
@patch("agents.DischargeAgent.process", new_callable=AsyncMock)
@patch("agents.ValidationAgent.validate", new_callable=AsyncMock)
def test_edge_case_empty_pdf(mock_validate, mock_discharge_process, mock_bill_process, mock_extract_text, mock_classify):
    mock_classify.return_value = "bill"
    mock_extract_text.return_value = ""
    mock_bill_process.return_value = {
        "type": "bill",
        "hospital_name": "",
        "total_amount": 0,
        "date_of_service": ""
    }
    mock_validate.return_value = {
        "missing_documents": ["bill missing hospital_name", "bill missing date_of_service"],
        "discrepancies": [],
        "claim_decision": {
            "status": "rejected",
            "reason": "Missing required fields"
        }
    }

    dummy_pdf_content = b"%PDF-1.4 dummy pdf content"
    files = [("files", ("empty_bill.pdf", BytesIO(dummy_pdf_content), "application/pdf"))]

    response = client.post("/process-claim", files=files)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["validation"]["missing_documents"]
    assert json_response["claim_decision"]["status"] == "rejected"

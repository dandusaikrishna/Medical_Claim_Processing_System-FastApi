import asyncio
import time
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
def test_concurrent_requests(mock_validate, mock_discharge_process, mock_bill_process, mock_extract_text, mock_classify):
    # Setup mocks with cycle to avoid StopAsyncIteration
    side_effect_classify = ["bill", "discharge_summary"] * 10
    side_effect_extract = ["Bill text content", "Discharge summary text content"] * 10
    mock_classify.side_effect = side_effect_classify
    mock_extract_text.side_effect = side_effect_extract
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

    async def send_request():
        response = client.post("/process-claim", files=files)
        assert response.status_code == 200
        json_response = response.json()
        assert "documents" in json_response
        assert "validation" in json_response
        assert "claim_decision" in json_response

    async def run_concurrent_requests(n):
        tasks = [asyncio.create_task(send_request()) for _ in range(n)]
        await asyncio.gather(*tasks)

    start_time = time.time()
    asyncio.run(run_concurrent_requests(10))  # Simulate 10 concurrent requests
    duration = time.time() - start_time
    print(f"Handled 10 concurrent requests in {duration:.2f} seconds")

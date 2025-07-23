import os
import openai
from typing import Dict, Any
import json

# Set your OpenAI API key as environment variable OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

class BaseAgent:
    async def classify(self, file_content: bytes, filename: str) -> str:
        """
        Classify the document type based on content or filename.
        """
        prompt = f"Classify the following document based on filename and content snippet:\nFilename: {filename}\nContent snippet: {file_content[:500].decode(errors='ignore')}\nPossible types: bill, discharge_summary, id_card, unknown\nReturn only the type."
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0
        )
        doc_type = response.choices[0].message.content.strip().lower()
        if doc_type not in ["bill", "discharge_summary", "id_card"]:
            doc_type = "unknown"
        return doc_type

    async def extract_text(self, file_content: bytes) -> str:
        """
        Extract text from the document using an LLM or OCR.
        """
        prompt = f"Extract the main text content from the following document snippet:\n{file_content[:1000].decode(errors='ignore')}"
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0
        )
        extracted_text = response.choices[0].message.content.strip()
        return extracted_text

    async def process(self, text: str) -> Dict[str, Any]:
        """
        Process extracted text into structured data.
        """
        # Extract bill fields
        bill_prompt = f"Extract the following fields from the medical bill text: hospital_name, total_amount, date_of_service (ISO format). Return as JSON.\nText:\n{text}"
        bill_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": bill_prompt}],
            max_tokens=200,
            temperature=0
        )
        try:
            bill_data = json.loads(bill_response.choices[0].message.content.strip())
            bill_data["type"] = "bill"
        except Exception:
            bill_data = {}

        # Extract discharge summary fields
        discharge_prompt = f"Extract the following fields from the discharge summary text: patient_name, diagnosis, admission_date (ISO format), discharge_date (ISO format). Return as JSON.\nText:\n{text}"
        discharge_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": discharge_prompt}],
            max_tokens=300,
            temperature=0
        )
        try:
            discharge_data = json.loads(discharge_response.choices[0].message.content.strip())
            discharge_data["type"] = "discharge_summary"
        except Exception:
            discharge_data = {}

        documents = []
        if bill_data:
            documents.append(bill_data)
        if discharge_data:
            documents.append(discharge_data)

        return {"documents": documents}

    async def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the structured data for missing or inconsistent information.
        """
        missing_documents = []
        discrepancies = []

        required_fields = {
            "bill": ["hospital_name", "total_amount", "date_of_service"],
            "discharge_summary": ["patient_name", "diagnosis", "admission_date", "discharge_date"],
            "id_card": ["patient_name", "id_number"]
        }

        for doc in data.get("documents", []):
            doc_type = doc.get("type")
            if doc_type in required_fields:
                for field in required_fields[doc_type]:
                    if field not in doc or not doc[field]:
                        missing_documents.append(f"{doc_type} missing {field}")

        bill_dates = [doc.get("date_of_service") for doc in data.get("documents", []) if doc.get("type") == "bill"]
        discharge_dates = [(doc.get("admission_date"), doc.get("discharge_date")) for doc in data.get("documents", []) if doc.get("type") == "discharge_summary"]

        for b_date in bill_dates:
            for adm_date, dis_date in discharge_dates:
                if adm_date and dis_date and b_date:
                    if not (adm_date <= b_date <= dis_date):
                        discrepancies.append(f"Bill date {b_date} not within admission {adm_date} and discharge {dis_date} dates")

        claim_decision = {
            "status": "approved" if not missing_documents and not discrepancies else "rejected",
            "reason": "All required documents present and data is consistent" if not missing_documents and not discrepancies else "Missing or inconsistent data"
        }

        return {
            "missing_documents": missing_documents,
            "discrepancies": discrepancies,
            "claim_decision": claim_decision
        }

from pydantic import BaseModel
from typing import List, Optional, Literal

class BillDocument(BaseModel):
    type: Literal["bill"]
    hospital_name: str
    total_amount: float
    date_of_service: str  # ISO date string

class DischargeSummaryDocument(BaseModel):
    type: Literal["discharge_summary"]
    patient_name: str
    diagnosis: str
    admission_date: str  # ISO date string
    discharge_date: str  # ISO date string

class IDCardDocument(BaseModel):
    type: Literal["id_card"]
    patient_name: str
    id_number: str

from pydantic import BaseModel, RootModel
from typing import List, Optional, Literal, Union

class BillDocument(BaseModel):
    type: Literal["bill"]
    hospital_name: str
    total_amount: float
    date_of_service: str  # ISO date string

class DischargeSummaryDocument(BaseModel):
    type: Literal["discharge_summary"]
    patient_name: str
    diagnosis: str
    admission_date: str  # ISO date string
    discharge_date: str  # ISO date string

class IDCardDocument(BaseModel):
    type: Literal["id_card"]
    patient_name: str
    id_number: str

class GenericDocument(BaseModel):
    type: str
    content: Optional[str]

class Document(RootModel[Union[BillDocument, DischargeSummaryDocument, IDCardDocument, GenericDocument]]):
    pass

class ValidationResult(BaseModel):
    missing_documents: List[str]
    discrepancies: List[str]

class ClaimDecision(BaseModel):
    status: str
    reason: str

class ClaimResponse(BaseModel):
    documents: List[Document]
    validation: ValidationResult
    claim_decision: ClaimDecision

class ValidationResult(BaseModel):
    missing_documents: List[str]
    discrepancies: List[str]

class ClaimDecision(BaseModel):
    status: str
    reason: str

class ClaimResponse(BaseModel):
    documents: List[Document]
    validation: ValidationResult
    claim_decision: ClaimDecision

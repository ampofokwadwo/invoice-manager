from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, field_serializer
from typing import List, Optional, Literal
from datetime import datetime
import uuid

################# CUSTOMER MODEL ##########################
# Customer Create Model
class CustomerCreate(BaseModel):
    client_name : str
    client_email : EmailStr
    client_contact: str
    company_name : str

    @field_validator("client_email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

# Customer Update model
class CustomerUpdate(BaseModel):
    client_name : Optional[str] = None
    client_email : Optional[EmailStr] = None
    client_contact : Optional[str] = None
    company_name : Optional[str] = None

    @field_validator("client_email")
    @classmethod
    def normalize_email(cls, value: Optional[str]) -> Optional[str]:
        return value.lower() if value else value

# Customer Read Model
class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    client_name : str
    client_email : EmailStr
    client_contact : str
    company_name : str
    created_at : datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")


################# INVOICE MODEL ##########################
# InvoiceItem Create
class InvoiceItemCreate(BaseModel):
    description : str
    quantity: int = Field(gt=0)
    unit_price : float = Field(gt=0)

# InvoiceItem Read — defined before InvoiceRead to avoid forward reference errors
class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    quantity: int
    unit_price: float
    subtotal: float

# Create Invoice Model
class InvoiceCreate(BaseModel):
    customer_id : int
    invoice_number : str = Field(default_factory=lambda: f"INV-{uuid.uuid4().hex[:8].upper()}")
    issue_date : datetime
    due_date : datetime
    items : List[InvoiceItemCreate] = Field(min_length=1)

    @field_validator("invoice_number")
    @classmethod
    def generate_invoice_number(cls, value: str) -> str:
        if not value or not value.strip():
            return f"INV-{uuid.uuid4().hex[:8].upper()}"
        return value.strip()

# Read Invoice Model
class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    customer_id : int
    invoice_number : str
    issue_date : datetime
    due_date : datetime
    total_amount : float
    status : str
    created_at : datetime
    items : List[InvoiceItemRead] = []

    @field_serializer("issue_date", "due_date", "created_at")
    def serialize_dates(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M")

# Update Invoice Model
class InvoiceUpdate(BaseModel):
    invoice_number : Optional[str] = None
    status : Optional[Literal["Paid", "Unpaid", "Pending"]] = None
    issue_date : Optional[datetime] = None
    due_date : Optional[datetime] = None
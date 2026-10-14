from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base

class Customer(Base):
    __tablename__ = "Customer"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String, nullable=False)
    client_email = Column(String, nullable=False)
    client_contact = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Invoice(Base):
    __tablename__ = "Invoice"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("Customer.id"), nullable=False)
    invoice_number = Column(String, nullable=False)
    status = Column(String, default="Pending")
    issue_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "InvoiceItem"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("Invoice.id"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src.database import *
from src.models import *
from src.schemas import *


app = FastAPI(title="Invoice Manager", description="A simple invoice manager API")


@app.get("/")
def read_root():
    return {"message": "Invoice Manager API", "status": "running"}

############## CUSTOMER OPERATIONS #########################
# Create Customer
@app.post("/customers", response_model= CustomerRead)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db), ):
  existing_customer = (db.query(Customer).filter(Customer.client_email == customer.client_email).first())
  if existing_customer:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Customer with this email already exists")

  new_customer = Customer(**customer.model_dump())
  db.add(new_customer)
  db.commit()
  db.refresh(new_customer)
  return new_customer


# Get All customers
@app.get("/customers", response_model= List[CustomerRead])
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers

# Get Customer by ID
@app.get("/customers/{customer_id}", response_model = CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail = "Customer not found")

    return customer


# Update Customer
@app.patch("/customers/{customer_id}", response_model= CustomerRead)
def update_customer(customer_id: int, customer_data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer: 
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= "Customer not found")

    update_data = customer_data.model_dump(exclude_unset= True)

    if "client_email" in update_data:
        existing_customer = (db.query(Customer)
                             .filter(Customer.client_email == update_data["client_email"], Customer.id != customer_id)
                             .first())
        if existing_customer:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Customer with this email already exists")

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


# Delete Customer
@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")

    has_invoices = db.query(Invoice).filter(Invoice.customer_id == customer_id).first()
    if has_invoices:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cannot delete customer with existing invoices")

    db.delete(customer)
    db.commit()

    return {"detail": "Customer deleted successfully"}


# Delete All Customers
@app.delete("/customers")
def delete_all_customers(db: Session = Depends(get_db)):
    customer_ids = [cid for (cid,) in db.query(Customer.id).all()]
    if not customer_ids:
        return {"detail": "No customers to delete"}

    invoice_ids = [iid for (iid,) in db.query(Invoice.id).filter(Invoice.customer_id.in_(customer_ids)).all()]
    if invoice_ids:
        db.query(InvoiceItem).filter(InvoiceItem.invoice_id.in_(invoice_ids)).delete(synchronize_session=False)
        db.query(Invoice).filter(Invoice.id.in_(invoice_ids)).delete(synchronize_session=False)

    db.query(Customer).filter(Customer.id.in_(customer_ids)).delete(synchronize_session=False)
    db.commit()

    return {"detail": "All customers deleted successfully"}


################# INVOICE OPERATIONS ########################
# Create Invoice
@app.post("/invoices", response_model= InvoiceRead)
def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db)):
    customer = (db.query(Customer).filter(Customer.id == invoice_data.customer_id).first())
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")

    existing_invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_data.invoice_number).first()
    if existing_invoice:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Invoice already exists")

    new_invoice = Invoice(customer_id = invoice_data.customer_id, invoice_number = invoice_data.invoice_number, status= "Unpaid", issue_date = invoice_data.issue_date, due_date = invoice_data.due_date)

    total_amount = 0
    for item_data in invoice_data.items:
        subtotal = item_data.quantity * item_data.unit_price
        total_amount += subtotal
        new_item = InvoiceItem(
            description = item_data.description,
            quantity = item_data.quantity,
            unit_price = item_data.unit_price,
            subtotal = subtotal
        )
        new_invoice.items.append(new_item)

    new_invoice.total_amount = total_amount

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return new_invoice


# Get All invoices
@app.get("/invoices", response_model= List[InvoiceRead])
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return invoices


################ INVOICE SUMMARY ############################
# NOTE: must stay above /invoices/{invoice_id} or the path param shadows it
@app.get("/invoices/summary")
def get_invoice_summary(
    db: Session = Depends(get_db),
):
    invoices = db.query(Invoice).all()

    total_invoices = len(invoices)
    paid_invoices = 0
    unpaid_invoices = 0

    total_amount = 0
    paid_amount = 0
    unpaid_amount = 0

    for invoice in invoices:
        invoice_total = sum(
            item.quantity * item.unit_price
            for item in invoice.items
        )

        total_amount += invoice_total

        if invoice.status.lower() == "paid":
            paid_invoices += 1
            paid_amount += invoice_total
        else:
            unpaid_invoices += 1
            unpaid_amount += invoice_total

    return {
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "unpaid_invoices": unpaid_invoices,
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "unpaid_amount": unpaid_amount,
    }


# Get Invoice by ID
@app.get("/invoices/{invoice_id}", response_model= InvoiceRead)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    return invoice


# Update Invoice
@app.patch("/invoices/{invoice_id}", response_model= InvoiceRead)
def update_invoice(invoice_id: int, invoice_data: InvoiceUpdate, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    update_data = invoice_data.model_dump(exclude_unset= True)

    if "invoice_number" in update_data:
        existing = (db.query(Invoice)
                    .filter(Invoice.invoice_number == update_data["invoice_number"], Invoice.id != invoice_id)
                    .first())
        if existing:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Invoice number already exists")

    for field, value in update_data.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)

    return invoice


# Delete Invoice
@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    db.delete(invoice)
    db.commit()

    return {"detail": "Invoice deleted successfully"}
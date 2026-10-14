# 🧾 Invoice Manager API

A clean, lightweight REST API for managing customers and invoices — built with **FastAPI**, **SQLAlchemy**, and **SQLite**, with **Alembic** handling database migrations.

---

## ✨ Features

- **Customer Management** — Create, read, update, and delete customers
- **Invoice Management** — Create invoices with line items, track status, and delete them
- **Auto-calculated totals** — Subtotals and invoice totals are computed automatically
- **Duplicate prevention** — Unique email and invoice number enforcement
- **Invoice summary** — Aggregate stats (paid vs unpaid counts and amounts)
- **Data validation** — Strict input validation via Pydantic schemas
- **Database migrations** — Schema versioning with Alembic

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework & automatic OpenAPI docs |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM & database abstraction |
| [Alembic](https://alembic.sqlalchemy.org/) | Database migrations |
| [Pydantic v2](https://docs.pydantic.dev/) | Request/response validation & serialization |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Environment-based configuration |
| [SQLite](https://www.sqlite.org/) | Embedded database (zero config) |
| [uv](https://docs.astral.sh/uv/) | Fast Python package manager |

---

## 📁 Project Structure

```
invoice-manger/
├── src/
│   ├── main.py          # FastAPI app & all route handlers
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── database.py      # DB engine, session, and Base
│   ├── config.py        # App settings (pydantic-settings)
│   └── __init__.py
├── migrations/
│   ├── versions/        # Alembic migration scripts
│   ├── env.py           # Alembic environment config
│   └── script.py.mako   # Migration template
├── alembic.ini          # Alembic configuration file
├── pyproject.toml       # Project metadata & dependencies
├── uv.lock              # Locked dependency tree
└── invoice_manager.db   # SQLite database file (auto-created)
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### 1. Clone the repository

```bash
git clone https://github.com/ampofokwadwo/team-task-manager.git
cd invoice-manger
```

### 2. Create the virtual environment and install dependencies

```bash
uv sync
```

### 3. Apply database migrations

```bash
uv run alembic upgrade head
```

### 4. Start the development server

```bash
uv run fastapi dev src/main.py
```

The API will be live at **http://127.0.0.1:8000**

---

## ⚙️ Configuration

Settings are managed via environment variables or a `.env` file in the project root.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./invoice_manager.db` | SQLAlchemy database connection string |
| `PROJECT_NAME` | `Invoice Manager` | Application name |

**Example `.env`:**
```env
DATABASE_URL=sqlite:///./invoice_manager.db
PROJECT_NAME=Invoice Manager
```

---

## 📖 API Reference

Interactive documentation is available at:
- **Swagger UI** → `http://127.0.0.1:8000/docs`
- **ReDoc** → `http://127.0.0.1:8000/redoc`

---

### Customers

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/customers` | List all customers |
| `POST` | `/customers` | Create a new customer |
| `GET` | `/customers/{id}` | Get a customer by ID |
| `PATCH` | `/customers/{id}` | Update a customer |
| `DELETE` | `/customers/{id}` | Delete a customer (fails if they have invoices) |
| `DELETE` | `/customers` | Delete all customers (cascades to invoices) |

#### Create Customer — Request Body
```json
{
  "client_name": "Jane Doe",
  "client_email": "jane@example.com",
  "client_contact": "+1-555-0100",
  "company_name": "Acme Corp"
}
```

#### Create Customer — Response
```json
{
  "id": 1,
  "client_name": "Jane Doe",
  "client_email": "jane@example.com",
  "client_contact": "+1-555-0100",
  "company_name": "Acme Corp",
  "created_at": "2026-10-14 01:00"
}
```

---

### Invoices

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/invoices` | List all invoices |
| `POST` | `/invoices` | Create a new invoice with line items |
| `GET` | `/invoices/summary` | Get aggregate paid/unpaid stats |
| `GET` | `/invoices/{id}` | Get an invoice by ID (includes line items) |
| `PATCH` | `/invoices/{id}` | Update invoice fields (e.g. mark as Paid) |
| `DELETE` | `/invoices/{id}` | Delete an invoice (cascades to its items) |

#### Create Invoice — Request Body
```json
{
  "customer_id": 1,
  "invoice_number": "INV-2026-001",
  "issue_date": "2026-10-14T00:00:00",
  "due_date": "2026-11-14T00:00:00",
  "items": [
    {
      "description": "Web Design",
      "quantity": 1,
      "unit_price": 1500.00
    },
    {
      "description": "Hosting (annual)",
      "quantity": 1,
      "unit_price": 120.00
    }
  ]
}
```

> `invoice_number` is optional — one is auto-generated in the format `INV-XXXXXXXX` if omitted.

#### Create Invoice — Response
```json
{
  "id": 1,
  "customer_id": 1,
  "invoice_number": "INV-2026-001",
  "status": "Unpaid",
  "issue_date": "2026-10-14 00:00",
  "due_date": "2026-11-14 00:00",
  "total_amount": 1620.00,
  "created_at": "2026-10-14 01:00",
  "items": [
    { "id": 1, "description": "Web Design", "quantity": 1, "unit_price": 1500.00, "subtotal": 1500.00 },
    { "id": 2, "description": "Hosting (annual)", "quantity": 1, "unit_price": 120.00, "subtotal": 120.00 }
  ]
}
```

#### Update Invoice Status
```json
{
  "status": "Paid"
}
```

Valid statuses: `Paid` | `Unpaid` | `Pending`

#### Invoice Summary — Response
```json
{
  "total_invoices": 5,
  "paid_invoices": 3,
  "unpaid_invoices": 2,
  "total_amount": 8500.00,
  "paid_amount": 6000.00,
  "unpaid_amount": 2500.00
}
```

---

## 🗄️ Database Schema

```
Customer
├── id            INTEGER  PK
├── client_name   TEXT     NOT NULL
├── client_email  TEXT     NOT NULL  (unique enforced at app level)
├── client_contact TEXT    NOT NULL
├── company_name  TEXT     NOT NULL
└── created_at    DATETIME

Invoice
├── id             INTEGER  PK
├── customer_id    INTEGER  FK → Customer.id
├── invoice_number TEXT     NOT NULL  (unique enforced at app level)
├── status         TEXT     DEFAULT 'Pending'
├── issue_date     DATETIME
├── due_date       DATETIME
├── total_amount   FLOAT    NOT NULL
└── created_at     DATETIME

InvoiceItem
├── id          INTEGER  PK
├── invoice_id  INTEGER  FK → Invoice.id  (CASCADE delete)
├── description TEXT     NOT NULL
├── quantity    INTEGER  NOT NULL
├── unit_price  FLOAT    NOT NULL
└── subtotal    FLOAT    NOT NULL
```

---

## 🔄 Database Migrations

This project uses **Alembic** for schema migrations.

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Roll back the last migration
uv run alembic downgrade -1

# Auto-generate a new migration after editing models.py
uv run alembic revision --autogenerate -m "your description here"

# View migration history
uv run alembic history
```

---

## 📦 Dependency Management

Dependencies are managed with **uv**.

```bash
# Install all dependencies from lockfile
uv sync

# Add a new dependency
uv add <package>

# Update the lockfile
uv lock
```

---

## 📄 License

This project is open source and available under the [MIT License].

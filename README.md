# FinanceOS — Finance Dashboard Backend Assignment

> A full-stack finance dashboard system with role-based access control, JWT authentication, financial records management, and real-time analytics. Built as a backend internship assignment.

---

## 🔗 Live Demo

| Layer | URL |
|---|---|
| 🌐 Frontend (Vercel) | https://zorvyn-finance-assignment-ochre.vercel.app |
| ⚙️ Backend API Docs (Railway) | https://zorvyn-finance-assignment-production.up.railway.app/docs |
| 📦 GitHub Repository | https://github.com/AkashParley/zorvyn-finance-Assignment |

---

## 📌 What This Project Does

FinanceOS is a backend-first finance dashboard system where different users interact with financial records based on their assigned role. The system enforces access control at the API level — not just in the UI — so no amount of frontend manipulation can bypass permissions.

**Three roles, three levels of access:**

| Role | What they can do |
|---|---|
| **Viewer** | View dashboard summary and transaction records |
| **Analyst** | Everything a Viewer can do, plus access to insights and category breakdowns |
| **Admin** | Full access — create, edit, delete records and manage all users |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Python + FastAPI |
| Database | PostgreSQL (hosted on Railway) |
| ORM & Migrations | SQLAlchemy 2.0 + Alembic |
| Authentication | JWT (python-jose) + bcrypt password hashing |
| Validation | Pydantic v2 |
| Frontend | React 18 + Tailwind CSS + Recharts |
| Backend Hosting | Railway |
| Frontend Hosting | Vercel |
| Testing | pytest + httpx (SQLite in-memory) |

---

## 🏗 Project Architecture

```
finance-backend/
├── app/
│   ├── main.py                  # App factory, CORS, global error handlers, lifespan
│   ├── api/v1/endpoints/
│   │   ├── auth.py              # Register, login, /me
│   │   ├── users.py             # Admin user management
│   │   ├── transactions.py      # CRUD + filters + search
│   │   └── dashboard.py         # Aggregated summary analytics
│   ├── core/
│   │   ├── config.py            # Environment-based settings
│   │   ├── security.py          # JWT encode/decode, bcrypt
│   │   ├── roles.py             # Role enum + permission map
│   │   └── exceptions.py        # Typed HTTP exception helpers
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── services/                # Business logic layer
│   └── middleware/auth.py       # require_permission() dependency factory
│
finance-frontend/
├── src/
│   ├── pages/                   # LoginPage, DashboardPage, TransactionsPage, UsersPage
│   ├── components/              # Reusable UI + layout components
│   ├── context/AuthContext.jsx  # Global JWT auth state
│   └── services/api.js          # All API calls with auto-logout on 401
```

---

## ✅ Features Implemented

### Core Requirements
- [x] User registration and login with JWT authentication
- [x] Role-based access control (Viewer / Analyst / Admin)
- [x] User status management (active / inactive)
- [x] Financial records — create, read, update, soft-delete
- [x] Filter transactions by type, category, date range
- [x] Full-text search across category and description
- [x] Paginated transaction listing
- [x] Dashboard summary — total income, expenses, net balance
- [x] Category-wise income and expense breakdowns
- [x] Monthly trend analytics
- [x] Permission enforcement via middleware (not just frontend guards)

### Optional Enhancements
- [x] JWT authentication with configurable expiry
- [x] Pagination on both transactions and users
- [x] Soft delete (records are hidden, not permanently removed)
- [x] Auto-seeded first admin on startup
- [x] Unit tests (security, role logic)
- [x] Integration tests (auth, transactions, dashboard)
- [x] Full API documentation via Swagger UI and ReDoc
- [x] Alembic database migrations
- [x] Deployed and publicly accessible

---

## 🔐 API Overview

All endpoints are prefixed with `/api/v1`.

### Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | None | Register new user (default: viewer) |
| POST | `/auth/login` | None | Login and receive JWT token |
| GET | `/auth/me` | Any | Get current user profile |

### Transactions
| Method | Endpoint | Min Role | Description |
|---|---|---|---|
| GET | `/transactions` | Viewer | List with filters, search, pagination |
| GET | `/transactions/{id}` | Viewer | Get single transaction |
| POST | `/transactions` | Admin | Create new record |
| PATCH | `/transactions/{id}` | Admin | Update record |
| DELETE | `/transactions/{id}` | Admin | Soft-delete record |

### Dashboard
| Method | Endpoint | Min Role | Description |
|---|---|---|---|
| GET | `/dashboard/summary` | Viewer | Full aggregated analytics |

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users` | List all users |
| PATCH | `/users/{id}` | Update role or status |
| DELETE | `/users/{id}` | Deactivate user |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Node.js 18+

### Backend

```bash
cd finance-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Edit DATABASE_URL and SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd finance-frontend
npm install
npm start
```

Open `http://localhost:3000` — default admin credentials: `admin / Admin@123`

---

## 🧪 Running Tests

Tests use SQLite in-memory — no PostgreSQL required.

```bash
cd finance-backend
pytest --cov=app --cov-report=term-missing
```

Test coverage includes:
- Password hashing and JWT encode/decode
- Role permission logic for all three roles
- Auth endpoints (register, login, /me)
- Transaction CRUD and access control per role
- Dashboard summary accuracy

---

## 💡 Design Decisions

### Permission-String Model over Role Hierarchy
Rather than comparing role levels as integers (`role >= ANALYST`), each role maps to an explicit set of permission strings stored in a dictionary. This makes the intent clear at every call site — `require_permission("create:records")` — and allows future role changes without touching unrelated code.

### Soft Deletes
Transactions are never permanently removed. A boolean `is_deleted` flag hides records from all queries while preserving the full audit trail. In financial systems, being able to trace what happened and when is more important than freeing storage.

### Service Layer Separation
Business logic lives entirely in `app/services/`, not in route handlers. Routes are kept thin — validate input, call a service, return the result. This made testing straightforward and kept the codebase readable as it grew.

### Schema Separation (Request vs Response)
`UserCreate` and `UserResponse` are intentionally separate Pydantic models. This guarantees that `hashed_password`, `is_deleted`, and other internal fields can never accidentally leak into API responses, regardless of what gets added to the ORM model later.

### SQLite for Tests
Tests run against an in-memory SQLite database with transaction rollback between each test function. No PostgreSQL needed to run the test suite — tests are fully isolated and run in seconds.

---

## 🐛 Problems I Faced and How I Solved Them

This section is honest about the real friction I ran into during development.

### 1. CORS Blocking the Frontend — The Hardest Bug to Diagnose

The most frustrating issue was when I deployed the frontend and every API call failed with `Failed to fetch`. The backend logs showed the requests were arriving fine but the browser was silently dropping the responses.

The root cause was that my React dev server was running on **port 3001** instead of the expected 3000 (because something else was occupying 3000). The CORS middleware was configured to allow only `localhost:3000`, so every request from `localhost:3001` was rejected at the browser level before the response could be read.

My first instinct was to check the backend code for bugs. I spent time looking at the route handlers, the auth middleware, the database connection — none of it was wrong. It took opening the browser DevTools Network tab and reading the actual CORS error to understand what was happening.

The fix was twofold: add all relevant origins to the CORS allowlist during development, and later switch to `allow_origins=["*"]` with `allow_credentials=False` for the local environment. For production on Railway, I set the specific Vercel domain explicitly.

**What I learned:** CORS errors are browser-level blocks, not server errors. The server returns 200 but the browser refuses to hand the response to JavaScript. Always check the Network tab — not just the console — when debugging fetch failures.

### 2. JWT Token Expiry Mid-Session

The default token expiry was set to 30 minutes. During testing I would set up users, add transactions, and come back to the dashboard after a break — only to find every API call returning `401 Could not validate credentials`. The error surfaced in the Edit User modal which made it look like a permissions bug rather than an expiry issue.

The fix had two parts: extend `ACCESS_TOKEN_EXPIRE_MINUTES` to 1440 (24 hours) in the `.env` file for development, and add an automatic redirect to `/login` in `api.js` whenever a 401 response is received. This way the user gets cleanly sent to the login page instead of seeing a confusing error in the middle of a modal.

```js
if (res.status === 401) {
  localStorage.removeItem("token");
  window.location.href = "/login";
  return;
}
```

**What I learned:** Token expiry is invisible until it happens at the worst moment. Auto-logout on 401 is not optional — it is the minimum expected behaviour for any authenticated app.

### 3. Accidentally Creating an Analyst as Viewer with Inactive Status

During user setup I registered `analyst1` but forgot to specify the correct role, so they were created as a Viewer. I then tried to fix it from the frontend Edit User modal — which triggered the CORS bug above — so both the role and the status ended up wrong.

Rather than fighting the frontend while CORS was broken, I went directly to the Swagger UI at `/docs`, authenticated with the admin token, and sent the PATCH request manually:

```json
{
  "role": "analyst",
  "status": "active"
}
```

This fixed both problems in a single request. It also confirmed that the backend logic itself was correct — the bug was entirely in how the frontend was communicating with it.

**What I learned:** Having interactive API docs (`/docs`) is not a nice-to-have for development — it is a debugging tool. Being able to test endpoints directly, bypassing the frontend entirely, saved a lot of time.

### 4. PostgreSQL Connection on Railway

Connecting the deployed backend to the Railway PostgreSQL instance required understanding how Railway injects environment variables. The `DATABASE_URL` format Railway provides uses `postgres://` as the scheme, but SQLAlchemy 2.0 requires `postgresql://`.

The fix was a one-line normalisation in `config.py`:

```python
DATABASE_URL: str = Field(..., env="DATABASE_URL")

@validator("DATABASE_URL", pre=True)
def fix_postgres_scheme(cls, v):
    if v.startswith("postgres://"):
        return v.replace("postgres://", "postgresql://", 1)
    return v
```

**What I learned:** Cloud providers and libraries do not always agree on URL formats. Always read the SQLAlchemy docs when something that works locally fails in production for no obvious reason.

---

## 📁 Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key — keep this secret and long |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (1440 = 24 hours recommended for dev) |
| `FIRST_ADMIN_EMAIL` | Email for the auto-seeded admin user |
| `FIRST_ADMIN_PASSWORD` | Password for the auto-seeded admin user |
| `FIRST_ADMIN_USERNAME` | Username for the auto-seeded admin user |

---

## 📄 Assumptions Made

- **Single currency** — all amounts are stored as `NUMERIC(15,2)` in a single implicit currency (INR in the UI). Multi-currency would require a `currency` field and an exchange-rate service.
- **No multi-tenancy** — all admin users share visibility of all records. A multi-tenant design would scope queries by `organization_id`.
- **Soft delete only** — there is no hard delete endpoint. This is intentional for financial audit trail integrity.
- **First admin is seeded** — rather than requiring a manual setup step, the first admin account is created automatically on startup using credentials from `.env`.

---

## 👤 Author

**Akash Parley**
GitHub: [@AkashParley](https://github.com/AkashParley)

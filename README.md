# Finance Tracker API

A robust, secure, and performant backend built with **Django REST Framework (DRF)** and **PostgreSQL**. Designed to handle complex financial tracking with a focus on data integrity, role-based security, and live analytics.

---

## Key Features

- **Identity & Access**: 
  - Role-Based Access Control (**RBAC**) with `ADMIN`, `ANALYST`, and `VIEWER` roles.
  - Secure **JWT Authentication** (SimpleJWT) with token rotation and blacklisting.
  - Self-healing Admin setup: One-time singleton creation logic for the first system admin.
- **Transaction Engine**: 
  - Track **INCOME** and **EXPENSE** with category tagging and real-time validation.
  - Powerful filtering by date ranges, categories, and types.
- **Data Resilience (Soft Delete)**: 
  - Non-destructive deletion pattern for all financial records.
  - Admin-only restoration tools to recover accidentally "removed" data.
- **Live Analytics**: 
  - Service-layer architecture (`FinanceAnalytics`) for high-performance aggregate calculations.
  - Dashboards for net balance, category distributions, and 6-month trends.
- **Developer Experience**:
  - Automated **OpenAPI 3.0** schema generation.
  - Interactive **Swagger UI** and **ReDoc** for sandbox testing.
  - Global API **Rate Limiting** to prevent brute-force attacks.

---

## Tech Stack

- **Framework**: Django 6.0 + Django REST Framework 3.17
- **Database**: PostgreSQL
- **Security**: SimpleJWT (Bearer Tokens), Python-Dotenv
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Architecture**: Service Layer Pattern, Custom QuerySets & Managers

---

## Getting Started

### 1. Prerequisites
- Python 3.14+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) (recommended package manager, however you can use pip as well.)

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd fintracker

# Install dependencies using uv
uv sync
```

### 3. Environment Configuration
Create a `.env` file in the root directory and populate it based on the `env_template.txt`:
```ini
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=fintracker
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Database Setup
```bash
uv run python manage.py migrate
```

---

## Access Control Matrix

| Role | Financial Records | Dashboard / Analytics | User Management | Restore Deleted Records |
| :--- | :---: | :---: | :---: | :---: |
| **ADMIN** | Full Access | Full Access | Full Access | Yes |
| **ANALYST** | Read Only | Full Access | No | No |
| **VIEWER** | No | Full Access | No | No |

---

## API Documentation

The API includes live interactive documentation out of the box:

- **Swagger UI**: [`/api/docs/`](http://localhost:8000/api/docs/) — *Best for testing and exploration.*
- **ReDoc**: [`/api/redoc/`](http://localhost:8000/api/redoc/) — *Best for technical reference.*
- **Raw Schema**: [`/api/schema/`](http://localhost:8000/api/schema/) — *Exportable OpenAPI v3 YAML.*

---

## Testing
The project maintains a healthy test suite covering logic, permissions, and security.
```bash
uv run python manage.py test
```

---

> [!NOTE]
> **Authentication Check**: Remember to use the `Bearer` prefix when authorizing in Swagger (e.g., `Bearer <your_token>`).

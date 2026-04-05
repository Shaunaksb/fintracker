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
- [uv](https://github.com/astral-sh/uv) (recommended) or [pip](https://pip.pypa.io/en/stable/)

### 2. Quick Setup (Recommended)
The easiest way to get started is by running the automated installation script. It handles dependencies, generates your `SECRET_KEY`, and runs initial migrations.

```bash
# Clone the repository
git clone <repository-url>
cd fintracker

# Run the installation script
# It auto-detects 'uv' if installed, otherwise defaults to 'pip'
python install.py
```

> [!TIP]
> You can force a specific manager using `python install.py --uv` or `python install.py --pip`.

### 3. Manual Installation (Optional)

#### Dependencies
If using **uv**:
```bash
uv sync
```
If using **pip**:
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file from `env_template.txt`. **Note: `install.py` will generate the `SECRET_KEY` for you.**

#### Database Setup
```bash
# Using uv
uv run python manage.py migrate

# Using pip
python manage.py migrate
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

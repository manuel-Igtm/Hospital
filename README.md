# Hospital Backend System

A modern, enterprise-ready hospital management backend built with Django and high-performance C modules. This system provides secure, scalable APIs for patient management, appointments, encounters, laboratory orders, billing, and comprehensive audit logging.

## 📚 Quick Links

- **[⚡ QUICKSTART](QUICKSTART.md)** - Get running in 5 minutes
- **[📖 PROJECT SUMMARY](PROJECT_SUMMARY.md)** - Complete overview
- **[🐳 Docker Guide](docker/README.md)** - Containerized deployment
- **[💻 Dev Guide](backend/README.md)** - Local development setup
- **[📊 Progress Tracking](docs/progress.md)** - Weekly updates
- **[🤝 Contributing](CONTRIBUTING.md)** - How to contribute

## 🏗️ Architecture

**Multi-language approach:**
- **C modules**: High-performance components for data validation (HL7/FHIR), cryptographic operations (AES-GCM, PHI pseudonymization), ABAC authorization policy evaluation, and billing calculations
- **Django (Python 3.12+)**: REST APIs, business logic, authentication, admin interface, and orchestration
- **PostgreSQL**: Primary production database with optimized indexes and partitioning
- **Redis + Celery**: Async task processing
- **ASGI via Uvicorn/Gunicorn**: Modern async-capable deployment

## ✨ Key Features

- **Complete Patient Management**: MRN-based patient records with PII protection
- **Appointment Scheduling**: Full lifecycle with calendar queries and status tracking
- **Clinical Encounters**: Visit documentation with diagnosis codes, orders, and notes
- **Laboratory Orders**: HL7-validated lab results with LOINC coding
- **E-Prescribing**: Medication management with ATC codes and dosing
- **Billing & Insurance**: Automated invoice generation with DRG/ICD-based calculations
- **Comprehensive Audit**: Every write operation logged with actor, timestamp, and IP
- **JWT Authentication**: Secure token-based auth with refresh and blacklist
- **RBAC + ABAC**: Role-based and attribute-based access control via compiled C policies
- **OpenAPI Documentation**: Auto-generated Swagger UI with examples

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended) OR
- Python 3.12+, PostgreSQL 14+, Redis, CMake, GCC/Clang, OpenSSL dev libraries

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/manuel-Igtm/Hospital.git
cd Hospital

# Copy environment template
cp docker/.env.example docker/.env

# Start all services
docker compose -f docker/docker-compose.yml up -d

# Wait for database to be ready, then run migrations
docker compose -f docker/docker-compose.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser

# Load demo data
docker compose -f docker/docker-compose.yml exec web python scripts/seed_demo_data.py

# Access the services:
# - API: http://localhost:8000/api/v1/
# - API Docs: http://localhost:8000/api/v1/docs/
# - Admin: http://localhost:8000/admin/
# - PgAdmin: http://localhost:5050/
```

### Option 2: Local Development

```bash
# Install C dependencies (Ubuntu/Debian)
sudo apt-get install build-essential cmake libssl-dev

# Build C modules
cd native
mkdir build && cd build
cmake ..
make
cd ../..

# Build Python extension
cd native
pip install -e .
cd ..

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements/dev.txt

# Setup environment
cp docker/.env.example .env
# Edit .env with your local PostgreSQL credentials

# Run migrations
cd backend
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load demo data
python scripts/seed_demo_data.py

# Run development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A config worker -l info
```

## 🧪 Running Tests

### All Tests (Docker)
```bash
docker compose -f docker/docker-compose.yml exec web make test
```

### C Module Tests
```bash
cd native/build
ctest --output-on-failure

# With Valgrind (memory leak detection)
ctest -T memcheck
```

### Django Tests
```bash
cd backend
pytest --cov=apps --cov-report=html --cov-report=term
```

### Linting & Type Checking
```bash
make lint        # Run all linters
make format      # Auto-format code
```

## 📊 Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | - | Yes |
| `DJANGO_DEBUG` | Debug mode | `False` | No |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` | No |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes (prod) |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` | Yes |
| `CELERY_BROKER_URL` | Celery broker | Same as `REDIS_URL` | Yes |
| `JWT_ACCESS_TOKEN_LIFETIME` | Access token expiry | `15` (minutes) | No |
| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token expiry | `7` (days) | No |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |

## 👤 Demo Users

After running `seed_demo_data.py`, the following users are available:

| Username | Password | Role | Capabilities |
|----------|----------|------|--------------|
| `admin` | `admin123!` | Superuser | Full system access |
| `dr.smith` | `doctor123!` | Doctor | Clinical operations |
| `nurse.jane` | `nurse123!` | Nurse | Patient care |
| `lab.tech` | `lab123!` | Lab Tech | Lab results entry |
| `billing.clerk` | `billing123!` | Billing | Invoice management |

**⚠️ Change these passwords in production!**

## 📖 API Documentation

### Authentication

All endpoints (except `/auth/login` and health checks) require JWT authentication:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "dr.smith", "password": "doctor123!"}'

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use access token in subsequent requests
curl -X GET http://localhost:8000/api/v1/patients/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Key Endpoints

- **Auth**: `/api/v1/auth/` - login, refresh, logout, me
- **Patients**: `/api/v1/patients/` - CRUD, search, bulk import
- **Appointments**: `/api/v1/appointments/` - scheduling, check-in, reschedule
- **Encounters**: `/api/v1/encounters/` - clinical visits, diagnoses
- **Orders**: `/api/v1/orders/` - lab/radiology orders
- **Labs**: `/api/v1/labs/` - result entry and queries
- **Medications**: `/api/v1/medications/` - medication catalog
- **Prescriptions**: `/api/v1/prescriptions/` - e-prescribing
- **Billing**: `/api/v1/billing/` - invoices, payments
- **Insurance**: `/api/v1/insurance/` - policy management
- **Audit**: `/api/v1/audit/` - audit log queries
- **Health**: `/health/`, `/ping/` - service health

Full interactive documentation: **http://localhost:8000/api/v1/docs/**

## 🏛️ Database Schema

The system uses a normalized PostgreSQL schema with the following core entities:

- **Patient**: Demographics, MRN, PII pseudonymization tokens
- **Staff**: Employees with roles and departments
- **Appointment**: Scheduling with status tracking
- **Encounter**: Clinical visits linking patient, staff, diagnoses
- **Order**: Lab/radiology/consult requests
- **LabResult**: LOINC-coded results with reference ranges
- **Medication**: Drug catalog with ATC codes
- **Prescription**: Dosing instructions linked to encounters
- **BillingInvoice**: DRG/ICD-calculated charges
- **InsurancePolicy**: Coverage information
- **AuditLog**: Complete change tracking (partitioned by month)

See `docs/database.md` for ER diagrams and optimization details.

## 🔒 Security Features

- **JWT with short-lived tokens** and refresh mechanism
- **PII pseudonymization** via C-accelerated crypto (AES-GCM)
- **Field-level encryption** for sensitive data
- **RBAC + ABAC**: Compiled policy evaluation in C for performance
- **Comprehensive audit logging** of all mutations
- **Rate limiting** on authentication and write endpoints
- **Input validation** via HL7/FHIR validators in C
- **OWASP ASVS aligned** (see `docs/operations.md`)
- **No hardcoded secrets** - all via environment variables
- **SQL injection protection** via Django ORM
- **XSS protection** via Django defaults and DRF

## 🛠️ Development

### Project Structure

```
Hospital/
├── LICENSE                  # Custom commercial license (Immanuel Njogu)
├── README.md               # This file
├── CONTRIBUTING.md         # Contribution guidelines
├── CODE_OF_CONDUCT.md      # Community standards
├── Makefile                # Common development tasks
├── .pre-commit-config.yaml # Git hooks for quality
├── docker/                 # Docker configurations
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── .github/workflows/      # CI/CD pipelines
│   ├── ci.yml
│   └── release.yml
├── backend/                # Django project
│   ├── manage.py
│   ├── config/            # Settings and routing
│   ├── apps/              # Domain applications
│   │   ├── core/          # Common utilities
│   │   ├── users/         # Authentication
│   │   ├── patients/      # Patient management
│   │   ├── appointments/  # Scheduling
│   │   ├── encounters/    # Clinical visits
│   │   ├── orders/        # Order management
│   │   ├── labs/          # Lab results
│   │   ├── medications/   # Drug catalog
│   │   ├── billing/       # Invoicing
│   │   ├── insurance/     # Coverage
│   │   └── audit/         # Audit logs
│   ├── requirements/      # Python dependencies
│   ├── scripts/           # Utility scripts
│   └── tests/             # Django tests
├── native/                 # C modules
│   ├── CMakeLists.txt
│   ├── include/           # C headers
│   ├── src/               # C implementations
│   ├── python/            # CPython extensions
│   ├── tests/             # C unit tests
│   ├── setup.py           # Python extension build
│   └── pyproject.toml
└── docs/                   # Documentation
    ├── architecture.md
    ├── api.md
    ├── database.md
    ├── operations.md
    └── progress.md
```

### Common Commands (via Makefile)

```bash
make setup          # Initial project setup
make build          # Build C modules and Python packages
make test           # Run all tests (C + Python)
make test-c         # Run C tests only
make test-python    # Run Python tests only
make lint           # Run all linters
make format         # Auto-format all code
make run            # Start development server
make seed           # Load demo data
make docker-up      # Start Docker services
make docker-down    # Stop Docker services
make migrations     # Generate Django migrations
make migrate        # Apply migrations
make clean          # Clean build artifacts
```

### Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

Hooks include: black, isort, flake8, mypy, clang-format, trailing whitespace, YAML checks.

## 📈 Performance Considerations

- **C modules** handle performance-critical paths (validation, crypto, billing calculations)
- **Minimal GIL contention** via `Py_BEGIN_ALLOW_THREADS` in C extensions
- **Database indexes** on all foreign keys, unique constraints, and query paths
- **Partial indexes** for active records (e.g., non-completed appointments)
- **GIN indexes** for JSONB and array fields (diagnosis codes, audit snapshots)
- **Partitioned audit logs** by month for efficient querying
- **Cursor-based pagination** for large result sets
- **Redis caching** for frequently accessed data (optional, not yet implemented)
- **Celery** for async operations (bulk imports, reports)

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Note**: This project is copyright Immanuel Njogu. By contributing, you agree that:
1. Non-commercial use is freely permitted with attribution
2. Commercial use requires written permission from the copyright holder
3. Your contributions will be licensed under the same terms

See [LICENSE](LICENSE) for full details.

## 📄 License

Copyright (c) 2025, Immanuel Njogu. All rights reserved.

This software is available for non-commercial use under a custom license. Commercial use requires explicit written permission from Immanuel Njogu.

See [LICENSE](LICENSE) file for complete terms.

## 🙏 Acknowledgments

- Built with Django, Django REST Framework, and CPython extensions
- Uses PostgreSQL for reliable data storage
- Security patterns inspired by OWASP ASVS and HL7 FHIR standards

## 📞 Contact

**Author**: Immanuel Njogu

For commercial licensing inquiries, please contact the author.

---

**Built with ❤️ for modern healthcare infrastructure**

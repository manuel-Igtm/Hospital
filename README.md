# Hospital Backend System (MVP)# Hospital Backend System (MVP)# Hospital Backend System



A Django-based hospital management system with secure C modules for cryptography and HL7 validation.



[![CI](https://github.com/manuel-Igtm/Hospital/actions/workflows/ci.yml/badge.svg)](https://github.com/manuel-Igtm/Hospital/actions/workflows/ci.yml)A modern, enterprise-ready hospital management backend built with Django and high-performance C modules. This MVP provides secure, scalable APIs for user authentication, patient management, and laboratory orders with HL7 validation.A modern, enterprise-ready hospital management backend built with Django and high-performance C modules. This system provides secure, scalable APIs for patient management, appointments, encounters, laboratory orders, billing, and comprehensive audit logging.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)

[![Django 5.0](https://img.shields.io/badge/django-5.0-green.svg)](https://www.djangoproject.com/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ MVP Features## 📚 Quick Links

## Features



### MVP Scope

- **Authentication**: JWT-based with role-based access control- **User Authentication**: JWT-based auth with role-based access control (RBAC)- **[⚡ QUICKSTART](QUICKSTART.md)** - Get running in 5 minutes

- **Patient Management**: CRUD operations with search and history tracking

- **Lab Orders**: Create, track, and manage lab orders with results- **Patient Management**: CRUD operations with encrypted SSN using AES-256-GCM- **[📖 PROJECT SUMMARY](PROJECT_SUMMARY.md)** - Complete overview



### Technical Highlights- **Lab Orders**: Full workflow management with HL7 v2 message validation- **[🐳 Docker Guide](docker/README.md)** - Containerized deployment

- **C Modules**: Native cryptography (AES-256-GCM) and HL7v2.x validation

- **Security**: HIPAA-compliant encryption, audit logging- **[💻 Dev Guide](backend/README.md)** - Local development setup

- **CI/CD**: GitHub Actions, Jenkins pipeline, Kubernetes manifests

- **Testing**: 82% code coverage, 57 tests## 🏗️ Architecture- **[📊 Progress Tracking](docs/progress.md)** - Weekly updates



## Quick Start- **[🤝 Contributing](CONTRIBUTING.md)** - How to contribute



### Prerequisites**Multi-language approach:**

- Python 3.13+

- PostgreSQL 14+- **C modules**: High-performance components for data validation (HL7) and cryptographic operations (AES-GCM)## 🏗️ Architecture

- Docker (optional)

- GCC and OpenSSL development libraries (for C modules)- **Django (Python 3.13+)**: REST APIs, business logic, authentication, admin interface



### Installation- **PostgreSQL**: Primary production database**Multi-language approach:**



```bash- **SQLite**: In-memory testing- **C modules**: High-performance components for data validation (HL7/FHIR), cryptographic operations (AES-GCM, PHI pseudonymization), ABAC authorization policy evaluation, and billing calculations

# Clone the repository

git clone https://github.com/manuel-Igtm/Hospital.git- **Django (Python 3.12+)**: REST APIs, business logic, authentication, admin interface, and orchestration

cd Hospital

## 🚀 Quick Start- **PostgreSQL**: Primary production database with optimized indexes and partitioning

# Create virtual environment

python -m venv venv- **Redis + Celery**: Async task processing

source venv/bin/activate  # On Windows: venv\Scripts\activate

### Prerequisites- **ASGI via Uvicorn/Gunicorn**: Modern async-capable deployment

# Install dependencies

pip install -r backend/requirements/dev.txt



# Build C modules (optional, provides AES encryption and HL7 validation)- Python 3.12+ ## ✨ Key Features

cd native && pip install -e . && cd ..

- Git

# Set up environment variables

cp backend/.env.example backend/.env- **Complete Patient Management**: MRN-based patient records with PII protection

# Edit .env with your database credentials

### Local Development- **Appointment Scheduling**: Full lifecycle with calendar queries and status tracking

# Run migrations

cd backend- **Clinical Encounters**: Visit documentation with diagnosis codes, orders, and notes

python manage.py migrate

```bash- **Laboratory Orders**: HL7-validated lab results with LOINC coding

# Create superuser

python manage.py createsuperuser# Clone the repository- **E-Prescribing**: Medication management with ATC codes and dosing



# Run development servergit clone https://github.com/manuel-Igtm/Hospital.git- **Billing & Insurance**: Automated invoice generation with DRG/ICD-based calculations

python manage.py runserver

```cd Hospital/backend- **Comprehensive Audit**: Every write operation logged with actor, timestamp, and IP



### Docker Deployment- **JWT Authentication**: Secure token-based auth with refresh and blacklist



```bash# Create virtual environment- **RBAC + ABAC**: Role-based and attribute-based access control via compiled C policies

# Build and run with Docker Compose

docker compose up -dpython3 -m venv venv- **OpenAPI Documentation**: Auto-generated Swagger UI with examples



# Or build image directlysource venv/bin/activate  # On Windows: venv\Scripts\activate

docker build -t hospital-backend .

docker run -p 8000:8000 hospital-backend## 🚀 Quick Start

```

# Install dependencies

## API Endpoints

pip install -r requirements/dev.txt### Prerequisites

### Authentication

| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/api/v1/auth/register/` | Register new user |# Run migrations- Docker & Docker Compose (recommended) OR

| POST | `/api/v1/auth/login/` | Obtain JWT tokens |

| POST | `/api/v1/auth/refresh/` | Refresh access token |python manage.py migrate- Python 3.12+, PostgreSQL 14+, Redis, CMake, GCC/Clang, OpenSSL dev libraries

| POST | `/api/v1/auth/logout/` | Blacklist refresh token |

| GET | `/api/v1/auth/me/` | Current user profile |



### Patients# Create superuser### Option 1: Docker (Recommended)

| Method | Endpoint | Description |

|--------|----------|-------------|python manage.py createsuperuser

| GET | `/api/v1/patients/` | List patients (paginated) |

| POST | `/api/v1/patients/` | Create patient |```bash

| GET | `/api/v1/patients/{id}/` | Get patient details |

| PUT | `/api/v1/patients/{id}/` | Update patient |# Run development server# Clone the repository

| DELETE | `/api/v1/patients/{id}/` | Delete patient |

| GET | `/api/v1/patients/{id}/history/` | Patient history |python manage.py runservergit clone https://github.com/manuel-Igtm/Hospital.git



### Lab Orderscd Hospital

| Method | Endpoint | Description |

|--------|----------|-------------|# Access the services:

| GET | `/api/v1/lab-orders/` | List lab orders |

| POST | `/api/v1/lab-orders/` | Create lab order |# - API: http://localhost:8000/api/v1/# Copy environment template

| GET | `/api/v1/lab-orders/{id}/` | Get order details |

| PATCH | `/api/v1/lab-orders/{id}/` | Update order/results |# - Admin: http://localhost:8000/admin/cp docker/.env.example docker/.env

| GET | `/api/v1/lab-orders/patient/{id}/` | Orders by patient |

```

## User Roles

# Start all services

| Role | Permissions |

|------|-------------|## 🧪 Running Testsdocker compose -f docker/docker-compose.yml up -d

| Admin | Full system access |

| Doctor | View patients, create/view orders, view results |

| Nurse | View patients, view orders |

| Lab Technician | View orders, enter results |```bash# Wait for database to be ready, then run migrations



## Project Structurecd backenddocker compose -f docker/docker-compose.yml exec web python manage.py migrate



```source venv/bin/activate

Hospital/

├── backend/# Create superuser

│   ├── apps/

│   │   ├── core/          # Shared utilities, encryption# Run all tests with coveragedocker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser

│   │   ├── users/         # Authentication, roles

│   │   ├── patients/      # Patient managementpytest

│   │   └── lab_orders/    # Lab order tracking

│   ├── config/            # Django settings# Load demo data

│   └── requirements/      # Dependencies

├── native/# Run specific test filedocker compose -f docker/docker-compose.yml exec web python scripts/seed_demo_data.py

│   ├── libcutils/         # AES-256-GCM encryption

│   └── libhl7val/         # HL7v2.x validationpytest tests/test_users.py -v

├── k8s/                   # Kubernetes manifests

├── docker-compose.yml# Access the services:

├── Dockerfile

└── Jenkinsfile# Run with verbose output# - API: http://localhost:8000/api/v1/

```

pytest -v --tb=long# - API Docs: http://localhost:8000/api/v1/docs/

## Environment Variables

```# - Admin: http://localhost:8000/admin/

| Variable | Description | Default |

|----------|-------------|---------|# - PgAdmin: http://localhost:5050/

| `DATABASE_URL` | PostgreSQL connection string | - |

| `SECRET_KEY` | Django secret key | - |**Current test status: 57 tests passing, 82% coverage**```

| `DEBUG` | Debug mode | `False` |

| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost` |

| `CORS_ALLOWED_ORIGINS` | CORS origins | - |

| `SENTRY_DSN` | Sentry error tracking | - |## 📊 API Endpoints### Option 2: Local Development



## Testing



```bash### Authentication (`/api/v1/auth/`)```bash

cd backend

pytest --cov=apps --cov-report=html# Install C dependencies (Ubuntu/Debian)

```

| Endpoint | Method | Description | Auth Required |sudo apt-get install build-essential cmake libssl-dev

## Contributing

|----------|--------|-------------|---------------|

1. Fork the repository

2. Create a feature branch (`git checkout -b feature/amazing-feature`)| `/login/` | POST | Get JWT tokens | No |# Build C modules

3. Commit your changes (`git commit -m 'Add amazing feature'`)

4. Push to the branch (`git push origin feature/amazing-feature`)| `/refresh/` | POST | Refresh access token | No |cd native

5. Open a Pull Request

| `/logout/` | POST | Blacklist refresh token | Yes |mkdir build && cd build

## License

| `/me/` | GET | Get current user info | Yes |cmake ..

MIT License - see [LICENSE](LICENSE) for details.

| `/me/` | PATCH | Update current user | Yes |make

## Author

| `/change-password/` | POST | Change password | Yes |cd ../..

**Immanuel Njogu** - [GitHub](https://github.com/manuel-Igtm)



---

### Users (`/api/v1/users/`) - Admin only# Build Python extension

© 2025 Immanuel Njogu. All rights reserved.

cd native

| Endpoint | Method | Description |pip install -e .

|----------|--------|-------------|cd ..

| `/` | GET | List all users |

| `/` | POST | Create user |# Create virtual environment

| `/{id}/` | GET | Get user details |python3.12 -m venv venv

| `/{id}/` | PUT/PATCH | Update user |source venv/bin/activate

| `/{id}/` | DELETE | Deactivate user |

| `/{id}/activate/` | POST | Reactivate user |# Install Python dependencies

pip install -r backend/requirements/dev.txt

### Patients (`/api/v1/patients/`)

# Setup environment

| Endpoint | Method | Description | Permissions |cp docker/.env.example .env

|----------|--------|-------------|-------------|# Edit .env with your local PostgreSQL credentials

| `/` | GET | List patients | All staff |

| `/` | POST | Create patient | Clinical staff |# Run migrations

| `/{id}/` | GET | Get patient details | All staff |cd backend

| `/{id}/` | PUT/PATCH | Update patient | Clinical staff |python manage.py migrate

| `/{id}/` | DELETE | Deactivate patient | Admin only |

| `/find_by_ssn/` | GET | Find by SSN | All staff |# Create superuser

python manage.py createsuperuser

### Lab Orders (`/api/v1/lab/`)

# Load demo data

| Endpoint | Method | Description | Permissions |python scripts/seed_demo_data.py

|----------|--------|-------------|-------------|

| `/test-types/` | GET | List test catalog | All |# Run development server

| `/test-types/` | POST | Create test type | Admin |python manage.py runserver

| `/orders/` | GET | List lab orders | All staff |

| `/orders/` | POST | Create order | Doctor/Nurse |# In another terminal, start Celery worker

| `/orders/{id}/collect/` | POST | Mark specimen collected | Lab Tech |celery -A config worker -l info

| `/orders/{id}/cancel/` | POST | Cancel order | Doctor |```

| `/results/` | GET | List results | All staff |

| `/results/` | POST | Submit result | Lab Tech |## 🧪 Running Tests

| `/results/{id}/review/` | POST | Review result | Doctor |

### All Tests (Docker)

## 👤 User Roles```bash

docker compose -f docker/docker-compose.yml exec web make test

| Role | Code | Capabilities |```

|------|------|--------------|

| Administrator | `ADMIN` | Full system access |### C Module Tests

| Doctor | `DOCTOR` | Patient care, create orders, review results |```bash

| Nurse | `NURSE` | Patient care, create orders |cd native/build

| Lab Technician | `LAB_TECH` | Collect specimens, enter results |ctest --output-on-failure

| Receptionist | `RECEPTIONIST` | View patients (read-only) |

# With Valgrind (memory leak detection)

## 🔐 Authentication Flowctest -T memcheck

```

```bash

# 1. Login to get tokens### Django Tests

curl -X POST http://localhost:8000/api/v1/auth/login/ \```bash

  -H "Content-Type: application/json" \cd backend

  -d '{"email": "admin@hospital.test", "password": "AdminPass123!"}'pytest --cov=apps --cov-report=html --cov-report=term

```

# Response:

# {### Linting & Type Checking

#   "access": "eyJ0eXAiOiJKV1Q...",```bash

#   "refresh": "eyJ0eXAiOiJKV1Q...",make lint        # Run all linters

#   "user": {"email": "admin@hospital.test", "role": "ADMIN", ...}make format      # Auto-format code

# }```



# 2. Use access token in subsequent requests## 📊 Environment Variables

curl -X GET http://localhost:8000/api/v1/patients/ \

  -H "Authorization: Bearer eyJ0eXAiOiJKV1Q..."| Variable | Description | Default | Required |

|----------|-------------|---------|----------|

# 3. Refresh token when access token expires (15 min)| `DJANGO_SECRET_KEY` | Django secret key | - | Yes |

curl -X POST http://localhost:8000/api/v1/auth/refresh/ \| `DJANGO_DEBUG` | Debug mode | `False` | No |

  -H "Content-Type: application/json" \| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` | No |

  -d '{"refresh": "eyJ0eXAiOiJKV1Q..."}'| `DATABASE_URL` | PostgreSQL connection string | - | Yes (prod) |

| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` | Yes |

# 4. Logout (blacklist refresh token)| `CELERY_BROKER_URL` | Celery broker | Same as `REDIS_URL` | Yes |

curl -X POST http://localhost:8000/api/v1/auth/logout/ \| `JWT_ACCESS_TOKEN_LIFETIME` | Access token expiry | `15` (minutes) | No |

  -H "Authorization: Bearer eyJ0eXAiOiJKV1Q..." \| `JWT_REFRESH_TOKEN_LIFETIME` | Refresh token expiry | `7` (days) | No |

  -H "Content-Type: application/json" \| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` | No |

  -d '{"refresh": "eyJ0eXAiOiJKV1Q..."}'| `LOG_LEVEL` | Logging level | `INFO` | No |

```

## 👤 Demo Users

## 🗄️ Project Structure

After running `seed_demo_data.py`, the following users are available:

```

Hospital/| Username | Password | Role | Capabilities |

├── LICENSE                    # Commercial license (Immanuel Njogu)|----------|----------|------|--------------|

├── README.md                  # This file| `admin` | `admin123!` | Superuser | Full system access |

├── Makefile                   # Common development tasks| `dr.smith` | `doctor123!` | Doctor | Clinical operations |

├── .github/workflows/         # CI/CD pipelines| `nurse.jane` | `nurse123!` | Nurse | Patient care |

│   └── ci.yml| `lab.tech` | `lab123!` | Lab Tech | Lab results entry |

├── backend/                   # Django project| `billing.clerk` | `billing123!` | Billing | Invoice management |

│   ├── manage.py

│   ├── pyproject.toml         # Python project config**⚠️ Change these passwords in production!**

│   ├── config/                # Settings and routing

│   │   ├── settings/## 📖 API Documentation

│   │   │   ├── base.py        # Common settings

│   │   │   ├── dev.py         # Development settings### Authentication

│   │   │   ├── prod.py        # Production settings

│   │   │   └── test.py        # Test settingsAll endpoints (except `/auth/login` and health checks) require JWT authentication:

│   │   └── urls.py

│   ├── apps/```bash

│   │   ├── core/              # Common utilities, encryption# Login

│   │   ├── users/             # Authentication & RBACcurl -X POST http://localhost:8000/api/v1/auth/login/ \

│   │   ├── patients/          # Patient management  -H "Content-Type: application/json" \

│   │   └── lab_orders/        # Lab order workflow  -d '{"username": "dr.smith", "password": "doctor123!"}'

│   ├── requirements/

│   │   ├── base.txt# Response

│   │   ├── dev.txt{

│   │   ├── prod.txt  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",

│   │   └── test.txt  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."

│   └── tests/                 # Test suite}

│       ├── conftest.py        # Pytest fixtures

│       ├── test_users.py# Use access token in subsequent requests

│       ├── test_patients.pycurl -X GET http://localhost:8000/api/v1/patients/ \

│       └── test_lab_orders.py  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."

├── docker/                    # Docker configurations```

│   ├── Dockerfile

│   ├── docker-compose.yml### Key Endpoints

│   └── .env.example

└── native/                    # C modules (optional)- **Auth**: `/api/v1/auth/` - login, refresh, logout, me

    ├── CMakeLists.txt- **Patients**: `/api/v1/patients/` - CRUD, search, bulk import

    ├── include/- **Appointments**: `/api/v1/appointments/` - scheduling, check-in, reschedule

    └── src/- **Encounters**: `/api/v1/encounters/` - clinical visits, diagnoses

```- **Orders**: `/api/v1/orders/` - lab/radiology orders

- **Labs**: `/api/v1/labs/` - result entry and queries

## 📈 Lab Order Workflow- **Medications**: `/api/v1/medications/` - medication catalog

- **Prescriptions**: `/api/v1/prescriptions/` - e-prescribing

```- **Billing**: `/api/v1/billing/` - invoices, payments

[PENDING] → [COLLECTED] → [RESULTED] → [REVIEWED]- **Insurance**: `/api/v1/insurance/` - policy management

     ↓- **Audit**: `/api/v1/audit/` - audit log queries

[CANCELLED]- **Health**: `/health/`, `/ping/` - service health

```

Full interactive documentation: **http://localhost:8000/api/v1/docs/**

1. **PENDING**: Order created by doctor/nurse

2. **COLLECTED**: Specimen collected by lab tech## 🏛️ Database Schema

3. **RESULTED**: Results entered by lab tech

4. **REVIEWED**: Results reviewed by doctorThe system uses a normalized PostgreSQL schema with the following core entities:

5. **CANCELLED**: Order cancelled (only from PENDING state)

- **Patient**: Demographics, MRN, PII pseudonymization tokens

## 🔒 Security Features- **Staff**: Employees with roles and departments

- **Appointment**: Scheduling with status tracking

- **JWT Authentication** with 15-minute access tokens and 7-day refresh tokens- **Encounter**: Clinical visits linking patient, staff, diagnoses

- **Token Blacklisting** on logout- **Order**: Lab/radiology/consult requests

- **AES-256-GCM Encryption** for sensitive data (SSN)- **LabResult**: LOINC-coded results with reference ranges

- **Role-Based Access Control** (RBAC) with 5 predefined roles- **Medication**: Drug catalog with ATC codes

- **Input Validation** with DRF serializers- **Prescription**: Dosing instructions linked to encounters

- **SQL Injection Protection** via Django ORM- **BillingInvoice**: DRG/ICD-calculated charges

- **InsurancePolicy**: Coverage information

## 🛠️ Environment Variables- **AuditLog**: Complete change tracking (partitioned by month)



| Variable | Description | Default |See `docs/database.md` for ER diagrams and optimization details.

|----------|-------------|---------|

| `DJANGO_SECRET_KEY` | Django secret key | *required* |## 🔒 Security Features

| `DJANGO_DEBUG` | Debug mode | `False` |

| `DATABASE_URL` | PostgreSQL connection | SQLite for dev |- **JWT with short-lived tokens** and refresh mechanism

| `ENCRYPTION_KEY` | 32-byte key for AES-GCM | *generated* |- **PII pseudonymization** via C-accelerated crypto (AES-GCM)

- **Field-level encryption** for sensitive data

## 📄 License- **RBAC + ABAC**: Compiled policy evaluation in C for performance

- **Comprehensive audit logging** of all mutations

Copyright (c) 2025, Immanuel Njogu. All rights reserved.- **Rate limiting** on authentication and write endpoints

- **Input validation** via HL7/FHIR validators in C

This software is available for non-commercial use. Commercial use requires explicit written permission from Immanuel Njogu.- **OWASP ASVS aligned** (see `docs/operations.md`)

- **No hardcoded secrets** - all via environment variables

See [LICENSE](LICENSE) for complete terms.- **SQL injection protection** via Django ORM

- **XSS protection** via Django defaults and DRF

---

## 🛠️ Development

**Built with ❤️ for modern healthcare infrastructure**

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

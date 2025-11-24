# Hospital Backend MVP - Architecture & Scope

**Version**: 1.0 (MVP)  
**Author**: Immanuel Njogu  
**Date**: November 24, 2025  
**License**: Custom Commercial (see LICENSE)

---

## 🎯 MVP Scope

**Goal**: Build a focused, production-quality hospital backend demonstrating:
- High-performance C integration with Django
- Real-world healthcare workflows
- Enterprise-grade security and testing

**Non-Goal**: Build every hospital feature imaginable

---

## 📦 MVP Features (3 Core Areas)

### 1. Authentication & Authorization ✅

**What:**
- JWT-based authentication (access + refresh tokens)
- Role-based access control (Admin, Doctor, Nurse, Lab Tech)
- User management API

**Why MVP:**
- Required for all other features
- Demonstrates security best practices
- Shows RBAC implementation

**Endpoints:**
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login (returns JWT tokens)
- `POST /api/v1/auth/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout (blacklist token)
- `GET /api/v1/auth/me/` - Get current user info
- `GET/POST/PUT/DELETE /api/v1/users/` - User CRUD (admin only)

---

### 2. Patient Management ✅

**What:**
- Patient CRUD with encrypted PII
- MRN (Medical Record Number) generation
- Search and filtering
- Role-based access (doctors/nurses can view, admin can manage)

**Why MVP:**
- Core entity in any hospital system
- Demonstrates C module integration (encryption)
- Shows data protection (HIPAA-like)

**C Module Integration:**
- `libcutils.aes_gcm_encrypt()` - Encrypt patient SSN
- `libcutils.aes_gcm_decrypt()` - Decrypt SSN for authorized users
- `libcutils.sha256()` - Generate PII tokens for pseudonymization

**Endpoints:**
- `GET /api/v1/patients/` - List patients (paginated, filtered)
- `POST /api/v1/patients/` - Create patient
- `GET /api/v1/patients/{id}/` - Get patient details
- `PUT /api/v1/patients/{id}/` - Update patient
- `DELETE /api/v1/patients/{id}/` - Soft delete patient
- `GET /api/v1/patients/search/?q=<query>` - Search patients

**Database Schema:**
```sql
CREATE TABLE patients (
    id BIGSERIAL PRIMARY KEY,
    mrn VARCHAR(20) UNIQUE NOT NULL,  -- Medical Record Number
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    encrypted_ssn BYTEA,  -- AES-256-GCM encrypted
    pii_token VARCHAR(64),  -- SHA-256 hash for pseudonymization
    created_by_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL  -- Soft delete
);

CREATE INDEX idx_patients_mrn ON patients(mrn);
CREATE INDEX idx_patients_pii_token ON patients(pii_token);
CREATE INDEX idx_patients_deleted_at ON patients(deleted_at) WHERE deleted_at IS NULL;
```

---

### 3. Lab Orders & Results Workflow ✅

**What:**
- Lab test ordering (doctors can order)
- HL7 v2.x result upload (lab techs can upload)
- C module validation of HL7 messages
- Status workflow (Ordered → In-Progress → Completed → Reviewed)

**Why MVP:**
- Demonstrates realistic healthcare workflow
- Shows second C module integration (HL7 validation)
- Connects multiple actors (doctor, lab tech, patient)

**C Module Integration:**
- `libhl7val.validate_segment()` - Validate HL7 v2.x message structure
- `libhl7val.extract_field()` - Parse HL7 fields efficiently

**Endpoints:**
- `GET /api/v1/lab-orders/` - List orders (filtered by patient/status)
- `POST /api/v1/lab-orders/` - Create order (doctors only)
- `GET /api/v1/lab-orders/{id}/` - Get order details
- `PUT /api/v1/lab-orders/{id}/status/` - Update status
- `POST /api/v1/lab-orders/{id}/results/` - Upload HL7 results (lab tech only)
- `GET /api/v1/lab-orders/{id}/results/` - Get results

**Database Schema:**
```sql
CREATE TABLE lab_orders (
    id BIGSERIAL PRIMARY KEY,
    patient_id BIGINT REFERENCES patients(id) ON DELETE CASCADE,
    ordered_by_id BIGINT REFERENCES users(id),
    test_code VARCHAR(50) NOT NULL,  -- LOINC code
    test_name VARCHAR(200) NOT NULL,
    priority VARCHAR(20) DEFAULT 'ROUTINE',  -- STAT, URGENT, ROUTINE
    status VARCHAR(20) DEFAULT 'ORDERED',  -- ORDERED, IN_PROGRESS, COMPLETED, REVIEWED
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE lab_results (
    id BIGSERIAL PRIMARY KEY,
    lab_order_id BIGINT REFERENCES lab_orders(id) ON DELETE CASCADE,
    uploaded_by_id BIGINT REFERENCES users(id),
    hl7_message TEXT NOT NULL,  -- Raw HL7 v2.x message
    result_value VARCHAR(200),
    result_unit VARCHAR(50),
    reference_range VARCHAR(100),
    abnormal_flag VARCHAR(10),  -- N (normal), H (high), L (low)
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lab_orders_patient ON lab_orders(patient_id);
CREATE INDEX idx_lab_orders_status ON lab_orders(status);
CREATE INDEX idx_lab_results_order ON lab_results(lab_order_id);
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Client (Web/Mobile)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS + JWT
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django REST API (Gunicorn)                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Apps: users, patients, lab_orders                    │  │
│  │  Auth: JWT (djangorestframework-simplejwt)            │  │
│  │  Permissions: IsDoctor, IsNurse, IsLabTech, IsAdmin   │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Core Utils: C Module Wrappers                        │  │
│  │  - encrypt_pii() → libcutils.aes_gcm_encrypt()        │  │
│  │  - validate_hl7() → libhl7val.validate_segment()      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────┬───────────────────────────┬───────────────────────────┘
      │ Django ORM                │ C FFI
      ▼                           ▼
┌─────────────┐            ┌─────────────┐
│ PostgreSQL  │            │ C Modules   │
│  - users    │            │ - libcutils │
│  - patients │            │ - libhl7val │
│  - orders   │            └─────────────┘
│  - results  │
└─────────────┘
```

---

## 🔐 Security Features

### Authentication
- **JWT tokens** with 15-min access, 7-day refresh
- **Token blacklist** on logout
- **Password hashing** with Django's PBKDF2

### Authorization
- **Role-based permissions** (4 roles)
- **Object-level permissions** (can only access own patients)

### Data Protection
- **AES-256-GCM encryption** for SSN (via C module)
- **SHA-256 pseudonymization** for PII tokens
- **HTTPS enforcement** in production
- **Secrets via environment variables** (12-factor)

### Input Validation
- **DRF serializers** for Python-level validation
- **C module validation** for HL7 messages
- **SQL injection protection** via Django ORM

---

## 📂 Project Structure (MVP)

```
Hospital/
├── LICENSE                      # Custom commercial license
├── README.md                    # Getting started guide
├── QUICKSTART.md               # 5-min setup
├── Makefile                     # Dev automation
│
├── native/                      # C Modules (MVP: 2 libs)
│   ├── CMakeLists.txt
│   ├── include/
│   │   ├── libcutils.h         # Encryption utilities
│   │   └── libhl7val.h         # HL7 validation
│   ├── src/
│   │   ├── libcutils.c
│   │   └── libhl7val.c
│   ├── python/                 # CPython bindings
│   │   ├── _cutils.c
│   │   └── _hl7val.c
│   ├── tests/                  # C unit tests
│   │   ├── test_cutils.c
│   │   └── test_hl7val.c
│   └── setup.py
│
├── backend/                     # Django Backend (MVP: 3 apps)
│   ├── manage.py
│   ├── pyproject.toml          # uv package management
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── dev.py
│   │   │   ├── test.py
│   │   │   └── prod.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── core/               # Shared utilities
│   │   │   ├── models.py       # Mixins (Timestamp, SoftDelete)
│   │   │   ├── utils.py        # C module wrappers
│   │   │   └── permissions.py  # Custom permissions
│   │   ├── users/              # Authentication
│   │   │   ├── models.py       # Custom User with roles
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── tests/
│   │   ├── patients/           # Patient management
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── tests/
│   │   └── lab_orders/         # Lab workflow
│   │       ├── models.py       # LabOrder + LabResult
│   │       ├── serializers.py
│   │       ├── views.py
│   │       └── tests/
│   └── pytest.ini
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml      # web + postgres + redis
│   └── .env.example
│
├── .github/
│   └── workflows/
│       └── ci.yml              # Build, test, lint
│
└── docs/
    ├── MVP_ARCHITECTURE.md     # This file
    ├── API.md                  # API documentation
    └── DEPLOYMENT.md           # Docker deployment
```

---

## 🧪 Testing Strategy

### C Modules
- **CTest** unit tests for each function
- **Valgrind** memory leak checks
- **Coverage target**: ≥80%

### Django Apps
- **pytest** with pytest-django
- **factory_boy** for test data
- **Coverage target**: ≥85%
- Test types:
  - Model tests (validation, methods)
  - Serializer tests (validation, field behavior)
  - View tests (permissions, status codes, responses)
  - Integration tests (full workflows)

### CI/CD
- **GitHub Actions** runs on every push
- Build C modules
- Run C tests
- Run Python tests
- Lint (black, isort, mypy)
- Security scan (Bandit)

---

## 🚀 Development Workflow

### Setup (5 minutes)
```bash
# Option 1: Docker (fastest)
cd docker
cp .env.example .env
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Option 2: Local
make setup  # Builds C modules, installs deps, runs migrations
make run    # Starts Django dev server
```

### Development
```bash
make test          # Run all tests
make lint          # Run linters
make format        # Auto-format code
make docker-logs   # View logs
```

### Weekly Contributions
- **Week 1**: ✅ Foundation (C modules, Django structure, Docker)
- **Week 2**: Users + Patients apps
- **Week 3**: Lab orders + results
- **Week 4**: Testing + CI/CD + docs polish

---

## 📊 Success Criteria

### Must Have ✅
- [x] C modules compile and pass tests
- [ ] JWT authentication works
- [ ] Patients CRUD with encrypted SSN
- [ ] Lab orders workflow functional
- [ ] HL7 validation via C module
- [ ] Role-based permissions enforced
- [ ] Docker setup works
- [ ] CI/CD pipeline passes
- [ ] API documented with examples
- [ ] Test coverage ≥85%

### Nice to Have (Post-MVP)
- Appointments scheduling
- Medications/prescriptions
- Billing integration
- Audit logging
- WebSocket notifications
- GraphQL API
- Mobile app

---

## 🎓 What This MVP Demonstrates

### Technical Skills
- **C programming** with OpenSSL integration
- **CPython extensions** with proper GIL handling
- **Django REST Framework** with JWT auth
- **PostgreSQL** schema design
- **Docker** containerization
- **CI/CD** with GitHub Actions
- **Testing** (C + Python, ≥85% coverage)

### System Design
- **Hybrid architecture** (C + Python)
- **Security** (encryption, auth, RBAC)
- **Healthcare domain** knowledge (HL7, LOINC)
- **Clean code** (DRY, SOLID principles)
- **Production-ready** (Docker, env vars, logging)

### Project Management
- **Realistic scope** (MVP, not everything)
- **Weekly contributions** (sustainable pace)
- **Clear documentation** (setup, API, architecture)
- **Open source** (contributions welcome)

---

## 📜 License & Rights

**Copyright © 2025 Immanuel Njogu. All rights reserved.**

- **Non-commercial use**: Free with attribution
- **Commercial use**: Requires written permission from Immanuel Njogu
- **Contributions**: Welcome! Contributors retain rights to their contributions

See [LICENSE](../LICENSE) for full terms.

---

## 🤝 Contributing

**Want to help?**
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Check [docs/TODO.md](TODO.md) for tasks
3. Pick an issue or feature
4. Submit a PR

**Questions?** Open a GitHub discussion or contact Immanuel Njogu.

---

## 📞 Contact

**Immanuel Njogu**  
Email: immanuel@njogu.tech  
GitHub: @manuel-Igtm

---

**Remember**: This is an MVP. Keep it tight, make it work, then iterate. 🚀

**Next Steps**: See [docs/week-2-tasks.md](week-2-tasks.md) for implementation tasks.

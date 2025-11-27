# 🏥 Hospital Management System

<div align="center">

![Hospital Banner](https://img.shields.io/badge/Hospital-Management_System-blue?style=for-the-badge&logo=hospital&logoColor=white)

[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django 5.0](https://img.shields.io/badge/Django-5.0-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-316192?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0+-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![CI](https://github.com/manuel-Igtm/Hospital/actions/workflows/ci.yml/badge.svg)](https://github.com/manuel-Igtm/Hospital/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-113_passing-success?style=flat-square)](https://github.com/manuel-Igtm/Hospital/actions)

**A modern, secure, and scalable hospital backend built with Django and high-performance C modules.**

[📖 Documentation](#-documentation) •
[🚀 Quick Start](#-quick-start) •
[✨ Features](#-features) •
[🔌 API Reference](#-api-reference) •
[🤝 Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Configuration](#-configuration)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The Hospital Management System is an enterprise-ready backend solution for healthcare facilities. It provides secure APIs for managing patients, appointments, laboratory orders, billing, and comprehensive security auditing.

### Why This Project?

| Challenge | Our Solution |
|-----------|--------------|
| 🔒 Data Security | AES-256-GCM encryption, JWT auth, HIPAA-compliant logging |
| ⚡ Performance | High-performance C modules for cryptography & validation |
| 🏗️ Scalability | Microservices-ready architecture with Celery async tasks |
| 📊 Analytics | Real-time dashboards for patients, finances, and operations |
| 💳 Payments | M-Pesa mobile money integration |

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔐 Authentication & Security
- JWT-based authentication with refresh tokens
- Role-Based Access Control (RBAC)
- IP blocking and rate limiting
- Security event logging
- Request audit trails

</td>
<td width="50%">

### 👥 Patient Management
- Complete patient records with MRN
- Medical history tracking
- Encrypted PII storage
- Search and filtering
- Bulk operations

</td>
</tr>
<tr>
<td width="50%">

### 🔬 Laboratory Orders
- Full order lifecycle management
- HL7 v2.x message validation
- Specimen tracking
- Result entry and review
- Test catalog management

</td>
<td width="50%">

### 💰 Billing & Payments
- Automated invoice generation
- M-Pesa STK Push integration
- Payment tracking
- Service catalog
- Financial reporting

</td>
</tr>
<tr>
<td width="50%">

### 📊 Analytics Dashboard
- Patient demographics
- Revenue analytics
- Lab order statistics
- Turnaround time metrics
- Date range filtering

</td>
<td width="50%">

### 🛡️ Security Features
- IP blocking middleware
- Request logging
- Security event tracking
- Rate limiting
- Admin dashboard

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer                            │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌─────────┐     ┌─────────┐     ┌─────────┐
        │  Django │     │  Django │     │  Django │
        │   API   │     │   API   │     │   API   │
        └────┬────┘     └────┬────┘     └────┬────┘
             │               │               │
             └───────────────┼───────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌──────────┐       ┌──────────┐       ┌──────────┐
   │PostgreSQL│       │  Redis   │       │  Celery  │
   │    DB    │       │  Cache   │       │ Workers  │
   └──────────┘       └──────────┘       └──────────┘
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.13, Django 5.0, Django REST Framework |
| **Database** | PostgreSQL 14+ (production), SQLite (development) |
| **Cache/Queue** | Redis 7.0+, Celery 5.3+ |
| **Security** | JWT, AES-256-GCM (C module), bcrypt |
| **Validation** | HL7 v2.x validator (C module) |
| **Testing** | pytest, pytest-django, pytest-cov |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 14+ (or SQLite for development)
- Redis 7.0+ (optional, for caching)
- Docker & Docker Compose (recommended)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/manuel-Igtm/Hospital.git
cd Hospital

# Copy environment template
cp docker/.env.example docker/.env

# Start all services
docker compose -f docker/docker-compose.yml up -d

# Run migrations
docker compose -f docker/docker-compose.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker/docker-compose.yml exec web python manage.py createsuperuser

# Access the API
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/manuel-Igtm/Hospital.git
cd Hospital/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# API available at http://localhost:8000/api/v1/
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication

All endpoints (except login) require JWT authentication:

```bash
# Login to get tokens
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@hospital.test", "password": "AdminPass123!"}'

# Response
{
  "access": "eyJ0eXAiOiJKV1Q...",
  "refresh": "eyJ0eXAiOiJKV1Q...",
  "user": { ... }
}

# Use access token
curl -X GET http://localhost:8000/api/v1/patients/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Q..."
```

### Endpoints Overview

<details>
<summary><b>🔐 Authentication</b> <code>/api/v1/auth/</code></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/login/` | Obtain JWT tokens |
| `POST` | `/register/` | Register new user |
| `POST` | `/refresh/` | Refresh access token |
| `POST` | `/logout/` | Blacklist refresh token |
| `GET` | `/me/` | Get current user profile |
| `PATCH` | `/me/` | Update current user |

</details>

<details>
<summary><b>👥 Patients</b> <code>/api/v1/patients/</code></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List patients (paginated) |
| `POST` | `/` | Create patient |
| `GET` | `/{id}/` | Get patient details |
| `PUT` | `/{id}/` | Update patient |
| `DELETE` | `/{id}/` | Delete patient |
| `GET` | `/{id}/history/` | Patient history |

</details>

<details>
<summary><b>🔬 Lab Orders</b> <code>/api/v1/lab-orders/</code></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List lab orders |
| `POST` | `/` | Create lab order |
| `GET` | `/{id}/` | Get order details |
| `PATCH` | `/{id}/` | Update order |
| `POST` | `/{id}/collect/` | Mark specimen collected |
| `POST` | `/{id}/result/` | Enter results |
| `POST` | `/{id}/cancel/` | Cancel order |

</details>

<details>
<summary><b>💰 Billing</b> <code>/api/v1/billing/</code></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/services/` | List services |
| `GET` | `/invoices/` | List invoices |
| `POST` | `/invoices/` | Create invoice |
| `POST` | `/invoices/{id}/cancel/` | Cancel invoice |
| `GET` | `/payments/` | List payments |
| `POST` | `/mpesa/stk-push/` | Initiate M-Pesa payment |
| `POST` | `/mpesa/callback/` | M-Pesa callback |

</details>

<details>
<summary><b>📊 Analytics</b> <code>/api/v1/analytics/</code></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/dashboard/` | Aggregated statistics |
| `GET` | `/patients/` | Patient analytics |
| `GET` | `/financial/` | Financial analytics |
| `GET` | `/lab/` | Lab order analytics |

</details>

<details>
<summary><b>🛡️ Security</b> <code>/api/v1/security/</code></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/blocked-ips/` | List blocked IPs |
| `POST` | `/blocked-ips/` | Block an IP |
| `POST` | `/blocked-ips/{id}/unblock/` | Unblock IP |
| `GET` | `/request-logs/` | View request logs |
| `GET` | `/events/` | Security events |
| `GET` | `/dashboard/` | Security dashboard |

</details>

### User Roles

| Role | Code | Permissions |
|------|------|-------------|
| **Admin** | `ADMIN` | Full system access |
| **Doctor** | `DOCTOR` | Patients, orders, results |
| **Nurse** | `NURSE` | Patients, orders (read) |
| **Lab Technician** | `LAB_TECH` | Lab orders, results |
| **Receptionist** | `RECEPTIONIST` | Patients (read-only) |

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_users.py -v

# Run specific test class
pytest tests/test_billing.py::TestInvoiceEndpoints -v

# Current status: 113 tests passing
```

### Test Coverage

| Module | Coverage |
|--------|----------|
| Users | 95% |
| Patients | 92% |
| Lab Orders | 88% |
| Billing | 85% |
| Analytics | 90% |
| Security | 100% |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | SQLite |
| `SECRET_KEY` | Django secret key | *required* |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `MPESA_CONSUMER_KEY` | M-Pesa API key | - |
| `MPESA_CONSUMER_SECRET` | M-Pesa API secret | - |
| `MPESA_SHORTCODE` | M-Pesa business shortcode | - |
| `MPESA_PASSKEY` | M-Pesa passkey | - |

### Project Structure

```
Hospital/
├── 📁 backend/
│   ├── 📁 apps/
│   │   ├── 📁 analytics/      # Dashboard & reporting
│   │   ├── 📁 billing/        # Invoices & payments
│   │   ├── 📁 core/           # Shared utilities
│   │   ├── 📁 lab_orders/     # Lab order management
│   │   ├── 📁 patients/       # Patient records
│   │   ├── 📁 security/       # IP blocking & logging
│   │   └── 📁 users/          # Authentication
│   ├── 📁 config/             # Django settings
│   ├── 📁 requirements/       # Dependencies
│   └── 📁 tests/              # Test suite
├── 📁 docker/                 # Docker configs
├── 📁 native/                 # C modules (optional)
├── 📄 docker-compose.yml
└── 📄 README.md
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [📖 API Docs](http://localhost:8000/api/v1/docs/) | Interactive Swagger UI |
| [🐳 Docker Guide](docker/README.md) | Container deployment |
| [💻 Backend README](backend/README.md) | Development setup |
| [🔧 Contributing](CONTRIBUTING.md) | Contribution guidelines |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation as needed
- Use conventional commits

---

## �� License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Immanuel Njogu**

- GitHub: [@manuel-Igtm](https://github.com/manuel-Igtm)

---

<div align="center">

**Built with ❤️ for modern healthcare infrastructure**

⭐ Star this repository if you find it helpful!

</div>

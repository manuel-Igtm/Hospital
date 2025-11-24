# Week 2 Development Tasks

**Date**: Week of December 1, 2025  
**Focus**: Users App + Patients App + Testing Infrastructure

## 🎯 Goals

Implement authentication and first domain model with comprehensive tests.

## 📋 Tasks

### 1. Users App (Priority: HIGH)

#### Setup
- [ ] Create `backend/apps/users/` directory structure
- [ ] Configure Django app in `INSTALLED_APPS`
- [ ] Update `AUTH_USER_MODEL` in settings

#### Model
- [ ] Create custom User model extending `AbstractUser`
- [ ] Add `role` field (choices: Doctor, Nurse, Admin, Lab, Billing)
- [ ] Add `employee_id` field (unique)
- [ ] Add `phone_number` field
- [ ] Add mixins from core app (TimestampMixin, SoftDeleteMixin)
- [ ] Create and run migration

#### Serializers
- [ ] `UserSerializer` - Basic user info
- [ ] `UserDetailSerializer` - Includes permissions
- [ ] `RegisterSerializer` - User registration validation
- [ ] `LoginSerializer` - Email + password
- [ ] `ChangePasswordSerializer`

#### Views
- [ ] `RegisterView` - POST /api/v1/auth/register/
- [ ] `LoginView` - POST /api/v1/auth/login/ (returns access + refresh tokens)
- [ ] `RefreshView` - POST /api/v1/auth/refresh/
- [ ] `LogoutView` - POST /api/v1/auth/logout/
- [ ] `MeView` - GET /api/v1/auth/me/ (current user)
- [ ] `UserViewSet` - CRUD for user management (admin only)

#### Permissions
- [ ] `IsDoctor` - Only doctors can access
- [ ] `IsNurse` - Only nurses can access
- [ ] `IsAdmin` - Only admins can access
- [ ] `IsLabTech` - Only lab techs can access
- [ ] `IsBilling` - Only billing staff can access

#### Admin
- [ ] Register User model with custom admin
- [ ] Add filters for role, is_active, is_staff
- [ ] Add search by username, email, employee_id
- [ ] Add inline for last_login, date_joined

#### Tests
- [ ] Test user registration
- [ ] Test login (success + failures)
- [ ] Test token refresh
- [ ] Test logout (token blacklist)
- [ ] Test /me endpoint
- [ ] Test permission classes
- [ ] Test CRUD operations with different roles

---

### 2. Patients App (Priority: HIGH)

#### Setup
- [ ] Create `backend/apps/patients/` directory structure
- [ ] Configure Django app in `INSTALLED_APPS`

#### Model
- [ ] Create `Patient` model
- [ ] Add `mrn` field (Medical Record Number, unique, indexed)
- [ ] Add demographic fields (first_name, last_name, dob, gender)
- [ ] Add contact fields (phone, email, address)
- [ ] Add `pii_token` field (from C module)
- [ ] Add `encrypted_ssn` field (AES-GCM)
- [ ] Add ForeignKey to User (created_by, updated_by)
- [ ] Add mixins (TimestampMixin, SoftDeleteMixin, AuditMixin)
- [ ] Add `generate_mrn()` method
- [ ] Add `encrypt_pii()` method
- [ ] Create and run migration

#### Serializers
- [ ] `PatientSerializer` - Basic patient info
- [ ] `PatientDetailSerializer` - Includes relationships
- [ ] `PatientCreateSerializer` - Create validation
- [ ] `PatientSearchSerializer` - Search filters

#### Views
- [ ] `PatientViewSet` - Full CRUD
- [ ] List filtering by name, mrn, dob
- [ ] Search endpoint with fuzzy matching
- [ ] Pagination (cursor-based)
- [ ] Permission checks (role-based)

#### Admin
- [ ] Register Patient model
- [ ] Add filters for gender, created_at
- [ ] Add search by mrn, name
- [ ] Readonly fields for pii_token, audit fields

#### Tests
- [ ] Test patient creation (MRN generation, PII encryption)
- [ ] Test patient retrieval (by MRN, by ID)
- [ ] Test patient update
- [ ] Test soft delete
- [ ] Test search functionality
- [ ] Test permission checks (role-based access)
- [ ] Test C module integration (PII token, encryption)

---

### 3. Testing Infrastructure (Priority: MEDIUM)

#### Configuration
- [ ] Create `backend/pytest.ini`
- [ ] Configure pytest-django settings
- [ ] Configure coverage settings (≥85% target)
- [ ] Configure test database (in-memory SQLite)

#### Fixtures
- [ ] Create `backend/conftest.py`
- [ ] Add `api_client` fixture (authenticated)
- [ ] Add `admin_user` fixture
- [ ] Add `doctor_user` fixture
- [ ] Add `nurse_user` fixture
- [ ] Add `sample_patient` fixture

#### Factories
- [ ] Install factory_boy
- [ ] Create `UserFactory` in users/tests/factories.py
- [ ] Create `PatientFactory` in patients/tests/factories.py

#### Sample Tests
- [ ] Create users/tests/test_models.py
- [ ] Create users/tests/test_serializers.py
- [ ] Create users/tests/test_views.py
- [ ] Create users/tests/test_permissions.py
- [ ] Create patients/tests/test_models.py
- [ ] Create patients/tests/test_serializers.py
- [ ] Create patients/tests/test_views.py

#### CI Setup (If Time Permits)
- [ ] Create `.github/workflows/test.yml`
- [ ] Configure Python 3.12 environment
- [ ] Build C modules in CI
- [ ] Run pytest with coverage
- [ ] Upload coverage to Codecov

---

### 4. Documentation Updates (Priority: LOW)

- [ ] Update `docs/progress.md` with Week 2 completion
- [ ] Add API examples to README
- [ ] Document authentication flow
- [ ] Document patient management endpoints
- [ ] Update PROJECT_SUMMARY.md

---

## 📊 Success Criteria

- [ ] Users can register and login
- [ ] JWT tokens work (access + refresh)
- [ ] Patients can be created with encrypted PII
- [ ] MRN generation works automatically
- [ ] Role-based permissions enforced
- [ ] All tests pass with ≥85% coverage
- [ ] API documentation updated
- [ ] C module integration verified

## 🚀 Getting Started

```bash
# Create feature branch
git checkout -b feature/week-2-users-patients

# Run development server
cd backend
python manage.py runserver

# Run tests as you develop
pytest apps/users/tests/test_models.py -v
pytest apps/patients/ --cov=apps.patients

# Check coverage
pytest --cov=apps --cov-report=html
open htmlcov/index.html
```

## 📝 Notes

- Start with Users app (required for Patients ForeignKey)
- Use C module wrappers from `apps.core.utils`
- Follow Django best practices (fat models, thin views)
- Write tests BEFORE implementation (TDD encouraged)
- Run `make lint` before committing
- Update progress.md when tasks complete

## 🎓 Learning Resources

- [Django Custom User Model](https://docs.djangoproject.com/en/5.0/topics/auth/customizing/)
- [DRF JWT Auth](https://django-rest-framework-simplejwt.readthedocs.io/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [pytest-django](https://pytest-django.readthedocs.io/)
- [factory_boy](https://factoryboy.readthedocs.io/)

---

**Questions?** Check [CONTRIBUTING.md](../CONTRIBUTING.md) or open a discussion!

# 📋 Hospital Backend - Complete TODO List

**Last Updated**: November 24, 2025  
**Project Status**: Week 1 Complete ✅

---

## Legend

- ✅ **Complete** - Done and tested
- 🚧 **In Progress** - Currently being worked on
- 📅 **Planned** - Scheduled for future weeks
- 🔮 **Future** - Nice-to-have features
- ❌ **Blocked** - Waiting on dependencies

---

## Week 1 (Nov 24) - Foundation ✅

### Repository Setup ✅
- [x] LICENSE with custom commercial terms
- [x] README.md with comprehensive documentation
- [x] CONTRIBUTING.md guidelines
- [x] CODE_OF_CONDUCT.md
- [x] .gitignore
- [x] .editorconfig
- [x] Makefile with automation commands

### C Native Modules ✅
- [x] CMake build system
- [x] libhl7val (HL7 v2 validation)
- [x] libcutils (AES-GCM, SHA-256, token generation)
- [x] libauthz (ABAC policy evaluation)
- [x] libbill (billing calculations)
- [x] CPython extension bindings
- [x] CTest unit tests (20+ tests)
- [x] setup.py and pyproject.toml

### Django Backend ✅
- [x] Project structure (config/)
- [x] Settings (base/dev/test/prod)
- [x] URLs, WSGI, ASGI
- [x] Celery configuration
- [x] Core app (exceptions, models, utils)
- [x] C module wrappers with fallbacks
- [x] Database wait management command
- [x] pyproject.toml with uv support

### Docker & DevOps ✅
- [x] Multi-stage Dockerfile
- [x] docker-compose.yml with 7 services
- [x] .env.example
- [x] Health checks
- [x] Volume management
- [x] Docker README

### Documentation ✅
- [x] QUICKSTART.md
- [x] PROJECT_SUMMARY.md
- [x] backend/README.md
- [x] docker/README.md
- [x] docs/progress.md
- [x] docs/week-2-tasks.md
- [x] docs/ARCHITECTURE.md
- [x] docs/WEEK_1_COMPLETE.md

---

## Week 2 (Dec 1) - Authentication & Patients 🚧

### Users App (Priority: HIGH)
- [ ] Create apps/users/ directory structure
- [ ] Custom User model extending AbstractUser
- [ ] Add role field (Doctor, Nurse, Admin, Lab, Billing)
- [ ] Add employee_id field (unique)
- [ ] Add phone_number field
- [ ] UserSerializer (basic info)
- [ ] UserDetailSerializer (with permissions)
- [ ] RegisterSerializer (validation)
- [ ] LoginSerializer
- [ ] ChangePasswordSerializer
- [ ] RegisterView (POST /api/v1/auth/register/)
- [ ] LoginView (POST /api/v1/auth/login/)
- [ ] RefreshView (POST /api/v1/auth/refresh/)
- [ ] LogoutView (POST /api/v1/auth/logout/)
- [ ] MeView (GET /api/v1/auth/me/)
- [ ] UserViewSet (CRUD for admins)
- [ ] IsDoctor permission class
- [ ] IsNurse permission class
- [ ] IsAdmin permission class
- [ ] IsLabTech permission class
- [ ] IsBilling permission class
- [ ] User admin configuration
- [ ] User tests (models, serializers, views, permissions)

### Patients App (Priority: HIGH)
- [ ] Create apps/patients/ directory structure
- [ ] Patient model with MRN
- [ ] Demographic fields (name, DOB, gender)
- [ ] Contact fields (phone, email, address)
- [ ] pii_token field (SHA-256)
- [ ] encrypted_ssn field (AES-GCM)
- [ ] ForeignKey to User (created_by, updated_by)
- [ ] generate_mrn() method
- [ ] encrypt_pii() method
- [ ] PatientSerializer
- [ ] PatientDetailSerializer
- [ ] PatientCreateSerializer
- [ ] PatientSearchSerializer
- [ ] PatientViewSet with CRUD
- [ ] List filtering (name, MRN, DOB)
- [ ] Search endpoint with fuzzy matching
- [ ] Cursor-based pagination
- [ ] Role-based permissions
- [ ] Patient admin configuration
- [ ] Patient tests (models, serializers, views)

### Testing Infrastructure (Priority: MEDIUM)
- [ ] pytest.ini configuration
- [ ] conftest.py with fixtures
- [ ] UserFactory with factory_boy
- [ ] PatientFactory with factory_boy
- [ ] api_client fixture (authenticated)
- [ ] Sample test patterns
- [ ] Coverage reporting (≥85% target)
- [ ] GitHub Actions CI (if time permits)

---

## Week 3 (Dec 8) - Appointments & Encounters 📅

### Appointments App
- [ ] Create apps/appointments/ directory structure
- [ ] Appointment model
- [ ] Fields: patient, doctor, datetime, duration, status, reason
- [ ] Status choices (Scheduled, Confirmed, In-Progress, Completed, Cancelled)
- [ ] Validation (no overlapping appointments)
- [ ] AppointmentSerializer
- [ ] AppointmentViewSet with CRUD
- [ ] Calendar view (filter by date range)
- [ ] Availability checking
- [ ] Email notifications (Celery task)
- [ ] SMS reminders (Celery task)
- [ ] Appointment admin
- [ ] Tests (models, views, business logic)

### Encounters App
- [ ] Create apps/encounters/ directory structure
- [ ] Encounter model (clinical visit)
- [ ] Fields: patient, doctor, appointment, datetime, notes
- [ ] chief_complaint field
- [ ] diagnosis_codes field (JSONField for ICD-10)
- [ ] EncounterSerializer
- [ ] EncounterDetailSerializer (with nested orders/meds)
- [ ] EncounterViewSet with CRUD
- [ ] Filter by patient, doctor, date
- [ ] Search by diagnosis codes
- [ ] Permissions (doctors can create, nurses can view)
- [ ] Encounter admin
- [ ] Tests

### Rate Limiting & Throttling
- [ ] Configure DRF throttling
- [ ] AnonRateThrottle (100/hour)
- [ ] UserRateThrottle (1000/hour)
- [ ] Custom throttle for sensitive endpoints
- [ ] Tests

---

## Week 4 (Dec 15) - Orders & Labs 📅

### Orders App
- [ ] Create apps/orders/ directory structure
- [ ] Order model (base for lab/imaging orders)
- [ ] Fields: encounter, ordered_by, order_type, status
- [ ] Status choices (Ordered, In-Progress, Completed, Cancelled)
- [ ] LabOrder model (extends Order)
- [ ] ImagingOrder model (extends Order)
- [ ] OrderSerializer
- [ ] OrderViewSet with CRUD
- [ ] Filter by status, patient, date
- [ ] Permissions (doctors/nurses can order, lab tech can update)
- [ ] Order admin
- [ ] Tests

### Labs App
- [ ] Create apps/labs/ directory structure
- [ ] LabResult model
- [ ] Fields: order, test_code (LOINC), result, unit, reference_range
- [ ] HL7 validation using C module
- [ ] LabResultSerializer
- [ ] LabResultViewSet
- [ ] Upload HL7 messages endpoint
- [ ] Parse and validate HL7
- [ ] Store results
- [ ] Permissions (lab tech can create, doctors can view)
- [ ] Lab admin
- [ ] Tests (including HL7 validation)

---

## Week 5 (Dec 22) - Medications & Billing 📅

### Medications App
- [ ] Create apps/medications/ directory structure
- [ ] Medication model
- [ ] Fields: name, atc_code, dosage, route, frequency
- [ ] Prescription model
- [ ] Fields: encounter, medication, prescriber, instructions
- [ ] start_date, end_date, refills
- [ ] MedicationSerializer
- [ ] PrescriptionSerializer
- [ ] PrescriptionViewSet with CRUD
- [ ] Drug interaction checking (external API)
- [ ] Allergy checking
- [ ] Permissions (only doctors can prescribe)
- [ ] Medication admin
- [ ] Tests

### Billing App
- [ ] Create apps/billing/ directory structure
- [ ] Invoice model
- [ ] Fields: patient, encounter, total_amount, status
- [ ] InvoiceLineItem model (individual charges)
- [ ] C module integration (calculate_invoice)
- [ ] DRG/ICD-based pricing
- [ ] InvoiceSerializer
- [ ] InvoiceViewSet with CRUD
- [ ] Generate invoice endpoint
- [ ] Payment tracking
- [ ] Permissions (billing staff only)
- [ ] Invoice admin
- [ ] Tests (including C module calculations)

### Insurance App
- [ ] Create apps/insurance/ directory structure
- [ ] InsuranceProvider model
- [ ] InsurancePlan model
- [ ] PatientInsurance model (link patient to plan)
- [ ] Eligibility checking (external API)
- [ ] Claims submission
- [ ] InsuranceSerializer
- [ ] InsuranceViewSet
- [ ] Admin
- [ ] Tests

---

## Week 6 (Dec 29) - Audit & Analytics 📅

### Audit App
- [ ] Create apps/audit/ directory structure
- [ ] AuditLog model
- [ ] Fields: actor, action, resource, timestamp, ip_address
- [ ] changes field (JSONField for before/after)
- [ ] Middleware to auto-log all write operations
- [ ] AuditLogSerializer
- [ ] AuditLogViewSet (read-only)
- [ ] Filter by actor, resource, date range
- [ ] Export to CSV (Celery task)
- [ ] Permissions (admin only)
- [ ] Partitioning by month (PostgreSQL)
- [ ] Automated archival (7-year retention)
- [ ] Tests

### Analytics (Optional)
- [ ] Dashboard model (store custom dashboards)
- [ ] Report model (scheduled reports)
- [ ] Patient statistics endpoint
- [ ] Appointment statistics endpoint
- [ ] Billing statistics endpoint
- [ ] Chart.js/D3.js integration (frontend)
- [ ] Celery task for daily reports
- [ ] Tests

---

## Week 7 (Jan 5) - Advanced Features 📅

### Search & Filtering
- [ ] Install django-filter
- [ ] Configure filterset for all models
- [ ] Full-text search (PostgreSQL)
- [ ] Elasticsearch integration (optional)
- [ ] Search endpoint (/api/v1/search/)
- [ ] Tests

### File Uploads
- [ ] Configure media storage (S3 or local)
- [ ] Document model (attach files to encounters)
- [ ] Image model (X-rays, MRIs)
- [ ] File upload endpoint
- [ ] File download with permissions
- [ ] Virus scanning (ClamAV integration)
- [ ] Tests

### Notifications
- [ ] Notification model
- [ ] Email notifications (via Celery + SMTP)
- [ ] SMS notifications (via Twilio)
- [ ] Push notifications (via FCM)
- [ ] WebSocket support (Django Channels)
- [ ] Real-time updates for appointments
- [ ] Tests

---

## Week 8 (Jan 12) - Testing & CI/CD 📅

### Comprehensive Testing
- [ ] Increase test coverage to ≥85%
- [ ] Integration tests (full API flows)
- [ ] Load testing (Locust)
- [ ] Security testing (OWASP ZAP)
- [ ] Performance testing
- [ ] C module Valgrind checks

### CI/CD Pipeline
- [ ] GitHub Actions workflow
- [ ] Build C modules
- [ ] Run Python tests
- [ ] Run C tests
- [ ] Linting (black, isort, mypy)
- [ ] Security scanning (Bandit, Safety)
- [ ] Docker image building
- [ ] Deploy to staging
- [ ] Deploy to production (manual approval)

### Pre-commit Hooks
- [ ] Install pre-commit
- [ ] Configure hooks (black, isort, mypy, trailing-whitespace)
- [ ] C formatting (clang-format)
- [ ] Tests as pre-push hook

---

## Week 9+ (Jan 19+) - Production Readiness 🔮

### Performance Optimization
- [ ] Database query optimization
- [ ] Add indexes for common queries
- [ ] Redis caching for read-heavy endpoints
- [ ] Celery task optimization
- [ ] C module profiling
- [ ] API response time monitoring

### Security Hardening
- [ ] Penetration testing
- [ ] Dependency updates
- [ ] SSL/TLS configuration
- [ ] Secrets management (HashiCorp Vault)
- [ ] WAF setup (Cloudflare or AWS WAF)
- [ ] DDoS protection

### Monitoring & Observability
- [ ] Prometheus + Grafana
- [ ] Application metrics
- [ ] Database metrics
- [ ] Celery metrics
- [ ] ELK stack for logging
- [ ] Sentry for error tracking
- [ ] OpenTelemetry for tracing

### Kubernetes Deployment
- [ ] Kubernetes manifests
- [ ] Deployment YAML
- [ ] Service YAML
- [ ] Ingress YAML
- [ ] ConfigMap and Secret
- [ ] Helm chart
- [ ] CI/CD pipeline for K8s

### Documentation
- [ ] API documentation examples
- [ ] Architecture decision records (ADRs)
- [ ] Runbooks for common issues
- [ ] Disaster recovery plan
- [ ] Backup and restore procedures
- [ ] Performance tuning guide

---

## Future Enhancements 🔮

### FHIR Support
- [ ] Install fhir.resources
- [ ] FHIR Patient resource
- [ ] FHIR Encounter resource
- [ ] FHIR Observation resource
- [ ] FHIR API endpoints
- [ ] FHIR validation

### GraphQL API
- [ ] Install graphene-django
- [ ] GraphQL schema
- [ ] Queries and mutations
- [ ] GraphQL permissions
- [ ] GraphQL Playground

### Mobile App
- [ ] React Native app
- [ ] Patient portal
- [ ] Doctor app
- [ ] Push notifications
- [ ] Offline mode

### Telemedicine
- [ ] Video consultation (WebRTC)
- [ ] Screen sharing
- [ ] Chat during video call
- [ ] Recording and storage

### AI/ML Features
- [ ] Disease prediction models
- [ ] Drug interaction prediction
- [ ] Appointment no-show prediction
- [ ] Readmission risk prediction

### Blockchain (Audit Trail)
- [ ] Hyperledger Fabric integration
- [ ] Immutable audit logs
- [ ] Smart contracts for insurance claims

---

## Maintenance Tasks 🔧

### Weekly
- [ ] Update dependencies (pip, npm)
- [ ] Review security advisories
- [ ] Check CI/CD status
- [ ] Review error logs (Sentry)

### Monthly
- [ ] Database backups verification
- [ ] Performance review
- [ ] Security audit
- [ ] Dependency updates (major versions)

### Quarterly
- [ ] Penetration testing
- [ ] Disaster recovery drill
- [ ] Architecture review
- [ ] Team retrospective

---

## Known Issues & Tech Debt 🐛

### High Priority
- [ ] Implement full ABAC policy parser in C
- [ ] Add Valgrind checks to CI
- [ ] Field-level encryption for PII

### Medium Priority
- [ ] Add type stubs for C modules
- [ ] Improve error messages in C modules
- [ ] Add more C module examples

### Low Priority
- [ ] Refactor C code for better readability
- [ ] Add benchmarks for C modules
- [ ] Consider async Django (ASGI fully)

---

## Current Sprint (Week 2)

### 🔥 This Week's Focus
1. Users app (authentication + authorization)
2. Patients app (CRUD + PII encryption)
3. Testing infrastructure (pytest + factory_boy)

### 📅 Due Date: December 1, 2025

**See [docs/week-2-tasks.md](week-2-tasks.md) for detailed task breakdown.**

---

## Contributing

Want to pick up a task?

1. Check this TODO list
2. Look for unchecked items
3. Comment on the issue or create a new one
4. Follow [CONTRIBUTING.md](../CONTRIBUTING.md) guidelines
5. Submit a PR when done
6. Update this TODO list in your PR

---

**Last Updated**: Week 1 Complete (Nov 24, 2025)  
**Next Review**: End of Week 2 (Dec 1, 2025)

---

*This is a living document. Update it as the project evolves!*

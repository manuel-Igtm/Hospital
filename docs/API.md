# Hospital Backend API Documentation

Complete API reference for the Hospital Backend System MVP.

## Base URL

- **Development**: `http://localhost:8000/api/v1/`
- **Production**: `https://api.hospital.example.com/api/v1/`

## Authentication

All endpoints (except registration and login) require JWT authentication.

### Headers

```text
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Lifecycle

| Token | Expiry | Purpose |
|-------|--------|---------|
| Access Token | 15 minutes | API authentication |
| Refresh Token | 7 days | Obtain new access tokens |

---

## Auth Endpoints

### Register User

```http
POST /api/v1/auth/register/
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123",
  "password_confirm": "SecureP@ss123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "doctor"
}
```

**Roles:** `admin`, `doctor`, `nurse`, `lab_technician`

**Response (201 Created):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "doctor",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### Login

```http
POST /api/v1/auth/login/
```

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecureP@ss123"
}
```

**Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "doctor"
  }
}
```

---

### Refresh Token

```http
POST /api/v1/auth/refresh/
```

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### Logout

```http
POST /api/v1/auth/logout/
```

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** `204 No Content`

---

### Get Current User

```http
GET /api/v1/auth/me/
```

**Response (200 OK):**

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "doctor",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-01-20T14:22:00Z"
}
```

---

## Patient Endpoints

### List Patients

```http
GET /api/v1/patients/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20, max: 100) |
| `search` | string | Search by name or MRN |
| `ordering` | string | Sort field (`created_at`, `-created_at`, `last_name`) |

**Response (200 OK):**

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/patients/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "mrn": "MRN-0001234",
      "first_name": "Jane",
      "last_name": "Smith",
      "date_of_birth": "1985-03-15",
      "gender": "female",
      "phone": "+1-555-123-4567",
      "email": "jane.smith@email.com",
      "created_at": "2025-01-10T09:00:00Z"
    }
  ]
}
```

---

### Create Patient

```http
POST /api/v1/patients/
```

**Request Body:**

```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1985-03-15",
  "gender": "female",
  "phone": "+1-555-123-4567",
  "email": "jane.smith@email.com",
  "address": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip_code": "62701",
    "country": "USA"
  },
  "emergency_contact": {
    "name": "John Smith",
    "relationship": "spouse",
    "phone": "+1-555-987-6543"
  }
}
```

**Response (201 Created):**

```json
{
  "id": "uuid",
  "mrn": "MRN-0001234",
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1985-03-15",
  "gender": "female",
  "phone": "+1-555-123-4567",
  "email": "jane.smith@email.com",
  "address": {...},
  "emergency_contact": {...},
  "created_at": "2025-01-15T10:30:00Z",
  "created_by": "uuid"
}
```

---

### Get Patient

```http
GET /api/v1/patients/{id}/
```

**Response (200 OK):**

```json
{
  "id": "uuid",
  "mrn": "MRN-0001234",
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1985-03-15",
  "gender": "female",
  "phone": "+1-555-123-4567",
  "email": "jane.smith@email.com",
  "address": {...},
  "emergency_contact": {...},
  "medical_history": "Previous surgeries: appendectomy (2010)",
  "allergies": ["Penicillin", "Shellfish"],
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

---

### Update Patient

```http
PUT /api/v1/patients/{id}/
```

**Request Body:** Same as Create Patient

**Response (200 OK):** Updated patient object

---

### Partial Update Patient

```http
PATCH /api/v1/patients/{id}/
```

**Request Body:** Any subset of patient fields

**Response (200 OK):** Updated patient object

---

### Delete Patient

```http
DELETE /api/v1/patients/{id}/
```

**Response:** `204 No Content`

---

### Patient History

```http
GET /api/v1/patients/{id}/history/
```

**Response (200 OK):**

```json
{
  "patient_id": "uuid",
  "history": [
    {
      "timestamp": "2025-01-15T14:30:00Z",
      "action": "updated",
      "user": "dr.smith@hospital.local",
      "changes": {
        "phone": {
          "old": "+1-555-111-2222",
          "new": "+1-555-123-4567"
        }
      }
    }
  ]
}
```

---

## Lab Order Endpoints

### List Lab Orders

```http
GET /api/v1/lab-orders/
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number |
| `status` | string | Filter by status |
| `patient` | uuid | Filter by patient ID |
| `ordering` | string | Sort field |

**Status Values:** `pending`, `in_progress`, `completed`, `cancelled`

**Response (200 OK):**

```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "patient": {
        "id": "uuid",
        "mrn": "MRN-0001234",
        "full_name": "Jane Smith"
      },
      "test_type": "CBC",
      "status": "pending",
      "priority": "routine",
      "ordered_by": {
        "id": "uuid",
        "full_name": "Dr. John Smith"
      },
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

### Create Lab Order

```http
POST /api/v1/lab-orders/
```

**Request Body:**

```json
{
  "patient_id": "uuid",
  "test_type": "CBC",
  "priority": "urgent",
  "notes": "Patient presenting with fatigue",
  "fasting_required": false
}
```

**Test Types:** `CBC`, `BMP`, `CMP`, `LFT`, `TSH`, `UA`, `LIPID`, `HBA1C`, `PT_INR`, `CUSTOM`

**Priority:** `stat`, `urgent`, `routine`

**Response (201 Created):**

```json
{
  "id": "uuid",
  "patient": {...},
  "test_type": "CBC",
  "status": "pending",
  "priority": "urgent",
  "notes": "Patient presenting with fatigue",
  "fasting_required": false,
  "ordered_by": {...},
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### Get Lab Order

```http
GET /api/v1/lab-orders/{id}/
```

**Response (200 OK):**

```json
{
  "id": "uuid",
  "patient": {...},
  "test_type": "CBC",
  "status": "completed",
  "priority": "urgent",
  "notes": "Patient presenting with fatigue",
  "ordered_by": {...},
  "results": {
    "wbc": {"value": 7.5, "unit": "K/uL", "reference": "4.5-11.0"},
    "rbc": {"value": 4.8, "unit": "M/uL", "reference": "4.5-5.5"},
    "hemoglobin": {"value": 14.2, "unit": "g/dL", "reference": "13.5-17.5"},
    "hematocrit": {"value": 42, "unit": "%", "reference": "38-50"},
    "platelets": {"value": 250, "unit": "K/uL", "reference": "150-400"}
  },
  "result_entered_by": {...},
  "result_entered_at": "2025-01-15T14:30:00Z",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### Update Lab Order (Enter Results)

```http
PATCH /api/v1/lab-orders/{id}/
```

**Request Body:**

```json
{
  "status": "completed",
  "results": {
    "wbc": {"value": 7.5, "unit": "K/uL", "reference": "4.5-11.0"},
    "rbc": {"value": 4.8, "unit": "M/uL", "reference": "4.5-5.5"}
  }
}
```

**Response (200 OK):** Updated lab order object

---

### Get Patient Lab Orders

```http
GET /api/v1/lab-orders/patient/{patient_id}/
```

**Response (200 OK):** List of lab orders for the patient

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid input",
  "errors": {
    "email": ["This field is required."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found

```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error. Please try again later."
}
```

---

## Rate Limiting

| Endpoint | Rate Limit |
|----------|------------|
| Auth endpoints | 5 requests/minute |
| API endpoints | 100 requests/minute |

---

## Role Permissions Matrix

| Endpoint | Admin | Doctor | Nurse | Lab Tech |
|----------|-------|--------|-------|----------|
| List Patients | ✓ | ✓ | ✓ | ✗ |
| Create Patient | ✓ | ✓ | ✓ | ✗ |
| Update Patient | ✓ | ✓ | ✓ | ✗ |
| Delete Patient | ✓ | ✗ | ✗ | ✗ |
| List Lab Orders | ✓ | ✓ | ✓ | ✓ |
| Create Lab Order | ✓ | ✓ | ✗ | ✗ |
| Enter Results | ✓ | ✗ | ✗ | ✓ |
| Cancel Order | ✓ | ✓ | ✗ | ✗ |

---

© 2025 Immanuel Njogu. All rights reserved.

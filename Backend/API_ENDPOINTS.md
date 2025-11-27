# Job Search API - Complete Endpoint Documentation

## Overview

This document provides comprehensive documentation for all REST API endpoints in the Job Search Application backend. All endpoints follow RESTful conventions and use JSON for request/response payloads.

## Base URL

```
http://localhost:8000
```

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

---

## Authentication Endpoints

### 1. Register User
**Endpoint:** `POST /auth/register`

**Description:** Create a new user account and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": null,
    "location": null,
    "bio": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Status Codes:**
- `201 Created` - User successfully registered
- `400 Bad Request` - Invalid input or email already exists
- `422 Unprocessable Entity` - Validation error

---

### 2. Login User
**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "bio": "Software engineer",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T15:45:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid email or password
- `422 Unprocessable Entity` - Validation error

---

### 3. Logout User
**Endpoint:** `POST /auth/logout`

**Description:** Logout the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

**Status Codes:**
- `200 OK` - Successfully logged out
- `401 Unauthorized` - Invalid or missing token

---

### 4. Get Current User
**Endpoint:** `GET /auth/me`

**Description:** Retrieve the currently authenticated user's information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "bio": "Software engineer with 5 years experience",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T15:45:00Z"
}
```

**Status Codes:**
- `200 OK` - User information retrieved
- `401 Unauthorized` - Invalid or missing token

---

## User Profile Endpoints

### 5. Get User Profile
**Endpoint:** `GET /users/{id}`

**Description:** Retrieve a user's profile information by ID.

**Path Parameters:**
- `id` (string) - User unique identifier

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "bio": "Software engineer with 5 years experience",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T15:45:00Z"
}
```

**Status Codes:**
- `200 OK` - User profile retrieved
- `404 Not Found` - User not found

---

### 6. Update User Profile
**Endpoint:** `PUT /users/{id}`

**Description:** Update the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `id` (string) - User unique identifier (must match authenticated user)

**Request Body:**
```json
{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "bio": "Senior software engineer with 5 years experience"
}
```

**Response (200 OK):**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "bio": "Senior software engineer with 5 years experience",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T16:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Profile updated successfully
- `401 Unauthorized` - Invalid token or unauthorized user
- `404 Not Found` - User not found
- `422 Unprocessable Entity` - Validation error

---

### 7. Delete User Account
**Endpoint:** `DELETE /users/{id}`

**Description:** Delete a user account (irreversible).

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `id` (string) - User unique identifier (must match authenticated user)

**Response (200 OK):**
```json
{
  "message": "User account successfully deleted"
}
```

**Status Codes:**
- `200 OK` - Account deleted successfully
- `401 Unauthorized` - Invalid token or unauthorized user
- `404 Not Found` - User not found

---

## Job Endpoints

### 8. Search Jobs
**Endpoint:** `GET /jobs`

**Description:** Search for jobs with various filters and pagination.

**Query Parameters:**
- `title` (string, optional) - Filter by job title keyword
- `location` (string, optional) - Filter by job location
- `skills` (array[string], optional) - Filter by required skills
- `job_type` (string, optional) - Filter by employment type
- `experience_level` (string, optional) - Filter by experience level
- `salary_min` (number, optional) - Minimum salary filter
- `salary_max` (number, optional) - Maximum salary filter
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 10, max: 100) - Results per page

**Example Request:**
```
GET /jobs?title=Python&location=San%20Francisco&skills=FastAPI&skills=PostgreSQL&salary_min=100000&limit=20
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "job123",
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "job_type": "Full-time",
      "experience_level": "Senior",
      "description": "We are looking for a senior Python developer...",
      "required_skills": ["Python", "FastAPI", "PostgreSQL"],
      "salary_min": 150000,
      "salary_max": 200000,
      "currency": "USD",
      "posted_at": "2024-01-15T10:30:00Z",
      "deadline": "2024-02-15T23:59:59Z"
    }
  ],
  "total": 45,
  "skip": 0,
  "limit": 20
}
```

**Status Codes:**
- `200 OK` - Jobs retrieved successfully
- `400 Bad Request` - Invalid query parameters

---

### 9. Get Job Details
**Endpoint:** `GET /jobs/{id}`

**Description:** Retrieve detailed information about a specific job.

**Path Parameters:**
- `id` (string) - Job unique identifier

**Response (200 OK):**
```json
{
  "id": "job123",
  "title": "Senior Python Developer",
  "company": "Tech Corp",
  "location": "San Francisco, CA",
  "job_type": "Full-time",
  "experience_level": "Senior",
  "description": "We are looking for a senior Python developer with expertise in...",
  "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "salary_min": 150000,
  "salary_max": 200000,
  "currency": "USD",
  "posted_at": "2024-01-15T10:30:00Z",
  "deadline": "2024-02-15T23:59:59Z"
}
```

**Status Codes:**
- `200 OK` - Job details retrieved
- `404 Not Found` - Job not found

---

## Saved Jobs Endpoints

### 10. Save a Job
**Endpoint:** `POST /saved-jobs/{jobId}`

**Description:** Save a job to the authenticated user's list.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `jobId` (string) - Job unique identifier

**Response (201 Created):**
```json
{
  "id": "saved123",
  "user_id": "user123",
  "job": {
    "id": "job123",
    "title": "Senior Python Developer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "job_type": "Full-time",
    "experience_level": "Senior",
    "description": "We are looking for a senior Python developer...",
    "required_skills": ["Python", "FastAPI"],
    "salary_min": 150000,
    "salary_max": 200000,
    "currency": "USD",
    "posted_at": "2024-01-15T10:30:00Z",
    "deadline": "2024-02-15T23:59:59Z"
  },
  "saved_at": "2024-01-20T14:30:00Z"
}
```

**Status Codes:**
- `201 Created` - Job saved successfully
- `400 Bad Request` - Job already saved or invalid job ID
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Job not found

---

### 11. List Saved Jobs
**Endpoint:** `GET /saved-jobs`

**Description:** Retrieve all saved jobs for the authenticated user.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `skip` (integer, default: 0) - Pagination offset
- `limit` (integer, default: 10, max: 100) - Results per page

**Example Request:**
```
GET /saved-jobs?skip=0&limit=10
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "saved123",
      "user_id": "user123",
      "job": {
        "id": "job123",
        "title": "Senior Python Developer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "job_type": "Full-time",
        "experience_level": "Senior",
        "description": "We are looking for a senior Python developer...",
        "required_skills": ["Python", "FastAPI"],
        "salary_min": 150000,
        "salary_max": 200000,
        "currency": "USD",
        "posted_at": "2024-01-15T10:30:00Z",
        "deadline": "2024-02-15T23:59:59Z"
      },
      "saved_at": "2024-01-20T14:30:00Z"
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 10
}
```

**Status Codes:**
- `200 OK` - Saved jobs retrieved successfully
- `401 Unauthorized` - Invalid or missing token

---

### 12. Remove Saved Job
**Endpoint:** `DELETE /saved-jobs/{jobId}`

**Description:** Remove a job from the authenticated user's saved jobs.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Path Parameters:**
- `jobId` (string) - Job unique identifier

**Response (200 OK):**
```json
{
  "message": "Job successfully removed from saved jobs"
}
```

**Status Codes:**
- `200 OK` - Job removed successfully
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - Saved job not found

---

## Health Check Endpoints

### 13. Root Endpoint
**Endpoint:** `GET /`

**Response (200 OK):**
```json
{
  "message": "Job Search API is running",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

### 14. Health Check
**Endpoint:** `GET /health`

**Response (200 OK):**
```json
{
  "status": "healthy"
}
```

---

## Error Response Format

All error responses follow this standard format:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

---

## Pagination

List endpoints support pagination via query parameters:

- `skip` - Number of records to skip (default: 0)
- `limit` - Number of records to return (default: 10, max: 100)

Example:
```
GET /jobs?skip=20&limit=10
```

---

## Documentation

Access interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

## Rate Limiting & Best Practices

1. Use reasonable pagination limits (10-50 records)
2. Cache results when possible
3. Implement exponential backoff for retries
4. Keep JWT tokens secure
5. Use HTTPS in production

---

## Example cURL Requests

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

### Search Jobs
```bash
curl -X GET "http://localhost:8000/jobs?title=Python&location=San%20Francisco&limit=10"
```

### Save Job (Requires Token)
```bash
curl -X POST http://localhost:8000/saved-jobs/job123 \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json"
```

### Get Saved Jobs (Requires Token)
```bash
curl -X GET "http://localhost:8000/saved-jobs?skip=0&limit=10" \
  -H "Authorization: Bearer <jwt_token>"
```

---

## Version History

### v1.0.0 (Current)
- Initial API release
- Complete REST endpoints for job search functionality
- JWT authentication
- User profile management
- Job search with filters
- Saved jobs management

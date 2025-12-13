# Job Search API - Architecture & Design

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  (Web, Mobile, Desktop - Sends HTTP requests with JWT tokens)   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI SERVER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   CORS Middleware                        │  │
│  │  (Allow cross-origin requests)                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │                    Router Layer                         │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  /auth           /users          /jobs    /saved-jobs   │  │
│  │  • register      • get           • search • save        │  │
│  │  • login         • update        • detail • list        │  │
│  │  • logout        • delete                 • remove      │  │
│  │  • me                                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │              Dependency Injection Layer                 │  │
│  │  • get_current_user (JWT validation)                   │  │
│  │  • Security: Bearer token extraction                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │            Security & Utilities Layer                  │  │
│  │  • JWT creation & validation                           │  │
│  │  • Password hashing (bcrypt)                           │  │
│  │  • Token expiration                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │              Pydantic Models Layer                      │  │
│  │  • Request validation                                  │  │
│  │  • Response serialization                              │  │
│  │  • OpenAPI schema generation                           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               DATA LAYER (Future Implementation)                 │
│  • SQLAlchemy ORM                                               │
│  • Database Models                                              │
│  • Connection Pool                                              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
                    ┌───────────────────────┐
                    │   PostgreSQL/SQLite   │
                    │     Database          │
                    └───────────────────────┘
```

## 📂 Module Organization

### 1. Router Modules
Each resource has its own router with related endpoints:

```
auth.py
├── POST /auth/register          (201 Created)
├── POST /auth/login             (200 OK)
├── POST /auth/logout            (200 OK)
└── GET /auth/me                 (200 OK)

users.py
├── GET /users/{id}              (200 OK)
├── PUT /users/{id}              (200 OK)
└── DELETE /users/{id}           (200 OK)

jobs.py
├── GET /jobs                    (200 OK)
└── GET /jobs/{id}               (200 OK)

saved_jobs.py
├── POST /saved-jobs/{jobId}     (201 Created)
├── GET /saved-jobs              (200 OK)
└── DELETE /saved-jobs/{jobId}   (200 OK)
```

### 2. Security Layer
```
core/security.py
├── hash_password()              - Bcrypt hashing
├── verify_password()            - Password validation
├── create_access_token()        - JWT generation
├── get_current_user()           - Auth dependency
└── Imports: passlib, python-jose
```

### 3. Configuration Layer
```
core/config.py
├── Settings class              - Environment management
├── API configuration
├── Security settings
└── Database configuration
```

### 4. Schema Layer
```
schemas/schemas.py
├── Authentication
│   ├── UserRegisterRequest
│   ├── UserLoginRequest
│   ├── TokenResponse
│   └── LogoutResponse
├── User Profile
│   ├── UserResponse
│   └── UserUpdateRequest
├── Jobs
│   ├── JobResponse
│   ├── JobSearchQuery
│   └── JobsListResponse
├── Saved Jobs
│   ├── SavedJobRequest
│   ├── SavedJobResponse
│   └── SavedJobsListResponse
└── Generic
    ├── MessageResponse
    └── ErrorResponse
```

## 🔐 Authentication Flow

```
User Action                 API Operation               Response
─────────────────────────────────────────────────────────────────
1. Register        →  POST /auth/register        →  JWT Token + User
                        ↓
                   password hashed
                   user created (DB)
                   token generated

2. Login           →  POST /auth/login           →  JWT Token + User
                        ↓
                   password verified
                   token generated

3. Authenticated   →  GET /auth/me               →  User Info
   Request              ↓
                   Bearer token extracted
                   JWT decoded & validated
                   user_id retrieved

4. Protected       →  PUT /users/{id}            →  Updated User
   Operation            ↓
                   Token validated
                   User ID verified
                   Operation performed
```

## 📊 Data Models Hierarchy

```
TokenResponse
├── access_token (str)
├── token_type (str)
└── user (UserResponse)

UserResponse
├── id (str)
├── email (str)
├── name (str)
├── phone (Optional[str])
├── location (Optional[str])
├── bio (Optional[str])
├── created_at (str)
└── updated_at (str)

JobResponse
├── id (str)
├── title (str)
├── company (str)
├── location (str)
├── job_type (str)
├── experience_level (str)
├── description (str)
├── required_skills (list[str])
├── salary_min (Optional[float])
├── salary_max (Optional[float])
├── currency (Optional[str])
├── posted_at (str)
└── deadline (Optional[str])

SavedJobResponse
├── id (str)
├── user_id (str)
├── job (JobResponse)
└── saved_at (str)

*ListResponse (Paginated)
├── items (list[Item])
├── total (int)
├── skip (int)
└── limit (int)
```

## 🔄 Request/Response Flow Example

### Example: Save a Job

```
REQUEST
┌──────────────────────────────────┐
│ POST /saved-jobs/{jobId}         │
├──────────────────────────────────┤
│ Headers:                         │
│  Authorization: Bearer <token>   │
│  Content-Type: application/json  │
│                                  │
│ Body: (empty, jobId in path)    │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Dependency: get_current_user()   │
├──────────────────────────────────┤
│ • Extract Bearer token           │
│ • Decode JWT                     │
│ • Validate expiration            │
│ • Return user_id & claims        │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Route Handler                    │
├──────────────────────────────────┤
│ • Validate job_id exists         │
│ • Check if already saved         │
│ • Save association               │
│ • Get full job details           │
└──────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│ Response Serialization           │
├──────────────────────────────────┤
│ • Create SavedJobResponse        │
│ • Validate with Pydantic         │
│ • Convert to JSON                │
└──────────────────────────────────┘
           │
           ▼
RESPONSE
┌──────────────────────────────────┐
│ HTTP 201 Created                 │
├──────────────────────────────────┤
│ Body: SavedJobResponse (JSON)    │
│ {                                │
│   "id": "saved123",              │
│   "user_id": "user123",          │
│   "job": { ... },                │
│   "saved_at": "2024-01-20..."    │
│ }                                │
└──────────────────────────────────┘
```

## 🎯 Design Principles

### 1. Separation of Concerns
- **Routes**: Handle HTTP requests/responses
- **Schemas**: Define data models
- **Security**: Handle authentication
- **Config**: Manage settings

### 2. Type Safety
- Full type hints on all functions
- Pydantic validation on all data
- IDE autocomplete support

### 3. DRY (Don't Repeat Yourself)
- Shared schemas across routes
- Dependency injection for common logic
- Centralized error handling

### 4. RESTful Conventions
- HTTP methods used appropriately
- Meaningful status codes
- Resource-based URLs
- Pagination for lists

### 5. Security First
- JWT for stateless auth
- Bcrypt for password hashing
- Bearer token validation
- Protected endpoints with dependencies

### 6. Documentation
- Docstrings on all endpoints
- OpenAPI/Swagger support
- Schema examples
- README documentation

## 📝 Status Codes Used

| Code | Meaning | Used For |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, DELETE, logout |
| 201 | Created | Register, save job |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Invalid/missing token |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |

## 🚀 Scalability Considerations

### Current (Route Layer Only)
- No database dependencies
- Stateless API
- Can run multiple instances
- Load balancer ready

### Future (Implementation)
- Add database connection pooling
- Implement caching layer
- Add rate limiting
- Implement logging
- Add monitoring

## 🔗 Dependency Chain

```
main.py (Entry point)
  ├── app = FastAPI()
  ├── app.add_middleware() [CORS]
  ├── app.include_router(auth)
  ├── app.include_router(users)
  ├── app.include_router(jobs)
  └── app.include_router(saved_jobs)

routers/auth.py
  ├── imports: schemas, security
  ├── uses: get_current_user dependency
  └── returns: Pydantic models

core/security.py
  ├── imports: config, jose, passlib
  ├── uses: settings from config
  └── provides: get_current_user dependency

core/config.py
  ├── imports: pydantic_settings
  └── provides: Settings instance

schemas/schemas.py
  ├── imports: pydantic
  └── defines: all request/response models
```

## 🎓 Pattern Used: Dependency Injection

```python
# Security dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    # Validates token and returns user info
    pass

# Usage in routes
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)  # ← Injected
) -> MessageResponse:
    pass
```

This allows:
- Reusable authentication logic
- Single source of truth
- Easy testing (can mock dependency)
- Clear security requirements

---

**This architecture is production-ready for implementing business logic.**

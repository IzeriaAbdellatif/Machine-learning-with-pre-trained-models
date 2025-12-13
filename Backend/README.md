# Job Search API Backend

A production-ready FastAPI backend for a job-search application with comprehensive REST endpoints.

## Project Structure

```
Backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration and settings
│   │   └── security.py        # JWT and password utilities
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── users.py           # User profile endpoints
│   │   ├── jobs.py            # Job search endpoints
│   │   └── saved_jobs.py      # Saved jobs endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models for request/response
│   ├── __init__.py
│   └── main.py                # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register a new user
- `POST /auth/login` - User login (returns JWT token)
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current authenticated user

### User Profile (`/users`)
- `GET /users/{id}` - Get user profile
- `PUT /users/{id}` - Update user profile
The API will be available at `http://localhost:8000`
- `DELETE /users/{id}` - Delete user account

### Jobs (`/jobs`)
- `GET /jobs` - Search jobs with filters
  - Query parameters: `title`, `location`, `skills`, `job_type`, `experience_level`, `salary_min`, `salary_max`, `skip`, `limit`
- `GET /jobs/{id}` - Get job details

### Saved Jobs (`/saved-jobs`)
- `POST /saved-jobs/{jobId}` - Save a job
- `GET /saved-jobs` - List saved jobs
- `DELETE /saved-jobs/{jobId}` - Remove saved job

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the Backend directory:

```env
# API Configuration
API_TITLE=Job Search API
API_VERSION=1.0.0
API_DESCRIPTION=REST API for job search application

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (for future implementation)
DATABASE_URL=sqlite:///./test.db
```

### 4. Run the Application

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Key Features

### Authentication & Security
- JWT (JSON Web Token) based authentication
- BCrypt password hashing
- HTTP Bearer token security scheme
- `get_current_user` dependency for protected routes

### Schema Definitions
All endpoints use Pydantic models for:
- Request validation
- Response serialization
- Automatic OpenAPI documentation
- JSON schema generation

### Router Organization
- **Modular structure**: Each resource has its own router module
- **Automatic path prefixing**: `/auth`, `/users`, `/jobs`, `/saved-jobs`
- **Consistent tagging**: Grouped in Swagger UI by resource type

### Request/Response Examples
- All schemas include detailed descriptions
- JSON examples for each schema
- Comprehensive field documentation

## Authentication Flow

1. **Register**: `POST /auth/register` → Returns JWT token
2. **Login**: `POST /auth/login` → Returns JWT token
3. **Authenticated Requests**: Add `Authorization: Bearer <token>` header
4. **Current User**: `GET /auth/me` → Returns authenticated user info
5. **Logout**: `POST /auth/logout` → Invalidates session

## Query Parameter Examples

### Job Search
```
GET /jobs?title=Python&location=San%20Francisco&skills=FastAPI&salary_min=100000&limit=20
```

### Pagination
```
GET /saved-jobs?skip=10&limit=10
```

## Error Handling

All endpoints return standardized error responses:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

## Next Steps for Implementation

1. **Database Layer**: Integrate SQLAlchemy ORM
2. **Business Logic**: Implement actual job search functionality
3. **Persistence**: Connect to database
4. **Validation**: Add custom validators to schemas
5. **Testing**: Create comprehensive unit and integration tests
6. **Deployment**: Configure for production (Docker, environment variables, etc.)

## Development

### Project Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-jose` - JWT handling
- `passlib` - Password hashing
- `bcrypt` - Cryptographic hashing

### Code Organization

- **Route handlers**: Only function signatures, no implementation logic
- **Pydantic models**: Comprehensive field descriptions and examples
- **Type hints**: Full type annotation for IDE support
- **Documentation**: Detailed docstrings and OpenAPI descriptions

## Production Considerations

- [ ] Update `SECRET_KEY` environment variable
- [ ] Configure CORS origins appropriately
- [ ] Use environment-specific configuration
- [ ] Implement database persistence
- [ ] Add comprehensive error handling
- [ ] Implement request logging
- [ ] Add rate limiting
- [ ] Setup SSL/TLS
- [ ] Create unit tests
- [ ] Setup CI/CD pipeline

## License

MIT

# Job Search API - Quick Start Guide

## 📁 Project Structure

```
Backend/
├── app/                          # Application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── core/                     # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py             # Settings and configuration
│   │   └── security.py           # JWT and password utilities
│   ├── routers/                  # API route modules
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication routes
│   │   ├── users.py              # User profile routes
│   │   ├── jobs.py               # Job search routes
│   │   └── saved_jobs.py         # Saved jobs routes
│   └── schemas/                  # Pydantic models
│       ├── __init__.py
│       └── schemas.py            # All request/response schemas
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── API_ENDPOINTS.md              # Detailed API documentation
├── README.md                     # Project README
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
└── start.sh                      # Startup script
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd Backend
chmod +x start.sh
./start.sh
```

### 2. Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env

# Run server
python -m uvicorn app.main:app --reload
```

### 3. Access API
- **API Docs:** http://localhost:8000/docs
- **API Root:** http://localhost:8000/
- **Health Check:** http://localhost:8000/health

## 📚 API Endpoints Summary

### Authentication (`/auth`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/logout` | Logout user |
| GET | `/auth/me` | Get current user |

### User Profile (`/users`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/users/{id}` | Get user profile |
| PUT | `/users/{id}` | Update profile |
| DELETE | `/users/{id}` | Delete account |

### Jobs (`/jobs`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/jobs` | Search jobs (with filters) |
| GET | `/jobs/{id}` | Get job details |

### Saved Jobs (`/saved-jobs`)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/saved-jobs/{jobId}` | Save a job |
| GET | `/saved-jobs` | List saved jobs |
| DELETE | `/saved-jobs/{jobId}` | Remove saved job |

## 🔐 Authentication

1. **Register:** `POST /auth/register` → Get JWT token
2. **Add to headers:** `Authorization: Bearer <token>`
3. **Use in requests:** All protected endpoints require this header

Example:
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiI..."
```

## 📦 Dependencies

### Core
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### Security
- `python-jose[cryptography]` - JWT handling
- `passlib[bcrypt]` - Password hashing

### Development (Optional)
- `pytest` - Testing
- `black` - Code formatting
- `flake8` - Linting

## 📝 Key Features

✅ **Production-Ready Routes**
- Clean route signatures with no business logic
- Full type hints for IDE support
- Comprehensive docstrings

✅ **Complete Schemas**
- Pydantic models for all requests/responses
- Field descriptions and examples
- Automatic OpenAPI documentation

✅ **Security**
- JWT authentication via HTTP Bearer
- Password hashing with bcrypt
- Protected route dependencies

✅ **Organization**
- Modular router structure
- Separated concerns (auth, users, jobs)
- Configuration management

## 🧪 Testing with Swagger

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in required parameters
5. Click "Execute"

## 🔧 Configuration

Edit `.env` file:
```env
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_TITLE=Job Search API
```

## 📖 Documentation Files

- **README.md** - Project overview and setup
- **API_ENDPOINTS.md** - Comprehensive endpoint documentation
- **QUICK_START.md** - This file

## 🛣️ Next Steps

To implement business logic:

1. **Database Layer**
   - Add SQLAlchemy models
   - Create database connection

2. **Services**
   - Create business logic in service classes
   - Separate from route handlers

3. **Testing**
   - Add pytest unit tests
   - Create fixtures for test data

4. **Deployment**
   - Create Dockerfile
   - Setup CI/CD pipeline
   - Configure production environment

## 💡 Example Request Flows

### User Registration & Login Flow
```
1. POST /auth/register
   → Get JWT token

2. POST /auth/login (alternative)
   → Get JWT token

3. GET /auth/me
   → Get authenticated user info
```

### Job Search Flow
```
1. GET /jobs?title=Python&location=SF
   → Browse available jobs

2. GET /jobs/{id}
   → View job details

3. POST /saved-jobs/{jobId}
   → Save job to profile

4. GET /saved-jobs
   → View all saved jobs
```

## 📞 Support

For issues or questions:
1. Check API_ENDPOINTS.md for endpoint details
2. Review Swagger UI at /docs
3. Check route docstrings in code
4. Review schema.py for data models

## 📄 License

MIT License - Feel free to use and modify

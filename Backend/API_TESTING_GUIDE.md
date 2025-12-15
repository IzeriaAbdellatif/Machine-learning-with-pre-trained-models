# API Testing Guide: Job Recommendations with Scoring

## Overview
This document demonstrates how to test the new `/jobs/me/recommendations` endpoint which retrieves authenticated user and returns jobs enriched with computed relevance scores.

## Implementation Summary

### New Features:
1. **ScoringService** (`app/services/scoring_service.py`)
   - Wraps `rule_scoring_service` with clean interfaces
   - Converts ORM models to scoring-friendly dictionaries
   - Computes relevance scores for jobs based on user profile
   - Enriches jobs with score breakdowns

2. **Extended JobService** (`app/services/job_service.py`)
   - `get_all_jobs()`: Fetch all jobs with pagination
   - `get_jobs_with_scores()`: Retrieve jobs and enrich with scores for authenticated user

3. **New Schemas** (`app/schemas/schemas.py`)
   - `JobScoreBreakdown`: Detailed score metrics (skills, location, salary, etc.)
   - `EnrichedJobResponse`: Job with computed relevance score
   - `EnrichedJobsListResponse`: Paginated list of scored jobs

4. **Authenticated Endpoint** (`app/routers/jobs.py`)
   - `GET /jobs/me/recommendations`: Personalized job recommendations

## Architecture

```
Client (with JWT token)
    ↓
GET /jobs/me/recommendations
    ↓
jobs.py router
    ↓
get_current_user() → extract user_id from token
    ↓
fetch User from database
    ↓
job_service.get_jobs_with_scores(db, user)
    ↓
[For each job]:
  - ScoringService.enrich_job_with_score()
    - Convert Job ORM → dict
    - Build UserProfile from User
    - rule_scoring_service.compute_rule_scores_for_job()
    - rule_scoring_service.compute_final_score()
    - Return enriched dict with scores
    ↓
Sort by final score (descending)
    ↓
Return EnrichedJobsListResponse to client
```

## Score Components

Each job receives a score breakdown with these components (all 0.0-1.0):

| Component | Description |
|-----------|-------------|
| `skills` | Match between user's skills and job's required_skills |
| `mode_travail` | Work mode preference match (remote/hybrid/in-office) |
| `location` | Location preference match |
| `remuneration` | Salary compatibility with user's expectations |
| `embedding` | ML-based semantic similarity score |
| `final` | Weighted combined score (main ranking metric) |

## Testing Steps

### 1. Start the API Server

```bash
cd /home/aizeria/Documents/Machine-learning-with-pre-trained-models/Backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestPassword123",
    "name": "Test User"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid-here",
    "email": "testuser@example.com",
    "name": "Test User",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

### 3. Get Personalized Job Recommendations

Use the `access_token` from the registration response:

```bash
curl -X GET "http://localhost:8000/jobs/me/recommendations?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Expected Response (200 OK):
```json
{
  "items": [
    {
      "id": "job-uuid",
      "title": "Senior Data Scientist",
      "company": "Tech Corp",
      "location": "Remote",
      "job_type": "Full-time",
      "experience_level": "Senior",
      "description": "...",
      "required_skills": ["Python", "Machine Learning"],
      "salary_min": 150000,
      "salary_max": 200000,
      "currency": "USD",
      "job_url": "https://...",
      "mode_travail": "remote",
      "remuneration": "150k - 200k USD",
      "score": {
        "skills": 0.85,
        "mode_travail": 1.0,
        "location": 0.5,
        "remuneration": 0.9,
        "embedding": 0.75,
        "final": 0.78
      }
    },
    {
      "id": "job-uuid-2",
      "title": "Junior Python Developer",
      "company": "Startup Inc",
      "location": "Casablanca",
      "job_type": "Full-time",
      "score": {
        "skills": 0.60,
        "mode_travail": 0.2,
        "location": 1.0,
        "remuneration": 0.5,
        "embedding": 0.65,
        "final": 0.58
      }
    }
  ],
  "total": 156,
  "skip": 0,
  "limit": 10
}
```

### 4. Test Error Cases

#### Missing Authentication Token
```bash
curl -X GET "http://localhost:8000/jobs/me/recommendations"
```
Response: 403 Forbidden (or 401 Unauthorized)

#### Invalid Token
```bash
curl -X GET "http://localhost:8000/jobs/me/recommendations" \
  -H "Authorization: Bearer invalid_token_here"
```
Response: 401 Unauthorized

#### Invalid Pagination Parameters
```bash
curl -X GET "http://localhost:8000/jobs/me/recommendations?limit=1000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```
Response: 422 Unprocessable Entity (limit must be ≤ 100)

## Key Design Decisions

### 1. Separation of Concerns
- **jobs.py**: HTTP request/response handling
- **job_service.py**: Database queries and orchestration
- **scoring_service.py**: Scoring logic and enrichment
- **rule_scoring_service.py**: Rule-based scoring algorithms

### 2. User Profile Handling
```python
# Current implementation (TODO: enhance for production)
user_profile = ScoringService._build_user_profile(user)

# In production, you should:
# - Store UserProfile data in database (new UserProfile table)
# - Allow users to update their preferences via /users/me/profile endpoint
# - Cache user profiles in Redis for performance
```

### 3. Sorting & Pagination
- Jobs returned sorted by `final` score (highest relevance first)
- Pagination applied before scoring (for performance with large datasets)
- Total count reflects total jobs available, not just paginated result

### 4. Error Handling
- 401: Authentication failures (missing/invalid token)
- 404: User not found (should not happen after successful auth)
- 422: Validation errors (bad query parameters)

## Integration with Existing System

The implementation follows existing patterns:

1. **Authentication**: Uses existing `get_current_user()` dependency
2. **Database**: Uses existing `get_session()` dependency and ORM models
3. **Schemas**: Extends existing Pydantic models with new response types
4. **Scoring**: Wraps existing `rule_scoring_service` module

## Performance Considerations

### Current Implementation
- Scores computed in-memory for each job
- Linear complexity: O(n_jobs * complexity_of_scoring)
- Suitable for: ~1000 jobs with pagination

### Future Optimizations
1. **Cache computed scores** in database
   - Add `score_final` to Job model (already done)
   - Periodically re-compute for active jobs

2. **Use vectorized scoring**
   - Batch compute embeddings
   - Use numpy/pandas for vectorized operations

3. **Implement user preference caching**
   - Store in Redis
   - Invalidate on profile updates

4. **Async job enrichment**
   - Use asyncio.gather() for parallel scoring
   - For very large result sets

## Files Modified

1. **Created**: `app/services/scoring_service.py` (150 lines)
2. **Modified**: `app/services/job_service.py` (added 70 lines)
3. **Modified**: `app/schemas/schemas.py` (added 150 lines)
4. **Modified**: `app/routers/jobs.py` (added endpoint + imports)

## Next Steps

1. ✅ Implement authenticated endpoint
2. ✅ Add score computation
3. ✅ Create proper schemas
4. ⏳ Implement user profile storage (currently reads from User model attributes)
5. ⏳ Add score caching/pre-computation
6. ⏳ Implement advanced filtering on scores
7. ⏳ Add analytics/logging for score distributions

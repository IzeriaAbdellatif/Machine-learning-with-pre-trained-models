# Quick Reference: Job Scoring

## The Three Files

### 1️⃣ `app/services/scoring.py` (NEW - 60 lines)
```
Contains: scoring_function(user, job) -> float
Purpose: Calculate job relevance (0.0-1.0)
Input: User ORM, Job ORM
Output: Score between 0.0 and 1.0
```

### 2️⃣ `app/routers/jobs.py` (MODIFIED)
```
Changed: GET /jobs endpoint
Added: Optional authentication
Added: Score computation if authenticated
New import: from app.services.scoring import scoring_function
```

### 3️⃣ `app/schemas/schemas.py` (MODIFIED)
```
Changed: JobResponse class
Added: score: Optional[float] field
Range: 0.0 to 1.0 (or None if unauthenticated)
```

---

## Flow Diagram

```
GET /jobs?...
    ↓
[Check if authenticated]
    ├─→ No Auth → Return jobs (score = null)
    └─→ Has Auth ↓
            Fetch User from DB
            ↓
            For each job:
              score = scoring_function(user, job)
              ↓
              Returns float (0.0-1.0)
            ↓
            Return jobs with scores
```

---

## Scoring Breakdown

**Base Score**: 0.5

| Factor | Points | Calculation |
|--------|--------|-------------|
| Skills | 0-0.4 | Word overlap: user bio vs job text |
| Location | 0-0.3 | Exact/substring match |
| Salary | 0-0.3 | Has salary or remuneration field |
| **MAX** | **1.0** | Clamped to 0.0-1.0 |

**Examples**:
- Skills only (4 matches): 0.5 + 0.2 = **0.7**
- Location only (exact): 0.5 + 0.3 = **0.8**
- All factors: 0.5 + 0.4 + 0.3 + 0.3 = **1.5** → clamped to **1.0**

---

## API Examples

### Example 1: Unauthenticated
```bash
curl http://localhost:8000/jobs?limit=2
```
Response:
```json
{
  "items": [
    {"id": "1", "title": "Dev", "score": null},
    {"id": "2", "title": "Data", "score": null}
  ]
}
```

### Example 2: Authenticated
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/jobs?limit=2
```
Response:
```json
{
  "items": [
    {"id": "1", "title": "Dev", "score": 0.85},
    {"id": "2", "title": "Data", "score": 0.45}
  ]
}
```

---

## Frontend Implementation

```javascript
// JobCard.tsx
export const JobCard = ({ job }) => {
  return (
    <div className="job-card">
      <h3>{job.title}</h3>
      <p>{job.company}</p>
      
      {/* Show score only if authenticated */}
      {job.score !== null && (
        <div className="relevance-score">
          Match: {Math.round(job.score * 100)}%
          <ProgressBar value={job.score} max={1.0} />
        </div>
      )}
    </div>
  );
};
```

---

## Modifying the Scoring

To change how scoring works, edit **only** `app/services/scoring.py`:

```python
def scoring_function(user: User, job: Job) -> float:
    score = 0.5
    
    # Example: Add job type preference
    if user.preferred_job_type == job.job_type:
        score += 0.2
    
    # Example: Heavy weight location
    if user.location == job.location:
        score += 0.5
    
    return min(1.0, score)
```

Changes apply **automatically** to all API calls.

---

## No Changes To:
✅ Database schema
✅ JSON files
✅ Authentication system
✅ Other endpoints
✅ Job model

---

## What Changed:
✅ GET /jobs endpoint (added scoring)
✅ JobResponse schema (added score field)
✅ New scoring.py service

---

## Testing Checklist

- [ ] Unauthenticated request works (score = null)
- [ ] Authenticated request works (score = float)
- [ ] Score is between 0.0 and 1.0
- [ ] Different users get different scores
- [ ] Scores change when user profile changes
- [ ] No database changes
- [ ] JSON files untouched
- [ ] Other endpoints unaffected

---

## Dependencies

None! Uses only existing:
- FastAPI
- SQLAlchemy
- JWT authentication
- Pydantic

---

## Performance

- ✅ O(n) complexity (one pass per job)
- ✅ No database queries per job
- ✅ No caching overhead
- ✅ Suitable for ~100 jobs per request

---

## Summary

A **simple, focused solution**:
- Single function: `scoring_function(user, job)`
- Runs: Only in `GET /jobs` when authenticated
- Computes: Fresh score dynamically each request
- Returns: Score field in job response (0.0-1.0)
- Storage: None (computed on-the-fly)
- Changes: Only 3 files, minimal modifications

**Ready to deploy! 🚀**

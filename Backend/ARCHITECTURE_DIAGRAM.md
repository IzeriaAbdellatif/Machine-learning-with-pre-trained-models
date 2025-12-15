# Architecture Diagram: Job Scoring System

## System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT REQUEST                       │
│   GET /jobs?title=Python&limit=10                            │
│   [Optional: Authorization: Bearer <token>]                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI ROUTER                            │
│              (app/routers/jobs.py)                           │
│                                                               │
│  @router.get("/")                                            │
│  async def search_jobs(...):                                 │
└────────┬──────────────────────────────────────────────┬─────┘
         │                                              │
         ▼                                              ▼
    ┌─────────────┐                          ┌──────────────────┐
    │ Query Jobs  │                          │ Extract Auth     │
    │ from DB     │                          │ from Token       │
    │ (filters)   │                          │ (if present)     │
    └─────┬───────┘                          └────────┬─────────┘
          │                                           │
          │                    ┌──────────────────────┘
          │                    │
          │                    ▼
          │          ┌──────────────────────┐
          │          │ Has Token?           │
          │          └──┬──────────────────┬┘
          │             │ No               │ Yes
          │             │                  ▼
          │             │          ┌────────────────────┐
          │             │          │ Get User from DB   │
          │             │          │ Using user_id      │
          │             │          └────────┬───────────┘
          │             │                   │
          │  ┌──────────┴────────────────────┘
          │  │
          ▼  ▼
    ┌────────────────────────────────────────┐
    │ Apply Scoring (if user exists)         │
    │                                        │
    │ For each job:                          │
    │   score = scoring_function(user, job)  │
    │                                        │
    │ scoring_function:                      │
    │   • Skills match (0-0.4)               │
    │   • Location match (0-0.3)             │
    │   • Salary presence (0-0.3)            │
    │   • Base score (0.5)                   │
    │   • Clamp to 0.0-1.0                   │
    └────────┬─────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────┐
    │ Return Response          │
    │                          │
    │ JobsListResponse {       │
    │   items: [               │
    │     {                    │
    │       id, title, ...     │
    │       score: 0.75        │  ← Added field
    │     }                    │
    │   ]                      │
    │ }                        │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Return to CLIENT (JSON)  │
    └──────────────────────────┘
```

---

## Component Interaction

```
┌──────────────────────────────────────────────────────────────┐
│                        FASTAPI                               │
│                    (app/routers/jobs.py)                     │
│                                                              │
│  • Handles HTTP requests                                    │
│  • Extracts authentication                                  │
│  • Orchestrates job_service & scoring                       │
└────────────┬───────────────────────────────┬────────────────┘
             │                               │
             ▼                               ▼
    ┌──────────────────┐         ┌───────────────────┐
    │  job_service     │         │  scoring.py       │
    │                  │         │                   │
    │ • search_jobs()  │────────▶│ scoring_function()│
    │ • get_job()      │         │                   │
    │                  │         │ Pure function:    │
    └────────┬─────────┘         │ user + job → score│
             │                   └───────────────────┘
             ▼
    ┌──────────────────┐
    │   Database       │
    │  (ORM models)    │
    │                  │
    │ • User           │
    │ • Job            │
    │ • SavedJob       │
    └──────────────────┘
```

---

## Data Flow for Authenticated Request

```
User                Token              DB              Scoring          Response
 │                   │                  │                │                │
 ├─GET /jobs────────►│                  │                │                │
 │                   │                  │                │                │
 │                ▶  ├──Get User───────►│                │                │
 │                   │  (user_id)       │                │                │
 │                   │              User◄───────────────┤│                │
 │                   │              Model               ││                │
 │                   │                  │                │                │
 │                ▶  ├──Get Jobs───────►│                │                │
 │                   │  (filters)       │                │                │
 │                   │              Jobs◄──────┐         │                │
 │                   │              List       │         │                │
 │                   │                  │  ┌───┴─────────┴────┐           │
 │                   │                  │  │ For each Job:   │           │
 │                   │                  │  │ score=          │           │
 │                   │                  │  │ scoring_func()  │           │
 │                   │                  │  │                 │           │
 │                   │                  │  └────────┬────────┘           │
 │                   │                  │           │                    │
 │                   │◄─────────────────Jobs with Scores─────────────────┤
 │                   │                           │                       │
 │◄──────JSON────────┤ (id, title, score: 0.75) │                       │
 │                   │                           │                       │
```

---

## File Dependencies

```
jobs.py (Router)
    ├─ imports scoring.scoring_function
    │
    ├─ calls job_service.search_jobs()
    │
    ├─ calls get_current_user() [existing auth]
    │
    └─ calls scoring_function(user, job)
            │
            └─ accepts User ORM model
            │
            └─ accepts Job ORM model
            │
            └─ returns float (0.0-1.0)

schemas.py
    └─ JobResponse
        └─ includes score: Optional[float] field

scoring.py
    └─ scoring_function(user, job)
        ├─ Pure function (no side effects)
        ├─ Uses user.bio, user.location
        ├─ Uses job.title, job.description, job.location
        └─ Returns float
```

---

## Request Without Authentication

```
GET /jobs?limit=10
    │
    ├─ current_user = None (no token)
    │
    ├─ search_jobs() returns jobs
    │
    └─ Skip scoring (no user)
            │
            └─ Return jobs with score = null
```

---

## Request With Authentication

```
GET /jobs?limit=10
Authorization: Bearer eyJhbGc...
    │
    ├─ Extract user_id from token
    │
    ├─ Fetch User from database
    │
    ├─ search_jobs() returns jobs
    │
    ├─ For each job:
    │   └─ score = scoring_function(user, job)
    │       └─ Computes 0.0-1.0 score
    │
    └─ Return jobs with computed scores
```

---

## Scoring Algorithm Flow

```
scoring_function(user, job)
    │
    ├─ Initialize: score = 0.5
    │
    ├─ FACTOR 1: Skills
    │   ├─ job_text = job.title + company + description
    │   ├─ user_words = tokenize(user.bio)
    │   ├─ job_words = tokenize(job_text)
    │   ├─ skill_matches = count(user_words ∩ job_words)
    │   └─ score += min(0.4, skill_matches × 0.05)
    │
    ├─ FACTOR 2: Location  
    │   ├─ IF exact_match(user.location, job.location)
    │   │   └─ score += 0.3
    │   ├─ ELSE_IF substring_match(...)
    │   │   └─ score += 0.15
    │   └─ ELSE
    │       └─ no change
    │
    ├─ FACTOR 3: Salary
    │   ├─ IF has_salary(job)
    │   │   └─ score += 0.3
    │   └─ ELSE
    │       └─ no change
    │
    └─ Return clamp(score, 0.0, 1.0)
```

---

## Score Distribution Example

```
Score Range    Jobs    Example Titles
0.00-0.25      10%     Unrelated positions
0.25-0.50      20%     Some match
0.50-0.75      40%     Good match        ← Most jobs
0.75-0.90      20%     Excellent match
0.90-1.00       5%     Perfect match
```

---

## Error Handling Flow

```
GET /jobs (authenticated)
    │
    ├─ get_current_user() 
    │   ├─ Valid token → OK
    │   └─ Invalid token → 401 error
    │
    ├─ Fetch User
    │   ├─ User found → OK
    │   └─ User not found → Skip scoring
    │
    ├─ search_jobs()
    │   ├─ Query succeeds → OK
    │   └─ Query fails → 500 error
    │
    └─ Return response
```

---

## No Changes To (Immutable)

```
┌─────────────────┐
│  Database       │
│  Schema         │  ← Untouched
└─────────────────┘

┌─────────────────┐
│  JSON Files     │  ← Untouched
│  (seed data)    │
└─────────────────┘

┌─────────────────┐
│  Job Models     │  ← Only schema modified
│  (schema layer) │
└─────────────────┘

┌─────────────────┐
│  Auth System    │  ← Uses existing JWT
│                 │
└─────────────────┘

┌─────────────────┐
│  Other Routes   │  ← Completely unchanged
│  /users, etc    │
└─────────────────┘
```

---

This architecture ensures:
- ✅ Clean separation of concerns
- ✅ No side effects
- ✅ Easy to test
- ✅ Easy to modify
- ✅ No unintended changes

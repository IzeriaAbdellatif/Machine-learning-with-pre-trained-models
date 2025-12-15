"""
Example: Using the Job Recommendations API with Score-Based Ranking

This module demonstrates how to use the new /jobs/me/recommendations endpoint
to get personalized job recommendations with detailed relevance scoring.
"""

import requests
import json
from typing import Dict, List, Optional


class JobRecommendationsClient:
    """Client for interacting with the job recommendations API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None

    def register(self, email: str, password: str, name: str) -> Dict:
        """
        Register a new user and obtain authentication token.

        Args:
            email: User email address
            password: User password (min 8 chars)
            name: User full name

        Returns:
            Dictionary containing access_token, token_type, and user info

        Example:
            >>> client = JobRecommendationsClient()
            >>> response = client.register(
            ...     email="john@example.com",
            ...     password="SecurePass123",
            ...     name="John Doe"
            ... )
            >>> print(response['access_token'])
        """
        url = f"{self.base_url}/auth/register"
        payload = {
            "email": email,
            "password": password,
            "name": name,
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        self.token = data["access_token"]

        print(f"✅ User registered: {data['user']['email']}")
        print(f"✅ Token obtained: {self.token[:20]}...")

        return data

    def get_recommendations(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by_score: bool = True,
    ) -> List[Dict]:
        """
        Get personalized job recommendations with relevance scores.

        Args:
            skip: Number of results to skip (pagination)
            limit: Number of results to return (1-100)
            sort_by_score: Already sorted by API, just noted for clarity

        Returns:
            List of jobs enriched with relevance scores

        Raises:
            ValueError: If not authenticated
            requests.HTTPError: If API returns error

        Example:
            >>> client = JobRecommendationsClient()
            >>> client.register(...)  # Setup auth
            >>> jobs = client.get_recommendations(skip=0, limit=10)
            >>> for job in jobs:
            ...     print(f"{job['title']}: {job['score']['final']:.2%}")
        """
        if not self.token:
            raise ValueError("Not authenticated. Call register() first.")

        url = f"{self.base_url}/jobs/me/recommendations"
        headers = {"Authorization": f"Bearer {self.token}"}
        params = {"skip": skip, "limit": limit}

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        return data["items"]

    def get_recommendations_paginated(
        self,
        page_size: int = 10,
        max_pages: Optional[int] = None,
    ):
        """
        Generator for iterating through paginated job recommendations.

        Args:
            page_size: Number of results per page
            max_pages: Maximum pages to fetch (None = all)

        Yields:
            Each job from paginated results

        Example:
            >>> client = JobRecommendationsClient()
            >>> client.register(...)
            >>> for job in client.get_recommendations_paginated(page_size=20):
            ...     print(f"{job['title']} ({job['score']['final']:.1%})")
        """
        page = 0
        while True:
            if max_pages and page >= max_pages:
                break

            skip = page * page_size
            jobs = self.get_recommendations(skip=skip, limit=page_size)

            if not jobs:
                break

            for job in jobs:
                yield job

            page += 1

    @staticmethod
    def print_job_with_score(job: Dict) -> None:
        """
        Pretty print a job with its relevance score breakdown.

        Args:
            job: Job dictionary with score information

        Example:
            >>> job = {
            ...     "title": "Senior Python Developer",
            ...     "company": "Tech Corp",
            ...     "location": "Remote",
            ...     "score": {
            ...         "skills": 0.95,
            ...         "mode_travail": 1.0,
            ...         "location": 1.0,
            ...         "remuneration": 0.9,
            ...         "embedding": 0.88,
            ...         "final": 0.92
            ...     }
            ... }
            >>> JobRecommendationsClient.print_job_with_score(job)
        """
        score = job["score"]
        final_score = score["final"]

        # Color coding based on final score
        if final_score >= 0.8:
            rating = "🟢 EXCELLENT"
        elif final_score >= 0.6:
            rating = "🟡 GOOD"
        elif final_score >= 0.4:
            rating = "🟠 FAIR"
        else:
            rating = "🔴 POOR"

        print(f"\n{rating} [{final_score:.1%}]")
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Mode: {job.get('mode_travail', 'N/A')}")

        # Score breakdown
        print(f"  Score Breakdown:")
        print(f"    • Skills:       {score['skills']:.1%}")
        print(f"    • Work Mode:    {score['mode_travail']:.1%}")
        print(f"    • Location:     {score['location']:.1%}")
        print(f"    • Salary:       {score['remuneration']:.1%}")
        print(f"    • Semantic:     {score['embedding']:.1%}")
        print(f"    • FINAL SCORE:  {score['final']:.1%}")

    @staticmethod
    def filter_by_score(
        jobs: List[Dict],
        min_score: float = 0.0,
        max_score: float = 1.0,
    ) -> List[Dict]:
        """
        Filter jobs by final score range.

        Args:
            jobs: List of job dictionaries
            min_score: Minimum final score (0.0-1.0)
            max_score: Maximum final score (0.0-1.0)

        Returns:
            Filtered list of jobs

        Example:
            >>> jobs = client.get_recommendations(limit=100)
            >>> high_relevance = JobRecommendationsClient.filter_by_score(
            ...     jobs, min_score=0.8
            ... )
            >>> print(f"Found {len(high_relevance)} highly relevant jobs")
        """
        return [
            job
            for job in jobs
            if min_score <= job["score"]["final"] <= max_score
        ]

    @staticmethod
    def filter_by_component(
        jobs: List[Dict],
        component: str,
        min_score: float = 0.0,
    ) -> List[Dict]:
        """
        Filter jobs by a specific score component.

        Args:
            jobs: List of job dictionaries
            component: Score component ('skills', 'mode_travail', 'location', etc.)
            min_score: Minimum score for component

        Returns:
            Jobs where component score >= min_score

        Example:
            >>> jobs = client.get_recommendations(limit=100)
            >>> remote_jobs = JobRecommendationsClient.filter_by_component(
            ...     jobs, component='mode_travail', min_score=0.9
            ... )
            >>> print(f"Found {len(remote_jobs)} remote-compatible jobs")
        """
        return [
            job
            for job in jobs
            if job["score"].get(component, 0.0) >= min_score
        ]

    @staticmethod
    def group_by_score_band(jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group jobs by score band for analysis.

        Args:
            jobs: List of job dictionaries

        Returns:
            Dictionary with keys: 'excellent', 'good', 'fair', 'poor'

        Example:
            >>> jobs = client.get_recommendations(limit=100)
            >>> bands = JobRecommendationsClient.group_by_score_band(jobs)
            >>> for band, job_list in bands.items():
            ...     print(f"{band.upper()}: {len(job_list)} jobs")
        """
        bands = {
            "excellent": [],  # 0.8+
            "good": [],       # 0.6-0.8
            "fair": [],       # 0.4-0.6
            "poor": [],       # <0.4
        }

        for job in jobs:
            score = job["score"]["final"]
            if score >= 0.8:
                bands["excellent"].append(job)
            elif score >= 0.6:
                bands["good"].append(job)
            elif score >= 0.4:
                bands["fair"].append(job)
            else:
                bands["poor"].append(job)

        return bands


def main():
    """Example usage of the JobRecommendationsClient."""

    print("=" * 60)
    print("Job Recommendations API - Example Usage")
    print("=" * 60)

    client = JobRecommendationsClient()

    # Step 1: Register/Login
    print("\n[1] Registering user...")
    try:
        client.register(
            email="example@test.com",
            password="TestPassword123",
            name="Example User",
        )
    except requests.exceptions.HTTPError as e:
        if "already exists" in str(e):
            print("User already exists, using existing account")
            # In real scenario, login instead
        else:
            raise

    # Step 2: Get recommendations
    print("\n[2] Fetching personalized job recommendations...")
    jobs = client.get_recommendations(skip=0, limit=20)
    print(f"✅ Retrieved {len(jobs)} jobs")

    # Step 3: Display top recommendations
    print("\n[3] Top 5 recommendations (by relevance score):")
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Relevance Score: {job['score']['final']:.1%}")
        print(f"   Location: {job['location']}")
        print(f"   Skills Match: {job['score']['skills']:.1%}")

    # Step 4: Analyze score distribution
    print("\n[4] Score analysis for all jobs:")
    bands = JobRecommendationsClient.group_by_score_band(jobs)
    for band, job_list in bands.items():
        print(f"   {band.capitalize():12} ({len(job_list):3} jobs)")

    # Step 5: Filter by score component
    print("\n[5] Jobs with high skills match (>80%):")
    high_skills = JobRecommendationsClient.filter_by_component(
        jobs, "skills", min_score=0.8
    )
    for job in high_skills[:3]:
        print(f"   • {job['title']}: {job['score']['skills']:.1%} match")

    # Step 6: Detailed view of best match
    if jobs:
        print("\n[6] Detailed view - Best match:")
        best_job = jobs[0]
        client.print_job_with_score(best_job)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

"""
SCORE BREAKDOWN EXPLANATION
=============================

Final Score Composition:
    final = 0.6 × embedding + 0.25 × skills + 0.10 × mode + 0.05 × location

Components:
  • embedding (0-1): ML-based semantic similarity between job and user profile
  • skills (0-1): How many user skills match job requirements
  • mode_travail (0-1): Work mode preference match
  • location (0-1): Location preference match
  • remuneration (0-1): Salary alignment

Example Interpretations:
  • 0.90+ EXCELLENT: Highly relevant, strongly recommended
  • 0.70-0.89 GOOD: Good match, worth reviewing
  • 0.50-0.69 FAIR: Some relevance, may be worth exploring
  • <0.50 POOR: Low relevance, consider other options

Usage Scenarios:
  1. Find top jobs: jobs[0] is highest relevance
  2. Filter good matches: filter_by_score(jobs, min_score=0.7)
  3. Find remote jobs: filter_by_component(jobs, 'mode_travail', min_score=0.9)
  4. Analyze distribution: group_by_score_band(jobs)
"""

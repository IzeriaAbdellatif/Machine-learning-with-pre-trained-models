// User type
export interface User {
  id: string;
  email: string;
  name: string;
  skills?: string[];
  location?: string;
  createdAt?: string;
  updatedAt?: string;
}

// Job type - score is provided by backend, never computed on frontend
export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  skills: string[];
  salary?: string;
  type?: string;
  postedAt?: string;
  url?: string;
  score_final: number;
  
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface JobSearchParams {
  title?: string;
  location?: string;
  skills?: string;
  skip?: number;
  limit?: number;
}

// Saved job type
export interface SavedJob {
  id: string;
  jobId: string;
  job: Job;
  saved_at: string;
}

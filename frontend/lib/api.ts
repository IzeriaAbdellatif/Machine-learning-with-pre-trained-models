import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { getToken, removeToken, setToken } from './auth';

// Base URL for the API - update this to match your backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Axios instance with interceptors for authentication
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies in cross-origin requests
});

// Request interceptor to inject authorization token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    console.log('[Axios] Token found:', !!token, 'URL:', config.url);
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('[Axios] Authorization header set');
    } else {
      console.log('[Axios] No token or no headers available');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // If unauthorized, remove token and redirect to login (but delay to allow logs)
    if (error.response?.status === 401) {
      console.error('[Axios] 401 Unauthorized - removing token and will redirect');
      removeToken();
      if (typeof window !== 'undefined') {
        // Delay redirect to allow debugging
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// ==================== AUTH API ====================

import {
  LoginCredentials,
  RegisterCredentials,
  AuthResponse,
  User,
  Job,
  JobSearchParams,
  SavedJob,
} from '@/types';

/**
 * Register a new user
 */
export const register = async (credentials: RegisterCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/register', credentials);
  const data = response.data;
  if (data?.access_token) {
    setToken(data.access_token);
  }
  return data;
};

/**
 * Login user
 */
export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await api.post<AuthResponse>('/auth/login', credentials);
  const data = response.data;
  if (data?.access_token) {
    setToken(data.access_token);
  }
  return data;
};

/**
 * Logout user
 */
export const logout = async (): Promise<void> => {
  await api.post('/auth/logout');
  removeToken();
};

/**
 * Get current user
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me');
  return response.data;
};

// ==================== USERS API ====================

/**
 * Get user by ID
 */
export const getUser = async (id: string): Promise<User> => {
  const response = await api.get<User>(`/users/${id}`);
  return response.data;
};

/**
 * Update user
 */
export const updateUser = async (id: string, data: Partial<User>): Promise<User> => {
  const response = await api.put<User>(`/users/${id}`, data);
  return response.data;
};

/**
 * Delete user
 */
export const deleteUser = async (id: string): Promise<void> => {
  await api.delete(`/users/${id}`);
};

// ==================== JOBS API ====================

/**
 * Search jobs with optional filters
 * Note: Score is returned by backend, never computed on frontend
 */
export const searchJobs = async (
  params?: JobSearchParams
): Promise<{ items: Job[]; total: number; skip: number; limit: number }> => {
  const response = await api.get<{ items: Job[]; total: number; skip: number; limit: number }>(
    '/jobs',
    { params }
  );
  console.log(
    '[API] searchJobs params:',
    params,
    'returned:',
    response.data.items.length,
    'total:',
    response.data.total
  );
  return response.data;
};

/**
 * Get job by ID
 * Note: Score is returned by backend, never computed on frontend
 */
export const getJob = async (id: string): Promise<Job> => {
  const response = await api.get<Job>(`/jobs/${id}`);
  return response.data;
};

// ==================== SAVED JOBS API ====================

/**
 * Save a job
 */
export const saveJob = async (jobId: string): Promise<SavedJob> => {
  const response = await api.post<SavedJob>(`/saved-jobs/${jobId}`);
  return response.data;
};

/**
 * Get all saved jobs
 */
export const getSavedJobs = async (): Promise<SavedJob[]> => {
  const response = await api.get<{ items: SavedJob[], total: number, skip: number, limit: number }>('/saved-jobs');
  console.log('[API] getSavedJobs returned:', response.data.items.length, 'total:', response.data.total);
  return response.data.items;
};

/**
 * Remove a saved job
 */
export const removeSavedJob = async (jobId: string): Promise<void> => {
  await api.delete(`/saved-jobs/${jobId}`);
};

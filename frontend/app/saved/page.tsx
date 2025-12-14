'use client';

import { useState, useEffect, useCallback } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import JobCard from '@/components/JobCard';
import { getSavedJobs } from '@/lib/api';
import { SavedJob } from '@/types';
import Link from 'next/link';

function SavedJobsContent() {
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSavedJobs = useCallback(async () => {
    setLoading(true);
    setError('');
    
    try {
      const data = await getSavedJobs();
      // Sort by saved date (most recent first)
      const sorted = [...data].sort(
        (a, b) => new Date(b.saved_at).getTime() - new Date(a.saved_at).getTime()
      );
      setSavedJobs(sorted);
    } catch (err) {
      console.error('Failed to fetch saved jobs:', err);
      setError('Failed to load saved jobs. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSavedJobs();
  }, [fetchSavedJobs]);

  const handleSaveToggle = () => {
    // Refresh the list when a job is unsaved
    fetchSavedJobs();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          <p className="text-gray-500">Loading saved jobs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Saved Jobs</h1>
          <p className="mt-2 text-gray-600">
            Jobs you&apos;ve bookmarked for later review
          </p>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Stats */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 mb-8">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg
                className="w-6 h-6 text-yellow-600"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{savedJobs.length}</p>
              <p className="text-sm text-gray-500">Saved Jobs</p>
            </div>
          </div>
        </div>

        {/* Saved Jobs Grid */}
        {savedJobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedJobs.map((savedJob) => (
              <div key={savedJob.id} className="relative">
                <JobCard
                  job={savedJob.job}
                  isSaved={true}
                  onSaveToggle={handleSaveToggle}
                  showSaveButton={true}
                  saved_at={savedJob.saved_at}
                />
                
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center border border-gray-100">
            <svg
              className="w-16 h-16 text-gray-300 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No saved jobs yet
            </h3>
            <p className="text-gray-500 mb-6">
              Start browsing and save jobs you&apos;re interested in.
              <br />
              They&apos;ll appear here for easy access.
            </p>
            <Link
              href="/jobs"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              Browse Jobs
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SavedJobsPage() {
  return (
    <ProtectedRoute>
      <SavedJobsContent />
    </ProtectedRoute>
  );
}

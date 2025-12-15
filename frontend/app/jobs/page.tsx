'use client';

import { useState, useEffect, FormEvent } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import JobCard from '@/components/JobCard';
import { searchJobs, getSavedJobs } from '@/lib/api';
import { Job, JobSearchParams } from '@/types';

function JobsContent() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 10;
  const [savedMap, setSavedMap] = useState<Record<string, { isSaved: boolean; saved_at?: string }>>({});
  
  // Search filters
  const [title, setTitle] = useState('');
  const [location, setLocation] = useState('');
  const [skills, setSkills] = useState('');
  
  // Applied filters (for display)
  const [appliedFilters, setAppliedFilters] = useState<JobSearchParams>({});

  const fetchJobs = async (params?: JobSearchParams) => {
    setLoading(true);
    setError('');
    
    try {
      const [response, savedItems] = await Promise.all([
        searchJobs({
          skip: page * PAGE_SIZE,
          limit: PAGE_SIZE,
          ...params,
        }),
        getSavedJobs(),
      ]);
      const { items, total } = response;
      console.log('[JobsPage] Fetched jobs:', items.length, 'total:', total);
      // Jobs come with scores from backend - sort by score
      const sortedJobs = [...items].sort((a, b) => b.score - a.score);
      setJobs(sortedJobs);
      setTotal(total);
      const map: Record<string, { isSaved: boolean; saved_at?: string }> = {};
      savedItems.forEach((sj) => {
        map[sj.job.id] = { isSaved: true, saved_at: sj.saved_at };
      });
      setSavedMap(map);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
      setError('Failed to load jobs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(appliedFilters);
  }, [page]);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    
    const params: JobSearchParams = {};
    if (title.trim()) params.title = title.trim();
    if (location.trim()) params.location = location.trim();
    if (skills.trim()) params.skills = skills.trim();
    
    setAppliedFilters(params);
    setPage(0);
    fetchJobs({ ...params, skip: 0, limit: PAGE_SIZE });
  };

  const handleClearFilters = () => {
    setTitle('');
    setLocation('');
    setSkills('');
    setAppliedFilters({});
    setPage(0);
    fetchJobs({ skip: 0, limit: PAGE_SIZE });
  };

  const hasFilters = Object.keys(appliedFilters).length > 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Find Jobs</h1>
          <p className="mt-2 text-gray-600">
            Search and filter through available job opportunities
          </p>
        </div>

        {/* Search Form */}
        <form
          onSubmit={handleSearch}
          className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label
                htmlFor="title"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Job Title
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Software Engineer"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label
                htmlFor="location"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Location
              </label>
              <input
                id="location"
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. New York, Remote"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
              />
            </div>

            <div>
              <label
                htmlFor="skills"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Skills
              </label>
              <input
                id="skills"
                type="text"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                placeholder="e.g. Python, React"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
              />
            </div>

            <div className="flex items-end gap-2">
              <button
                type="submit"
                className="flex-1 bg-primary-600 text-white px-6 py-2.5 rounded-lg hover:bg-primary-700 transition-colors font-medium"
              >
                Search
              </button>
              {hasFilters && (
                <button
                  type="button"
                  onClick={handleClearFilters}
                  className="px-4 py-2.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-gray-600"
                  title="Clear filters"
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
          </div>

          {/* Active Filters */}
          {hasFilters && (
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="text-sm text-gray-500">Active filters:</span>
              {appliedFilters.title && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                  Title: {appliedFilters.title}
                </span>
              )}
              {appliedFilters.location && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                  Location: {appliedFilters.location}
                </span>
              )}
              {appliedFilters.skills && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                  Skills: {appliedFilters.skills}
                </span>
              )}
            </div>
          )}
        </form>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
              <p className="text-gray-500">Searching jobs...</p>
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && (
          <>
            {/* Results count */}
            <div className="mb-6 flex items-center justify-between">
              <p className="text-gray-600">
                Found <span className="font-semibold">{total}</span> jobs
                {hasFilters && ' matching your criteria'}
              </p>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Sorted by match score (highest first)</span>
                <span>
                  Page {page + 1} of {totalPages} (total {total})
                </span>
              </div>
            </div>

            {/* Pagination controls */}
            <div className="mb-6 flex items-center gap-3">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className={`px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  page === 0
                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page + 1 >= totalPages}
                className={`px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  page + 1 >= totalPages
                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                Next
              </button>
            </div>

            {/* Jobs Grid */}
            {jobs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    isSaved={!!savedMap[job.id]?.isSaved}
                    saved_at={savedMap[job.id]?.saved_at}
                  />
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
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No jobs found
                </h3>
                <p className="text-gray-500 mb-4">
                  {hasFilters
                    ? 'Try adjusting your search filters to find more results.'
                    : 'There are no jobs available at the moment.'}
                </p>
                {hasFilters && (
                  <button
                    onClick={handleClearFilters}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
                  >
                    Clear all filters
                  </button>
                )}
              </div>
            )}

            {/* Pagination controls (bottom) */}
            <div className="mt-8 flex items-center gap-3 justify-end">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className={`px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  page === 0
                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page + 1 >= totalPages}
                className={`px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  page + 1 >= totalPages
                    ? 'border-gray-200 text-gray-400 cursor-not-allowed'
                    : 'border-gray-300 text-gray-700 hover:bg-gray-50'
                }`}
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function JobsPage() {
  return (
    <ProtectedRoute>
      <JobsContent />
    </ProtectedRoute>
  );
}

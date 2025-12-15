'use client';

import { useState, FormEvent, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { register } from '@/lib/api';

export default function RegisterProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Basic info from previous step
  const [basicData, setBasicData] = useState<{ email: string; password: string; name: string } | null>(null);

  // Profile fields
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [bio, setBio] = useState('');
  const [skills, setSkills] = useState('');
  const [softSkills, setSoftSkills] = useState('');
  const [preferredLocations, setPreferredLocations] = useState('');
  const [preferredModeTravail, setPreferredModeTravail] = useState('');
  const [minRemuneration, setMinRemuneration] = useState('');

  useEffect(() => {
    // Get basic data from sessionStorage
    const data = sessionStorage.getItem('registerData');
    if (!data) {
      // If no data, redirect back to register
      router.push('/register');
      return;
    }
    setBasicData(JSON.parse(data));
  }, [router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!basicData) {
      setError('Registration data not found. Please start over.');
      return;
    }

    setLoading(true);

    try {
      // Call register with all data
      await register({
        email: basicData.email,
        password: basicData.password,
        name: basicData.name,
        phone: phone || undefined,
        location: location || undefined,
        bio: bio || undefined,
        skills: skills || undefined,
        soft_skills: softSkills || undefined,
        preferred_locations: preferredLocations || undefined,
        preferred_mode_travail: preferredModeTravail || undefined,
        min_remuneration: minRemuneration ? parseFloat(minRemuneration) : undefined,
      });

      // Clear session storage
      sessionStorage.removeItem('registerData');
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = async () => {
    if (!basicData) return;

    setLoading(true);
    try {
      // Register with just basic info
      await register({
        email: basicData.email,
        password: basicData.password,
        name: basicData.name,
      });

      sessionStorage.removeItem('registerData');
      router.push('/dashboard');
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Registration failed. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!basicData) {
    return null; // Will redirect
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto w-12 h-12 bg-primary-600 rounded-xl flex items-center justify-center mb-4">
            <svg
              className="w-7 h-7 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Complete your profile</h2>
          <p className="mt-2 text-sm text-gray-600">
            Help us personalize your job recommendations
          </p>
        </div>

        {/* Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div
              className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
              role="alert"
            >
              {error}
            </div>
          )}

          <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Contact Information</h3>
            
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="+212 6 12 34 56 78"
              />
            </div>

            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                Current Location
              </label>
              <input
                id="location"
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="Casablanca, Morocco"
              />
            </div>

            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-1">
                Bio / Summary
              </label>
              <textarea
                id="bio"
                rows={3}
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="Brief description about yourself..."
              />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Skills & Experience</h3>
            
            <div>
              <label htmlFor="skills" className="block text-sm font-medium text-gray-700 mb-1">
                Technical Skills
              </label>
              <input
                id="skills"
                type="text"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="Python, SQL, Machine Learning, Power BI"
              />
              <p className="mt-1 text-xs text-gray-500">Separate skills with commas</p>
            </div>

            <div>
              <label htmlFor="softSkills" className="block text-sm font-medium text-gray-700 mb-1">
                Soft Skills
              </label>
              <input
                id="softSkills"
                type="text"
                value={softSkills}
                onChange={(e) => setSoftSkills(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="Travail en équipe, Communication, Autonomie"
              />
              <p className="mt-1 text-xs text-gray-500">Separate skills with commas</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Job Preferences</h3>
            
            <div>
              <label htmlFor="preferredLocations" className="block text-sm font-medium text-gray-700 mb-1">
                Preferred Locations
              </label>
              <input
                id="preferredLocations"
                type="text"
                value={preferredLocations}
                onChange={(e) => setPreferredLocations(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="Casablanca, Rabat, Remote"
              />
              <p className="mt-1 text-xs text-gray-500">Separate locations with commas</p>
            </div>

            <div>
              <label htmlFor="preferredModeTravail" className="block text-sm font-medium text-gray-700 mb-1">
                Preferred Work Mode
              </label>
              <input
                id="preferredModeTravail"
                type="text"
                value={preferredModeTravail}
                onChange={(e) => setPreferredModeTravail(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="remote, hybride, presentiel"
              />
              <p className="mt-1 text-xs text-gray-500">Separate modes with commas</p>
            </div>

            <div>
              <label htmlFor="minRemuneration" className="block text-sm font-medium text-gray-700 mb-1">
                Minimum Expected Salary
              </label>
              <input
                id="minRemuneration"
                type="number"
                value={minRemuneration}
                onChange={(e) => setMinRemuneration(e.target.value)}
                className="appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors"
                placeholder="6000"
              />
              <p className="mt-1 text-xs text-gray-500">Monthly salary in MAD</p>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              type="button"
              onClick={handleSkip}
              disabled={loading}
              className="flex-1 py-3 px-4 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Skip for now
            </button>
            
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating account...</span>
                </div>
              ) : (
                'Complete Registration'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

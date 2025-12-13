const TOKEN_KEY = 'auth_token';

/**
 * Set the authentication token in localStorage
 */
export const setToken = (token: string): void => {
  try {
    if (typeof window !== 'undefined') {
      localStorage.setItem(TOKEN_KEY, token);
      console.log('[Auth] Token saved to localStorage');
    }
  } catch (e) {
    console.error('[Auth] Failed to save token:', e);
  }
};

/**
 * Get the authentication token from localStorage
 */
export const getToken = (): string | undefined => {
  try {
    if (typeof window === 'undefined') return undefined;
    const token = localStorage.getItem(TOKEN_KEY);
    console.log('[Auth] Token from localStorage:', !!token);
    return token || undefined;
  } catch (e) {
    console.error('[Auth] Failed to get token:', e);
    return undefined;
  }
};

/**
 * Remove the authentication token from localStorage
 */
export const removeToken = (): void => {
  try {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
      console.log('[Auth] Token removed from localStorage');
    }
  } catch (e) {
    console.error('[Auth] Failed to remove token:', e);
  }
};

/**
 * Check if user is authenticated (has valid token)
 */
export const isAuthenticated = (): boolean => {
  const token = getToken();
  return !!token;
};

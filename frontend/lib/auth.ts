import Cookies from 'js-cookie';

const TOKEN_KEY = 'auth_token';

/**
 * Set the authentication token in cookies
 * Using cookies with secure settings for better security
 */
export const setToken = (token: string): void => {
  Cookies.set(TOKEN_KEY, token, {
    expires: 7, // 7 days
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
  });
};

/**
 * Get the authentication token from cookies
 */
export const getToken = (): string | undefined => {
  return Cookies.get(TOKEN_KEY);
};

/**
 * Remove the authentication token from cookies
 */
export const removeToken = (): void => {
  Cookies.remove(TOKEN_KEY);
};

/**
 * Check if user is authenticated (has valid token)
 */
export const isAuthenticated = (): boolean => {
  const token = getToken();
  return !!token;
};

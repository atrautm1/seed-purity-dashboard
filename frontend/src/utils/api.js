// src/utils/api.js

export async function apiFetch(url, options = {}) {
  // Retrieve token from storage
  const token = localStorage.getItem('auth_token')

  // Setup headers object
  const headers = options.headers || {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Note: If sending FormData, do NOT set 'Content-Type': 'application/json'. 
  // Let the browser set multipart/form-data automatically.
  
  const response = await fetch(url, {
    ...options,
    headers
  })

  // Global 401 Unauthorized interceptor (token expired or invalid)
  if (response.status === 401) {
    localStorage.removeItem('auth_token')
    window.location.href = '/login'
    throw new Error('Session expired. Please log in again.')
  }

  return response
}
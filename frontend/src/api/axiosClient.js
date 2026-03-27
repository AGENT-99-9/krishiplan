import axios from 'axios';

const axiosClient = axios.create({
    baseURL: '/api/',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 seconds — ML endpoints can be slow
});

// Request interceptor — attach JWT token
axiosClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error),
);

// Response interceptor — handle 401
axiosClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Only clear tokens and redirect for actual auth failures,
            // not for publicly accessible endpoints returning 401
            const isAuthEndpoint = error.config?.url?.includes('auth/');
            if (!isAuthEndpoint) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                // Redirect to login if not already there
                const currentPath = window.location.pathname;
                if (currentPath !== '/login' && currentPath !== '/signup' && currentPath !== '/' && currentPath !== '/register') {
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    },
);

export default axiosClient;

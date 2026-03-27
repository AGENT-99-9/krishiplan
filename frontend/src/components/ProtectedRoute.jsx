import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('access_token');

    if (!token || !token.trim()) {
        // Clear any stale data
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        // Redirect to login if not authenticated
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default ProtectedRoute;

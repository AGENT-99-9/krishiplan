import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signupSchema } from '../schemas/authSchema';
import axiosClient from '../api/axiosClient';

export default function SignupPage() {
    const navigate = useNavigate();
    const [form, setForm] = useState({ email: '', password: '', full_name: '' });
    const [errors, setErrors] = useState({});
    const [apiError, setApiError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
        setErrors({ ...errors, [e.target.name]: '' });
        setApiError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const result = signupSchema.safeParse(form);
        if (!result.success) {
            const fieldErrors = {};
            result.error.errors.forEach((err) => {
                fieldErrors[err.path[0]] = err.message;
            });
            setErrors(fieldErrors);
            return;
        }

        setLoading(true);
        try {
            const res = await axiosClient.post('auth/register/', form);
            localStorage.setItem('access_token', res.data.access_token);
            localStorage.setItem('user', JSON.stringify({
                username: res.data.username,
                email: res.data.email,
                full_name: form.full_name || '',
            }));
            navigate('/dashboard');
        } catch (err) {
            if (err.response) {
                setApiError(err.response.data?.detail || 'Registration failed. Please try again.');
            } else if (err.request) {
                setApiError('Cannot connect to server. Please check if the backend is running.');
            } else {
                setApiError('An unexpected error occurred. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-krishi-50 via-white to-krishi-100/60 px-4 py-12">
            <div className="w-full max-w-md">
                {/* Brand */}
                <Link to="/" className="flex items-center justify-center gap-2 mb-8">
                    <div className="w-10 h-10 bg-gradient-to-br from-krishi-500 to-krishi-700 rounded-xl flex items-center justify-center shadow-lg shadow-krishi-500/20">
                        <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M17.12 2.12c-2.34 0-4.69.96-6.36 2.64C8.41 7.12 7.56 10.22 8.12 13.12c-2.9-.56-6-.29-8.36 2.07a1 1 0 0 0 1.06 1.66c.1-.03 2.4-.82 4.18-.82.58 0 1.12.08 1.6.24a7.46 7.46 0 0 0 2.22 4.38 1 1 0 0 0 1.42-1.42 5.46 5.46 0 0 1-1.42-2.5c1.28.82 2.78 1.27 4.3 1.27 2.34 0 4.69-.96 6.36-2.64C23.58 11.26 23.58 5.42 19.76 2.12a1 1 0 0 0-.64-.24c-.7 0-1.38.08-2 .24z" />
                        </svg>
                    </div>
                    <span className="text-2xl font-bold bg-gradient-to-r from-krishi-700 to-krishi-500 bg-clip-text text-transparent">
                        KrishiSaarthi
                    </span>
                </Link>

                {/* Card */}
                <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 border border-gray-100 p-8">
                    <h2 className="text-2xl font-bold text-gray-900 text-center mb-2">Create your account</h2>
                    <p className="text-sm text-gray-500 text-center mb-8">Join the farming revolution</p>

                    {apiError && (
                        <div className="mb-6 p-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600 text-center">
                            {apiError}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
                            <input
                                id="full_name"
                                name="full_name"
                                type="text"
                                value={form.full_name}
                                onChange={handleChange}
                                placeholder="Rajesh Kumar"
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white"
                            />
                            {errors.full_name && <p className="mt-1.5 text-xs text-red-500">{errors.full_name}</p>}
                        </div>


                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                value={form.email}
                                onChange={handleChange}
                                placeholder="you@example.com"
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white"
                            />
                            {errors.email && <p className="mt-1.5 text-xs text-red-500">{errors.email}</p>}
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                value={form.password}
                                onChange={handleChange}
                                placeholder="••••••••"
                                className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 focus:border-transparent transition-all duration-200 bg-gray-50 hover:bg-white"
                            />
                            {errors.password && <p className="mt-1.5 text-xs text-red-500">{errors.password}</p>}
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 rounded-xl bg-krishi-600 text-white font-semibold text-sm hover:bg-krishi-700 transition-all duration-300 hover:shadow-lg hover:shadow-krishi-500/25 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                        >
                            {loading ? 'Creating account…' : 'Create Account'}
                        </button>
                    </form>

                    <p className="mt-6 text-center text-sm text-gray-500">
                        Already have an account?{' '}
                        <Link to="/login" className="text-krishi-600 font-semibold hover:text-krishi-700">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

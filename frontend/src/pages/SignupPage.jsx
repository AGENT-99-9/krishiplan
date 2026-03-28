import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signupSchema } from '../schemas/authSchema';
import axiosClient from '../api/axiosClient';

export default function SignupPage() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        email: '',
        password: '',
        full_name: '',
        role: 'farmer',
        shop_name: '',
        location: ''
    });
    const [errors, setErrors] = useState({});
    const [apiError, setApiError] = useState('');
    const [loading, setLoading] = useState(false);

    const isVendor = form.role === 'vendor';

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
                role: res.data.role || form.role,
                vendor_profile: res.data.vendor_profile || null
            }));

            // Redirect based on role
            if (res.data.role === 'vendor') {
                navigate('/vendor-dashboard');
            } else {
                navigate('/dashboard');
            }
        } catch (err) {
            if (err.response) {
                setApiError(err.response.data?.detail || 'Registration failed. Please try again.');
            } else {
                setApiError('An unexpected error occurred. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-krishi-50 via-white to-krishi-100/60 px-4 py-12 animate-fade-in">
            <div className="w-full max-w-md">
                {/* Brand */}
                <Link to="/" className="flex items-center justify-center gap-2 mb-8 group">
                    <div className="w-12 h-12 bg-gradient-to-br from-krishi-600 to-krishi-800 rounded-2xl flex items-center justify-center shadow-2xl shadow-krishi-500/30 group-hover:scale-110 transition-transform duration-300">
                        <svg className="w-7 h-7 text-white" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M17.12 2.12c-2.34 0-4.69.96-6.36 2.64C8.41 7.12 7.56 10.22 8.12 13.12c-2.9-.56-6-.29-8.36 2.07a1 1 0 0 0 1.06 1.66c.1-.03 2.4-.82 4.18-.82.58 0 1.12.08 1.6.24a7.46 7.46 0 0 0 2.22 4.38 1 1 0 0 0 1.42-1.42 5.46 5.46 0 0 1-1.42-2.5c1.28.82 2.78 1.27 4.3 1.27 2.34 0 4.69-.96 6.36-2.64C23.58 11.26 23.58 5.42 19.76 2.12a1 1 0 0 0-.64-.24c-.7 0-1.38.08-2 .24z" />
                        </svg>
                    </div>
                    <span className="text-3xl font-black bg-gradient-to-r from-krishi-800 to-krishi-600 bg-clip-text text-transparent tracking-tight">
                        KrishiSaarthi
                    </span>
                </Link>

                {/* Card */}
                <div className="bg-white/80 backdrop-blur-xl rounded-[32px] shadow-[0_30px_60px_-15px_rgba(0,0,0,0.1)] border border-white p-10">
                    <div className="text-center mb-10">
                        <h2 className="text-3xl font-black text-gray-900 mb-2">Grow with us</h2>
                        <p className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Select your pathway</p>
                    </div>

                    {apiError && (
                        <div className="mb-8 p-4 rounded-2xl bg-red-50 border border-red-100 text-sm text-red-600 font-bold flex items-center gap-3 animate-pulse">
                            <span className="w-2 h-2 rounded-full bg-red-600" />
                            {apiError}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Role Switcher */}
                        <div className="flex bg-gray-100 p-1 rounded-2xl mb-8">
                            <button
                                type="button"
                                onClick={() => setForm({ ...form, role: 'farmer' })}
                                className={`flex-1 py-3 text-xs font-black uppercase tracking-widest rounded-xl transition-all duration-300 ${form.role === 'farmer' ? 'bg-white text-krishi-700 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                Farmer
                            </button>
                            <button
                                type="button"
                                onClick={() => setForm({ ...form, role: 'vendor' })}
                                className={`flex-1 py-3 text-xs font-black uppercase tracking-widest rounded-xl transition-all duration-300 ${form.role === 'vendor' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                            >
                                Vendor
                            </button>
                        </div>

                        <div className="grid grid-cols-1 gap-5">
                            <div>
                                <label className="block text-[11px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2 px-1">Full Identity</label>
                                <input
                                    name="full_name"
                                    type="text"
                                    value={form.full_name}
                                    onChange={handleChange}
                                    placeholder="Enter full name"
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl text-sm font-bold focus:outline-none focus:ring-4 focus:ring-krishi-500/10 focus:bg-white focus:border-krishi-500 transition-all shadow-inner"
                                />
                                {errors.full_name && <p className="mt-2 text-xs text-red-500 font-bold ml-1 italic">! {errors.full_name}</p>}
                            </div>

                            <div>
                                <label className="block text-[11px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2 px-1">Email Address</label>
                                <input
                                    name="email"
                                    type="email"
                                    value={form.email}
                                    onChange={handleChange}
                                    placeholder="your@email.com"
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl text-sm font-bold focus:outline-none focus:ring-4 focus:ring-krishi-500/10 focus:bg-white focus:border-krishi-500 transition-all shadow-inner"
                                />
                                {errors.email && <p className="mt-2 text-xs text-red-500 font-bold ml-1 italic">! {errors.email}</p>}
                            </div>

                            {/* Vendor Specific Fields */}
                            {isVendor && (
                                <div className="space-y-5 animate-slide-down">
                                    <div>
                                        <label className="block text-[11px] font-black text-blue-400 uppercase tracking-[0.2em] mb-2 px-1">Business Name</label>
                                        <input
                                            name="shop_name"
                                            value={form.shop_name}
                                            onChange={handleChange}
                                            placeholder="Store / Warehouse Name"
                                            className="w-full px-6 py-4 bg-blue-50/30 border border-transparent rounded-2xl text-sm font-bold focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:bg-white focus:border-blue-500 transition-all shadow-inner"
                                        />
                                        {errors.shop_name && <p className="mt-2 text-xs text-red-500 font-bold ml-1 italic">! {errors.shop_name}</p>}
                                    </div>
                                    <div>
                                        <label className="block text-[11px] font-black text-blue-400 uppercase tracking-[0.2em] mb-2 px-1">Warehouse Location</label>
                                        <input
                                            name="location"
                                            value={form.location}
                                            onChange={handleChange}
                                            placeholder="City / District"
                                            className="w-full px-6 py-4 bg-blue-50/30 border border-transparent rounded-2xl text-sm font-bold focus:outline-none focus:ring-4 focus:ring-blue-500/10 focus:bg-white focus:border-blue-500 transition-all shadow-inner"
                                        />
                                        {errors.location && <p className="mt-2 text-xs text-red-500 font-bold ml-1 italic">! {errors.location}</p>}
                                    </div>
                                </div>
                            )}

                            <div>
                                <label className="block text-[11px] font-black text-gray-400 uppercase tracking-[0.2em] mb-2 px-1">Secure Password</label>
                                <input
                                    name="password"
                                    type="password"
                                    value={form.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    className="w-full px-6 py-4 bg-gray-50 border border-transparent rounded-2xl text-sm font-bold focus:outline-none focus:ring-4 focus:ring-krishi-500/10 focus:bg-white focus:border-krishi-500 transition-all shadow-inner"
                                />
                                {errors.password && <p className="mt-2 text-xs text-red-500 font-bold ml-1 italic">! {errors.password}</p>}
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className={`w-full py-5 rounded-[22px] text-white font-black text-xs uppercase tracking-[0.3em] transition-all duration-500 shadow-2xl hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:cursor-wait mt-4 cursor-pointer ${isVendor ? 'bg-blue-600 shadow-blue-500/30 hover:bg-blue-700' : 'bg-krishi-600 shadow-krishi-500/30 hover:bg-krishi-700'}`}
                        >
                            {loading ? (
                                <div className="flex items-center justify-center gap-2">
                                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" />
                                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:0.2s]" />
                                    <div className="w-1.5 h-1.5 bg-white rounded-full animate-bounce [animation-delay:0.4s]" />
                                </div>
                            ) : 'Initialize Account'}
                        </button>
                    </form>

                    <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                            Member already?{' '}
                            <Link to="/login" className="text-krishi-600 hover:text-krishi-800 transition-colors">
                                Authenticate
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

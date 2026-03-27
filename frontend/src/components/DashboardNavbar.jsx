import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from './Button';

export default function DashboardNavbar() {
    const [mobileOpen, setMobileOpen] = useState(false);
    const navigate = useNavigate();

    const navLinks = [
        { label: 'Marketplace', to: '/marketplace' },
        { label: 'AI Assistant', to: '/assistant' },
        { label: 'Community', to: '/community' },
    ];

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        navigate('/login');
    };

    return (
        <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-100 shadow-sm">
            <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* ── Left: Brand ──────────────────── */}
                    <Link to="/" className="flex items-center gap-2 group">
                        <div className="w-9 h-9 bg-gradient-to-br from-krishi-500 to-krishi-700 rounded-xl flex items-center justify-center shadow-md shadow-krishi-500/20 group-hover:shadow-krishi-500/40 transition-shadow duration-300">
                            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M17.12 2.12c-2.34 0-4.69.96-6.36 2.64C8.41 7.12 7.56 10.22 8.12 13.12c-2.9-.56-6-.29-8.36 2.07a1 1 0 0 0 1.06 1.66c.1-.03 2.4-.82 4.18-.82.58 0 1.12.08 1.6.24a7.46 7.46 0 0 0 2.22 4.38 1 1 0 0 0 1.42-1.42 5.46 5.46 0 0 1-1.42-2.5c1.28.82 2.78 1.27 4.3 1.27 2.34 0 4.69-.96 6.36-2.64C23.58 11.26 23.58 5.42 19.76 2.12a1 1 0 0 0-.64-.24c-.7 0-1.38.08-2 .24z" />
                            </svg>
                        </div>
                        <span className="text-xl font-bold bg-gradient-to-r from-krishi-700 to-krishi-500 bg-clip-text text-transparent">
                            KrishiSaarthi
                        </span>
                    </Link>

                    {/* ── Center: Navigation Links (Desktop) ── */}
                    <div className="hidden md:flex items-center gap-1">
                        {navLinks.map((link) => (
                            <Link
                                key={link.to}
                                to={link.to}
                                className="relative px-4 py-2 text-sm font-medium text-gray-600 hover:text-krishi-600 transition-colors duration-200 group"
                            >
                                {link.label}
                                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0 h-0.5 bg-krishi-500 rounded-full transition-all duration-300 group-hover:w-3/4" />
                            </Link>
                        ))}
                    </div>

                    {/* ── Right: Actions (Desktop) ──────── */}
                    <div className="hidden md:flex items-center gap-3">
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-red-500 transition-colors duration-200 cursor-pointer"
                        >
                            Logout
                        </button>
                        <Button to="/dashboard" variant="primary" className="text-sm px-6 py-2.5">
                            Dashboard
                        </Button>
                    </div>

                    {/* ── Mobile Hamburger ──────────────── */}
                    <button
                        className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors cursor-pointer"
                        onClick={() => setMobileOpen(!mobileOpen)}
                        aria-label="Toggle menu"
                    >
                        {mobileOpen ? (
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        ) : (
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>

            {/* ── Mobile Menu ────────────────────── */}
            {mobileOpen && (
                <div className="md:hidden bg-white border-t border-gray-100 shadow-lg animate-fade-in-up">
                    <div className="px-4 py-4 space-y-1">
                        {navLinks.map((link) => (
                            <Link
                                key={link.to}
                                to={link.to}
                                className="block px-4 py-3 rounded-xl text-sm font-medium text-gray-600 hover:text-krishi-600 hover:bg-krishi-50 transition-all duration-200"
                                onClick={() => setMobileOpen(false)}
                            >
                                {link.label}
                            </Link>
                        ))}
                        <div className="pt-3 border-t border-gray-100 flex flex-col gap-2">
                            <Button to="/dashboard" variant="primary" className="justify-center w-full" onClick={() => setMobileOpen(false)}>
                                Dashboard
                            </Button>
                            <button
                                onClick={() => { setMobileOpen(false); handleLogout(); }}
                                className="w-full px-4 py-3 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50 transition-all duration-200 cursor-pointer"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </nav>
    );
}

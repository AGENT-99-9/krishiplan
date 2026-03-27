import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardNavbar from '../components/DashboardNavbar';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import RecentActivity from '../components/RecentActivity';
import axiosClient from '../api/axiosClient';
import { aiApi } from '../api/aiApi';
import marketplaceApi from '../api/marketplaceApi';

export default function DashboardPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const [user, setUser] = useState(null);
    const [stats, setStats] = useState({ active_orders: 0, ai_reports: 0, forum_posts: 0 });
    const [activities, setActivities] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                const [profileRes, statsRes, activityRes] = await Promise.all([
                    axiosClient.get('dashboard/profile/'),
                    axiosClient.get('dashboard/stats/'),
                    axiosClient.get('dashboard/activity/'),
                ]);
                setUser(profileRes.data);
                setStats(statsRes.data);
                setActivities(activityRes.data);
            } catch (err) {
                console.error('Dashboard fetch error:', err);
                // Fallback to stored user
                try {
                    const stored = localStorage.getItem('user');
                    if (stored) setUser(JSON.parse(stored));
                } catch (e) {
                    console.error('Failed to parse stored user:', e);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, [navigate]);

    const renderContent = () => {
        const path = location.pathname;

        if (path === '/dashboard/orders') {
            return <OrdersSection navigate={navigate} />;
        }

        if (path === '/dashboard/recommendations') {
            return (
                <div className="animate-fade-in-up">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Personalized Recommendations</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {[
                            { title: 'Soil Enrichment', desc: 'Based on your location, your soil might need Nitrogen boost this season.', tag: 'Soil Health', color: 'bg-green-100 text-green-700' },
                            { title: 'Wheat Rust Warning', desc: 'Local alerts indicate increased rust cases nearby. Check your crops.', tag: 'Pest Alert', color: 'bg-red-100 text-red-700' }
                        ].map((rec, i) => (
                            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm group hover:border-krishi-500/50 transition-all">
                                <div className={`inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider mb-4 ${rec.color}`}>
                                    {rec.tag}
                                </div>
                                <h3 className="text-lg font-bold text-gray-900 mb-2">{rec.title}</h3>
                                <p className="text-sm text-gray-500 leading-relaxed mb-6">{rec.desc}</p>
                                <button className="text-krishi-600 font-bold text-sm flex items-center gap-2 group-hover:translate-x-1 transition-transform">
                                    Analyze now <span>→</span>
                                </button>
                            </div>
                        ))}
                    </div>
                    <div className="mt-8 bg-krishi-900 rounded-3xl p-8 text-white relative overflow-hidden shadow-xl shadow-krishi-900/20">
                        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
                            <div>
                                <h3 className="text-xl font-bold mb-2">Want deeper insights?</h3>
                                <p className="text-krishi-200 text-sm max-w-md">Our AI can analyze your farm specifically if you provide more data.</p>
                            </div>
                            <button
                                onClick={() => navigate('/assistant')}
                                className="bg-white text-krishi-900 font-bold py-3 px-8 rounded-xl hover:bg-krishi-50 transition-all shadow-md active:scale-95"
                            >
                                Talk to AI
                            </button>
                        </div>
                        <div className="absolute -right-10 -bottom-10 w-40 h-40 bg-krishi-500/20 rounded-full blur-3xl" />
                    </div>
                </div>
            );
        }

        if (path === '/dashboard/soil-reports') {
            return <SoilReportsSection navigate={navigate} />;
        }

        if (path === '/dashboard/change-password') {
            return (
                <div className="animate-fade-in-up max-w-xl">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Security Settings</h2>
                    <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm">
                        <div className="space-y-5">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1.5">Current Password</label>
                                <input type="password" placeholder="••••••••" className="w-full px-4 py-2.5 rounded-xl border border-gray-100 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1.5">New Password</label>
                                <input type="password" placeholder="Min 8 characters" className="w-full px-4 py-2.5 rounded-xl border border-gray-100 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1.5">Confirm New Password</label>
                                <input type="password" placeholder="••••••••" className="w-full px-4 py-2.5 rounded-xl border border-gray-100 bg-gray-50 focus:bg-white focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all" />
                            </div>
                            <button className="w-full bg-krishi-600 text-white font-bold py-3 rounded-xl hover:bg-krishi-700 transition-all shadow-lg shadow-krishi-600/20 active:scale-[0.98] mt-4">
                                Update Password
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        // Default Overview
        return (
            <>
                <div className="mb-6 animate-fade-in-up">
                    <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Welcome back, <span className="text-krishi-600 font-medium">{user?.full_name || user?.username || 'User'}</span>
                    </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8 animate-fade-in-up-delay">
                    <StatCard
                        title="Active Orders"
                        value={stats.active_orders}
                        color="blue"
                        icon={
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                            </svg>
                        }
                    />
                    <StatCard
                        title="AI Reports"
                        value={stats.ai_reports}
                        color="purple"
                        icon={
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19 14.5M14.25 3.104c.251.023.501.05.75.082M19 14.5l-2.47 2.47a2.25 2.25 0 01-1.591.659H9.061a2.25 2.25 0 01-1.591-.659L5 14.5m14 0V17a2.25 2.25 0 01-2.25 2.25H7.25A2.25 2.25 0 015 17v-2.5" />
                            </svg>
                        }
                    />
                    <StatCard
                        title="Forum Posts"
                        value={stats.forum_posts}
                        color="krishi"
                        icon={
                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                            </svg>
                        }
                    />
                </div>

                <div className="animate-fade-in-up-delay-2">
                    <RecentActivity activities={activities} />
                </div>
            </>
        );
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-4 border-krishi-100 border-t-krishi-600 rounded-full animate-spin shadow-inner" />
                    <p className="text-sm text-gray-500 font-bold tracking-tight">Syncing your dashboard…</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50/80">
            <DashboardNavbar />

            <div className="flex gap-8 max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="hidden lg:block flex-shrink-0">
                    <Sidebar user={user} />
                </div>

                <main className="flex-1 min-w-0">
                    {renderContent()}
                </main>
            </div>

            {/* Mobile Bottom Sidebar */}
            <div className="lg:hidden fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] bg-white/95 backdrop-blur-md border border-gray-100 shadow-2xl rounded-2xl z-40 px-6 py-3">
                <div className="flex items-center justify-between">
                    {[
                        { to: '/dashboard', icon: '📊' },
                        { to: '/dashboard/orders', icon: '📦' },
                        { to: '/dashboard/recommendations', icon: '✨' },
                        { to: '/dashboard/soil-reports', icon: '🌱' },
                        { to: '/dashboard/change-password', icon: '⚙️' },
                    ].map((item) => (
                        <button
                            key={item.to}
                            onClick={() => navigate(item.to)}
                            className={`p-2 rounded-xl text-xl transition-all ${location.pathname === item.to ? 'bg-krishi-100 grayscale-0' : 'grayscale opacity-50'}`}
                        >
                            {item.icon}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

// ─── Soil Reports Sub-Section ──────────────────────────────────
function SoilReportsSection({ navigate }) {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchReports = async () => {
            try {
                const data = await aiApi.getSoilReports();
                setReports(data);
            } catch (err) {
                console.error('Failed to load soil reports:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchReports();
    }, []);

    const formatDate = (iso) => {
        try {
            return new Date(iso).toLocaleDateString('en-IN', {
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
            });
        } catch { return iso; }
    };

    return (
        <div className="animate-fade-in-up">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Soil Analysis Reports</h2>
                <button
                    onClick={() => navigate('/assistant')}
                    className="text-sm font-bold text-krishi-600 hover:text-krishi-700 transition-colors flex items-center gap-1"
                >
                    + New Analysis <span>→</span>
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-16">
                    <div className="w-10 h-10 border-4 border-krishi-100 border-t-krishi-600 rounded-full animate-spin" />
                </div>
            ) : reports.length === 0 ? (
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                    <div className="p-12 text-center">
                        <div className="w-20 h-20 bg-emerald-50 text-emerald-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-bold text-gray-900">No soil reports yet</h3>
                        <p className="text-gray-500 mt-2 max-w-sm mx-auto">Upload a soil photo or lab report from the Fertilizer Advisor to see your analysis history.</p>
                        <button
                            onClick={() => navigate('/assistant')}
                            className="mt-8 bg-krishi-600 text-white font-bold py-3 px-8 rounded-xl hover:bg-krishi-700 transition-all shadow-lg shadow-krishi-600/20"
                        >
                            Go to Fertilizer Advisor
                        </button>
                    </div>
                </div>
            ) : (
                <div className="space-y-4">
                    {reports.map((report) => (
                        <div key={report.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:border-krishi-200 transition-all group">
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-white shadow-md ${report.report_type === 'soil_image'
                                        ? 'bg-gradient-to-br from-amber-500 to-orange-600'
                                        : 'bg-gradient-to-br from-blue-500 to-indigo-600'
                                        }`}>
                                        {report.report_type === 'soil_image' ? (
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                                        ) : (
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                        )}
                                    </div>
                                    <div>
                                        <h4 className="text-sm font-bold text-gray-800">
                                            {report.report_type === 'soil_image' ? 'Soil Photo Analysis' : 'Lab Report Scan'}
                                        </h4>
                                        <p className="text-xs text-gray-400">{report.source_file}</p>
                                    </div>
                                </div>
                                <span className="text-[10px] text-gray-400 font-medium">{formatDate(report.created_at)}</span>
                            </div>

                            {/* Key metrics */}
                            {report.form_values && Object.keys(report.form_values).length > 0 && (
                                <div className="flex flex-wrap gap-1.5 mt-2">
                                    {Object.entries(report.form_values).slice(0, 6).map(([key, val]) => (
                                        <span key={key} className="px-2 py-0.5 bg-gray-50 rounded-lg text-[10px] font-semibold text-gray-600">
                                            {key.replace(/_/g, ' ')}: <span className="text-gray-900">{typeof val === 'number' ? val.toFixed(1) : val}</span>
                                        </span>
                                    ))}
                                </div>
                            )}

                            {/* Health indicators (soil_image only) */}
                            {report.analysis?.health && (
                                <div className="flex flex-wrap gap-1 mt-2">
                                    {Object.entries(report.analysis.health).slice(0, 4).map(([key, val]) => (
                                        <span key={key} className={`px-1.5 py-0.5 rounded-full text-[9px] font-bold ${val.includes('✓') ? 'bg-green-50 text-green-700' :
                                            val.includes('⚠') ? 'bg-red-50 text-red-600' :
                                                'bg-gray-50 text-gray-500'
                                            }`}>
                                            {key}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

// ─── Orders Sub-Section ──────────────────────────────────
function OrdersSection({ navigate }) {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const data = await marketplaceApi.fetchOrders();
                setOrders(data);
            } catch (err) {
                console.error('Failed to load orders:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, []);

    const formatDate = (iso) => {
        try {
            return new Date(iso).toLocaleDateString('en-IN', {
                day: 'numeric', month: 'short', year: 'numeric',
                hour: '2-digit', minute: '2-digit',
            });
        } catch { return iso; }
    };

    return (
        <div className="animate-fade-in-up">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">My Orders</h2>
                <button
                    onClick={() => navigate('/marketplace')}
                    className="text-sm font-bold text-krishi-600 hover:text-krishi-700 transition-colors flex items-center gap-1"
                >
                    Marketplace <span>→</span>
                </button>
            </div>

            {loading ? (
                <div className="flex justify-center py-16">
                    <div className="w-10 h-10 border-4 border-krishi-100 border-t-krishi-600 rounded-full animate-spin" />
                </div>
            ) : orders.length === 0 ? (
                <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                    <div className="p-12 text-center">
                        <div className="w-20 h-20 bg-blue-50 text-blue-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                            </svg>
                        </div>
                        <h3 className="text-lg font-bold text-gray-900">No orders yet</h3>
                        <p className="text-gray-500 mt-2 max-w-sm mx-auto">Items you buy from the marketplace will appear here.</p>
                        <button
                            onClick={() => navigate('/marketplace')}
                            className="mt-8 bg-krishi-600 text-white font-bold py-3 px-8 rounded-xl hover:bg-krishi-700 transition-all shadow-lg shadow-krishi-600/20"
                        >
                            Browse Marketplace
                        </button>
                    </div>
                </div>
            ) : (
                <div className="space-y-4">
                    {orders.map((order) => (
                        <div key={order.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:border-krishi-200 transition-all flex flex-col sm:flex-row gap-4">
                            <img src={order.product_image || 'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?q=80&w=600&auto=format&fit=crop'} alt={order.product_name} className="w-20 h-20 rounded-xl object-cover" />
                            <div className="flex-1">
                                <div className="flex items-start justify-between">
                                    <div>
                                        <h4 className="font-bold text-gray-900">{order.product_name}</h4>
                                        <p className="text-sm text-gray-500">Qty: {order.quantity}</p>
                                    </div>
                                    <span className="text-lg font-black text-krishi-700">₹{parseFloat(order.total_price).toFixed(2)}</span>
                                </div>
                                <div className="flex items-center justify-between mt-4">
                                    <span className={`px-2 py-1 rounded-md text-xs font-bold ${order.status === 'Pending' ? 'bg-yellow-50 text-yellow-700' : 'bg-green-50 text-green-700'}`}>
                                        {order.status}
                                    </span>
                                    <span className="text-xs text-gray-400 font-medium">Ordered on {formatDate(order.created_at)}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

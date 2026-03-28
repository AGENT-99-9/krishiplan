import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import DashboardNavbar from '../components/DashboardNavbar';
import Footer from '../components/Footer';

export default function AdminDashboardPage() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({ users: 0, products: 0, orders: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        try {
            const raw = localStorage.getItem('user');
            const storedUser = raw ? JSON.parse(raw) : null;
            if (!storedUser || storedUser.role !== 'admin') {
                navigate('/login');
                return;
            }
        } catch {
            navigate('/login');
            return;
        }
        // Admin stats fetch logic would go here
        setLoading(false);
    }, []);

    return (
        <div className="min-h-screen flex flex-col bg-gray-50/50">
            <DashboardNavbar />
            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
                <h1 className="text-4xl font-black text-gray-900 tracking-tight mb-12">
                    System <span className="text-red-600">Administration</span>
                </h1>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                    {[
                        { label: 'Platform Users', value: '1,240', hoverShadow: 'hover:shadow-blue-500/5', textHover: 'group-hover:text-blue-600' },
                        { label: 'Active Listings', value: '458', hoverShadow: 'hover:shadow-green-500/5', textHover: 'group-hover:text-green-600' },
                        { label: 'Total Revenue', value: '₹14.2L', hoverShadow: 'hover:shadow-red-500/5', textHover: 'group-hover:text-red-600' }
                    ].map((stat, i) => (
                        <div key={i} className={`bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-2xl ${stat.hoverShadow} transition-all group`}>
                            <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2">{stat.label}</div>
                            <div className={`text-4xl font-black text-gray-900 ${stat.textHover} transition-colors`}>{stat.value}</div>
                        </div>
                    ))}
                </div>

                <div className="bg-white rounded-[40px] shadow-sm border border-gray-100 p-10">
                    <h2 className="text-xl font-black text-gray-900 mb-6 flex items-center gap-3">
                        <span className="w-2 h-8 bg-black rounded-full" />
                        Platform Monitoring
                    </h2>
                    <div className="flex flex-col gap-4">
                        <div className="p-6 bg-gray-50 rounded-2xl flex items-center justify-between">
                            <span className="text-sm font-bold text-gray-600">Database Connection</span>
                            <span className="px-3 py-1 bg-green-100 text-green-700 text-[10px] font-black uppercase tracking-widest rounded-lg">Healthy</span>
                        </div>
                        <div className="p-6 bg-gray-50 rounded-2xl flex items-center justify-between">
                            <span className="text-sm font-bold text-gray-600">AI Compute Capacity</span>
                            <span className="px-3 py-1 bg-blue-100 text-blue-700 text-[10px] font-black uppercase tracking-widest rounded-lg">94% Available</span>
                        </div>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    );
}

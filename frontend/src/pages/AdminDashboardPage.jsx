import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import DashboardNavbar from '../components/DashboardNavbar';
import Footer from '../components/Footer';

export default function AdminDashboardPage() {
    const navigate = useNavigate();
    const [stats, setStats] = useState({ users: 0, products: 0, orders: 0, posts: 0, revenue: 0 });
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    // Data states
    const [users, setUsers] = useState([]);
    const [products, setProducts] = useState([]);
    const [posts, setPosts] = useState([]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [statsRes, usersRes, productsRes, postsRes] = await Promise.all([
                axiosClient.get('/dashboard/admin/stats/'),
                axiosClient.get('/dashboard/admin/users/'),
                axiosClient.get('/dashboard/admin/products/'),
                axiosClient.get('/dashboard/admin/posts/')
            ]);
            setStats(statsRes.data);
            setUsers(usersRes.data);
            setProducts(productsRes.data);
            setPosts(postsRes.data);
        } catch (err) {
            console.error("Failed to load admin data:", err);
            if (err.response?.status === 403) navigate('/login');
        } finally {
            setLoading(false);
        }
    };

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
        loadData();
    }, []);

    const handleDelete = async (type, id) => {
        if (!window.confirm(`Are you sure you want to delete this ${type.slice(0, -1)}?`)) return;
        try {
            await axiosClient.delete(`/dashboard/admin/${type}/${id}/`);
            loadData();
        } catch (err) {
            alert(`Failed to delete ${type.slice(0, -1)}`);
        }
    };

    const renderOverview = () => (
        <div className="space-y-8 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    { label: 'Platform Users', value: stats.users, hoverShadow: 'hover:shadow-blue-500/10', textHover: 'group-hover:text-blue-600', icon: '👤', bg: 'bg-blue-50' },
                    { label: 'Active Listings', value: stats.products, hoverShadow: 'hover:shadow-green-500/10', textHover: 'group-hover:text-green-600', icon: '🛒', bg: 'bg-green-50' },
                    { label: 'Community Posts', value: stats.posts, hoverShadow: 'hover:shadow-purple-500/10', textHover: 'group-hover:text-purple-600', icon: '📝', bg: 'bg-purple-50' },
                    { label: 'Total Revenue', value: `₹${stats.revenue.toLocaleString()}`, hoverShadow: 'hover:shadow-red-500/10', textHover: 'group-hover:text-red-600', icon: '📈', bg: 'bg-red-50' }
                ].map((stat, i) => (
                    <div key={i} className={`bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-2xl ${stat.hoverShadow} transition-all group flex flex-col`}>
                        <div className="flex items-center justify-between mb-4">
                            <div className={`w-12 h-12 ${stat.bg} rounded-2xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform`}>{stat.icon}</div>
                        </div>
                        <div className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400 mb-2">{stat.label}</div>
                        <div className={`text-4xl font-black text-gray-900 ${stat.textHover} transition-colors`}>{stat.value}</div>
                    </div>
                ))}
            </div>

            <div className="bg-white rounded-[40px] shadow-sm border border-gray-100 p-10">
                <h2 className="text-xl font-black text-gray-900 mb-6 flex items-center gap-3">
                    <span className="w-2 h-8 bg-black rounded-full" />
                    System Monitoring
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-6 bg-gray-50 rounded-2xl flex items-center justify-between border border-gray-100">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                            <span className="text-sm font-bold text-gray-600">Database Connection</span>
                        </div>
                        <span className="px-3 py-1 bg-green-100/50 text-green-700 text-[10px] font-black uppercase tracking-widest rounded-lg border border-green-200">Healthy</span>
                    </div>
                    <div className="p-6 bg-gray-50 rounded-2xl flex items-center justify-between border border-gray-100">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                            <span className="text-sm font-bold text-gray-600">AI Compute Capacity</span>
                        </div>
                        <span className="px-3 py-1 bg-blue-100/50 text-blue-700 text-[10px] font-black uppercase tracking-widest rounded-lg border border-blue-200">98% Available</span>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderTable = (columns, data, type) => (
        <div className="bg-white rounded-[32px] shadow-sm border border-gray-100 overflow-hidden animate-fade-in">
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-gray-50/80 border-b border-gray-100">
                            {columns.map((col, i) => (
                                <th key={i} className="py-5 px-6 text-[11px] font-bold uppercase tracking-wider text-gray-500">{col.header}</th>
                            ))}
                            <th className="py-5 px-6 text-[11px] font-bold uppercase tracking-wider text-gray-500 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.length === 0 ? (
                            <tr><td colSpan={columns.length + 1} className="py-12 text-center text-gray-400 font-medium">No records found.</td></tr>
                        ) : data.map((item, i) => (
                            <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                                {columns.map((col, j) => (
                                    <td key={j} className="py-4 px-6 text-sm font-medium text-gray-900 border-r border-transparent">
                                        {col.render ? col.render(item) : item[col.key] || '-'}
                                    </td>
                                ))}
                                <td className="py-4 px-6 text-right">
                                    <button onClick={() => handleDelete(type, item.id)} className="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg transition-colors">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen flex flex-col bg-gray-50/50">
            <DashboardNavbar />
            <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
                    <div>
                        <h1 className="text-4xl font-black text-gray-900 tracking-tight mb-2 flex items-center gap-3">
                            <span className="w-3 h-10 bg-red-600 rounded-full" />
                            Admin Console
                        </h1>
                        <p className="text-gray-500 font-medium ml-6">Complete system overview and management capabilities.</p>
                    </div>
                    {/* Navigation Tabs */}
                    <div className="flex bg-white p-1.5 rounded-2xl shadow-sm border border-gray-100">
                        {['overview', 'users', 'products', 'posts'].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-6 py-2.5 rounded-xl text-sm font-bold capitalize transition-all ${activeTab === tab ? 'bg-gray-900 text-white shadow-md' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'}`}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <div className="w-12 h-12 border-4 border-gray-200 border-t-red-600 rounded-full animate-spin"></div>
                    </div>
                ) : (
                    <>
                        {activeTab === 'overview' && renderOverview()}

                        {activeTab === 'users' && renderTable([
                            { header: 'ID', key: 'id', render: (u) => <span className="text-xs text-gray-400 font-mono">{u.id.slice(-6)}</span> },
                            { header: 'Username', key: 'username', render: (u) => <div className="flex items-center gap-3"><div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold">{u.username[0].toUpperCase()}</div>{u.username}</div> },
                            { header: 'Email', key: 'email', render: (u) => <span className="text-gray-500">{u.email}</span> },
                            { header: 'Role', key: 'role', render: (u) => <span className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wider ${u.role === 'admin' ? 'bg-red-100 text-red-700' : u.role === 'vendor' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>{u.role}</span> },
                        ], users, 'users')}

                        {activeTab === 'products' && renderTable([
                            { header: 'ID', key: 'id', render: (p) => <span className="text-xs text-gray-400 font-mono">{p.id.slice(-6)}</span> },
                            { header: 'Product Name', key: 'name', render: (p) => <span className="font-bold text-gray-900">{p.name}</span> },
                            { header: 'Category', key: 'category', render: (p) => <span className="text-gray-500 bg-gray-100 px-2 py-1 rounded text-xs font-bold">{p.category}</span> },
                            { header: 'Price', key: 'price', render: (p) => <span className="text-green-600 font-black">₹{p.price}</span> },
                            { header: 'Stock', key: 'stock', render: (p) => <span className={p.stock > 10 ? 'text-gray-600' : 'text-red-500 font-bold'}>{p.stock} units</span> },
                        ], products, 'products')}

                        {activeTab === 'posts' && renderTable([
                            { header: 'ID', key: 'id', render: (p) => <span className="text-xs text-gray-400 font-mono">{p.id.slice(-6)}</span> },
                            { header: 'Title', key: 'title', render: (p) => <span className="font-bold text-gray-900 max-w-xs truncate block">{p.title}</span> },
                            { header: 'Author', key: 'author', render: (p) => <span className="text-blue-600 font-medium">{p.author}</span> },
                            { header: 'Likes', key: 'likes', render: (p) => <span className="flex items-center gap-1 text-gray-500 text-sm"><svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656v.001l-6.828 6.829a1 1 0 01-1.414 0L3.172 10.83a4 4 0 010-5.658z" clipRule="evenodd" /></svg>{p.likes}</span> },
                        ], posts, 'posts')}
                    </>
                )}
            </main>
            <Footer />
        </div>
    );
}

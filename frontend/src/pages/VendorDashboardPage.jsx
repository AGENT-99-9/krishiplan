import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import DashboardNavbar from '../components/DashboardNavbar';
import Footer from '../components/Footer';

export default function VendorDashboardPage() {
    const navigate = useNavigate();
    const [currentUser, setCurrentUser] = useState(null);
    const [activeTab, setActiveTab] = useState('overview'); // overview, inventory, orders, analytics
    const [products, setProducts] = useState([]);
    const [orders, setOrders] = useState([]);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    // Form States
    const [showAddForm, setShowAddForm] = useState(false);
    const [newProduct, setNewProduct] = useState({
        name: '', description: '', price: '', category: 'Fertilizers', stock_quantity: '', image_url: ''
    });

    useEffect(() => {
        try {
            const raw = localStorage.getItem('user');
            const storedUser = raw ? JSON.parse(raw) : null;
            if (!storedUser || storedUser.role !== 'vendor') {
                navigate('/login');
                return;
            }
            setCurrentUser(storedUser);
            fetchAllData();
        } catch {
            navigate('/login');
        }
    }, []);

    const fetchAllData = async () => {
        setLoading(true);
        try {
            const [prodRes, orderRes, analRes] = await Promise.all([
                axiosClient.get('marketplace/products/manage/'),
                axiosClient.get('marketplace/vendor/orders/'),
                axiosClient.get('marketplace/vendor/analytics/')
            ]);
            setProducts(prodRes.data);
            setOrders(orderRes.data);
            setAnalytics(analRes.data);
        } catch (err) {
            console.error("Data fetch error", err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddProduct = async (e) => {
        e.preventDefault();
        try {
            await axiosClient.post('marketplace/products/', newProduct);
            setShowAddForm(false);
            setNewProduct({ name: '', description: '', price: '', category: 'Fertilizers', stock_quantity: '', image_url: '' });
            fetchAllData();
        } catch (err) { alert('Failed to add product'); }
    };

    const updateOrderStatus = async (orderId, statusData) => {
        try {
            await axiosClient.patch(`marketplace/vendor/orders/${orderId}/`, statusData);
            fetchAllData();
        } catch (err) { alert('Failed to update order'); }
    };

    const renderOverview = () => (
        <div className="space-y-10 animate-fade-in">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Total Revenue" value={`₹${analytics?.total_revenue?.toLocaleString() || 0}`} icon="💰" color="blue" />
                <StatCard title="Active Orders" value={orders.filter(o => o.status === 'Pending').length} icon="📦" color="orange" />
                <StatCard title="Products Live" value={products.length} icon="🏪" color="green" />
                <StatCard title="Stock Alerts" value={products.filter(p => p.stock_quantity < 50).length} icon="⚠️" color="red" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Orders Table */}
                <div className="lg:col-span-2 bg-white rounded-[32px] shadow-sm border border-gray-100 p-8">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-black text-gray-900 italic">Latest Shipments</h3>
                        <button onClick={() => setActiveTab('orders')} className="text-xs font-bold text-blue-600 uppercase tracking-widest hover:underline">View All</button>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-[10px] font-black uppercase tracking-widest text-gray-400 border-b border-gray-50">
                                    <th className="pb-4">Order ID</th>
                                    <th className="pb-4">Product</th>
                                    <th className="pb-4">Value</th>
                                    <th className="pb-4">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {orders.slice(0, 5).map(order => (
                                    <tr key={order.id} className="group">
                                        <td className="py-4 text-xs font-mono font-bold text-gray-500">#{order.id.slice(-6)}</td>
                                        <td className="py-4 text-sm font-bold text-gray-900">{order.product_name}</td>
                                        <td className="py-4 text-sm font-black text-gray-900">₹{order.total_price}</td>
                                        <td className="py-4">
                                            <span className={`px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-tighter ${order.status === 'Delivered' ? 'bg-green-50 text-green-600' :
                                                order.status === 'Shipped' ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-600'
                                                }`}>
                                                {order.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Inventory Insights */}
                <div className="bg-white rounded-[32px] shadow-sm border border-gray-100 p-8">
                    <h3 className="text-xl font-black text-gray-900 italic mb-6">Store Performance</h3>
                    <div className="space-y-6">
                        {(analytics?.categories || []).map(cat => (
                            <div key={cat.name}>
                                <div className="flex justify-between text-xs font-bold mb-2">
                                    <span className="text-gray-500">{cat.name}</span>
                                    <span className="text-gray-900">{cat.count} Units</span>
                                </div>
                                <div className="h-2 bg-gray-50 rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-600 rounded-full" style={{ width: `${products.length > 0 ? (cat.count / products.length) * 100 : 0}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );

    const renderInventory = () => (
        <div className="space-y-8 animate-fade-in">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-black text-gray-900">Warehouse <span className="text-blue-600">Stock</span></h2>
                <button onClick={() => setShowAddForm(!showAddForm)} className="bg-black text-white px-6 py-3 rounded-2xl text-xs font-black uppercase tracking-widest hover:scale-105 transition-all">
                    {showAddForm ? 'Close Editor' : '+ New Unit'}
                </button>
            </div>

            {showAddForm && (
                <div className="bg-white rounded-[32px] shadow-2xl border border-gray-100 p-10 animate-slide-down">
                    <form onSubmit={handleAddProduct} className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            <InputField label="Product Name" placeholder="e.g. NPK Power" value={newProduct.name} onChange={v => setNewProduct({ ...newProduct, name: v })} />
                            <div className="grid grid-cols-2 gap-6">
                                <InputField label="Price (₹)" type="number" placeholder="0" value={newProduct.price} onChange={v => setNewProduct({ ...newProduct, price: v })} />
                                <InputField label="Stock" type="number" placeholder="Qty" value={newProduct.stock_quantity} onChange={v => setNewProduct({ ...newProduct, stock_quantity: v })} />
                            </div>
                        </div>
                        <div className="space-y-6">
                            <InputField label="Image URL" placeholder="https://..." value={newProduct.image_url} onChange={v => setNewProduct({ ...newProduct, image_url: v })} />
                            <textarea placeholder="Description" rows="3" className="w-full px-6 py-4 bg-gray-50 rounded-2xl text-sm font-bold outline-none" value={newProduct.description} onChange={e => setNewProduct({ ...newProduct, description: e.target.value })} />
                            <button className="w-full bg-blue-600 text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest shadow-xl shadow-blue-500/20">Authorize Publishing</button>
                        </div>
                    </form>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map(p => (
                    <div key={p.id} className="bg-white p-6 rounded-[28px] shadow-sm border border-gray-100 group">
                        <div className="flex justify-between items-start mb-4">
                            <div className="w-12 h-12 bg-gray-50 rounded-xl overflow-hidden shadow-inner">
                                {p.image_url ? <img src={p.image_url} alt="" className="w-full h-full object-cover" /> : <div className="flex items-center justify-center p-2 text-xl">📦</div>}
                            </div>
                            <span className={`px-2 py-1 rounded-lg text-[8px] font-black uppercase ${p.stock_quantity < 50 ? 'bg-red-50 text-red-500' : 'bg-green-50 text-green-500'}`}>
                                {p.stock_quantity} Left
                            </span>
                        </div>
                        <h4 className="font-black text-gray-900 truncate mb-1">{p.name}</h4>
                        <div className="text-lg font-black text-blue-600 mb-4">₹{p.price}</div>
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onClick={() => { const qty = prompt('Enter new stock quantity:', p.stock_quantity); if (qty !== null && !isNaN(qty)) { axiosClient.patch(`marketplace/products/manage/${p.id}/`, { stock_quantity: parseInt(qty) }).then(() => fetchAllData()).catch(() => alert('Failed to restock')); } }} className="flex-1 py-2 bg-gray-100 rounded-xl text-[10px] font-black uppercase hover:bg-gray-200 cursor-pointer">Restock</button>
                            <button onClick={() => { if (window.confirm(`Delist "${p.name}"?`)) { axiosClient.delete(`marketplace/products/manage/${p.id}/`).then(() => fetchAllData()).catch(() => alert('Failed to delist')); } }} className="px-3 py-2 bg-red-50 text-red-500 rounded-xl text-[10px] font-black uppercase hover:bg-red-100 cursor-pointer">Delist</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

    const renderOrders = () => (
        <div className="space-y-8 animate-fade-in">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-black text-gray-900">Order <span className="text-orange-600">Fulfillment</span></h2>
                <div className="flex gap-3">
                    <span className="px-3 py-1.5 bg-orange-50 text-orange-600 text-[10px] font-black uppercase rounded-xl">
                        {orders.filter(o => o.status === 'Pending').length} Pending
                    </span>
                    <span className="px-3 py-1.5 bg-blue-50 text-blue-600 text-[10px] font-black uppercase rounded-xl">
                        {orders.filter(o => o.status === 'Shipped').length} In Transit
                    </span>
                    <span className="px-3 py-1.5 bg-green-50 text-green-600 text-[10px] font-black uppercase rounded-xl">
                        {orders.filter(o => o.status === 'Delivered').length} Delivered
                    </span>
                </div>
            </div>

            {orders.length === 0 ? (
                <div className="bg-white rounded-[32px] shadow-sm border border-gray-100 p-16 text-center">
                    <div className="text-5xl mb-4">📭</div>
                    <h3 className="text-xl font-black text-gray-900 mb-2">No Orders Yet</h3>
                    <p className="text-sm text-gray-400 font-medium">When farmers purchase your products, orders will appear here for fulfillment.</p>
                </div>
            ) : (
                <div className="bg-white rounded-[32px] shadow-sm border border-gray-100 overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50/50">
                            <tr className="text-[10px] font-black uppercase tracking-widest text-gray-400">
                                <th className="px-8 py-6">Reference</th>
                                <th className="px-8 py-6">Customer / Item</th>
                                <th className="px-8 py-6">Qty</th>
                                <th className="px-8 py-6">Logistics</th>
                                <th className="px-8 py-6">Action</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {orders.map(order => (
                                <tr key={order.id} className="hover:bg-gray-50/50 transition-colors">
                                    <td className="px-8 py-6">
                                        <div className="text-xs font-black text-gray-900">#{order.id.slice(-8)}</div>
                                        <div className="text-[10px] text-gray-400">{new Date(order.created_at).toLocaleDateString()}</div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="text-sm font-black text-gray-900">{order.product_name}</div>
                                        <div className="text-xs text-blue-600 font-bold">₹{order.total_price?.toLocaleString()} • Paid</div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <span className="text-sm font-black text-gray-700">{order.quantity}x</span>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className={`text-[10px] font-black uppercase px-2 py-1 inline-block rounded ${order.status === 'Delivered' ? 'text-green-600 bg-green-50' :
                                            order.status === 'Shipped' ? 'text-blue-600 bg-blue-50' :
                                                'text-orange-600 bg-orange-50'
                                            }`}>
                                            {order.status}
                                        </div>
                                        {order.tracking_id && <div className="text-[10px] font-bold text-gray-400 mt-1">🚚 {order.tracking_id}</div>}
                                        {order.shipping_provider && <div className="text-[9px] font-bold text-gray-300 mt-0.5">via {order.shipping_provider}</div>}
                                    </td>
                                    <td className="px-8 py-6">
                                        {order.status === 'Pending' ? (
                                            <button
                                                onClick={() => updateOrderStatus(order.id, { status: 'Shipped', tracking_id: `TRS${Math.floor(Math.random() * 1000000)}`, shipping_provider: 'Bluedart' })}
                                                className="bg-blue-600 text-white px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-blue-700 cursor-pointer transition-colors"
                                            >
                                                Ship Now
                                            </button>
                                        ) : order.status === 'Shipped' ? (
                                            <button
                                                onClick={() => updateOrderStatus(order.id, { status: 'Delivered' })}
                                                className="bg-green-600 text-white px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-green-700 cursor-pointer transition-colors"
                                            >
                                                Mark Delivered
                                            </button>
                                        ) : (
                                            <span className="text-[10px] font-black text-green-600 uppercase tracking-widest">✓ Complete</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );

    const renderAnalytics = () => (
        <div className="space-y-10 animate-fade-in">
            <h2 className="text-2xl font-black text-gray-900">Advanced <span className="text-blue-600">Insights</span></h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                <div className="bg-white p-10 rounded-[40px] shadow-sm border border-gray-100 flex flex-col items-center">
                    <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-10 w-full">Inventory Distribution</h3>
                    <div className="relative w-64 h-64 mb-10">
                        {/* CSS-based Donut Chart Placeholder */}
                        <div className="absolute inset-0 border-[20px] border-blue-600 rounded-full" />
                        <div className="absolute inset-0 border-[20px] border-gray-100 rounded-full border-t-transparent border-l-transparent rotate-45" />
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-4xl font-black text-gray-900">{products.length}</span>
                            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Total SKUs</span>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 w-full">
                        {(analytics?.categories || []).map((cat, i) => (
                            <div key={cat.name} className="flex items-center gap-3 p-4 bg-gray-50 rounded-2xl">
                                <div className={`w-3 h-3 rounded-full ${['bg-blue-600', 'bg-green-500', 'bg-orange-500', 'bg-purple-500', 'bg-pink-500'][i % 5]}`} />
                                <div className="flex flex-col overflow-hidden">
                                    <span className="text-[10px] font-black text-gray-900 truncate">{cat.name}</span>
                                    <span className="text-[9px] font-bold text-gray-400">{cat.count} Units</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white p-10 rounded-[40px] shadow-sm border border-gray-100">
                    <h3 className="text-sm font-black text-gray-400 uppercase tracking-widest mb-10">Sales Momentum</h3>
                    <div className="flex items-end justify-between h-48 gap-4 px-4 overflow-hidden pt-10 border-b border-gray-100">
                        {/* Mock historical bars */}
                        {[30, 55, 45, 70, 90, 65, 80].map((h, i) => (
                            <div key={i} className={`flex-1 rounded-t-xl transition-all duration-1000 hover:scale-110 relative group ${i === 4 ? 'bg-blue-600' : 'bg-gray-100'}`}
                                style={{ height: `${h}%` }}>
                                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-gray-900 text-white text-[8px] font-bold py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity">₹{h * 10}k</div>
                            </div>
                        ))}
                    </div>
                    <div className="flex justify-between mt-4 px-2">
                        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
                            <span key={day} className="text-[10px] font-black text-gray-300 uppercase tracking-widest">{day}</span>
                        ))}
                    </div>
                    <div className="mt-10 p-6 bg-blue-50/50 rounded-3xl border border-blue-100/50">
                        <span className="text-[10px] font-black text-blue-600 uppercase tracking-widest block mb-1">AI Business Prediction</span>
                        <p className="text-xs font-bold text-gray-600 leading-relaxed">Demand for <span className="text-blue-700">Fertilizers</span> is expected to increase by <span className="text-blue-700">14%</span> next week due to harvesting season cycles.</p>
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen flex flex-col bg-gray-50/30">
            <DashboardNavbar />
            <div className="flex-1 flex flex-col lg:flex-row">
                {/* Sidebar Navigation */}
                <aside className="w-full lg:w-72 bg-white border-r border-gray-100 p-8 flex flex-col gap-2">
                    <div className="mb-10 px-4">
                        <div className="w-12 h-12 bg-blue-600 flex items-center justify-center rounded-2xl text-white text-xl mb-4 shadow-xl shadow-blue-500/20">🏭</div>
                        <h2 className="text-sm font-black text-gray-900 uppercase tracking-widest">Business Portal</h2>
                        <p className="text-[10px] font-bold text-gray-400">Vendor Management Suite</p>
                    </div>

                    {[
                        { id: 'overview', label: 'Overview', icon: '⚡' },
                        { id: 'inventory', label: 'Stock Manager', icon: '🍱' },
                        { id: 'orders', label: 'Fulfillment', icon: '📝' },
                        { id: 'analytics', label: 'Deep Insights', icon: '📊' }
                    ].map(item => (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`flex items-center gap-4 px-6 py-4 rounded-2xl text-[11px] font-black uppercase tracking-[0.15em] transition-all ${activeTab === item.id ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-gray-400 hover:bg-gray-50'
                                }`}
                        >
                            <span className="text-base">{item.icon}</span>
                            {item.label}
                        </button>
                    ))}

                    <div className="mt-auto pt-8 px-4 border-t border-gray-50">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs uppercase">V</div>
                            <div className="flex-1">
                                <div className="text-[10px] font-black text-gray-900 leading-none mb-1">{currentUser?.vendor_profile?.shop_name || currentUser?.full_name}</div>
                                <div className="text-[8px] font-bold text-gray-400 uppercase tracking-widest">{currentUser?.vendor_profile?.location || 'Verified Vendor'}</div>
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 p-8 lg:p-12 overflow-y-auto max-h-[calc(100vh-64px)]">
                    {loading ? (
                        <div className="h-full flex flex-col items-center justify-center gap-4 animate-pulse">
                            <div className="w-12 h-12 bg-blue-100 rounded-2xl border-4 border-blue-600 border-t-transparent animate-spin" />
                            <span className="text-xs font-black uppercase tracking-widest text-gray-400">Syncing Enterprise Cloud...</span>
                        </div>
                    ) : (
                        <>
                            {activeTab === 'overview' && renderOverview()}
                            {activeTab === 'inventory' && renderInventory()}
                            {activeTab === 'orders' && renderOrders()}
                            {activeTab === 'analytics' && renderAnalytics()}
                        </>
                    )}
                </main>
            </div>
            <Footer />
        </div>
    );
}

// Helper Components
function StatCard({ title, value, icon, color }) {
    const colorClasses = {
        blue: 'text-blue-600 bg-blue-50',
        orange: 'text-orange-600 bg-orange-50',
        green: 'text-green-600 bg-green-50',
        red: 'text-red-600 bg-red-50'
    };
    return (
        <div className="bg-white p-8 rounded-[32px] shadow-sm border border-gray-100 hover:shadow-2xl hover:shadow-blue-500/5 transition-all group">
            <div className="flex justify-between items-start mb-4">
                <span className={`w-10 h-10 flex items-center justify-center rounded-xl text-lg ${colorClasses[color]}`}>{icon}</span>
                <span className="text-[10px] font-black text-gray-300 uppercase tracking-widest">{title}</span>
            </div>
            <div className="text-3xl font-black text-gray-900 group-hover:scale-105 transition-transform origin-left">{value}</div>
        </div>
    );
}

function InputField({ label, ...props }) {
    return (
        <div>
            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3 px-1">{label}</label>
            <input
                {...props}
                onChange={e => props.onChange(e.target.value)}
                className="w-full px-6 py-4 bg-gray-50 border border-transparent focus:bg-white focus:border-blue-500 rounded-2xl text-sm font-bold transition-all outline-none"
            />
        </div>
    );
}

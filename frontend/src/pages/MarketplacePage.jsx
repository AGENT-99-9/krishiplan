import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import marketplaceApi from '../api/marketplaceApi';

const categories = ["All Categories", "Seeds", "Fertilizers", "Tools", "Equipment", "Livestock"];

export default function MarketplacePage() {
    const navigate = useNavigate();
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState("All Categories");
    const [search, setSearch] = useState("");

    const [showSellModal, setShowSellModal] = useState(false);
    const [showBuyModal, setShowBuyModal] = useState(false);
    const [selectedProduct, setSelectedProduct] = useState(null);

    const [sellForm, setSellForm] = useState({ name: '', description: '', price: '', category: 'Seeds', image_url: '' });
    const [buyQuantity, setBuyQuantity] = useState(1);
    const [actionLoading, setActionLoading] = useState(false);

    const fetchProducts = async () => {
        setLoading(true);
        try {
            const data = await marketplaceApi.fetchProducts({ category: activeCategory, search });
            setProducts(data);
        } catch (err) {
            console.error('Marketplace fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, [activeCategory, search]);

    const checkAuth = () => {
        if (!localStorage.getItem('access_token')) {
            alert('Please log in to use this feature.');
            navigate('/login');
            return false;
        }
        return true;
    };

    const handleSellProduct = async (e) => {
        e.preventDefault();
        setActionLoading(true);
        try {
            await marketplaceApi.createProduct(sellForm);
            setShowSellModal(false);
            setSellForm({ name: '', description: '', price: '', category: 'Seeds', image_url: '' });
            fetchProducts();
        } catch (err) {
            console.error('Error creating product:', err);
            alert('Failed to list product. Please try again.');
        } finally {
            setActionLoading(false);
        }
    };

    const handleBuyProduct = async () => {
        if (!selectedProduct) return;
        setActionLoading(true);
        try {
            await marketplaceApi.buyProduct({
                product_id: selectedProduct.id,
                quantity: buyQuantity
            });
            setShowBuyModal(false);
            setSelectedProduct(null);
            setBuyQuantity(1);
            alert('Purchase successful! You can view your order in the dashboard.');
        } catch (err) {
            console.error('Error buying product:', err);
            alert('Failed to purchase product. Please try again.');
        } finally {
            setActionLoading(false);
        }
    };

    const openSellModal = () => {
        if (checkAuth()) setShowSellModal(true);
    };

    const openBuyModal = (product) => {
        if (checkAuth()) {
            setSelectedProduct(product);
            setBuyQuantity(1);
            setShowBuyModal(true);
        }
    };

    return (
        <div className="min-h-screen flex flex-col bg-gray-50/50">
            <Navbar />

            <main className="flex-1 max-w-[1440px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-10">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-10 gap-6">
                    <div>
                        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Agricultural Marketplace</h1>
                        <p className="mt-2 text-gray-500">Find quality materials and equipment for your farm.</p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search products..."
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="w-full sm:w-64 pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 transition-all shadow-sm"
                            />
                            <svg className="absolute left-3 top-3 h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                        <button
                            onClick={openSellModal}
                            className="bg-krishi-600 text-white font-bold text-sm px-6 py-2.5 rounded-xl hover:bg-krishi-700 transition-all shadow-lg shadow-krishi-600/20 active:scale-95 flex items-center justify-center gap-2">
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                            Sell Product
                        </button>
                    </div>
                </div>

                {/* Categories Bar */}
                <div className="flex overflow-x-auto pb-4 mb-8 gap-3 no-scrollbar">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setActiveCategory(cat)}
                            className={`whitespace-nowrap px-5 py-2 rounded-full text-sm font-semibold transition-all ${activeCategory === cat
                                ? 'bg-krishi-600 text-white shadow-md shadow-krishi-600/20'
                                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-100 hover:border-gray-200'
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>

                {/* Product Grid */}
                {loading ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                            <div key={i} className="bg-white rounded-3xl h-80 animate-pulse border border-gray-100 shadow-sm" />
                        ))}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                        {products.map((product) => (
                            <div key={product.id} className="group bg-white rounded-3xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-krishi-200 hover:-translate-y-1 transition-all duration-300 overflow-hidden flex flex-col">
                                <div className="aspect-square bg-gray-50 relative overflow-hidden">
                                    <img
                                        src={product.image_url || 'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?q=80&w=600&auto=format&fit=crop'}
                                        alt={product.name}
                                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                                    />
                                    <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider text-gray-800 shadow-sm border border-white/20">
                                        {product.category}
                                    </div>
                                </div>
                                <div className="p-6 flex-1 flex flex-col">
                                    <h3 className="font-bold text-gray-900 mb-2 group-hover:text-krishi-600 transition-colors capitalize text-base tracking-tight">{product.name}</h3>
                                    <p className="text-sm text-gray-500 line-clamp-2 mb-6 h-10 flex-1">{product.description}</p>
                                    <div className="flex items-center justify-between mt-auto">
                                        <div>
                                            <span className="text-xs text-gray-400 font-medium uppercase tracking-wider block mb-0.5">Price</span>
                                            <span className="text-xl font-black text-krishi-700">₹{product.price}</span>
                                        </div>
                                        <button
                                            onClick={() => openBuyModal(product)}
                                            className="px-5 py-2.5 rounded-xl bg-gray-50 text-gray-900 font-bold text-sm hover:bg-krishi-600 hover:text-white transition-all shadow-sm group-hover:shadow-md cursor-pointer border border-gray-100 hover:border-krishi-500 flex items-center gap-2"
                                        >
                                            Buy
                                            <svg className="w-4 h-4 opacity-50 group-hover:translate-x-1 group-hover:opacity-100 transition-all" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                        {products.length === 0 && (
                            <div className="col-span-full py-24 text-center bg-white rounded-3xl border border-dashed border-gray-200">
                                <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <span className="text-4xl text-gray-300">🛒</span>
                                </div>
                                <h3 className="text-xl font-bold text-gray-900 mb-2">No products found</h3>
                                <p className="text-gray-500">Try adjusting your search or category filters.</p>
                                <button
                                    onClick={() => { setSearch(''); setActiveCategory('All Categories'); }}
                                    className="mt-6 text-krishi-600 font-bold hover:text-krishi-700 transition-colors"
                                >
                                    Clear all filters
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </main>

            {/* Sell Product Modal */}
            {showSellModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-fade-in">
                    <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl animate-scale-in max-h-[90vh] overflow-y-auto no-scrollbar">
                        <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
                            <div>
                                <h2 className="text-2xl font-black text-gray-900">List an Item</h2>
                                <p className="text-gray-500 text-sm mt-1">Sell your agricultural products to thousands of farmers.</p>
                            </div>
                            <button onClick={() => setShowSellModal(false)} className="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-900 hover:bg-gray-100 transition-colors cursor-pointer">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                        </div>
                        <form onSubmit={handleSellProduct} className="space-y-5">
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1.5 flex items-center gap-2">
                                    Product Name <span className="text-red-500">*</span>
                                </label>
                                <input required type="text" value={sellForm.name} onChange={e => setSellForm({ ...sellForm, name: e.target.value })} className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all shadow-sm" placeholder="e.g. Premium Wheat Seeds (5kg)" />
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1.5 flex items-center gap-2">
                                    Description <span className="text-red-500">*</span>
                                </label>
                                <textarea required value={sellForm.description} onChange={e => setSellForm({ ...sellForm, description: e.target.value })} className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all shadow-sm" placeholder="Describe the quality, benefits, and origin of your product..." rows={4}></textarea>
                            </div>
                            <div className="grid grid-cols-2 gap-5">
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1.5 flex items-center gap-2">
                                        Price (₹) <span className="text-red-500">*</span>
                                    </label>
                                    <div className="relative">
                                        <span className="absolute left-4 top-3 text-gray-500 font-bold">₹</span>
                                        <input required type="number" min="1" step="0.01" value={sellForm.price} onChange={e => setSellForm({ ...sellForm, price: e.target.value })} className="w-full pl-8 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all shadow-sm" placeholder="999.00" />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-gray-700 mb-1.5 flex items-center gap-2">
                                        Category <span className="text-red-500">*</span>
                                    </label>
                                    <select required value={sellForm.category} onChange={e => setSellForm({ ...sellForm, category: e.target.value })} className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all shadow-sm cursor-pointer appearance-none">
                                        {categories.filter(c => c !== "All Categories").map(c => (
                                            <option key={c} value={c}>{c}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 mb-1.5 flex items-center justify-between">
                                    <span>Image URL</span>
                                    <span className="text-gray-400 font-normal text-xs uppercase tracking-wider">Optional</span>
                                </label>
                                <input type="url" value={sellForm.image_url} onChange={e => setSellForm({ ...sellForm, image_url: e.target.value })} className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 outline-none transition-all shadow-sm" placeholder="https://example.com/product-image.jpg" />
                            </div>

                            <div className="pt-4 border-t border-gray-100 mt-6 flex gap-3">
                                <button type="button" onClick={() => setShowSellModal(false)} className="flex-1 py-3 px-4 rounded-xl font-bold text-gray-600 bg-gray-50 hover:bg-gray-100 transition-colors border border-gray-200 cursor-pointer">
                                    Cancel
                                </button>
                                <button type="submit" disabled={actionLoading} className="flex-1 bg-krishi-600 hover:bg-krishi-700 text-white font-bold py-3 px-4 rounded-xl transition-all shadow-lg shadow-krishi-600/30 disabled:opacity-70 flex items-center justify-center gap-2 cursor-pointer">
                                    {actionLoading ? (
                                        <>
                                            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                            Publishing...
                                        </>
                                    ) : 'Complete Listing'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Buy Product Modal */}
            {showBuyModal && selectedProduct && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/60 backdrop-blur-sm animate-fade-in">
                    <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl animate-scale-in">
                        <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
                            <h2 className="text-2xl font-black text-gray-900">Secure Purchase</h2>
                            <button onClick={() => setShowBuyModal(false)} className="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center text-gray-400 hover:text-gray-900 hover:bg-gray-100 transition-colors cursor-pointer">
                                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                        </div>

                        <div className="flex gap-5 mb-8 bg-gray-50 p-4 rounded-2xl border border-gray-100">
                            <img src={selectedProduct.image_url || 'https://images.unsplash.com/photo-1592982537447-7440770cbfc9?q=80&w=600&auto=format&fit=crop'} alt={selectedProduct.name} className="w-20 h-20 rounded-xl object-cover shadow-sm" />
                            <div className="flex flex-col justify-center">
                                <span className="text-[10px] uppercase tracking-wider font-bold text-krishi-600 mb-1">{selectedProduct.category}</span>
                                <h3 className="font-bold text-gray-900 leading-tight mb-1">{selectedProduct.name}</h3>
                                <p className="text-xl font-black text-krishi-700">₹{selectedProduct.price} <span className="text-sm font-medium text-gray-400">/ unit</span></p>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="text-sm font-bold text-gray-700">Select Quantity</label>
                                    <span className="text-xs font-medium text-gray-500 bg-white px-2 py-0.5 rounded border border-gray-200">Stock Available</span>
                                </div>
                                <div className="flex border border-gray-200 bg-white rounded-xl overflow-hidden shadow-sm">
                                    <button onClick={() => setBuyQuantity(Math.max(1, buyQuantity - 1))} className="px-5 py-3 bg-gray-50 text-gray-600 hover:bg-gray-100 font-bold border-r border-gray-200 transition-colors cursor-pointer">-</button>
                                    <input type="number" min="1" value={buyQuantity} onChange={e => setBuyQuantity(Math.max(1, Number(e.target.value)) || 1)} className="w-full text-center font-bold text-gray-900 bg-white outline-none" />
                                    <button onClick={() => setBuyQuantity(buyQuantity + 1)} className="px-5 py-3 bg-gray-50 text-gray-600 hover:bg-gray-100 font-bold border-l border-gray-200 transition-colors cursor-pointer">+</button>
                                </div>
                            </div>

                            <div className="bg-krishi-50/50 p-5 rounded-xl border border-krishi-100/50">
                                <div className="flex justify-between items-center mb-2 text-sm text-gray-600">
                                    <span>Subtotal ({buyQuantity} items)</span>
                                    <span>₹{(selectedProduct.price * buyQuantity).toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between items-center mb-3 text-sm text-green-600 font-medium">
                                    <span>Platform Fee</span>
                                    <span>₹0.00</span>
                                </div>
                                <div className="pt-3 border-t border-krishi-200/40 flex justify-between items-end">
                                    <span className="font-bold text-gray-900">Total Price</span>
                                    <span className="text-2xl font-black text-krishi-700">₹{(selectedProduct.price * buyQuantity).toFixed(2)}</span>
                                </div>
                            </div>

                            <button onClick={handleBuyProduct} disabled={actionLoading} className="w-full bg-krishi-600 hover:bg-krishi-700 text-white font-bold py-4 rounded-xl transition-all shadow-xl shadow-krishi-600/30 disabled:opacity-70 flex items-center justify-center gap-2 cursor-pointer mt-2">
                                {actionLoading ? (
                                    <>
                                        <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        Pay ₹{(selectedProduct.price * buyQuantity).toFixed(2)} securely
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <Footer />
        </div>
    );
}


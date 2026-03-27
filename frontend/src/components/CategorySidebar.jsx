export default function CategorySidebar({ activeCategory, setActiveCategory }) {
    const categories = [
        'All Discussions',
        'Crop Management',
        'Soil Health',
        'Pest & Disease',
        'Fertilizer & Nutrients',
        'Equipment',
        'Market Prices'
    ];

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 sticky top-24">
            <div className="mb-6 relative">
                <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                    type="text"
                    placeholder="Search discussions..."
                    className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 transition-all"
                />
            </div>

            <h3 className="font-semibold text-gray-900 mb-3 px-2 text-sm uppercase tracking-wider">Categories</h3>
            <ul className="space-y-1">
                {categories.map((cat) => (
                    <li key={cat}>
                        <button
                            onClick={() => setActiveCategory(cat)}
                            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${activeCategory === cat
                                    ? 'bg-krishi-50 text-krishi-700'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            {cat}
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

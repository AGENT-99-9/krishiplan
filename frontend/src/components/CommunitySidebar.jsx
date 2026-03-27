import { useState } from 'react';

const categories = [
    "All Discussions",
    "Crop Management",
    "Soil Health",
    "Pest & Disease",
    "Fertilizer & Nutrients",
    "Irrigation & Water"
];

export default function CommunitySidebar({ activeCategory, onCategoryChange, onSearch }) {
    const [searchTerm, setSearchTerm] = useState('');

    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
        onSearch(e.target.value);
    };

    return (
        <aside className="space-y-6">
            {/* Search */}
            <div className="bg-white rounded-xl shadow-sm p-4">
                <div className="relative">
                    <input
                        type="text"
                        placeholder="Search discussions..."
                        value={searchTerm}
                        onChange={handleSearch}
                        className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500/20 focus:border-krishi-500 transition-all"
                    />
                    <svg
                        className="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
            </div>

            {/* Categories */}
            <div className="bg-white rounded-xl shadow p-6">
                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4">Categories</h3>
                <nav className="space-y-1">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => onCategoryChange(cat)}
                            className={`w-full text-left px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${activeCategory === cat
                                    ? 'bg-krishi-50 text-krishi-700 shadow-sm shadow-krishi-500/10'
                                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                                }`}
                        >
                            {cat}
                        </button>
                    ))}
                </nav>
            </div>
        </aside>
    );
}

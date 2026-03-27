import { useState } from 'react';
import communityApi from '../api/communityApi';

export default function AskQuestionModal({ isOpen, onClose, onCreated, category: defaultCategory }) {
    const [form, setForm] = useState({ title: '', category: defaultCategory || 'Crop Management', description: '' });
    const [loading, setLoading] = useState(false);

    const categories = [
        "Crop Management",
        "Soil Health",
        "Pest & Disease",
        "Fertilizer & Nutrients",
        "Irrigation & Water"
    ];

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await communityApi.createPost(form);
            onCreated();
            onClose();
            setForm({ title: '', category: 'Crop Management', description: '' });
        } catch (err) {
            console.error('Create post error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-gray-900/50 backdrop-blur-sm px-4">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-fade-in-up">
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-gray-900">Ask a Question</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition p-1">
                        <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Question Title</label>
                        <input
                            required
                            type="text"
                            value={form.title}
                            onChange={(e) => setForm({ ...form, title: e.target.value })}
                            placeholder="E.g., How to prevent rice leaf disease?"
                            className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 bg-gray-50 focus:bg-white transition-colors"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Category</label>
                        <select
                            value={form.category}
                            onChange={(e) => setForm({ ...form, category: e.target.value })}
                            className="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 bg-gray-50 focus:bg-white transition-colors appearance-none"
                        >
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                        <textarea
                            required
                            rows={4}
                            value={form.description}
                            onChange={(e) => setForm({ ...form, description: e.target.value })}
                            placeholder="Provide more details about your question..."
                            className="w-full px-4 py-3 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-krishi-500 bg-gray-50 focus:bg-white transition-colors resize-none"
                        />
                    </div>

                    <div className="pt-4 flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-6 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="px-6 py-2.5 text-sm font-medium text-white bg-krishi-600 hover:bg-krishi-700 rounded-full transition-colors shadow-lg shadow-krishi-500/25 disabled:opacity-50"
                        >
                            {loading ? 'Posting...' : 'Post Question'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

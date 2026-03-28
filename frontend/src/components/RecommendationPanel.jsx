import React from 'react';
import { Link } from 'react-router-dom';

const RecommendationPanel = ({ recommendation, loading }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-xl shadow-sm p-8 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
                <h3 className="text-xl font-semibold text-gray-800">Analyzing Field Data...</h3>
                <p className="text-gray-500 mt-2">Determining optimal fertilizer strategy based on your parameters.</p>
            </div>
        );
    }

    if (!recommendation) {
        return (
            <div className="bg-white rounded-xl shadow-sm p-8 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
                <div className="bg-gray-100 p-4 rounded-full mb-4">
                    <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9l-.707.707M12 18a6 6 0 100-12 6 6 0 000 12z" />
                    </svg>
                </div>
                <h3 className="text-xl font-semibold text-gray-800">Awaiting Data</h3>
                <p className="text-gray-500 mt-2 max-w-xs">
                    Fill out all parameters and click "Get Recommendation" to generate personalized insight.
                </p>
            </div>
        );
    }

    return (
        <div className="bg-white/80 backdrop-blur-xl rounded-[32px] shadow-2xl shadow-green-900/5 border border-white p-8 sticky top-6">
            <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
                <h3 className="text-2xl font-black text-gray-800">Results</h3>
                <div className="bg-emerald-100 text-emerald-700 px-3 py-1.5 rounded-full text-xs font-bold tracking-wider">
                    {Math.round(recommendation.confidence * 10000) / 100}% Confidence
                </div>
            </div>

            <div className="space-y-6">
                <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl border border-green-100/50">
                    <p className="text-xs text-green-600 uppercase tracking-widest font-bold mb-2">Recommended Fertilizer</p>
                    <p className="text-3xl font-black text-green-800 leading-tight">{recommendation.fertilizer}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                        <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Dosage</p>
                        <p className="text-lg font-bold text-gray-800">{recommendation.dosage}</p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                        <p className="text-xs text-gray-500 uppercase font-semibold mb-1">Expected Yield</p>
                        <p className="text-lg font-bold text-green-600">{recommendation.yield_increase}</p>
                    </div>
                </div>

                {recommendation.related_products && recommendation.related_products.length > 0 && (
                    <div className="pt-4 border-t border-gray-100">
                        <p className="text-[10px] font-black uppercase text-gray-400 tracking-wider mb-4">Available in Marketplace</p>
                        <div className="space-y-3">
                            {recommendation.related_products.map(prod => (
                                <Link to="/marketplace" key={prod.id} className="flex items-center gap-4 bg-white border border-gray-100 p-3 rounded-2xl hover:border-green-300 hover:shadow-md transition-all group">
                                    <div className="w-12 h-12 bg-gray-50 rounded-xl overflow-hidden shadow-sm flex-shrink-0">
                                        <img src={prod.image_url || 'https://via.placeholder.com/150'} alt={prod.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h4 className="text-sm font-bold text-gray-900 truncate group-hover:text-green-700 transition-colors">{prod.name}</h4>
                                        <p className="text-[10px] font-medium text-gray-500 truncate">by {prod.seller_name}</p>
                                    </div>
                                    <div className="text-right flex-shrink-0">
                                        <p className="text-sm font-black text-green-700">₹{prod.price}</p>
                                        <p className="text-[8px] font-bold text-gray-400 uppercase tracking-widest mt-0.5 group-hover:text-green-600">Buy Now &rarr;</p>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>
                )}

                <div className="pt-2">
                    <Link
                        to="/marketplace"
                        className="block w-full bg-green-600 hover:bg-green-700 text-white text-center font-bold py-4 rounded-xl transition duration-200 shadow-lg shadow-green-100 flex items-center justify-center gap-2"
                    >
                        Browse Full Marketplace
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                    </Link>
                </div>

                <p className="text-xs text-gray-400 text-center italic mt-4">
                    *Recommendations are based on ML model predictions and should be verified with local agricultural experts.
                </p>
            </div>
        </div>
    );
};

export default RecommendationPanel;

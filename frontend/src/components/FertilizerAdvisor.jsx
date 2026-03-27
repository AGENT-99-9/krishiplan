import React, { useState } from 'react';
import SoilParametersForm from './SoilParametersForm';
import NutrientInputs from './NutrientInputs';
import ClimateInputs from './ClimateInputs';
import CropInputs from './CropInputs';
import RecommendationPanel from './RecommendationPanel';
import SoilAnalysisUploader from './SoilAnalysisUploader';
import { aiApi } from '../api/aiApi';

const FertilizerAdvisor = () => {
    const [loading, setLoading] = useState(false);
    const [recommendation, setRecommendation] = useState(null);
    const [error, setError] = useState(null);
    const [autoFilled, setAutoFilled] = useState(false);

    const [formData, setFormData] = useState({
        soil_type: 'Loamy',
        soil_ph: 6.5,
        soil_moisture: 30,
        organic_carbon: 0.5,
        electrical_conductivity: 0.8,
        nitrogen: 60,
        phosphorus: 40,
        potassium: 50,
        temperature: 25,
        humidity: 60,
        rainfall: 1000,
        crop_type: 'Wheat',
        growth_stage: 'Vegetative',
        season: 'Rabi',
        previous_crop: 'None',
        irrigation_type: 'Drip',
        region: 'North'
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear auto-filled badge when user manually changes something
        setAutoFilled(false);
    };

    const handleAutoFill = (values) => {
        setFormData(prev => ({
            ...prev,
            ...values,
        }));
        setAutoFilled(true);
        setError(null);
        // Smooth scroll to the form
        setTimeout(() => {
            document.getElementById('precision-field-data')?.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
            });
        }, 200);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const result = await aiApi.getRecommendation(formData);
            setRecommendation(result);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to generate recommendation. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr] gap-10 animate-fade-in pb-12">
            <div className="space-y-0">
                {/* ── Smart Uploader ─────────────────────── */}
                <SoilAnalysisUploader onAutoFill={handleAutoFill} />

                {/* ── Main Form ──────────────────────────── */}
                <form onSubmit={handleSubmit} className="space-y-8">
                    <div id="precision-field-data" className="bg-white/80 backdrop-blur-xl rounded-[32px] shadow-2xl shadow-green-900/5 border border-white overflow-hidden">
                        <div className="p-8">
                            <div className="flex items-center gap-3 mb-8">
                                <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center text-green-600">
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <h2 className="text-2xl font-black text-gray-800">Precision Field Data</h2>
                                </div>
                                {autoFilled && (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-xs font-bold animate-fade-in">
                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                        </svg>
                                        Smart Auto-Filled
                                    </span>
                                )}
                            </div>

                            <div className="space-y-4">
                                <SoilParametersForm formData={formData} handleChange={handleChange} />
                                <NutrientInputs formData={formData} handleChange={handleChange} />
                                <ClimateInputs formData={formData} handleChange={handleChange} />
                                <CropInputs formData={formData} handleChange={handleChange} />
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className={`w-full mt-8 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-black py-5 rounded-[22px] text-lg transition-all shadow-xl shadow-green-600/30 active:scale-[0.98] ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center gap-3">
                                        <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Crunching Bio-Data...
                                    </span>
                                ) : 'Generate Optimized Strategy'}
                            </button>
                        </div>
                    </div>
                    {error && (
                        <div className="bg-red-50 border border-red-100 p-4 rounded-2xl flex items-center gap-3 text-red-600 animate-shake">
                            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="font-semibold">{error}</p>
                        </div>
                    )}
                </form>
            </div>

            <aside className="lg:sticky lg:top-24 h-fit">
                <RecommendationPanel recommendation={recommendation} loading={loading} />
            </aside>
        </div>
    );
};

export default FertilizerAdvisor;

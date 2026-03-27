import React, { useState, useRef } from 'react';
import { aiApi } from '../api/aiApi';

const SoilAnalysisUploader = ({ onAutoFill }) => {
    const [mode, setMode] = useState(null); // 'image' | 'document' | null
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dragOver, setDragOver] = useState(false);
    const [fileName, setFileName] = useState('');
    const fileInputRef = useRef(null);

    const resetState = () => {
        setResult(null);
        setError(null);
        setFileName('');
    };

    const handleModeSelect = (newMode) => {
        setMode(mode === newMode ? null : newMode);
        resetState();
    };

    const handleFile = async (file) => {
        if (!file || !mode) return;
        setFileName(file.name);
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            let data;
            if (mode === 'image') {
                data = await aiApi.extractSoilImage(file);
            } else {
                data = await aiApi.extractSoilDocument(file);
            }
            setResult(data);
        } catch (err) {
            console.error('Extraction error:', err);
            setError(
                err.response?.data?.detail ||
                'Failed to analyze. Please try with a clearer image.'
            );
        } finally {
            setLoading(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    };

    const handleInputChange = (e) => {
        const file = e.target.files[0];
        if (file) handleFile(file);
    };

    const handleAutoFill = () => {
        if (result?.form_values && onAutoFill) {
            onAutoFill(result.form_values);
        }
    };

    const filledCount = result?.form_values ? Object.keys(result.form_values).length : 0;

    return (
        <div className="bg-gradient-to-br from-emerald-50/80 to-teal-50/80 backdrop-blur-xl rounded-[28px] shadow-xl shadow-green-900/5 border border-emerald-100/50 overflow-hidden mb-8">
            {/* Header */}
            <div className="p-6 pb-4">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/30">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-lg font-black text-gray-800">Smart Auto-Fill</h3>
                        <p className="text-xs text-gray-500">Upload a soil photo or lab report to auto-fill parameters</p>
                    </div>
                </div>
            </div>

            {/* Mode Selector */}
            <div className="px-6 pb-4">
                <div className="flex gap-3">
                    <button
                        type="button"
                        onClick={() => handleModeSelect('image')}
                        className={`flex-1 flex items-center gap-3 px-4 py-3.5 rounded-2xl text-sm font-bold transition-all duration-300 border-2 cursor-pointer ${mode === 'image'
                                ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg shadow-emerald-600/30 scale-[1.02]'
                                : 'bg-white text-gray-600 border-gray-100 hover:border-emerald-300 hover:text-emerald-600'
                            }`}
                    >
                        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        <span className="truncate">Scan Soil Photo</span>
                    </button>
                    <button
                        type="button"
                        onClick={() => handleModeSelect('document')}
                        className={`flex-1 flex items-center gap-3 px-4 py-3.5 rounded-2xl text-sm font-bold transition-all duration-300 border-2 cursor-pointer ${mode === 'document'
                                ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg shadow-emerald-600/30 scale-[1.02]'
                                : 'bg-white text-gray-600 border-gray-100 hover:border-emerald-300 hover:text-emerald-600'
                            }`}
                    >
                        <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="truncate">Scan Lab Report</span>
                    </button>
                </div>
            </div>

            {/* Upload Zone */}
            {mode && (
                <div className="px-6 pb-6 animate-fade-in">
                    <div
                        onDrop={handleDrop}
                        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                        onDragLeave={() => setDragOver(false)}
                        onClick={() => !loading && fileInputRef.current?.click()}
                        className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-all duration-300 cursor-pointer ${dragOver
                                ? 'border-emerald-500 bg-emerald-50 scale-[1.01]'
                                : loading
                                    ? 'border-amber-300 bg-amber-50/50'
                                    : 'border-gray-200 bg-white/60 hover:border-emerald-400 hover:bg-emerald-50/30'
                            }`}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept={mode === 'image' ? 'image/*' : 'image/*,.pdf'}
                            onChange={handleInputChange}
                            className="hidden"
                        />

                        {loading ? (
                            <div className="py-2">
                                <div className="w-10 h-10 mx-auto mb-3 border-3 border-emerald-100 border-t-emerald-600 rounded-full animate-spin" />
                                <p className="text-sm font-bold text-emerald-700">
                                    {mode === 'image' ? 'Analyzing soil colors & texture…' : 'Running OCR & parsing report…'}
                                </p>
                                <p className="text-xs text-gray-400 mt-1">This may take 10-30 seconds</p>
                            </div>
                        ) : (
                            <div className="py-2">
                                <div className="w-12 h-12 mx-auto mb-3 bg-emerald-100 rounded-2xl flex items-center justify-center">
                                    <svg className="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                </div>
                                {fileName ? (
                                    <p className="text-sm font-semibold text-gray-700">{fileName}</p>
                                ) : (
                                    <>
                                        <p className="text-sm font-bold text-gray-700">
                                            Drop your {mode === 'image' ? 'soil photo' : 'lab report'} here
                                        </p>
                                        <p className="text-xs text-gray-400 mt-1">
                                            or click to browse • {mode === 'image' ? 'JPG, PNG' : 'JPG, PNG, PDF'}
                                        </p>
                                    </>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Error */}
                    {error && (
                        <div className="mt-4 bg-red-50 border border-red-100 p-3 rounded-xl flex items-center gap-2 text-red-600 text-sm">
                            <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="font-medium">{error}</p>
                        </div>
                    )}

                    {/* Result panel */}
                    {result && (
                        <div className="mt-4 space-y-4 animate-fade-in">
                            {/* Analysis summary */}
                            {mode === 'image' && result.analysis && (
                                <div className="bg-white rounded-2xl border border-gray-100 p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                                        <h4 className="text-sm font-bold text-gray-800">Soil Analysis Complete</h4>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                        {result.analysis.colour && (
                                            <div className="bg-amber-50 rounded-xl p-2.5">
                                                <span className="text-gray-500 block">Colour</span>
                                                <span className="font-bold text-gray-800">{result.analysis.colour.colour_name}</span>
                                            </div>
                                        )}
                                        {result.analysis.texture_class && (
                                            <div className="bg-emerald-50 rounded-xl p-2.5">
                                                <span className="text-gray-500 block">Texture</span>
                                                <span className="font-bold text-gray-800">{result.analysis.texture_class}</span>
                                            </div>
                                        )}
                                        {result.analysis.values?.ph && (
                                            <div className="bg-blue-50 rounded-xl p-2.5">
                                                <span className="text-gray-500 block">pH</span>
                                                <span className="font-bold text-gray-800">{result.analysis.values.ph}</span>
                                            </div>
                                        )}
                                        {result.analysis.values?.organic_carbon_pct && (
                                            <div className="bg-purple-50 rounded-xl p-2.5">
                                                <span className="text-gray-500 block">Organic Carbon</span>
                                                <span className="font-bold text-gray-800">{result.analysis.values.organic_carbon_pct}%</span>
                                            </div>
                                        )}
                                    </div>
                                    {result.analysis.health && (
                                        <div className="mt-3 flex flex-wrap gap-1.5">
                                            {Object.entries(result.analysis.health).map(([key, val]) => (
                                                <span key={key} className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${val.includes('✓') ? 'bg-green-100 text-green-700' :
                                                        val.includes('⚠') ? 'bg-red-100 text-red-700' :
                                                            'bg-gray-100 text-gray-600'
                                                    }`}>
                                                    {key}: {val}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}

                            {mode === 'document' && result.analysis?.soil_parameters && (
                                <div className="bg-white rounded-2xl border border-gray-100 p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                                        <h4 className="text-sm font-bold text-gray-800">Report Parsed Successfully</h4>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2 text-xs">
                                        {Object.entries(result.analysis.soil_parameters)
                                            .filter(([_, v]) => v)
                                            .map(([key, val]) => (
                                                <div key={key} className="bg-gray-50 rounded-xl p-2.5">
                                                    <span className="text-gray-500 block capitalize">{key.replace(/_/g, ' ')}</span>
                                                    <span className="font-bold text-gray-800">{val}</span>
                                                </div>
                                            ))
                                        }
                                    </div>
                                    {result.analysis.farmer_details?.name && (
                                        <p className="mt-2 text-xs text-gray-500">
                                            Farmer: <span className="font-semibold text-gray-700">{result.analysis.farmer_details.name}</span>
                                        </p>
                                    )}
                                </div>
                            )}

                            {/* Auto-fill button */}
                            {filledCount > 0 && (
                                <button
                                    type="button"
                                    onClick={handleAutoFill}
                                    className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white font-black py-4 rounded-2xl text-sm transition-all shadow-xl shadow-emerald-600/30 active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                    Auto-Fill {filledCount} Fields into Form Below
                                </button>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default SoilAnalysisUploader;

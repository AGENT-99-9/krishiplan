import React from 'react';

const NutrientInputs = ({ formData, handleChange }) => {
    return (
        <div className="mb-8">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-gray-100 pb-2">Nutrient Levels (mg/kg)</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Nitrogen (N)</label>
                    <input
                        type="number"
                        name="nitrogen"
                        value={formData.nitrogen}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Phosphorus (P)</label>
                    <input
                        type="number"
                        name="phosphorus"
                        value={formData.phosphorus}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Potassium (K)</label>
                    <input
                        type="number"
                        name="potassium"
                        value={formData.potassium}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
            </div>
        </div>
    );
};

export default NutrientInputs;

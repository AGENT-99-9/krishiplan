import React from 'react';

const ClimateInputs = ({ formData, handleChange }) => {
    return (
        <div className="mb-8">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-gray-100 pb-2">Climate Conditions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Temperature (°C)</label>
                    <input
                        type="number"
                        name="temperature"
                        value={formData.temperature}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Humidity (%)</label>
                    <input
                        type="number"
                        name="humidity"
                        value={formData.humidity}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Rainfall (mm)</label>
                    <input
                        type="number"
                        name="rainfall"
                        value={formData.rainfall}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
            </div>
        </div>
    );
};

export default ClimateInputs;

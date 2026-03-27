import React from 'react';

const SoilParametersForm = ({ formData, handleChange }) => {
    return (
        <div className="mb-8">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-gray-100 pb-2">Soil Parameters</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Soil Type</label>
                    <select
                        name="soil_type"
                        value={formData.soil_type}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                    >
                        <option value="Clay">Clay</option>
                        <option value="Sandy">Sandy</option>
                        <option value="Loamy">Loamy</option>
                        <option value="Silt">Silt</option>
                        <option value="Peaty">Peaty</option>
                        <option value="Chalky">Chalky</option>
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Soil pH</label>
                    <input
                        type="number"
                        step="0.1"
                        name="soil_ph"
                        value={formData.soil_ph}
                        onChange={handleChange}
                        placeholder="e.g. 6.5"
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Soil Moisture (%)</label>
                    <input
                        type="number"
                        name="soil_moisture"
                        value={formData.soil_moisture}
                        onChange={handleChange}
                        placeholder="e.g. 35"
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Organic Carbon (%)</label>
                    <input
                        type="number"
                        step="0.01"
                        name="organic_carbon"
                        value={formData.organic_carbon}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1 md:col-span-2">
                    <label className="text-sm font-medium text-gray-600">Electrical Conductivity (dS/m)</label>
                    <input
                        type="number"
                        step="0.01"
                        name="electrical_conductivity"
                        value={formData.electrical_conductivity}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                    />
                </div>
            </div>
        </div>
    );
};

export default SoilParametersForm;

import React from 'react';

const CropInputs = ({ formData, handleChange }) => {
    return (
        <div className="mb-8">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4 border-b border-gray-100 pb-2">Crop Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Crop Type</label>
                    <select
                        name="crop_type"
                        value={formData.crop_type}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    >
                        <option value="Maize">Maize</option>
                        <option value="Rice">Rice</option>
                        <option value="Wheat">Wheat</option>
                        <option value="Cotton">Cotton</option>
                        <option value="Sugarcane">Sugarcane</option>
                        <option value="Potato">Potato</option>
                        <option value="Tomato">Tomato</option>
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Growth Stage</label>
                    <select
                        name="growth_stage"
                        value={formData.growth_stage}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    >
                        <option value="Sowing">Sowing</option>
                        <option value="Vegetative">Vegetative</option>
                        <option value="Flowering">Flowering</option>
                        <option value="Harvest">Harvest / Maturity</option>
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Season</label>
                    <select
                        name="season"
                        value={formData.season}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    >
                        <option value="Kharif">Kharif</option>
                        <option value="Rabi">Rabi</option>
                        <option value="Zaid">Zaid</option>
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Irrigation Type</label>
                    <select
                        name="irrigation_type"
                        value={formData.irrigation_type}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    >
                        <option value="Flood">Flood / Canal</option>
                        <option value="Drip">Drip</option>
                        <option value="Sprinkler">Sprinkler</option>
                        <option value="Rainfed">Rainfed</option>
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Previous Crop</label>
                    <input
                        type="text"
                        name="previous_crop"
                        value={formData.previous_crop}
                        onChange={handleChange}
                        placeholder="e.g. Rice"
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-sm font-medium text-gray-600">Region</label>
                    <select
                        name="region"
                        value={formData.region}
                        onChange={handleChange}
                        className="w-full rounded-lg border p-3 focus:ring-2 focus:ring-green-500 outline-none"
                    >
                        <option value="North">North India</option>
                        <option value="South">South India</option>
                        <option value="East">East India</option>
                        <option value="West">West India</option>
                        <option value="Central">Central India</option>
                    </select>
                </div>
            </div>
        </div>
    );
};

export default CropInputs;

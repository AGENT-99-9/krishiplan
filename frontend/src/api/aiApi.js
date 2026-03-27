import axiosClient from './axiosClient';

export const aiApi = {
    // Existing: fertilizer recommendation
    getRecommendation: async (data) => {
        const response = await axiosClient.post('ai/recommendation/', data);
        return response.data;
    },

    // NEW: Upload soil photo → get predictions + auto-fill values
    extractSoilImage: async (imageFile) => {
        const formData = new FormData();
        formData.append('image', imageFile);
        const response = await axiosClient.post('ai/extract-soil-image/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 120000, // 2 min — ML inference can be slow
        });
        return response.data;
    },

    // NEW: Upload soil lab report (image/PDF) → OCR + parse + auto-fill values
    extractSoilDocument: async (docFile) => {
        const formData = new FormData();
        formData.append('document', docFile);
        const response = await axiosClient.post('ai/extract-soil-document/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 120000,
        });
        return response.data;
    },

    // NEW: Fetch saved soil analysis reports
    getSoilReports: async () => {
        const response = await axiosClient.get('ai/soil-reports/');
        return response.data;
    },
};

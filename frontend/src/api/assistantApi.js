import axiosClient from './axiosClient';

const assistantApi = {
    askQuestion: async (query) => {
        const res = await axiosClient.post('assistant/ask/', { query });
        return res.data;
    },
    getStatus: async () => {
        const res = await axiosClient.get('assistant/status/');
        return res.data;
    }
};

export default assistantApi;

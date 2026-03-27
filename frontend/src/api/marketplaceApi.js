import axiosClient from './axiosClient';

const marketplaceApi = {
    fetchProducts: async (params) => {
        const res = await axiosClient.get('marketplace/products/', { params });
        return res.data;
    },
    fetchProduct: async (id) => {
        const res = await axiosClient.get(`marketplace/products/${id}/`);
        return res.data;
    },
    createProduct: async (productData) => {
        const res = await axiosClient.post('marketplace/products/', productData);
        return res.data;
    },
    buyProduct: async (orderData) => {
        const res = await axiosClient.post('marketplace/orders/', orderData);
        return res.data;
    },
    fetchOrders: async () => {
        const res = await axiosClient.get('marketplace/orders/');
        return res.data;
    }
};

export default marketplaceApi;

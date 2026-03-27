import axiosClient from './axiosClient';

const communityApi = {
    fetchPosts: async (params) => {
        const res = await axiosClient.get('community/posts/', { params });
        return res.data;
    },
    fetchTrending: async () => {
        const res = await axiosClient.get('community/trending/');
        return res.data;
    },
    fetchContributors: async () => {
        const res = await axiosClient.get('community/contributors/');
        return res.data;
    },
    createPost: async (postData) => {
        const res = await axiosClient.post('community/create/', postData);
        return res.data;
    },
    likePost: async (postId) => {
        const res = await axiosClient.post(`community/posts/${postId}/like/`);
        return res.data;
    },
    createComment: async (postId, comment) => {
        const res = await axiosClient.post(`community/posts/${postId}/comment/`, { comment });
        return res.data;
    }
};

export default communityApi;

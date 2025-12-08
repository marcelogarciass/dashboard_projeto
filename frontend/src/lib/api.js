import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api',
});

export const getFilters = async () => {
    const response = await api.get('/filters');
    return response.data;
};

export const getDashboardData = async (filters) => {
    const response = await api.post('/dashboard', filters);
    return response.data;
};

export default api;
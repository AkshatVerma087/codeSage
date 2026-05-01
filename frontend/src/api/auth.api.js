export const login = async (credentials, axiosInstance) => {
  const response = await axiosInstance.post('/api/auth/login', credentials);
  return response.data;
};

export const register = async (data, axiosInstance) => {
  const response = await axiosInstance.post('/api/auth/register', data);
  return response.data;
};

export const logout = async (axiosInstance) => {
  const response = await axiosInstance.post('/api/auth/logout');
  return response.data;
};
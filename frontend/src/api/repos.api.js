export const createRepo = async (repoData, axiosInstance) => {
    const { data } = await axiosInstance.post('/api/repos', repoData)
    return data
}

export const getRepos = async (axiosInstance) => {
    const { data } = await axiosInstance.get('/api/repos')
    return data
}

export const getRepoById = async (repoId, axiosInstance) => {
    const { data } = await axiosInstance.get(`/api/repos/${repoId}`)
    return data
}

export const deleteRepo = async (repoId, axiosInstance) => {
    const { data } = await axiosInstance.delete(`/api/repos/${repoId}`)
    return data
}
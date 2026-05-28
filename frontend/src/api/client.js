import axios from "axios"

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

const client = axios.create({
  baseURL: API_BASE_URL,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("esg_token")
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("esg_token")
      localStorage.removeItem("esg_email")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  },
)

export default client
export { API_BASE_URL }

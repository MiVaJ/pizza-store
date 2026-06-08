import axios from 'axios';

// Создаем клиент для отправки запросов на FastAPI
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

let isRefreshing = false;

// Создаём перехватчик ответов (response)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Если кука доступа умерла и мы еще не пытались её обновить
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;

        try {
          // Делаем тихий запрос на обновление токенов
          await axios.post(
            `${api.defaults.baseURL}/api/auth/refresh`,
            {},
            { withCredentials: true },
          );

          isRefreshing = false;
          // Повторяем запрос пользователя с уже обновленной кукой доступа
          return api(originalRequest);
        } catch (refreshError) {
          isRefreshing = false;
          // Если даже после обновления сессия закрыта, то редиректим для повторного логина
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      }
    }

    // Возвращаем ошибки
    return Promise.reject(error);
  },
);

export default api;

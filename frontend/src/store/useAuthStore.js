import { create } from 'zustand';
import api from '../core/api';

export const useAuthStore = create((set) => ({
  user: null,
  isAuth: false,

  // Функция входа в систему
  login: async (loginData) => {
    // Отправляем JSON. Куки fastapi_access и fastapi_refresh встанут автоматически
    await api.post('/api/auth/login', loginData);

    // Сразу запрашиваем данные профиля (эндпоинт /api/auth/me, который напишем позже)
    const response = await api.get('/api/auth/me');
    set({ user: response.data, isAuth: true });
  },

  // Функция выхода из системы
  logout: async () => {
    set({ user: null, isAuth: false });
    window.location.href = '/login';
  },

  // Автоматическая проверка сессии при перезагрузке страницы
  checkAuth: async () => {
    try {
      const response = await api.get('/api/auth/me');
      set({ user: response.data, isAuth: true });
    } catch (error) {
      // Если даже после интерцептора запрос упал — сессия полностью мертва
      set({ user: null, isAuth: false });
    }
  },
}));

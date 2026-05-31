import axios from 'axios';

// Создаем клиент для отправки запросов на FastAPI
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;

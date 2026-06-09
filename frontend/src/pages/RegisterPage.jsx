import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/core/api';
import { useAuthStore } from '@/store/useAuthStore';

export default function RegisterPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const [form, setForm] = useState({
    email: '',
    password: '',
    name: '',
    phone: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Регистрируем пользователя
      await api.post('/api/auth/register', {
        email: form.email,
        password: form.password,
        name: form.name || undefined,
        phone: form.phone || undefined,
      });

      // Сразу логиним после регистрации
      await login({ email: form.email, password: form.password });
      navigate('/');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg.replace(/^value error,\s*/i, '')).join(' · '));
      } else {
        setError(detail || 'Не удалось зарегистрироваться. Попробуйте ещё раз.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh] px-4">
      <div className="w-full max-w-md p-6 bg-white border border-gray-100 rounded-2xl">
        <div className="text-center mb-6">
          <span className="text-4xl">🍕</span>
          <h1 className="text-2xl font-black text-gray-800 mt-2">Регистрация</h1>
          <p className="text-sm text-gray-400 mt-1">Создайте аккаунт в ПиццаТут</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Email <span className="text-red-400">*</span>
            </label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              required
              placeholder="example@pizza.ru"
              className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
                placeholder:text-gray-300 focus:outline-none focus:border-orange-400
                transition-colors"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Пароль <span className="text-red-400">*</span>
            </label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              required
              placeholder="Минимум 6 символов"
              className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
                placeholder:text-gray-300 focus:outline-none focus:border-orange-400
                transition-colors"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Имя
            </label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Иван Петров"
              className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
                placeholder:text-gray-300 focus:outline-none focus:border-orange-400
                transition-colors"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Телефон
            </label>
            <input
              type="tel"
              name="phone"
              value={form.phone}
              onChange={handleChange}
              placeholder="+7 900 000-00-00"
              className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
                placeholder:text-gray-300 focus:outline-none focus:border-orange-400
                transition-colors"
            />
          </div>

          {error && <p className="text-sm text-red-500 bg-red-50 rounded-xl px-4 py-3">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300
              text-white font-bold text-sm rounded-xl transition-colors active:scale-[0.99]
              cursor-pointer select-none mt-1"
          >
            {loading ? 'Регистрируем...' : 'Создать аккаунт'}
          </button>

          <p className="text-center text-sm text-gray-400">
            Уже есть аккаунт?{' '}
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-orange-500 font-semibold hover:underline cursor-pointer"
            >
              Войти
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}

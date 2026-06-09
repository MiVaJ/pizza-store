import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Неверная почта или пароль');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh] px-4">
      <div className="w-full max-w-md p-6 bg-white border border-gray-100 rounded-2xl">
        <div className="text-center mb-6">
          <span className="text-4xl">🍕</span>
          <h1 className="text-2xl font-black text-gray-800 mt-2">Вход в ПиццаТут</h1>
          <p className="text-sm text-gray-400 mt-1">Введите email и пароль</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="example@pizza.ru"
              className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
                placeholder:text-gray-300 focus:outline-none focus:border-orange-400
                transition-colors"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
                placeholder:text-gray-300 focus:outline-none focus:border-orange-400
                transition-colors"
              placeholder="••••••••"
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
            {loading ? 'Входим...' : 'Войти в аккаунт'}
          </button>

          <p className="text-center text-sm text-gray-400">
            Нет аккаунта?{' '}
            <button
              type="button"
              onClick={() => navigate('/register')}
              className="text-orange-500 font-semibold hover:underline cursor-pointer"
            >
              Зарегистрироваться
            </button>
          </p>
        </form>
      </div>
    </div>
  );
}

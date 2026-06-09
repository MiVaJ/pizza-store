import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useAuthStore } from '@/store/useAuthStore';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const login = useAuthStore((state) => state.login);
  const isAuth = useAuthStore((state) => state.isAuth);
  const user = useAuthStore((state) => state.user);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login({ email, password });
    } catch (err) {
      setError(err.response?.data?.detail || 'Неверная почта или пароль');
    }
  };

  // Экран успешного входа
  if (isAuth && user) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] p-6 text-center">
        <div className="w-full max-w-md p-6 bg-background border border-border rounded-xl shadow-sm">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Вы успешно вошли, {user.name}!
          </h2>
          <p className="text-sm text-muted-foreground">
            Ваша роль в системе: <span className="font-semibold text-primary">{user.role}</span>
          </p>
        </div>
      </div>
    );
  }

  // Экран формы авторизации
  return (
    <div className="flex items-center justify-center min-h-[70vh] px-4">
      <div className="w-full max-w-md p-6 bg-background border border-border rounded-xl shadow-sm">
        <h2 className="text-2xl text-orange-500 font-bold text-center text-foreground mb-6">
          Вход в ПиццаТут
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-muted-foreground">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full h-9 px-3 text-sm bg-background border border-input rounded-lg
                outline-none focus-visible:border-ring focus-visible:ring-2
                focus-visible:ring-ring/20 transition-all"
              placeholder="example@pizza.ru"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-muted-foreground">Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full h-9 px-3 text-sm bg-background border border-input rounded-lg
                outline-none focus-visible:border-ring focus-visible:ring-2
                focus-visible:ring-ring/20 transition-all"
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-sm font-medium text-destructive mt-1">{error}</p>}

          <Button
            type="submit"
            variant="default"
            size="lg"
            className="w-full mt-2 bg-orange-500 px-4 font-bold text-white shadow-sm transition-all
              duration-300 hover:bg-orange-600 text-sm cursor-pointer select-none"
          >
            Войти в аккаунт
          </Button>
        </form>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import api from '@/core/api';
import { useAuthStore } from '@/store/useAuthStore';

const ROLE_LABELS = {
  client: 'Клиент',
  manager: 'Менеджер',
  courier: 'Курьер',
  admin: 'Админ',
};

const ROLE_COLORS = {
  client: 'bg-gray-100 text-gray-600',
  manager: 'bg-blue-50 text-blue-600',
  courier: 'bg-purple-50 text-purple-600',
  admin: 'bg-orange-50 text-orange-600',
};

export default function AdminPage() {
  const { user: currentUser } = useAuthStore();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ email: '', password: '', name: '', role: 'manager' });
  const [creating, setCreating] = useState(false);
  const [formError, setFormError] = useState(null);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/admin/users');
      setUsers(response.data);
    } catch (err) {
      setError('Не удалось загрузить список пользователей');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleCreateUser = async () => {
    setCreating(true);
    setFormError(null);
    try {
      const response = await api.post('/api/admin/users', form);
      setUsers((prev) => [...prev, response.data]);
      setForm({ email: '', password: '', name: '', role: 'manager' });
      setShowForm(false);
    } catch (err) {
      setFormError(err.response?.data?.detail ?? 'Не удалось создать пользователя');
    } finally {
      setCreating(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    setUpdatingId(userId);
    try {
      const response = await api.patch(`/api/admin/users/${userId}/role`, {
        role: newRole,
      });
      setUsers((prev) => prev.map((u) => (u.id === userId ? response.data : u)));
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Не удалось обновить роль');
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) return <p className="p-6 text-gray-400">Загрузка...</p>;

  return (
    <section className="mx-auto max-w-3xl p-6 space-y-4">
      {/* Заголовок и Кнопка */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-black text-gray-800">Пользователи</h1>
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="h-9 px-4 bg-orange-500 hover:bg-orange-600 text-white text-sm font-bold
            rounded-xl transition-colors cursor-pointer"
        >
          {showForm ? 'Отмена' : '+ Новый пользователь'}
        </button>
      </div>

      {/* Форма создания */}
      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
          <h2 className="text-sm font-semibold text-gray-800">Новый пользователь</h2>

          <div className="grid grid-cols-2 gap-3">
            {/* Email */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Email
              </label>
              <input
                value={form.email}
                onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                placeholder="user@pizzatut.ru"
                autoComplete="email"
                type="email"
                className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm
                  focus:outline-none focus:border-orange-400 transition-colors"
              />
            </div>

            {/* Имя */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Имя
              </label>
              <input
                value={form.name}
                onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                placeholder="Иван Петров"
                type="text"
                autoComplete="name"
                className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm
                  focus:outline-none focus:border-orange-400 transition-colors"
              />
            </div>

            {/* Пароль */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Пароль
              </label>
              <input
                type="password"
                value={form.password}
                onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                placeholder="••••••••"
                autoComplete="new-password"
                className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm
                  focus:outline-none focus:border-orange-400 transition-colors"
              />
            </div>

            {/* Роль */}
            <div className="space-y-1">
              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                Роль
              </label>
              <select
                value={form.role}
                onChange={(e) => setForm((p) => ({ ...p, role: e.target.value }))}
                className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm
                  focus:outline-none focus:border-orange-400 transition-colors cursor-pointer"
              >
                <option value="manager">Менеджер</option>
                <option value="courier">Курьер</option>
                <option value="admin">Админ</option>
              </select>
            </div>
          </div>

          {formError && (
            <p className="text-sm text-red-500 bg-red-50 rounded-xl px-4 py-3">{formError}</p>
          )}

          <button
            onClick={handleCreateUser}
            disabled={creating || !form.email || !form.password}
            className="w-full h-10 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300
              text-white text-sm font-bold rounded-xl transition-colors cursor-pointer"
          >
            {creating ? 'Создаём...' : 'Создать пользователя'}
          </button>
        </div>
      )}

      {/* Ошибки */}
      {error && <p className="text-sm text-red-500 bg-red-50 rounded-xl px-4 py-3">{error}</p>}

      {users.length === 0 && <p className="text-gray-400 text-sm">Пользователей пока нет.</p>}

      {/* Список пользователей */}
      <ul className="space-y-3">
        {users.map((user) => (
          <li key={user.id} className="bg-white rounded-2xl border border-gray-100 p-4 space-y-2">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <div
                  className="w-9 h-9 rounded-full bg-orange-100 flex items-center justify-center
                    text-orange-600 text-sm font-bold flex-shrink-0"
                >
                  {user.name?.[0]?.toUpperCase() ?? user.email[0].toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-gray-800">{user.name ?? 'Без имени'}</p>
                  <p className="text-sm text-gray-400">{user.email}</p>
                </div>
              </div>

              <span
                className={`text-xs font-medium px-2.5 py-1 rounded-full ${ROLE_COLORS[user.role]}`}
              >
                {ROLE_LABELS[user.role]}
              </span>
            </div>

            {user.id !== currentUser?.id && (
              <div className="flex items-center gap-2 pt-1">
                <span className="text-xs text-gray-400">Изменить роль:</span>
                <select
                  value={user.role}
                  disabled={updatingId === user.id}
                  onChange={(e) => handleRoleChange(user.id, e.target.value)}
                  className="ml-auto text-sm border border-gray-200 rounded-lg px-2 py-1
                    cursor-pointer focus:outline-none focus:border-orange-400 disabled:opacity-50"
                >
                  {Object.entries(ROLE_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {user.id === currentUser?.id && (
              <p className="text-xs text-gray-300 pt-1">Это вы - роль нельзя изменить</p>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

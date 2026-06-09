import React, { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/core/api';

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const [ordersRes, statsRes] = await Promise.all([
          api.get('/api/orders/my'),
          api.get('/api/orders/my/stats'),
        ]);
        setOrders(ordersRes.data);
        setStats(statsRes.data);
      } catch (error) {
        console.error('Ошибка при загрузке профиля:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <p className="animate-bounce text-3xl">👤</p>
          <p className="mt-2 text-sm font-medium text-gray-400">Загружаем профиль...</p>
        </div>
      </div>
    );
  }

  return (
    <section className="mx-auto max-w-4xl p-6 space-y-6">
      {/* Шапка профиля */}
      <div
        className="bg-white rounded-2xl border border-gray-100 p-5 flex items-center
          justify-between"
      >
        <div className="flex items-center gap-4">
          <div
            className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center
              text-orange-600 font-semibold text-lg"
          >
            {user?.name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-800 text-base">{user?.name ?? 'Без имени'}</p>
            <p className="text-sm text-gray-400">{user?.email}</p>
            {user?.phone && <p className="text-sm text-gray-400">{user.phone}</p>}
          </div>
        </div>
        <span className="text-xs font-medium px-3 py-1 rounded-full bg-gray-100 text-gray-500">
          {user?.role}
        </span>
      </div>

      {/* Метрики */}
      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <p className="text-xs text-gray-400 mb-1">Заказов</p>
            <p className="text-2xl font-semibold text-gray-800">{stats.total_orders}</p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <p className="text-xs text-gray-400 mb-1">Потрачено</p>
            <p className="text-2xl font-semibold text-gray-800">
              {stats.total_spent.toLocaleString('ru-RU')} ₽
            </p>
          </div>
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <p className="text-xs text-gray-400 mb-1">Любимая пицца</p>
            <p className="text-lg font-semibold text-gray-800 truncate">
              {stats.favourite_pizza ?? '—'}
            </p>
          </div>
        </div>
      )}

      {/* История заказов */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5">
        <h2 className="text-base font-semibold text-gray-800 mb-4">История заказов</h2>

        {orders.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-3xl mb-2">🍕</p>
            <p className="text-sm text-gray-400">Заказов пока нет</p>
          </div>
        ) : (
          <ul className="space-y-3">
            {orders.map((order) => (
              <li
                key={order.id}
                className="flex items-center justify-between py-3 border-b border-gray-50
                  last:border-none"
              >
                <div>
                  <p className="text-sm font-medium text-gray-800">
                    № {order.id} · {order.items.map((i) => i.product_name).join(', ')}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(order.created_at).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={order.status} />
                  <span className="text-sm font-semibold text-gray-800">
                    {order.total_price.toLocaleString('ru-RU')} ₽
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

// Компонент бейджа статуса заказа
const STATUS_CONFIG = {
  pending: { label: 'Ожидает', className: 'bg-yellow-50 text-yellow-600' },
  cooking: { label: 'Готовится', className: 'bg-blue-50 text-blue-600' },
  delivering: { label: 'В пути', className: 'bg-purple-50 text-purple-600' },
  completed: { label: 'Доставлен', className: 'bg-green-50 text-green-600' },
  cancelled: { label: 'Отменён', className: 'bg-red-50 text-red-600' },
};

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? { label: status, className: 'bg-gray-100 text-gray-500' };
  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${config.className}`}>
      {config.label}
    </span>
  );
}

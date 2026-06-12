import React, { useState, useEffect } from 'react';
import api from '@/core/api';

const STATUS_LABELS = {
  pending: 'Ожидает',
  cooking: 'Готовится',
  delivering: 'В пути',
  completed: 'Доставлен',
  cancelled: 'Отменён',
};

// Допустимые переходы — синхронизировано с бэкендом
const ALLOWED_TRANSITIONS = {
  pending: ['cooking', 'cancelled'],
  cooking: ['delivering', 'cancelled'],
  delivering: ['completed', 'cancelled'],
  completed: [],
  cancelled: [],
};

export default function ManagerOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/api/orders/');
      setOrders(response.data);
    } catch (err) {
      setError('Не удалось загрузить заказы');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleStatusChange = async (orderId, newStatus) => {
    setUpdatingId(orderId);
    try {
      const response = await api.patch(`/api/orders/${orderId}/status`, {
        status: newStatus,
      });
      setOrders((prev) => prev.map((o) => (o.id === orderId ? response.data : o)));
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Не удалось обновить статус');
    } finally {
      setUpdatingId(null);
    }
  };

  if (loading) return <p className="p-6 text-gray-400">Загрузка...</p>;

  return (
    <section className="mx-auto max-w-3xl p-6 space-y-4">
      <h1 className="text-2xl font-black text-gray-800">Заказы</h1>

      {error && <p className="text-sm text-red-500 bg-red-50 rounded-xl px-4 py-3">{error}</p>}

      {orders.length === 0 && <p className="text-gray-400 text-sm">Заказов пока нет.</p>}

      <ul className="space-y-3">
        {orders.map((order) => {
          const nextStatuses = ALLOWED_TRANSITIONS[order.status] ?? [];
          return (
            <li
              key={order.id}
              className="bg-white rounded-2xl border border-gray-100 p-4 space-y-2"
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold text-gray-800">
                    Заказ №{order.id} — {order.customer_name}
                  </p>
                  <p className="text-sm text-gray-400">
                    {order.phone} · {order.delivery_address}
                  </p>
                </div>
                <span className="text-sm font-bold text-gray-800">
                  {order.total_price.toLocaleString('ru-RU')} ₽
                </span>
              </div>

              <ul className="text-sm text-gray-600 space-y-1">
                {order.items.map((item) => (
                  <li key={item.id}>
                    {item.product_name} × {item.quantity}
                  </li>
                ))}
              </ul>

              <div className="flex items-center gap-2 pt-2">
                <span className="text-xs font-semibold text-gray-500 uppercase">
                  Статус: {STATUS_LABELS[order.status]}
                </span>

                {nextStatuses.length > 0 && (
                  <select
                    value=""
                    disabled={updatingId === order.id}
                    onChange={(e) => handleStatusChange(order.id, e.target.value)}
                    className="ml-auto text-sm border border-gray-200 rounded-lg px-2 py-1
                      cursor-pointer focus:outline-none focus:border-orange-400"
                  >
                    <option value="" disabled>
                      Изменить статус
                    </option>
                    {nextStatuses.map((s) => (
                      <option key={s} value={s}>
                        {STATUS_LABELS[s]}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

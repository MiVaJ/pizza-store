import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '@/store/useCartStore';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/core/api';

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { items, totalPrice, clearCart } = useCartStore();
  const { user } = useAuthStore();

  const [form, setForm] = useState({
    customer_name: user?.name ?? '',
    phone: user?.phone ?? '',
    delivery_address: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [orderPlaced, setOrderPlaced] = useState(false);

  // Если корзина пустая - редиректим на главную
  useEffect(() => {
    if (items.length === 0 && !orderPlaced) {
      navigate('/');
    }
  }, [items.length, orderPlaced]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async () => {
    setOrderPlaced(true);
    setError(null);
    setLoading(true);

    try {
      // Формируем items для бэкенда
      const orderItems = items.map((item) => {
        // Извлекаем id соусов вида "sauce-5"
        if (String(item.id).startsWith('sauce-')) {
          return {
            ingredient_id: parseInt(item.id.replace('sauce-', '')),
            pizza_id: null,
            quantity: item.quantity,
          };
        }
        return {
          pizza_id: item.id,
          ingredient_id: null,
          quantity: item.quantity,
        };
      });

      const payload = {
        customer_name: form.customer_name,
        phone: form.phone,
        delivery_address: form.delivery_address,
        items: orderItems,
      };

      await api.post('/api/orders/', payload);

      clearCart();
      navigate('/profile');
    } catch (err) {
      console.log('err:', err);
      console.log('err.response:', err.response);
      console.log('detail:', err.response?.data?.detail);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        const messages = detail.map((d) => d.msg.replace(/^value error,\s*/i, ''));
        setError(messages.join(', '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError(detail ?? 'Не удалось оформить заказ. Попробуйте ещё раз.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-lg p-6 space-y-6">
      {/* Заголовок */}
      <div>
        <h1 className="text-2xl font-black text-gray-800">Оформление заказа</h1>
        <p className="text-sm text-gray-400 mt-1">Проверьте данные доставки</p>
      </div>

      {/* Форма */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5 space-y-4">
        <div className="space-y-1">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Имя получателя
          </label>
          <input
            name="customer_name"
            value={form.customer_name}
            onChange={handleChange}
            placeholder="Иван Петров"
            className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
              placeholder:text-gray-300 focus:outline-none focus:border-orange-400
              transition-colors"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Телефон
          </label>
          <input
            name="phone"
            value={form.phone}
            onChange={handleChange}
            placeholder="+7 900 000-00-00"
            className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
              placeholder:text-gray-300 focus:outline-none focus:border-orange-400
              transition-colors"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
            Адрес доставки
          </label>
          <input
            name="delivery_address"
            value={form.delivery_address}
            onChange={handleChange}
            placeholder="ул. Пушкина, д. 10, кв. 5"
            className="w-full h-10 px-3 rounded-xl border border-gray-200 text-sm text-gray-800
              placeholder:text-gray-300 focus:outline-none focus:border-orange-400
              transition-colors"
          />
        </div>
      </div>

      {/* Состав заказа */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <h2 className="text-sm font-semibold text-gray-800">Состав заказа</h2>
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.id} className="flex justify-between text-sm">
              <span className="text-gray-700">
                {item.name}
                {item.quantity > 1 && <span className="text-gray-400"> × {item.quantity}</span>}
              </span>
              <span className="font-semibold text-gray-800">
                {(item.price * item.quantity).toLocaleString('ru-RU')} ₽
              </span>
            </li>
          ))}
        </ul>
        <div className="border-t border-gray-100 pt-3 flex justify-between">
          <span className="text-sm font-medium text-gray-400">Итого</span>
          <span className="text-lg font-black text-gray-900">
            {totalPrice.toLocaleString('ru-RU')} ₽
          </span>
        </div>
      </div>

      {/* Ошибка */}
      {error && <p className="text-sm text-red-500 bg-red-50 rounded-xl px-4 py-3">{error}</p>}

      {/* Кнопка */}
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full h-12 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white
          font-bold text-sm rounded-xl transition-colors active:scale-[0.99] duration-150
          cursor-pointer"
      >
        {loading ? 'Оформляем...' : 'Подтвердить заказ'}
      </button>
    </section>
  );
}

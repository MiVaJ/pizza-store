import React, { useState, useEffect, useRef } from 'react';
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
  const [paymentType, setPaymentType] = useState('card');
  const [savedCard, setSavedCard] = useState(null);
  const [useSavedCard, setUseSavedCard] = useState(false);
  const [saveCard, setSaveCard] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [orderPlaced, setOrderPlaced] = useState(false);

  const [showWidget, setShowWidget] = useState(false);
  const [confirmationToken, setConfirmationToken] = useState(null);
  const widgetRef = useRef(null);

  // Загрузка SDK ЮКассы при монтировании
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://yookassa.ru/checkout-widget/v1/checkout-widget.js';
    script.async = true;
    document.head.appendChild(script);
    return () => document.head.removeChild(script);
  }, []);

  // Инициализация виджета когда есть токен
  useEffect(() => {
    if (!confirmationToken || !showWidget) return;

    const checkout = new window.YooMoneyCheckoutWidget({
      confirmation_token: confirmationToken,
      return_url: 'http://localhost:5173/payment/success',
      customization: {
        colors: {
          controlPrimary: '#f97316',
        },
      },
      error_callback: (error) => {
        console.error('Ошибка виджета:', error);
        setError('Ошибка при инициализации оплаты');
        setShowWidget(false);
      },
    });

    checkout.render('payment-widget');

    return () => checkout.destroy();
  }, [confirmationToken, showWidget]);

  // Загружаем информацию о сохранённой карте
  useEffect(() => {
    if (user) {
      api
        .get('/api/payments/saved-card')
        .then((res) => setSavedCard(res.data))
        .catch(() => {});
    }
  }, [user]);

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

      // Создаём заказ
      const orderRes = await api.post('/api/orders/', {
        customer_name: form.customer_name,
        phone: form.phone,
        delivery_address: form.delivery_address,
        items: orderItems,
      });

      const orderId = orderRes.data.id;

      // Создаём платёж
      const paymentRes = await api.post('/api/payments/create', {
        order_id: orderId,
        save_card: saveCard,
        use_saved_card: paymentType === 'saved',
        payment_type: paymentType,
      });

      // Если производится автосписание с сохранённой карты, то сразу переходим на профиль
      if (paymentType === 'saved') {
        clearCart();
        navigate('/profile');
        return;
      }

      // Если нет сохранённой карты, то показываетм виджет ЮКассы
      setConfirmationToken(paymentRes.data.confirmation_token);
      setShowWidget(true);
    } catch (err) {
      setOrderPlaced(false);
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

      {/* Способ оплаты */}
      <div className="bg-white rounded-2xl border border-gray-100 p-5 space-y-3">
        <h2 className="text-sm font-semibold text-gray-800">Способ оплаты</h2>

        <div className="space-y-2">
          {/* Банковская карта */}
          <button
            onClick={() => {
              setUseSavedCard(false);
              setPaymentType('card');
            }}
            className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-colors
              cursor-pointer text-left ${
                paymentType === 'card'
                  ? 'border-orange-400 bg-orange-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
          >
            <div
              className={`w-4 h-4 rounded-full border-2 flex items-center justify-center
                flex-shrink-0 ${paymentType === 'card' ? 'border-orange-500' : 'border-gray-300'}`}
            >
              {paymentType === 'card' && <div className="w-2 h-2 rounded-full bg-orange-500" />}
            </div>
            <p className="text-sm font-medium text-gray-800">Банковская карта</p>
          </button>

          {/* СБП */}
          <button
            onClick={() => {
              setUseSavedCard(false);
              setPaymentType('sbp');
            }}
            className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-colors
              cursor-pointer text-left ${
                paymentType === 'sbp'
                  ? 'border-orange-400 bg-orange-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
          >
            <div
              className={`w-4 h-4 rounded-full border-2 flex items-center justify-center
                flex-shrink-0 ${paymentType === 'sbp' ? 'border-orange-500' : 'border-gray-300'}`}
            >
              {paymentType === 'sbp' && <div className="w-2 h-2 rounded-full bg-orange-500" />}
            </div>
            <p className="text-sm font-medium text-gray-800">СБП</p>
          </button>

          {/* Сохранённая карта (только если есть). */}
          {savedCard?.has_saved_card && (
            <button
              onClick={() => {
                setUseSavedCard(true);
                setPaymentType('saved');
              }}
              className={`w-full flex items-center gap-3 p-3 rounded-xl border transition-colors
              cursor-pointer text-left ${
                paymentType === 'saved'
                  ? 'border-orange-400 bg-orange-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div
                className={`w-4 h-4 rounded-full border-2 flex items-center justify-center
                flex-shrink-0 ${paymentType === 'saved' ? 'border-orange-500' : 'border-gray-300'}`}
              >
                {paymentType === 'saved' && <div className="w-2 h-2 rounded-full bg-orange-500" />}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">{savedCard.card_title}</p>
                <p className="text-xs text-gray-400">Привязанная карта</p>
              </div>
            </button>
          )}
        </div>

        {/* Тогл сохранения карты только при оплате новой картой */}
        {paymentType === 'card' && user && (
          <button
            onClick={() => setSaveCard((prev) => !prev)}
            className="w-full flex items-center justify-between p-3 rounded-xl border
              border-gray-100 hover:border-gray-200 transition-colors cursor-pointer"
          >
            <span className="text-sm text-gray-600">Сохранить карту для быстрой оплаты</span>
            <div
              className={`w-10 h-6 rounded-full transition-colors flex items-center px-1
              ${saveCard ? 'bg-orange-500' : 'bg-gray-200'}`}
            >
              <div
                className={`w-4 h-4 rounded-full bg-white shadow transition-transform
                ${saveCard ? 'translate-x-4' : 'translate-x-0'}`}
              />
            </div>
          </button>
        )}

        {!user && (
          <p className="text-xs text-gray-400 px-1">Войдите в аккаунт чтобы сохранить карту</p>
        )}
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

      {/* Виджет оплаты */}
      {showWidget && (
        <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden">
          <div id="payment-widget" />
        </div>
      )}

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

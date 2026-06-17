import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function PaymentSuccessPage() {
  const navigate = useNavigate();

  return (
    <section
      className="mx-auto max-w-lg p-6 flex flex-col items-center justify-center min-h-[60vh]
        text-center space-y-4"
    >
      <div className="text-6xl">🍕</div>
      <h1 className="text-2xl font-black text-gray-800">Заказ оплачен!</h1>
      <p className="text-sm text-gray-400">
        Мы уже готовим вашу пиццу. Следить за статусом можно в личном кабинете.
      </p>
      <button
        onClick={() => navigate('/profile')}
        className="h-11 px-6 bg-orange-500 hover:bg-orange-600 text-white font-bold text-sm
          rounded-xl transition-colors cursor-pointer"
      >
        Перейти в профиль
      </button>
      <button
        onClick={() => navigate('/')}
        className="h-11 px-6 border border-gray-200 hover:border-orange-300 text-gray-600
          hover:text-orange-500 text-sm font-medium rounded-xl transition-colors cursor-pointer"
      >
        Вернуться в меню
      </button>
    </section>
  );
}

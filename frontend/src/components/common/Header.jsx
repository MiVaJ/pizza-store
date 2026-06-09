import React from 'react';
import { useCartStore } from '@/store';
import { CartSheet } from '@/components';
import AnimatedNumber from './AnimatedNumber';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const totalQuantity = useCartStore((state) => state.totalQuantity);
  const totalPrice = useCartStore((state) => state.totalPrice);
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/80 p-4 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        {/* Логотип пиццерии */}
        <div onClick={() => navigate('/')} className="flex items-center gap-2 cursor-pointer">
          <span className="text-3xl">🍕</span>
          <span className="text-2xl font-black tracking-tight text-gray-800">
            Пицца<span className="text-orange-500">ТуТ</span>
          </span>
        </div>

        {/* Кнопка корзины */}
        <CartSheet>
          <button
            className="group relative flex h-11 w-36 items-center justify-center overflow-hidden
              rounded-full bg-orange-500 px-4 font-bold text-white shadow-sm transition-all
              duration-300 hover:bg-orange-600 active:scale-95 md:w-40 md:text-base text-sm
              cursor-pointer select-none"
          >
            {/* Отображаем общую стоимость, если пользвоатель добавил пиццу в корзину */}

            <div className="relative h-5 w-20 overflow-hidden">
              <span
                className={`absolute inset-0 flex items-center justify-center transition-all
                  duration-300 ease-in-out ${
                    totalQuantity === 0
                      ? 'translate-y-0 opacity-100'
                      : '-translate-y-full opacity-0'
                  }`}
              >
                Корзина
              </span>

              <div
                className={`absolute inset-0 flex items-center justify-center transition-all
                  duration-300 ease-in-out tracking-tight ${
                    totalQuantity === 0 ? 'translate-y-full opacity-0' : 'translate-y-0 opacity-100'
                  }`}
              >
                <AnimatedNumber value={totalPrice} />
              </div>
            </div>
          </button>
        </CartSheet>
      </div>
    </header>
  );
}

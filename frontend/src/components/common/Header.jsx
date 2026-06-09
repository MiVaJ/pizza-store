import React from 'react';
import { useCartStore } from '@/store';
import { CartSheet } from '@/components';
import AnimatedNumber from './AnimatedNumber';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';

export default function Header() {
  const totalQuantity = useCartStore((state) => state.totalQuantity);
  const totalPrice = useCartStore((state) => state.totalPrice);
  const { user, isAuth } = useAuthStore();
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
        {/* Правый блок: Профиль, Корзина */}
        <div className="flex items-center gap-3">
          {/* Кнопка профиля или входа */}
          {isAuth ? (
            <button
              onClick={() => navigate('/profile')}
              className="flex items-center gap-2 h-11 px-4 rounded-full border border-gray-200
                bg-white hover:border-orange-300 hover:bg-orange-50 transition-colors cursor-pointer
                select-none"
            >
              <div
                className="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center
                  text-orange-600 text-xs font-bold flex-shrink-0"
              >
                {user?.name?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase()}
              </div>
              <span
                className="text-sm font-medium text-gray-700 max-w-[80px] truncate hidden sm:block"
              >
                {user?.name ?? user?.email}
              </span>
            </button>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="h-11 px-4 rounded-full border border-gray-200 bg-white text-sm font-medium
                text-gray-600 hover:border-orange-300 hover:text-orange-500 transition-colors
                cursor-pointer select-none"
            >
              Войти
            </button>
          )}

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
                      totalQuantity === 0
                        ? 'translate-y-full opacity-0'
                        : 'translate-y-0 opacity-100'
                    }`}
                >
                  <AnimatedNumber value={totalPrice} />
                </div>
              </div>
            </button>
          </CartSheet>
        </div>
      </div>
    </header>
  );
}

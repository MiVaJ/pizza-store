import React from 'react';
import { useCartStore } from '@/store/useCartStore';

export default function Header() {
  const totalQuantity = useCartStore((state) => state.getTotalQuantity());

  return (
    <header className="sticky top-0 z-50 border-b border-gray-100 bg-white/80 p-4 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between">
        {/* Логотип пиццерии */}
        <div className="flex items-center gap-2">
          <span className="text-3xl">🍕</span>
          <span className="text-2xl font-black tracking-tight text-gray-800">
            Пицца<span className="text-orange-500">ТуТ</span>
          </span>
        </div>

        {/* Кнопка корзины */}
        <button
          className="flex items-center gap-2 rounded-full bg-orange-500 px-5 py-2.5 font-bold
            text-white transition hover:bg-orange-600 shadow-sm"
        >
          <span>Корзина</span>
          {/* ОТображаем цифру, только если в корзине что-то есть */}
          {totalQuantity > 0 && (
            <span className="rounded-full bg-white px-2 py-0.5 text-xs font-black text-orange-500">
              {totalQuantity}
            </span>
          )}
        </button>
      </div>
    </header>
  );
}

import React from 'react';

export default function Header() {
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
          <span className="rounded-full bg-white/20 px-2 py-0.5 text-sm">0</span>
        </button>
      </div>
    </header>
  );
}

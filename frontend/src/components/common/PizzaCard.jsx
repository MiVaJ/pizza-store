import React, { useState } from 'react';

export default function PizzaCard({ pizza }) {
  const [count, setCount] = useState(0);

  return (
    <div
      className="group flex flex-col justify-between overflow-hidden rounded-2xl border
        border-gray-100 bg-white shadow-sm transition-all duration-300 hover:shadow-md"
    >
      {/* Верхний блок: Картинка и Описание*/}
      <div
        className="relative flex h-48 w-full items-center justify-center overflow-hidden
          bg-transparent"
      >
        {/* Картинка */}
        {pizza.image_url && (
          <img
            src={pizza.image_url}
            alt={pizza.name}
            className="h-full w-auto object-contain p-2 transition-all duration-300
              group-hover:opacity-40 group-hover:blur-[3px]"
          />
        )}

        {/* Адаптивная панель описания */}
        {pizza.description && (
          <div
            className="absolute inset-x-0 bottom-0 flex hidden h-auto max-h-[85%] translate-y-[105%]
              flex-col justify-end rounded-t-2xl border-t border-gray-100/50 bg-white/90 p-4
              backdrop-blur-sm transition-transform duration-300 ease-out group-hover:translate-y-0
              md:flex"
          >
            <p className="mb-1 text-[10px] font-bold tracking-wider text-gray-400 uppercase">
              Описание:
            </p>
            <p className="overflow-y-auto pr-1 text-xs leading-relaxed font-medium text-gray-700">
              {pizza.description}
            </p>
          </div>
        )}
      </div>

      {/* Нижний блок: Название, Стоимость и Кнопка */}
      <div className="flex flex-grow flex-col justify-between p-4 pt-0">
        {/* Название*/}
        <h3
          className="mt-2 line-clamp-1 text-lg font-bold tracking-tight text-gray-800
            transition-colors group-hover:text-orange-600"
        >
          {pizza.name}
        </h3>

        {/* Блок цены и кнопки */}
        <div className="mt-4 flex items-center justify-between">
          {/* Цена */}
          <span className="text-xl font-black text-gray-900">{pizza.price} ₽</span>

          {/* Кнопка */}
          {count === 0 ? (
            // Кнопка с текстом
            <button
              onClick={() => setCount(1)}
              className="inline-flex h-9 w-28 items-center justify-center rounded-full bg-secondary
                px-2 py-2 text-xs font-bold text-secondary-foreground shadow-sm transition-colors
                hover:bg-orange-500 hover:text-white active:scale-95 duration-200 cursor-pointer"
            >
              + В корзину
            </button>
          ) : (
            // Кнопка с отображением счётчика
            <div
              className="flex h-9 w-28 items-center justify-between rounded-full bg-orange-500 p-1
                text-white shadow-sm select-none"
            >
              <button
                onClick={() => setCount(count - 1)}
                className="flex h-7 w-7 items-center justify-center rounded-full text-base font-bold
                  transition hover:bg-orange-600 active:scale-90 cursor-pointer"
              >
                -
              </button>
              <span className="text-xs font-bold">{count}</span>
              <button
                onClick={() => setCount(count + 1)}
                className="flex h-7 w-7 items-center justify-center rounded-full text-base font-bold
                  transition hover:bg-orange-600 active:scale-90 cursor-pointer"
              >
                +
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

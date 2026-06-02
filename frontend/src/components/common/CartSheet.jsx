import React, { useRef, useState } from 'react';
import { useCartStore } from '@/store';
import NumberFlow from '@number-flow/react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetTrigger,
} from '@/components/ui/sheet';

function SauceCard({ sauce, onAdd }) {
  // Флаг: сломалась Картинка или нет.
  const [isImageBroken, setIsImageBroken] = useState(false);

  // Создаём уникальный ID, чтобы соусы не конфликтовали с ID пицц
  const uniqueId = `sauce-${sauce.id}`;

  return (
    <div
      className="w-28 flex-shrink-0 border border-gray-100 bg-gray-50/50 p-3 rounded-xl flex
        flex-col items-center justify-between text-center hover:border-orange-200 transition-colors"
    >
      {/* Картинка соуса */}
      <div
        className="h-12 w-12 flex items-center justify-center rounded-lg shadow-sm bg-white
          overflow-hidden"
      >
        {sauce.image_url && !isImageBroken ? (
          <img
            src={sauce.image_url}
            alt={sauce.name}
            className="h-full w-full object-cover"
            // В случае ошибки, состояние изменится автоматически
            onError={() => setIsImageBroken(true)}
          />
        ) : (
          // Вывод иконки, если произошла ошибка загрузки картинки
          <span className="text-2xl">🥫</span>
        )}
      </div>

      <h5 className="text-[10px] font-bold text-gray-700 mt-2 line-clamp-2 h-7 leading-tight">
        {sauce.name}
      </h5>

      {/* Кнопка добавления соуса в корзину */}
      <button
        onClick={() => onAdd({ ...sauce, id: uniqueId })}
        className="mt-2.5 w-full h-6 bg-white border border-orange-200 hover:bg-orange-500
          hover:text-white text-[10px] font-black text-orange-600 rounded-lg transition-all
          active:scale-95 cursor-pointer shadow-sm"
      >
        +{sauce.price} ₽
      </button>
    </div>
  );
}

// children — это кнопка из Header, которая обёрнута в CartSheet
export default function CartSheet({ children }) {
  const items = useCartStore((state) => state.items);
  const totalQuantity = useCartStore((state) => state.totalQuantity);
  const totalPrice = useCartStore((state) => state.totalPrice);
  const addItem = useCartStore((state) => state.addItem);
  const removeItem = useCartStore((state) => state.removeItem);

  // Создаём ссылку на блок соусов, чтобы управлять его прокруткой
  const sauceScrollRef = useRef(null);

  // Функция, которая переводит вертикальный скролл мыши в горизонтальное движение соусов
  const handleWheel = (e) => {
    if (sauceScrollRef.current) {
      e.preventDefault();

      sauceScrollRef.current.scrollTo({
        left: sauceScrollRef.current.scrollLeft + e.deltaY * 1.2,
        behavior: 'smooth',
      });
    }
  };

  // Получаем все ингредиенты, которые прикреплены к текущим пиццам в корзине
  const allIngredients = items.flatMap((item) => item.ingredients || []);

  // Получаем только соусы из всех ингредиентов
  const rawSauces = allIngredients.filter((ing) => ing.is_sauce === true);

  // Оставляем только уникальные значения соусов
  const dynamicSauces = Array.from(
    new Map(rawSauces.map((sauce) => [sauce.id, sauce.id])).values(),
  ).map((id) => rawSauces.find((sauce) => sauce.id === id));

  return (
    <Sheet>
      {/* Открывает шторку при клике на кнопку (вешается onClick) */}
      <SheetTrigger asChild>{children}</SheetTrigger>

      {/* Шторка */}
      <SheetContent
        side="right"
        className="w-full sm:!max-w-[460px] flex flex-col justify-between p-6 bg-white border-l
          border-gray-100"
      >
        {/* Верхний блок: Шапка шторки */}
        <SheetHeader className="border-b border-gray-100 pb-4">
          <SheetTitle className="text-xl font-black text-gray-900 flex items-center gap-2">
            Корзина{' '}
            {totalQuantity > 0 && (
              <span className="text-sm font-medium text-gray-400">({totalQuantity})</span>
            )}
          </SheetTitle>

          {/* Описание для программ чтения с экрана */}
          <SheetDescription className="sr-only">
            Список выбранных пицц и форма оформления заказа.
          </SheetDescription>
        </SheetHeader>

        {/* Средний блок: Список пицц или экран пустой корзины */}
        <div className="flex-grow overflow-y-auto !-mt-4 pt-4 pb-4 space-y-3 scrollbar-none">
          {items.length === 0 ? (
            //Если пиццы нет, то показываем, что корзина пуста
            <div
              className="flex h-full flex-col items-center justify-center text-center
                animate-fade-in"
            >
              <p className="text-5xl mb-3 select-none">🍕</p>
              <h4 className="text-base font-bold text-gray-800">В корзине пусто</h4>
              <p className="mt-1 text-xs text-gray-400 max-w-[200px] leading-relaxed">
                Добавьте пиццу из меню, чтобы оформить доставку
              </p>
            </div>
          ) : (
            // Если пицца есть, то отображаем её циклом .map()
            <div className="space-y-3">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-4 bg-gray-50/80 p-3 rounded-xl
                    border border-gray-100/60 animate-fade-in"
                >
                  {/* Мини-картинка (на маленьких дисплеях скрывается) */}
                  <div
                    className="h-16 w-16 flex-shrink-0 items-center justify-center rounded-xl
                      bg-white border border-gray-100 p-1 hidden sm:flex shadow-sm"
                  >
                    {item.image_url && (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        className="h-full w-full object-contain rounded-lg"
                      />
                    )}
                  </div>

                  {/* Текстовый блок: Название и цена за штуку */}
                  <div className="flex-grow">
                    <h4 className="text-sm font-bold text-gray-800 line-clamp-1">{item.name}</h4>
                    <p className="text-sm font-extrabold text-gray-400 mt-0.5">{item.price} ₽</p>
                  </div>

                  {/* Кнопочный блок управления количеством товара */}
                  <div
                    className="flex items-center gap-3 bg-orange-500 rounded-full p-1 h-9
                      select-none shadow-md shadow-orange-500/10"
                  >
                    <button
                      onClick={() => removeItem(item.id)}
                      className="flex h-7 w-7 items-center justify-center rounded-full text-base
                        font-black text-white hover:bg-orange-600 transition-all active:scale-90
                        cursor-pointer"
                    >
                      -
                    </button>
                    <span className="text-sm font-black text-white w-4 text-center">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => addItem(item)}
                      className="flex h-7 w-7 items-center justify-center rounded-full text-base
                        font-black text-white hover:bg-orange-600 transition-all active:scale-90
                        cursor-pointer"
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Нижний блок: Карусель соусов, Итоговый чек и Кнопка */}
        {items.length > 0 && (
          <div className="border-t border-gray-100 pt-4 space-y-5 bg-white">
            {/* Блок соусов */}
            {dynamicSauces.length > 0 && (
              // Отображаем соусы, если они доступны для добавленных пицц
              <div className="space-y-2">
                <p className="text-[10px] font-black uppercase tracking-wider text-gray-400">
                  Добавить к заказу?
                </p>

                <div
                  ref={sauceScrollRef}
                  onWheel={handleWheel}
                  className="flex gap-3 overflow-x-auto pb-1 scrollbar-none scroll-smooth
                    select-none"
                >
                  {/* Вызываем компонент отображения соусов */}
                  {dynamicSauces.map((sauce) => (
                    <SauceCard key={sauce.id} sauce={sauce} onAdd={addItem} />
                  ))}
                </div>
              </div>
            )}

            {/* Итоговый чек */}
            <div className="space-y-4 border-t border-gray-50 pt-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-400">Итого к оплате:</span>
                <div
                  className="flex items-center text-xl font-black text-gray-900 tabular-nums
                    tracking-tight"
                >
                  <NumberFlow value={totalPrice} />
                  <span className="ml-0.5">₽</span>
                </div>
              </div>

              <button
                className="w-full h-12 bg-orange-500 hover:bg-orange-600 text-white font-bold
                  text-sm rounded-xl shadow-sm transition-colors active:scale-[0.99] duration-150
                  cursor-pointer"
              >
                Перейти к оформлению
              </button>
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

import React from 'react';
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

// children — это кнопка из Header, которая обёрнута в CartSheet
export default function CartSheet({ children }) {
  const items = useCartStore((state) => state.items);
  const totalQuantity = useCartStore((state) => state.totalQuantity);
  const totalPrice = useCartStore((state) => state.totalPrice);
  const addItem = useCartStore((state) => state.addItem);
  const removeItem = useCartStore((state) => state.removeItem);

  return (
    <Sheet>
      {/* Открывает шторку при клике на кнопку (вешается onClick) */}
      <SheetTrigger asChild>{children}</SheetTrigger>

      {/* Шторка */}
      <SheetContent
        side="right"
        className="w-full sm:max-w-md flex flex-col justify-between p-6 bg-white border-l
          border-gray-100"
      >
        {/* Верхний блок: Шапка шторки */}
        <SheetHeader className="border-b border-gray-50 pb-4">
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
        <div className="flex-grow overflow-y-auto py-4">
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
            <div className="space-y-4">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-4 border-b border-gray-50 pb-4
                    animate-fade-in"
                >
                  {/* Мини-картинка (на маленьких дисплеях скрывается) */}
                  <div
                    className="h-16 w-16 flex-shrink-0 items-center justify-center rounded-xl
                      bg-gray-50 p-1 hidden sm:flex"
                  >
                    {item.image_url && (
                      <img
                        src={item.image_url}
                        alt={item.name}
                        className="h-full w-full object-contain"
                      />
                    )}
                  </div>

                  {/* Текстовый блок: Название и цена за штуку */}
                  <div className="flex-grow">
                    <h4 className="text-sm font-bold text-gray-800 line-clamp-1">{item.name}</h4>
                    <p className="text-xs text-gray-400 font-medium mt-0.5">{item.price} ₽</p>
                  </div>

                  {/* Кнопочный блок управления количеством товара */}
                  <div
                    className="flex items-center gap-2.5 bg-gray-50 border border-gray-100
                      rounded-full p-1 h-8 select-none"
                  >
                    <button
                      onClick={() => removeItem(item.id)}
                      className="flex h-6 w-6 items-center justify-center rounded-full text-sm
                        font-bold text-gray-500 hover:bg-gray-200 transition-colors cursor-pointer"
                    >
                      -
                    </button>
                    <span className="text-xs font-black text-gray-800 w-3 text-center">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => addItem(item)}
                      className="flex h-6 w-6 items-center justify-center rounded-full text-sm
                        font-bold text-gray-500 hover:bg-gray-200 transition-colors cursor-pointer"
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Нижний блок: Итоговый чек и кнопка (отображаются только если есть товары) */}
        {items.length > 0 && (
          <div className="border-t border-gray-50 pt-4 space-y-4">
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
              className="w-full h-12 bg-orange-500 hover:bg-orange-600 text-white font-bold text-sm
                rounded-xl shadow-sm transition-colors active:scale-[0.99] duration-150
                cursor-pointer"
            >
              Перейти к оформлению
            </button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

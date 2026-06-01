import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Рассчитываем итоги
const calculateTotals = (items) => {
  const totalQuantity = items.reduce((total, item) => total + item.quantity, 0);
  const totalPrice = items.reduce((total, item) => total + item.price * item.quantity, 0);
  return { totalQuantity, totalPrice };
};

export const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],
      totalQuantity: 0, // Итоговое количество
      totalPrice: 0, // Итоговая стоимость

      // Функция добавления пиццы или увеличения её количества
      addItem: (pizza) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((item) => item.id === pizza.id);
        let newItems;

        if (existingItem) {
          newItems = currentItems.map((item) =>
            item.id === pizza.id ? { ...item, quantity: item.quantity + 1 } : item,
          );
        } else {
          newItems = [...currentItems, { ...pizza, quantity: 1 }];
        }

        // Рассчитываем итоговые значения после изменения состояния
        const { totalQuantity, totalPrice } = calculateTotals(newItems);

        set({ items: newItems, totalQuantity, totalPrice });
      },

      // Функция уменьшения количества или удаления пиццы, если количество стало 0
      removeItem: (pizzaId) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((item) => item.id === pizzaId);

        if (!existingItem) return;
        let newItems;

        if (existingItem.quantity === 1) {
          // Если была всего 1 пицца, полностью удаляем её из массива
          newItems = currentItems.filter((item) => item.id !== pizzaId);
        } else {
          // Если пицц больше, уменьшаем количество на 1
          newItems = currentItems.map((item) =>
            item.id === pizzaId ? { ...item, quantity: item.quantity - 1 } : item,
          );
        }

        // Вызываем функцию для рассчёта итоговых сумм
        const { totalQuantity, totalPrice } = calculateTotals(newItems);
        set({ items: newItems, totalQuantity, totalPrice });
      },

      // Функция для получения количества конкретной пиццы по её id
      getItemQuantity: (pizzaId) => {
        const item = get().items.find((item) => item.id === pizzaId);
        return item ? item.quantity : 0;
      },
    }),
    {
      // Уникальное имя ключа в localStorage браузера
      name: 'pizza-cart-storage',
    },
  ),
);

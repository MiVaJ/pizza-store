import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useCartStore = create(
  persist(
    (set, get) => ({
      items: [],

      // Функция добавления пиццы или увеличения её количества
      addItem: (pizza) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((item) => item.id === pizza.id);

        if (existingItem) {
          // Если пицца уже в корзине, увеличиваем её количество на 1
          set({
            items: currentItems.map((item) =>
              item.id === pizza.id ? { ...item, quantity: item.quantity + 1 } : item,
            ),
          });
        } else {
          // Если пиццы нет, добавляем её как новый объект с количеством 1
          set({ items: [...currentItems, { ...pizza, quantity: 1 }] });
        }
      },

      // Функция уменьшения количества или удаления пиццы, если количество стало 0
      removeItem: (pizzaId) => {
        const currentItems = get().items;
        const existingItem = currentItems.find((item) => item.id === pizzaId);

        if (!existingItem) return;

        if (existingItem.quantity === 1) {
          // Если была всего 1 пицца, полностью удаляем её из массива
          set({ items: currentItems.filter((item) => item.id !== pizzaId) });
        } else {
          // Если пицц больше, уменьшаем количество на 1
          set({
            items: currentItems.map((item) =>
              item.id === pizzaId ? { ...item, quantity: item.quantity - 1 } : item,
            ),
          });
        }
      },

      // Считаем общее количество ВСЕХ пицц в корзине
      getTotalQuantity: () => {
        return get().items.reduce((total, item) => total + item.quantity, 0);
      },

      // Считаем общую стоимость ВСЕХ пицц в корзине
      getTotalPrice: () => {
        return get().items.reduce((total, item) => total + item.price * item.quantity, 0);
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

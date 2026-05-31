import React, { useEffect, useState } from 'react';
import api from '@/core/api';
import PizzaCard from '@/components/common/PizzaCard';

export default function MenuSection() {
  const [pizzas, setPizzas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMenu = async () => {
      try {
        const response = await api.get('/api/menu/');
        setPizzas(response.data);
      } catch (error) {
        console.error('Ошибка при загрузке меню пиццы:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMenu();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <p className="animate-bounce text-3xl">🍕</p>
          <p className="mt-2 text-sm font-medium text-gray-400">Готовим свежее меню...</p>
        </div>
      </div>
    );
  }

  return (
    <section className="mx-auto max-w-7xl p-6">
      <h2 className="mb-8 text-2xl font-black tracking-tight text-gray-800">
        Свежие и горячие пиццы
      </h2>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-4">
        {pizzas.map((pizza) => (
          <PizzaCard key={pizza.id} pizza={pizza} />
        ))}
      </div>
    </section>
  );
}

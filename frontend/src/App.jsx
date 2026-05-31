import React from 'react';
import { NoticeBanner, Header, MenuSection } from '@/components';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50/50">
      {/* 1. Плашка-предупреждение на самом верху */}
      <NoticeBanner />

      {/* 2. Шапка сайта с корзиной */}
      <Header />

      {/* 3. Секция меню */}
      <main>
        <MenuSection />
      </main>
    </div>
  );
}

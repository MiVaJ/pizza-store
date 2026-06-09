import React from 'react';
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom';
import { NoticeBanner, Header } from '@/components';
import MenuPage from '@/pages/MenuPage';
import LoginPage from '@/pages/LoginPage';

// Общая структура сайта
function Layout() {
  return (
    <div className="min-h-screen bg-gray-50/50 flex flex-col">
      {/* Плашка-предупреждение на самом верху */}
      <NoticeBanner />

      {/* Шапка сайта с корзиной */}
      <Header />

      {/* Местодля подключения нужной страницы */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}

// Конфигурация маршрутов
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />, // Главный каркас сайта
    children: [
      {
        path: '/',
        element: <MenuPage />, // Главная страница: секция меню пицц
      },
      {
        path: '/login',
        element: <LoginPage />, // Страница авторизации
      },
    ],
  },
]);

// Функция запуска сайта
export default function App() {
  return <RouterProvider router={router} />;
}

import React from 'react';
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom';
import { NoticeBanner, Header, ProtectedRoute } from '@/components';
import MenuPage from '@/pages/MenuPage';
import LoginPage from '@/pages/LoginPage';
import ProfilePage from '@/pages/ProfilePage';
import CheckoutPage from '@/pages/CheckoutPage';
import RegisterPage from '@/pages/RegisterPage';
import ManagerOrdersPage from '@/pages/ManagerOrdersPage';
import PaymentSuccessPage from '@/pages/PaymentSuccessPage';
import AdminPage from '@/pages/AdminPage';

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
      {
        path: '/profile',
        element: (
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        ), //Страница профиля
      },
      {
        path: '/checkout',
        element: <CheckoutPage />, // Страница оформления заказа
      },
      {
        path: '/register',
        element: <RegisterPage />, //Страница регистрации
      },
      {
        path: '/manager/orders',
        element: (
          <ProtectedRoute allowedRoles={['manager', 'admin']}>
            <ManagerOrdersPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/payment/success',
        element: <PaymentSuccessPage />, // Страница успешной оплаты заказа
      },
      {
        path: '/admin',
        element: (
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminPage />
          </ProtectedRoute>
        ), // Админ панель
      },
    ],
  },
]);

// Функция запуска сайта
export default function App() {
  return <RouterProvider router={router} />;
}

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/useAuthStore';

export default function ProtectedRoute({ allowedRoles, children }) {
  const { user, isAuth, isLoading } = useAuthStore();

  if (isLoading) {
    return <p className="p-6 text-gray-400 text-sm">Загрузка...</p>;
  }

  if (!isAuth) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/" replace />;
  }

  return children;
}

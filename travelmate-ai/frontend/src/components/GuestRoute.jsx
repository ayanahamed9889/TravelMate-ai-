import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Loader from './ui/Loader';

// Login / Register are only for logged-out visitors
export default function GuestRoute() {
  const { user, loading } = useAuth();
  if (loading) return <Loader />;
  return user ? <Navigate to="/dashboard" replace /> : <Outlet />;
}

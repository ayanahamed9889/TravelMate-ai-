import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Loader from './ui/Loader';

export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <Loader text="Authenticating..." />;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
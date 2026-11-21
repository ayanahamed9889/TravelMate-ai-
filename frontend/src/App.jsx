import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/ProtectedRoute';
import GuestRoute from './components/GuestRoute';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import MyTrips from './pages/MyTrips';
import TripWizard from './pages/TripWizard';
import TripDetail from './pages/TripDetail';
import Explorer from './pages/Explorer';
import HotelsSearch from './pages/HotelsSearch';
import FlightsSearch from './pages/FlightsSearch';
import Assistant from './pages/Assistant';
import SavedPlaces from './pages/SavedPlaces';
import Settings from './pages/Settings';
import Budget from './pages/Budget';

function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { pathname } = useLocation();

  // close the mobile menu and jump to top whenever the page changes
  useEffect(() => {
    setMenuOpen(false);
    window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className="min-h-screen bg-surface">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="lg:ml-64 min-h-screen flex flex-col">
        <Navbar onMenu={() => setMenuOpen(true)} />
        <main className="flex-1 w-full min-w-0"><Outlet /></main>
        <Footer />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route element={<GuestRoute />}>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Route>
            <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/trips" element={<MyTrips />} />
              <Route path="/trips/:id" element={<TripDetail />} />
              <Route path="/planner" element={<TripWizard />} />
              <Route path="/explore" element={<Explorer />} />
              <Route path="/hotels" element={<HotelsSearch />} />
              <Route path="/flights" element={<FlightsSearch />} />
              <Route path="/assistant" element={<Assistant />} />
              <Route path="/saved" element={<SavedPlaces />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/budget" element={<Budget />} />
            </Route>
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

import { NavLink, Route, Routes } from 'react-router-dom';
import BookingFlow from './components/BookingFlow';
import CalendarView from './components/CalendarView';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-10 border-b bg-white/90 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <span className="font-bold">YPlaces Clone</span>
          <nav className="flex gap-3 text-sm">
            <NavLink className={({ isActive }) => (isActive ? 'font-semibold text-brand-600' : 'text-slate-500')} to="/">
              Client
            </NavLink>
            <NavLink className={({ isActive }) => (isActive ? 'font-semibold text-brand-600' : 'text-slate-500')} to="/admin">
              Admin
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-3xl">
        <Routes>
          <Route path="/" element={<BookingFlow />} />
          <Route path="/admin" element={<CalendarView />} />
        </Routes>
      </main>
    </div>
  );
}

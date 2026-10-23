export default function Footer() {
  return (
    <footer className="border-t border-slate-200 px-4 sm:px-8 py-4 text-center text-xs text-slate-400">
      © {new Date().getFullYear()} TravelMate AI. Prices and itineraries are estimates — verify before booking.
    </footer>
  );
}

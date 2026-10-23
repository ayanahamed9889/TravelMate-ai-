import { useEffect, useState } from 'react';
import ChatWindow from '../components/ChatWindow';
import api from '../api/axios';

export default function Assistant() {
  const [trips, setTrips] = useState([]);
  const [tripId, setTripId] = useState('');

  useEffect(() => { api.get('/trips').then((r) => setTrips(r.data.items || [])).catch(() => {}); }, []);

  return (
    <div className="page max-w-[900px]">
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mb-2">AI Assistant</h1>
      <p className="text-sm text-slate-500 mb-4">Ask anything about your trips, hotels, or destinations.</p>
      {trips.length > 0 && (
        <div className="mb-4 max-w-sm">
          <label className="label" htmlFor="chat-trip">Chat about</label>
          <select id="chat-trip" className="field" value={tripId} onChange={(e) => setTripId(e.target.value)}>
            <option value="">General travel questions</option>
            {trips.map((t) => <option key={t.id} value={t.id} className="capitalize">{t.destination}{t.start_date ? ` (${t.start_date})` : ''}</option>)}
          </select>
        </div>
      )}
      <ChatWindow key={tripId} tripId={tripId ? Number(tripId) : null} />
    </div>
  );
}

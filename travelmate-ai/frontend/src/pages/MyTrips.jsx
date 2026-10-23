import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import TripCard from '../components/TripCard';
import Loader from '../components/ui/Loader';
import Modal from '../components/ui/Modal';
import Button from '../components/ui/Button';
import { useToast } from '../context/ToastContext';
import { getErrorMessage } from '../utils/errors';

const FILTERS = [['active', 'Active'], ['past', 'Past'], ['drafts', 'Drafts'], ['all', 'All']];

export default function MyTrips() {
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [trips, setTrips] = useState([]);
  const [filter, setFilter] = useState('active');
  const [toDelete, setToDelete] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const load = useCallback(() => {
    setLoading(true); setError('');
    api.get('/trips', { params: { status: filter } })
      .then((r) => setTrips(r.data.items || []))
      .catch((err) => { setTrips([]); setError(getErrorMessage(err, 'Could not load your trips.')); })
      .finally(() => setLoading(false));
  }, [filter]);
  useEffect(load, [load]);

  const confirmDelete = async () => {
    setDeleting(true);
    try {
      await api.delete(`/trips/${toDelete.id}`);
      addToast('Trip deleted');
      setToDelete(null);
      load();
    } catch (err) { addToast(getErrorMessage(err, 'Could not delete the trip'), 'error'); }
    finally { setDeleting(false); }
  };

  return (
    <div className="page">
      <div className="flex justify-between items-center mb-6 gap-3">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">My Trips</h1>
        <Button variant="primary" onClick={() => navigate('/planner')}>+ New Trip</Button>
      </div>
      <div className="flex flex-wrap gap-2 mb-6">
        {FILTERS.map(([key, label]) => (
          <button key={key} onClick={() => setFilter(key)} className={`chip ${filter === key ? 'chip-active' : 'chip-light'}`}>{label}</button>
        ))}
      </div>

      {loading ? <Loader /> : error ? (
        <div className="glass-panel p-8 text-center"><p className="text-red-600 mb-3">{error}</p><Button variant="secondary" onClick={load}>Retry</Button></div>
      ) : trips.length === 0 ? (
        <div className="glass-panel p-10 text-center">
          <p className="text-slate-500 mb-3">No {filter === 'all' ? '' : filter + ' '}trips yet.</p>
          <button onClick={() => navigate('/planner')} className="btn-primary">Create a Trip</button>
        </div>
      ) : (
        <div className="space-y-4">{trips.map((t) => <TripCard key={t.id} trip={t} onDelete={setToDelete} />)}</div>
      )}

      <Modal open={!!toDelete} onClose={() => setToDelete(null)} title="Delete this trip?">
        <p className="text-sm text-slate-600 mb-5">
          “{toDelete?.destination}” and its itinerary and expenses will be permanently removed.
        </p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={() => setToDelete(null)}>Cancel</Button>
          <button onClick={confirmDelete} disabled={deleting} className="inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-sm font-semibold bg-red-600 text-white hover:bg-red-700 disabled:opacity-60">
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </Modal>
    </div>
  );
}

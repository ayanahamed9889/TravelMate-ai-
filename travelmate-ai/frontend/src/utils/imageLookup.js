import api from '../api/axios';

// Photo lookups go through the backend (/images). Results are cached for the whole session and
// at most 4 requests run at once, so a page with 30 cards doesn't hammer the server.
const cache = new Map();
const queue = [];
let active = 0;
const LIMIT = 4;

function pump() {
  while (active < LIMIT && queue.length) {
    const job = queue.shift();
    active += 1;
    job().finally(() => { active -= 1; pump(); });
  }
}

const schedule = (fn) => new Promise((resolve) => {
  queue.push(() => fn().then(resolve, () => resolve(null)));
  pump();
});

export function lookupImage({ q, kind = 'place', exclude = '', city = '' }) {
  if (!q || q.trim().length < 2) return Promise.resolve(null);
  const key = [kind, q, exclude, city].join('|').toLowerCase();
  if (!cache.has(key)) {
    const p = schedule(() => api.get('/images', { params: { q, kind, exclude: exclude || undefined, city: city || undefined } }).then((r) => r.data));
    cache.set(key, p);
    // don't remember failures/misses forever - a retry later may work
    p.then((res) => { if (!res || !res.url) cache.delete(key); });
  }
  return cache.get(key);
}

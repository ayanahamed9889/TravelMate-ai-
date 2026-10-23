import { useEffect, useState } from 'react';
import { lookupImage } from '../utils/imageLookup';

// useImage({ q: 'Hawa Mahal', kind: 'place', exclude: 'Jaipur' }) -> { url, generic, credit, loading }
export function useImage(lookup, enabled = true) {
  const q = lookup?.q || '';
  const kind = lookup?.kind || 'place';
  const exclude = lookup?.exclude || '';
  const city = lookup?.city || '';
  const [state, setState] = useState({ url: null, generic: false, credit: '', loading: !!q && enabled });

  useEffect(() => {
    if (!enabled || !q) { setState({ url: null, generic: false, credit: '', loading: false }); return undefined; }
    let cancelled = false;
    setState((s) => ({ ...s, loading: true }));
    lookupImage({ q, kind, exclude, city }).then((r) => {
      if (!cancelled) setState({ url: r?.url || null, generic: !!r?.generic, credit: r?.credit || '', loading: false });
    });
    return () => { cancelled = true; };
  }, [q, kind, exclude, city, enabled]);

  return state;
}

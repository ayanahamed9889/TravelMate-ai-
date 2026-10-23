import { useEffect, useRef, useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import api from '../api/axios';
import { getErrorMessage } from '../utils/errors';

const GREETING = { role: 'ai', content: 'Hi! I am your AI travel assistant. Ask me about destinations, budgets, the best time to visit, or what to pack.' };
const SUGGESTIONS = ['Best time to visit Bali?', 'Plan a 5-day budget trip to Bangkok', 'Do Indians need a visa for Japan?'];

export default function ChatWindow({ tripId = null }) {
  const [messages, setMessages] = useState([GREETING]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [demo, setDemo] = useState(false);
  const bottom = useRef(null);

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, loading]);

  const send = async (text = input) => {
    const message = text.trim();
    if (!message || loading) return;
    const history = messages.slice(1).map((m) => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }));
    setMessages((prev) => [...prev, { role: 'user', content: message }]);
    setInput('');
    setLoading(true);
    try {
      const res = await api.post('/assistant/chat', { message, trip_id: tripId, history }, { timeout: 90000 });
      setDemo(!!res.data.demo);
      setMessages((prev) => [...prev, { role: 'ai', content: res.data.reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'ai', error: true, content: getErrorMessage(err, 'Sorry, I could not respond. Please try again.') }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel flex flex-col h-[70vh] min-h-[420px]">
      <div className="p-4 border-b border-slate-100 flex items-center gap-2">
        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center"><Sparkles size={16} className="text-white" /></div>
        <div className="flex-1">
          <h3 className="font-bold text-sm text-slate-900">TravelMate AI Assistant</h3>
          <p className="text-[10px] text-emerald-600 font-bold">● Online</p>
        </div>
        {demo && <span className="text-[10px] font-bold bg-amber-50 text-amber-700 px-2 py-1 rounded-md">DEMO MODE</span>}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] sm:max-w-[80%] px-3.5 py-2.5 rounded-2xl text-sm whitespace-pre-wrap break-words ${
              m.role === 'user' ? 'bg-primary text-white rounded-br-none'
                : m.error ? 'bg-red-50 text-red-700 rounded-bl-none' : 'bg-slate-100 text-slate-700 rounded-bl-none'}`}>
              {m.content}
            </div>
          </div>
        ))}
        {messages.length === 1 && (
          <div className="flex flex-wrap gap-2 pt-2">
            {SUGGESTIONS.map((s) => <button key={s} onClick={() => send(s)} className="chip chip-light">{s}</button>)}
          </div>
        )}
        {loading && <p className="text-xs text-slate-400 animate-pulse">AI is thinking…</p>}
        <div ref={bottom} />
      </div>

      <form onSubmit={(e) => { e.preventDefault(); send(); }} className="p-3 border-t border-slate-100 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          maxLength={2000}
          aria-label="Message"
          placeholder="Ask about your trip..."
          className="field flex-1 !bg-slate-50"
        />
        <button type="submit" disabled={loading || !input.trim()} className="btn-primary px-3" aria-label="Send"><Send size={16} /></button>
      </form>
    </div>
  );
}

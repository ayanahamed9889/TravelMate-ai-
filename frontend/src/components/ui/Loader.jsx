export default function Loader({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center p-12" role="status">
      <div className="w-10 h-10 border-4 border-slate-200 border-t-secondary rounded-full animate-spin"></div>
      <p className="text-sm text-slate-500 mt-4">{text}</p>
    </div>
  );
}

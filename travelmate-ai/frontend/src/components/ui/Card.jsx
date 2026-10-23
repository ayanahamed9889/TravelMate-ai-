export default function Card({ children, className = '', ...props }) {
  return (
    <div {...props} className={`glass-panel p-5 ${className}`}>
      {children}
    </div>
  );
}
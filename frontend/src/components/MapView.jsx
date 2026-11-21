// Embeds a Google map centred on the destination (no API key needed).
export default function MapView({ destination, origin, height = 300 }) {
  if (!destination) return null;
  const query = origin ? `${origin} to ${destination}` : destination;
  const src = `https://maps.google.com/maps?q=${encodeURIComponent(query)}&output=embed`;
  return (
    <div className="rounded-xl overflow-hidden border border-slate-100">
      <iframe
        title={`Map of ${destination}`}
        width="100%"
        height={height}
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        style={{ border: 0 }}
        src={src}
        allowFullScreen
      />
    </div>
  );
}

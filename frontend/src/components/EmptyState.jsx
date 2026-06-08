// EmptyState.jsx — shown when a table or list has no data
export default function EmptyState({ title = 'No data found', subtitle = 'Try adjusting your search or filters.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <span className="text-5xl mb-4">📭</span>
      <p className="font-semibold text-slate-600">{title}</p>
      <p className="text-sm mt-1">{subtitle}</p>
    </div>
  );
}

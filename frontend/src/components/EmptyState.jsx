// EmptyState.jsx — shown when a table or list has no data
export default function EmptyState({ title = 'No data found', subtitle = 'Try adjusting your search or filters.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-slate-400">
      <svg xmlns="http://www.w3.org/2000/svg" className="w-12 h-12 mb-4 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
      <p className="font-semibold text-slate-600">{title}</p>
      <p className="text-sm mt-1">{subtitle}</p>
    </div>
  );
}

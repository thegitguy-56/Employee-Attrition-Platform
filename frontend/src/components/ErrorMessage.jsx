// ErrorMessage.jsx — shown when an API call fails
export default function ErrorMessage({ message = 'Something went wrong. Please try again.' }) {
  return (
    <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      <span className="text-xl">⚠️</span>
      <p className="text-sm">{message}</p>
    </div>
  );
}

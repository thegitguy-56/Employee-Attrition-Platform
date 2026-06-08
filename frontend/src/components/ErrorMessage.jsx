// ErrorMessage.jsx — shown when an API call fails
export default function ErrorMessage({ message = 'Something went wrong. Please try again.' }) {
  let displayMessage = '';

  if (Array.isArray(message)) {
    displayMessage = message.map(e => (typeof e === 'object' && e?.msg ? `${e.loc?.join('.') || 'error'}: ${e.msg}` : String(e))).join(', ');
  } else if (typeof message === 'object' && message !== null) {
    displayMessage = message.detail 
      ? (Array.isArray(message.detail) 
          ? message.detail.map(e => `${e.loc?.join('.') || 'error'}: ${e.msg}`).join(', ')
          : String(message.detail))
      : JSON.stringify(message);
  } else {
    displayMessage = String(message);
  }

  return (
    <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      <span className="text-xl">⚠️</span>
      <p className="text-sm">{displayMessage}</p>
    </div>
  );
}

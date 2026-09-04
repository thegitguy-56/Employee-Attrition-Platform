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
      <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
      <p className="text-sm">{displayMessage}</p>
    </div>
  );
}

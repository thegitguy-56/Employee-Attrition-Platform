// Layout.jsx — the shell that wraps every protected page
// Renders: Sidebar on the left | Navbar + page content on the right

import Sidebar from './Sidebar';
import Navbar from './Navbar';

export default function Layout({ children }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Left sidebar — always visible */}
      <Sidebar />

      {/* Right side — Navbar + page content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

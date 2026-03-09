'use client';
import { useAuth } from '@/lib/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/Layout/Sidebar';
import Navbar from '@/components/Layout/Navbar';

export default function AppLayout({ children, title }: { children: React.ReactNode; title?: string }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    // Immediate check: no token in localStorage = not authenticated at all
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

    if (!loading && !user) {
      setRedirecting(true);
      router.replace('/login');
    }

    if (!token && !loading) {
      setRedirecting(true);
      router.replace('/login');
    }
  }, [user, loading, router]);

  // NEVER render children if user is not authenticated
  if (loading || !user || redirecting) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div style={{ animation: 'pulse 1.5s infinite', fontSize: '20px', color: '#1E3A5F', fontWeight: 600 }}>
          {redirecting ? 'Redirecting to login...' : 'Loading...'}
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <div style={{ marginLeft: 'var(--sidebar-width)', flex: 1, minHeight: '100vh', background: 'var(--bg)' }}>
        <Navbar title={title} />
        <main>{children}</main>
      </div>
    </div>
  );
}

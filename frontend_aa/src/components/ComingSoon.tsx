'use client';
import AppLayout from '@/components/Layout/AppLayout';

export default function ComingSoonPage({ title, description }: { title: string, description?: string }) {
  return (
    <AppLayout title={title}>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '80vh',
        textAlign: 'center',
        padding: '0 24px'
      }}>
        <div style={{ fontSize: '64px', marginBottom: '24px' }}>🚧</div>
        <h1 style={{ fontSize: '32px', fontWeight: 800, color: 'var(--navy)', marginBottom: '12px' }}>
          Coming Soon
        </h1>
        <p style={{ fontSize: '16px', color: 'var(--gray-500)', maxWidth: '500px', lineHeight: 1.6 }}>
          {description || `We're working hard to bring you the ${title} feature. It will be available in an upcoming release.`}
        </p>
        <a href="/dashboard" className="btn btn-primary" style={{ marginTop: '32px' }}>
          Return to Dashboard
        </a>
      </div>
    </AppLayout>
  );
}

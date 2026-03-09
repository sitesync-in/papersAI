'use client';
import { useEffect, useState } from 'react';
import { papersAPI, PaperListItem } from '@/lib/api';
import AppLayout from '@/components/Layout/AppLayout';
import styles from './papers.module.css';

export default function MyPapersPage() {
  const [papers, setPapers] = useState<PaperListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<number | null>(null);

  useEffect(() => {
    papersAPI.list()
      .then(data => setPapers(data.results || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleDownload = async (paper: PaperListItem) => {
    setDownloading(paper.id);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(papersAPI.downloadUrl(paper.id), {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${paper.title || paper.subject}_paper.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Failed to download PDF. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadAnswerKey = async (paper: PaperListItem) => {
    setDownloading(paper.id * -1); // use negative ID to track answer key loading
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(papersAPI.downloadAnswerKeyUrl(paper.id), {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Download failed');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `answer_key_${paper.title || paper.subject}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Failed to download Answer Key PDF. Please try again.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <AppLayout title="My Papers">
      <div className={styles.page}>
        <div className={styles.header}>
          <div>
            <h1 className="page-title">My Papers</h1>
            <p className="page-subtitle">All your generated exam papers</p>
          </div>
          <a href="/generate" className="btn btn-gold">+ Generate New</a>
        </div>

        <div className="card">
          {loading ? (
            <div className={styles.loading}>Loading papers...</div>
          ) : papers.length === 0 ? (
            <div className={styles.empty}>
              <div className={styles.emptyIcon}>📂</div>
              <h3>No papers yet</h3>
              <p>Generate your first exam paper to get started.</p>
              <a href="/generate" className="btn btn-primary" style={{ marginTop: '16px' }}>Generate Paper</a>
            </div>
          ) : (
            <div className={styles.tableContainer}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Paper Name</th>
                    <th>Board</th>
                    <th>Class</th>
                    <th>Subject</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {papers.map(p => (
                    <tr key={p.id}>
                      <td style={{ fontWeight: 600 }}>📄 {p.title || `${p.subject} Paper`}</td>
                      <td>{p.board}</td>
                      <td>{p.class_name}</td>
                      <td>{p.subject}</td>
                      <td>{new Date(p.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</td>
                      <td><span className={`badge ${p.status === 'ready' ? 'badge-success' : 'badge-gold'}`}>● {p.status}</span></td>
                      <td>
                        <div className={styles.actions}>
                          {p.status === 'ready' && (
                            <>
                              <button className="btn btn-outline" style={{ padding: '6px 12px', fontSize: '12px' }}
                                onClick={() => handleDownload(p)}
                                disabled={downloading === p.id}>
                                {downloading === p.id ? '⏳...' : '📄 Paper'}
                              </button>
                              <button className="btn btn-gold" style={{ padding: '6px 12px', fontSize: '12px' }}
                                onClick={() => handleDownloadAnswerKey(p)}
                                disabled={downloading === (p.id * -1)}>
                                {downloading === (p.id * -1) ? '⏳...' : '🔑 Answer Key'}
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}

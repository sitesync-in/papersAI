'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/AuthContext';
import { useRouter } from 'next/navigation';
import { papersAPI, DashboardStats } from '@/lib/api';
import AppLayout from '@/components/Layout/AppLayout';
import styles from './dashboard.module.css';
import { useTranslation } from 'react-i18next';

export default function DashboardPage() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [board, setBoard] = useState('RBSE');
  const [classVal, setClassVal] = useState('Class 10');
  const [subject, setSubject] = useState('Mathematics');

  useEffect(() => {
    papersAPI.dashboardStats().then(setStats).catch(() => {});
  }, []);

  const handleQuickGenerate = () => {
    router.push(`/generate?board=${board}&class=${classVal}&subject=${subject}`);
  };

  return (
    <AppLayout title="Dashboard">
      <div className={styles.page}>
        {/* Greeting */}
        <div className="animate-fadeIn">
          <h1 className={styles.greeting}>{t('dashboard.welcome')}, {user?.first_name}!</h1>
          <p className={styles.greetingSub}>Here is what&apos;s happening with your papers today.</p>
        </div>

        {/* Stats Row */}
        <div className={styles.statsRow}>
          <div className={`card ${styles.statCard}`}>
            <div className={styles.statIcon} style={{ background: 'rgba(30,58,95,0.1)' }}>📄</div>
            <div>
              <div className={styles.statLabel}>{t('dashboard.stats.papers_generated').toUpperCase()}</div>
              <div className={styles.statValue}>{stats?.papers_generated ?? 0}</div>
            </div>
          </div>
          <div className={`card ${styles.statCard}`}>
            <div className={styles.statIcon} style={{ background: 'rgba(212,175,55,0.1)' }}>🕐</div>
            <div>
              <div className={styles.statLabel}>{t('dashboard.stats.hours_saved').toUpperCase()}</div>
              <div className={styles.statValue}>{stats?.hours_saved ?? 0} hrs</div>
            </div>
          </div>
          <div className={`card ${styles.statCard}`}>
            <div className={styles.statIcon} style={{ background: 'rgba(46,125,50,0.1)' }}>🎓</div>
            <div>
              <div className={styles.statLabel}>{t('dashboard.stats.active_classes').toUpperCase()}</div>
              <div className={styles.statValue}>{stats?.active_classes ?? 0}</div>
            </div>
          </div>
        </div>

        {/* Quick Generate + Recent Papers */}
        <div className={styles.mainRow}>
          {/* Quick Generate */}
          <div className={`card ${styles.quickGenerate}`}>
            <h3 className={styles.sectionTitle}>⚡ Quick Generate</h3>
            <div className={styles.qgField}>
              <label className="label">Board</label>
              <select className="input-field" value={board} onChange={e => setBoard(e.target.value)}>
                <option>RBSE</option>
                <option>RTU</option>
                <option>CBSE</option>
              </select>
            </div>
            <div className={styles.qgField}>
              <label className="label">Class</label>
              <select className="input-field" value={classVal} onChange={e => setClassVal(e.target.value)}>
                {['Class 6','Class 7','Class 8','Class 9','Class 10','Class 11','Class 12'].map(c =>
                  <option key={c}>{c}</option>
                )}
              </select>
            </div>
            <div className={styles.qgField}>
              <label className="label">Subject</label>
              <select className="input-field" value={subject} onChange={e => setSubject(e.target.value)}>
                {['Mathematics','Science','Hindi','English','Social Science','Physics','Chemistry','Biology'].map(s =>
                  <option key={s}>{s}</option>
                )}
              </select>
            </div>
            <button className="btn btn-gold btn-lg" style={{ width: '100%', marginTop: '8px' }} onClick={handleQuickGenerate}>
              ✨ Generate Now
            </button>
          </div>

          {/* Recent Papers */}
          <div className={`card ${styles.recentPapers}`}>
            <div className={styles.recentHeader}>
              <h3 className={styles.sectionTitle}>Recent Papers</h3>
              <a href="/my-papers" className={styles.viewAll}>View All</a>
            </div>

            <table className={styles.table}>
              <thead>
                <tr>
                  <th>PAPER NAME</th>
                  <th>CLASS</th>
                  <th>DATE</th>
                  <th>STATUS</th>
                </tr>
              </thead>
              <tbody>
                {stats?.recent_papers?.length ? (
                  stats.recent_papers.map((p) => (
                    <tr key={p.id} onClick={() => router.push(`/my-papers?id=${p.id}`)} style={{ cursor: 'pointer' }}>
                      <td>
                        <div className={styles.paperName}>
                          <span className={styles.paperIcon}>📄</span>
                          {p.title || `${p.subject} Paper`}
                        </div>
                      </td>
                      <td>{p.class_name}</td>
                      <td>{new Date(p.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</td>
                      <td>
                        <span className="badge badge-success">● {p.status === 'ready' ? 'Ready' : p.status}</span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={4} style={{ textAlign: 'center', padding: '32px', color: 'var(--gray-400)' }}>
                      No papers generated yet. Use Quick Generate to create one!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

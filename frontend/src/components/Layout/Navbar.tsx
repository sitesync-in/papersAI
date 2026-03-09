'use client';
import { useAuth } from '@/lib/AuthContext';
import { useEffect, useState } from 'react';
import { subscriptionsAPI } from '@/lib/api';
import styles from './Navbar.module.css';
import { useTranslation } from 'react-i18next';

export default function Navbar({ title, onMenuClick }: { title?: string, onMenuClick?: () => void }) {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const [credits, setCredits] = useState(0);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    subscriptionsAPI.wallet()
      .then(w => setCredits(w.credits))
      .catch(() => {});
  }, []);

  return (
    <header className={styles.navbar}>
      <div className={styles.left}>
        <button className={styles.menuBtn} onClick={onMenuClick}>
          ☰
        </button>
        <h2 className={styles.pageTitle}>{title || t('sidebar.dashboard')}</h2>
      </div>

      <div className={styles.right}>
        <div className={styles.creditBadge}>
          <span className={styles.creditIcon}>🟡</span>
          <span>{credits} Credits</span>
        </div>

        <button className={styles.notifBtn}>🔔</button>

        <div className={styles.profileArea} onClick={() => setShowMenu(!showMenu)}>
          <div className={styles.profileInfo}>
            <span className={styles.profileName}>
              {user?.first_name} {user?.last_name?.charAt(0)}.
            </span>
            <span className={styles.profileRole}>
              {user?.role === 'teacher' ? 'Educator' : 'Student'}
            </span>
          </div>
          <div className={styles.avatar}>
            {user?.first_name?.charAt(0) || '?'}
          </div>

          {showMenu && (
            <div className={styles.dropdown}>
              <a href="/settings" className={styles.dropItem}>Profile Settings</a>
              <button onClick={logout} className={styles.dropItem}>Sign Out</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

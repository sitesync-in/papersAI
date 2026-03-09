'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import styles from './Sidebar.module.css';

import { useTranslation } from 'react-i18next';

export default function Sidebar({ isOpen, onClose }: { isOpen?: boolean, onClose?: () => void }) {
  const pathname = usePathname();
  const { t } = useTranslation();

  const menuItems = [
    { href: '/dashboard', icon: '📊', label: t('sidebar.dashboard') },
    { href: '/generate', icon: '📝', label: t('sidebar.generate') },
    { href: '/my-papers', icon: '📂', label: t('sidebar.my_papers') },
    { href: '/students', icon: '👥', label: t('sidebar.students') },
    { href: '/subscription', icon: '💳', label: t('sidebar.subscription') },
    { href: '/settings', icon: '⚙️', label: t('sidebar.settings') },
  ];

  return (
    <aside className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
      <div className={styles.logoRow}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>✦</div>
          <div>
            <div className={styles.logoText}>papersAI</div>
            <div className={styles.logoSub}>{t('sidebar.teacher_panel')}</div>
          </div>
        </div>
        <button className={styles.closeBtn} onClick={onClose}>×</button>
      </div>

      <nav className={styles.nav}>
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`${styles.navItem} ${pathname === item.href ? styles.active : ''}`}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      <div className={styles.planStatus}>
        <div className={styles.planLabel}>PLAN STATUS</div>
        <div className={styles.planRow}>
          <span className={styles.planName}>Pro Plan</span>
          <span className={styles.planBadge}>Active</span>
        </div>
        <div className={styles.planBar}>
          <div className={styles.planProgress}></div>
        </div>
      </div>
    </aside>
  );
}

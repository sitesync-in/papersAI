'use client';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import styles from './Sidebar.module.css';

const menuItems = [
  { href: '/dashboard', icon: '📊', label: 'Dashboard' },
  { href: '/generate', icon: '📝', label: 'Generate Paper' },
  { href: '/my-papers', icon: '📂', label: 'My Papers' },
  { href: '/students', icon: '👥', label: 'My Students' },
  { href: '/subscription', icon: '💳', label: 'Subscription' },
  { href: '/settings', icon: '⚙️', label: 'Settings' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <div className={styles.logoIcon}>✦</div>
        <div>
          <div className={styles.logoText}>papersAI</div>
          <div className={styles.logoSub}>Teacher Panel</div>
        </div>
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

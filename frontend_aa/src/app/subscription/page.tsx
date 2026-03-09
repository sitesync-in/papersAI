'use client';
import { useEffect, useState } from 'react';
import { subscriptionsAPI, Plan, Wallet } from '@/lib/api';
import AppLayout from '@/components/Layout/AppLayout';
import styles from './subscription.module.css';

export default function SubscriptionPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [wallet, setWallet] = useState<Wallet | null>(null);

  useEffect(() => {
    subscriptionsAPI.plans().then(setPlans).catch(() => {});
    subscriptionsAPI.wallet().then(setWallet).catch(() => {});
  }, []);

  return (
    <AppLayout title="Subscription">
      <div className={styles.page}>
        <h1 className="page-title">Subscription & Plans</h1>
        <p className="page-subtitle">Manage your subscription and credits</p>

        {/* Wallet */}
        <div className={`card ${styles.walletCard}`}>
          <div className={styles.walletLeft}>
            <div className={styles.walletLabel}>Credit Balance</div>
            <div className={styles.walletAmount}>{wallet?.credits ?? 0} Credits</div>
          </div>
          <button className="btn btn-gold">+ Buy Credits</button>
        </div>

        {/* Plans */}
        <div className={styles.plansGrid}>
          {plans.map(plan => (
            <div key={plan.id} className={`card ${styles.planCard} ${plan.plan_type === 'school' ? styles.planHighlight : ''}`}>
              {plan.plan_type === 'school' && <div className={styles.recommended}>Recommended</div>}
              <h3 className={styles.planName}>{plan.name}</h3>
              <p className={styles.planDesc}>{plan.description}</p>
              <div className={styles.planPrice}>
                {plan.plan_type === 'free' ? (
                  <span className={styles.priceMain}>Free</span>
                ) : plan.plan_type === 'b2g' ? (
                  <span className={styles.priceMain}>Custom</span>
                ) : (
                  <>
                    <span className={styles.priceMain}>₹{plan.price_per_paper}</span>
                    <span className={styles.priceSub}>/paper</span>
                  </>
                )}
              </div>
              <ul className={styles.features}>
                {plan.features?.map((f, i) => (
                  <li key={i}>✓ {f}</li>
                ))}
              </ul>
              <button className={`btn ${plan.plan_type === 'school' ? 'btn-gold' : 'btn-outline'} ${styles.planBtn}`}>
                {plan.plan_type === 'b2g' ? 'Contact Sales' : 'Choose Plan'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}

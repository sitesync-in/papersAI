'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/AuthContext';
import { authAPI } from '@/lib/api';
import AppLayout from '@/components/Layout/AppLayout';
import styles from './settings.module.css';

export default function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '',
    employee_id: '', shala_darpan_id: '',
    school_name: '', udise_code: '', district: '',
    phone: '', preferred_language: 'English',
  });

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        employee_id: user.employee_id || '',
        shala_darpan_id: user.shala_darpan_id || '',
        school_name: user.school_name || '',
        udise_code: user.udise_code || '',
        district: user.district || '',
        phone: user.phone || '',
        preferred_language: user.preferred_language || 'English',
      });
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await authAPI.updateProfile(form);
      await refreshUser();
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error("Profile update failed:", err);
      alert("Failed to update profile. Please check console for details.");
    }
    setSaving(false);
  };

  return (
    <AppLayout title="Settings">
      <div className={styles.page}>
        <h1 className="page-title">Profile & Settings</h1>
        <p className="page-subtitle">Manage your account and school details</p>

        {saved && <div className={styles.success}>✅ Profile saved successfully!</div>}

        <form onSubmit={handleSave}>
          {/* Teacher Details */}
          <div className={`card ${styles.section}`}>
            <h3 className={styles.sectionTitle}>👤 Teacher Details</h3>
            <div className={styles.grid}>
              <div><label className="label">First Name</label><input className="input-field" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} /></div>
              <div><label className="label">Last Name</label><input className="input-field" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} /></div>
              <div><label className="label">Email</label><input className="input-field" type="email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} /></div>
              <div><label className="label">Phone</label><input className="input-field" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} /></div>
              <div><label className="label">Employee ID</label><input className="input-field" value={form.employee_id} onChange={e => setForm({ ...form, employee_id: e.target.value })} /></div>
              <div><label className="label">Shala Darpan ID</label><input className="input-field" value={form.shala_darpan_id} onChange={e => setForm({ ...form, shala_darpan_id: e.target.value })} /></div>
            </div>
          </div>

          {/* School Details */}
          <div className={`card ${styles.section}`}>
            <h3 className={styles.sectionTitle}>🏫 School Details</h3>
            <div className={styles.grid}>
              <div><label className="label">School Name</label><input className="input-field" value={form.school_name} onChange={e => setForm({ ...form, school_name: e.target.value })} /></div>
              <div><label className="label">UDISE Code</label><input className="input-field" value={form.udise_code} onChange={e => setForm({ ...form, udise_code: e.target.value })} /></div>
              <div><label className="label">District</label><input className="input-field" value={form.district} onChange={e => setForm({ ...form, district: e.target.value })} /></div>
            </div>
          </div>

          {/* Preferences */}
          <div className={`card ${styles.section}`}>
            <h3 className={styles.sectionTitle}>🌐 Preferences</h3>
            <div className={styles.langRow}>
              <label className="label">Default Language</label>
              <div className={styles.langBtns}>
                <button type="button" className={`${styles.langBtn} ${form.preferred_language === 'English' ? styles.langActive : ''}`}
                  onClick={() => setForm({ ...form, preferred_language: 'English' })}>English</button>
                <button type="button" className={`${styles.langBtn} ${form.preferred_language === 'Hindi' ? styles.langActive : ''}`}
                  onClick={() => setForm({ ...form, preferred_language: 'Hindi' })}>हिंदी (Hindi)</button>
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-lg" disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </AppLayout>
  );
}

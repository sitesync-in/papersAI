'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/AuthContext';
import { authAPI } from '@/lib/api';
import styles from './login.module.css';

const DISTRICTS = [
  'Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Bikaner', 'Ajmer',
  'Alwar', 'Bharatpur', 'Bhilwara', 'Chittorgarh', 'Sikar',
  'Pali', 'Nagaur', 'Tonk', 'Bundi', 'Barmer', 'Jaisalmer',
];

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Login form
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Signup form
  const [fullName, setFullName] = useState('');
  const [schoolName, setSchoolName] = useState('');
  const [district, setDistrict] = useState('');
  const [preferredLanguage, setPreferredLanguage] = useState('en');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await authAPI.login({ email, password });
      login(res.access, res.refresh, res.user);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err?.non_field_errors?.[0] || err?.email?.[0] || 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const parts = fullName.trim().split(' ');
    try {
      const res = await authAPI.register({
        username: email.split('@')[0],
        email,
        password,
        first_name: parts[0] || '',
        last_name: parts.slice(1).join(' ') || '',
        school_name: schoolName,
        district,
        preferred_language: preferredLanguage,
      });
      login(res.access, res.refresh, res.user);
      router.push('/dashboard');
    } catch (err: any) {
      let errorMsg = 'Registration failed. Check your details.';
      if (err && typeof err === 'object') {
        const messages = [];
        // Skip HTTP status codes or generic keys if needed, but usually DRF returns field arrays
        for (const [key, val] of Object.entries(err)) {
          if (key === 'status') continue;
          if (Array.isArray(val)) messages.push(...val);
          else if (typeof val === 'string') messages.push(val);
        }
        if (messages.length > 0) errorMsg = messages.join(' ');
      }
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className={styles.container}>
      {/* Left: Branding */}
      <div className={styles.left}>
        <div className={styles.brand}>
          <div className={styles.logoRow}>
            <div className={styles.logoIcon}>📄</div>
            <span className={styles.logoText}>papersAI</span>
          </div>

          <h1 className={styles.headline}>
            Intelligent Assessment Generation for Rajasthan&apos;s Educators.
          </h1>

          <p className={styles.desc}>
            Revolutionizing the way teachers create high-quality, curriculum-aligned exam papers in minutes.
          </p>

          <div className={styles.features}>
            <div className={styles.featureItem}>✅ State-approved curriculum alignment</div>
            <div className={styles.featureItem}>✅ AI-powered question bank generation</div>
          </div>
        </div>

        <div className={styles.footer}>
          © 2024 papersAI. Official partner for Rajasthan Educational Excellence.
        </div>
      </div>

      {/* Right: Forms */}
      <div className={styles.right}>
        <div className={styles.formSection}>
          {error && <div className={styles.error}>{error}</div>}

          {!isSignUp ? (
            /* ==================== LOGIN VIEW ==================== */
            <>
              <h2 className={styles.welcome}>Welcome back, Educator.</h2>
              <p className={styles.subline}>Access your dashboard to manage assessments.</p>

              <div className={styles.ssoBtn} style={{ opacity: 0.5, cursor: 'not-allowed' }}>
                <span>🔒</span> Login with SSO Rajasthan (Coming Soon)
              </div>

              <form onSubmit={handleLogin}>
                <div className={styles.field}>
                  <label className="label">Email Address</label>
                  <input type="email" className="input-field" placeholder="educator@school.rj.gov.in"
                    value={email} onChange={e => setEmail(e.target.value)} required />
                </div>
                <div className={styles.field}>
                  <label className="label">
                    Password
                    <a href="#" className={styles.forgot}>Forgot?</a>
                  </label>
                  <input type="password" className="input-field" placeholder="••••••••"
                    value={password} onChange={e => setPassword(e.target.value)} required />
                </div>
                <button type="submit" className={`btn btn-primary btn-lg ${styles.submitBtn}`} disabled={loading}>
                  {loading ? 'Signing in...' : 'Sign In'}
                </button>
              </form>

              <div className={styles.signupSection}>
                <h3 className={styles.signupTitle}>New to papersAI? Create Account</h3>
                <button type="button" className={styles.toggleBtn} onClick={() => setIsSignUp(true)}>
                  Create a new account →
                </button>
              </div>
            </>
          ) : (
            /* ==================== SIGNUP VIEW ==================== */
            <>
              <h2 className={styles.welcome}>Create your account</h2>
              <p className={styles.subline}>Register as an educator to get started.</p>

              <form onSubmit={handleSignup}>
                <div className={styles.field}>
                  <label className="label">Email Address</label>
                  <input type="email" className="input-field" placeholder="educator@school.rj.gov.in"
                    value={email} onChange={e => setEmail(e.target.value)} required />
                </div>
                <div className={styles.field}>
                  <label className="label">Password</label>
                  <input type="password" className="input-field" placeholder="••••••••"
                    value={password} onChange={e => setPassword(e.target.value)} required />
                </div>
                <div className={styles.field}>
                  <label className="label">Full Name</label>
                  <input className="input-field" placeholder="Rajesh Kumar"
                    value={fullName} onChange={e => setFullName(e.target.value)} required />
                </div>
                <div className={styles.field}>
                  <label className="label">School Name</label>
                  <input className="input-field" placeholder="Govt. Sr. Sec. School"
                    value={schoolName} onChange={e => setSchoolName(e.target.value)} />
                </div>
                <div className={styles.field}>
                  <label className="label">District (Rajasthan)</label>
                  <select className="input-field" value={district} onChange={e => setDistrict(e.target.value)} required>
                    <option value="">Select District</option>
                    {DISTRICTS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
                <div className={styles.field}>
                  <label className="label">Preferred Generation Language</label>
                  <select className="input-field" value={preferredLanguage} onChange={e => setPreferredLanguage(e.target.value)}>
                    <option value="en">English</option>
                    <option value="hi">Hindi (हिंदी)</option>
                  </select>
                </div>
                <button type="submit" className={`btn btn-primary btn-lg ${styles.submitBtn}`} disabled={loading}>
                  {loading ? 'Registering...' : 'Register as Educator'}
                </button>
              </form>

              <button type="button" className={styles.toggleBtn} style={{ marginTop: '16px' }} onClick={() => setIsSignUp(false)}>
                Already have an account? Sign In
              </button>
            </>
          )}

          <div className={styles.support}>
            Need assistance? <a href="#">Contact Support</a>
          </div>
        </div>
      </div>
    </div>
  );
}

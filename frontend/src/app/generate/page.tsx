'use client';
import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { papersAPI } from '@/lib/api';
import AppLayout from '@/components/Layout/AppLayout';
import styles from './generate.module.css';
import { useAuth } from '@/lib/AuthContext';
import { useTranslation } from 'react-i18next';

function GenerateContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const { t } = useTranslation();

  const [step, setStep] = useState(1);
  const [board, setBoard] = useState(searchParams.get('board') || 'RBSE');
  const [classVal, setClassVal] = useState(searchParams.get('class') || '');
  const [subject, setSubject] = useState(searchParams.get('subject') || '');
  const [difficulty, setDifficulty] = useState('balanced');
  const [topics, setTopics] = useState('');
  const [adhereScheme, setAdhereScheme] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [genStep, setGenStep] = useState(0);
  const [paper, setPaper] = useState<any>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [error, setError] = useState('');
  const [paperLanguage, setPaperLanguage] = useState(user?.preferred_language || 'en');

  // RTU-specific states
  const [rtuBranch, setRtuBranch] = useState('');
  const [rtuSemester, setRtuSemester] = useState('');
  const [rtuBranches, setRtuBranches] = useState<any[]>([]);
  const [rtuSemesters, setRtuSemesters] = useState<any[]>([]);
  const [rtuSubjects, setRtuSubjects] = useState<any[]>([]);
  const [loadingRtuData, setLoadingRtuData] = useState(false);

  // If user loads later, override initial state
  useEffect(() => {
    if (user?.preferred_language && paperLanguage === 'en') {
      setPaperLanguage(user.preferred_language);
    }
  }, [user]);

  // Fetch RTU branches when board is RTU
  useEffect(() => {
    if (board === 'RTU') {
      fetchRtuBranches();
      setRtuBranch('');
      setRtuSemester('');
      setClassVal('');
      setSubject('');
    }
  }, [board]);

  // Fetch RTU semesters when branch is selected
  useEffect(() => {
    if (board === 'RTU' && rtuBranch) {
      fetchRtuSemesters(rtuBranch);
      setRtuSemester('');
      setSubject('');
    }
  }, [rtuBranch]);

  // Fetch RTU subjects when semester is selected
  useEffect(() => {
    if (board === 'RTU' && rtuBranch && rtuSemester) {
      fetchRtuSubjects(rtuBranch, rtuSemester);
    }
  }, [rtuSemester]);

  const fetchRtuBranches = async () => {
    setLoadingRtuData(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('/api/papers/curriculum-options/?board=RTU', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.branches) {
        setRtuBranches(data.branches);
      }
    } catch (err) {
      console.error('Failed to fetch RTU branches:', err);
    } finally {
      setLoadingRtuData(false);
    }
  };

  const fetchRtuSemesters = async (branch: string) => {
    setLoadingRtuData(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/papers/curriculum-options/?board=RTU&branch=${branch}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.semesters) {
        setRtuSemesters(data.semesters);
      }
    } catch (err) {
      console.error('Failed to fetch RTU semesters:', err);
    } finally {
      setLoadingRtuData(false);
    }
  };

  const fetchRtuSubjects = async (branch: string, semester: string) => {
    setLoadingRtuData(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`/api/papers/curriculum-options/?board=RTU&branch=${branch}&semester=${semester}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.subjects) {
        setRtuSubjects(data.subjects);
      }
    } catch (err) {
      console.error('Failed to fetch RTU subjects:', err);
    } finally {
      setLoadingRtuData(false);
    }
  };

  const steps = [
    { num: 1, label: 'Curriculum' },
    { num: 2, label: 'Blueprint' },
    { num: 3, label: 'Generation' },
    { num: 4, label: 'Output' },
  ];

  const genSteps = [
    'Connecting to AI Core...',
    'Analyzing Syllabus...',
    'Drafting Questions...',
    'Generating Answer Key...',
  ];

  const handleGenerate = async () => {
    setStep(3);
    setGenerating(true);
    setError('');

    // Show progressive loading states
    for (let i = 0; i < genSteps.length; i++) {
      setGenStep(i);
      await new Promise(r => setTimeout(r, 1200));
    }

    try {
      const payload: any = {
        board, class_name: classVal, subject,
        difficulty, topics, adhere_marking_scheme: adhereScheme,
        preferred_language: paperLanguage,
      };

      // Add RTU-specific fields if applicable
      if (board === 'RTU') {
        payload.branch = rtuBranch;
        payload.semester = rtuSemester;
      }

      const result = await papersAPI.generate(payload);
      setPaper(result);
      setStep(4);
    } catch (err: any) {
      setError(err?.error || 'Generation failed. Please check your API key.');
      setStep(2);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    if (!paper) return;
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
      a.download = `paper_${paper.id}_${paper.subject?.replace(/\s/g, '_') || 'exam'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Failed to download PDF. Please try again.');
    }
  };

  const handleDownloadAnswerKey = async () => {
    if (!paper) return;
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
      a.download = `answer_key_${paper.id}_${paper.subject?.replace(/\s/g, '_') || 'exam'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Failed to download Answer Key PDF. Please try again.');
    }
  };

  return (
    <div className={styles.page}>
      {/* Step Indicator */}
      <div className={styles.stepBar}>
        {steps.map((s, i) => (
          <div key={s.num} className={styles.stepItem}>
            <div className={`${styles.stepNum} ${step >= s.num ? styles.stepActive : ''} ${step > s.num ? styles.stepDone : ''}`}>
              {step > s.num ? '✓' : s.num}
            </div>
            <span className={`${styles.stepLabel} ${step >= s.num ? styles.stepLabelActive : ''}`}>
              {s.label}
            </span>
            {i < steps.length - 1 && <div className={`${styles.stepLine} ${step > s.num ? styles.stepLineDone : ''}`} />}
          </div>
        ))}
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* Step 1: Curriculum Selection */}
      {step === 1 && (
        <div className={styles.stepContent}>
          <div className="card">
            <h3 className={styles.cardTitle}>📚 1. Curriculum Selection</h3>

            <label className="label">Board</label>
            <div className={styles.boardRow}>
              {['RBSE', 'RTU', 'CBSE'].map(b => (
                <button key={b}
                  className={`${styles.boardBtn} ${board === b ? styles.boardActive : ''}`}
                  onClick={() => setBoard(b)}>
                  {b}
                </button>
              ))}
            </div>

            <div className={styles.formRow} style={{ marginTop: '16px' }}>
              <div className={styles.formField}>
                <label className="label">{t('generate.paper_language') || "Language"}</label>
                <select className="input-field" value={paperLanguage} onChange={e => setPaperLanguage(e.target.value)}>
                  <option value="en">English</option>
                  <option value="hi">Hindi (हिंदी)</option>
                </select>
              </div>
            </div>

            {/* RTU-specific selectors */}
            {board === 'RTU' ? (
              <div className={styles.formRow}>
                <div className={styles.formField}>
                  <label className="label">Branch</label>
                  <select className="input-field" value={rtuBranch} onChange={e => setRtuBranch(e.target.value)} disabled={loadingRtuData}>
                    <option value="">Select Branch</option>
                    {rtuBranches.map(b => (
                      <option key={b.code} value={b.code}>{b.code} - {b.name}</option>
                    ))}
                  </select>
                </div>

                {rtuBranch && (
                  <div className={styles.formField}>
                    <label className="label">Semester</label>
                    <select className="input-field" value={rtuSemester} onChange={e => setRtuSemester(e.target.value)} disabled={loadingRtuData}>
                      <option value="">Select Semester</option>
                      {rtuSemesters.map(s => (
                        <option key={s.semester} value={s.semester}>Semester {s.semester} ({s.totalCredits} Credits)</option>
                      ))}
                    </select>
                  </div>
                )}

                {rtuSemester && (
                  <div className={styles.formField}>
                    <label className="label">Subject</label>
                    <select className="input-field" value={subject} onChange={e => setSubject(e.target.value)} disabled={loadingRtuData}>
                      <option value="">Select Subject</option>
                      {rtuSubjects.map(s => (
                        <option key={s.name} value={s.name}>{s.name} ({s.credits} credits)</option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            ) : (
              /* RBSE/CBSE standard selectors */
              <div className={styles.formRow}>
                <div className={styles.formField}>
                  <label className="label">Class</label>
                  <select className="input-field" value={classVal} onChange={e => setClassVal(e.target.value)}>
                    <option value="">Select Class / Semester</option>
                    {['Class 6','Class 7','Class 8','Class 9','Class 10','Class 11','Class 12'].map(c =>
                      <option key={c} value={c}>{c}</option>
                    )}
                  </select>
                </div>
                <div className={styles.formField}>
                  <label className="label">Subject</label>
                  <select className="input-field" value={subject} onChange={e => setSubject(e.target.value)}>
                    <option value="">Select Subject</option>
                    {['Mathematics','Science','Hindi','English','Social Science','Physics','Chemistry','Biology','Computer Science'].map(s =>
                      <option key={s} value={s}>{s}</option>
                    )}
                  </select>
                </div>
              </div>
            )}

            <button className="btn btn-primary" style={{ marginTop: '16px' }}
              onClick={() => setStep(2)} 
              disabled={board === 'RTU' ? !rtuBranch || !rtuSemester || !subject : !classVal || !subject}>
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Blueprint */}
      {step === 2 && (
        <div className={styles.stepContent}>
          <div className="card">
            <h3 className={styles.cardTitle}>🔧 2. Paper Blueprint</h3>

            <label className="label">Difficulty Level</label>
            <div className={styles.sliderWrap}>
              <input type="range" min="0" max="2" step="1"
                value={difficulty === 'easy' ? 0 : difficulty === 'balanced' ? 1 : 2}
                onChange={e => setDifficulty(['easy','balanced','hard'][parseInt(e.target.value)])}
                className={styles.slider} />
              <div className={styles.sliderLabels}>
                <span>EASY</span>
                <span>MODERATE</span>
                <span>HARD</span>
              </div>
              <span className={styles.diffBadge}>{difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</span>
            </div>

            <label className={styles.checkLabel}>
              <input type="checkbox" checked={adhereScheme} onChange={e => setAdhereScheme(e.target.checked)} />
              <span>Adhere to Rajasthan State Marking Scheme (2023-24)</span>
            </label>

            <label className="label" style={{ marginTop: '16px' }}>Target Topics</label>
            <textarea className="input-field" rows={3} placeholder="e.g. Calculus, Trigonometry, Vectors..."
              value={topics} onChange={e => setTopics(e.target.value)} />

            <div className={styles.btnRow}>
              <button className="btn btn-outline" onClick={() => setStep(1)}>← Back</button>
              <button className="btn btn-gold btn-lg" onClick={handleGenerate}>
                ✨ Generate Paper
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Generating */}
      {step === 3 && (
        <div className={styles.stepContent}>
          <div className={`card ${styles.genCenter}`}>
            <div className={styles.genIcon}>✦</div>
            <h3>AI state: Processing</h3>
            <div className={styles.genSteps}>
              {genSteps.map((gs, i) => (
                <div key={i} className={`${styles.genStepItem} ${genStep >= i ? styles.genStepDone : ''}`}>
                  <span className={styles.genDot}>{genStep > i ? '✓' : genStep === i ? '◉' : '○'}</span>
                  <span>{gs}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Output */}
      {step === 4 && paper && (
        <div className={styles.stepContent}>
          <div className={styles.outputRow}>
            {/* Paper Preview */}
            <div className={`card ${styles.paperPreview}`}>
              <div className={styles.previewHeader}>
                <span className="label">DRAFT PREVIEW</span>
                <button className={styles.expandBtn}>⛶</button>
              </div>
              <div className={styles.previewContent}>
                <pre>{paper.paper_text}</pre>
              </div>
            </div>

            {/* Answer Key */}
            <div className={`${styles.answerKey}`}>
              <div className={styles.answerHeader}>
                <span className="label" style={{ color: 'rgba(255,255,255,0.6)' }}>ANSWER KEY</span>
                <button className={styles.lockBtn} onClick={() => setShowAnswer(!showAnswer)}>
                  {showAnswer ? '🔓' : '🔒'}
                </button>
              </div>
              <div className={styles.answerContent}>
                {showAnswer ? (
                  <pre>{paper.answer_key_text}</pre>
                ) : (
                  <div className={styles.answerBlur}>Click the lock to reveal the answer key</div>
                )}
              </div>
            </div>
          </div>

          {/* Action Bar */}
          <div className={styles.actionBar}>
            <button className="btn btn-outline" onClick={() => { setStep(1); setPaper(null); }}>
              Generate Another
            </button>
            <button className="btn btn-outline">📧 E-Mail</button>
            <button className="btn btn-primary" onClick={handleDownload} style={{ background: 'var(--navy)' }}>
              ⬇️ Download PDF
            </button>
            <button className="btn btn-gold" onClick={handleDownloadAnswerKey}>
              🔑 Download Answer Key
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default function GeneratePage() {
  return (
    <AppLayout title="Generate Paper">
      <Suspense fallback={<div style={{padding:32}}>Loading...</div>}>
        <GenerateContent />
      </Suspense>
    </AppLayout>
  );
}

// Fall back to relative path in production so Nginx can proxy to backend
const DEFAULT_API = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';
const API_URL = process.env.NEXT_PUBLIC_API_URL || DEFAULT_API;

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((customHeaders as Record<string, string>) || {}),
  };

  const storedToken = token || (typeof window !== 'undefined' ? localStorage.getItem('access_token') : null);
  if (storedToken) {
    headers['Authorization'] = `Bearer ${storedToken}`;
  }

  const res = await fetch(`${API_URL}${endpoint}`, { headers, ...rest });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw { status: res.status, ...errorData };
  }

  if (res.status === 204) return {} as T;
  return res.json();
}

// ========================= AUTH =========================
export interface LoginPayload { email: string; password: string; }
export interface RegisterPayload {
  username: string; email: string; password: string;
  first_name: string; last_name: string;
  school_name?: string; district?: string;
  preferred_language?: string;
}
export interface AuthResponse {
  access: string; refresh: string;
  user: UserProfile;
}
export interface UserProfile {
  id: number; username: string; email: string;
  first_name: string; last_name: string; role: string;
  school_name: string; district: string;
  employee_id: string; shala_darpan_id: string; udise_code: string;
  phone: string; preferred_language: string; avatar: string | null;
  date_joined: string; created_at: string;
}

export const authAPI = {
  login: (data: LoginPayload) => apiFetch<AuthResponse>('/api/auth/login/', { method: 'POST', body: JSON.stringify(data) }),
  register: (data: RegisterPayload) => apiFetch<AuthResponse>('/api/auth/register/', { method: 'POST', body: JSON.stringify(data) }),
  sso: (sso_token: string) => apiFetch<AuthResponse>('/api/auth/sso/', { method: 'POST', body: JSON.stringify({ sso_token }) }),
  me: () => apiFetch<UserProfile>('/api/auth/me/'),
  updateProfile: (data: Partial<UserProfile>) => apiFetch<UserProfile>('/api/auth/profile/', { method: 'PATCH', body: JSON.stringify(data) }),
  refreshToken: (refresh: string) => apiFetch<{ access: string }>('/api/auth/token/refresh/', { method: 'POST', body: JSON.stringify({ refresh }) }),
};

// ========================= PAPERS =========================
export interface PaperGeneratePayload {
  board: string; class_name: string; subject: string;
  difficulty?: string; topics?: string; adhere_marking_scheme?: boolean;
  preferred_language?: string;
}
export interface PaperListItem {
  id: number; title: string; board: string; class_name: string;
  subject: string; difficulty: string; status: string;
  credits_used: number; created_at: string;
}

export interface PaperDetail extends PaperListItem {
  paper_content: any; answer_key: any;
  paper_text: string; answer_key_text: string;
  topics: string; adhere_marking_scheme: boolean;
}

export interface DashboardStats {
  papers_generated: number; hours_saved: number;
  active_classes: number; recent_papers: PaperListItem[];
}

export const papersAPI = {
  generate: (data: PaperGeneratePayload) => apiFetch<PaperDetail>('/api/papers/generate/', { method: 'POST', body: JSON.stringify(data) }),
  list: () => apiFetch<{ results: PaperListItem[] }>('/api/papers/'),
  detail: (id: number) => apiFetch<PaperDetail>(`/api/papers/${id}/`),
  downloadUrl: (id: number) => `${API_URL}/api/papers/${id}/download/`,
  dashboardStats: () => apiFetch<DashboardStats>('/api/papers/dashboard/stats/'),
};

// ========================= STUDENTS =========================
export interface StudentClass { id: number; name: string; board: string; section: string; academic_year: string; student_count: number; }
export interface Student { id: number; first_name: string; last_name: string; roll_number: string; email: string; phone: string; student_class: number; class_name: string; }

export const studentsAPI = {
  listClasses: () => apiFetch<any>('/api/students/classes/').then(r => Array.isArray(r) ? r : (r.results || [])),
  createClass: (data: Partial<StudentClass>) => apiFetch<StudentClass>('/api/students/classes/', { method: 'POST', body: JSON.stringify(data) }),
  list: () => apiFetch<{ results: Student[] }>('/api/students/'),
  create: (data: Partial<Student>) => apiFetch<Student>('/api/students/', { method: 'POST', body: JSON.stringify(data) }),
  delete: (id: number) => apiFetch<void>(`/api/students/${id}/`, { method: 'DELETE' }),
};

// ========================= SUBSCRIPTIONS =========================
export interface Plan { id: number; name: string; plan_type: string; price_per_paper: string; monthly_price: string; credits_included: number; description: string; features: string[]; }
export interface Wallet { credits: number; updated_at: string; }

export const subscriptionsAPI = {
  plans: () => apiFetch<Plan[]>('/api/subscriptions/plans/'),
  wallet: () => apiFetch<Wallet>('/api/subscriptions/wallet/'),
  mySubscription: () => apiFetch<any>('/api/subscriptions/my/'),
};

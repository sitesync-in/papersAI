import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/lib/AuthContext';

export const metadata: Metadata = {
  title: 'PapersAI — Intelligent Assessment Generation',
  description: 'AI-powered exam paper generation for Rajasthan educators. Generate curriculum-aligned papers in minutes.',
};

import I18nProviderWrapper from '@/components/Layout/I18nProviderWrapper';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <I18nProviderWrapper>
            {children}
          </I18nProviderWrapper>
        </AuthProvider>
      </body>
    </html>
  );
}

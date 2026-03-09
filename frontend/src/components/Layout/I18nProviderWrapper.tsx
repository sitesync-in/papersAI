'use client';

import { useEffect } from 'react';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n';
import { useAuth } from '@/lib/AuthContext';

export default function I18nProviderWrapper({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  useEffect(() => {
    // Whenever the logged-in user changes or updates profile, sync their language to i18next
    if (user && user.preferred_language) {
      if (i18n.language !== user.preferred_language) {
        i18n.changeLanguage(user.preferred_language);
      }
    }
  }, [user]);

  return <I18nextProvider i18n={i18n}>{children}</I18nextProvider>;
}

'use client';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      sidebar: {
        dashboard: "Dashboard",
        generate: "Generate Paper",
        my_papers: "My Papers",
        students: "My Students",
        subscription: "Subscription",
        settings: "Settings",
        teacher_panel: "Teacher Panel"
      },
      dashboard: {
        welcome: "Welcome back",
        quick_actions: "Quick Actions",
        recent_papers: "Recent Papers",
        stats: {
          papers_generated: "Papers Generated",
          hours_saved: "Hours Saved",
          active_classes: "Active Classes"
        }
      },
      settings: {
        title: "Profile & Settings",
        subtitle: "Manage your account and school details",
        teacher_details: "Teacher Details",
        school_details: "School Details",
        preferences: "Preferences",
        save: "Save Changes",
        saving: "Saving...",
        success: "Profile saved successfully!"
      },
      generate: {
        paper_language: "Paper Output Language"
      }
    }
  },
  hi: {
    translation: {
      sidebar: {
        dashboard: "डैशबोर्ड",
        generate: "प्रश्न पत्र बनाएं",
        my_papers: "मेरे प्रश्न पत्र",
        students: "छात्र प्रबंधन",
        subscription: "सदस्यता",
        settings: "सेटिंग्स",
        teacher_panel: "शिक्षक पैनल"
      },
      dashboard: {
        welcome: "वापसी पर स्वागत है",
        quick_actions: "त्वरित कार्रवाई",
        recent_papers: "हाल ही के प्रश्न पत्र",
        stats: {
          papers_generated: "प्रश्न पत्र बनाए गए",
          hours_saved: "बचाए गए घंटे",
          active_classes: "सक्रिय कक्षाएं"
        }
      },
      settings: {
        title: "प्रोफ़ाइल और सेटिंग्स",
        subtitle: "अपने खाते और स्कूल विवरण प्रबंधित करें",
        teacher_details: "शिक्षक का विवरण",
        school_details: "स्कूल का विवरण",
        preferences: "प्राथमिकताएं",
        save: "परिवर्तन सहेजें",
        saving: "सहेजा जा रहा है...",
        success: "प्रोफ़ाइल सफलतापूर्वक सहेजी गई!"
      },
      generate: {
        paper_language: "प्रश्न पत्र की भाषा"
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en', // Default initial language
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false 
    }
  });

export default i18n;

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import resources from './resources';

const STORAGE_KEY = 'viethome-lang';
const savedLang = typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;

i18n.use(initReactI18next).init({
  resources,
  lng: savedLang ?? 'vi',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

i18n.on('languageChanged', (lng) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, lng);
  }
});

export default i18n;

import { useTranslation } from 'react-i18next';
import type { LocalizedText } from '../data/properties';

export function useLocalizedText() {
  const { i18n } = useTranslation();
  const lang = i18n.language as keyof LocalizedText;

  return (text: LocalizedText) => text[lang] ?? text.en;
}

// Clean react-i18next setup — no full-page reloads on language switch (unlike
// the old Krishi-Rakshak prototype, which reloaded the page twice per switch
// and only ever shipped English/Hindi/Punjabi, not Marathi). Language changes
// here just update React state and re-render via the useTranslation() hook.
import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import en from "./locales/en";
import hi from "./locales/hi";
import mr from "./locales/mr";

export const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिंदी" },
  { code: "mr", label: "मराठी" },
] as const;

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      mr: { translation: mr },
    },
    fallbackLng: "en",
    supportedLngs: ["en", "hi", "mr"],
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "sfa_lang",
    },
  });

export default i18n;

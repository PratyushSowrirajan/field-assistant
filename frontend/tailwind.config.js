/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Deep agricultural green — primary nav, major actions, active states
        forest: {
          DEFAULT: "#1F3D2B",
          light: "#2B5039",
          dark: "#152A1D",
        },
        // Mid/leaf green — healthy states, positive indicators
        leaf: {
          DEFAULT: "#4C7A3F",
          light: "#6B9757",
          dark: "#3A5F30",
        },
        // Olive — secondary agricultural info
        olive: {
          DEFAULT: "#7A7550",
          light: "#96916B",
        },
        // Warm neutrals — page surfaces, soil accents
        cream: "#FBF7EE",
        sand: "#F1E9D8",
        soil: {
          DEFAULT: "#8A5A3B",
          dark: "#6B4429",
        },
        ink: "#26291F",
        // Risk semantics — reserved for actual severity, not decoration
        risk: {
          healthy: "#4C7A3F",
          monitor: "#C89B2E",
          attention: "#D97B2B",
          high: "#C1502E",
          critical: "#A32F26",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(38, 41, 31, 0.06), 0 1px 8px rgba(38, 41, 31, 0.05)",
      },
      borderRadius: {
        xl2: "1.25rem",
      },
    },
  },
  plugins: [],
};

import type { Config } from "tailwindcss";

/**
 * Corporation Premium palette — professional automotive.
 *   navy   #0F3057  primary brand, headers, buttons
 *   amber  #E8890C  CTAs, accents, highlights
 *   steel  neutral grays for text and surfaces
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#0F3057",
          50: "#EEF3F9",
          100: "#D5E1EF",
          600: "#164371",
          700: "#123A64",
          800: "#0F3057",
          900: "#0A2240",
        },
        amber: {
          DEFAULT: "#E8890C",
          500: "#F59E0B",
          600: "#E8890C",
          700: "#C46F04",
        },
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;

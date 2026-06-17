import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        mist: "#EEF3F5",
        signal: "#0F766E",
        caution: "#B45309",
        steel: "#334155",
        berry: "#BE123C"
      },
      boxShadow: {
        panel: "0 1px 2px rgba(15, 23, 42, 0.08), 0 14px 34px rgba(15, 23, 42, 0.10)"
      }
    }
  },
  plugins: []
};

export default config;

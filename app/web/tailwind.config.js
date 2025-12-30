/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: "#c86bff",
        brandDark: "#a44ddd",
        accent: "#2f81f7",
        soft: "#f3f4f7",
      },
      borderRadius: {
        card: "12px",
      },
      boxShadow: {
        card: "0 4px 12px rgba(0,0,0,0.06)",
      },
    },
  },
  plugins: [],
};

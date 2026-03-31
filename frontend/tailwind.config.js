/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#060914",
      },
      boxShadow: {
        glow: "0 0 40px rgba(124, 58, 237, 0.35)",
      },
      keyframes: {
        floaty: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-14px)" },
        },
      },
      animation: {
        floaty: "floaty 9s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

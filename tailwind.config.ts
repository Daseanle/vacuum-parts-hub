import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}", // <--- 关键是这一行，指明了app文件夹
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
export default config;

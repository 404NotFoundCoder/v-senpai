export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans TC"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#FDF7F0', // 奶白（背景）
          100: '#FBECDC', // 淺杏桃
          200: '#F9D8C1', // 柔橘
          300: '#F8C4AF', // 蜜桃
          400: '#E4B2A0', // 奶茶橘棕
          500: '#C79288', // 焦糖棕（主色）
          600: '#A76F65', // 深奶茶
          700: '#87564D', // 可可棕
          800: '#654039', // 木質深棕
          900: '#3F2825', // 極深紅棕（hover/focus）
        },
      },
    },
  },
}

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/src/**/*.js"],
  theme: {
    extend: {
      colors: {
        "dark-green": "rgba(63, 106, 84, 1)",
        "green-btn": "rgba(29, 47, 35, 1)",
        "input-gray": "rgb(34, 42, 39)",
        "light-green": "rgba(213, 239, 225, 1)",
        "light-gray": "rgba(63, 106, 84, 0.1)",
      },
      fontFamily: {
        roboto: ["Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};

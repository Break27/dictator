const defaultTheme = require('tailwindcss/defaultTheme');
const { addDynamicIconSelectors } = require('@iconify/tailwind');

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['../templates/**/*.html'],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Open Sans', ...defaultTheme.fontFamily.sans],
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        addDynamicIconSelectors(),
    ],
}
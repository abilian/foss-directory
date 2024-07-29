const colors = require("tailwindcss/colors");

module.exports = {
  content: [
    "../src/**/templates/**/*.html",
    "../src/**/templates/**/*.j2",
    "../src/**/*.py",
  ],

  theme: {
    extend: {},
    fontFamily: {
      primary:
        'var(--family-primary, "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji")',
      secondary:
        'var(--family-secondary, "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji")',
      sans: [
        "Inter",
        "system-ui",
        "-apple-system",
        "BlinkMacSystemFont",
        '"Segoe UI"',
        "Roboto",
        '"Helvetica Neue"',
        "Arial",
        '"Noto Sans"',
        "sans-serif",
        '"Apple Color Emoji"',
        '"Segoe UI Emoji"',
        '"Segoe UI Symbol"',
        '"Noto Color Emoji"',
      ],
      serif: ["Georgia", "Cambria", '"Times New Roman"', "Times", "serif"],
      mono: [
        "Menlo",
        "Monaco",
        "Consolas",
        '"Liberation Mono"',
        '"Courier New"',
        "monospace",
      ],
    },
  },
  plugins: [
    /**
     * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
     * for forms. If you don't like it or have own styling for forms,
     * comment the line below to disable '@tailwindcss/forms'.
     */
    require("@tailwindcss/forms"),
    require("@tailwindcss/typography"),
    require("@tailwindcss/line-clamp"),
    require("@tailwindcss/aspect-ratio"),
    require("daisyui"),
  ],

  daisyui: {
    styled: true,
    themes: [
      {
        'abilian': {                          /* your theme name */
          'primary': colors.sky[400],           /* Primary color */
          'primary-focus': colors.sky[600],     /* Primary color - focused */
          'primary-content': '#ffffff',   /* Foreground content color to use on primary color */

          'secondary': colors.amber[400],         /* Secondary color */
          'secondary-focus': colors.amber[600],   /* Secondary color - focused */
          'secondary-content': '#ffffff', /* Foreground content color to use on secondary color */

          'accent': colors.teal[500],            /* Accent color */
          'accent-focus': colors.teal[700],      /* Accent color - focused */
          'accent-content': '#ffffff',    /* Foreground content color to use on accent color */

          'neutral': colors.zinc[500],           /* Neutral color */
          'neutral-focus': colors.zinc[700],     /* Neutral color - focused */
          'neutral-content': '#ffffff',   /* Foreground content color to use on neutral color */

          'base-100': '#ffffff',          /* Base color of page, used for blank backgrounds */
          'base-200': '#f9fafb',          /* Base color, a little darker */
          'base-300': '#d1d5db',          /* Base color, even more darker */
          'base-content': '#1f2937',      /* Foreground content color to use on base color */

          // 'info': '#2094f3',              /* Info */
          // 'success': '#009485',           /* Success */
          // 'warning': '#ff9900',           /* Warning */
          // 'error': '#ff5724',             /* Error */

          'info': colors.blue[600],
          'success': colors.green[600],
          'warning': colors.orange[600],
          'error': colors.red[600],
        },
      },
    ],
  },
};

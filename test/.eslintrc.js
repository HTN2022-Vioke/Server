module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint'],
  rules: {
    'operator-linebreak': [2, 'before'],
    quotes: [2, 'single', 'avoid-escape'],
  },
};

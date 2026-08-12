// design-scope final variant — shared theme toggle
function toggleTheme() {
  const dark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.documentElement.setAttribute('data-theme', dark ? 'light' : 'dark');
  document.querySelectorAll('.theme-btn').forEach(b => { b.textContent = dark ? 'dark' : 'light'; });
}
// persist
(function () {
  const saved = localStorage.getItem('ds-theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
  window.addEventListener('storage', () => {
    const t = localStorage.getItem('ds-theme');
    if (t) document.documentElement.setAttribute('data-theme', t);
  });
})();
function setTheme(t) { document.documentElement.setAttribute('data-theme', t); localStorage.setItem('ds-theme', t); }

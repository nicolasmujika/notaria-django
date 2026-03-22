(function () {
  const btn = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');

  if (btn && menu) {
    btn.addEventListener('click', () => {
      const expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      menu.classList.toggle('show');
    });
  }

  const toggles = document.querySelectorAll('.nav-toggle');

  function closeAll() {
    document.querySelectorAll('.submenu').forEach((u) => u.classList.remove('open'));
    document.querySelectorAll('.nav-toggle').forEach((t) => t.setAttribute('aria-expanded', 'false'));
    document.querySelectorAll('.nav-toggle .caret').forEach((c) => {
      c.style.transform = '';
    });
  }

  toggles.forEach((t) => {
    t.addEventListener('click', (e) => {
      e.preventDefault();
      const id = t.dataset.target;
      const sub = document.getElementById(id);
      if (!sub) return;

      const open = sub.classList.contains('open');
      closeAll();

      if (!open) {
        sub.classList.add('open');
        t.setAttribute('aria-expanded', 'true');
        const c = t.querySelector('.caret');
        if (c) c.style.transform = 'rotate(180deg)';
      }
    });
  });

  document.addEventListener('click', (e) => {
    const inside = e.target.closest('.nav-item');
    if (!inside) closeAll();
  });
})();
// Kai download site: download links, hero island loop, live clock, reveal on scroll.
(() => {
  const url = window.DOWNLOAD_URL;
  document.querySelectorAll('[data-download]').forEach((link) => {
    link.href = url;
    link.setAttribute('download', '');
  });

  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const island = document.querySelector('.island');
  const time = document.querySelector('.face-clock .time');
  const date = document.querySelector('.face-clock span');
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  function tick() {
    const now = new Date();
    time.textContent = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    date.innerHTML = `<small>${days[now.getDay()]}</small>${now.getDate()} ${months[now.getMonth()]}`;
  }
  tick();
  setInterval(tick, 15000);

  const labels = {
    pill: 'Kai island resting as a small pill',
    clock: 'Kai island showing the time',
    media: 'Kai island playing music',
    toast: 'Kai island offering to open a copied link',
  };
  if (!reduce) {
    const order = ['pill', 'clock', 'media', 'toast'];
    let index = 1;
    setInterval(() => {
      if (document.hidden) return;
      index = (index + 1) % order.length;
      island.dataset.state = order[index];
      island.setAttribute('aria-label', labels[order[index]]);
    }, 3200);
  }

  const items = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach((item) => item.classList.add('in'));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  items.forEach((item) => observer.observe(item));
})();

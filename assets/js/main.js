/* ============================================================
   DIRTYGEN · «Я не в сети» — интерактив сайта
   помехи / смена канала / визуализатор / синхро-текст
   ============================================================ */
(() => {
'use strict';

/* ---------- данные: главы клипа ---------- */
const CHAPTERS = [
  { t: 0,   label: 'Интро',            f: '01' },
  { t: 20,  label: 'Куплет 1',         f: '04' },
  { t: 50,  label: 'Пре-дроп',         f: '08' },
  { t: 60,  label: 'Дроп · Смени канал', f: '10' },
  { t: 75,  label: 'Куплет 2',         f: '14' },
  { t: 105, label: 'Брейк',            f: '18' },
  { t: 120, label: 'Билд-ап',          f: '20' },
  { t: 140, label: 'Финальный дроп',   f: '23' },
  { t: 165, label: 'Аутро',            f: '27' },
  { t: 181, label: 'Титры',            f: '24' },
];

/* ---------- данные: текст с таймингами ---------- */
const LYRICS = [
  { s: 'Интро' },
  { t: 0.5,   x: '— Замечал, что одни постоянно жалуются на жизнь?' },
  { t: 4.2,   x: '— А другие? — Другие тоже. Просто не тратят на это всё время.' },
  { t: 8.5,   x: '— То есть всё зависит от мышления?' },
  { t: 11.5,  x: '— Не совсем. Ещё от того, что ты с ним делаешь.' },
  { s: 'Куплет 1' },
  { t: 20.5,  x: 'Утро, город, знакомый маршрут.' },
  { t: 24.0,  x: 'Все куда-то спешат, что-то ждут.' },
  { t: 27.5,  x: 'Кто-то снова винит обстоятельства,' },
  { t: 31.0,  x: 'Кто-то ищет другие возможности.' },
  { t: 34.5,  x: 'Можно годами доказывать всем,' },
  { t: 38.0,  x: 'Что вокруг виноваты не те и не те.' },
  { t: 41.5,  x: 'А можно однажды признать без прикрас:' },
  { t: 45.0,  x: 'Не всё в этом мире зависит от нас.' },
  { s: 'Пре-дроп' },
  { t: 50.6,  x: 'Тот же город.' },
  { t: 52.8,  x: 'Тот же свет.' },
  { t: 55.0,  x: 'Только разных' },
  { t: 57.2,  x: 'взглядов не счесть.' },
  { s: 'Дроп — Смени канал' },
  { t: 60.4,  x: 'СМЕНИ КАНАЛ.' },
  { t: 62.0,  x: 'ВЗГЛЯНИ ИНАЧЕ.' },
  { t: 63.8,  x: 'МИР НЕ ИЗМЕНИЛСЯ —' },
  { t: 65.2,  x: 'ТЫ СМОТРИШЬ ИНАЧЕ.' },
  { t: 67.5,  x: 'СМЕНИ КАНАЛ.' },
  { t: 69.1,  x: 'НЕ ЖДИ ЗНАКА СВЫШЕ.' },
  { t: 70.9,  x: 'ИНОГДА ДОСТАТОЧНО' },
  { t: 72.5,  x: 'СДЕЛАТЬ ШАГ ПОБЛИЖЕ.' },
  { s: 'Куплет 2' },
  { t: 75.5,  x: 'У каждого свой угол зрения,' },
  { t: 79.0,  x: 'Свои объяснения и сомнения.' },
  { t: 82.5,  x: 'Мы часто уверены, что всё поняли,' },
  { t: 86.0,  x: 'Пока не увидели то, чего не заметили.' },
  { t: 89.5,  x: 'У каждого правда — своя высота,' },
  { t: 93.0,  x: 'Свои повороты, свои тупики.' },
  { t: 96.5,  x: 'Но если уверен, что прав только ты,' },
  { t: 100.0, x: 'То как ты заметишь другие пути?' },
  { s: 'Брейк' },
  { t: 105.8, x: '— Ну что, решил изменить свою жизнь?' },
  { t: 108.6, x: '— Да, начал с чистого листа.' },
  { t: 111.2, x: '— И как успехи?' },
  { t: 113.0, x: '— Поменял обои на телефоне.' },
  { t: 115.6, x: '— Впечатляет.' },
  { t: 117.4, x: '— Не торопи события.' },
  { s: 'Билд-ап' },
  { t: 120.5, x: 'Не всё нам подвластно.' },
  { t: 122.7, x: 'Не всё решено.' },
  { t: 124.9, x: 'И всё же не всё' },
  { t: 127.1, x: 'Предрешено.' },
  { t: 130.0, x: 'Между тем, что случилось,' },
  { t: 133.0, x: 'И тем, что придёт,' },
  { t: 136.0, x: 'Есть короткое место.' },
  { t: 138.2, x: 'Оно называется — выбор.' },
  { s: 'Финальный дроп' },
  { t: 140.5, x: 'СМЕНИ КАНАЛ.' },
  { t: 142.3, x: 'ВЗГЛЯНИ ИНАЧЕ.' },
  { t: 144.0, x: 'МИР НЕ ИЗМЕНИЛСЯ —' },
  { t: 145.7, x: 'ТЫ СМОТРИШЬ ИНАЧЕ.' },
  { t: 148.0, x: 'СМЕНИ КАНАЛ.' },
  { t: 149.8, x: 'ПУСТЬ МЕНЯЕТСЯ ЗВУК.' },
  { t: 151.6, x: 'ИНОГДА НОВЫЙ ВЗГЛЯД —' },
  { t: 153.6, x: 'ЭТО ВЫХОД ИЗ КРУГА.' },
  { s: 'Аутро' },
  { t: 166.0, x: 'Мир не обязан быть таким,' },
  { t: 169.5, x: 'как тебе хотелось.' },
  { t: 173.0, x: 'Но и твой взгляд на него —' },
  { t: 176.5, x: 'не последняя инстанция.' },
  { t: 180.5, x: 'Грязный Гена.' },
  { t: 182.5, x: 'Связи нет. Бас есть.' },
];

const $  = (s, p = document) => p.querySelector(s);
const $$ = (s, p = document) => [...p.querySelectorAll(s)];
const fmt = t => `${Math.floor(t / 60)}:${String(Math.floor(t % 60)).padStart(2, '0')}`;

/* ============================================================
   1. TV-ПОМЕХИ ПРИ ЗАГРУЗКЕ
   ============================================================ */
const introCv = $('#staticIntro');
const ictx = introCv.getContext('2d');
const IW = 220, IH = 124;
introCv.width = IW; introCv.height = IH;
let introStart = performance.now();

function noiseFrame(ctx, w, h, alpha = 1) {
  const img = ctx.createImageData(w, h);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    const v = (Math.random() * 255) | 0;
    d[i] = d[i + 1] = d[i + 2] = v;
    d[i + 3] = 255 * alpha;
  }
  ctx.putImageData(img, 0, 0);
}

(function introLoop(now) {
  const el = now - introStart;
  if (el < 1050) {
    noiseFrame(ictx, IW, IH);
    requestAnimationFrame(introLoop);
  } else {
    introCv.style.opacity = '0';
    setTimeout(() => introCv.remove(), 600);
  }
})(introStart);

/* ============================================================
   2. СМЕНИ КАНАЛ (переключение темы)
   ============================================================ */
const flashCv = $('#flash');
flashCv.width = IW; flashCv.height = IH;
const fctx = flashCv.getContext('2d');
let flashing = false;

function staticFlash(dur = 380) {
  if (flashing) return;
  flashing = true;
  const t0 = performance.now();
  flashCv.style.opacity = '1';
  (function loop(now) {
    if (now - t0 < dur) {
      noiseFrame(fctx, IW, IH);
      requestAnimationFrame(loop);
    } else {
      flashCv.style.opacity = '0';
      flashing = false;
    }
  })(t0);
}

const root = document.documentElement;
const chBtn = $('#chSwitch');
const tvMode = $('#tvMode');

function applyTheme(th, withFlash) {
  if (withFlash) staticFlash();
  setTimeout(() => {
    root.dataset.theme = th;
    const meta = $('meta[name="theme-color"]');
    if (meta) meta.content = th === 'dark' ? '#05060a' : '#f6efe2';
    if (tvMode) tvMode.textContent = th === 'dark' ? 'NO SIGNAL / БАС ЕСТЬ' : 'CH 02 / РАССВЕТ';
    try { localStorage.setItem('dg-theme', th); } catch (e) {}
  }, withFlash ? 120 : 0);
}

/* восстановление темы */
try {
  const saved = localStorage.getItem('dg-theme');
  if (saved && saved !== root.dataset.theme) applyTheme(saved, false);
} catch (e) {}

chBtn.addEventListener('click', () => {
  applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true);
});

/* ============================================================
   3. ПЛЕЕР + ВИЗУАЛИЗАТОР
   ============================================================ */
const video = $('#player');
const bigPlay = $('#bigPlay');
const viz = $('#viz');
const vctx = viz.getContext('2d');
let audioCtx = null, analyser = null, dataArr = null, rafId = null;

function sizeViz() {
  viz.width = viz.clientWidth * devicePixelRatio;
  viz.height = 150 * devicePixelRatio;
}
addEventListener('resize', sizeViz);
sizeViz();

function initAudio() {
  if (audioCtx) return;
  try {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const src = audioCtx.createMediaElementSource(video);
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.82;
    src.connect(analyser);
    analyser.connect(audioCtx.destination);
    dataArr = new Uint8Array(analyser.frequencyBinCount);
  } catch (e) { /* визуализатор недоступен — не беда */ }
}

function cssVar(n) {
  return getComputedStyle(root).getPropertyValue(n).trim();
}

function drawViz() {
  rafId = requestAnimationFrame(drawViz);
  if (!analyser) return;
  analyser.getByteFrequencyData(dataArr);
  const W = viz.width, H = viz.height;
  vctx.clearRect(0, 0, W, H);

  const bars = 56;
  const gap = 2 * devicePixelRatio;
  const bw = (W - gap * (bars - 1)) / bars;
  const c1 = cssVar('--acc') || '#00e5ff';
  const c2 = cssVar('--acc2') || '#ff2bd6';

  const grad = vctx.createLinearGradient(0, H, 0, 0);
  grad.addColorStop(0, c1);
  grad.addColorStop(1, c2);
  vctx.fillStyle = grad;
  vctx.shadowColor = c1;
  vctx.shadowBlur = 12 * devicePixelRatio;

  for (let i = 0; i < bars; i++) {
    const idx = Math.floor(Math.pow(i / bars, 1.6) * (dataArr.length * 0.72));
    const v = dataArr[idx] / 255;
    const h = Math.max(2 * devicePixelRatio, v * H * 0.92);
    const x = i * (bw + gap);
    /* основной столбик */
    vctx.globalAlpha = 0.92;
    vctx.fillRect(x, H - h, bw, h);
    /* отражение */
    vctx.globalAlpha = 0.16;
    vctx.fillRect(x, H, bw, h * 0.34);
  }
  vctx.globalAlpha = 1;
  vctx.shadowBlur = 0;
}

bigPlay.addEventListener('click', () => {
  initAudio();
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
  video.play();
});
video.addEventListener('play', () => {
  bigPlay.classList.add('hide');
  if (!rafId) drawViz();
});
video.addEventListener('pause', () => {
  if (video.ended) bigPlay.classList.remove('hide');
});

/* ============================================================
   4. ГЛАВЫ (чипы + сетка сцен)
   ============================================================ */
const chaptersRow = $('#chapters');
const sceneGrid = $('#sceneGrid');

CHAPTERS.forEach((c, i) => {
  /* чип */
  const b = document.createElement('button');
  b.className = 'ch';
  b.role = 'tab';
  b.innerHTML = `<b>${fmt(c.t)}</b>${c.label}`;
  b.addEventListener('click', () => seekTo(c.t));
  chaptersRow.appendChild(b);
  /* карточка сцены */
  const card = document.createElement('div');
  card.className = 'scene';
  card.innerHTML = `
    <img src="assets/frames_web/${c.f}.jpg" alt="${c.label}" loading="lazy">
    <div class="sc-meta"><b>${c.label}</b><span>${fmt(c.t)}</span></div>`;
  card.addEventListener('click', () => {
    seekTo(c.t);
    $('#clip').scrollIntoView({ behavior: 'smooth' });
  });
  sceneGrid.appendChild(card);
});

function seekTo(t) {
  initAudio();
  video.currentTime = t;
  video.play().catch(() => {});
  if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
}

function setActiveChapter(t) {
  let idx = 0;
  CHAPTERS.forEach((c, i) => { if (t >= c.t) idx = i; });
  $$('.ch').forEach((el, i) => el.classList.toggle('active', i === idx));
}

/* ============================================================
   5. СИНХРОННЫЙ ТЕКСТ
   ============================================================ */
const termBody = $('#termBody');
const lineEls = [];

LYRICS.forEach(item => {
  if (item.s) {
    const h = document.createElement('div');
    h.className = 'lyr-sec';
    h.textContent = `[ ${item.s} ]`;
    termBody.appendChild(h);
    lineEls.push(null);
  } else {
    const p = document.createElement('span');
    p.className = 'lyr';
    p.textContent = item.x;
    termBody.appendChild(p);
    lineEls.push(p);
  }
});

function setActiveLyric(t) {
  let idx = -1;
  LYRICS.forEach((l, i) => { if (l.t !== undefined && t >= l.t - 0.15) idx = i; });
  lineEls.forEach((el, i) => {
    if (!el) return;
    const on = i === idx;
    if (on && !el.classList.contains('on')) {
      el.classList.add('on');
      const bodyRect = termBody.getBoundingClientRect();
      const elRect = el.getBoundingClientRect();
      const target = termBody.scrollTop + (elRect.top - bodyRect.top) - bodyRect.height / 2 + elRect.height;
      termBody.scrollTo({ top: target, behavior: 'smooth' });
    } else if (!on && el.classList.contains('on')) {
      el.classList.remove('on');
    }
  });
}

video.addEventListener('timeupdate', () => {
  setActiveChapter(video.currentTime);
  setActiveLyric(video.currentTime);
});
video.addEventListener('seeked', () => {
  setActiveChapter(video.currentTime);
  setActiveLyric(video.currentTime);
});

/* ============================================================
   6. КЛАВИАТУРА
   ============================================================ */
addEventListener('keydown', e => {
  if (e.target.matches('input,textarea')) return;
  if (e.code === 'KeyK') {
    chBtn.click();
  } else if (e.code === 'Space' && $('#clip').getBoundingClientRect().top < innerHeight * 0.7) {
    e.preventDefault();
    initAudio();
    if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
    video.paused ? video.play() : video.pause();
  } else if (e.code === 'ArrowRight') {
    video.currentTime = Math.min(video.currentTime + 5, video.duration || 187);
  } else if (e.code === 'ArrowLeft') {
    video.currentTime = Math.max(video.currentTime - 5, 0);
  }
});

/* ============================================================
   7. ПОЯВЛЕНИЕ ПРИ СКРОЛЛЕ
   ============================================================ */
const io = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('on'); io.unobserve(en.target); }
  });
}, { threshold: 0.12 });
$$('.reveal').forEach(el => io.observe(el));

/* первая глава активна сразу */
setActiveChapter(0);

})();

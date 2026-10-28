/* ============================================================
   DIRTYGEN·ТВ — сайт-телевизор
   Прокрутка = смена канала через вспышку помех.
   CH 01 герой · CH 02-04 клипы · CH 05 музыкант
   ============================================================ */
(() => {
'use strict';

/* ---------- текст «Я не в сети» (тайминги под оригинальный трек 3:05.6) ---------- */
const LYRICS = [
  { t: 0.4,  x: '— Замечал, что одни постоянно жалуются на жизнь?' },
  { t: 4.3,  x: '— А другие? — Другие тоже. Просто не тратят на это всё время.' },
  { t: 8.6,  x: '— То есть всё зависит от мышления?' },
  { t: 12.2, x: '— Не совсем. Ещё от того, что ты с ним делаешь.' },
  { t: 16.5, x: 'Утро, город, знакомый маршрут.' },
  { t: 20.2, x: 'Все куда-то спешат, что-то ждут.' },
  { t: 23.9, x: 'Кто-то снова винит обстоятельства,' },
  { t: 27.6, x: 'Кто-то ищет другие возможности.' },
  { t: 31.3, x: 'Можно годами доказывать всем,' },
  { t: 35.0, x: 'Что вокруг виноваты не те и не те.' },
  { t: 38.7, x: 'А можно однажды признать без прикрас:' },
  { t: 42.4, x: 'Не всё в этом мире зависит от нас.' },
  { t: 46.4, x: 'Тот же город.' },
  { t: 47.9, x: 'Тот же свет.' },
  { t: 49.4, x: 'Только разных' },
  { t: 50.8, x: 'взглядов не счесть.' },
  { t: 52.5, x: 'СМЕНИ КАНАЛ.' },
  { t: 55.5, x: 'ВЗГЛЯНИ ИНАЧЕ.' },
  { t: 58.5, x: 'МИР НЕ ИЗМЕНИЛСЯ —' },
  { t: 61.5, x: 'ТЫ СМОТРИШЬ ИНАЧЕ.' },
  { t: 64.5, x: 'СМЕНИ КАНАЛ.' },
  { t: 67.5, x: 'НЕ ЖДИ ЗНАКА СВЫШЕ.' },
  { t: 70.5, x: 'ИНОГДА ДОСТАТОЧНО' },
  { t: 73.5, x: 'СДЕЛАТЬ ШАГ ПОБЛИЖЕ.' },
  { t: 82.5, x: 'У каждого свой угол зрения,' },
  { t: 87.0, x: 'Свои объяснения и сомнения.' },
  { t: 91.5, x: 'Мы часто уверены, что всё поняли,' },
  { t: 96.0, x: 'Пока не увидели то, чего не заметили.' },
  { t: 100.5, x: 'У каждого правда — своя высота,' },
  { t: 105.0, x: 'Свои повороты, свои тупики.' },
  { t: 109.5, x: 'Но если уверен, что прав только ты,' },
  { t: 114.0, x: 'То как ты заметишь другие пути?' },
  { t: 118.5, x: '— Ну что, решил изменить свою жизнь?' },
  { t: 121.3, x: '— Да, начал с чистого листа.' },
  { t: 124.1, x: '— И как успехи?' },
  { t: 126.4, x: '— Поменял обои на телефоне.' },
  { t: 129.2, x: '— Впечатляет.' },
  { t: 132.0, x: '— Не торопи события.' },
  { t: 135.5, x: 'Не всё нам подвластно.' },
  { t: 138.1, x: 'Не всё решено.' },
  { t: 140.7, x: 'И всё же не всё' },
  { t: 143.3, x: 'Предрешено.' },
  { t: 145.9, x: 'Между тем, что случилось,' },
  { t: 149.0, x: 'И тем, что придёт,' },
  { t: 152.1, x: 'Есть короткое место.' },
  { t: 154.2, x: 'Оно называется — выбор.' },
  { t: 156.5, x: 'СМЕНИ КАНАЛ.' },
  { t: 159.1, x: 'ВЗГЛЯНИ ИНАЧЕ.' },
  { t: 161.7, x: 'МИР НЕ ИЗМЕНИЛСЯ —' },
  { t: 164.3, x: 'ТЫ СМОТРИШЬ ИНАЧЕ.' },
  { t: 168.2, x: 'СМЕНИ КАНАЛ.' },
  { t: 170.8, x: 'ПУСТЬ МЕНЯЕТСЯ ЗВУК.' },
  { t: 173.4, x: 'ИНОГДА НОВЫЙ ВЗГЛЯД —' },
  { t: 176.0, x: 'ЭТО ВЫХОД ИЗ КРУГА.' },
  { t: 178.5, x: 'Мир не обязан быть таким,' },
  { t: 180.6, x: 'как тебе хотелось.' },
  { t: 182.7, x: 'Но и твой взгляд на него —' },
  { t: 184.4, x: 'не последняя инстанция.' },
];

const $  = (s, p = document) => p.querySelector(s);
const $$ = (s, p = document) => [...p.querySelectorAll(s)];

const channels = $$('.channel');
const N = channels.length;
let cur = 0, animating = false;

/* ============================================================
   ПОМЕХИ (переход между каналами)
   ============================================================ */
const cv = $('#tvNoise');
const NW = 200, NH = 112;
cv.width = NW; cv.height = NH;
const nx = cv.getContext('2d');

function drawNoise() {
  const img = nx.createImageData(NW, NH);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    const v = (Math.random() * 255) | 0;
    d[i] = d[i+1] = d[i+2] = v;
    d[i+3] = 255;
  }
  nx.putImageData(img, 0, 0);
  // горизонтальная полоса-срыв
  if (Math.random() < 0.7) {
    const y = (Math.random() * NH) | 0;
    const h = 2 + ((Math.random() * 6) | 0);
    nx.fillStyle = 'rgba(255,255,255,.25)';
    nx.fillRect(0, y, NW, h);
  }
}

/* щелчок помех через WebAudio */
let actx = null;
function ensureAudio() {
  if (!actx) {
    try { actx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {}
  }
  if (actx && actx.state === 'suspended') actx.resume().catch(() => {});
}
function staticClick() {
  if (!actx) return;
  try {
    const len = Math.floor(actx.sampleRate * 0.12);
    const buf = actx.createBuffer(1, len, actx.sampleRate);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < len; i++) ch[i] = (Math.random() * 2 - 1) * Math.exp(-i / (len / 3));
    const src = actx.createBufferSource();
    src.buffer = buf;
    const g = actx.createGain();
    g.gain.value = 0.10;
    src.connect(g); g.connect(actx.destination);
    src.start();
  } catch (e) {}
}

let noiseRAF = null;
function staticBurst(dur = 430) {
  const t0 = performance.now();
  cv.style.opacity = '1';
  staticClick();
  cancelAnimationFrame(noiseRAF);
  (function loop(now) {
    if (now - t0 < dur) {
      drawNoise();
      noiseRAF = requestAnimationFrame(loop);
    } else {
      cv.style.opacity = '0';
    }
  })(t0);
}

/* ---------- OSD номера канала ---------- */
const osd = document.createElement('div');
osd.className = 'ch-osd';
document.body.appendChild(osd);
let osdT = null;
function showOSD(text) {
  osd.textContent = text;
  osd.classList.add('show');
  clearTimeout(osdT);
  osdT = setTimeout(() => osd.classList.remove('show'), 1500);
}

/* ============================================================
   ПЕРЕКЛЮЧЕНИЕ КАНАЛОВ
   ============================================================ */
const hudName = $('#hudName');
const dotsBox = $('#dots');
const hint = $('#scrollHint');

const CH_LABELS = ['CH 01', 'CH 02', 'CH 03', 'CH 04', 'CH 05'];
channels.forEach((ch, i) => {
  const d = document.createElement('button');
  d.className = 'dot' + (i === 0 ? ' on' : '');
  d.dataset.label = CH_LABELS[i];
  d.setAttribute('aria-label', ch.dataset.name);
  d.addEventListener('click', () => go(i));
  dotsBox.appendChild(d);
});
const dots = $$('.dot', dotsBox);

function pauseAllVideos() {
  $$('video').forEach(v => v.pause());
}
function resetPlays() {
  $$('.big-play').forEach(b => b.classList.remove('hide'));
}

function go(n) {
  n = Math.max(0, Math.min(N - 1, n));
  if (animating || n === cur) return;
  animating = true;
  ensureAudio();
  staticBurst();
  setTimeout(() => {
    pauseAllVideos();
    channels[cur].classList.remove('active');
    channels[n].classList.add('active');
    const artist = channels[n].querySelector('.artist-scroll');
    if (artist) artist.scrollTop = 0;
    cur = n;
    hudName.textContent = channels[n].dataset.name;
    dots.forEach((d, i) => d.classList.toggle('on', i === cur));
    showOSD(CH_LABELS[cur]);
    if (cur > 0) hint.classList.add('hide'); else hint.classList.remove('hide');
    setTimeout(() => { animating = false; }, 160);
  }, 230);
}

/* ============================================================
   ВВОД: колесо / свайп / клавиатура
   ============================================================ */
let acc = 0, accT = null;

addEventListener('wheel', e => {
  ensureAudio();
  const sc = e.target.closest && e.target.closest('.artist-scroll');
  if (sc) {
    const canDown = sc.scrollTop + sc.clientHeight < sc.scrollHeight - 6;
    const canUp = sc.scrollTop > 6;
    if ((e.deltaY > 0 && canDown) || (e.deltaY < 0 && canUp)) return;
  }
  acc += e.deltaY;
  clearTimeout(accT);
  accT = setTimeout(() => { acc = 0; }, 220);
  if (Math.abs(acc) > 70) {
    go(cur + (acc > 0 ? 1 : -1));
    acc = 0;
  }
}, { passive: true });

let tY = null;
addEventListener('touchstart', e => { tY = e.touches[0].clientY; ensureAudio(); }, { passive: true });
addEventListener('touchend', e => {
  if (tY === null) return;
  const d = tY - e.changedTouches[0].clientY;
  if (Math.abs(d) > 60) go(cur + (d > 0 ? 1 : -1));
  tY = null;
}, { passive: true });

addEventListener('keydown', e => {
  if (e.target.matches('input,textarea')) return;
  ensureAudio();
  switch (e.code) {
    case 'ArrowDown': case 'PageDown': go(cur + 1); break;
    case 'ArrowUp': case 'PageUp': go(cur - 1); break;
    case 'Home': go(0); break;
    case 'End': go(N - 1); break;
    case 'KeyK': themeBtn.click(); break;
    case 'KeyT': lyrBtn.click(); break;
    case 'Space': {
      const v = channels[cur].querySelector('video');
      if (v) { e.preventDefault(); v.paused ? v.play() : v.pause(); }
      break;
    }
  }
});

/* кнопки-ссылки data-go */
$$('[data-go]').forEach(b => b.addEventListener('click', () => {
  const n = +b.dataset.go;
  go(n);
  const v = channels[n].querySelector('video');
  if (v) setTimeout(() => v.play().catch(() => {}), 500);
}));

/* ============================================================
   ВИДЕО
   ============================================================ */
$$('.big-play').forEach(b => {
  b.addEventListener('click', () => {
    const v = $('#' + b.dataset.play);
    ensureAudio();
    v.play().catch(() => {});
  });
});
$$('video').forEach(v => {
  v.addEventListener('play', () => {
    v.closest('.channel').querySelector('.big-play').classList.add('hide');
  });
  v.addEventListener('pause', () => {
    v.closest('.channel').querySelector('.big-play').classList.remove('hide');
  });
});

/* ============================================================
   ТЕКСТ ПЕСНИ (CH 02)
   ============================================================ */
const vid1 = $('#vid1');
const lyrOv = $('#lyrOv');
const lyrBtn = $('#lyrBtn');
let lyrOn = false;

lyrBtn.addEventListener('click', () => {
  lyrOn = !lyrOn;
  lyrBtn.textContent = lyrOn ? 'ТЕКСТ: ВКЛ' : 'ТЕКСТ: ВЫКЛ';
  lyrBtn.classList.toggle('on', lyrOn);
  lyrOv.classList.toggle('on', lyrOn);
  if (!lyrOn) lyrOv.innerHTML = '';
});

vid1.addEventListener('timeupdate', () => {
  if (!lyrOn) return;
  let idx = -1;
  for (let i = 0; i < LYRICS.length; i++) {
    if (vid1.currentTime >= LYRICS[i].t - 0.12) idx = i; else break;
  }
  const line = idx >= 0 ? LYRICS[idx].x : '';
  if (lyrOv.dataset.idx !== String(idx)) {
    lyrOv.dataset.idx = String(idx);
    lyrOv.innerHTML = line ? `<span>${line}</span>` : '';
  }
});

/* ============================================================
   ТЕМА (тьма ↔ рассвет)
   ============================================================ */
const themeBtn = $('#themeBtn');
const root = document.documentElement;

function applyTheme(th, flash) {
  if (flash) staticBurst(360);
  setTimeout(() => {
    root.dataset.theme = th;
    const meta = $('meta[name="theme-color"]');
    if (meta) meta.content = th === 'dark' ? '#05060a' : '#f6efe2';
    try { localStorage.setItem('dg-theme', th); } catch (e) {}
  }, flash ? 110 : 0);
}
try {
  const saved = localStorage.getItem('dg-theme');
  if (saved && saved !== root.dataset.theme) applyTheme(saved, false);
} catch (e) {}
themeBtn.addEventListener('click', () => {
  applyTheme(root.dataset.theme === 'dark' ? 'light' : 'dark', true);
});

/* приветственный OSD */
showOSD('CH 01');

})();

/* DIRTYGEN — переключение каналов */
(function () {
  "use strict";

  const CHANNELS = [
    { num: "CH 01", name: "СМЕНИ КАНАЛ", file: "video/ch1_main.mp4" },
    { num: "CH 02", name: "СМЕНИ КАНАЛ · NIGHT", file: "video/ch2_night.mp4" },
    { num: "CH 03", name: "СМЕНИ КАНАЛ · DAWN", file: "video/ch3_dawn.mp4" },
    { num: "", name: "ГРЯЗНЫЙ ГЕНА", file: null },
  ];
  const ARTIST = 3; // индекс страницы артиста

  const $ = (s) => document.querySelector(s);
  const power = $("#power");
  const sections = document.querySelectorAll(".channel");
  const videos = document.querySelectorAll(".channel video");
  const staticCv = $("#static");
  const osdCh = $("#osdCh"), osdBrand = $("#osdBrand");
  const chMenu = $("#chMenu");
  const splash = $("#chSplash"), splashNum = $("#splashNum"), splashName = $("#splashName");
  const endCard = $("#endCard");

  let cur = -1;
  let powered = false;
  let lastSwitch = 0;
  let audioCtx = null;
  let soundRetry = false;
  let userPaused = false; // пользователь поставил паузу тапом — не трогаем
  let playToken = 0;      // гасит висящие ретраи play() при переключении/паузе

  /* ---------- вспышка помех: буфер под пропорции экрана ---------- */
  /* одинаковые квадратные зёрна шума на любом экране (телефон/десктоп) */
  function staticSize() {
    const w = 240;
    const h = Math.max(120, Math.round((w * window.innerHeight) / Math.max(1, window.innerWidth)));
    staticCv.width = w;
    staticCv.height = h;
    return [w, h];
  }
  let SW = 0, SH = 0;
  function resizeStatic() { [SW, SH] = staticSize(); }
  resizeStatic();
  window.addEventListener("resize", resizeStatic);
  window.addEventListener("orientationchange", resizeStatic);
  const sctx = staticCv.getContext("2d");

  function noiseBurst(dur) {
    if (!audioCtx) return;
    try {
      const len = Math.floor(audioCtx.sampleRate * dur);
      const buf = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 1.6) * 0.22;
      const src = audioCtx.createBufferSource();
      src.buffer = buf;
      src.connect(audioCtx.destination);
      src.start();
    } catch (e) { /* noop */ }
  }

  function staticFlash(dur) {
    if (dur == null) dur = 420;
    const t0 = performance.now();
    staticCv.style.opacity = "1";
    noiseBurst(dur / 1000);
    (function draw() {
      const t = (performance.now() - t0) / dur;
      if (t >= 1) { staticCv.style.opacity = "0"; return; }
      const img = sctx.createImageData(SW, SH);
      const d = img.data;
      for (let i = 0; i < d.length; i += 4) {
        const v = (Math.random() * 255) | 0;
        d[i] = v; d[i + 1] = v; d[i + 2] = v; d[i + 3] = 255;
      }
      sctx.putImageData(img, 0, 0);
      // полосы сдвига — пропорциональны высоте буфера
      const bands = 4;
      for (let b = 0; b < bands; b++) {
        const y = (Math.random() * SH) | 0;
        const h = Math.max(2, Math.round(SH * (0.02 + Math.random() * 0.1)));
        const dx = ((Math.random() - 0.5) * SW * 0.18) | 0;
        if (dx === 0) continue;
        const strip = sctx.getImageData(0, y, SW, Math.min(h, SH - y));
        sctx.putImageData(strip, dx, y);
      }
      if (Math.random() < 0.3) {
        sctx.fillStyle = "rgba(255,255,255," + (0.06 + Math.random() * 0.1) + ")";
        sctx.fillRect(0, Math.random() * SH, SW, 1 + Math.random() * 2);
      }
      requestAnimationFrame(draw);
    })();
  }

  /* ---------- запуск видео: ретраи, пока клип не пойдёт ---------- */
  /* AbortError (медиа ещё грузится — тяжёлый файл) лечится повтором с задержкой,
     NotAllowedError (жёсткая политика автоплея) — тихий старт, звук вернётся
     первым тапом (retrySound). Клип на открытом канале не должен «зависать» */
  function startVideo(v) {
    const tok = ++playToken;
    const attempt = (n) => {
      if (tok !== playToken || v.paused === false) return; // уже играем или ушли дальше
      v.muted = false;
      const p = v.play();
      if (p && p.then) {
        p.then(() => { if (tok === playToken) soundRetry = false; })
         .catch((err) => {
           if (tok !== playToken) return;
           const name = (err && err.name) || "";
           if (name === "NotAllowedError") {
             v.muted = true;
             const p2 = v.play();
             if (p2 && p2.catch) p2.catch(() => {});
             soundRetry = true;
             return;
           }
           if (n < 40) setTimeout(() => attempt(n + 1), 450);
         });
      }
    };
    attempt(0);
  }

  /* ---------- переключение каналов ---------- */
  function label(i) {
    return CHANNELS[i].num ? CHANNELS[i].num + " / 03" : CHANNELS[i].name;
  }

  function showSplash(i) {
    const hasNum = !!CHANNELS[i].num;
    splashNum.textContent = hasNum ? CHANNELS[i].num : "";
    splashNum.style.display = hasNum ? "" : "none";
    splashName.textContent = CHANNELS[i].name;
    splash.classList.remove("show");
    void splash.offsetWidth; // reflow
    splash.classList.add("show");
  }

  function switchTo(i, silent) {
    i = ((i % CHANNELS.length) + CHANNELS.length) % CHANNELS.length;
    if (i === cur && powered) return;
    lastSwitch = performance.now();
    userPaused = false; // сменили канал — снова хотим играть
    hidePauseBadge();
    const prevVideo = videos[cur];
    if (prevVideo && !prevVideo.paused) { prevVideo.pause(); }

    cur = i;
    sections.forEach((s, k) => s.classList.toggle("active", k === cur));

    const isVideo = !!CHANNELS[cur].file;
    osdCh.textContent = label(cur);
    endCard.classList.remove("show");
    closeMenu();

    if (!silent) staticFlash();
    showSplash(cur);

    if (isVideo) {
      const v = videos[cur];
      v.preload = "auto";
      if (v.ended) { v.currentTime = 0; } // возврат на канал — с начала
      startVideo(v);
      // прогреваем все видео-каналы
      for (let k = 0; k < CHANNELS.length; k++) {
        if (CHANNELS[k].file) videos[k].preload = "auto";
      }
    }
  }

  function next() { switchTo(cur + 1); }
  function prev() { switchTo(cur - 1); }

  /* ---------- тихий ретрай звука (без интерфейса) ---------- */
  function retrySound() {
    if (!soundRetry || !powered || userPaused) return;
    const v = videos[cur];
    if (!v || !CHANNELS[cur].file) return;
    v.muted = false;
    const p = v.play();
    if (p && p.catch) {
      p.then(() => { soundRetry = false; })
       .catch(() => { v.muted = true; v.play().catch(() => {}); });
    } else {
      soundRetry = false;
    }
  }
  ["click", "touchstart", "keydown"].forEach((ev) =>
    window.addEventListener(ev, retrySound, { passive: true })
  );

  /* ---------- запуск ---------- */
  function powerOn() {
    if (powered) return;
    powered = true;
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      audioCtx.resume();
    } catch (e) { /* noop */ }
    power.classList.add("off");
    document.body.classList.add("on");
    // разблокировка звука синхронно в жесте клика (autoplay policy)
    const v0 = videos[0];
    v0.muted = false;
    startVideo(v0);
    // тихий анлок остальных каналов В ТОМ ЖЕ ЖЕСТЕ: unmuted play при
    // volume=0 «благословляет» элемент — после этого звук разрешён и вне
    // жеста (переключение колесом/стрелками). iOS volume не меняет
    // (остаётся 1) — там пропускаем: свайп/клик сам является жестом.
    for (let k = 1; k < CHANNELS.length; k++) {
      if (!CHANNELS[k].file) continue;
      const u = videos[k];
      try {
        u.volume = 0;
        if (u.volume !== 0) continue; // iOS: тихий анлок недоступен
        u.muted = false;
        const p = u.play();
        if (p && p.then) {
          p.then(() => {
            if (videos[cur] !== u) { u.pause(); try { u.currentTime = 0; } catch (e) {} }
            try { u.volume = 1; } catch (e) {}
          }).catch(() => { try { u.volume = 1; } catch (e) {} });
        } else {
          u.pause(); try { u.volume = 1; } catch (e) {}
        }
      } catch (e) { /* noop */ }
    }
    // прогреваем все каналы для мобильных
    for (let k = 0; k < CHANNELS.length; k++) {
      if (CHANNELS[k].file) videos[k].preload = "auto";
    }
    staticFlash(650);
    setTimeout(() => switchTo(0, true), 260);
    setTimeout(() => { power.style.display = "none"; }, 500);
  }
  power.addEventListener("click", powerOn);

  /* ---------- события видео ---------- */
  videos.forEach((v) => {
    v.addEventListener("ended", () => {
      if (sections[cur].querySelector("video") !== v) return;
      endCard.classList.add("show");
    });
    // данные дошли — текущий канал обязан играть
    ["canplay", "loadeddata"].forEach((ev) =>
      v.addEventListener(ev, () => {
        if (!powered || userPaused || v.ended) return;
        if (videos[cur] !== v) return;
        if (v.paused) startVideo(v);
      })
    );
  });

  /* сторож: канал открыт и не на паузе — клип должен идти */
  setInterval(() => {
    if (!powered || userPaused) return;
    const v = videos[cur];
    if (!v || !CHANNELS[cur] || !CHANNELS[cur].file || v.ended) return;
    if (v.paused) startVideo(v);
  }, 900);

  /* ---------- меню страниц (выпадающий список) ---------- */
  function buildMenu() {
    chMenu.innerHTML = "";
    CHANNELS.forEach((c, i) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "menu-item" + (i === cur ? " cur" : "");
      const numHtml = c.num
        ? "<span class='mi-num'>" + c.num + "</span>"
        : "<span class='mi-num star'>★</span>";
      b.innerHTML = numHtml + "<span class='mi-name'>" + c.name + "</span>";
      b.addEventListener("click", (e) => {
        e.stopPropagation();
        switchTo(i);
      });
      chMenu.appendChild(b);
    });
  }
  function openMenu() { buildMenu(); chMenu.classList.add("open"); }
  function closeMenu() { chMenu.classList.remove("open"); }

  osdCh.addEventListener("click", (e) => {
    e.stopPropagation();
    if (chMenu.classList.contains("open")) closeMenu(); else openMenu();
  });
  document.addEventListener("click", (e) => {
    if (!chMenu.contains(e.target)) closeMenu();
  });

  /* ---------- клик по бренду -> страница артиста ---------- */
  osdBrand.addEventListener("click", () => {
    if (powered) switchTo(ARTIST);
  });

  /* ---------- тап по экрану: пауза, повторный тап — продолжить ---------- */
  const pauseBadge = $("#pauseBadge");
  function showPauseBadge() { pauseBadge.classList.add("show"); }
  function hidePauseBadge() { pauseBadge.classList.remove("show"); }

  let lastTap = 0;
  sections.forEach((s) => {
    s.addEventListener("click", () => {
      if (!powered) return;
      if (chMenu.classList.contains("open")) return;
      const c = CHANNELS[cur];
      if (!c || !c.file) return; // страница артиста — без плеера
      const v = videos[cur];
      if (!v) return;
      // клип играет, но звук ещё ждёт жеста: этот тап только возвращает
      // звук, НЕ ставя клип на паузу (иначе «тап за звук» паузил видео)
      if (soundRetry && !v.paused && v.muted) { retrySound(); return; }
      const now = performance.now();
      if (now - lastSwitch < 800) return; // это был свайп/переключение
      if (now - lastTap < 350) return;    // защита от двойного тапа
      lastTap = now;
      if (v.paused || v.ended) {
        userPaused = false;
        if (v.ended) { v.currentTime = 0; endCard.classList.remove("show"); }
        startVideo(v);
        hidePauseBadge();
      } else {
        userPaused = true;
        playToken++; // погасить висящие ретраи
        v.pause();
        showPauseBadge();
      }
    });
  });

  /* ---------- ввод: колесо ---------- */
  window.addEventListener(
    "wheel",
    (e) => {
      if (!powered) return;
      if (Math.abs(e.deltaY) < 16) return;
      const now = performance.now();
      if (now - lastSwitch < 750) return;
      lastSwitch = now;
      (e.deltaY > 0 ? next : prev)();
    },
    { passive: true }
  );

  /* ---------- ввод: свайп ---------- */
  let tx = 0, ty = 0, tt = 0;
  window.addEventListener("touchstart", (e) => {
    tx = e.touches[0].clientX; ty = e.touches[0].clientY; tt = performance.now();
  }, { passive: true });
  window.addEventListener("touchend", (e) => {
    if (!powered) return;
    if (chMenu.classList.contains("open")) return;
    const dx = e.changedTouches[0].clientX - tx;
    const dy = e.changedTouches[0].clientY - ty;
    const dt = performance.now() - tt;
    if (dt > 700) return;
    if (Math.max(Math.abs(dx), Math.abs(dy)) < 55) return;
    const now = performance.now();
    if (now - lastSwitch < 750) return;
    lastSwitch = now;
    const forward = (Math.abs(dx) > Math.abs(dy) ? dx < 0 : dy < 0);
    (forward ? next : prev)();
  }, { passive: true });

  /* ---------- ввод: клавиатура ---------- */
  window.addEventListener("keydown", (e) => {
    if (!powered) {
      powerOn();
      return;
    }
    switch (e.code) {
      case "ArrowDown": case "ArrowRight": case "PageDown": case "KeyD":
        e.preventDefault(); next(); break;
      case "ArrowUp": case "ArrowLeft": case "PageUp": case "KeyA":
        e.preventDefault(); prev(); break;
      case "Digit1": case "Digit2": case "Digit3":
        switchTo(+e.code.slice(-1) - 1); break;
      case "Digit0":
        switchTo(ARTIST); break;
    }
  });

  /* ---------- автоскрытие шапки ---------- */
  let hideTimer;
  function pokeChrome() {
    document.body.classList.remove("idle");
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      if (powered && !chMenu.classList.contains("open")) document.body.classList.add("idle");
    }, 3500);
  }
  window.addEventListener("mousemove", pokeChrome);
  window.addEventListener("touchstart", pokeChrome, { passive: true });
  window.addEventListener("click", pokeChrome);
})();

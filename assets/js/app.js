/* DIRTYGEN·ТВ — channel switcher logic */
(function () {
  "use strict";

  const CHANNELS = [
    { num: "CH 01", name: "Я НЕ В СЕТИ", file: "video/ch1_main.mp4" },
    { num: "CH 02", name: "Я НЕ В СЕТИ · NIGHT", file: "video/ch2_night.mp4" },
    { num: "CH 03", name: "Я НЕ В СЕТИ · DAWN", file: "video/ch3_dawn.mp4" },
    { num: "CH 04", name: "DIRTYGEN", file: null },
  ];

  const $ = (s) => document.querySelector(s);
  const power = $("#power"), tv = $("#tv");
  const sections = document.querySelectorAll(".channel");
  const videos = document.querySelectorAll(".channel video");
  const staticCv = $("#static");
  const osdCh = $("#osdCh"), osdTitle = $("#osdTitle"), osdTime = $("#osdTime");
  const osdBottom = $("#osdBottom"), osdHint = $("#osdHint");
  const splash = $("#chSplash"), splashNum = $("#splashNum"), splashName = $("#splashName");
  const progress = $("#progress"), progressFill = $("#progressFill"), progressHead = $("#progressHead");
  const soundChip = $("#soundChip"), endCard = $("#endCard");

  let cur = -1;
  let powered = false;
  let muted = false;
  let lastSwitch = 0;
  let audioCtx = null;

  /* ---------- static flash ---------- */
  const SW = 260, SH = 146;
  staticCv.width = SW; staticCv.height = SH;
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

  function staticFlash(dur = 420) {
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
      // displacement bands
      const bands = 4;
      for (let b = 0; b < bands; b++) {
        const y = (Math.random() * SH) | 0;
        const h = 4 + (Math.random() * 22) | 0;
        const dx = ((Math.random() - 0.5) * 46) | 0;
        if (dx === 0) continue;
        const strip = sctx.getImageData(0, y, SW, Math.min(h, SH - y));
        sctx.putImageData(strip, dx, y);
      }
      // occasional bright tear
      if (Math.random() < 0.3) {
        sctx.fillStyle = "rgba(255,255,255," + (0.06 + Math.random() * 0.1) + ")";
        sctx.fillRect(0, Math.random() * SH, SW, 1 + Math.random() * 2);
      }
      requestAnimationFrame(draw);
    })();
  }

  /* ---------- channel control ---------- */
  function fmt(s) {
    if (!isFinite(s)) return "0:00";
    s = Math.max(0, s | 0);
    return ((s / 60) | 0) + ":" + String(s % 60).padStart(2, "0");
  }

  function showSplash(i) {
    splashNum.textContent = CHANNELS[i].num;
    splashName.textContent = CHANNELS[i].name;
    splash.classList.remove("show");
    void splash.offsetWidth; // reflow
    splash.classList.add("show");
  }

  function switchTo(i, silent) {
    i = ((i % CHANNELS.length) + CHANNELS.length) % CHANNELS.length;
    if (i === cur && powered) return;
    const prevVideo = videos[cur];
    if (prevVideo && !prevVideo.paused) { prevVideo.pause(); }

    cur = i;
    sections.forEach((s, k) => s.classList.toggle("active", k === cur));

    const isVideo = !!CHANNELS[cur].file;
    osdBottom.classList.toggle("hidden", !isVideo);
    osdCh.textContent = CHANNELS[cur].num + " / 04";
    osdTitle.textContent = CHANNELS[cur].name;
    osdHint.style.display = isVideo ? "" : "none";
    endCard.classList.remove("show");
    if (!isVideo) { osdTime.textContent = ""; }

    if (!silent) staticFlash();
    showSplash(cur);

    if (isVideo) {
      const v = videos[cur];
      v.preload = "auto";
      v.muted = muted;
      const p = v.play();
      if (p) p.catch(() => {
        v.muted = true; muted = true;
        soundChip.classList.add("show");
        v.play().catch(() => {});
      });
      // warm next video channel
      const nxt = (cur + 1) % CHANNELS.length;
      if (CHANNELS[nxt].file) videos[nxt].preload = "auto";
    }
  }

  function next() { switchTo(cur + 1); }
  function prev() { switchTo(cur - 1); }

  /* ---------- power on ---------- */
  function powerOn() {
    if (powered) return;
    powered = true;
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      audioCtx.resume();
    } catch (e) { /* noop */ }
    power.classList.add("off");
    document.body.classList.add("on");
    staticFlash(650);
    setTimeout(() => switchTo(0, true), 260);
    setTimeout(() => { power.style.display = "none"; }, 500);
  }
  power.addEventListener("click", powerOn);

  /* ---------- video events ---------- */
  videos.forEach((v) => {
    v.addEventListener("timeupdate", () => {
      if (sections[cur].querySelector("video") !== v) return;
      if (v.duration) {
        const p = (v.currentTime / v.duration) * 100;
        progressFill.style.width = p + "%";
        progressHead.style.left = p + "%";
        osdTime.textContent = fmt(v.currentTime) + " / " + fmt(v.duration);
      }
    });
    v.addEventListener("ended", () => {
      if (sections[cur].querySelector("video") !== v) return;
      endCard.classList.add("show");
    });
    v.addEventListener("click", () => {
      if (sections[cur].querySelector("video") !== v) return;
      if (v.paused) { v.play(); endCard.classList.remove("show"); }
      else v.pause();
    });
  });

  progress.addEventListener("click", (e) => {
    const v = videos[cur];
    if (!v || !v.duration) return;
    const r = progress.getBoundingClientRect();
    v.currentTime = ((e.clientX - r.left) / r.width) * v.duration;
  });

  /* ---------- sound chip ---------- */
  soundChip.addEventListener("click", () => {
    muted = false;
    videos.forEach((v) => (v.muted = false));
    soundChip.classList.remove("show");
  });

  /* ---------- input: wheel ---------- */
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

  /* ---------- input: touch ---------- */
  let tx = 0, ty = 0, tt = 0;
  window.addEventListener("touchstart", (e) => {
    tx = e.touches[0].clientX; ty = e.touches[0].clientY; tt = performance.now();
  }, { passive: true });
  window.addEventListener("touchend", (e) => {
    if (!powered) return;
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

  /* ---------- input: keyboard ---------- */
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
      case "Space":
        e.preventDefault();
        { const v = videos[cur];
          if (v) { v.paused ? v.play() : v.pause(); } }
        break;
      case "KeyM": {
        muted = !muted;
        videos.forEach((v) => (v.muted = muted));
        soundChip.classList.toggle("show", muted);
        break;
      }
      case "KeyF":
        if (document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen().catch(() => {});
        break;
      case "Digit1": case "Digit2": case "Digit3": case "Digit4":
        switchTo(+e.code.slice(-1) - 1);
        break;
    }
  });

  /* ---------- nosignal links ---------- */
  document.querySelectorAll("a.nosignal").forEach((a) => {
    a.addEventListener("click", (e) => {
      e.preventDefault();
      staticFlash(500);
      const old = a.textContent;
      a.textContent = "НЕТ СИГНАЛА";
      setTimeout(() => (a.textContent = a.dataset.name), 1400);
    });
  });

  /* ---------- auto-hide chrome ---------- */
  let hideTimer;
  function pokeChrome() {
    document.body.classList.remove("idle");
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => {
      if (powered) document.body.classList.add("idle");
    }, 3500);
  }
  window.addEventListener("mousemove", pokeChrome);
  window.addEventListener("touchstart", pokeChrome, { passive: true });
  window.addEventListener("click", pokeChrome);
})();

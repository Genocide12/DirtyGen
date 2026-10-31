// Генератор AI-кадров CH 02 «Смени канал» · NIGHT (v5).
// 16 ночных кадров N01-N16, длинные мульти-экшен промпты (2-3 действия
// в одном кадре + свет/текстуры/движение камеры) — по записке юзера для v5.
// Проба длительности встроена: пробуем 12с, при 400 «不支持当前duration值»
// автоматически пересоздаём с 10с (максимум, который API точно принимает).
// Состояние: aivideo/film_ch2/gen_state.json (НЕ в .gitignore — уходит на
// GitHub частичными коммитами как страховка от откатов диска).
// Запуск: node tools/film_gen_ch2.mjs [budget_seconds] [max_concurrency]

import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const BASE = path.dirname(path.dirname(new URL(import.meta.url).pathname));
const OUT_DIR = path.join(BASE, 'aivideo', 'film_ch2');
const STATE = path.join(OUT_DIR, 'gen_state.json');
fs.mkdirSync(OUT_DIR, { recursive: true });

const DUR_MAX = 12;   // пробуем максимум; фолбэк на 10 при 400
const DUR_MIN = 10;

const SHOTS = [
  // ---- ПРОЛОГ: ночь опускается (0-16) ----
  { id: 'N01', dur: DUR_MAX, prompt: 'Cinematic night aerial over a big city, camera drifting slowly above rooftops, light rain begins to fall and neon reflections bloom across wet streets below, deep blue night palette with scattered neon accents, atmospheric haze, anamorphic lens flare, 35mm film look, music video style, no text, no watermark' },
  { id: 'N02', dur: DUR_MAX, prompt: 'Cinematic night street, lonely young man in a hoodie walking along an empty sidewalk, he passes a row of glowing shop windows, warm light slides across his hood as he walks by without stopping, slow dolly following him from behind, wet asphalt, bokeh of street lamps, moody, music video style, no text' },
  { id: 'N03', dur: DUR_MAX, prompt: 'Cinematic close-up portrait at night, young man in a hoodie with a blank stare, neon signs reflected in his eyes and sliding across his face, a sign flickers and a red neon glow sweeps over his cheek, shallow depth of field, blurred neon bokeh behind, 50mm lens, moody music video style, no text' },

  // ---- БРЕЙК 1: зеркало города (38-46) ----
  { id: 'N04', dur: DUR_MAX, prompt: 'Cinematic macro shot of a rain puddle on dark asphalt at night, a whole neon city reflected perfectly in the still water, a single raindrop falls and ripples break the reflection into shimmering fragments, then the neon sign in the reflection flares brighter, high detail, moody, music video style, no text' },

  // ---- ДРОП 1: неоновый канал (46-74) ----
  { id: 'N05', dur: DUR_MAX, prompt: 'Cinematic wet night street with neon signs on both sides, camera pushing steadily forward at street level, pedestrians with umbrellas cross the frame one by one, neon reflections stretching long across the wet asphalt, vibrant magenta and cyan palette, anamorphic bokeh, atmospheric drizzle, music video aesthetic, no text' },
  { id: 'N06', dur: DUR_MAX, prompt: 'Cinematic night crossroads in heavy rain, cars waiting at a red light with headlights glowing through mist, traffic light switches to green and the cars burst forward, tires whipping spray out of puddles, streaks of tail lights, filmed from a low angle across the intersection, dynamic, music video style, no text' },
  { id: 'N07', dur: DUR_MAX, prompt: 'Cinematic night street food market, steam rising from food stalls with warm hanging bulbs, a cook tosses noodles in a flaming wok and the fire flashes up, customers laugh and clink skewers, strings of lights flickering, rich warm colors against deep blue night, handheld energy, music video style, no text' },

  // ---- ДРОП 2: живая ночная фактура (82-142) ----
  { id: 'N08', dur: DUR_MAX, prompt: 'Cinematic narrow night alley with graffiti walls lit by neon, a stray cat dashes across the frame, a faulty neon sign buzzes off and on and suddenly floods the whole wall with electric pink light, wet puddles mirroring the glow, slow camera creep forward, texture of brick and spray paint, music video style, no text' },
  { id: 'N09', dur: DUR_MAX, prompt: 'Cinematic subway platform at night, a young man in a hoodie stands still near the edge, an express train blasts past behind him and horizontal light streaks sweep across his face, wind from the train ripples his hood and jacket, train lights vanishing into the tunnel, high contrast, slow motion feel, music video style, no text' },
  { id: 'N10', dur: DUR_MAX, prompt: 'Cinematic nightclub interior, rotating light beams sweeping through haze over a moving crowd, silhouettes dancing in sync, a strobe light kicks in and freezes the crowd in bright flashes, deep shadows and vivid beams, slow push through the dance floor, anamorphic flares, music video style, no text' },
  { id: 'N14', dur: DUR_MAX, prompt: 'Cinematic late night diner seen from the street, people at the counter with steam rising from coffee cups, a big neon sign flickers and stabilizes, its pink light spilling across the wet sidewalk toward the camera, reflections in the glass, nostalgic film grain, quiet nocturnal mood, music video style, no readable text' },

  // ---- ПЕРЕХОД: наверх (142-156) ----
  { id: 'N11', dur: DUR_MAX, prompt: 'Cinematic shot of a young man in a hoodie climbing an iron fire escape at night, flight after flight, city lights growing larger behind him with every level, he finally steps out onto a rooftop edge, camera following from below then rising with him, cold night wind, industrial textures, dramatic city glow, music video style, no text' },

  // ---- ФИНАЛ: крыша/горизонт (156-214) ----
  { id: 'N12', dur: DUR_MAX, prompt: 'Cinematic rooftop panorama at night, vast neon city stretching to the horizon, a young man stands at the edge facing the skyline, he pulls back his hood, night wind in his hair, city lights flicker in a slow wave across the skyline as if breathing, camera slowly circling him, emotional, anamorphic, music video style, no text' },
  { id: 'N13', dur: DUR_MAX, prompt: 'Cinematic night sky at the edge of dawn, deep blue overhead fading into a thin orange line on the horizon, stars going out one by one, low clouds catching pink and orange city glow from below, a distant plane blinking across the frame, very slow upward tilt, majestic and calm, music video style, no text' },
  { id: 'N15', dur: DUR_MAX, prompt: 'Cinematic night drive over a long city bridge, camera tracking a single car from the side, headlight beams drawing long light trails, the river below mirroring the city lights in moving colors, the car pulls away toward the glowing skyline, light rain sparkle, dynamic tracking shot, music video style, no text' },
  { id: 'N16', dur: DUR_MAX, prompt: 'Cinematic finale on a rooftop at night, young man without hood standing at the roof edge with the entire neon city behind him, he takes one calm step toward the light, camera slowly rises and pulls back revealing the endless glowing city and a faint dawn line appearing on the far horizon, hopeful, anamorphic lens flare, film look, no text' },
];

const budgetMs = (Number(process.argv[2] || 540)) * 1000;
const MAXCONC = Number(process.argv[3] || 3);
const t0 = Date.now();
const outOfTime = () => Date.now() - t0 > budgetMs;
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

let state = {};
if (fs.existsSync(STATE)) state = JSON.parse(fs.readFileSync(STATE, 'utf8'));

const have = (id) => {
  const f = path.join(OUT_DIR, id + '.mp4');
  return fs.existsSync(f) && fs.statSync(f).size > 50000;
};
const save = () => fs.writeFileSync(STATE, JSON.stringify(state, null, 1));
const count = () => fs.readdirSync(OUT_DIR).filter(f => /^N\d+\.mp4$/.test(f)).length;
const TOTAL = SHOTS.length;

async function dl(url, file) {
  execSync(`curl -sL --retry 3 -o "${file}" "${url}"`, { stdio: 'pipe' });
  return fs.statSync(file).size > 50000;
}

// create с фолбэком длительности: 400 «不支持当前duration值» -> 10с
async function createShot(s) {
  let dur = state[s.id + ':dur'] || s.dur;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const task = await zai.video.generations.create({
        prompt: s.prompt, quality: 'quality', with_audio: false,
        size: '1920x1080', fps: 30, duration: dur,
      });
      state[s.id + ':dur'] = dur; save();
      return { task, dur };
    } catch (e) {
      const msg = String(e.message || e);
      if (/1214|duration/i.test(msg) && dur !== DUR_MIN) {
        console.log(s.id, `dur=${dur} не поддержан — фолбэк на ${DUR_MIN}`);
        dur = DUR_MIN; state[s.id + ':dur'] = dur; save();
        continue;
      }
      throw e;
    }
  }
  throw new Error('create: оба варианта длительности отвергнуты');
}

let zai;
async function main() {
  zai = await ZAI.create();

  const queue = SHOTS.filter(s => !have(s.id) && !state[s.id + ':task']);
  const inflight = [];
  for (const s of SHOTS) {
    const tid = state[s.id + ':task'];
    if (tid && !have(s.id)) inflight.push({ s, taskId: tid });
  }
  console.log(`старт: файлов ${count()}/${TOTAL}, в полёте ${inflight.length}, в очереди ${queue.length}`);

  let made = 0;
  let last429 = 0;

  while (!outOfTime()) {
    // 1) опрос в полёте
    const still = [];
    for (const p of inflight) {
      try {
        const r = await zai.async.result.query(p.taskId);
        const f = path.join(OUT_DIR, p.s.id + '.mp4');
        if (r.task_status === 'SUCCESS') {
          const url = r.video_result?.[0]?.url || r.video_url || r.url || r.video;
          if (url && await dl(url, f)) {
            state[p.s.id] = 'done'; delete state[p.s.id + ':task']; save();
            console.log(p.s.id, 'DOWNLOADED', fs.statSync(f).size, `(${count()}/${TOTAL})`, new Date().toISOString()); made++;
          } else { console.log(p.s.id, 'download problem — таск сброшен'); delete state[p.s.id + ':task']; save(); queue.unshift(p.s); }
        } else if (r.task_status === 'FAIL' || r.task_status === 'FAILED') {
          console.log(p.s.id, 'TASK FAILED — в очередь'); delete state[p.s.id + ':task']; save(); queue.push(p.s);
        } else { still.push(p); }
      } catch (e) {
        console.log(p.s.id, 'poll err:', String(e.message || e).slice(0, 80));
        still.push(p);
      }
      await sleep(1200);
    }
    inflight.length = 0; inflight.push(...still);

    if (count() >= TOTAL) break;

    // 2) занять свободные слоты (не чаще раза в 20с после 429)
    while (queue.length && inflight.length < MAXCONC && !outOfTime()) {
      if (Date.now() - last429 < 20000) break;
      const s = queue.shift();
      try {
        const { task, dur } = await createShot(s);
        state[s.id + ':task'] = task.id; save();
        inflight.push({ s, taskId: task.id });
        console.log(s.id, `task created (dur=${dur}) → в полёте ${inflight.length}`, new Date().toISOString());
        await sleep(5000);
      } catch (e) {
        const msg = String(e.message || e);
        if (/429/.test(msg)) { console.log(s.id, 'create: слотов нет (429), ждём'); last429 = Date.now(); queue.unshift(s); break; }
        console.log(s.id, 'create failed:', msg.slice(0, 90), '— обратно в очередь'); queue.push(s); break;
      }
    }

    if (inflight.length === 0 && queue.length === 0) break;
    await sleep(8000);
  }
  console.log(`итог: скачано ${made}; файлов ${count()}/${TOTAL}; в полёте ${inflight.length}; в очереди ${queue.length}`);
  if (count() >= TOTAL) console.log('ALL_DONE');
}
main().catch(e => { console.error('FATAL', e.message); process.exit(1); });

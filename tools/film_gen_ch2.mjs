// Генератор AI-кадров CH 02 «Смени канал» (v5, план Б: режиссёрский монтажный лист юзера).
// 25 кадров S01-S25 = 14 сцен монтажного листа (03:34 / 214с), сцены длиннее 10с
// разбиты на 2-3 кадра по экшен-битам (лимит API 10с/кадр).
// Герой во всех промптах: 33-летний восточноевропеец, короткие тёмные волосы,
// лёгкая щетина, простое чёрное шерстяное пальто поверх тёмного худи —
// одинаковое описание в каждом промпте для консистентности персонажа.
// Проба длительности встроена: пробуем 12с, при 400 «不支持当前duration值»
// автоматически пересоздаём с 10с (максимум, который API точно принимает).
// Состояние: aivideo/film_ch2/gen_state.json (НЕ в .gitignore — уходит на
// GitHub частичными коммитами как страховка от откатов диска).
// Запуск: node tools/film_gen_ch2.mjs [budget_seconds] [ax_concurrency]

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

const HERO = 'A 33-year-old Eastern European man with short dark hair, light stubble, wearing a simple black wool coat over a dark hoodie';

const SHOTS = [
  // ---- АКТ 1 · СТАРЫЙ КАНАЛ (0-45): холодный нуар ----
  { id: 'S01', dur: DUR_MAX, prompt: `Cinematic 4k music video shot, 35mm anamorphic lens. ${HERO}, stands completely still on a crowded modern city street at cold gray dawn. Heavy rain. Blurred crowds of people rush past him in fast motion blur around his still figure. Moody blue-gray color palette, premium film production quality, photorealistic, cinematic lighting, reflections of headlights in wet asphalt, no text, no watermark` },
  { id: 'S02', dur: DUR_MAX, prompt: `Cinematic 4k music video shot, 35mm anamorphic lens. Slow dolly zoom pulling back, isolating the same ${HERO}, from the rushing motion-blurred crowd of people at cold gray dawn in heavy rain. Moody blue-gray palette, deep depth, premium film production quality, photorealistic, cinematic lighting, no text, no watermark` },
  { id: 'S03', dur: DUR_MAX, prompt: `Close-up cinematic shot through the glass door of a moving subway car. The tired expressive face of the ${HERO}, reflections on the glass overlaying his face, dark concrete tunnel walls flashing outside. Monotonous oppressive underground techno aesthetic, deep shadows, cinematic reflections, 4k, photorealistic, no text, no watermark` },
  { id: 'S04', dur: DUR_MAX, prompt: `Close-up cinematic shot inside a moving subway car. The hand of a man in a dark hoodie slowly scrolling a smartphone screen with glowing social media feeds, someone else's luxury cars and success graphs, dark concrete tunnel walls flashing outside the window, reflections mixing layers on the glass. Monotonous, oppressive underground techno aesthetic, deep shadows, cinematic, 4k, photorealistic, no text, no watermark` },
  { id: 'S05', dur: DUR_MAX, prompt: `Medium shot. The ${HERO}, standing inside a glass elevator of a modern anonymous office building, looking out through the glass at cold monolithic concrete architecture. Slow vertical tilt up parallel to the rising elevator. Depressing gray-blue tones, natural human movement, professional cinematography, photorealistic, 16:9, no text, no watermark` },
  { id: 'S06', dur: DUR_MAX, prompt: `Slow cinematic tilt up over a panorama of faceless gray office buildings and rows of identical windows at cold dusk, passengers in shadow inside a glass business center elevator staring down at glowing phone screens. Depressing gray-blue tones, professional cinematography, photorealistic, 16:9, no text, no watermark` },

  // ---- АКТ 2 · ДВА ВЗГЛЯДА (45-80): дуализм, стекло ----
  { id: 'S07', dur: DUR_MAX, prompt: `Cinematic shot on a rainy city street at cold gray dusk. The ${HERO}, stands before a large glass store window; one side of the frame shows a dark, hopeless rainy street. Moody blue-gray noir palette, deep shadows, reflections of headlights in wet asphalt, premium film production quality, photorealistic, 4k, no text, no watermark` },
  { id: 'S08', dur: DUR_MAX, prompt: `Cinematic match cut shot, slow camera pan left to right across a large glass store window on a city street. In the reflection the same rainy street transforms: warm golden light rays break through heavy clouds, revealing beautiful architectural textures, warm stone details and an open empty road ahead. The ${HERO}, notices it and slightly tilts his head. Sophisticated lighting, realistic glass reflections, warm golden versus cold blue-gray contrast, 4k, photorealistic, no text, no watermark` },
  { id: 'S09', dur: DUR_MAX, prompt: `Cinematic macro shot. A single rain droplet on a metal handrail refracting and bending golden warm light, ultra shallow depth of field, 35mm lens, photorealistic water texture, soft golden bokeh, intimate contemplative mood, 4k, no text, no watermark` },
  { id: 'S10', dur: DUR_MAX, prompt: `Cinematic macro shot with a fast rack focus shift from a rain droplet refracting golden light on a metal handrail to the thoughtful face of the ${HERO}, observing it. Subtle internal transformation, intelligent gaze, photorealistic, shallow depth of field, 35mm lens, warm light, no text, no watermark` },

  // ---- АКТ 3 · ПЕРВЫЙ ВСПЛЕСК (80-110): войд экранов ----
  { id: 'S11', dur: DUR_MAX, prompt: `Epic cinematic shot in a dark abstract void. The ${HERO}, stands calmly surrounded by dozens of flat floating screens, each screen showing a different version of the same gray city. Cold silver light, deep black space, subtle glow from the screens, high contrast, premium vfx look, photorealistic, 4k, no text, no watermark` },
  { id: 'S12', dur: DUR_MAX, prompt: `Epic cinematic shot in a dark abstract void. The ${HERO}, walks calmly toward the grayest most colorless floating screen and firmly touches it with one finger, his faint reflection in the dark glass. Cold silver rim light, tense anticipation, deep black space, premium vfx, photorealistic, 4k, no text, no watermark` },
  { id: 'S13', dur: DUR_MAX, prompt: `Epic cinematic drop sequence with a dynamic 180-degree camera orbit. A flat gray screen shatters into hundreds of luminous glowing silver fragments flying past the camera toward the viewer, revealing a bright warm light horizon behind the broken screen; the ${HERO}, stands still at the center. High-speed camera effect, breathtaking premium vfx, silver sparks, photorealistic, 4k, no text, no watermark` },

  // ---- АКТ 4 · ИРОНИЯ (110-135): Уэс Андерсон, бытовая самоирония ----
  { id: 'S14', dur: DUR_MAX, prompt: `Understated visual comedy scene, static frontal medium shot in Wes Anderson style, realistic tones. An ordinary man sits on a simple sofa in a mundane unchanged apartment room and proudly, with a victorious expression, changes his smartphone wallpaper to a luxury image, golden light glowing on his face from the screen. Clean symmetrical composition, dry humor, natural acting, photorealistic, 4k, no text, no watermark` },
  { id: 'S15', dur: DUR_MAX, prompt: `Understated visual comedy scene, static frontal medium shot, realistic tones. The same man on the sofa slowly raises his eyes from the smartphone and looks around his absolutely gray dull unchanged apartment room with a blank absurd expression. Clean symmetrical composition, dry humor, realistic human behavior, natural window light, photorealistic, 4k, no text, no watermark` },
  { id: 'S16', dur: DUR_MAX, prompt: `Close-up shot with a slow push-in. The ${HERO}, looks toward the camera with a subtle intelligent ironic half-smile, a knowing look of understated self-irony. Rich bokeh, cinematic lighting, warm neutral tones, photorealistic, 4k, no text, no watermark` },

  // ---- АКТ 5 · ВНУТРЕННИЙ ПЕРЕХОД (135-160): глитчи -> искры, туннель ----
  { id: 'S17', dur: DUR_MAX, prompt: `Cinematic build-up shot, detailed macro close-up on the shoulder and hands of the ${HERO}, in his black wool coat. Thin blue digital glitch lines appear and run around the fabric, then smoothly dissolve into a soft flow of silver particles and warm golden light dust. Sophisticated sci-fi realism, magical but grounded visual effect, photorealistic, 4k, no text, no watermark` },
  { id: 'S18', dur: DUR_MAX, prompt: `Cinematic tracking shot, camera retreating backwards in front of the ${HERO}, walking confidently through a long dark concrete underpass tunnel, his steady steps echoing, cold dim light, deep shadows, industrial concrete texture, photorealistic, 4k, 16:9, no text, no watermark` },
  { id: 'S19', dur: DUR_MAX, prompt: `Cinematic tracking shot in a long underpass tunnel: with every confident step of the man in a black wool coat, the cold concrete walls behind him transform into polished mirror surfaces reflecting warm golden light, and at the end of the tunnel a bright exit glows. Architectural light transformation, no magic, steady camera movement, photorealistic, 4k, no text, no watermark` },

  // ---- АКТ 6 · НА ВЫСОТЕ (160-195): золото, рассвет, триумф ----
  { id: 'S20', dur: DUR_MAX, prompt: `Grand final drop scene, wide crane shot. The ${HERO}, steps out through a door onto the massive rooftop of a modern skyscraper overlooking a vast city; heavy clouds part away and intense golden morning sunlight floods the glass architecture, wind blows his black coat. Epic panoramic view, high production value, cinematic scale, photorealistic, 4k, no text, no watermark` },
  { id: 'S21', dur: DUR_MAX, prompt: `Epic cinematic 360-degree crane orbit around the ${HERO}, standing at the edge of a skyscraper rooftop, golden morning sunlight flooding a vast modern city below, clouds parting, wind in his coat, majestic scale, high production value, anamorphic lens flares, photorealistic, 4k, no text, no watermark` },
  { id: 'S22', dur: DUR_MAX, prompt: `Cinematic drone aerial shot of a magnificent modern city grid at golden hour sunrise. Sunlight reflecting off glass skyscraper facades, shadows retreating, clear open roads with cars starting to move. The frame is wide, majestic, full of space and freedom, premium color grading, photorealistic, 4k, no text, no watermark` },
  { id: 'S23', dur: DUR_MAX, prompt: `Cinematic FPV drone shot slowly pushing in toward a calm man in a black wool coat standing quietly on a skyscraper rooftop at golden sunrise, the city glowing below, he simply breathes deeply, accepting responsibility for his next step. Majestic, warm golden light, premium color grading, photorealistic, 4k, no text, no watermark` },

  // ---- АКТ 7 · АУТРО (195-214): интимно, выдох, уход в свет ----
  { id: 'S24', dur: DUR_MAX, prompt: `Extreme close-up shot, static, soft bokeh. The face of the 33-year-old man with short dark hair looking out at a sunlit city; he takes a slow calm breath and gives a subtle confident genuine smile of inner peace and clarity, warm morning light illuminating his features. High emotional depth, photorealistic, 35mm lens, 4k, no text, no watermark` },
  { id: 'S25', dur: DUR_MAX, prompt: `Cinematic wide low-angle shot, slow pull-back and descent. A man in a black wool coat turns away from the camera and walks forward across a rooftop into the warm morning sunlight; the upper half of the frame is clean negative space with a soft gradient sky and silhouettes of distant buildings, perfect for titles. Minimalist, philosophical, atmospheric ending, warm golden light, photorealistic, 4k, no text, no watermark` },
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
const count = () => fs.readdirSync(OUT_DIR).filter(f => /^S\d+\.mp4$/.test(f)).length;
const TOTAL = SHOTS.length;

async function dl(url, file) {
  execSync(`curl -sL --retry 3 -o "${file}" "${url}"`, { stdio: 'pipe' });
  return fs.statSync(file).size > 50000;
}

// create с фолбэком длительности: 400 «不支持当前duration值» -> 10с
// (глобальный флаг: если 12с отвергнуто хотя бы раз — все следующие кадры сразу на 10с)
async function createShot(s) {
  let dur = state[s.id + ':dur'] || s.dur;
  if (state['dur_max_invalid'] && dur > DUR_MIN) dur = DUR_MIN;
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
        console.log(s.id, `dur=${dur} не поддержан — фолбэк на ${DUR_MIN} (глобально)`);
        dur = DUR_MIN; state[s.id + ':dur'] = dur; state['dur_max_invalid'] = true; save();
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

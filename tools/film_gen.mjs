// Очередь генерации кадров для клип-фильма «Смени канал» (v2-обогащение).
// Запуск: node tools/film_gen.mjs [budget_seconds] [only_priority_n]
// Файлы результатов: aivideo/film/Q##.mp4, состояние: .build_film/gen_state.json
// 429 → пауза внутри бюджета; повторный запуск продолжает с места.

import ZAI from 'z-ai-web-dev-sdk';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const BASE = path.dirname(path.dirname(new URL(import.meta.url).pathname));
const OUT_DIR = path.join(BASE, 'aivideo', 'film');
const STATE = path.join(BASE, '.build_film', 'gen_state.json');
fs.mkdirSync(OUT_DIR, { recursive: true });
fs.mkdirSync(path.dirname(STATE), { recursive: true });

// ---- раскадровка: приоритет сверху вниз (spine → money shots → расширение) ----
const SHOTS = [
  { id: 'Q01', p: 0, dur: 10, prompt: 'Cinematic music video shot, gray dawn city street, young man in hoodie walking away from camera down an empty street, desaturated cold blue tones, flat overcast light, slow dolly following him, 35mm film look, muted colors, no text, no watermark', },
  { id: 'Q13', p: 1, dur: 10, prompt: 'Cinematic music video shot, man standing at a doorway threshold seen from behind, cold hallway behind him, warm golden dawn light flooding through the open door into a bright street, he hesitates, very slow camera push toward the door, emotional, film grain, no text' },
  { id: 'Q14', p: 2, dur: 10, prompt: 'Cinematic music video finale, man steps through a doorway into a golden sunrise street, camera slowly rises up revealing the whole city waking up in warm light, people smiling, cafe windows glowing, hopeful, anamorphic lens flare, film look, no text' },
  { id: 'Q12', p: 3, dur: 5,  prompt: 'Cinematic close-up: a hand holding a smartphone, thumb changes the phone wallpaper to a bright sunrise photo, the owner half-smiles looking at it, warm light, shallow depth of field, 50mm lens, music video style, no UI text' },
  { id: 'Q11', p: 4, dur: 10, prompt: 'Cinematic music video shot, young man stops at a city crossroads at dusk, looks to the right toward a narrow alley glowing with warm string lights and murals, left side is gray and cold, he hesitates then turns right toward the light, slow motion, film look' },
  { id: 'Q07', p: 5, dur: 10, prompt: 'Cinematic neon city at night, wet asphalt with vivid reflections, slow steady camera push forward down the street, vibrant colors, anamorphic bokeh, atmospheric haze, music video aesthetic, high detail, no text, no watermark' },
  { id: 'Q08', p: 6, dur: 10, prompt: 'Cinematic city corner in full color at night, warm lights, people crossing the street, camera crane rises up over the crossing, alive urban atmosphere, neon reflections, music video style, film grain, no text' },
  { id: 'Q02', p: 7, dur: 5,  prompt: 'Cinematic close-up portrait of a young man in a hoodie, blank tired stare, gray desaturated cold tones, shallow depth of field, 50mm lens, moody overcast light, music video style, no text' },
  { id: 'Q03', p: 8, dur: 5,  prompt: 'Cinematic shot, tired middle-aged man at a bus stop looking at his watch with a frustrated expression, gray cold morning, desaturated tones, static camera, people waiting motionless, music video style, no text' },
  { id: 'Q04', p: 9, dur: 10, prompt: 'Cinematic shot of a gray cold city street where everything is desaturated except one warmly lit cafe window with people laughing inside, golden light spills onto the wet pavement, composition focused on the contrast, rain, film look, no text' },
  { id: 'Q05', p: 10, dur: 10, prompt: 'Cinematic POV shot: walking with eyes down, gray pavement in focus, colorful blurred life beyond shop windows out of focus in the background, bokeh of warm lights the walker does not notice, shallow depth of field, melancholic, music video style' },
  { id: 'Q06', p: 11, dur: 5,  prompt: 'Cinematic macro shot of a rain puddle: gray sky reflected above, vivid neon signs reflected below, split composition in one reflection, raindrops ripple the surface, moody, high detail, music video style, no text' },
  { id: 'Q09', p: 12, dur: 5, prompt: 'Cinematic extreme low angle looking up between two buildings toward the sky, dramatic perspective, dawn light breaking between the towers, lens flare, gray turning to gold, music video style, no text' },
  { id: 'Q10', p: 13, dur: 10, prompt: 'Cinematic aerial drone view of a city intersection at golden hour, streams of people crossing like light trails, warm evening light, slow aerial push forward, epic yet intimate, music video style, no text' },
];

const budgetMs = (Number(process.argv[2] || 480)) * 1000;
const maxPri = process.argv[3] !== undefined ? Number(process.argv[3]) : 99;
const t0 = Date.now();
const outOfTime = () => Date.now() - t0 > budgetMs;

let state = {};
if (fs.existsSync(STATE)) state = JSON.parse(fs.readFileSync(STATE, 'utf8'));

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function dl(url, file) {
  execSync(`curl -sL --retry 3 -o "${file}" "${url}"`, { stdio: 'pipe' });
  return fs.statSync(file).size > 50000;
}

async function main() {
  const zai = await ZAI.create();
  let made = 0;
  for (const s of SHOTS) {
    if (s.p > maxPri) break;
    const file = path.join(OUT_DIR, s.id + '.mp4');
    if (fs.existsSync(file) && fs.statSync(file).size > 50000) { console.log(s.id, 'already downloaded'); continue; }
    if (state[s.id] === 'done') continue;

    // задача создана ранее? — опрашиваем
    let taskId = state[s.id + ':task'];
    if (!taskId) {
      if (outOfTime()) { console.log('budget: stop before create', s.id); break; }
      try {
        const task = await zai.video.generations.create({
          prompt: s.prompt, quality: 'quality', with_audio: false,
          size: '1920x1080', fps: 30, duration: s.dur,
        });
        taskId = task.id;
        state[s.id + ':task'] = taskId;
        fs.writeFileSync(STATE, JSON.stringify(state, null, 1));
        console.log(s.id, 'task created', taskId, new Date().toISOString());
      } catch (e) {
        const msg = String(e.message || e);
        console.log(s.id, 'create failed:', msg.slice(0, 120));
        if (/429/.test(msg)) { console.log('429 — пауза 60с'); await sleep(60000); if (outOfTime()) break; }
        continue;
      }
    }
    // поллинг
    let backoff = 15000;
    while (!outOfTime()) {
      try {
        const r = await zai.async.result.query(taskId);
        if (r.task_status === 'SUCCESS') {
          const url = r.video_result?.[0]?.url || r.video_url || r.url || r.video;
          if (url && await dl(url, file)) {
            state[s.id] = 'done'; delete state[s.id + ':task'];
            fs.writeFileSync(STATE, JSON.stringify(state, null, 1));
            console.log(s.id, 'DOWNLOADED', fs.statSync(file).size);
            made++;
          } else { console.log(s.id, 'download problem'); }
          break;
        } else if (r.task_status === 'FAIL' || r.task_status === 'FAILED') {
          console.log(s.id, 'TASK FAILED'); delete state[s.id + ':task'];
          fs.writeFileSync(STATE, JSON.stringify(state, null, 1));
          break;
        } else {
          await sleep(backoff); backoff = Math.min(backoff * 1.3, 45000);
        }
      } catch (e) {
        const msg = String(e.message || e);
        console.log(s.id, 'poll err:', msg.slice(0, 120));
        if (!/429/.test(msg)) break;
        await sleep(45000);
      }
    }
  }
  console.log(`итог: скачано ${made}; в состоянии:`, Object.keys(state).filter(k=>!k.includes(':')));
}
main().catch(e => { console.error('FATAL', e.message); process.exit(1); });

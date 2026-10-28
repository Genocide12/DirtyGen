#!/bin/bash
# ============================================================
# Грязный Гена — «Я не в сети» | Генерация кадров для клипа
# 16:9, стиль: неон/киберпанк, арка ТЬМА -> СВЕТ
# Использование: bash gen_frames.sh <start> <end>  (индексы 1..28)
# ============================================================
OUT=/home/z/my-project/dirtygen/frames
mkdir -p "$OUT"

DARK="cinematic film still, moody atmosphere, neon cyberpunk aesthetic, cyan and magenta accent lights, volumetric fog, film grain, anamorphic lens flare, dramatic lighting, ultra detailed, 35mm photography"
LIGHT="cinematic film still, warm golden hour light, sun rays and lens bloom, airy hopeful atmosphere, film grain, anamorphic lens flare, ultra detailed, 35mm photography"
MAN="young slavic man with short dark hair wearing a black hoodie"

declare -A P
# ---------- ИНТРО (0:00-0:20) — тьма, демонический шёпот ----------
P[1]="aerial night view of a sprawling megapolis under heavy storm clouds, city glowing with cold cyan and magenta neon from below, ominous dark atmosphere, rain haze, $DARK"
P[2]="$MAN seen from behind standing on the edge of a rooftop high above a dark neon city at night, faint red neon rim light on his shoulders, fog below, tiny cars with light trails, ominous mood, $DARK"
P[3]="close-up of a man's face in a pitch dark room half-lit by the flickering blue glow of an old CRT television showing static, reflection of TV static in his eye, deep shadows, mysterious, $DARK"

# ---------- КУПЛЕТ 1 (0:20-0:50) — серое утро, рутина ----------
P[4]="grey overcast morning in a big city, crowded crosswalk full of blurred faceless commuters staring at their phones under umbrellas, desaturated cold colors, motion blur, routine and alienation, cinematic film still, muted palette, film grain, 35mm"
P[5]="view from inside a rainy tram window at dawn, raindrops on the glass, blurred grey city sliding by outside, reflections of pale lights, melancholic mood, desaturated cinematic film still, film grain, 35mm"
P[6]="$MAN walking alone through a grey city street against a stream of motion-blurred faceless commuters, he is the only sharp figure, cold desaturated tones, cinematic contrast of individual vs crowd, film grain, 35mm"
P[7]="grey city street where a crowd of people stare down at glowing phone screens, one young man looks up at a single ray of light breaking between tall buildings, symbolic hope, desaturated with one warm light accent, cinematic film still, film grain"

# ---------- ПРЕ-ДРОП (0:50-1:00) — тот же город, тот же свет ----------
P[8]="ordinary slightly dull city street in the morning, overcast sky, one small lone figure with a black hoodie walking on the wet asphalt, flat grey lighting, minimal cinematic composition, film grain, 35mm"
P[9]="the same ordinary city street from a slightly different angle, but now warm golden light rays break through the clouds and illuminate the wet asphalt, the lone figure in black hoodie pauses and raises his head, same place seen with new eyes, cinematic film still, warm and cold contrast, film grain"

# ---------- ДРОП 1 (1:00-1:15) — СМЕНИ КАНАЛ ----------
P[10]="a wall of stacked old CRT televisions all showing white static noise, one single screen in the center glows bright cyan showing a door of light, dark room, magenta and cyan neon reflections, glitch aesthetic, $DARK"
P[11]="a hand reaching into the glowing screen of an old CRT television, the screen shows a bright parallel neon world inside, shards of glass and static particles floating, magenta and cyan glow, surreal, $DARK"
P[12]="extreme close-up of an eye slowly opening, the iris reflects a grey city transforming into a vivid neon cyberpunk city, a streak of cyan light across the pupil, hyper detailed, $DARK"
P[13]="$MAN walking through a shattering wall of TV static and glitch shards, stepping from the dark side into a vivid neon-lit street, dynamic movement, particles of light, transformation moment, $DARK"

# ---------- КУПЛЕТ 2 (1:15-1:45) — разные углы зрения ----------
P[14]="night city with neon signs reflected upside down in a large puddle on dark asphalt, a boot about to step into the reflection, surreal mirrored world, cyan magenta reflections, $DARK"
P[15]="view from a rooftop over a vast night city, a thin line of warm golden dawn light appearing on the far horizon cutting through the blue darkness, first sign of change, $DARK"
P[16]="cinematic split composition of the same city intersection seen from two opposite corners at once: left half cold grey and gloomy, right half warm golden and alive, diptych of perspectives, film grain, 35mm"
P[17]="surreal city stairways crossing each other like an Escher drawing, multiple paths going in different directions, all paths are grey except one glowing with warm golden light, a small figure standing at the bottom choosing, cinematic, symbolic"

# ---------- БРЕЙК (1:45-2:00) — ирония ----------
P[18]="dim messy apartment at night lit only by a TV showing static, a young slavic man slouched on a worn couch smirking at his phone, ironic lazy mood, blue TV glow and warm lamp clash, cinematic, film grain, 35mm"
P[19]="close-up of hands holding a smartphone in a dark room, the phone screen shows a vibrant live wallpaper of a golden sunset over a city, thumb hovering above the screen, screen light reflecting on the face, contrast of fake and real light, cinematic"

# ---------- БИЛД-АП (2:00-2:20) — свет нарастает ----------
P[20]="first person standing on a rooftop at dawn, golden light flooding over the city horizon, morning mist between buildings, the dark night retreating, breath visible in cold air, hope rising, $LIGHT"
P[21]="$MAN standing at a fork of two streets: left street is a dark cold alley with blue shadows, right street is flooded with warm morning sunlight, he faces the choice, dramatic backlight, symbolic crossroads, $LIGHT"
P[22]="$MAN stepping from deep shadow into a beam of warm light, half of his face lit, hoodie sliding off his head, dust particles floating in the sunbeam, silhouette brightening, transformation, $LIGHT"

# ---------- ФИНАЛЬНЫЙ ДРОП (2:20-2:45) — свет, мощь ----------
P[23]="an ordinary city street at sunrise, wet asphalt mirroring the golden sky, long warm shadows, a lone figure in a black hoodie walking toward the sun, lens flare, the same street reborn in gold, $LIGHT"
P[24]="confident young slavic man with short dark hair, no hood, calm slight smile, walking toward the camera in golden hour backlight, city street behind him glowing, sun bloom flaring around his silhouette, liberation, $LIGHT"
P[25]="wide panoramic view of a huge city bathed in warm morning sunlight, birds flying across the sky, light rays between skyscrapers, mist glowing gold, airy and uplifting, $LIGHT"
P[26]="sun rays bursting between glass skyscrapers, god rays cutting through morning haze, golden flares, camera looking up, epic and uplifting, $LIGHT"

# ---------- АУТРО (2:45-3:07) — покой ----------
P[27]="calm pastel dawn over a city river, soft pink and blue sky, gentle mist on the water, bridge silhouettes, serene and clean minimal composition, peaceful resolution, cinematic film still, soft light, film grain"
P[28]="morning rooftop scene, a young slavic man with short dark hair sits peacefully on the rooftop edge, hood down, face visible in profile with a calm expression, the city below awake and bathed in soft morning light, full circle from darkness to light, $LIGHT"

START=${1:-1}
END=${2:-28}

for i in $(seq "$START" "$END"); do
  f=$(printf "%02d" "$i")
  if [ -s "$OUT/${f}.png" ]; then echo "[$f] already exists, skip"; continue; fi
  echo "[$f] generating..."
  for attempt in 1 2 3; do
    z-ai image -p "${P[$i]}" -o "$OUT/${f}.png" -s 1344x768 && break
    echo "[$f] attempt $attempt failed, retry in 5s..."
    sleep 5
  done
  [ -s "$OUT/${f}.png" ] && echo "[$f] OK" || echo "[$f] FAILED AFTER RETRIES"
done
echo "BATCH DONE ($START-$END)"

#!/bin/bash
# Дополнительные изображения для сайта: обложка, портрет артиста, OG-картинка
OUT=/home/z/my-project/dirtygen/assets/img
mkdir -p "$OUT"

gen() {  # gen <file> <size> <prompt>
  local f="$OUT/$1"
  [ -s "$f" ] && { echo "[$1] skip"; return; }
  for attempt in 1 2 3; do
    z-ai image -p "$3" -o "$f" -s "$2" && break
    sleep 5
  done
  [ -s "$f" ] && echo "[$1] OK" || echo "[$1] FAILED"
}

gen "cover.png" "1024x1024" "square album cover art for a dark electronic rap song, hooded man silhouette standing before a wall of glowing CRT televisions showing static, one TV glowing bright cyan like a portal, neon cyan and magenta palette, deep black background, bold graphic composition, high contrast, ultra detailed"
gen "artist.png" "864x1152" "mysterious portrait of a young slavic rap artist in a black hoodie, hood up, face half-lit by cold neon cyan light from one side and faint magenta from the other, standing in dark smoke, confident calm expression, cinematic lighting, ultra detailed"
gen "og.png" "1344x768" "wide cinematic key art: a lone man in black hoodie stands with his back to the camera facing a giant glowing wall of CRT televisions in a dark city, one screen bursts with golden light rays, neon cyan and magenta atmosphere, epic music video poster, ultra detailed"
echo "EXTRA IMAGES DONE"

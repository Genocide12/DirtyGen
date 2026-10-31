#!/bin/bash
# tools/enrich_v5.sh — полный цикл CH 02 «Смени канал» · NIGHT (v5).
# Запуск: nohup bash tools/enrich_v5.sh > logs/enrich_v5.log 2>&1 &
# Фазы: A) генерация N01-N16 (film_gen_ch2, resume, частичные пуши)
#       B) build_film_ch2  C) encode_web_ch2  D) деплой-коммит (cache-bust ?v=5)
# Страховка от откатов диска: каждый скачанный N-кадр + состояние уходят на GitHub.
set -u
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
QDIR="aivideo/film_ch2"
TOTAL=16
STATE="$QDIR/gen_state.json"
last_pushed=0

log() { echo "[$(date '+%m-%d %H:%M:%S')] $*"; }

have() { ls $QDIR/N*.mp4 2>/dev/null | wc -l; }

push_partial() {
  # страховка от отката диска: N-кадры + gen_state уходят на GitHub
  git add "$QDIR" 2>/dev/null
  if git diff --cached --quiet; then return; fi
  git pull --rebase origin main >/dev/null 2>&1 || git pull origin main >/dev/null 2>&1
  git commit -m "CH 02 v5: AI-кадры NIGHT (частично $1/16)" >/dev/null 2>&1 || return
  git push origin main >/dev/null 2>&1 && log "partial push $1/16 OK" || log "partial push FAILED"
}

# Фаза A: генерация N-кадров
log "PHASE A start: have $(have)/$TOTAL"
for i in $(seq 1 120); do
  n=$(have)
  if [ "$n" -ge "$TOTAL" ]; then log "ALL $n/$TOTAL DOWNLOADED"; break; fi
  log "gen iter $i (have $n/$TOTAL)"
  node tools/film_gen_ch2.mjs 240 3 || log "film_gen_ch2 exit $?"
  n=$(have)
  if [ $((n - last_pushed)) -ge 3 ]; then push_partial "$n"; last_pushed=$n; fi
done

n=$(have)
if [ "$n" -lt "$TOTAL" ]; then
  log "ABORT: only $n/$TOTAL after 120 iters (квота умерла?)"
  exit 3
fi
push_partial "$n"

# Фаза B: сборка таймлайна
log "PHASE B: build_film_ch2.py"
python3 tools/build_film_ch2.py || { log "BUILD FAILED"; exit 4; }

# Фаза C: кодирование (resume, повторять до успеха)
log "PHASE C: encode_web_ch2.py"
ok=0
for i in $(seq 1 12); do
  log "encode iter $i"
  if python3 tools/encode_web_ch2.py; then ok=1; break; fi
  sleep 5
done
[ "$ok" = 1 ] || { log "ENCODE FAILED after retries"; exit 5; }

# Фаза D: деплой — cache-bust ?v=5 на ch2, коммит, пуш
log "PHASE D: deploy commit+push"
sed -i 's|video/ch2_night\.mp4?v=[0-9]*"|video/ch2_night.mp4"|; s|video/ch2_night\.mp4"|video/ch2_night.mp4?v=5"|' index.html
grep -n 'ch2_night' index.html | head -2
git add -A video/ch2_night.mp4 index.html aivideo/film_ch2 tools
git pull --rebase origin main >/dev/null 2>&1 || git pull origin main >/dev/null 2>&1
git commit -m "CH 02 v5: клип NIGHT полностью из 16 AI-кадров (деплой, cache-bust ?v=5)" || log "nothing to commit"
git push origin main && log "PUSH OK" || { log "PUSH FAILED"; exit 6; }
log "ENRICH_V5_DONE_PUSHED"

#!/bin/bash
# tools/enrich_v4.sh — полный цикл обогащения ch1 (v4: AI-кадры) в фоне.
# Запуск: nohup bash tools/enrich_v4.sh > logs/enrich_v4.log 2>&1 &
# Фазы: A) генерация Q01–Q14 (film_gen, resume) B) build_film C) encode_web (resume) D) commit+push
set -u
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
QDIR="aivideo/film"
TOTAL=14
last_pushed=0

log() { echo "[$(date '+%m-%d %H:%M:%S')] $*"; }

push_partial() {
  # страховка от откката диска: скачанные Q-файлы + состояние уходят на GitHub
  git add "$QDIR" .build_film/gen_state.json 2>/dev/null
  if git diff --cached --quiet; then return; fi
  git pull --rebase origin main >/dev/null 2>&1 || git pull origin main >/dev/null 2>&1
  git commit -m "CH 01 v4: AI-кадры (частично $1/14)" >/dev/null 2>&1 || return
  git push origin main >/dev/null 2>&1 && log "partial push $1/14 OK" || log "partial push FAILED"
}

# Фаза A: генерация Q-кадров
log "PHASE A start: have $(ls $QDIR/Q*.mp4 2>/dev/null | wc -l)/$TOTAL"
for i in $(seq 1 60); do
  n=$(ls $QDIR/Q*.mp4 2>/dev/null | wc -l)
  if [ "$n" -ge $TOTAL ]; then log "ALL $n/$TOTAL DOWNLOADED"; break; fi
  log "gen iter $i (have $n/$TOTAL)"
  node tools/film_gen.mjs 240 13 || log "film_gen exit $?"
  n=$(ls $QDIR/Q*.mp4 2>/dev/null | wc -l)
  if [ $((n - last_pushed)) -ge 4 ]; then push_partial "$n"; last_pushed=$n; fi
done

n=$(ls $QDIR/Q*.mp4 2>/dev/null | wc -l)
if [ "$n" -lt $TOTAL ]; then
  log "ABORT: only $n/$TOTAL after 60 iters (квота умерла?)"
  exit 3
fi
push_partial "$n"

# Фаза B: сборка таймлайна
log "PHASE B: build_film.py"
python3 tools/build_film.py || { log "BUILD FAILED"; exit 4; }

# Фаза C: кодирование (resume, повторять до успеха)
log "PHASE C: encode_web.py"
ok=0
for i in $(seq 1 12); do
  log "encode iter $i"
  if python3 tools/encode_web.py; then ok=1; break; fi
  sleep 5
done
[ "$ok" = 1 ] || { log "ENCODE FAILED after retries"; exit 5; }

# Фаза D: финальный коммит и пуш
log "PHASE D: commit+push"
git add -A
git pull --rebase origin main >/dev/null 2>&1 || git pull origin main >/dev/null 2>&1
git commit -m "CH 01 v4: AI-кадры" || log "nothing to commit"
git push origin main && log "PUSH OK" || { log "PUSH FAILED"; exit 6; }
log "ENRICH_V4_DONE_PUSHED"

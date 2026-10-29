# CRON.md — управляющий файл cron-задачи DIRTYGEN (его читает агент по расписанию)

Цель: клип v4 для трека «Смени канал» = ВСЕ 14 AI-кадров (aivideo/film/Q01–Q14) → сборка → деплой ch1_main.mp4.
ЮЗЕР СКАЗАЛ: частичный клип НЕ собирать. Ждём 14/14.

## Прогон
1. N = число aivideo/film/Q*.mp4. Если `pgrep -f 'film_gen|build_film|encode_web'` жив — ответь «работа идёт: N/14» и законч.
2. N<14: `node tools/film_gen_par.mjs 500 4` (параллельный планировщик, до 4 задач в полёте, 429 переживает сам).
   - Повторяй запуск, пока позволяет время сессии (скрипт с resume).
   - После каждого нового кадра: `git add aivideo/film && git commit -m "CH 01 v4: кадры N/14" && git push` (страховка — откаты диска были 3 раза).
   - Отчёт одной строкой: «генерация: N/14» либо «квота закрыта: N/14».
3. N=14 (впервые): `python3 tools/build_film.py` → `python3 tools/encode_web.py` (таймаут убивает кодирование — норм, повторяй до надписи ГОТОВО) → `git add -A && git commit -m "CH 01 v4: AI-кадры" && git push` → через 90с сверить content-length https://genocide12.github.io/DirtyGen/video/ch1_main.mp4 с локальным размером файла → если изменился, деплой ок → УДАЛИ cron-задачу и отчитайся юзеру подробно.
4. Если Bash-инструмент падает 3+ раза подряд — ответь одной строкой и жди следующего прогона.

## Запрещено
- Собирать/кодировать при N<14 (юзер ждёт полный клип).
- Трогать ch2/ch3, index.html, assets/js/app.js, tools/film_gen.mjs.

## Состояние (агент обновляет после изменений)
- 2026-10-30 19:20 UTC: **9/14** — Q01,Q02,Q03,Q07,Q08,Q11,Q12,Q13,Q14. В работе: Q04 (таск создан 18:00 UTC). Очередь: Q05, Q06, Q09, Q10.
- Квота: окна нерегулярные, бывали стены 429 часами. Просто ретраить каждый прогон.

## Если диск откатился (HEAD=2befacb, нет tools/film_gen_par.mjs)
1. Токен: `git config --get remote.origin.url | sed -n 's|https://\([^:@]*\)@github.com.*|\1|p'`
2. `mv dirtygen dirtygen_salvage && git clone https://TOKEN@github.com/Genocide12/DirtyGen.git dirtygen && cd dirtygen && ln -sfn /home/z/.bun/install/global/node_modules node_modules && rm -rf dirtygen_salvage`
3. Проверить `git log --oneline -2` и продолжить с шага «Прогон».

# DIRTYGEN · лог задачи v4 (читает крон)

> Это «последний лог» в репозитории: агент обновляет его по мере изменения состояния.
> Обновлён: 2026-10-30 ~23:00 мск · HEAD: 132b1d8 · кадров: **9/14** · крон №485148 каждые 20 мин

## Факты сейчас
- Репо локально: `/home/z/my-project/dirtygen` · GitHub: `Genocide12/DirtyGen` · деплой = push в main.
- Цель: клип ch1 v4 из 14 AI-кадров (`aivideo/film/Q01–Q14.mp4`). Есть: Q01,Q02,Q03,Q07,Q08,Q11,Q12,Q13,Q14. Нет: Q04,Q05,Q06,Q09,Q10 (Q04 — таск создан, дорендерится).
- Квота видео-API: окна нерегулярные, 429 = ждать; уже созданные задачи дорендериваются и качаются сами.
- **Правило юзера: клип собирать ТОЛЬКО при 14/14. Из неполного набора НЕ собирать!**

## Задача крона (выполнять точно)
1. `pgrep -f 'film_gen|build_film|encode_web'` — если что-то работает: ответить одной строкой «работа идёт: N/14», ничего не запускать.
2. N = `ls aivideo/film/Q*.mp4 | wc -l`:
   - **N<14** → `node tools/film_gen_par.mjs 530 4` (параллельный планировщик, 429-ретраи встроены). Ответить одной строкой «генерация: N/14». Клип НЕ собирать!
   - **N=14** → ШАГ 0 (сразу, до сборки): написать юзеру будильник №1 — «✅ 14/14 — все кадры собраны, клею клип, напишу когда выложу». Потом: `python3 tools/build_film.py` → `python3 tools/encode_web.py` (таймаут убивает кодирование — это норма, resume: просто запускать повторно до надписи ГОТОВО) → `git add -A && git add -f .build_film/gen_state.json && git commit -m "CH 01 v4: AI-кадры" && git push` → ждать 90с → проверить, что content-length `https://genocide12.github.io/DirtyGen/video/ch1_main.mp4` изменился → УДАЛИТЬ cron-задачу №485148 → РАЗБУДИТЬ юзера ФИНАЛЬНЫМ сообщением: первая строка «🔔 КЛИП v4 ГОТОВ — СМЕНИ КАНАЛ !!!», дальше ссылка https://genocide12.github.io/DirtyGen/ и 3–5 строк что стало лучше в клипе (живые AI-кадры вместо слайдов).
3. Обновить этот файл (счётчик кадров, дату, HEAD) и запушить вместе с новым прогрессом.
4. Страховка от отката диска (бывало 3 раза!): после каждого нового кадра `git add aivideo/film && git add -f .build_film/gen_state.json && git commit -m "v4: N/14" && git push`.

## Если репо откатилось (файлы пропали / HEAD старый)
1. Токен: `git config --get remote.origin.url` → вырезать между `https://` и `@github.com`.
2. `cd /home/z/my-project && mv dirtygen dirtygen_salvage && git clone https://ТОКЕН@github.com/Genocide12/DirtyGen.git dirtygen && cd dirtygen && ln -sfn /home/z/.bun/install/global/node_modules node_modules && rm -rf ../dirtygen_salvage`.
3. MP3-исходники живы вне репо: `/home/z/my-project/upload/`.

## Не трогать
`video/ch2_night.mp4`, `video/ch3_dawn.mp4`, `index.html`, `assets/js/app.js`, `assets/css/`.

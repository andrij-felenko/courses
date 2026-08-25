# Скрипти — що живе, що відставне

Стан на 2026-08-25, після переведення тулінгу на дерево v7 (`PLAN.md §2`, Фаза 4).

**Головне правило:** маніфест читає й пише **тільки** `scripts/lib/manifest7.js`. У v6 схему
розбирали чотири скрипти, кожен по-своєму, — саме тому правило «нову групу створюєш сам»
тихо не працювало: одна з ланок про нього не знала. Новий скрипт, якому треба маніфест,
бере його звідти й нізвідки більше.

---

## Ядро

| файл | що робить |
|---|---|
| **`lib/manifest7.js`** | єдиний розбір схеми 7. Читання (`loadBook`, `allTopics`, `findTopic`, `groupSlugs`, `chapterSlugs`), запис (`applyOps`: `group` · `chapter` · `topic` · `ref` · `status` · `status-if` · `insert`), пошук книги (`books`, `bookDirOf`, `bookDirOfTopic`) і сигнали дубля (`dupeHints`) |
| `manifest-patch.js` | CLI поверх `applyOps`; приймає слуг книги або шлях до `manifest.json`. Легасі `op:"section"` і поле `section` перекладає в `group` |

## Письмо — Antigravity

| файл | що робить |
|---|---|
| `antigravity/newtopic.js` | нова тема в чергу. `--group` + `--chapter`; коли групи чи розділу ще немає — вимагає `--group-title`/`--group-scope`/`--chapter-title` |
| `antigravity/finish-batch.js` | єдиний дотик до маніфесту за батч: статуси, вставки, нові теми, **створення групи й розділу** |
| `checks/gate.js` · `checks/01…17` · `checks/_lib.js` · `checks/verdict.js` | сімнадцять перевірок; усі ходять через `manifestOf` у `_lib.js` |

## Письмо — Клод

| файл | що робить |
|---|---|
| `claude/write-batch.js` | повний батч. Скаут і фаза «Маніфест» тепер **локальні** — черга рахується з JSON, агенти на це не витрачаються |
| `batch-state.js` | звіряє диск із маніфестом, піднімає урваний батч; пише через `manifest7` |

## Перевірки корпусу

| файл | що робить |
|---|---|
| `linkcheck.js` | лінки за `PLAN §2.3`: книга з першого сегмента, тема з останнього; середина довгої форми — сигнал «адреса застаріла», не поломка |
| `audit-layout.js` | гейт «тек == тем»: сироти на диску, теми без теки, групи без файлів, слуг двічі |
| `guidelinks.js` | чи ведуть кроки курсу туди, де читач щось побачить |
| `wordcount.js` · `svgcheck.py` · `svgkit.py` · `textcheck.js` · `arduinocheck.js` | працюють у межах теки — переносу не помітили |

## Разові проходи (зроблені, лишені для аудиту)

`prefix-to-root.js` — `topic:` → `root:` · `retarget-books.js` — перецілення книг у лінках ·
`apply-linkchanges.js` · `fix-figrefs.js` · `claude/mark-recheck.js`

## Кампанійні воркфлоу

`claude/recheck-*` (7) · `claude/review-*` (4) · `claude/place-batch.js` ·
`claude/adjudicate-batch.js` · `claude/svgfix-prep.js` · `claude/svgfix-apply.js` ·
`claude/rules-audit.js` · `claude/arduino-fix.wf.js` — шляхи переведено на v7, самі кампанії
запускає людина за потреби.

---

## ⚠️ Відставне — НЕ запускати

Одноразові генератори доби v2–v4. Вони пишуть у теки, яких більше немає, і знають схему,
якої більше немає. Лишені як історія, не як інструмент:

- `build*.py` · `gen*.py` · `make_all*.py` · `make_docs.py` · `write_*.py` · `generate_all.py`
- `build_heap_files.js` · `make_all_topic_files.js` · `write_b64.js` · `writefile.js`
- `check_verdicts.js` · `fix_all_verdicts.js` · `temp_check.js`
- `claude/migrate-manifests-v2.js` — міграція під схему v2
- `_finish/*.js` (19 файлів) — чернетки минулих батчів
- `migrate/*` — інструмент самого переносу; його справа зроблена

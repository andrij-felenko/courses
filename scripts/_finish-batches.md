# Доробка 5 урваних батчів — стан і як продовжити

**Зріз на 2026-07-17 03:05, перевірено НЕЗАЛЕЖНИМ аудитом** (`scripts/_finish/audit.js` — рахує з диска + маніфестів, payload не читає).

> ## 🔴 УВАГА: `algorithms` — У ПОЛЬОТІ в ПАРАЛЕЛЬНІЙ сесії (станом на 03:05)
> Три вставки backpressure з'явились на диску о **02:49:58 · 02:53:53 · 03:01:28** (інтервал ~4 хв,
> остання за 3,5 хв до зрізу) — там працює живий батч сусідньої сесії. `state.js` о 02:3x показував
> `0/3`, о 03:05 — вже `3/3`.
>
> **НЕ ЗАПУСКАТИ нічого на `algorithms`, поки та сесія не звітує про кінець** — два батчі на один
> маніфест гублять правки (правило ізоляції по книзі). Далі та сесія сама зробить фази «Фігури» й
> «Маніфест» для algorithms.
>
> ⚠️ Будь-який зріз у цьому файлі про algorithms може застаріти за хвилини. Перед дією — перевір:
> `node scripts/_finish/state.js`

## Де ми

Статті — **усі 65 на диску й усі проходять канон**. Лишились тільки вставки, реєстрація в маніфесті та фігури.

| книга | статті | вставки | manifest basic→done | нові теми | стан |
|---|---|---|---|---|---|
| communications | 13/13 | 92/92 ✅ | 13/13 ✅ | 0 ✅ | **закрито** |
| programming | 13/13 | 509/509 ✅ | 13/13 ✅ | 0 ✅ | **закрито** |
| algorithms | 13/13 | **3/3 ✅ (о 03:01)** | 13/13 ✅ | 0 ✅ | 🔴 **у польоті в сусідній сесії — не чіпати** |
| math | 13/13 | **25 писати** | **0/13 ❌** | **18 завести** | батч НЕ запускався |
| electronics | 13/13 | **28 писати** | **0/13 ❌** | **1 завести** | батч НЕ запускався |

math/electronics свої нові теми заведуть САМІ — payload їх уже несе, усі 19 — у своїй книзі (крос-книжних нема, ізоляція ціла).

### Що таке ці «18 + 1 нових тем» (`_finish/explain.js` — повний список із тим, хто лінкує)

Це **не** побажання й не план розширення. Це теми, на які написані статті **вже лінкують у прозі**
(`[текст](book:math/slug)`), але яких **нема в жодному маніфесті** — тобто автори статей самі їх
наобіцяли читачеві. Саме вони й дають 29 із 93 битих лінків. Не завести = лишити лінки битими.

- **math 18**: `prime-numbers` (← лінкують 3 статті), `church-turing-thesis` ×2, `natural-numbers` ×2,
  `modular-inverse` (← 2 статті), `chomsky-hierarchy`, `godel-incompleteness`, `formal-language`,
  `binary-decision-diagram`, `boolean-satisfiability`, `zhegalkin-polynomial`, `mathematical-proof`,
  `well-ordering-principle`, `signed-multiplication`, `fibonacci-numbers`, `lcm`, `linear-diophantine`,
  `fermat-little-theorem`, `multiplicative-order`
- **electronics 1**: `lateral-pnp` (← `linear-regulator-types`)

### 🔴 «18» — це биті ЛІНКИ, а НЕ 18 тем до створення (вирішити ДО запуску math)

Перевірка на близькі збіги — `node scripts/_finish/nearmiss.js`. **13 явно нові**
(`prime-numbers`, `church-turing-thesis`, `godel-incompleteness`, `natural-numbers`,
`binary-decision-diagram`, `boolean-satisfiability`, `zhegalkin-polynomial`, `mathematical-proof`,
`well-ordering-principle`, `fibonacci-numbers`, `linear-diophantine`, `fermat-little-theorem`,
`multiplicative-order`). **~5 — сумнівні**: правильніше може бути ПЕРЕЦІЛИТИ лінк, а не плодити дубль:

| «нова» тема | що вже є в маніфесті |
|---|---|
| `formal-language` | `combinatorics/formal-grammar` «Формальні граматики (CFG, BNF)» [pending] |
| `modular-inverse` | `number-theory/modular-arithmetic` [done] |
| `lcm` | `number-theory/gcd-euclidean` «НСД і алгоритм Евкліда» (НСК зазвичай там же) |
| `chomsky-hierarchy` | вже Є вставка `logic-foundations/regular-languages/hist-chomsky-hierarchy.md` |
| `signed-multiplication` | `combinatorics/unsigned-arithmetic` «Беззнакова арифметика і переповнення» |

Фаза «Маніфест» заведе всі 18 **наосліп** → 5 потенційних дублів. Це та сама пастка, що вже спрацювала
з `asymptotic-notation` / `asymptotic-complexity`. **Розсудити ДО запуску math-батчу.**

✅ ПЕРЕВІРЕНО й НЕ дубль: `number-theory/twos-complement` «Доповняльний код» [done] проти нашого
`twos-complement-arithmetic` «Арифметика доповняльного коду» — подання проти арифметики над ним, навмисно різні.

⚠️ **Назви в payload — це `titleHint`, а не `title`, і це НАВМИСНО.** Hint — сирий текст ref-лінка,
часто в непрямому відмінку («поліномом Жегалкіна») чи обрізаний («лінійних діофантових»). Механізм
наскрізний і ПЕРЕВІРЕНИЙ: `payload.js` кладе `titleHint` → `write-batch.js` (рядок 302) велить агентові
фази «Маніфест» прочитати контекст лінка у файлі-джерелі й сформулювати правильну назву (називний
відмінок, з великої, жива українська). У маніфест сирий hint НЕ потрапляє.

## Канон v6 на 65 статтях — чисто

- `<preknowlist>` під H1: **65/65** ✅
- §3 wordcount: **65/65 у межах** ✅ (`✖`/`▽` у книгах — це СТАРІ, чужі статті, не наші)
- `figs.py`: 63 з 64 статей зі SVG мають генератор; **нема** в `electronics/sic-mosfet-power`
- **6 битих SVG** — фаза «Фігури» їх закриє: `math/functional-completeness` ×2 (генератор є, не запускався), `electronics/sic-mosfet-power` ×4 (генератора нема)

## Биті лінки: 93 — і чому це не страшно

| причина | скільки | закриється |
|---|---|---|
| файла вставки нема | 58 | коли напишуться 56 вставок |
| теми нема в маніфесті | 29 | фаза «Маніфест» (math 18 + electronics 1 унікальних) |
| зображення нема | 6 | фаза «Фігури» |

**91 із 93 закриють 3 батчі.** Лишаться 2 — **чужі, дочасні, не наші**:
- `physics/mechanics/lift-to-drag-ratio` → `book:math/trigonometry` — теми нема
- `physics/mechanics/newtons-third-law/proj-collision-sim` → `book:algorithms/complexity-computability` — **лінк на ГАЛУЗЬ, а не на тему** (§6)

## Борг із попереднього зрізу — ЗАКРИТО (перевірено)

- ✅ 2 файли-сироти (`concatenated-codes/hist-voyager-codes.md`, `adr/hist-adr-origin.md`) — прибрані
- ✅ 3 криві §6-лінки в `backpressure.md` — виправлені (тепер це нормальні ref-и на власні вставки; впадуть, коли вставки напишуться)
- ✅ 2 крос-книжні теми заведені як `pending`: `math/combinatorics/combinations`, `programming/computer-architecture/iommu`
- ℹ️ `linkfix` у `payload-<book>.json` — **НЕ помилки авторів**: у всіх 6 випадках тема-власниця реальна, файл є й зареєстрований. Це нормальні крос-темні лінки; означає лише «не наша вставка, не писати тут».

## ⚠️ ВІДКРИТЕ ПИТАННЯ — черга детальних версій (НЕ плутати з «новими темами»)

Це про **26 уже написаних статей** (13 math + 13 electronics), а НЕ про нові теми. `detailed` у payload
збирається ТІЛЬКИ з журналів (`deeperTargets`/`needDetailedSelf` від агентів статей). math/electronics
померли найраніше (журнали 28 рядків проти 62/55) → судження авторів втрачено:

| книга | detailed зараз | батч поставить pending |
|---|---|---|
| algorithms | 13× `pending` (заведено вручну) | 13 (ідемпотентно) |
| math | **13× `empty`** | **лише 1** (`pushdown-automata`) |
| electronics | **13× `empty`** | **лише 1** (`soa-power-devices`) |

26 − 2 = **24 теми лишаться `empty`** (= «писати НЕ треба») назавжди.

**Норма по книгах** (`_finish/detnorm.js`, лише теми з `basic:done`) — рішення спирається на дані:

| книга | мають детальну | `empty` |
|---|---|---|
| communications | 96% | 2% |
| math | **95%** | **2%** (1 із 58!) |
| algorithms | 99% | 1% |
| programming | 84% | 16% |
| electronics | 59% | 41% |

electronics 41% нерівні по галузях (`_finish/detnorm2.js`):

| галузь | мають детальну | наших тем |
|---|---|---|
| **power-electronics** | **84%** (101 pending vs 19 empty) | **10** |
| analog | 33% | 2 (`transistor-switch`, `pwm`) |
| digital | 36% | 1 (`gpio`) |

**Висновок:**
- **math 13 → `pending`**: норма 95%, `empty` лише 1 на 58. Наші 13× `empty` — різка аномалія.
- **electronics power-electronics 10 → `pending`**: норма 84%.
- **electronics analog+digital 3 — неоднозначно** (норма 33–36%). Гіпотезу «більша стаття → потрібна
  детальна» ПЕРЕВІРЕНО й СПРОСТОВАНО (`_finish/detsize.js`): у analog ті, що БЕЗ детальної, навіть
  більші (медіана 2036w проти 1610w). Розмір не дискримінує → лишити `empty` за більшістю їхніх
  галузей, або судити поштучно.

**Рекомендація: 23 → `pending`** (13 math + 10 power-electronics), 3 лишити `empty`.
Серійна правка маніфесту, дешево, ПІСЛЯ батчів.

## Як продовжити

**`resumeFromRunId` НЕ вживати** — він same-session-only; батчі йшли в сесіях `6752e8fc…`/`c4e9035a…`, ми вже не там. Натомість — свіжий прогін: payload уже перезібраний і **досі точний** (аудит збігається з ним один-в-один), регенерувати не треба.

```
Workflow scriptPath="scripts/write-batch.js" args=<вміст scripts/_finish/args-<book>.json>
```

**Args уже durable в репо** (`scripts/_finish/`, перенесено з %TEMP% 2026-07-17 — тимчасову теку могло вимести):
- `skipArticles: [13 slug]` — статті НЕ переписуються;
- `inserts` — лише ненаписані; `insertsDone` — написані (тільки реєстрація);
- `briefFile` → `scripts/_finish/payload-<book>.json` (перецілено на durable-копію);
- `limit: 13` (⚠️ без нього дефолт 10 мовчки ріже чергу).

**Скільки за раз.** 56 вставок = 56 opus-max агентів; один батч — пул 4. П'ять паралельно (20 агентів) — саме це з'їло ліміт. По **1–2 книги за раз**. Порядок за розміром: **algorithms (3) → math (25) → electronics (28)**. math і electronics — різні маніфести, тож ізоляція дозволяє їх паралельно; але це 53 агенти, краще послідовно.

Регенерація payload (якщо колись знадобиться) — журнали живі:
`C:\Users\andri\.claude\projects\E--develop-courses\6752e8fc-…\subagents\workflows\{wf_733c29c7-cb1,wf_2582bc1c-4b0,wf_a94e7a56-553,wf_562b6642-f12,wf_8cb7a918-6b1}`
`cd scripts/_finish && node payload.js <book> && node mkargs.js <book>` (⚠️ mkargs віддасть briefFile на %TEMP% — перецілити).

## Фінальна перевірка після батчів

```bash
node scripts/linkcheck.js          # 93 → мають лишитись 2 (чужі physics)
node scripts/wordcount.js book/<book> --all
node scripts/_finish/audit.js      # вставок БРАКУЄ → 0, незаведених тем → 0
```

## Що змінено в `scripts/write-batch.js` (зворотно сумісно, ще не закомічено)

Нові опційні args; без них поведінка стара:
- `skipArticles: true | ["slug",…]` — пропустити фазу «Статті» цілком / для перелічених тем;
- `inserts` / `newTopics` / `detailed` — подати те, що мали повернути вбиті агенти;
- `insertsDone` — вставки на диску: зареєструвати, не переписувати;
- `briefFile` — JSON із брифами (не гнати 35 КБ через args);
- фаза «Фігури» тепер пише `figs.py`, якщо стаття підключає SVG, а генератора нема (було: «нема фігур» і 29 битих картинок).

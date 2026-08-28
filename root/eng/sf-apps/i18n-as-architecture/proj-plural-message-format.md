# ⚙️ Формувальник повідомлень: як усередині обирається форма й складається фраза

Нижче — робочий формувальник на півтори сотні рядків: він бере локаль, ключ повідомлення й торбу іменованих значень, а віддає готову фразу — і не містить жодного слова про граматику якоїсь мови. Скільки форм має слово, яку з них узяти для числа 21, у якому місці речення стоїть саме число — усе це лежить у даних поруч із перекладом, і тому нову мову доливають, не торкаючись коду.

<preknowlist>
- [Абстрактне синтаксичне дерево (AST)](root:sf-lang/abstract-syntax-tree) — текст розбирають один раз у дерево вузлів, а далі працюють із деревом, а не з рядком; тут шаблон повідомлення стає саме таким деревом.
- [Рекурсія](root:sf-algorithms/recursion) — гілка вибору всередині шаблону є повноцінним повідомленням, тож і розбір, і обчислення природно викликають самі себе.
</preknowlist>

## Що має вміти межа

Домовмося про контракт, перш ніж писати. На вхід приходять три речі:

```
locale = "uk-UA"            локаль читача
key    = "files.added"      КЛЮЧ повідомлення, а не текст
args   = { actor: "Оксана", gender: "female", count: 3, folder: "Звіти" }
```

На виході — один рядок, готовий до показу.

Дві заборони роблять цей контракт нетривіальним. Перша: у коді не сміє з'явитися жодне порівняння з числом — ані `count === 1`, ані `count % 10`. Друга: код не сміє склеювати фразу зі шматків. Обидві про одне. Щойно програма пише `"У вас " + count + " нових повідомлень"`, вона вже мовчки ухвалила два рішення про мову: що число стоїть посередині й що слово після нього не міняється. Для японської неправда і перше, і друге.

## Три речі, що залежать від мови

Покладімо поруч шаблони одного ключа для трьох мов — і відмінності стануть видимі:

```
uk  {gender, select, female {{actor} додала} other {{actor} додав}}
    {count, plural, one {# файл} few {# файли} many {# файлів} other {# файлу}}
    до теки «{folder}»

en  {actor} added {count, plural, one {# file} other {# files}} to “{folder}”

ja  {actor}が「{folder}」に{count}件のファイルを追加しました
```

Відмінностей три — і кожну з них інакше довелося б зашивати в код. **Скільки гілок** має вибір: англійській вистачає двох, українській треба чотирьох. **Яку гілку взяти** для конкретного числа: правило в кожної мови своє. І **де що стоїть**: японська виносить теку на початок речення, число супроводжує лічильним словом 件 і нічого не змінює в самому слові «файл»; українська натомість змінює ще й дієслово за родом того, хто діяв, — чого англійська не робить узагалі.

Звідси випливає, чому місця в шаблоні **іменовані**, а не позиційні. Аргументи приходять торбою `{actor, gender, count, folder}`; кожна мова бере з неї те, що їй потрібно, і в тому порядку, який їй потрібен, а значення, яких вона не вживає, просто лишаються в торбі. Позиційне `%1 %2 %3` цього не дозволяє: воно нав'язує перекладачеві порядок і не дає йому дотягтися до значення, яке його мові раптом знадобилося, а англійській — ні. Рід діяча — саме такий випадок: англійський шаблон `gender` не згадує жодного разу, український без нього не складеться.

## Половина перша: яка форма

Вибір форми — чиста функція від двох речей: локалі й числа. Її вже написали за нас: таблиця правил CLDR лежить усередині рушія. У браузері та Node її віддає вбудований `Intl`, у Python — Babel, бо в стандартній бібліотеці таблиці CLDR немає.

:::tabs
```ts
const uk = new Intl.PluralRules("uk");

uk.resolvedOptions().pluralCategories;
// [ 'one', 'few', 'many', 'other' ]  — які гілки взагалі потрібні цій мові

[1, 2, 5, 11, 21, 1.5].map(n => `${n}→${uk.select(n)}`);
// [ '1→one', '2→few', '5→many', '11→many', '21→one', '1.5→other' ]

new Intl.NumberFormat("uk").format(1234.5);   // '1 234,5'
new Intl.NumberFormat("en").format(1234.5);   // '1,234.5'
```
```python
# Таблиці CLDR у стандартній бібліотеці немає — її дає Babel.
from decimal import Decimal
from babel import Locale
from babel.numbers import format_decimal

uk = Locale.parse("uk")

[f"{n}→{uk.plural_form(n)}" for n in (1, 2, 5, 11, 21, Decimal("1.5"))]
# ['1→one', '2→few', '5→many', '11→many', '21→one', '1.5→other']

format_decimal(1234.5, locale="uk")   # '1 234,5'
format_decimal(1234.5, locale="en")   # '1,234.5'
```
:::

Усередині немає магії — є правило, записане мовою CLDR. Для української воно таке:

```
uk · кількісні числівники
one    v = 0 і i % 10 = 1 і i % 100 ≠ 11              1, 21, 31, 101, 1001
few    v = 0 і i % 10 = 2..4 і i % 100 ≠ 12..14       2, 3, 4, 22, 102
many   v = 0 і (i % 10 = 0 або i % 10 = 5..9
                або i % 100 = 11..14)                 0, 5..19, 100, 1000
other  решта                                          0.5, 1.5, 10.0
```

Літери — це операнди, які CLDR добуває з числа: `n` — його модуль, `i` — ціла частина, `v` — скільки в записі числа **видимих** десяткових знаків разом із нулями в кінці. Останній операнд пояснює найдивнішу на позір гілку. Українська для цілих чисел має три форми, а четверта, `other`, чекає на дробові: «1,5 файлу», «0,5 ставки». Умова `v = 0` у перших трьох гілках якраз і відводить дроби до неї. А «1» і «1,0» для правила — різні числа, хоч для арифметики однакові: у першого `v` дорівнює нулю, у другого — одиниці.

Це правило написане не для того, щоб його переписували в код. Найгірше, що можна зробити, — скопіювати його в ланцюжок `if`: CLDR час від часу правила уточнює, копія з ними розійдеться, і розійдеться мовчки — вивід стане граматично неправильним, але програма не впаде.

## Половина друга: шаблон — це дерево

Друга половина роботи — сам шаблон. Його синтаксис навмисне бідний, бо його редагує перекладач, а не програміст:

```
повідомлення := ( текст | місце )*
місце        := '{' ім'я '}'
              | '{' ім'я ',' 'plural' ',' [ 'offset:' ціле ] гілка+ '}'
              | '{' ім'я ',' 'select' ',' гілка+ '}'
гілка        := ( мітка | '=' число ) '{' повідомлення '}'
```

Плюс одна дрібниця: `#` усередині гілки означає саме число, уже відформатоване за локаллю. Останній рядок граматики — найважливіший: тіло гілки саме́ є повідомленням, тож усередині нього знову можуть стояти місця й вибори. Звідси рекурсія і в розбирачі, і в обчислювачі.

Це підмножина ICU MessageFormat — нотації з бібліотеки ICU (International Components for Unicode), що стала спільною мовою каталогів перекладу. Мітки гілок (`one`, `few`, `many`, `other`) — ті самі, що їх видає таблиця правил; саме на цьому стику дві половини й сходяться.

![Шаблон розбирають у дерево; правила локалі обирають гілку за числом; на місце # стає відформатоване число](/root/eng/sf-apps/i18n-as-architecture/img/format-pipeline.svg)
*Розбір відбувається раз на ключ, а далі кожен показ — це обхід готового дерева з торбою аргументів.*

## Розбір

Розбирач — рекурсивний спуск на індексі `i`. Два взаємні виклики: `body` збирає текст із дірками, `hole` розбирає одне місце й кличе `body` для кожної гілки.

```ts
type Node =
  | { t: "text"; v: string }                       // дослівний шматок
  | { t: "arg"; name: string }                     // {folder}
  | { t: "hash" }                                  // # усередині гілки
  | { t: "choice"; name: string; kind: "plural" | "select";
      offset: number; branches: Record<string, Node[]> };

function parse(src: string): Node[] {
  let i = 0;
  const fail = (why: string): never => {
    throw new SyntaxError(`${why} — позиція ${i} у «${src}»`);
  };
  const ws = () => { while (i < src.length && /\s/.test(src[i])) i++; };
  const word = (): string => {
    const from = i;
    while (i < src.length && /[A-Za-z0-9_.=+-]/.test(src[i])) i++;
    return i > from ? src.slice(from, i) : fail("очікував ім'я або мітку");
  };

  // Текст із дірками. inBranch=true — спиняємось на '}' і розуміємо '#'.
  const body = (inBranch: boolean): Node[] => {
    const out: Node[] = [];
    let buf = "";
    const flush = () => { if (buf) { out.push({ t: "text", v: buf }); buf = ""; } };

    while (i < src.length) {
      const c = src[i];
      if (c === "}" && inBranch) break;
      if (c === "#" && inBranch) { flush(); out.push({ t: "hash" }); i++; continue; }
      if (c === "{") { flush(); out.push(hole()); continue; }
      if (c === "'") {                          // апостроф за правилом ICU 4.8+
        const next = src[i + 1];
        if (next === "'") { buf += "'"; i += 2; continue; }   // '' → один апостроф
        if (next && "{}#".includes(next)) {                   // '…' → дослівний текст
          i++;
          while (i < src.length && src[i] !== "'") buf += src[i++];
          i++;
          continue;
        }
        buf += "'"; i++; continue;               // звичайний апостроф: «п'ять»
      }
      buf += c; i++;
    }
    flush();
    return out;
  };

  const hole = (): Node => {
    i++; ws();                                             // з'їли '{'
    const name = word(); ws();
    if (src[i] === "}") { i++; return { t: "arg", name }; } // просте місце {folder}
    if (src[i] !== ",") fail("очікував ',' або '}'");
    i++; ws();
    const kind = word();
    if (kind !== "plural" && kind !== "select") fail(`невідомий різновид «${kind}»`);
    ws();
    if (src[i] !== ",") fail("очікував ',' після різновиду");
    i++; ws();
    let offset = 0;
    if (src.startsWith("offset:", i)) { i += "offset:".length; offset = Number(word()); ws(); }

    const branches: Record<string, Node[]> = {};
    while (i < src.length && src[i] !== "}") {
      const label = word(); ws();                          // one | few | =0 | female…
      if (src[i] !== "{") fail(`очікував '{' після мітки «${label}»`);
      i++;
      branches[label] = body(true);                        // гілка — теж повідомлення
      if (src[i] !== "}") fail(`незакрита гілка «${label}»`);
      i++; ws();
    }
    if (src[i] !== "}") fail("незакрите місце");
    i++;
    if (!branches.other) fail("гілка other обов'язкова");
    return { t: "choice", name, kind, offset, branches };
  };

  return body(false);
}
```

Гілка про апостроф посеред `body` варта окремого погляду. В ICU апостроф — знак цитування: він каже «далі йде дослівний текст, не чіпай його». Для української це була б катастрофа, бо апостроф у нас стоїть усередині слів: «п'ять», «об'єднати», «ім'я». Тому починаючи з ICU 4.8 діє послаблене правило: апостроф відкриває цитату лише тоді, коли **одразу за ним** стоїть символ, який узагалі потребує цитування — `{`, `}` або `#`. Перед літерою це просто апостроф. Наш розбирач повторює цю поведінку рівно так само — а разом із нею успадковує й пастку, яку вона несе.

## Обчислення

Дерево обходять із торбою аргументів. Єдина хитрість — параметр `hash`: спускаючись у гілку вибору, обчислювач несе туди вже відформатоване число, щоб вузол `#` знав, що́ підставити.

```ts
type NumOpts = Intl.NumberFormatOptions & { type?: "cardinal" | "ordinal" };

const memo = <T,>(cache: Map<string, T>, key: string, make: () => T): T => {
  let v = cache.get(key);
  if (v === undefined) { v = make(); cache.set(key, v); }
  return v;
};
const nfs = new Map<string, Intl.NumberFormat>();
const prs = new Map<string, Intl.PluralRules>();

// ОДИН набір опцій живить і форматувальник чисел, і вибір форми:
// операнд v (скільки видимих десяткових) мусить збігтися в обох.
const nf = (loc: string, o: NumOpts) =>
  memo(nfs, loc + JSON.stringify(o), () => new Intl.NumberFormat(loc, o));
const pr = (loc: string, o: NumOpts) =>
  memo(prs, loc + JSON.stringify(o), () => new Intl.PluralRules(loc, o));

function run(nodes: Node[], args: Record<string, unknown>,
             loc: string, o: NumOpts, hash: string | null): string {
  let out = "";
  for (const n of nodes) {
    if (n.t === "text") { out += n.v; continue; }
    if (n.t === "hash") { out += hash ?? ""; continue; }
    if (n.t === "arg") {
      const v = args[n.name];
      out += typeof v === "number" ? nf(loc, o).format(v) : String(v);
      continue;
    }
    const v = args[n.name];
    let label: string;
    let inner = hash;
    if (n.kind === "plural") {
      const num = Number(v);
      const shown = num - n.offset;              // offset діє на форму й на '#'
      label = `=${num}` in n.branches            // точний збіг — за ПОВНИМ числом
        ? `=${num}`
        : pr(loc, o).select(shown);              // інакше — категорія від локалі
      inner = nf(loc, o).format(shown);
    } else {
      label = String(v) in n.branches ? String(v) : "other";
    }
    out += run(n.branches[label] ?? n.branches.other, args, loc, o, inner);
  }
  return out;
}
```

Гілка `plural` і гілка `select` різняться лише способом дібрати мітку: перша питає правила локалі, друга просто зіставляє рядок. Усе інше — спільне, і це не збіг: вибір форми множини є окремим випадком загальнішої дії «обрати гілку за значенням аргументу».

## Межа

Лишилося зв'язати каталог, запасний ланцюжок локалей і кеш дерев. Функцію на самій межі за традицією i18n звуть найкоротше з можливого — `t`, бо трапляється вона в коді на кожному кроці:

```ts
const BASE = "en";                               // мова-основа проєкту
const catalog: Record<string, Record<string, string>> = {
  uk: {
    "files.added":
      "{gender, select, female {{actor} додала} other {{actor} додав}} " +
      "{count, plural, one {# файл} few {# файли} many {# файлів} other {# файлу}} " +
      "до теки «{folder}»",
  },
  en: {
    "files.added":
      "{actor} added {count, plural, one {# file} other {# files}} to “{folder}”",
  },
  ja: {
    "files.added": "{actor}が「{folder}」に{count}件のファイルを追加しました",
  },
};

const trees = new Map<string, Node[]>();

function t(loc: string, key: string,
           args: Record<string, unknown> = {}, o: NumOpts = {}): string {
  const chain = [loc, loc.split("-")[0], BASE];          // uk-UA → uk → en
  const lang = chain.find(l => catalog[l]?.[key]);
  if (!lang) return key;                                 // перекладу нема — видно ключ
  const tree = memo(trees, lang + " " + key, () => parse(catalog[lang][key]));
  const fmt = loc.startsWith(lang) ? loc : lang;         // числа — у мові шаблону
  return run(tree, args, fmt, o, null);
}
```

Виклик і те, що з нього виходить:

```ts
const who = { actor: "Оксана", gender: "female", folder: "Звіти" };
for (const n of [1, 3, 5, 21, 1000, 1.5])
  console.log(t("uk-UA", "files.added", { ...who, count: n }));
```

```
Оксана додала 1 файл до теки «Звіти»
Оксана додала 3 файли до теки «Звіти»
Оксана додала 5 файлів до теки «Звіти»
Оксана додала 21 файл до теки «Звіти»
Оксана додала 1 000 файлів до теки «Звіти»
Оксана додала 1,5 файлу до теки «Звіти»

Oksana added 1 file to “Reports”          ← t("en", …, { count: 1 })
Oksana added 3 files to “Reports”
オクサナが「レポート」に3件のファイルを追加しました   ← t("ja", …, { count: 3 })
```

Дві дрібниці в цьому виводі ніхто спеціально не програмував. «1 000» — це нерозривний пробіл між розрядами, бо так групує числа українська локаль; англійська в тому самому місці поставила б кому. «1,5» — кома десятковим роздільником, з тієї самої причини. Обидві приїхали разом із локаллю, бо число проходить через `Intl.NumberFormat`, а не через `String(n)`.

> 🔧 **Навіщо це.** Найтонше місце всієї конструкції — рядок, де `nf` і `pr` дістають **той самий** об'єкт опцій. Категорію обирають не за математичним значенням числа, а за тим, як воно **виглядає** після форматування. Покажіть 1.4 з нульовою точністю — читач побачить «1» і чекатиме «1 файл»; правило, спитане про сире 1.4, поверне `other` і дасть «1 файлу». Один спільний набір опцій робить цю помилку структурно неможливою, тоді як два окремі виклики роблять її неминучою.

Ось як ця розбіжність виглядає, коли опції розходяться:

```ts
new Intl.NumberFormat("uk", { maximumFractionDigits: 0 }).format(1.4);  // '1'
new Intl.PluralRules("uk").select(1.4);                                 // 'other' → «1 файлу»
new Intl.PluralRules("uk", { maximumFractionDigits: 0 }).select(1.4);   // 'one'   → «1 файл»
```

## Синтаксичний парсер ICU MessageFormat зі статичним буфером (C99 та C++20)

У високорівневих середовищах (V8, Node.js, Python) синтаксичний розбір рядків спирається на регулярні вирази, створення динамічних об'єктів у купі та збирання сміття. Однак у системному програмуванні, на вбудованих контролерах та у високопродуктивних рушіях рендерингу виділення пам'яті в купі (`malloc`/`new`) є неприпустимим через недетермінований час виконання та небезпеку вичерпання RAM.

Для таких середовищ парсер ICU MessageFormat будується за принципом **нульового динамічного виділення пам'яті (Zero-Allocation AST)**.

### Архітектура детермінованого розбору

1. **Лексичний автомат і сканування токенів (LL(1) Lexer)**:
   Сканер обробляє вхідний потік символів UTF-8 за один послідовний прохід. На відміну від складних граматик, формат MessageFormat вимагає глибини попереднього перегляду лише в 1 символ (LL(1)). Символ `{` ініціює перехід автомата в режим розбору аргументу або керуючої конструкції (`select` / `plural`), символ `}` позначає завершення поточного блоку або гілки, а кома `,` слугує роздільником параметрів.
2. **Представлення AST у статичному пулі вузлів**:
   Замість виділення динамічних об'єктів для кожного вузла абстрактного синтаксичного дерева, парсер використовує фіксований плоский масив структур `msg_node_t` або `std::array<Node, N>`. Усі текстові фрагменти зберігаються не як копії рядків, а як легковажні зрізи пам'яті (вказівник на початок у вихідному шаблоні плюс довжина `size_t len` або `std::string_view`).
3. **Екранування та сумісність з апострофами ICU**:
   Специфікація ICU вимагає коректної обробки одинарного апострофа `'`. Парсер підтримує правило швидкого екранування: послідовність `''` перетворюється на один літеральний апостроф, а фрагмент `'{'` інтерпретується як звичайний символ фігурної дужки, а не початок блоку підстановки.
4. **Обчислення в обмежений вихідний буфер**:
   Під час виконання (Evaluation Phase) сформоване дерево вузлів рекурсивно обходиться із записом результату безпосередньо у наданий викликачем статичний вихідний буфер. Контроль меж гарантує відсутність переповнення буфера (Buffer Overflow Protection): якщо згенерований рядок перевищує ємність, вивід безпечно обрізається з коректним додаванням нульового байта `\0`.
5. **Роздільна диспетчеризація числових форм**:
   Вузол типу `#` усередині гілки множини автоматично підставляє активне числове значення, передане в контексті обчислення, забезпечуючи точну відповідність формі слова без дублювання аргументів у торбі значень.

### Граматичні інваріанти та крайові випадки синтаксичного розбору

Реалізація парсера ICU MessageFormat на мовах системного програмування C99 та C++20 вимагає суворого дотримання низки інваріантів граматики:

1. **Вкладеність конструкцій вибору (Nested Choice Resolution)**:
   Шаблони часто комбінують вибір за родом та множиною, наприклад: `{gender, select, female {{count, plural, one {Вона додала # файл} few {Вона додала # файли} other {Вона додала # файлів}}} other {{count, plural, one {Він додав # файл} few {Він додав # файли} other {Він додав # файлів}}}}`.
   Парсер обробляє таку вкладеність через рекурсивний спуск: кожна гілка вибору розбирається як ізольоване повідомлення, чиї дочірні вузли посилаються на діапазон у загальному масиві вузлів `[child_start .. child_start + child_count)`. Це дозволяє уникнути будь-яких динамічних алокацій для побудови ієрархічних зв'язків між вузлами.

2. **Пріоритет точних числових збігів (`=0`, `=1`) над лінгвістичними категоріями**:
   У граматиці ICU точний числовий збіг (наприклад, `=0 {Немає файлів}`) має абсолютний пріоритет над граматичною категорією множини (`zero`, `one`, `few`, `many`, `other`). Під час оцінки гілок формувальник спочатку зіставляє строковий вигляд числа з префіксом `=` (наприклад, перевіряє наявність мітки `=0` для значення `0`), і лише за відсутності прямого збігу звертається до таблиці або функції категорій CLDR.

3. **Обробка модифікатора `offset:N`**:
   Якщо блок множини містить параметр зміщення `offset:N`, точне порівняння `=value` перевіряється за повним значенням аргументу `n`, тоді як граматична категорія та підстановка у маркер `#` обчислюються для скоригованого значення `n - offset`. Це забезпечує коректне формулювання фраз на зразок «Ви та ще 2 користувачі вподобали це» при загальній кількості користувачів 3.

4. **Захист від некоректних шаблонів та безпечний відкат (Fail-Safe Evaluation)**:
   Якщо переданий шаблон містить незакриту дужку `}`, відсутню обов'язкову гілку `other` або невідомий тип селектора, парсер не перериває виконання програми та не викликає аварійного завершення. Натомість повертається статус помилки `MSG_ERR_*` або `std::unexpected(ParseError)`, а підсистема інтерфейсу користувача безпечно виводить сирий текст шаблону або ім'я ключа без зависання системи.

:::tabs
```c
/* Синтаксичний парсер та формувальник повідомлень зі статичним буфером на C99 */
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MSG_MAX_NODES 32
#define MSG_MAX_BRANCHES 8

typedef enum {
    MSG_ERR_OK = 0,
    MSG_ERR_SYNTAX,
    MSG_ERR_BUFFER_OVERFLOW,
    MSG_ERR_UNCLOSED_BRACE,
    MSG_ERR_MISSING_OTHER
} msg_err_t;

typedef enum {
    NODE_TEXT,
    NODE_ARG,
    NODE_HASH,
    NODE_CHOICE
} msg_node_type_t;

typedef struct {
    const char *ptr;
    size_t len;
} msg_str_t;

typedef struct {
    msg_str_t label;
    uint16_t child_start;
    uint16_t child_count;
} msg_branch_t;

typedef struct {
    msg_node_type_t type;
    msg_str_t str;
    bool is_plural;
    int32_t offset;
    uint16_t branch_start;
    uint16_t branch_count;
} msg_node_t;

typedef struct {
    const char *src;
    size_t len;
    size_t pos;
    msg_node_t nodes[MSG_MAX_NODES];
    size_t node_count;
    msg_branch_t branches[MSG_MAX_BRANCHES];
    size_t branch_count;
    msg_err_t err;
} msg_parser_t;

typedef struct {
    const char *name;
    const char *val_str;
    int32_t val_num;
    bool is_num;
} msg_arg_val_t;

typedef const char* (*msg_plural_fn)(int32_t num);

static bool str_eq(msg_str_t s, const char *lit) {
    size_t llen = strlen(lit);
    return s.len == llen && memcmp(s.ptr, lit, llen) == 0;
}

static void skip_ws(msg_parser_t *p) {
    while (p->pos < p->len && (p->src[p->pos] == ' ' || p->src[p->pos] == '\t' ||
                               p->src[p->pos] == '\n' || p->src[p->pos] == '\r')) {
        p->pos++;
    }
}

static msg_str_t parse_ident(msg_parser_t *p) {
    skip_ws(p);
    size_t start = p->pos;
    while (p->pos < p->len) {
        char c = p->src[p->pos];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '=') {
            p->pos++;
        } else {
            break;
        }
    }
    msg_str_t res = { .ptr = p->src + start, .len = p->pos - start };
    return res;
}

static uint16_t parse_message(msg_parser_t *p, bool in_branch, uint16_t *out_count);

static uint16_t parse_choice(msg_parser_t *p) {
    p->pos++; /* Пропуск '{' */
    msg_str_t arg_name = parse_ident(p);
    skip_ws(p);
    
    if (p->pos < p->len && p->src[p->pos] == '}') {
        p->pos++;
        if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; return 0; }
        uint16_t idx = (uint16_t)p->node_count++;
        p->nodes[idx] = (msg_node_t){ .type = NODE_ARG, .str = arg_name };
        return idx;
    }
    
    if (p->pos >= p->len || p->src[p->pos] != ',') { p->err = MSG_ERR_SYNTAX; return 0; }
    p->pos++;
    
    msg_str_t kind = parse_ident(p);
    bool is_plural = str_eq(kind, "plural");
    if (!is_plural && !str_eq(kind, "select")) { p->err = MSG_ERR_SYNTAX; return 0; }
    
    skip_ws(p);
    if (p->pos >= p->len || p->src[p->pos] != ',') { p->err = MSG_ERR_SYNTAX; return 0; }
    p->pos++;
    
    if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; return 0; }
    uint16_t choice_idx = (uint16_t)p->node_count++;
    uint16_t b_start = (uint16_t)p->branch_count;
    uint16_t b_count = 0;
    bool has_other = false;
    
    while (p->pos < p->len && p->src[p->pos] != '}') {
        skip_ws(p);
        if (p->pos < p->len && p->src[p->pos] == '}') break;
        
        msg_str_t lbl = parse_ident(p);
        if (lbl.len == 0) { p->err = MSG_ERR_SYNTAX; return choice_idx; }
        if (str_eq(lbl, "other")) has_other = true;
        
        skip_ws(p);
        if (p->pos >= p->len || p->src[p->pos] != '{') { p->err = MSG_ERR_SYNTAX; return choice_idx; }
        p->pos++;
        
        if (p->branch_count >= MSG_MAX_BRANCHES) { p->err = MSG_ERR_BUFFER_OVERFLOW; return choice_idx; }
        uint16_t b_idx = (uint16_t)p->branch_count++;
        b_count++;
        
        uint16_t child_cnt = 0;
        uint16_t child_st = parse_message(p, true, &child_cnt);
        p->branches[b_idx] = (msg_branch_t){ .label = lbl, .child_start = child_st, .child_count = child_cnt };
        
        if (p->pos >= p->len || p->src[p->pos] != '}') { p->err = MSG_ERR_UNCLOSED_BRACE; return choice_idx; }
        p->pos++;
    }
    
    if (p->pos >= p->len || p->src[p->pos] != '}') { p->err = MSG_ERR_UNCLOSED_BRACE; return choice_idx; }
    p->pos++;
    
    if (!has_other) { p->err = MSG_ERR_MISSING_OTHER; }
    
    p->nodes[choice_idx] = (msg_node_t){
        .type = NODE_CHOICE,
        .str = arg_name,
        .is_plural = is_plural,
        .offset = 0,
        .branch_start = b_start,
        .branch_count = b_count
    };
    return choice_idx;
}

static uint16_t parse_message(msg_parser_t *p, bool in_branch, uint16_t *out_count) {
    uint16_t start_idx = (uint16_t)p->node_count;
    uint16_t count = 0;
    size_t txt_start = p->pos;
    
    while (p->pos < p->len && p->err == MSG_ERR_OK) {
        char c = p->src[p->pos];
        if (in_branch && c == '}') break;
        
        if (c == '{' || (in_branch && c == '#')) {
            if (p->pos > txt_start) {
                if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; break; }
                p->nodes[p->node_count++] = (msg_node_t){
                    .type = NODE_TEXT,
                    .str = { .ptr = p->src + txt_start, .len = p->pos - txt_start }
                };
                count++;
            }
            if (c == '#') {
                if (p->node_count >= MSG_MAX_NODES) { p->err = MSG_ERR_BUFFER_OVERFLOW; break; }
                p->nodes[p->node_count++] = (msg_node_t){ .type = NODE_HASH };
                count++;
                p->pos++;
                txt_start = p->pos;
            } else {
                parse_choice(p);
                count++;
                txt_start = p->pos;
            }
        } else {
            p->pos++;
        }
    }
    if (p->pos > txt_start && p->err == MSG_ERR_OK) {
        if (p->node_count < MSG_MAX_NODES) {
            p->nodes[p->node_count++] = (msg_node_t){
                .type = NODE_TEXT,
                .str = { .ptr = p->src + txt_start, .len = p->pos - txt_start }
            };
            count++;
        }
    }
    *out_count = count;
    return start_idx;
}

static size_t format_eval(const msg_parser_t *p, uint16_t start, uint16_t count,
                          const msg_arg_val_t *args, size_t argc, msg_plural_fn pl_fn,
                          int32_t active_num, char *out, size_t out_cap, size_t *out_pos) {
    for (uint16_t i = 0; i < count; ++i) {
        const msg_node_t *n = &p->nodes[start + i];
        if (n->type == NODE_TEXT) {
            size_t copy_len = n->str.len;
            if (*out_pos + copy_len >= out_cap) copy_len = out_cap > *out_pos ? out_cap - *out_pos - 1 : 0;
            memcpy(out + *out_pos, n->str.ptr, copy_len);
            *out_pos += copy_len;
        } else if (n->type == NODE_HASH) {
            char num_buf[16];
            int nlen = snprintf(num_buf, sizeof(num_buf), "%d", (int)active_num);
            size_t copy_len = (size_t)nlen;
            if (*out_pos + copy_len >= out_cap) copy_len = out_cap > *out_pos ? out_cap - *out_pos - 1 : 0;
            memcpy(out + *out_pos, num_buf, copy_len);
            *out_pos += copy_len;
        } else if (n->type == NODE_ARG) {
            for (size_t a = 0; a < argc; ++a) {
                if (str_eq(n->str, args[a].name)) {
                    const char *val = args[a].val_str;
                    char tmp[16];
                    if (args[a].is_num) {
                        snprintf(tmp, sizeof(tmp), "%d", (int)args[a].val_num);
                        val = tmp;
                    }
                    size_t vlen = strlen(val);
                    if (*out_pos + vlen >= out_cap) vlen = out_cap > *out_pos ? out_cap - *out_pos - 1 : 0;
                    memcpy(out + *out_pos, val, vlen);
                    *out_pos += vlen;
                    break;
                }
            }
        } else if (n->type == NODE_CHOICE) {
            const char *matched_lbl = "other";
            int32_t next_num = active_num;
            for (size_t a = 0; a < argc; ++a) {
                if (str_eq(n->str, args[a].name)) {
                    if (n->is_plural && args[a].is_num) {
                        next_num = args[a].val_num;
                        matched_lbl = pl_fn ? pl_fn(next_num) : "other";
                    } else if (!n->is_plural && !args[a].is_num) {
                        matched_lbl = args[a].val_str;
                    }
                    break;
                }
            }
            uint16_t sel_idx = 0;
            for (uint16_t b = 0; b < n->branch_count; ++b) {
                const msg_branch_t *br = &p->branches[n->branch_start + b];
                if (str_eq(br->label, matched_lbl)) { sel_idx = b; break; }
                if (str_eq(br->label, "other")) sel_idx = b;
            }
            const msg_branch_t *chosen = &p->branches[n->branch_start + sel_idx];
            format_eval(p, chosen->child_start, chosen->child_count, args, argc, pl_fn, next_num, out, out_cap, out_pos);
        }
    }
    if (*out_pos < out_cap) out[*out_pos] = '\0';
    return *out_pos;
}
```
```cpp
// Синтаксичний парсер та формувальник повідомлень зі статичним буфером на C++20
#include <array>
#include <cstdint>
#include <cstring>
#include <expected>
#include <span>
#include <string_view>

namespace embedded::msg {

enum class ParseError : uint8_t {
    SyntaxError,
    BufferOverflow,
    UnclosedBrace,
    MissingOther
};

enum class NodeType : uint8_t {
    Text,
    Arg,
    Hash,
    Choice
};

struct Branch {
    std::string_view label{};
    uint16_t child_start{0};
    uint16_t child_count{0};
};

struct Node {
    NodeType type{NodeType::Text};
    std::string_view text{};
    bool is_plural{false};
    int32_t offset{0};
    uint16_t branch_start{0};
    uint16_t branch_count{0};
};

struct Argument {
    std::string_view name;
    std::string_view str_val{};
    int32_t num_val{0};
    bool is_numeric{false};
};

template <size_t MaxNodes = 32, size_t MaxBranches = 8>
class TemplateParser {
public:
    constexpr explicit TemplateParser(std::string_view src) noexcept : src_{src} {}

    [[nodiscard]] constexpr std::expected<uint16_t, ParseError> parse() noexcept {
        uint16_t count = 0;
        uint16_t start = parse_message(false, count);
        if (err_ != ParseError::SyntaxError && !has_error_) {
            return count;
        }
        return std::unexpected(err_);
    }

    [[nodiscard]] size_t evaluate(
        std::span<const Argument> args,
        std::string_view (*plural_fn)(int32_t),
        std::span<char> out_buf) const noexcept
    {
        size_t out_pos = 0;
        eval_range(0, root_count_, args, plural_fn, 0, out_buf, out_pos);
        if (out_pos < out_buf.size()) {
            out_buf[out_pos] = '\0';
        }
        return out_pos;
    }

private:
    std::string_view src_;
    size_t pos_{0};
    std::array<Node, MaxNodes> nodes_{};
    uint16_t node_count_{0};
    std::array<Branch, MaxBranches> branches_{};
    uint16_t branch_count_{0};
    uint16_t root_count_{0};
    ParseError err_{ParseError::SyntaxError};
    bool has_error_{false};

    constexpr void skip_whitespace() noexcept {
        while (pos_ < src_.size() && (src_[pos_] == ' ' || src_[pos_] == '\t' ||
                                      src_[pos_] == '\n' || src_[pos_] == '\r')) {
            ++pos_;
        }
    }

    constexpr std::string_view parse_ident() noexcept {
        skip_whitespace();
        size_t start = pos_;
        while (pos_ < src_.size()) {
            char c = src_[pos_];
            if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '=') {
                ++pos_;
            } else {
                break;
            }
        }
        return src_.substr(start, pos_ - start);
    }

    constexpr uint16_t parse_choice() noexcept {
        ++pos_; /* Пропуск '{' */
        auto arg_name = parse_ident();
        skip_whitespace();

        if (pos_ < src_.size() && src_[pos_] == '}') {
            ++pos_;
            if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); return 0; }
            uint16_t idx = node_count_++;
            nodes_[idx] = Node{ .type = NodeType::Arg, .text = arg_name };
            return idx;
        }

        if (pos_ >= src_.size() || src_[pos_] != ',') { set_err(ParseError::SyntaxError); return 0; }
        ++pos_;

        auto kind = parse_ident();
        bool is_plural = (kind == "plural");
        if (!is_plural && kind != "select") { set_err(ParseError::SyntaxError); return 0; }

        skip_whitespace();
        if (pos_ >= src_.size() || src_[pos_] != ',') { set_err(ParseError::SyntaxError); return 0; }
        ++pos_;

        if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); return 0; }
        uint16_t choice_idx = node_count_++;
        uint16_t b_start = branch_count_;
        uint16_t b_count = 0;
        bool has_other = false;

        while (pos_ < src_.size() && src_[pos_] != '}') {
            skip_whitespace();
            if (pos_ < src_.size() && src_[pos_] == '}') break;

            auto label = parse_ident();
            if (label.empty()) { set_err(ParseError::SyntaxError); return choice_idx; }
            if (label == "other") has_other = true;

            skip_whitespace();
            if (pos_ >= src_.size() || src_[pos_] != '{') { set_err(ParseError::SyntaxError); return choice_idx; }
            ++pos_;

            if (branch_count_ >= MaxBranches) { set_err(ParseError::BufferOverflow); return choice_idx; }
            uint16_t b_idx = branch_count_++;
            ++b_count;

            uint16_t child_cnt = 0;
            uint16_t child_st = parse_message(true, child_cnt);
            branches_[b_idx] = Branch{ .label = label, .child_start = child_st, .child_count = child_cnt };

            if (pos_ >= src_.size() || src_[pos_] != '}') { set_err(ParseError::UnclosedBrace); return choice_idx; }
            ++pos_;
        }

        if (pos_ >= src_.size() || src_[pos_] != '}') { set_err(ParseError::UnclosedBrace); return choice_idx; }
        ++pos_;

        if (!has_other) { set_err(ParseError::MissingOther); }

        nodes_[choice_idx] = Node{
            .type = NodeType::Choice,
            .text = arg_name,
            .is_plural = is_plural,
            .offset = 0,
            .branch_start = b_start,
            .branch_count = b_count
        };
        return choice_idx;
    }

    constexpr uint16_t parse_message(bool in_branch, uint16_t &out_count) noexcept {
        uint16_t start_idx = node_count_;
        uint16_t count = 0;
        size_t txt_start = pos_;

        while (pos_ < src_.size() && !has_error_) {
            char c = src_[pos_];
            if (in_branch && c == '}') break;

            if (c == '{' || (in_branch && c == '#')) {
                if (pos_ > txt_start) {
                    if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); break; }
                    nodes_[node_count_++] = Node{
                        .type = NodeType::Text,
                        .text = src_.substr(txt_start, pos_ - txt_start)
                    };
                    ++count;
                }
                if (c == '#') {
                    if (node_count_ >= MaxNodes) { set_err(ParseError::BufferOverflow); break; }
                    nodes_[node_count_++] = Node{ .type = NodeType::Hash };
                    ++count;
                    ++pos_;
                    txt_start = pos_;
                } else {
                    parse_choice();
                    ++count;
                    txt_start = pos_;
                }
            } else {
                ++pos_;
            }
        }
        if (pos_ > txt_start && !has_error_) {
            if (node_count_ < MaxNodes) {
                nodes_[node_count_++] = Node{
                    .type = NodeType::Text,
                    .text = src_.substr(txt_start, pos_ - txt_start)
                };
                ++count;
            }
        }
        out_count = count;
        if (!in_branch) root_count_ = count;
        return start_idx;
    }

    constexpr void set_err(ParseError e) noexcept {
        err_ = e;
        has_error_ = true;
    }

    void eval_range(uint16_t start, uint16_t count, std::span<const Argument> args,
                    std::string_view (*plural_fn)(int32_t), int32_t active_num,
                    std::span<char> out_buf, size_t &out_pos) const noexcept
    {
        for (uint16_t i = 0; i < count; ++i) {
            const auto &n = nodes_[start + i];
            if (n.type == NodeType::Text) {
                append_span(n.text, out_buf, out_pos);
            } else if (n.type == NodeType::Hash) {
                char num_buf[16];
                int nlen = std::snprintf(num_buf, sizeof(num_buf), "%d", active_num);
                append_span(std::string_view(num_buf, static_cast<size_t>(nlen)), out_buf, out_pos);
            } else if (n.type == NodeType::Arg) {
                for (const auto &a : args) {
                    if (a.name == n.text) {
                        if (a.is_numeric) {
                            char num_buf[16];
                            int nlen = std::snprintf(num_buf, sizeof(num_buf), "%d", a.num_val);
                            append_span(std::string_view(num_buf, static_cast<size_t>(nlen)), out_buf, out_pos);
                        } else {
                            append_span(a.str_val, out_buf, out_pos);
                        }
                        break;
                    }
                }
            } else if (n.type == NodeType::Choice) {
                std::string_view matched_lbl = "other";
                int32_t next_num = active_num;
                for (const auto &a : args) {
                    if (a.name == n.text) {
                        if (n.is_plural && a.is_numeric) {
                            next_num = a.num_val;
                            matched_lbl = plural_fn ? plural_fn(next_num) : "other";
                        } else if (!n.is_plural && !a.is_numeric) {
                            matched_lbl = a.str_val;
                        }
                        break;
                    }
                }
                uint16_t sel_idx = 0;
                for (uint16_t b = 0; b < n.branch_count; ++b) {
                    const auto &br = branches_[n.branch_start + b];
                    if (br.label == matched_lbl) { sel_idx = b; break; }
                    if (br.label == "other") sel_idx = b;
                }
                const auto &chosen = branches_[n.branch_start + sel_idx];
                eval_range(chosen.child_start, chosen.child_count, args, plural_fn, next_num, out_buf, out_pos);
            }
        }
    }

    static void append_span(std::string_view s, std::span<char> buf, size_t &pos) noexcept {
        if (pos >= buf.size()) return;
        size_t avail = buf.size() - pos - 1;
        size_t n = s.size() < avail ? s.size() : avail;
        std::memcpy(buf.data() + pos, s.data(), n);
        pos += n;
    }
};

} // namespace embedded::msg
```
:::

## Скільки це коштує

Розбір — один прохід по рядку, лінійний від його довжини, без вороття назад: індекс `i` тільки зростає. Але робиться він **раз на ключ**, а не раз на показ: `trees` тримає готове дерево, і кожен наступний виклик — це обхід дерева, лінійний від кількості вузлів. Тому вартість формування фрази близька до вартості її склеювання вручну; уся різниця пішла в одноразовий розбір.

Другий кеш важливіший, ніж здається. Побудова `Intl.NumberFormat` чи `Intl.PluralRules` — не дешеве присвоєння: рушій розбирає тег локалі й піднімає її дані. Створювати їх усередині циклу по тисячі рядків таблиці — надійний спосіб зробити локалізацію найповільнішою частиною відповіді. Тому обидва загорнуті в [мемоізацію](root:sf-algorithms/memoization) за ключем «локаль + опції».

Вибір категорії — стала вартість: правило локалі — це кілька остач від ділення.

## Пастки

**Гілки, якої бракує, ніхто не помітить.** Перекладач заповнив дві гілки, як в англійському зразку, і не помітив, що українських треба чотири, — програма не впаде: `run` тихо візьме `other`, і користувач прочитає «Оксана додала 3 файлу». Ловити це треба на збірці, звіряючи каталог зі списком категорій, який видає сама локаль:

```ts
function* choices(nodes: Node[]): Generator<Node> {
  for (const n of nodes)
    if (n.t === "choice") { yield n; for (const b of Object.values(n.branches)) yield* choices(b); }
}

function lint(catalog: Record<string, Record<string, string>>): string[] {
  const problems: string[] = [];
  for (const [lang, msgs] of Object.entries(catalog)) {
    const need = new Intl.PluralRules(lang).resolvedOptions().pluralCategories;
    for (const [key, pattern] of Object.entries(msgs))
      for (const node of choices(parse(pattern)))
        if (node.kind === "plural")
          for (const c of need)
            if (!(c in node.branches)) problems.push(`${lang}/${key}: бракує гілки «${c}»`);
  }
  return problems;
}

lint(catalog);   // [] — а без гілки few: ['uk/files.added: бракує гілки «few»']
```

**Апостроф з'їдає місце.** Наслідок правила цитування, яке ми повторили в розбирачі. Шаблон `Ключ '{key}' не знайдено` — спроба взяти назву ключа в лапки-апострофи — дає на виході дослівне «Ключ {key} не знайдено»: апостроф стоїть перед `{`, отже відкриває цитату, і місце всередині вже не місце, а текст. Лікується подвоєнням (`''`) або, краще, справжніми лапками — «…» чи “…”, яких ICU взагалі не чіпає. А от «п'ять» і «об'єднати» безпечні, бо там за апострофом стоїть літера.

**`=0` — не те саме, що `zero`.** Мітка `zero` — граматична категорія, і вона є, наприклад, в арабській, де нуль справді має власну форму слова. В українській нуль потрапляє в `many` — «0 файлів», і це граматично правильно. `=0` натомість — точний збіг за значенням, і потрібен він не для граматики, а для іншого формулювання: замість «0 файлів» написати «Немає файлів». Це рішення перекладача, тому й живе воно в шаблоні:

```ts
"{count, plural, offset:1 =0 {Ніхто ще не вподобав} =1 {{you} вподобали} " +
"one {{you} і ще # людина} few {{you} і ще # людини} " +
"many {{you} і ще # людей} other {{you} і ще # людини}}"

// count = 0 → Ніхто ще не вподобав
// count = 1 → Ви вподобали
// count = 3 → Ви і ще 2 людини
```

`offset:1` тут відкладає вбік самого читача: форму й `#` рахують від `count − 1`, тоді як точні збіги `=0` і `=1` звіряють із повним `count`. Через це «3» перетворюється на «Ви і ще 2 людини» — і форма береться під двійку, а не під трійку.

**Порядкові числівники — інша таблиця.** `{ type: "ordinal" }` вмикає окремий звід правил, і збігу з кількісним немає навіть у наборі міток: серед порядкових в української є лише `few` — для чисел, що закінчуються на 3, крім 13 (3-тя, 23-тя, 33-тя), — і `other` для решти. Кількісне правило кинуло б у ту саму `few` ще й двійку з четвіркою, і «2-га спроба» стала б «2-тя».

**Мова шаблону й мова читача можуть розійтися.** Коли українського перекладу для ключа немає й запасний ланцюжок дійшов до англійського шаблону, обирати гілку треба за англійськими правилами: у цьому шаблоні є `one` і `other`, а `few` немає. Тому `t` форматує в мові **шаблону**, а не в мові запиту. Інакше вийшло б найгірше з обох світів: англійське речення з українською комою в дробах і провалом у `other` там, де правило шукало `few`.

**Одне повідомлення — одне речення.** Спокуса зекономити й розбити фразу на два ключі («У вас » + ключ із множиною) повертає всі проблеми, заради яких це все й будувалося: перекладач отримує уламки без контексту й не може ані переставити їх місцями, ані узгодити між собою. Ключ має покривати ціле речення, навіть якщо частина його виглядає нудною сталою.

**Рядок на виході — це текст, а не розмітка.** Формувальник повертає звичайний рядок; якщо вставити його в сторінку як HTML, то будь-який каталог перекладу стає каналом для чужого коду. Розмітку тримають поза перекладом або віддають окремим механізмом, що збирає готові вузли, а не рядок.

**Стара нотація рахує гілки числами.** Каталоги `gettext` описують множину виразом, що дає **індекс** — `nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : …)` — і перекладач заповнює `msgstr[0]`, `msgstr[1]`, `msgstr[2]`. Мітки CLDR (`one`, `few`, `many`) з цими індексами не збігаються ані за порядком, ані за кількістю: сама лише українська має в CLDR чотири категорії проти трьох індексів. Переносячи каталог із такого формату, індекси доводиться зіставляти з мітками руками — механічний переклад «нульовий індекс → one» ламається на першій же мові, де вираз написано в іншому порядку.

/* ============================================================================
   library.js (v7) — стартова сторінка-«бібліотека».

   Полиці приходять із root/shelf.json: один запис на вид (sci · eng · course ·
   hw · sys), кожен зі своїм заголовком полиці, словником (`words`) і питанням,
   на яке вид відповідає (`asks`). Додав вид або книгу в shelf.json — полиця
   зʼявилась тут сама, правити цей файл не треба.

   ЧОТИРИ РІВНІ, ОДИН ВИГЛЯД: бібліотека → полиця → збірка → книга. Адреса тримає
   рівень («#», «#sci», «#sci/physics»), тож Back і перезавантаження працюють самі.
   Сегмент-контрол прибрано: сім полиць у його однорядкову смугу не вміщалися.

   Кнопка #view-btn лишає другий вигляд — "one": усі полиці на одній сторінці
   без переходів. Малюємо щоразу заново (draw), а не ховаємо копії DOM.
   ========================================================================== */
(function () {
  "use strict";
  var root = document.getElementById("library-root");
  if (!root) return;
  function esc(s) { return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function cap(s) { return String(s || "").charAt(0).toUpperCase() + String(s || "").slice(1); }

  var READ = (function () { try { return new Set(JSON.parse(localStorage.getItem("courses-read") || "[]")); } catch (e) { return new Set(); } })();

  /* Оформлення книг — суто фронтова справа (у контенті його нема). Нема запису —
     працює запасний варіант виду, тож нова книга зʼявляється й без правки цих мап. */
  var ICON = {
    /* збірки */
    physics: "⚛️", math: "🧮", plang: "🔤",
    /* sci */
    computability: "♾️", "math-algebra": "🔢", "math-analysis": "📈", "math-combinatorics": "🎲",
    "math-geometry": "📐", "math-information": "🔣", "math-logic": "⚖️", "math-number-theory": "🔟",
    "math-numeric": "🧮", "math-probability": "🎯", "ph-condensed": "🧊", "ph-electromagnetism": "🧲",
    "ph-mechanics": "⚙️", "ph-quantum": "⚛️", "ph-thermodynamics": "🔥", "ph-waves": "🌊",
    /* eng */
    "sf-algorithms": "🧠", "sf-apps": "🏛️", "sf-data": "🗄️", "sf-devices": "📟", "sf-distributed": "🕸️",
    "sf-lang": "🔤", "sf-ml": "🤖", "sf-os": "💽", "sf-release": "🚀", "sf-security": "🔐",
    "sf-tasks": "🧵", "sf-visual": "🎨", "sf-web": "🌐",
    /* course */
    "basic-chemistry": "⚗️", embedded: "🔌", "embedded-ultra": "⚡", progarch: "🏗️", unix: "🧭",
    /* hw */
    "hw-analog": "〰️", "hw-arch": "🖥️", "hw-components": "🔩", "hw-digital": "🔳", "hw-motion": "🌀",
    "hw-pcb": "🟩", "hw-power": "🔋", "hw-sensing": "🌡️",
    /* sys */
    "sys-bsystem": "🔨", "sys-dron": "🛰️", "sys-fw": "📦", "sys-ide": "🧰", "sys-media": "🎞️",
    "sys-notary": "📜", "sys-plang-cpp": "🧾", "sys-plang-python": "🐍", "sys-unix": "🐧",
    /* cat */
    "cat-hw-actuators": "🦾", "cat-hw-boards": "🧩", "cat-hw-connect": "📶", "cat-hw-controls": "🎛️",
    "cat-hw-drivers": "🎚️", "cat-hw-instruments": "🔬", "cat-hw-parts": "🧷", "cat-hw-power": "🔋",
    "cat-hw-sensors": "🌡️",
    /* com */
    "com-devices": "🔗", "com-medium": "📻", "com-modulation": "〽️", "com-protocol": "🤝",
    "com-signal": "📊", "com-transport": "📮"
  };
  /* Колір книги — приглушений відтінок за змістом: тепло в термодинаміці, крига
     в конденсованій, зелень у платі, бурштин у каталозі. Насиченість навмисно
     низька: тло картки бере лише 9% цього кольору, тож полиця не рябить. */
  /* Палітра — СПІЛЬНА, живе в bookbuild.js (він вантажиться першим і на обох
     сторінках). Тут лише беремо її: дві копії неминуче розходяться, і саме так
     курс був зелений у бібліотеці й синій у читачі. Запасні — на випадок, якщо
     bookbuild чомусь не завантажився.  */
  var ACCENT = (window.__PALETTE || {}).ACCENT || {};
  var KIND_ICON = { sci: "📚", eng: "🛠️", course: "🎓", hw: "🗂️", sys: "📗", cat: "🏷️", com: "📡" };
  var KIND_ACCENT = (window.__PALETTE || {}).KIND_ACCENT || { sci: "#3a6b9c", eng: "#b06a5a", course: "#16a34a", hw: "#5b6b7c", sys: "#4a6070", cat: "#8a6a3f", com: "#4a8296" };
  var KIND_CTA = { course: "Пройти →", hw: "Відкрити →", sys: "Відкрити →", cat: "Гортати →", com: "Читати →" };
  /* Підпис лічильника груп — множина від words.group (українська множина неправильна,
     тож тримаємо готові форми, а не доклеюємо закінчення). */
  var KIND_GROUPS = { sci: "Галузі", eng: "Технології", course: "Томи", hw: "Групи", sys: "Модулі", cat: "Родини", com: "Рівні" };
  /* Українська множина — три форми, за останніми цифрами. */
  function plural(n, one, few, many) {
    var a = Math.abs(n) % 100, b = a % 10;
    if (a > 10 && a < 20) return many;
    if (b > 1 && b < 5) return few;
    if (b === 1) return one;
    return many;
  }

  /* Опис книги береться з її manifest.json (`subtitle`). Тут — лише запасні описи
     для тих, що ще не мають свого; коли subtitle зʼявиться, він переможе. */
  var DESC = {
    "physics": "Шість книг про те, чому природа поводиться саме так, а не інакше. Від каменя, що падає, до електрона, який не має траєкторії.",
    "math": "Мова, якою записано решту наук. Дев'ять книг про те, як рахувати, доводити й бачити структуру там, де на вигляд лише числа.",
    "plang": "Мова програмування — теж домовленість, і в неї є версії. Що саме обіцяє стандарт і що з цього справді працює.",
    "computability": "Є задачі, яких не розв'яже жодна машина, і це доведено, а не припущено. Тут проходить межа можливого й починається питання ціни.",
    "math-algebra": "Коли додавання й множення виявляються однією дією, з'являються групи й кільця. Звідти ж ростуть вектори й матриці, якими крутять графіку й розв'язують системи.",
    "math-analysis": "Швидкість — це похідна, площа — інтеграл, а рух планети описує рівняння, де невідома сама функція. Про неперервну зміну й те, як її рахувати.",
    "math-combinatorics": "«Скільки є способів» — питання, на яке не відповісти переліком. Тут рахують міркуванням, і саме звідси беруться оцінки складності алгоритмів.",
    "math-geometry": "Форма, відстань і поворот — те, чим машина рухає об'єкт на екрані. Від Евкліда до координат і кривих, якими описують справжні поверхні.",
    "math-information": "Стиснути повідомлення можна рівно настільки, скільки в ньому несподіванки. Ентропія міряє цю несподіванку й ставить межу, нижче за яку не опуститься жоден архіватор.",
    "math-logic": "Що таке доведення і чому не все істинне можна довести. Тут будують саму мову математики й натрапляють на межі, знайдені Геделем.",
    "math-number-theory": "Прості числа поводяться так дивно, що на цьому тримається вся сучасна криптографія. Подільність і лишки — механіка кожного захищеного з'єднання.",
    "math-numeric": "Точної відповіді часто немає або вона задорога. Як рахувати наближено так, щоб похибка не з'їла результат, і бачити, коли метод ось-ось розсиплеться.",
    "math-probability": "Випадковість має закони, і з них випливає, чому середнє стабілізується, а рідкісна подія колись таки стається. Далі — як робити висновок із даних і не обманути себе.",
    "ph-condensed": "Чому мідь проводить, скло ні, а кремній — коли ми захочемо. Зонна структура пояснює провідність, магнетизм і те, як із піску виходить транзистор.",
    "ph-electromagnetism": "Заряд створює поле, змінне поле народжує струм, а разом вони відриваються від дроту й летять хвилею. Дорога від Кулона до Максвелла й антени.",
    "ph-mechanics": "Чому камінь падає, а супутник ні, і куди дівається енергія удару. Від опису руху до законів збереження, обертання тіла й течії рідини.",
    "ph-quantum": "У малому величини перестають бути неперервними, а частинка — точкою. Рівні атома й тунелювання, без якого не працює жодна флешка.",
    "ph-thermodynamics": "Тепло саме йде від гарячого до холодного, і жодна машина цього не обходить. Ентропія пояснює, чому час має напрямок, а ККД — стелю.",
    "ph-waves": "Резонанс ламає міст, а зустріч двох хвиль гасить обидві. Звук, світло й радіо виявляються однією математикою на різних частотах.",
    "sf-algorithms": "Та сама задача рахується секунду або тиждень — різниця в тому, як її подати машині. Структури даних і прийоми, що перетворюють перебір на розрахунок.",
    "sf-apps": "Великий код гниє не від складності, а від залежностей, яких ніхто не проводив навмисно. Про межі й стан — те, від чого залежить, чи можна буде щось змінити за рік.",
    "sf-data": "Дані переживають код, тому схема коштує дорожче за будь-яку функцію. Транзакції, реплікація й черги з чесною ціною кожного вибору.",
    "sf-devices": "Тут немає ні вільної пам'яті, ні права впасти, а оновлення прилітає на пристрій, до якого не дотягнешся рукою. Програмування, де видно кожен байт.",
    "sf-distributed": "Щойно машин стає дві, зникає спільний час і з'являється питання, кому вірити. Узгодження й консенсус, а головне — поведінка, коли мережа рветься посередині.",
    "sf-lang": "Між текстом програми й тим, що виконує процесор, лежить кілька перетворень. Розбір, типи й оптимізації, а заразом відповідь, чому мова дозволяє саме це.",
    "sf-ml": "Модель не знає правил — вона знаходить закономірність у прикладах разом з усіма їхніми перекосами. Як навчати, як міряти якість і де воно тихо ламається.",
    "sf-os": "Кожна програма думає, що машина належить їй, і саме цю ілюзію тримає система. Процеси, віртуальна пам'ять і межа, за якою починається ядро.",
    "sf-release": "Код, що працює на ноуті, ще нічого не вартий. Дорога до продакшену, спостережуваність і можливість відкотитися, коли о третій ночі щось поїхало.",
    "sf-security": "Безпеку не додають наприкінці — вона або закладена в модель, або її немає. Шифри й доступ, а поряд класика помилок, на яких ламаються акуратні системи.",
    "sf-tasks": "Паралельність прискорює доти, доки два потоки не візьмуться за одне й те саме. Гонки, блокування й ціна перемикання, з відповіддю, коли воно взагалі варте того.",
    "sf-visual": "Користувач бачить не архітектуру, а кадр і затримку між натиском і реакцією. Рендер, шрифт і колір з боку того, хто мусить намалювати вчасно.",
    "sf-web": "HTTP простий рівно доти, доки не з'являються кеш, проксі й повторні запити. Про контракти між службами й про те, хто за що відповідає в ланцюгу.",
    "basic-chemistry": "Хімія з нуля й послідовно, від атома до реакцій, розчинів і органіки. Кожен крок спирається на попередній, а задачі розв'язуються тим, що вже пройдено.",
    "embedded": "Від заряду в дроті до пристрою, який летить і сам приймає рішення. Довга доріжка, де ніщо не береться нізвідки й кожен крок спирається на попередній.",
    "embedded-ultra": "Той самий шлях, стиснутий до двох днів читання. Без заглиблень, але з розумінням, що з чим пов'язане й куди дивитися далі.",
    "progarch": "Як побудувати систему, яку через рік ще можна буде змінити. Модульність і межі на прикладах того, що зазвичай ламається під час зростання.",
    "unix": "Unix стає зрозумілим, коли бачиш, що файл, процес і право — три прості ідеї, які повторюються всюди. Доріжка від першої команди до цілісної картини.",
    "hw-analog": "Сигнал тут неперервний, і зіпсувати його можна на кожному кроці. Підсилювачі, зворотний зв'язок і фільтри, з поглядом на шум, який завжди поруч.",
    "hw-arch": "Що процесор насправді робить між двома рядками коду. Конвеєр, кеш і переривання пояснюють, чому однакові програми біжать із різною швидкістю.",
    "hw-components": "Резистор гріється, конденсатор має індуктивність, а транзистор — не ідеальний ключ. Про поведінку деталей у справжній схемі, а не в підручнику.",
    "hw-digital": "З двох рівнів напруги збирається пам'ять, лічильник і автомат. Тригери й синхронізація — місце, де цифрове знову стає аналоговим.",
    "hw-motion": "Щоб схема зрушила щось важче за світлодіод, потрібні струм, момент і зворотний зв'язок. Двигуни, серви й драйвери з реальними обмеженнями.",
    "hw-pcb": "Плата не підкладка, а частина схеми: доріжка має індуктивність, а земля не всюди нуль. Шари, цілісність сигналу й тепло, яке треба кудись подіти.",
    "hw-power": "Живлення вирішує, чи працюватиме решта, і воно ж перше гріється. Перетворювачі й акумулятори, де ККД і пульсації — частина розрахунку, а не дрібниця.",
    "hw-sensing": "Між фізичною величиною й числом у програмі стоїть ланцюг, який усе спотворює. Давач, підсилення й калібрування, щоб виміряному можна було вірити.",
    "sys-bsystem": "Збірка — не «натиснути кнопку», а граф залежностей, який мусить давати той самий результат щоразу. CMake й тулчейни з боку того, хто це налаштовує.",
    "sys-dron": "Апарат летить сам, поки алгоритм тримає його в заданих межах. ArduPilot і PX4 зсередини, а поряд станція, з якої це все видно й керується.",
    "sys-fw": "Фреймворк ховає регістри за зручним викликом, і варто знати, що саме він при цьому робить. Старт, шар абстракції й ціна цієї зручності.",
    "sys-ide": "Робоче місце — не редактор, а зв'язка індексації, відлагоджувача й контролю версій. Про те, як воно складається докупи й де економить години.",
    "sys-media": "Кадр іде конвеєром, і кожна ланка може стати вузьким місцем. GStreamer і OpenCV зсередини, з буферами й моделлю пам'яті зображення.",
    "sys-notary": "Виріб виходить у світ не тоді, коли працює, а коли має документи. Ліцензії, стандарти й гарантії — те, про що згадують надто пізно.",
    "sys-plang-cpp": "Мова, де час життя об'єкта — інструмент, а не дрібниця. Володіння й шаблони, з поглядом на те, що приніс кожен стандарт і навіщо.",
    "sys-plang-python": "Простота Python тримається на моделі об'єктів, яку варто побачити. Простори імен та ітератори, а також межі, за якими доводиться йти в C.",
    "sys-unix": "Система, де все — файл, процес має батька, а право вирішує решту. Не набір команд, а те, як воно влаштоване й чому саме так.",
    "cat-hw-actuators": "Мотори, серви й соленоїди з реальними струмами, а не з обіцянок в описі. Що витримає навантаження й що поставити поруч, аби не згоріло.",
    "cat-hw-boards": "Конкретні плати: що на борту, скільки їсть і які виводи насправді вільні. З підключенням і межами, про які продавець зазвичай мовчить.",
    "cat-hw-connect": "Радіомодулі з чесною дальністю й споживанням. Що обрати під задачу й що доведеться доробити самому, щоб воно заговорило.",
    "cat-hw-controls": "Кнопка деренчить, енкодер пропускає кроки, потенціометр шумить. Огляд органів керування разом із тим, як їх обробляти в коді.",
    "cat-hw-drivers": "Силовий ключ гріється, і від цього залежить, чи доживе схема до ранку. Драйвери з робочими струмами й тим, що треба на радіатор.",
    "cat-hw-instruments": "Мультиметр показує середнє, осцилограф — форму, і різниця між ними вирішує діагноз. Прилади з межами й типовими помилками читання.",
    "cat-hw-parts": "Дрібні деталі, у яких найлегше помилитися при купівлі. Маркування й допуски з поясненням, що справді важить у схемі, а що ні.",
    "cat-hw-power": "Готові перетворювачі й акумулятори з тим струмом, який вони справді тягнуть. Про запас, нагрів і захист, без якого модуль довго не живе.",
    "cat-hw-sensors": "Давачі руху, середовища, світла й відстані з тим, що вони насправді міряють. Чого чекати від дешевого модуля й де саме він почне брехати.",
    "com-devices": "Дві мікросхеми на одній платі домовляються за суворими правилами. I²C, SPI, UART і CAN з кадром, адресацією й граблями, на які наступають усі.",
    "com-medium": "Сигнал іде не «по дроту», а по лінії з опором, відбиттям і загасанням. Кабель, ефір і оптика з відповіддю, чому далі воно не добиває.",
    "com-modulation": "Щоб біт долетів, його треба покласти на хвилю й потім упізнати в шумі. Модуляція, кодування й виправлення помилок як одна задача.",
    "com-protocol": "Протокол починається там, де сторони мають домовитися про стан і про поведінку при збої. Формат і версіювання з боку того, хто це проєктує.",
    "com-signal": "Корисне майже завжди тонше за шум, і вся справа в тому, як його звідти дістати. Спектр і фільтри з поясненням, звідки береться кожен ефект.",
    "com-transport": "Пакет має знайти шлях, пережити чергу й не приїхати двічі. Адресація й контроль потоку — механіка, якої не видно, поки вона працює."
  };

  /* Опис полиці — той самий рівень подачі, що й у книги: коротко про те, що
     всередині і навіщо воно поруч. */
  var SHELF_DESC = {
    "sci": "Знання про те, що є незалежно від нас: закон, явище, доведена теорема. Фізика, математика й межа обчислюваного.",
    "eng": "Те, що люди пишуть і будують. Не як влаштований світ, а як роблять річ — від форми застосунку до мереж, безпеки й випуску.",
    "course": "Доріжки для того, хто починає з нуля. Крок спирається на пройдене й нічого не бере нізвідки, тому читати варто підряд.",
    "hw": "Як улаштована річ, а не яку купити. Схемотехніка й кремній під нею, живлення, плата й усе, що рухається.",
    "sys": "Рукотворні системи, до яких доречне питання «а в якій версії?». Unix, автопілот, мови програмування, збірка й робоче місце.",
    "cat": "Конкретні моделі з артикулом і даташитом. Не принцип, а те, що можна покласти в кошик і припаяти сьогодні.",
    "com": "Як сигнал долає відстань — від фізики середовища до протоколу між програмами. Родина навмисно перетинає межу софту й заліза."
  };

  /* Версія ЧИТАБЕЛЬНА, якщо статус не "empty"/"pending"; ЗАПЛАНОВАНА, якщо не "empty".
     Рахунок — по ТЕМАХ: тема «написана», якщо готова ХОЧ ОДНА версія (базова АБО детальна). */
  function verReadable(v) { return !!(v && v.status && v.status !== "empty" && v.status !== "pending"); }
  function verPlanned(v) { return !!(v && v.status && v.status !== "empty"); }

  /* Книга v7 → рядок для картки. `loadBook` (bookbuild.js) уже дав і адаптовану
     структуру, і сирі групи — рахуємо по сирих, бо там є ще й ref-кроки. */
  function stat(b) {
    var groups = b.groups || [];
    var chapters = 0, planned = 0, done = 0, refs = [], read = 0, written = {};
    groups.forEach(function (g) {
      (g.chapters || []).forEach(function (c) {
        if (c.title) chapters++;
        (c.topics || []).forEach(function (t) {
          if (!t) return;
          if (t.ref) {
            var pr = String(t.ref).split("/").filter(Boolean);
            var rb = pr[0], rt = pr[pr.length - 1];
            planned++; refs.push({ book: rb, slug: rt });
            if (READ.has(rb + "/" + rt)) read++;
            return;
          }
          if (!t.slug) return;                                   // місток — не стаття
          if (verPlanned(t.basic) || verPlanned(t.detailed)) planned++;
          if (verReadable(t.basic) || verReadable(t.detailed)) { done++; written[t.slug] = 1; }
          if (READ.has(b.bookSlug + "/" + t.slug)) read++;
        });
      });
    });
    return {
      slug: b.bookSlug, title: b.title, kind: b.kind, words: b.words || {},
      subtitle: b.subtitle || "", groups: groups.length, chapters: chapters,
      planned: planned, done: done, read: read, refs: refs, written: written
    };
  }

  /* ── Картка книги (одна форма на всі види; вид дає слова й підпис) ───── */
  function card(s) {
    var accent = ACCENT[s.slug] || KIND_ACCENT[s.kind] || "#1d6fa4";
    var ico = ICON[s.slug] || KIND_ICON[s.kind] || "📘";
    var desc = s.subtitle || DESC[s.slug] || "";
    var W = s.words || {};
    var pct = s.planned ? Math.round(s.done / s.planned * 100) : 0;
    var w = writtenLabel(s.kind, s.done, s.planned);
    var isCourse = s.kind === "course";

    return cardShell({
      href: "read.html?book=" + esc(s.slug), accent: accent, ico: ico, kind: s.kind, title: s.title, desc: desc, pct: pct,
      read: s.read, total: s.planned,
      left: esc(KIND_GROUPS[s.kind] || cap(W.group || "Групи")) + " " + s.groups +
            (s.chapters ? " · розділів " + s.chapters : "") +
            (isCourse && s.read ? " · прочитано " + s.read : ""),
      right: w.num, rightLbl: w.lbl
    });
  }

  /* ── ОДНА ФОРМА КАРТКИ на всі рівні: вид · збірка · книга · том ───────
     Заливка тла = відсоток написаного (варіант 8): стан читається периферійним
     зором, без окремої смужки. Праворуч — знак книги, щоб її впізнавали в лице.
     Унизу один рядок: ліворуч склад, праворуч «написано / усього» через скісну. */
  /* Другий показник — ВЛАСНИЙ прогрес читача. Заливка тла каже, скільки написано
     (стан корпусу); ця смужка — скільки з того прочитано. Два різні питання, тому
     й показані по-різному: одне тлом, друге явною смужкою з числом. */
  function readRow(read, total) {
    var p = total ? Math.round((read || 0) / total * 100) : 0;
    /* Усе прочитано — дріб не потрібен: «145 / 145» не каже нічого понад «145».
       Дріб має сенс лише доти, доки чисельник відрізняється від знаменника. */
    var done = total > 0 && (read || 0) >= total;
    var num = done ? String(total) : ((read || 0) + ' / ' + total);
    return '<div class="lc-read"><span class="lc-read-track"><i style="width:' + p + '%"></i></span>' +
      '<span class="lc-read-num">' + num + ' прочитано</span></div>';
  }

  /* Підпис лічильника написаного. Доки написано не все — це дріб і слово «написано».
     Коли написано все, цікаве вже не «скільки з чого», а СКІЛЬКИ ВСЬОГО, тож дріб
     згортається в число, а підпис називає саму одиницю: «145 тем», «215 кроків». */
  var KIND_UNIT = {
    course: ["крок", "кроки", "кроків"],
    cat: ["позиція", "позиції", "позицій"],
  };
  function writtenLabel(kind, done, planned) {
    if (!(planned > 0 && done >= planned)) return { num: done + " / " + planned, lbl: "написано" };
    var u = KIND_UNIT[kind] || ["тема", "теми", "тем"];
    return { num: String(planned), lbl: plural(planned, u[0], u[1], u[2]) };
  }

  function cardShell(o) {
    return '<a class="lib-card lib-card-' + esc(o.kind || "") + '" href="' + o.href +
      '" style="--accent:' + o.accent + ';--p:' + (o.pct || 0) + '">' +
      '<span class="lc-fill" aria-hidden="true"></span>' +
      '<div class="lc-head"><h3 class="lc-ttl">' + esc(o.title) + '</h3>' +
      '<span class="lc-ico" aria-hidden="true">' + o.ico + '</span></div>' +
      '<p class="lc-desc">' + esc(o.desc || "") + '</p>' +
      '<div class="lc-foot"><span class="lc-left">' + o.left + '</span>' +
      '<span class="lc-right">' + o.right + '<i>' + esc(o.rightLbl || "написано") + '</i></span></div>' +
      readRow(o.read, o.total) + '</a>';
  }


  /* ── Картка НАДКНИГИ (збірки книг) ───────────────────────────────────
     Збірка живе лише в shelf.json і лише для показу: на диску, в git і в адресі
     теми її немає. Тому картка веде не в читач, а на рівень глибше — у список
     книг збірки, який виглядає так само, як полиця. Числа — сума по книгах. */
  function groupStat(g) {
    var st = { slug: g.slug, title: g.title, asks: g.asks || "", books: g.items.length, groups: 0, chapters: 0, planned: 0, done: 0, read: 0 };
    g.items.forEach(function (s) {
      st.groups += s.groups; st.chapters += s.chapters; st.planned += s.planned; st.done += s.done; st.read += s.read;
    });
    return st;
  }
  function groupCard(kind, g) {
    var st = groupStat(g);
    var accent = ACCENT[st.slug] || KIND_ACCENT[kind] || "#1d6fa4";
    var ico = ICON[st.slug] || "📚";
    var desc = st.asks ? cap(st.asks) : (DESC[st.slug] || "");
    var pct = st.planned ? Math.round(st.done / st.planned * 100) : 0;
    var w = writtenLabel(kind, st.done, st.planned);

    return cardShell({
      href: "#" + esc(kind) + "/" + esc(st.slug), accent: accent, ico: ico, kind: kind, title: st.title, desc: DESC[st.slug] || cap(st.asks || ""), pct: pct,
      read: st.read, total: st.planned,
      left: "книг " + st.books + (st.chapters ? " · розділів " + st.chapters : ""),
      right: w.num, rightLbl: w.lbl
    });
  }

  /* ── Вигляд (одна сторінка ⇄ вкладки) і активна вкладка ─────────────── */
  var TABS = [];   // заповнюється з shelf.json
  function getView() { try { return localStorage.getItem("courses-lib-view") === "one" ? "one" : "tabs"; } catch (e) { return "tabs"; } }
  function setView(v) {
    document.documentElement.setAttribute("data-libview", v);
    try { localStorage.setItem("courses-lib-view", v); } catch (e) {}
    paintViewBtn();
  }
  /* Адреса бібліотеки: «#<вид>» — полиця, «#<вид>/<збірка>» — усередині збірки.
     Другий сегмент дає кнопку «назад» і переживає перезавантаження та Back. */
  function parseHash() {
    var p = (location.hash || "").slice(1).split("/");
    return { tab: p[0] || "", group: p[1] || "" };
  }

  function sectHead(ttl, count, note) {
    return '<div class="lib-sect-head"><h2 class="lib-sect-ttl">' + ttl + '</h2>' +
      '<span class="lib-sect-count">' + count + '</span><span class="lib-sect-line"></span>' +
      (note ? '<span class="lib-sect-note">' + note + '</span>' : '') + '</div>';
  }

  /* ── ЧОТИРИ РІВНІ, ОДИН ВИГЛЯД ───────────────────────────────────────
     бібліотека → полиця → збірка → книга. На кожному рівні той самий грид
     плиток, тож перехід углиб не міняє того, ЯК читач дивиться — міняється
     лише те, НА ЩО.

     Сегмент-контрол прибрано свідомо, а не полагоджено: він мав смугу-підсвітку,
     що позиціюється за номером активної вкладки в ОДНОМУ рядку. Сім полиць у рядок
     не вміщалися, контрол переносив їх у два — а смуга лишалася рахувати по-старому
     й накривала дві кнопки разом. Плитки такої вади не мають за побудовою: вони
     переносяться самі, і підсвічувати між ними нічого не треба. Ще й місця під
     нові полиці стільки, скільки їх буде. */
  var SHELVES = [];

  function tile(s) {
    var planned = 0, done = 0, read = 0;
    s.items.forEach(function (x) { planned += x.planned; done += x.done; read += x.read; });
    var w = writtenLabel(s.kind, done, planned);
    return cardShell({
      href: "#" + esc(s.kind), accent: KIND_ACCENT[s.kind] || "#1d6fa4",
      ico: KIND_ICON[s.kind] || "📘", kind: s.kind,
      title: s.shelf, desc: SHELF_DESC[s.kind] || cap(s.asks || ""),
      pct: planned ? Math.round(done / planned * 100) : 0,
      read: read, total: planned,
      left: s.items.length + " " + plural(s.items.length, "книга", "книги", "книг"),
      right: w.num, rightLbl: w.lbl
    });
  }

  function crumbs(parts) {
    return '<nav class="lib-crumbs" aria-label="Де ви зараз">' + parts.map(function (p, i) {
      var last = i === parts.length - 1;
      return (i ? '<span class="lib-crumb-sep" aria-hidden="true">/</span>' : "") +
        (last ? '<span class="lib-crumb is-here">' + esc(p.t) + '</span>'
              : '<a class="lib-crumb" href="' + esc(p.h) + '">' + esc(p.t) + '</a>');
    }).join("") + '</nav>';
  }
  function grid(kind, cards) {
    return '<div class="lib-shelf lib-shelf-' + esc(kind) + '">' + cards + '</div>';
  }
  function empty() { return '<p class="lib-empty">Ця полиця поки порожня — книги переїжджають у нове дерево.</p>'; }

  function viewHome() {
    var live = SHELVES.filter(function (s) { return s.items.length; });
    var books = live.reduce(function (a, s) { return a + s.items.length; }, 0);
    return '<header class="lib-hero"><div class="lib-wrap"><div class="kicker">Бібліотека</div><h1>Мої книги</h1>' +
      '<p>' + (live.length
        ? books + ' ' + plural(books, "книга", "книги", "книг") + ' на ' + live.length + ' ' + plural(live.length, "полиці", "полицях", "полицях") +
          '. Полиця відповідає на своє питання — вибери, яке зараз твоє.'
        : "Полиці зʼявляться, коли книги переїдуть у нове дерево.") + '</p></div></header>' +
      '<div class="lib-shelf lib-shelf-home">' + SHELVES.map(tile).join("") + '</div>';
  }
  function viewShelf(s) {
    /* Шапка полиці НЕСЕ ЇЇ КОЛІР (--accent) і її числа. Доти вона була темною плитою
       з зашитими відтінками: однакова для всіх полиць, глуха до теми, і показувала
       саму лише фразу — числа й перемикач, під які її й малювали, з розмітки зникли. */
    var pl = 0, dn = 0;
    s.items.forEach(function (x) { pl += x.planned; dn += x.done; });
    var w = writtenLabel(s.kind, dn, pl);
    return '<header class="lib-hero lib-hero-sub" style="--accent:' + (KIND_ACCENT[s.kind] || "#1d6fa4") + '"><div class="lib-wrap"><div class="kicker">' + esc(s.shelf) + '</div>' +
      '<h1>' + esc(cap(s.asks || s.shelf)) + '</h1>' +
      '<p>' + s.items.length + ' ' + plural(s.items.length, "книга", "книги", "книг") +
      (s.groups.length ? ' · ' + s.groups.length + ' ' + plural(s.groups.length, "збірка", "збірки", "збірок") : "") +
      (pl ? ' · ' + w.num + ' ' + w.lbl : "") + '</p></div></header>' +
      (s.items.length
        ? grid(s.kind, s.groups.map(function (g) { return groupCard(s.kind, g); }).join("") + s.loose.map(card).join(""))
        : empty());
  }
  function viewGroup(s, g) {
    return '<header class="lib-hero lib-hero-sub" style="--accent:' + (KIND_ACCENT[s.kind] || "#1d6fa4") + '"><div class="lib-wrap"><div class="kicker">' + esc(s.shelf) + ' · збірка</div>' +
      '<h1>' + esc(g.title) + '</h1>' +
      '<p>' + g.items.length + ' ' + plural(g.items.length, "книга", "книги", "книг") +
      (g.asks ? ' · ' + esc(g.asks) : "") + '</p></div></header>' +
      grid(s.kind, g.items.map(card).join(""));
  }
  /* Вигляд «усе на одній сторінці» — той самий матеріал без переходів. */
  function viewAll() {
    return '<header class="lib-hero"><div class="lib-wrap"><div class="kicker">Бібліотека</div><h1>Мої книги</h1>' +
      '<p>Усі полиці на одній сторінці.</p></div></header>' +
      SHELVES.map(function (s) {
        return '<section class="lib-sect lib-wrap"><div class="lib-sect-head"><h2 class="lib-sect-ttl">' + esc(s.shelf) +
          '</h2><span class="lib-sect-count">' + s.items.length + '</span><span class="lib-sect-line"></span>' +
          '<span class="lib-sect-note">' + esc(s.asks) + '</span></div>' +
          (s.items.length ? s.groups.map(function (g) {
            return '<div class="lib-subhead">' + esc(g.title) + '</div>' + grid(s.kind, g.items.map(card).join(""));
          }).join("") + (s.loose.length ? grid(s.kind, s.loose.map(card).join("")) : "") : empty()) +
          '</section>';
      }).join("");
  }

  /* ── Верхній рядок бібліотеки ─────────────────────────────────────────
     Те саме правило, що в читачі: кнопки не висять `fixed` над вмістом, а живуть
     у рядку, який має власне місце. Було чотири кнопки з ручними відступами
     (`right: 1rem / 3.9 / 6.8 / 9.7`) — вони лягали просто на крихти.
     Тепер сітка: крихти ліворуч, інструменти праворуч, накластися нема як. */
  function topbar(parts) {
    return '<header class="lib-topbar">' + crumbs(parts) + '<div class="lib-tools"></div></header>';
  }
  /* Кнопки вбудовуються самі (theme.js, density.js, search.js) — переселяємо їх
     у комірку інструментів після кожного малювання. */
  var TOOL_IDS = ["view-btn", "search-btn", "density-btn", "theme-btn"];
  /* Перемальовуючи сторінку, ми стираємо і комірку разом із кнопками — тож перед
     записом виносимо їх на body, а після повертаємо. Без цього кнопки зникали
     назавжди на першому ж переході між рівнями. */
  function parkTools() {
    TOOL_IDS.forEach(function (id) {
      var b = document.getElementById(id);
      if (b && b.parentNode !== document.body) document.body.appendChild(b);
    });
  }
  function mountTools() {
    var box = root.querySelector(".lib-tools");
    if (!box) return;
    TOOL_IDS.forEach(function (id) {
      var b = document.getElementById(id);
      if (b && b.parentNode !== box) box.appendChild(b);
    });
  }

  /* Малюємо рівень за адресою. Перемальовуємо цілком: рівнів чотири, карток
     щонайбільше кілька десятків — тримати приховані копії дорожче, ніж намалювати. */
  function draw() {
    var r = parseHash(), shelf = null, group = null;
    SHELVES.forEach(function (s) { if (s.kind === r.tab) shelf = s; });
    if (shelf && r.group) shelf.groups.forEach(function (g) { if (g.slug === r.group) group = g; });

    var parts = [{ t: "Бібліотека", h: shelf ? "#" : "" }];
    if (shelf) parts.push({ t: shelf.shelf, h: group ? "#" + shelf.kind : "" });
    if (group) parts.push({ t: group.title, h: "" });

    parkTools();
    /* Тіло — в ОДНІЙ колонці з картками: доти max-width стояв лише на сітці, а
       заголовки лишались притиснуті до краю вікна, і на широкому екрані макет
       мав дві різні ліві межі (0 і 375px). Тепер межа одна на всіх. */
    root.innerHTML = topbar(parts) + (getView() === "one" ? viewAll()
      : group ? viewGroup(shelf, group)
      : shelf ? viewShelf(shelf)
      : viewHome());

    document.title = "Бібліотека — мої книги";
    if (shelf) { try { localStorage.setItem("courses-lib-tab", shelf.kind); } catch (e) {} }
    buildViewBtn();   // кнопка вигляду створюється тут, тож переселяємо ПІСЛЯ неї
    mountTools();
    var g = root.querySelector(".lib-shelf, .lib-tiles");
    if (g) { g.classList.remove("shelf-in"); void g.offsetWidth; g.classList.add("shelf-in"); }
  }

  function render(shelves) {
    SHELVES = shelves;
    window.addEventListener("hashchange", draw);
    draw();
  }

  /* initSeg / segBtn / initialTab прибрано разом із сегмент-контролом:
     рівні веде draw(), підсвічувати активну вкладку нема чого. */

  /* Кнопка перемикання вигляду (⊞ вкладки ⇄ ▤ одна сторінка) */
  var viewBtn = null;
  function paintViewBtn() {
    if (!viewBtn) return;
    var one = getView() === "one";
    viewBtn.textContent = one ? "▤" : "⊞";
    viewBtn.title = one ? "Вигляд: одна сторінка — клік: вкладки" : "Вигляд: вкладки — клік: одна сторінка";
  }
  function buildViewBtn() {
    if (document.getElementById("view-btn")) return;
    viewBtn = document.createElement("button");
    viewBtn.id = "view-btn"; viewBtn.type = "button";
    viewBtn.setAttribute("aria-label", "Перемкнути вигляд бібліотеки");
    viewBtn.addEventListener("click", function () {
      setView(getView() === "one" ? "tabs" : "one");
      draw();
    });
    document.body.appendChild(viewBtn);
    paintViewBtn();
  }

  /* ── Завантаження: shelf.json → усі книги всіх видів ─────────────────── */
  loadShelf().then(function (sh) {
    if (!sh || !sh.kinds) throw new Error("root/shelf.json не прочитався");
    TABS = sh.kinds.map(function (k) { return k.kind; });
    var jobs = [];
    sh.kinds.forEach(function (k) {
      (k.books || []).forEach(function (slug) { jobs.push(loadBook(slug)); });
    });
    return Promise.all(jobs).then(function (all) {
      var bySlug = {};
      all.forEach(function (b) { if (b) bySlug[b.bookSlug] = stat(b); });
      // ref-кроки курсу написані, якщо тема написана в книзі-цілі
      Object.keys(bySlug).forEach(function (k) {
        var s = bySlug[k];
        s.refs.forEach(function (rf) {
          var tgt = bySlug[rf.book];
          if (tgt && tgt.written[rf.slug]) s.done++;
        });
      });
      return sh.kinds.map(function (k) {
        var items = (k.books || []).map(function (sl) { return bySlug[sl]; }).filter(Boolean);
        var byS = {}; items.forEach(function (s) { byS[s.slug] = s; });
        var inGroup = {};
        // Збірка бере лише ті книги, які справді є на полиці: названа в shelf.json, але
        // ще не переїхала → просто не показується, а не ламає рівень.
        var groups = (k.groups || []).map(function (g) {
          var gi = (g.books || []).map(function (sl) { return byS[sl]; }).filter(Boolean);
          gi.forEach(function (s) { inGroup[s.slug] = 1; });
          return { slug: g.slug, title: g.title || g.slug, asks: g.asks || "", items: gi };
        }).filter(function (g) { return g.items.length; });
        return {
          kind: k.kind, shelf: k.shelf, asks: k.asks || "", words: k.words || {},
          items: items, groups: groups,
          loose: items.filter(function (s) { return !inGroup[s.slug]; })
        };
      });
    });
  }).then(render)
    .catch(function (e) { root.innerHTML = '<div class="state error"><h2>Помилка</h2><p><code>' + esc(e && e.message) + '</code></p></div>'; });
})();

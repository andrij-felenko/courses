# Аналіз модуля «kola» — «Кола й закони» (guide/embedded)

Дата: 2026-07-02. Джерела: `E:/develop/courses/guide/embedded/manifest.js` (повністю), `E:/develop/courses/book/electronics/manifest.js` (перелік статей), вибірково перші ~40 рядків `root/course/embedded/reading-schematics/reading-schematics.md` і `root/course/embedded/circuit-analysis/circuit-analysis.md`.

## 1. Що модуль містить зараз (36 тем, пласким списком)

18 ref-ів поспіль: ohms-law, voltage-divider, current-divider, internal-resistance, nodes-branches-loops, kcl, kvl, series-connection, parallel-connection, superposition, thevenin, norton, power-matching, wheatstone-bridge, phase-shift, rc-time-constant, rl-time-constant, instrumentation-amp; далі 18 власних: circuit-analysis, reading-schematics, bjt-load-driving, bjt-vs-mosfet, multistage-amplifier, darlington-vs-sziklai, filter-families, tail-current-source, single-supply-opamp, feedback-topologies, impedance-matching-networks, cascaded-rc-filters, signal-conditioning, dc-ac-bias, kcl-opamp-analysis, opamp-input-types, pierce-oscillator-design, net-labels-buses (останній — basic: pending, єдиний ненаписаний).

Контекст: перед kola читач пройшов лише osnovy (фізика: заряд, поле, потенціал, напруга, струм, опір, потужність, ЕРС/замкнене коло, DC/AC, синусоїда, RMS, магнетизм, шум). Він ще НЕ бачив: резистора/конденсатора/котушки як компонентів (komponenty — наступна секція), напівпровідників (napivprovidnyky — через дві), ОП, цифри, частотних характеристик.

## 2. Головний діагноз

Модуль — це насправді **два різні модулі під одним дахом**:

1. **DC-теорія кіл** (Ом, з'єднання, дільники, Кірхгоф, аналіз, Тевенін/Нортон, міст) + мова схем — легітимне ядро «Кіл і законів», яке справді має стояти одразу після osnovy.
2. **Аналогова схемотехніка на транзисторах і ОП** (BJT-ключі, підсилювачі, Дарлінгтон, зворотний зв'язок, входи ОП, генератор Пірса, кондиціонування) + **AC-матеріал** (фаза, сталі часу RC/RL, каскадовані RC, родини фільтрів, узгодження імпедансів) — усе це фізично не може бути прочитане тут: компоненти C/L вводяться в наступній секції, напівпровідники — через дві, а транзистор і ОП у курсі **не вводяться взагалі ніде**.

Додатково зламаний порядок навіть усередині легітимного ядра (дільники перед послідовним/паралельним; читання схем 20-м кроком).

## 3. Конкретні порушення порядку

1. **«Дільник напруги» (крок 2) стоїть перед «Послідовне з'єднання» (крок 8)**, хоча дільник — це два резистори послідовно; формула дільника спирається на правило послідовного кола.
2. **«Дільник струму» (крок 3) перед «Паралельне з'єднання» (крок 9)** — аналогічно.
3. **«Внутрішній опір джерела» (крок 4) перед «Послідовне з'єднання»** — модель «ЕРС + послідовний резистор» і просідання напруги пояснюються через послідовне коло й дільник.
4. **«Читання схем» стоїть 20-м кроком**, після 19 тем, які всі подаються схемами. Гірше: сама стаття явно спирається на «абетку» — `book:electronics/component-symbols`, `book:electronics/nodes-connections`, `book:electronics/ground-power-rails` — **жодної з цих статей у курсі нема взагалі** (перевірено текстом статті, рядок 3).
5. **«Фаза й зсув фаз» (крок 15)** — зсув фаз у колах породжують реактивні елементи; конденсатор і котушка вводяться лише в наступній секції komponenty. Стаття electronics/phase-shift має вставки math-impedance, math-power-triangle — це матеріал AC-кіл.
6. **«Стала часу RC» (16) і «Стала часу RL» (17)** вимагають конденсатора й котушки — komponenty, наступна секція.
7. **«Інструментальний підсилювач» (18)** вимагає ОП (ideal-opamp, negative-feedback, virtual-short, CMRR) — про ОП у курсі перед цим нема ані слова (і немає взагалі ніде в курсі).
8. **«Аналіз кіл» (19) стоїть після** phase-shift/RC/RL/instrumentation-amp, хоча за змістом (перевірено: чотири знаряддя — Ом, зведення послідовних/паралельних груп, KCL, KVL; суто резистивні приклади) — це зшивка одразу після KCL/KVL і дільників.
9. **«BJT: навантаження» (21) і «BJT проти MOSFET» (22)** вимагають транзистора; напівпровідники в курсі йдуть аж у секції napivprovidnyky (через дві), і навіть там транзистор не вводиться: базові статті electronics/transistor-idea, bjt-operation, bjt-gain, bjt-regions, bjt-switch, field-control, mosfet-switch у курс не залучені взагалі.
10. **«Багатокаскадний підсилювач» (23), «Дарлінгтон проти Sziklai» (24), «Джерело струму хвоста» (26), «DC-зміщення і AC-сигнал» (32)** — вимагають однокаскадного підсилювача на BJT (electronics/bjt-amplifier), дзеркала струмів, диференційної пари — нічого з цього в курсі нема.
11. **«ОП на однополярному живленні» (27), «Топології зворотного зв'язку» (28), «KCL у вузлах схем на ОП» (33), «Типи входів ОП» (34)** — вимагають базового ОП (ideal-opamp → negative-feedback → virtual-short → inverting-noninverting) — у курсі відсутній цілий шар; JFET (для opamp-input-types) не з'являється ніде.
12. **«Родини фільтрів: Баттерворт, Чебишов, Бесель» (25)** — вимагає частотної характеристики, децибелів, АЧХ, поняття полюсів/добротності (electronics/frequency-response, decibels, bode-plot, rc-low-pass, quality-factor) — нічого з цього в курсі на цю мить нема (і не з'являється пізніше).
13. **«Схеми узгодження імпедансів» (29)** — вимагає реактивності й комплексного імпедансу (electronics/reactance, impedance) — імпеданс у курсі не вводиться ніде; діаграма Сміта (hist-вставка) — тим паче.
14. **«Каскадовані RC-ланки» (30)** — вимагають RC-фільтра (rc-low-pass/rc-high-pass) і поняття навантаження каскаду; RC-фільтр у курсі не вводиться.
15. **«Кондиціонування сигналу» (31)** — вимагає ОП, давачів і контексту АЦП; давачі — секція 10, АЦП — ще далі.
16. **«Генератор Пірса» (35)** — вимагає кварцового резонатора (у курсі кварц лише дотично в komponenty: ceramic-mems-resonators, tcxo-ocxo — пізніше), інвертора/підсилювача та умови самозбудження (loop gain, Барккгаузен) — усе це або пізніше, або ніде.
17. **«Принцип суперпозиції» (10)** — спирається на поняття лінійності кола; статті-передумови electronics/linear-circuit у курсі нема (м'якше порушення — «вимагає Z, якого в курсі нема»).
18. **«Теорема Нортона» (12)** — вимагає елемента «джерело струму», якого читач не бачив: в osnovy було лише джерело ЕРС/напруги (physics/closed-circuit). electronics/current-source у курс не залучена.

## 4. Що виношу (move_out) і куди

**До komponenty** (одразу після відповідних компонентів):
- ref electronics/rc-time-constant — після конденсаторної групи (capacitor → capacitor-dielectrics → …): перше «застосування» щойно вивченого конденсатора; також потрібна flyback-protection.
- ref electronics/rl-time-constant — після котушкової групи (inductor-coil → inductor-types): та сама логіка.

**До нового модуля «Змінний струм, імпеданс і фільтри»** (пропоную створити між komponenty і napivprovidnyky):
- ref electronics/phase-shift — відкриває AC-лінію після RC/RL.
- own cascaded-rc-filters — після введення RC-ФНЧ/ФВЧ (нові ref-и rc-low-pass, rc-high-pass у тому модулі).
- own filter-families — після частотної характеристики/децибелів/LC-фільтрів: «якими бувають форми АЧХ».
- own impedance-matching-networks — фінал модуля, після reactance/impedance; на нього далі обіпруться zvyazok (esp32-antenna з math-pi-matching, rf-frontend) і cyfra-pamyat/transmission-lines.
Цей модуль закриває діру, від якої страждають одразу три пізніші секції: cyfra-pamyat (transmission-lines, signal-integrity), keruvannia (фільтри), zvyazok (антени, RF). Будматеріал у книзі вже є: electronics/reactance, capacitive-reactance, inductive-reactance, impedance, frequency-response, decibels, bode-plot, rc-low-pass, rc-high-pass, bandwidth-3db, lc-resonance, quality-factor, lc-rlc-filters — усі basic done.

**До нового модуля «Аналогові схеми: транзистори й ОП»** (пропоную створити одразу після napivprovidnyky, який на той момент має дати діод і транзистор):
- ref electronics/instrumentation-amp — після ОП-базису, поруч із signal-conditioning (його comp-вставка — inamp+міст: гарний back-ref на wheatstone-bridge із kola).
- own bjt-load-driving — після transistor-idea/bjt-operation/bjt-switch (нові ref-и того модуля).
- own bjt-vs-mosfet — після field-control/mosfet-switch.
- own dc-ac-bias — перед/при bjt-amplifier.
- own multistage-amplifier — після однокаскадного підсилювача.
- own darlington-vs-sziklai — після bjt-load-driving (є hist Дарлінгтон—Sziklai).
- own tail-current-source — після differential-pair і current-mirror (нові ref-и).
- own feedback-topologies — після electronics/negative-feedback.
- own kcl-opamp-analysis — одразу після virtual-short/inverting-noninverting: застосовує KCL із kola до схем на ОП.
- own single-supply-opamp — після базових схем на ОП.
- own opamp-input-types — після real-opamp-limits; потребує ref electronics/jfet.
- own signal-conditioning — фінальний розділ «від давача до АЦП», перед keruvannia/signal-acquisition.
- own pierce-oscillator-design — розділ генераторів наприкінці: перед ним ref electronics/reference-frequency (і/або pierce-oscillator) + кварц із komponenty.

Разом move_out = 19 тем; у модулі лишається 17 (14 ref + 3 own) — цілісне DC-ядро.

## 5. move_in

Кандидатів не знайшов: теорія кіл більше ніде в курсі не розкидана. Резистор/маркування (komponenty) лишаю там — фізичний опір уже даний в osnovy (physics/resistance), а компонентні деталі для теорії кіл не потрібні.

## 6. Прогалини (missing) — усі закриваються готовими статтями book/electronics (basic: done)

Для новачка (а) і повноти (б):
1. ref:electronics/schematic-purpose — «Принципова схема»: навіщо схема взагалі; вхідні двері модуля.
2. ref:electronics/component-symbols — «Умовні позначення»: абетка, яку reading-schematics явно передбачає відомою.
3. ref:electronics/nodes-connections — «Вузли й з'єднання» на кресленні (крапка з'єднання, перетин без з'єднання) — теж з «абетки» reading-schematics.
4. ref:electronics/ground-power-rails — «Земля й шини»: точка відліку напруг; без неї не читається ані схема, ані «напруга у вузлі».
5. ref:electronics/short-circuit — «Коротке замикання»: граничні випадки R→0/обрив, безпека; струм КЗ потрібен і Нортону.
6. ref:electronics/multimeter — «Мультиметр»: чим перевіряти закон Ома й дільники руками (курс дає осцилограф лише в proshyvka, а вимірювати треба вже тут).
7. ref:electronics/spice-simulation — «Симуляція кіл (SPICE)»: пісочниця для самоперевірки одразу після методів аналізу (стикується зі вставками proj-circuit-sim/proj-mna-spice власної статті).
8. ref:electronics/linear-circuit — «Лінійність кола»: передумова суперпозиції.
9. ref:electronics/two-terminal-network — «Двополюсна мережа»: ідея чорної скриньки, на якій стоять Тевенін і Нортон.
10. ref:electronics/current-source — «Джерело струму»: елемент, без якого еквівалент Нортона не читається (читач бачив лише ЕРС).
11. ref:electronics/source-transformation — «Перетворення джерел»: місток Тевенін↔Нортон.

Свідомо НЕ додаю в kola: y-delta (вже math-вставка circuit-analysis), mesh/nodal як окремі кроки (покриті власною circuit-analysis), dependent-sources/load-line/differential-resistance (потрібні лише в майбутньому аналоговому модулі — там і місце).

## 7. Нова структура модуля (5 розділів, 28 кроків; усі 17 збережених тем на місцях)

**Розділ 1. Мова схем** (6) — графічна грамота до будь-якої теорії:
1. ДОДАТИ ref:electronics/schematic-purpose
2. ДОДАТИ ref:electronics/component-symbols
3. ДОДАТИ ref:electronics/nodes-connections
4. ДОДАТИ ref:electronics/ground-power-rails
5. own reading-schematics (тепер її «абетка» справді пройдена)
6. own net-labels-buses (pending — писати вже під це місце)

**Розділ 2. Закон Ома і прості з'єднання** (5):
1. ref electronics/ohms-law
2. ДОДАТИ ref:electronics/short-circuit
3. ДОДАТИ ref:electronics/multimeter
4. ref electronics/series-connection
5. ref electronics/parallel-connection

**Розділ 3. Дільники, міст і реальне джерело** (4):
1. ref electronics/voltage-divider (тепер після послідовного)
2. ref electronics/current-divider (після паралельного)
3. ref electronics/wheatstone-bridge (два дільники поруч)
4. ref electronics/internal-resistance (реальне джерело = ЕРС + послідовний опір; просідання як дільник)

**Розділ 4. Закони Кірхгофа й аналіз кіл** (5):
1. ref electronics/nodes-branches-loops
2. ref electronics/kcl
3. ref electronics/kvl
4. own circuit-analysis (зшивка чотирьох знарядь; y-delta/MNA — вставки)
5. ДОДАТИ ref:electronics/spice-simulation

**Розділ 5. Еквіваленти й теореми** (8):
1. ДОДАТИ ref:electronics/linear-circuit
2. ref electronics/superposition
3. ДОДАТИ ref:electronics/two-terminal-network
4. ref electronics/thevenin
5. ДОДАТИ ref:electronics/current-source
6. ref electronics/norton
7. ДОДАТИ ref:electronics/source-transformation
8. ref electronics/power-matching (максимум потужності — вінець еквівалентів)

Кумулятивність: розділ 1 не потребує нічого поза osnovy; 2 — лише osnovy+1; 3 — будується на 2; 4 — на 2–3 (перевірено текстом circuit-analysis: посилається рівно на ohms-law, series, parallel, voltage-divider, current-divider, kcl, kvl); 5 — на всьому попередньому.

## 8. Органічність ref/own

- Поточний стан: перші 18 кроків — суцільна стіна ref-ів без жодної власної нитки; обидві власні зшивки (reading-schematics, circuit-analysis) стоять ПІСЛЯ стіни, тобто нитку подано після того, як читач уже мав продертися сам.
- Після перебудови: власні статті стають воротами (reading-schematics у розділі 1) і замковим каменем (circuit-analysis у розділі 4); ref-блоки скорочуються до 3–5 поспіль у межах одного розділу зі спільною темою — прийнятно, бо статті electronics написані як самодостатні атоми, а розділова назва дає нитку.
- Місць, де ref стоїть замість потрібної власної статті, не виявив: додаткова власна «вступна» не потрібна — reading-schematics цю роль виконує. Навпаки теж ні: обидві own-статті справді кумулятивні (лінкують багато book-статей), як ref їх не замінити.
- Дрібниця: reading-schematics лінкує book:electronics/negative-feedback (форвард-згадка про зворотний зв'язок) — інлайн-попап, порядку не ламає.

## 9. Модуль як ціле

- **Назва** «Кола й закони» — влучна для очищеного модуля.
- **Місце** — правильне: одразу після osnovy, перед komponenty (теорія на ідеальних резисторах → далі реальні компоненти).
- **Розбиття**: фактично пропоную розділити навпіл — kola (DC-кола) лишається, а «аналогова» половина їде в два нові модулі: «Змінний струм, імпеданс і фільтри» (після komponenty) та «Аналогові схеми: транзистори й ОП» (після napivprovidnyky). Без другого модуля курс має системну діру: транзистор і ОП ніде не вводяться, хоча далі на них стоять zhyvlennia (ключі, драйвери), keruvannia (signal-acquisition з opamp-buffer), davachi, zvyazok.
- **Суміжне зауваження** (для аналітика napivprovidnyky): секція «Напівпровідники й діоди» зараз не містить транзистора взагалі — базові статті electronics/transistor-idea, bjt-operation, field-control там необхідні як передумова нового аналогового модуля.
- net-labels-buses — єдина pending-стаття модуля; писати її вже під нове місце (розділ 1, після reading-schematics).

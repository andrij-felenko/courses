# Аналіз модуля «Живлення» (zhyvlennia) — курс guide/embedded

Дата: 2026-07-02. Джерела: `E:/develop/courses/guide/embedded/manifest.js` (прочитано повністю),
`E:/develop/courses/book/electronics/manifest.js` і `book/physics/manifest.js` (grep за ключовими словами живлення).

## 0. Контекст модуля в курсі

Секція 6 із 14: osnovy → kola → komponenty → napivprovidnyky → cyfra-pamyat → **zhyvlennia** → mk → peryferiia → proshyvka → davachi → dyspleyi → keruvannia → zvyazok → drony.

Що читач ЗНАЄ на вході: фізика заряду/струму/поля/тепла, AC/DC, синусоїда, RMS, магнетизм та індукція (osnovy); закони кіл, RC/RL, фаза, BJT/MOSFET-ключі, ОП і зворотний зв'язок якісно (kola); резистор/конденсатор/котушка/ферит/трансформатор, запобіжники, стабілітрони й Шотткі, flyback-захист, даташити, тепловий бюджет, SOA (komponenty); діоди глибоко, флеш/EEPROM/FRAM, SiC/GaN, brown-out (napivprovidnyky); FPGA, вибір пам'яті, цілісність сигналу (cyfra-pamyat).

Чого читач ЩЕ НЕ знає: мікроконтролер як інструмент (режими сну, прошивки — секція mk далі), АЦП/ЦАП (ніде в курсі до цього місця!), теорію керування/стійкість петель (keruvannia, секція 12), протоколи шин (peryferiia).

## 1. Головний діагноз

1. **Порядок усередині модуля майже випадковий.** Перша ж тема — «Вибір топології» — порівнює buck/boost/charge-pump/flyback, яких читач ніде не бачив. USB-переговори про 9–20 В (№2–4) стоять до пояснення, навіщо пристрою різні напруги (перетворювачі — №10) і як заряджаються батареї (зарядки в курсі немає взагалі). Пари тем розірвані: міст Гретца (№14) ПІСЛЯ фільтра живлення (№11); PD (№3) і схема зчитування CC (№26) — 23 теми між ними; тепло пакета (№17) і теплова втеча (№29) — 12 тем.
2. **Модуль — 29/29 own-статей, нуль ref.** При цьому book/electronics має ГОТОВУ (basic done) лінійку атомів живлення: `rectification`, `bridge-rectifier`, `ldo`, `ldo-internals`, `switching-converter`, `buck`, `boost`, `buck-boost`, `charge-pump-conv`, `sync-rectifier`, `li-ion-charger`, `charge-termination`, `state-of-charge`, `battery-sag`, `battery-formats`, `battery-aging`, `battery-mechanics`, `battery-protection`, `battery-to-controller`, `power-path`, `power-sequencing`, `mains-safety`, `mains-transients`, `adc`, `voltage-reference-sources`, `usb-pd`, `legacy-charging`… Курс їх не підключає — own-статті модуля (переважно «вибір/розрахунок/аудит», тобто правильні кумулятивні жанри) висять без атомних основ. Це протилежність «стіни ref-ів»: стіна own-ів без фундаменту.

## 2. Порушення порядку (конкретно)

Нумерація — поточні позиції в маніфесті (1–29).

1. **topology-map (№1) стоїть перед linear-vs-switching (№10)**, хоча «вибір топології» спирається на розуміння лінійних та імпульсних перетворювачів і самих топологій. Buck/boost/charge-pump у курсі не введені ВЗАГАЛІ (атоми є в book/electronics, всі done).
2. **usb-power-map (№2), pd-sink-design (№3), usb-cables-field (№4) стоять перед battery-chemistries (№5) і перетворювачами (№10)** — переговори про підвищені напруги подано до мотивації (зарядка батарей, конверсія вниз на платі).
3. **usb-cc-adc-circuit (№26) вимагає АЦП, якого в курсі немає взагалі** — перша поява АЦП лише в mk/dma-adc і keruvannia/signal-acquisition (обидві секції пізніші). Атом `electronics/adc` готовий (done).
4. **pd-sink-design (№3) і usb-cc-adc-circuit (№26)** — протокол і його вимірювальна схема — розірвані 23 темами.
5. **bridge-rectifier-design (№14) стоїть після power-supply-filtering (№11)**, хоча згладжувач у першу чергу обробляє пульсації саме після містка.
6. **board-consumption (№9)** використовує порівняння «LDO vs buck» (comp-вставка) до появи linear-vs-switching (№10) і взагалі до пояснення LDO/buck; її proj-sleep-firmware спирається на режими сну МК (секція mk — наступна).
7. **loop-gain-measurement (№21) вимагає петлевого підсилення, запасу фази й Боде** — це keruvannia/loop-stability (секція 12, пізніше). У модулі й у пройденому курсі опертися нема на що. Середника не існує → перенести в keruvannia.
8. **bms-architecture (№15) і active-balancing (№16)** подані без зарядки літію (в курсі відсутня; `electronics/li-ion-charger` done) і до робочого знання топологій (активні балансири — це charge-pump/flyback-переноси енергії; topology-map формально №1, але сама зламана).
9. **thermal-runaway-protection (№29) відірвана від battery-pack-thermal (№17)** — а це одна розмова: нагрів пакета → Арреніус → втеча → бар'єри поширення.
10. **ac-switch-need (№7)** — комутація мережевого навантаження до будь-якої підготовки про мережу: міст — №14, а електробезпеки мережі в курсі немає ніде (`electronics/mains-safety`, `physics/current-safety` — готові done).
11. **sleep-current-audit (№18)** — прошивковий аудит режимів сну до знайомства з МК → перенести в mk (там уже живуть power-logger, current-profiler-tools, duty-cycle-current).
12. **power-spec-template (№20)** — підсумковий шаблон ТЗ стоїть посеред модуля, до flyback-transformer-design (№22), ldo-post-regulator (№24), power-tree-reading (№25) і power-budget (№27), які в таке ТЗ входять.
13. **Захисний кластер розсипаний**: reverse-polarity №6, esd-protection-circuits №28, thermal-runaway №29; а surge-protection-cascade й active-inrush-limiter узагалі живуть у «Пасивних компонентах» (де їм не місце — це активні схеми захисту входу живлення).

## 3. Пропоновані розділи (9 розділів, ~4–9 кроків)

Логіка модуля: **звідки енергія (батарея → мережа) → як нею керувати (комутація) → як її перетворювати (стабілізатори → топології) → батарейний пакет → USB → захист входів → бюджети й документи.**

### Р1. Батареї: звідки береться енергія (8)
1. ref:electronics/battery-to-controller — ДОДАТИ; готовий (done) огляд шляху «батарея → стабілізатор → шини плати» — рамка всього модуля, дзеркало фінального power-tree-reading.
2. own:energy-density-comparison — MOVE-IN з komponenty: порівняння конденсатор/суперконденсатор/акумулятор — стартова розмова про запас енергії (у «Пасивних компонентах» була завершенням лінії конденсаторів, але її суть — вибір джерела).
3. own:battery-chemistries — хімічна ЕРС уже знайома (osnovy/emf-sources).
4. ref:electronics/battery-formats — ДОДАТИ: 18650/pouch/призматичні — конкретика перед «просадкою» і пакетами.
5. ref:electronics/battery-sag — ДОДАТИ: просадка під навантаженням = внутрішній опір (kola ✓) у дії; критично для дронів.
6. ref:electronics/li-ion-charger — ДОДАТИ: CC/CV — БЕЗ цього і BMS, і швидка зарядка висять у повітрі.
7. ref:electronics/state-of-charge — ДОДАТИ: скільки лишилося; готує кулонометрію (проєкти в mk/proshyvka).
8. ref:electronics/battery-mechanics — ДОДАТИ: механіка й безпека літію — обов'язково для новачка до польових розділів.

### Р2. Мережа: безпека і випрямлення (6)
1. ref:physics/ac-power-grid — ДОДАТИ: розетка, фази, чому 50 Гц — місток від osnovy/dc-vs-ac до практики.
2. ref:physics/current-safety — ДОДАТИ: чому струм небезпечний (пороги, шляхи через тіло).
3. ref:electronics/mains-safety — ДОДАТИ: правила роботи з мережею — ПЕРЕД першою мережевою схемою, інакше курс садить новачка за 230 В без інструктажу.
4. ref:electronics/rectification — ДОДАТИ: пів/повноперіодне випрямлення — атом перед розрахунком містка.
5. own:bridge-rectifier-design — тепер на місці: після атома випрямлення.
6. own:power-supply-filtering — згладжувач одразу після містка (його пульсацій), розв'язка — місток до плат.

### Р3. Комутація потужності (4)
1. own:pwm-power-control — транзисторні ключі (kola ✓) + RC (kola ✓); ШІМ тут уперше — і він же фундамент імпульсних перетворювачів Р4.
2. own:inductive-load-switching — розвиває komponenty/flyback-protection.
3. own:inductive-clamp-design — розрахунок клампу одразу за комутацією.
4. own:ac-switch-need — тиристор/симістор; мережа вже знайома (Р2), фазове керування спирається на синусоїду (osnovy ✓).

### Р4. Стабілізація напруги (4)
1. ref:electronics/voltage-reference-sources — ДОДАТИ: від стабілітрона (komponenty/zener-schottky ✓) до bandgap — серце будь-якого стабілізатора.
2. ref:electronics/ldo — ДОДАТИ: лінійний стабілізатор як атом.
3. ref:electronics/switching-converter — ДОДАТИ: принцип імпульсника = ШІМ (Р3 ✓) + LC (komponenty ✓).
4. own:linear-vs-switching — порівняння НАРЕШТІ після обох порівнюваних.

### Р5. Топології перетворювачів (9)
1. ref:electronics/buck — ДОДАТИ (done, з матем. вставками).
2. ref:electronics/boost — ДОДАТИ.
3. ref:electronics/buck-boost — ДОДАТИ.
4. ref:electronics/charge-pump-conv — ДОДАТИ: заряд-помпа.
5. own:topology-map — тепер легітимна: «вибір топології» після самих топологій; own-стаття зшиває стіну з 4 ref-атомів.
6. ref:electronics/galvanic-isolation — ДОДАТИ (basic ще pending — легітимний стаб): розв'язка як поняття перед ізольованим flyback.
7. own:flyback-transformer-design — проєктування трансформатора flyback (трансформатор ✓ komponenty, феромагнетизм ✓ osnovy).
8. own:ldo-post-regulator — LDO-пост після імпульсника: потрібні і LDO (Р4), і пульсації (Р2/Р5).
9. own:emi-filter-design — вхідний фільтр перетворювача: шум перетворювача (щойно), X/Y-конденсатори мережі (Р2), зв'язані котушки (komponenty ✓).

### Р6. Батарейний пакет і BMS (7)
Повертаємось до батарей (Р1) уже озброєні перетворювачами й вимірюванням.
1. ref:electronics/adc — ДОДАТИ: ПЕРШИЙ АЦП курсу — без нього ні AFE монітора комірок, ні CC-схема (Р7), ні пізніші секції не читаються.
2. ref:electronics/battery-protection — ДОДАТИ: захисна ІС однієї комірки → природний трамплін до пакетного BMS.
3. own:bms-architecture — монітор комірок, ізоляція, контактор.
4. own:active-balancing — тепер після топологій (балансири = charge-pump/flyback-переноси) ✓.
5. own:battery-pack-thermal — тепло пакета, Арреніус.
6. ref:electronics/battery-aging — ДОДАТИ: старіння — просто після теплового прискорення старіння.
7. own:thermal-runaway-protection — втеча одразу за теплом пакета (була відірвана на 12 тем); MOSFET-частина спирається на SOA (komponenty ✓).

### Р7. USB як джерело (6)
1. own:usb-power-map — карта: 5 В, BC, PD.
2. own:usb-cables-field — кабелі, падіння (закон Ома ✓), польова діагностика.
3. own:pd-sink-design — переговори PD; мотивація тепер зрозуміла (заряджання Р1, перетворення Р4–Р5).
4. own:usb-cc-adc-circuit — схема зчитування CC одразу за PD (пара возз'єднана); АЦП відомий із Р6.
5. own:fast-charging-protocols — після li-ion-charger (Р1) і PD (щойно).
6. ref:electronics/power-path — ДОДАТИ: перемикання USB/батарея — пристрій, що працює під час зарядки; завершує тему джерел.

### Р8. Захист входу живлення (6)
Узагальнює ВСІ вивчені входи: батарея, мережа, USB.
1. own:reverse-polarity — діоди/MOSFET ✓.
2. own:active-inrush-limiter — MOVE-IN з komponenty: активна схема захисту (SOA ✓ там же), у «пасивних компонентах» їй не місце.
3. ref:electronics/mains-transients — ДОДАТИ: кидки в мережі — мотивація каскадного захисту.
4. own:surge-protection-cascade — MOVE-IN з komponenty: газорозрядник → MOV → TVS.
5. own:esd-protection-circuits — після esd-damage (napivprovidnyky ✓) і каскадів (щойно); контекст роз'ємів USB (Р7 ✓).
6. own:power-fail-safety — MOVE-IN з napivprovidnyky: brown-out і рятування стану — це життєвий цикл живлення плати, не «напівпровідники»; EEPROM/FRAM уже пройдені (napivprovidnyky ✓), перенос НЕ ламає її пререквізити (їде пізніше).

### Р9. Бюджети, дерево живлення, ТЗ (5)
1. own:board-consumption — середній струм; comp «LDO vs buck» тепер після Р4–Р5 ✓ (прошивкові деталі сну лишаються в proj-вставці — випереджання свідоме, кероване).
2. own:power-budget — бюджет потужності пристрою.
3. ref:electronics/power-sequencing — ДОДАТИ: черговість увімкнення шин — обов'язкова для багатошинних плат перед читанням дерев.
4. own:power-tree-reading — читання реальних дерев живлення; дзеркало опенера Р1.
5. own:power-spec-template — шаблон ТЗ як підсумок модуля (був №20 — посередині).

Разом: 55 кроків = 27 own модуля (29 − 2 move_out) + 4 move_in + 24 ref. Усі 29 поточних тем враховано, жодної не загублено.

## 4. move_out

| Тема | Куди | Чому |
|---|---|---|
| own:sleep-current-audit («Аудит струму спокою плати») | mk | Прошивковий аудит режимів сну МК; МК з'являється лише в наступній секції. У mk уже є кластер power-logger + current-profiler-tools + duty-cycle-current — аудит його завершує. |
| own:loop-gain-measurement («Вимірювання петлевого підсилення») | keruvannia | Вимагає петлевого підсилення, запасів стійкості й Боде — це keruvannia/loop-stability (пізніше). Після loop-stability читач знає і перетворювачі (zhyvlennia позаду), і стійкість — інжекція Мідлбрука стає природним практикумом. |

## 5. move_in

| Тема | Звідки | Куди в модулі | Чому |
|---|---|---|---|
| own:energy-density-comparison | komponenty | Р1 крок 2 | Порівняння «конденсатор/суперконденсатор/акумулятор» — це розмова про вибір ДЖЕРЕЛА енергії, а не про пасивний компонент. |
| own:active-inrush-limiter | komponenty | Р8 крок 2 | Активна схема (MOSFET + SOA) обмеження пускового струму — захист входу живлення; у «Пасивних компонентах» вона чужа. |
| own:surge-protection-cascade | komponenty | Р8 крок 4 | Каскад газорозрядник→MOV→TVS — захист входу живлення; тематично зшивається з mains-transients і ESD. |
| own:power-fail-safety | napivprovidnyky | Р8 крок 6 | Brown-out, супервізор, рятування стану — це поведінка ЖИВЛЕННЯ плати; у «Напівпровідниках» стояла лише через сусідство з FRAM. Перенос пізніше за курсом — пререквізити цілі. |

## 6. Прогалини (missing)

Усі закриваються ГОТОВИМИ статтями book/electronics і book/physics — new: не потрібен жоден. Критичні (без них новачок впирається в стіну): li-ion-charger, adc, mains-safety + current-safety, rectification, ldo + switching-converter + buck/boost/buck-boost/charge-pump-conv. Повний перелік із обґрунтуванням — у структурованому виводі (24 позиції, всі продубльовані ДОДАТИ-кроками в розділах). Єдина зі статусом pending — electronics/galvanic-isolation (стаб легітимний, черга письма).

Свідомо НЕ додано (щоб не задвоїти own-статті курсу): electronics/usb-pd і usb-pd-sink (дублюють own:pd-sink-design — навіть comp-вставка однойменна comp-pd-trigger.md), electronics/reverse-polarity-protection (дублює own:reverse-polarity), electronics/bridge-rectifier (own:bridge-rectifier-design), electronics/quick-charge (own:fast-charging-protocols), electronics/charge-termination (покривається li-ion-charger + own:bms), electronics/voltage-supervisor-ic (pending; покривається own:power-fail-safety).

## 7. Органічність ref/own

- Поточний стан: 29/29 own, 0 ref — власні статті-«порівняння/розрахунки» без атомної бази. Це і є головна причина «стін незнаного».
- Жанрово own-статті модуля правильні (вибір топології, розрахунок клампу, аудит, шаблон ТЗ — кумулятивні кути), тож фікс — не переписування, а ПІДКЛАДАННЯ ref-атомів під них.
- У новій структурі стіни ref-ів розбиті own-зшивками: 4 атоми топологій → own:topology-map; 3 атоми стабілізації → own:linear-vs-switching; батарейні атоми Р1 читаються ниткою «формат → просадка → зарядка → залишок → безпека».
- Дублікати book↔guide (pd-sink, reverse-polarity, bridge-rectifier, fast-charging) варто узгодити взаємними book:-лінками, а не додатковими кроками.

## 8. Модуль як ціле

- **Назва** «Живлення» влучна. `scope` порожній — заповнити: «від батареї, розетки й USB до шин плати: перетворення, захист, бюджети».
- **Місце в курсі** (6/14, перед mk) правильне: живити плату треба вміти до роботи з МК; прошивкові хвости (sleep-audit, loop-gain) винесено. Прошивкові proj-вставки, що лишаються (proj-sleep-firmware, proj-bms-state-machine, proj-pd-state-machine, proj-cc-reader), — свідоме випереджання в опційному шарі; альтернатива — помітити їх «повернись після mk».
- **Ділити чи ні:** після реструктуризації ~55 кроків / 9 розділів — великий, але однорідний модуль; природна лінія розрізу, якщо треба: «Джерела енергії» (Р1, Р2, Р6, Р7) + «Перетворення й надійність» (Р3–Р5, Р8–Р9). Поки розділи дають навігацію — краще лишити одним модулем.
- **Суміжний безлад поза модулем:** кластер вимірювання споживання розмазаний по 3 секціях (mk/power-logger, mk/current-profiler-tools, mk/duty-cycle-current, proshyvka/measure-consumption + перенесений sleep-current-audit) — зібрати одним розділом у mk або proshyvka.
- **Сонячне живлення** (electronics/photovoltaic-cell, real-sun-mppt — обидві done) свідомо поза модулем: курсова лінія — дрони на батареях. Якщо «автономні системи» включають стаціонарні вузли — додати мініблок у Р1.
- Кандидати на майбутнє поглиблення Р1/Р6: physics/battery-discharge-curve (pending), electronics/self-discharge (pending), electronics/battery-impedance (done), electronics/smbus-smart-battery (done).

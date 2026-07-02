# Аналіз модуля «komponenty» — Пасивні компоненти (guide/embedded)

Дата: 2026-07-02. Джерела: E:/develop/courses/guide/embedded/manifest.js (рядки 94–123), манифести книг electronics/physics.

## 1. Поточний стан

27 тем у пласкому списку: 12 ref-ів (резистор → трансформатор) + 15 власних статей. Модуль стоїть ТРЕТІМ, після «osnovy» і «kola».

## 2. Головний діагноз

1. **Глобальна інверсія:** komponenty стоїть ПІСЛЯ kola, хоча kola вже вовсю використовує компоненти: «Стала часу RC», «Каскадовані RC-ланки», «Родини фільтрів» — перед «Конденсатор»; «Стала часу RL» — перед «Котушка»; «Генератор Пірса: обв'язка кварцу» — перед будь-яким вводом кварцу (кварцу в курсі взагалі не було). Правильний глобальний порядок: osnovy → komponenty (принаймні розділи про R/C/L) → kola.
2. **Чужі теми:** діодні (zener-schottky, flyback-protection, surge-protection-cascade), транзисторний і МК-практикуми (datasheet-bjt, datasheet-mcu), силова схема (active-inrush-limiter) — в «пасивних компонентах» їм не місце, і всі вони ламають порядок (діоди/МК подаються пізніше).
3. **Прогалини-стіни:** імпеданс/реактивність, кварцовий резонатор, п'єзоефект, варистор, друкована плата, корпуси, даташит-грамота — усе це використовується темами модуля, але ніде в курсі до цього місця не вводиться. Усі прогалини закриваються ГОТОВИМИ статтями книг (18 ref-ів, з них 17 done, 1 pending).

## 3. Конкретні порушення порядку

1. `zener-schottky` (#14) стоїть за секцію ДО статті «Діоди» (napivprovidnyky): спеціальні діоди перед p-n переходом і діодом узагалі.
2. `flyback-protection` (#15) вимагає демпферного діода — діоди лише в наступній секції.
3. `surge-protection-cascade` (#22) вимагає TVS-діода (наступна секція) і варистора (в курсі відсутній).
4. `electronics/capacitor-parasitics` (#6) стоїть перед `electronics/inductor-coil` (#8): ESL і власний резонанс — це індуктивність; плюс потрібен імпеданс, якого в курсі нема взагалі.
5. `electronics/ferrite-bead` (#10) характеризується кривою «імпеданс від частоти» — імпеданс не вводився.
6. `ceramic-mems-resonators` (#17) і `tcxo-ocxo` (#18) спираються на кварцовий резонатор і п'єзоефект — жодного нема в курсі (comp-вставка mems-vs-quartz прямо порівнює з кварцом; TCXO = термокомпенсований КВАРЦОВИЙ генератор).
7. `datasheet-mcu` (#21) — даташит мікроконтролера за 4 секції до вводу МК (секція mk).
8. `datasheet-bjt` (#20) — транзисторний практикум у пасивах; його місце біля BJT-кластера kola.
9. `active-inrush-limiter` (#24) — MOSFET + hot-swap контролер: дизайн вузла живлення, не пасив.
10. `pcb-thermal-design` (#25) стоїть перед `pcb-assembly-methods` (#26): exposed pad і теплові via вимагають знання корпусів SMD і самої плати; вводу друкованої плати в курсі немає взагалі.
11. `energy-density-comparison` (#19) порівнює з акумулятором до «Хімій батарей» (zhyvlennia) — на побутовому рівні прийнятно, лишаю на місці з приміткою.
12. Органічність: перші 12 кроків — суцільна стіна ref-ів без жодної власної статті-нитки.

## 4. Пропонована структура: 7 розділів, 39 кроків

### Розділ 1. Резистори й захисні пасиви (6)
Спирається лише на osnovy (опір, R(T), джоулеве тепло, пробій повітря).
1. ref:electronics/resistor — Резистор
2. ref:electronics/resistor-marking — Номінали й допуск
3. ref:electronics/potentiometer — Потенціометр і підлаштовник
4. **ДОДАТИ** ref:electronics/ntc-thermistor — НТС-термістор (R(T); готує PPTC і майбутні теплові теми)
5. **ДОДАТИ** ref:electronics/varistor — Варистор (R(U), захист від сплесків; потрібен для surge-cascade у zhyvlennia)
6. own:fuses-ptc — Запобіжники (плавкі + PPTC — продовження історії PTC)

### Розділ 2. Конденсатори й запас енергії (5)
1. **ДОДАТИ** ref:physics/conductors-insulators — міст «провідник vs діелектрик» перед діелектриками
2. ref:electronics/capacitor — Конденсатор
3. ref:electronics/capacitor-dielectrics — Діелектрики конденсаторів
4. ref:electronics/supercapacitor — Суперконденсатор
5. own:energy-density-comparison — порівняння з акумулятором на побутовому рівні (хімія батарей — далі в zhyvlennia)

### Розділ 3. Котушки, трансформатори, реле (5)
Магнітна база вся в osnovy (магнітне поле, феромагнетизм, індукція, електромагніт).
1. ref:electronics/inductor-coil — Котушка
2. ref:electronics/inductor-types — Осердя й насичення
3. ref:electronics/mutual-inductance — Зв'язані котушки
4. ref:electronics/transformer — Трансформатор
5. **ДОДАТИ** ref:electronics/relay — Реле (електромагніт + контакти; в курсі відсутнє взагалі)

### Розділ 4. Змінний струм у компонентах: імпеданс і паразити (5)
Тепер відомі і C, і L → можна говорити про частотну поведінку.
1. **ДОДАТИ** ref:electronics/reactance — Реактивність (опір C і L змінному струму)
2. **ДОДАТИ** ref:electronics/impedance — Імпеданс
3. ref:electronics/capacitor-parasitics — Паразити конденсатора (ПЕРЕНЕСЕНО після котушок: ESR/ESL/власний резонанс)
4. ref:electronics/ferrite-bead — Феритова намистина (імпеданс від частоти, EMI)
5. **ДОДАТИ** ref:electronics/lc-resonance — LC-резонанс (підводить до резонаторів)

### Розділ 5. Резонатори й тактування (6)
1. **ДОДАТИ** ref:physics/piezoelectric-effect — П'єзоефект
2. **ДОДАТИ** ref:electronics/quartz-resonator — Кварцовий резонатор
3. **ДОДАТИ** ref:electronics/quartz-rlc-model — RLC-модель кварцу (Q, серія/паралель — база для порівнянь і Пірса в kola)
4. **ДОДАТИ** ref:electronics/watch-crystal-rtc — Годинниковий кварц 32.768 кГц (RTC кожної embedded-плати)
5. own:ceramic-mems-resonators — Керамічні резонатори (тепер порівняння з кварцом легітимне)
6. own:tcxo-ocxo — TCXO та OCXO

### Розділ 6. Даташити, дератинг і тепловий бюджет (5)
1. **ДОДАТИ** ref:electronics/datasheet-structure — Структура даташита (новачок бачить даташит уперше)
2. **ДОДАТИ** ref:electronics/datasheet-graphs — Графіки даташита (криві дератингу)
3. own:datasheet-practice — Практикум даташитів
4. **ДОДАТИ** ref:electronics/power-derating — Дератинг потужності
5. own:thermal-budget — Тепловий бюджет системи (θ-ланцюжки; osnovy: thermal-resistance, heat-transfer)

### Розділ 7. Плата: корпуси, монтаж, тепло (7)
1. **ДОДАТИ** ref:electronics/pcb-layout — Друкована плата (шари, доріжки, via — в курсі ніде не вводилася)
2. **ДОДАТИ** ref:electronics/packages — Корпуси компонентів
3. **ДОДАТИ** ref:electronics/smd-marking — Маркування SMD
4. own:pcb-assembly-methods — Методи монтажу (THT і SMD)
5. own:smd-rework — Ручне паяння SMD
6. own:pcb-thermal-design — Тепловідведення на PCB (тепер після теплобюджету, плати і корпусів)
7. **ДОДАТИ** ref:electronics/cables-connectors — Кабелі й конектори (у книзі стаття зареєстрована, basic=pending)

Перевірка: всі 21 тема, що лишаються в модулі, розкладені по розділах; жодна не загублена.

## 5. move_out (6)

| Тема | Куди | Чому |
|---|---|---|
| own:zener-schottky | napivprovidnyky (після «Діоди») | спецдіоди перед діодом узагалі — інверсія; це напівпровідники |
| own:flyback-protection | napivprovidnyky (після zener-schottky) | демпферний діод вимагає діодів; зв'язати інлайн з inductive-load-switching/inductive-clamp-design у zhyvlennia |
| own:surge-protection-cascade | zhyvlennia (біля esd-protection-circuits) | координація GDT+MOV+TVS = системний захист входів; потребує TVS (діоди) і варистора (мій розділ 1) |
| own:datasheet-bjt | kola (після bjt-vs-mosfet) | транзисторний практикум має жити біля BJT-кластера; якщо BJT-кластер переїде — їде разом |
| own:datasheet-mcu | mk (біля mcu-selection/mcu-checklist) | даташит МК за 4 секції до вводу МК |
| own:active-inrush-limiter | zhyvlennia (біля reverse-polarity) | power-path дизайн на MOSFET + hot-swap контролер; там же перед ним додати ref:electronics/inrush-ntc (пасивний варіант, done у книзі) |

## 6. move_in

Немає. Кандидати kola/rc-time-constant і kola/rl-time-constant краще лишити в kola і виправити ГЛОБАЛЬНИЙ порядок (kola після komponenty), ніж тягати кроки.

## 7. Прогалини (усі закриті готовими статтями книг)

Новачку: conductors-insulators, reactance, impedance, datasheet-structure, datasheet-graphs, pcb-layout, packages.
Для повноти теми: ntc-thermistor, varistor, relay, lc-resonance, piezoelectric-effect, quartz-resonator, quartz-rlc-model, watch-crystal-rtc, power-derating, smd-marking, cables-connectors (pending).
Усі — ref, нових статей писати не треба (лише cables-connectors у книзі ще не написана — стоїть у черзі pending).

## 8. Органічність ref/own

- Було: стіна з 12 ref-ів поспіль без нитки. Стало: кожен розділ закінчується власною статтею-практикою (fuses-ptc, energy-density-comparison, tcxo-ocxo, thermal-budget, pcb-thermal-design) — ref-и працюють на неї.
- Додані ref-ланцюжки (даташити 2 шт., кварц 3 шт.) — короткі й підводять до власних статей курсу; це не «стіна».
- Місць, де замість ref потрібна власна кумулятивна стаття, не знайшов: усі власні статті модуля справді кумулятивні (практикуми, порівняння, бюджети).

## 9. Модуль як ціле

- **Назва** «Пасивні компоненти» вже не влучна: реле, кварцові резонатори з TCXO, даташити, корпуси й монтаж — не пасиви. Пропозиція: **«Компоненти й монтаж»** (або «Компоненти: від резистора до плати»).
- **Позиція:** модуль (принаймні розділи 1–4) має стояти ПЕРЕД kola — поміняти секції місцями: osnovy → komponenty → kola. Тоді kola отримує C і L для RC/RL/фільтрів, а Пірсів генератор — кварц із розділу 5. Komponenty від kola майже нічого не потребує (опір/потужність — з osnovy).
- **Розбиття:** 39 кроків / 7 розділів — прийнятно для одного модуля; якщо захочеться дрібніше, природний шов — між розділами 5 і 6: «Пасивні компоненти» (розд. 1–5) + «Компонент на платі: даташити, тепло, монтаж» (розд. 6–7). Не наполягаю.
- **Сигнал аналітику kola:** pierce-oscillator-design ставити ПІСЛЯ кварцового ланцюжка (мій розділ 5); datasheet-bjt приходить до вас.
- **Сигнал аналітику zhyvlennia:** приходять surge-protection-cascade і active-inrush-limiter (+ ref:electronics/inrush-ntc перед ним).
- **Сигнал аналітику napivprovidnyky:** приходять zener-schottky і flyback-protection — ставити після «Діоди».

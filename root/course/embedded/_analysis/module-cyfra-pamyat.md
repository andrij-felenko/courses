# Аналіз модуля «cyfra-pamyat» — «Цифра й памʼять» (guide/embedded)

## 1. Що в модулі зараз (11 тем, порядок за маніфестом)

1. `ref:electronics/shift-register` — Зсувний регістр
2. `own:pal-to-fpga` — Від PAL до FPGA
3. `own:fpga-flow` — Потік розробки
4. `own:fpga-vs-mcu` — FPGA чи МК
5. `own:when-memory-runs-out` — Коли пам'яті мало
6. `own:choosing-memory` — Вибір пам'яті
7. `own:synchronous-reset` — Синхронне й асинхронне скидання
8. `ref:communications/transmission-lines` — Лінія передачі на PCB
9. `own:signal-integrity` — Цілісність сигналу
10. `own:ddr-signal-integrity` — Цілісність сигналу DDR-шини
11. `own:custom-instruction` — Кастомні інструкції процесора

Контекст: попередні секції курсу — osnovy (фізика), kola (кола, транзистори BJT/MOSFET, ОП), komponenty (пасив, кварци, монтаж), napivprovidnyky (діоди + NOR/NAND-флеш + EEPROM/FRAM + MRAM/RRAM/PCM). Далі йдуть zhyvlennia → mk → peryferiia → …

## 2. Головний діагноз

Модуль називається «Цифра й памʼять», але **самої цифри в ньому (і в усьому курсі до нього) немає**. Курс стрибає від діодів одразу до зсувного регістра і FPGA, оминувши весь фундамент: біти й двійкову систему, логічні рівні, вентилі, булеву алгебру, тригери, такт, лічильники, автомати. Перша ж тема модуля — зсувний регістр — складена з D-тригерів, про які читач не чув. Добра новина: практично весь відсутній фундамент уже написаний як done-статті у книгах electronics (секція digital), math і programming — модуль лагодиться майже виключно ref-ами, без жодної нової статті.

## 3. Порушення порядку (конкретно)

1. **«Зсувний регістр» стоїть першим кроком**, хоча зсувний регістр — це ланцюжок D-тригерів під спільним тактом; ні вентилів, ні тригерів, ні поняття такту курс до цього не подавав (їх нема ніде в курсі взагалі).
2. **pal-to-fpga спирається на булеву алгебру і базові вентилі** (стаття прямо лінкує `topic:math/boolean-algebra` і `topic:electronics/basic-gates`, оперує «сумою добутків», матрицями AND-OR, серією 74) — цих тем у курсі не було.
3. **fpga-flow вимагає LUT, HDL і уявлення про тканину FPGA** (math-вставки про LUT-covering і routing) — не подані.
4. **fpga-vs-mcu порівнює з мікроконтролером** (оперує перериваннями, опитуванням у циклі, прошивкою), а секція mk — аж через одну (після zhyvlennia). Стаття сама коротко визначає МК («Два слова про назви»), тож частково самоносна, але глибші поняття (polling vs interrupts) з'являться лише в mk.
5. **synchronous-reset потребує D-тригерів, регістрів, скінченних автоматів і метастабільності** (лінкує `topic:electronics/register`, `finite-state-machines`, `d-flip-flop`; посилається на макрокомірки з pal-to-fpga) — тригерів/автоматів курс не давав; метастабільність (серце двотригерного синхронізатора) — теж.
6. **ddr-signal-integrity вимагає знати, що таке SDRAM/DDR**, а кроку про SDRAM/DDR у модулі (і в курсі) немає — лише інлайн-згадки. Так само choosing-memory всім деревом рішень спирається на `topic:electronics/memory-controller`, `sd-card`, `emmc-ssd`, `sdram-ddr`, яких у курсі кроками нема.
7. **custom-instruction вимагає ISA, циклу вибірка-декодування-виконання, будови процесора** (лінкує `topic:programming/isa`, `fetch-decode-execute`, `processor-parts`) — це матеріал секції mk, що йде пізніше. Тема висить без процесора.
8. **Пам'ять розірвана по трьох секціях**: фізика комірок (memory-cell-physics) — в osnovy (секція 1, до того як читач дізнався про біти), NOR/NAND, EEPROM/FRAM, MRAM/RRAM/PCM — у napivprovidnyky (де назви NOR/NAND згадують вентилі, яких читач не бачив), а «Коли пам'яті мало»/«Вибір пам'яті» — тут. Мотивація (when-memory-runs-out) і вибір (choosing-memory) стоять коректно одна за одною, але без-контекстно.
9. Внутрішній порядок SI-хвоста (transmission-lines → signal-integrity → ddr-signal-integrity) — правильний і кумулятивний (статті прямо пишуть «у попередньому кроці»); бракує лише сходинки «фронти й час наростання» перед лініями передачі.
10. **when-memory-runs-out оперує стеком, купою, фрагментацією** — програмістські поняття, яких нуль-новачок ще не бачив (у курсі взагалі немає програмістського фундаменту до proshyvka). Це загальнокурсова прогалина, не лише цього модуля.

## 4. Що є в книгах (перевірено грепом маніфестів)

- **electronics, секція digital** — величезний done-набір: why-digital, logic-levels-as-ranges, noise-margin, logic-families, logic-74, threshold-schmitt, basic-gates, nand-nor, xor-comparison, cmos-gate, combinational-circuits, gates-to-functions, multiplexer, state-memory, sr-latch, d-flip-flop, edge-vs-level, register, clock-signal, counters, shift-register, finite-state-machines, metastability-timing, twos-complement, sampling-quantization, adc, adc-resolution, adc-types, dac, memory-hierarchy, sdram-ddr, memory-controller, sd-card, emmc-ssd, edges-rise-time, eye-diagram, crosstalk, ground-bounce, programmable-logic, lut, inside-fpga, hdl … (усі перелічені — basic:done).
- **math**: boolean-algebra (done), why-binary (done), positional-systems (done); binary-arithmetic — pending (не беру).
- **programming**: bits-bytes-endianness (done); isa, fetch-decode-execute, processor-parts — існують (їх лінкує custom-instruction).
- **communications**: transmission-lines (done); termination/eye-diagram — pending (не беру, покрито electronics-статтями і власною signal-integrity).

Висновок: **жодної new:-статті не потрібно** — всі прогалини закриваються done-ref-ами.

## 5. Пропоновані розділи (усі 10 тем модуля збережено; custom-instruction — у move_out)

### Розділ 1. Навіщо цифра: біти, числа, рівні (8 кроків)
Міст від аналогової половини курсу до цифрової: чому дискретні рівні перемагають шум, як числа стають бітами, де фізична межа «0» і «1».
1. ДОДАТИ ref:electronics/why-digital — Навіщо цифра
2. ДОДАТИ ref:math/why-binary — Чому двійкова
3. ДОДАТИ ref:math/positional-systems — Позиційні системи (двійкова, шістнадцяткова)
4. ДОДАТИ ref:programming/bits-bytes-endianness — Біти й порядок байтів
5. ДОДАТИ ref:electronics/twos-complement — Доповняльний код
6. ДОДАТИ ref:electronics/logic-levels-as-ranges — Рівні «0» і «1»
7. ДОДАТИ ref:electronics/noise-margin — Запас завадостійкості
8. ДОДАТИ ref:electronics/threshold-schmitt — Поріг і Шмітт

### Розділ 2. Вентилі й комбінаційна логіка (10 кроків)
Від MOSFET (bjt-vs-mosfet у kola) до вентиля, від вентиля до функцій. Прямий пререквізит pal-to-fpga (сума добутків, серія 74).
1. ДОДАТИ ref:math/boolean-algebra — Булева алгебра
2. ДОДАТИ ref:electronics/basic-gates — Базові вентилі
3. ДОДАТИ ref:electronics/nand-nor — NAND і NOR
4. ДОДАТИ ref:electronics/xor-comparison — XOR
5. ДОДАТИ ref:electronics/cmos-gate — CMOS-вентиль
6. ДОДАТИ ref:electronics/logic-families — Логічні сімейства
7. ДОДАТИ ref:electronics/logic-74 — Логіка 74
8. ДОДАТИ ref:electronics/combinational-circuits — Комбінаційні схеми
9. ДОДАТИ ref:electronics/gates-to-functions — Складні функції
10. ДОДАТИ ref:electronics/multiplexer — Мультиплексор

### Розділ 3. Такт і стан: послідовна логіка (10 кроків)
Пам'ять стану → тригери → такт → регістри/лічильники → зсувний регістр (нинішній перший крок стає на законне місце) → автомати → метастабільність (пререквізит synchronous-reset і CDC).
1. ДОДАТИ ref:electronics/state-memory — Пам'ять стану
2. ДОДАТИ ref:electronics/sr-latch — SR-засувка
3. ДОДАТИ ref:electronics/d-flip-flop — D-тригер
4. ДОДАТИ ref:electronics/clock-signal — Тактовий сигнал
5. ДОДАТИ ref:electronics/edge-vs-level — Фронт і рівень
6. ДОДАТИ ref:electronics/register — Регістр
7. ДОДАТИ ref:electronics/counters — Лічильники
8. ref:electronics/shift-register — Зсувний регістр (був кроком №1 модуля)
9. ДОДАТИ ref:electronics/finite-state-machines — Скінченні автомати
10. ДОДАТИ ref:electronics/metastability-timing — Метастабільність

### Розділ 4. Міст між світами: АЦП і ЦАП (5 кроків)
Ніде в курсі АЦП/ЦАП не вводяться, а вже наступна секція (zhyvlennia: usb-cc-adc-circuit) і далі mk (dma-adc), keruvannia (signal-acquisition) ними користуються. Це останнє місце, де їх можна ввести вчасно.
1. ДОДАТИ ref:electronics/sampling-quantization — Дискретизація й квантування
2. ДОДАТИ ref:electronics/adc — АЦП
3. ДОДАТИ ref:electronics/adc-resolution — Роздільність АЦП
4. ДОДАТИ ref:electronics/adc-types — Типи АЦП
5. ДОДАТИ ref:electronics/dac — ЦАП

### Розділ 5. Пам'ять: комірка, ієрархія, RAM (5 кроків)
1. own:memory-cell-physics — Фізика комірок (MOVE_IN з osnovy; when-memory-runs-out лінкує її як guide-пререквізит «шість транзисторів на біт»)
2. ДОДАТИ ref:electronics/memory-hierarchy — Ієрархія пам'яті
3. own:when-memory-runs-out — Коли пам'яті мало
4. ДОДАТИ ref:electronics/sdram-ddr — SDRAM і DDR (без цього ddr-signal-integrity висить)
5. ДОДАТИ ref:electronics/memory-controller — Контролер пам'яті (choosing-memory на нього спирається)

### Розділ 6. Нелетка пам'ять і вибір (6 кроків)
1. own:nor-vs-nand — NOR і NAND (MOVE_IN з napivprovidnyky; назви — від вентилів розділу 2)
2. own:eeprom-fram — EEPROM і FRAM (MOVE_IN з napivprovidnyky)
3. ДОДАТИ ref:electronics/sd-card — SD-картка
4. ДОДАТИ ref:electronics/emmc-ssd — eMMC і SSD
5. own:mram-rram-pcm — MRAM, RRAM і PCM (MOVE_IN з napivprovidnyky)
6. own:choosing-memory — Вибір пам'яті (капстоун: дерево рішень уже лінкує всі попередні кроки)

### Розділ 7. Програмована логіка: від PAL до FPGA (7 кроків)
1. own:pal-to-fpga — Від PAL до FPGA
2. ДОДАТИ ref:electronics/lut — LUT
3. ДОДАТИ ref:electronics/inside-fpga — Усередині FPGA
4. ДОДАТИ ref:electronics/hdl — HDL
5. own:fpga-flow — Потік розробки
6. own:synchronous-reset — Синхронне й асинхронне скидання (лінкує макрокомірки pal-to-fpga, тригери й автомати — усі вже подані)
7. own:fpga-vs-mcu — FPGA чи МК (закриває розділ і перекидає місток до секції mk)

### Розділ 8. Швидка цифра на платі (4 кроки)
1. ДОДАТИ ref:electronics/edges-rise-time — Фронти й час наростання (чому «цифровий» фронт — це високі частоти)
2. ref:communications/transmission-lines — Лінія передачі на PCB (був кроком №8)
3. own:signal-integrity — Цілісність сигналу (стаття прямо продовжує transmission-lines)
4. own:ddr-signal-integrity — Цілісність сигналу DDR-шини (тепер після SDRAM/DDR з розділу 5)

Разом: 55 кроків, 8 розділів. Усі 10 тем модуля (крім винесеної custom-instruction) на місцях.

## 6. move_out

- **own:custom-instruction → секція mk** (одразу після risc-cisc). Стаття вимагає ISA, декодера, циклу вибірки-виконання, будови ядра (`topic:programming/isa`, `fetch-decode-execute`, `processor-parts`) — усе це подає mk. Зворотне посилання на fpga-vs-mcu лишиться коректним (cyfra-pamyat раніше за mk).

## 7. move_in

- **own:memory-cell-physics ← osnovy.** Фізика SRAM/DRAM/floating-gate-комірок у секції 1 стояла до того, як читач дізнався про біт, транзистор і пам'ять; тут вона відкриває розділ про пам'ять, і when-memory-runs-out уже лінкує її як пройдену.
- **own:nor-vs-nand ← napivprovidnyky.** Це стаття про флеш-пам'ять, а не про діоди; її назва й механіка — від вентилів NOR/NAND, які подано тут у розділі 2. У napivprovidnyky вона стояла до будь-якої згадки вентилів.
- **own:eeprom-fram ← napivprovidnyky.** Технологія нелеткої пам'яті; логічне місце — поруч із NOR/NAND і перед choosing-memory, який на неї спирається.
- **own:mram-rram-pcm ← napivprovidnyky.** «Нові нелеткі пам'яті» — прямий шматок розділу про нелетку пам'ять, перед вибором пам'яті.

(power-fail-safety з napivprovidnyky не забираю: попри звʼязок із рятуванням стану в NVM, вона потребує brown-out-детектора МК — їй місце в zhyvlennia або mk.)

## 8. Прогалини (всі закриваються done-статтями книг; new: не потрібно)

(а) для новачка: усе з розділів 1–3 — двійкова система, біти/байти, доповняльний код, логічні рівні/запас/Шмітт, булева алгебра, вентилі (базові, NAND/NOR, XOR, CMOS), сімейства, серія 74, комбінаційні схеми, складні функції, мультиплексор, пам'ять стану, засувки/тригери, такт, фронт/рівень, регістр, лічильники, автомати, метастабільність.
(б) для повноти модуля: АЦП/ЦАП-міст (5 статей), ієрархія пам'яті, SDRAM/DDR, контролер пам'яті, SD-картка, eMMC/SSD, фронти й час наростання.

## 9. Органічність ref/own

- Зараз модуль — 9 own + 2 ref; після ремонту — 12 own + 43 ref. Розділи 1–3 виходять суцільними «стінами ref-ів» (8–10 поспіль без власної статті курсу). Це помʼякшено тим, що electronics/digital написана як послідовна лінійка (why-digital → рівні → вентилі → тригери → …), але для нитки курсу варто розглянути короткі власні містки-вступи до розділів 1 і 3 — або хоча б перевірити при верстці, що ref-и читаються один з одного. Практикум «вентилі на макетці» вже існує як вставка comp-74hc-breadboard у basic-gates — окрема new-стаття не потрібна.
- Зворотний випадок (own там, де досить ref) не знайдений: усі own-статті модуля справді кумулятивні (лінкують guide-сусідів, «у попередньому кроці» тощо) і на своїх місцях.

## 10. Модуль як ціле

- Назва «Цифра й памʼять» — влучна і після ремонту стає чесною (зараз «цифри» в модулі нема).
- Позиція в курсі правильна: після napivprovidnyky (транзистор → вентиль), перед mk (логіка → процесор). Але **між cyfra-pamyat і mk вклинилася zhyvlennia** — за логікою знань mk мала б іти одразу після цифри (тригери/регістри/автомати свіжі в голові), а живлення — або до цифри, або після mk. Втім, розділ АЦП тут якраз рятує zhyvlennia (usb-cc-adc-circuit).
- 55 кроків — на межі. Якщо захочеться різати, природний шов: модуль А «Цифрова логіка: від біта до FPGA» (розділи 1–4, 7) і модуль Б «Памʼять і швидкі сигнали на платі» (розділи 5, 6, 8). Але й вісім розділів в одному модулі працюють — вони строго кумулятивні.
- Загальнокурсове (поза моїм модулем, для зведення): when-memory-runs-out оперує стеком/купою/фрагментацією — програмування в курсі не вводиться ніде до proshyvka; komponenty/datasheet-mcu читає даташит МК до того, як курс пояснив, що таке МК.

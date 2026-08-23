# Аналіз модуля «mk» — «Мікроконтролер і процесор» (guide/embedded)

Дата: 2026-07-02. Джерела: `E:/develop/courses/guide/embedded/manifest.js` (повністю), маніфести книг `programming`, `electronics`, `communications`, `math`, `algorithms`; вибірково відкриті статті модуля: `von-neumann-harvard`, `baremetal-vs-framework`, `jtag-swd-tools`, `duty-cycle-current`, `autonomous-system`, `mavlink-commands`, `power-logger`, `current-profiler-tools`, `ota-server` (перші ~10–30 рядків кожної).

## 1. Діагноз модуля

Модуль mk — 33 теми, **усі own, жодного ref** — при тому, що книга `book/programming` має дві величезні готові секції: `computer-architecture` (~50 статей: що таке процесор, цикл виконання, ISA, конвеєр, кеш, DMA-контролер…) і `embedded-systems` (~170 статей: мікроконтролер, GPIO-регістри, переривання, таймери, watchdog, режими сну, bootloader, прошивання…). Курс, що декларує «нуль програмування» на вході, жодного разу не використовує ці атоми.

Наслідок перший: **новачкова стіна на першому ж кроці.** `von-neumann-harvard` починається з «Класичний процесор тримає "вузьке місце фон Неймана": код і дані живуть в одній пам'яті й ходять однією шиною» — а курс до цього моменту не дав ані «що таке процесор», ані «що таке програма», ані «що таке пам'ять/шина», ані двійкової системи. Для аудиторії «нуль програмування» це стіна з перших рядків.

Наслідок другий: **модуль став смітником для тем із другої половини курсу.** MAVLink-команди, автономна система, планування місій, GCS-порівняння, OTA-сервер, Wi-Fi fast connect, Edge AI — усе це вимагає зв'язку (секція 13), давачів (10), керування (12) і дронової частини (14). Статті самі це визнають: `autonomous-system` лінкує `root:embedded/proportional-control` (keruvannia) і `root:embedded/imu-barometer` (davachi); `mavlink-commands` лінкує `root:embedded/pymavlink` (zvyazok); `power-logger` і `current-profiler-tools` починаються з «[Чесно виміряти споживання] ми вже вміємо» — з посиланням на `measure-consumption` із **наступної через одну** секції proshyvka.

Наслідок третій: **розірвані внутрішні ланцюги.** Відлагодження (jtag-swd-tools, крок 6; openocd-gdb, 14; core-dump, 15) стоїть до прошивання (esptool-workflow, 27), хоча `jtag-swd-tools` сама посилається на `programming/flashing` і `programming/bootloader`. DMA-застосунки (кроки 8–9) стоять до введення АЦП (нема ніде в курсі) і SPI/I2S (SPI — лише в наступній секції peryferiia).

## 2. Конкретні порушення порядку

1. **von-neumann-harvard — перший крок модуля** — вимагає понять «процесор», «пам'ять», «шина», «код у пам'яті»; у курсі до нього нема ні що таке програма, ні що таке процесор, ні двійкової системи (їх нема в курсі взагалі — є в книгах: `programming/what-is-processor`, `math/why-binary` тощо).
2. **baremetal-vs-framework (крок 5)** прямо пише: «setup()/loop() і digitalWrite з прикладів ми мовчки використовуємо ввесь час» — але жодного кроку «перша програма/блимнути світлодіодом» у курсі перед ним не існує. Також лінкує `programming/memory-mapped-io` і `programming/bootloader` — не введені.
3. **jtag-swd-tools (крок 6)** починається з «зібраний шлях від тексту до прошивки… — лише півділа» і лінкує `programming/flashing`, `programming/bootloader` — а прошивання в курсі з'являється лише кроком 27 (esptool-workflow). Відлагодження подано ДО збирання й заливання прошивки.
4. **dma-adc (крок 8)**: АЦП у курсі не введений ніде (перша згадка — usb-cc-adc-circuit у zhyvlennia мимохідь; стаття `electronics/adc` існує, але не підключена).
5. **dma-spi-i2s (крок 9)**: SPI вводиться лише в наступній секції peryferiia (`spi-vs-i2c`), I2S — ніде в курсі.
6. **super-loop-limits (крок 10)**: сам super-loop у курсі не введено (`programming/super-loop` існує в книзі, не підключений).
7. **duty-cycle-current (крок 13)** спирається на `programming/sleep-modes`, `wakeup-sources`, `current-paths`, `ulp-coprocessor` (лінкує всі чотири) — жодного кроку про режими сну в курсі перед ним нема.
8. **mavlink-commands (крок 16)** лінкує `root:embedded/pymavlink` — це секція zvyazok (13), на шість секцій попереду; також `communications/telemetry-stream`.
9. **autonomous-system (крок 17)** лінкує `root:embedded/proportional-control` (keruvannia, секція 12) і `root:embedded/imu-barometer` (davachi, секція 10).
10. **mission-planning (18) і mission-planner-qgc (26)**: вейпойнти і GCS до того, як курс дав MAVLink, наземну станцію, давачі й керування.
11. **memory-budget-mcu (крок 19)**: розмови про .bss/.data/стек (hist-вставка — про ім'я BSS) без введених лінкування (`programming/linking`) і стека (`programming/stack-lifo`).
12. **power-logger (20) і current-profiler-tools (21)** посилаються на `root:embedded/measure-consumption` (proshyvka, секція 9) як на вже пройдене — «ми вже вміємо», «чому мультиметр бреше — з'ясували». Курс цього ще не проходив.
13. **edge-inference (22)**: ML-інференс без жодної підготовки; увесь його блок-рідня (model-zoo, model-export, on-device-benchmarking, training-data-pipeline) живе в drony (14).
14. **ota-server (25)**: перший рядок — «[Оновлення через ефір](book:programming/ota-update) ми досі дивилися очима пристрою» — але кроку про OTA-оновлення в курсі нема взагалі, а Wi-Fi буде лише в секції 13.
15. **wifi-fast-connect (30)**: кешування PMK/IP — до будь-якого Wi-Fi/802.11/DHCP у курсі (все в zvyazok, секція 13).
16. Міжсекційне (у контексті mk): **komponenty/datasheet-mcu (секція 3)** і **cyfra-pamyat/fpga-vs-mcu (секція 5)** читають даташит МК і порівнюють FPGA з МК до того, як МК узагалі введено (секція 7); **cyfra-pamyat/custom-instruction** вимагає розуміння ISA, яке дає mk/risc-cisc. Усі три природно живуть у mk — забираю move_in.

## 3. Move out (12 тем)

| Тема | Куди | Чому |
|---|---|---|
| dma-adc | peryferiia | АЦП не введений; застосунковий крок «DMA+АЦП» має стояти після кроку про АЦП (там же додати ref:electronics/adc) |
| dma-spi-i2s | peryferiia | SPI вводиться там (spi-vs-i2c), I2S — ніде; крок мусить іти після них |
| mavlink-commands | zvyazok | лінкує pymavlink (zvyazok); місце — одразу після pymavlink |
| autonomous-system | drony | лінкує proportional-control (керування) та imu-barometer (давачі); природне відкриття модуля дронів |
| mission-planning | drony | вейпойнти потребують MAVLink+GCS+навігації; поруч з autonomous-system |
| mission-planner-qgc | drony | порівняння GCS — після знайомства з MAVLink і місіями |
| ota-server | zvyazok | потребує Wi-Fi/мережі; перед ним там додати ref:programming/ota-update (бік пристрою), на який стаття прямо посилається |
| wifi-fast-connect | zvyazok | PMK/roaming/IP — після 802.11-тем (802-11-versions) |
| power-logger | proshyvka | лінкує measure-consumption і duty-cycle-current як пройдені; місце — після measure-consumption. NB: proj-coulomb-counter продубльований в обох темах |
| current-profiler-tools | proshyvka | лінкує measure-consumption та її comp-вставку (comp-current-profiler) як пройдені |
| edge-inference | drony | вступ ML-блоку, решта якого (model-zoo, model-export, benchmarking, training-data) уже в drony |
| fault-injection-testing | proshyvka | методика тестування прошивки; місце поруч із firmware-testing і fmea-embedded |

## 4. Move in (3 теми)

| Тема | Звідки | Чому |
|---|---|---|
| datasheet-mcu | komponenty | читати даташит МК у секції 3 неможливо — МК ще не існує для читача; тут, перед вибором МК, — саме місце |
| fpga-vs-mcu | cyfra-pamyat | порівняння з МК до введення МК; після mk обидва боки порівняння відомі (FPGA — із секції 5) |
| custom-instruction | cyfra-pamyat | вимагає розуміння ISA (дає risc-cisc тут); FPGA-потік уже пройдено раніше |

## 5. Нова структура: 11 розділів (і пропозиція спліту)

Разом із доданими ref-ами модуль виходить на ~70 кроків — це аргумент за **спліт на три модулі** (див. §7), але розділи вже нарізані так, щоб різати по межах розділів.

### Розділ 1. Число, пам'ять, програма (6)
Новачкова рампа: від «чому машина рахує двійкою» до «що таке програма».
1. ref:math/why-binary — ДОДАТИ
2. ref:math/positional-systems — ДОДАТИ
3. ref:programming/bits-bytes-endianness — ДОДАТИ
4. ref:programming/memory-as-array — ДОДАТИ
5. new:what-is-a-program — ДОДАТИ (власна: інструкції, змінні, цикли, умови — мінімум C; без цього «нуль програмування» не пройде далі)
6. ref:programming/integer-types-c — ДОДАТИ

### Розділ 2. Процесор: машина, що виконує код (10)
1. ref:programming/what-is-processor — ДОДАТИ
2. ref:programming/processor-parts — ДОДАТИ
3. ref:programming/fetch-decode-execute — ДОДАТИ
4. ref:programming/isa — ДОДАТИ
5. ref:programming/clock-frequency — ДОДАТИ
6. own:von-neumann-harvard (тепер усі його передумови — пам'ять, шина, цикл виконання — дано)
7. own:risc-cisc
8. ref:programming/pipeline — ДОДАТИ (пояснює, чому RISC переміг; поглиблення)
9. ref:programming/cache — ДОДАТИ (знадобиться для XIP/boot-time далі)
10. own:custom-instruction — move_in із cyfra-pamyat (ISA+FPGA вже відомі)

### Розділ 3. Мікроконтролер: комп'ютер на одному кристалі (7)
1. ref:programming/microcontroller — ДОДАТИ (досі «що таке МК» ніде не сказано!)
2. ref:programming/mcu-blocks — ДОДАТИ
3. ref:programming/flash-vs-ram — ДОДАТИ
4. ref:programming/memory-map — ДОДАТИ
5. own:esp32-vs-8bit
6. own:pic-architecture (поглиблення 8-бітного світу одразу після порівняння)
7. own:esp32-family

### Розділ 4. Перший код на живому залізі (6)
1. new:first-program-blink — ДОДАТИ (власна: середовище, setup()/loop(), digitalWrite, перше заливання; baremetal-vs-framework прямо посилається на «приклади, якими ми вже користуємось» — їх треба створити)
2. ref:programming/memory-mapped-io — ДОДАТИ (baremetal лінкує його двічі)
3. ref:programming/gpio-registers — ДОДАТИ
4. own:baremetal-vs-framework
5. own:hal-ll-registers (та сама драбина абстракцій на прикладі STM32 — одразу після)
6. own:pin-mux (одна ніжка — багато функцій; завершує тему GPIO)

### Розділ 5. Життя програми в часі: цикл, переривання, таймери (9)
1. ref:programming/super-loop — ДОДАТИ (без нього super-loop-limits висить у повітрі)
2. own:polling-vs-interrupts
3. ref:programming/isr — ДОДАТИ (правила写ання обробника)
4. ref:programming/interrupt-priorities — ДОДАТИ
5. ref:programming/timer-counter — ДОДАТИ (таймерів у курсі нема, а PWM у zhyvlennia ними вже користувався)
6. ref:programming/millis-micros — ДОДАТИ
7. ref:programming/nonblocking-time — ДОДАТИ
8. own:super-loop-limits
9. ref:programming/freertos — ДОДАТИ (природний вихід із меж super-loop; RTOS у курсі інакше не з'являється ніде)

### Розділ 6. DMA: дані течуть без процесора (4)
Мотивація — біль «переривання на кожен байт» із розділу 5. Застосунки (АЦП, SPI/I2S) переїхали в peryferiia, тут — сам механізм.
1. ref:programming/dma-problem — ДОДАТИ
2. ref:programming/dma-controller — ДОДАТИ
3. ref:programming/dma-channels — ДОДАТИ
4. ref:programming/double-buffering — ДОДАТИ (пінг-понг буфери — стандартний патерн DMA)

### Розділ 7. Від коду до чипа: збірка, прошивання, завантаження (10)
1. ref:programming/compilation — ДОДАТИ
2. ref:programming/linking — ДОДАТИ (потрібне і memory-budget-mcu: секції .bss/.data)
3. ref:programming/firmware-image — ДОДАТИ
4. ref:programming/flashing — ДОДАТИ
5. own:esptool-workflow
6. ref:programming/bootloader — ДОДАТИ (jtag-swd-tools і baremetal на нього посилаються)
7. ref:programming/reset-causes — ДОДАТИ
8. ref:programming/watchdog — ДОДАТИ (watchdog-reset — одна з причин reset; у курсі watchdog не введений ніде, хоча далі згадується)
9. own:reset-sequence
10. own:boot-time-budget

### Розділ 8. Зазирнути в живий чип: відлагодження (5)
Тепер стоїть ПІСЛЯ збірки/прошивання — як і передбачає перший абзац jtag-swd-tools.
1. own:jtag-swd-tools
2. own:openocd-gdb
3. own:debug-io-comparison
4. ref:programming/hardfault — ДОДАТИ (розбір HardFault — місток до посмертного аналізу)
5. own:core-dump

### Розділ 9. Пам'ять МК: скільки її і куди тече (4)
1. ref:programming/stack-lifo — ДОДАТИ
2. ref:programming/heap-dynamic-memory — ДОДАТИ
3. ref:programming/stack-overflow — ДОДАТИ
4. own:memory-budget-mcu (лінкерні секції з розділу 7 + стек/купа звідси)

### Розділ 10. Енергія: змусити батарею жити довго (6)
Рівно ті чотири book-статті, які duty-cycle-current лінкує в першому ж абзаці, — тепер кроки перед нею.
1. ref:programming/clock-power — ДОДАТИ
2. ref:programming/sleep-modes — ДОДАТИ
3. ref:programming/wakeup-sources — ДОДАТИ
4. ref:programming/current-paths — ДОДАТИ
5. ref:programming/ulp-coprocessor — ДОДАТИ
6. own:duty-cycle-current

### Розділ 11. Вибір мікроконтролера (4)
Фінал модуля: усе знання складається в інженерне рішення.
1. own:datasheet-mcu — move_in із komponenty
2. own:mcu-selection
3. own:mcu-checklist
4. own:fpga-vs-mcu — move_in із cyfra-pamyat (розширення поля вибору: а чи МК узагалі?)

Перевірка повноти: 33 поточні теми − 12 move_out = 21; усі 21 розкладені по розділах (2+3+3+2+2+3+4+1+1 у розділах 2–11… точніше: р.2 — von-neumann-harvard, risc-cisc; р.3 — esp32-vs-8bit, pic-architecture, esp32-family; р.4 — baremetal-vs-framework, hal-ll-registers, pin-mux; р.5 — polling-vs-interrupts, super-loop-limits; р.7 — esptool-workflow, reset-sequence, boot-time-budget; р.8 — jtag-swd-tools, openocd-gdb, debug-io-comparison, core-dump; р.9 — memory-budget-mcu; р.10 — duty-cycle-current; р.11 — mcu-selection, mcu-checklist). Жодної не загублено. + 3 move_in + 43 ref + 2 new.

## 6. Органічність ref/own

- Поточний стан — протилежна крайність від «стіни ref-ів»: **0 ref-ів на 33 own** при готових ~220 book-статтях із того самого матеріалу. Власні статті вже де-факто спираються на book-статті інлайн-лінками (duty-cycle-current — 4 лінки на programming, baremetal — 2, jtag-swd — 3, ota-server — 1) — тобто читач і так мусить їх читати, просто курс не ставить їх кроками. Перетворення цих інлайн-залежностей на кроки-ref-и — механічно обґрунтоване.
- Після правки розділи 1–2 стають ref-важкими (5–7 ref-ів поспіль). Це прийнятно (кожен ref — самодостатній атом драбинкою), але в ідеалі курсу пасувала б одна власна стаття-місток на кшталт «Від вентиля до процесора» замість частини цих ref-ів. Позначив як опцію, не як вимогу.
- Місць, де стоїть ref, а потрібна own-стаття, у модулі нема (ref-ів нема взагалі). Зворотне — є: von-neumann-harvard і risc-cisc як own виправдані (написані кумулятивно, з арками під курс), але вони потребують ref-підкладки, яку я додав.
- Дубль вставок: `proj-coulomb-counter.md` значиться і в mk/power-logger, і в proshyvka/measure-consumption — при переносі power-logger у proshyvka дубль треба звести до одного файлу.

## 7. Модуль як ціле

- **Назва** «Мікроконтролер і процесор» — влучна для ядра (розділи 2–3), але модуль на ~70 кроків завеликий. Пропозиція спліту по межах розділів: **I. «Код і процесор»** (розділи 1–2), **II. «Мікроконтролер зсередини»** (розділи 3–6), **III. «Інструменти розробника: збірка, відлагодження, ресурси»** (розділи 7–11). Мінімальний варіант — два модулі: (1–2) і (3–11).
- **Місце в курсі**: після zhyvlennia (6) — загалом правильне: до МК читач уже знає електрику, компоненти, живлення. Але є натяжки на рівні курсу: cyfra-pamyat (5) згадує МК (fpga-vs-mcu — забрав сюди), komponenty (3) читає даташит МК (забрав сюди), zhyvlennia (6) вже використовує PWM і «сплячі» прошивки (proj-sleep-firmware) до введення МК. Радикальніший варіант — підняти mk ПЕРЕД zhyvlennia — ламає інше (mk потребує понять споживання/живлення). Виваженіше: лишити порядок, але прибрати з ранніх секцій усе МК-специфічне (що я і роблю move_in-ами).
- **RTOS**: у курсі ніде нема введення RTOS (лише spinlock-mutex у proshyvka). Додав ref:programming/freertos як фінал розділу 5; глибший RTOS-блок (задачі, черги, пріоритети — усе є в book/programming) — кандидат у proshyvka, поза межами цього модуля.
- **UART для Serial-монітора**: jtag-swd-tools користується Serial як чорною скринькою — прийнятно; глибокий UART лишається в peryferiia одразу після модуля. Опційно можна додати ref:communications/async-serial перед розділом 8, не наполягаю.
- Порядок нових розділів кумулятивний: число→програма (1) → процесор (2) → МК (3) → перший код (4) → час/переривання (5) → DMA (6) → збірка/boot (7) → відлагодження (8) → пам'ять (9) → енергія (10) → вибір (11). Кожен розділ спирається лише на попередні + секції 1–6 курсу.

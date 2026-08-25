# Лінза «Новачок»: прохід курсу embedded очима читача з нуля

Джерело: `E:/develop/courses/guide/embedded/manifest.js` (14 секцій, 286 тем).
Позиції тем нижче — порядкові номери всередині секції за поточним маніфестом. `ref:` — статті предметних книг, `slug` — власні статті курсу.

## 0. Діагноз одним абзацом

Курс має три системні хвороби. **(а) Перші теми секцій майже всюди вимагають незнаного**: `zhyvlennia` починається з «Вибору топології» до того, як читач бачив хоч один стабілізатор; `zvyazok` — з маршрутизації без жодного слова про мережі; `drony` — з порівняння відеокодеків, хоча «що таке дрон і як він літає» в курсі немає взагалі. **(б) Вертикалі знань розірвані**: компоненти вводяться ПІСЛЯ кіл, які з них складаються; діоди — після стабілітронів; МК — після порівнянь із МК; шини SPI/I2C — після DMA по SPI. **(в) Цілих шарів бази немає**: транзистор, операційний підсилювач, цифрова логіка (біт → вентиль → тригер), вхід у програмування (C, компіляція, тулчейн), АЦП/ЦАП, UART, RTOS, модуляція, мережевий стек, мотори, нейромережі — усе це використовується, але ніде не вводиться. Більшість дір закривається готовими `done`-статтями книг `electronics`, `communications` і особливо `programming` (галузі `computer-architecture` та `embedded-systems`), які курс зараз НЕ референсить жодного разу.

---

## 1. Прохід по секціях: де новачок впирається

### С1. `osnovy` — Основи: заряд, струм, поле, тепло (47 тем)

Єдина секція з майже правильним хребтом (заряд → поле → потенціал → напруга → струм → опір → потужність). Але:

- **#8 `physics/faraday-cage`** — потребує поняття «провідник, у якому заряди вільно перерозподіляються»; провідність з'являється лише з №9 (`electric-current`) і №14 (`ionic-conduction`). Перенести після блоку про струм/провідність або в блок «електростатика в житті» (№38–39, 46).
- **#21 `physics/thermal-resistance`** («Тепловий опір і відведення тепла») — спирається на механізми передачі тепла, а власна стаття **`heat-transfer` стоїть #40**. Поміняти місцями: heat-transfer → joule-heating → thermal-resistance.
- **#36 `physics/capacitive-coupling`, #37 `physics/inductive-coupling`** — ємнісна й індуктивна наводки до того, як введено ємність і індуктивність (конденсатор і котушка — секція 3!). Або перенести після компонентів, або лишити тільки якісний огляд `noise-interference`.
- **#41 `field-and-potential`, #42 `electrostatics-summary`** — це підсумкові «зшивки» блоку №5–8, а стоять після магнетизму й шумів. Підняти впритул до свого блоку (field-and-potential після #7 `voltage`, electrostatics-summary — закрити електростатичний блок перед #9 `electric-current`).
- **#34 `physics/noise-interference` («Шум і завади як фізика») та #43 власна `noise-interference` («Шум і завади»)** — дубль за назвою; читач двічі проходить «шум і завади» з відстанню в 9 тем. Поставити поруч або злити роль (ref — фізика, own — інженерне зведення) і явно розвести назви.
- **#44 `frequency-wavelength`** — логічне продовження #24–25 (`sine-wave`, `amplitude-frequency`); на позиції 44 відірвана від свого блоку.
- **#45 `memory-cell-physics` («Фізика комірок»)** — найгірше місце секції: плаваючий затвор, тунелювання, SRAM noise margin — це потребує транзисторів, цифрової логіки й пам'ятей. Місце цієї теми — у блоці пам'яті (нинішні `nor-vs-nand`/`eeprom-fram`), тобто секції 4–5, а не перша секція курсу.
- **#47 `emf-sources`** — «Типи ЕРС» природно йде одразу за #22 `closed-circuit` («Замкнене коло й джерело ЕРС»), а не в кінці.

### С2. `kola` — Кола й закони (36 тем)

Перша половина (закони) майже правильна, друга половина — аналоговий блок, що висить у повітрі.

- **#2 `voltage-divider`, #3 `current-divider` стоять ДО #8 `series-connection` і #9 `parallel-connection`** — дільник напруги це і є послідовне з'єднання, дільник струму — паралельне. Порядок: series/parallel → дільники.
- **#16 `rc-time-constant`, #17 `rl-time-constant`** — конденсатор і котушка вводяться в секції 3 (`komponenty` #4, #8). Читач рахує сталу часу елемента, якого ще не бачив. Це головний доказ, що секції 2 і 3 треба переплести.
- **#15 `phase-shift`** — зсув фаз «між чим і чим» без реактивних елементів незрозумілий; теж після C і L.
- **#18 `electronics/instrumentation-amp`** — інструментальний підсилювач БЕЗ операційного підсилювача. ОП не вводиться ніде в курсі, хоча в книзі є **`electronics/opamp` («Оппідсилювач»)**. Через це висять і #27 `single-supply-opamp`, #28 `feedback-topologies`, #33 `kcl-opamp-analysis`, #34 `opamp-input-types`.
- **#21 `bjt-load-driving`, #22 `bjt-vs-mosfet`, #24 `darlington-vs-sziklai`, #26 `tail-current-source`, #32 `dc-ac-bias`, #23 `multistage-amplifier`** — весь транзисторний блок без введення транзистора. У книзі готові кандидати: **`electronics/transistor-idea`, `bjt-operation`, `bjt-gain`, `bjt-regions`, `bjt-switch`, `bjt-amplifier`, `mosfet-modes`, `mosfet-switch`**. До того ж `bjt-load-driving` у вставці має `proj-base-drive-firmware` — прошивку в секції 2 з 14.
- **#25 `filter-families`** (Баттерворт/Чебишов/Бесель) — до поняття АЧХ і взагалі «що таке фільтр»; має йти після `cascaded-rc-filters` (#30) і базового RC-фільтра.
- **#29 `impedance-matching-networks`** — імпеданс ніде не введено; кандидати **`electronics/reactance` («Реактивність») і `electronics/impedance` («Імпеданс»)**.
- **#35 `pierce-oscillator-design`** — «розрахунок обв'язки кварцу» до введення кварцового резонатора; кандидати **`electronics/crystal`, `quartz-resonator`, `quartz-rlc-model`**.
- **#20 `reading-schematics`** — навичка читання схем потрібна з першої ж схеми курсу, а стоїть двадцятою. Підняти на самий початок секції кіл; #36 `net-labels-buses` — впритул до неї.

### С3. `komponenty` — Пасивні компоненти (27 тем)

- **Глобально: секція стоїть ПІСЛЯ кіл, які цими компонентами оперують** (див. С2). R → кола з R → C, L → перехідні процеси — природний порядок.
- **#6 `electronics/capacitor-parasitics`** — ESL (паразитна індуктивність) до введення котушки (#8 `inductor-coil`).
- **#14 `zener-schottky`** — стабілітрон і Шотткі до введення звичайного діода: власна стаття `diodes` живе в секції 4 (`napivprovidnyky` #2), тобто ПІСЛЯ. Діод → типи діодів → зенер/Шотткі.
- **#15 `flyback-protection`** — потребує діод (ще нема) і транзисторний ключ (нема ніде).
- **#20 `datasheet-bjt`** — практикум даташита транзистора без транзистора.
- **#21 `datasheet-mcu`** — практикум даташита МІКРОКОНТРОЛЕРА в секції 3, за чотири секції до появи МК (секція 7). Найяскравіший приклад теми не на своєму місці.
- **#22 `surge-protection-cascade`** — каскад GDT/варистор/TVS, жоден із цих приладів не введений (TVS з'явиться аж у `zhyvlennia` #28 `esd-protection-circuits`). Зібрати «захисний» кластер в одному місці пізніше.
- **#17 `ceramic-mems-resonators`, #18 `tcxo-ocxo`** — знову резонатори до кварцу (див. С2 #35).
- **#25 `pcb-thermal-design` стоїть ДО #26 `pcb-assembly-methods`** — тепловідведення на платі до знайомства з платою. Взагалі кроку «що таке друкована плата: шари, доріжки, перехідні отвори» в курсі нема — потрібен місточок перед PCB-темами.

### С4. `napivprovidnyky` — Напівпровідники й діоди (7 тем)

- **#1 `electronics/esd-damage`** — перша тема секції про пошкодження напівпровідників розрядом... до введення напівпровідників. Порядок: `diodes` (де, судячи з назви, вводиться p-n) → типи → esd-damage.
- **#3 `nor-vs-nand`, #4 `eeprom-fram`, #6 `mram-rram-pcm`** — це теми про ПАМ'ЯТІ (флеш, EEPROM), а не про діоди: потребують плаваючого затвора (`memory-cell-physics`, який застряг у С1 #45) і навіть SPI-команд (вставка `comp-w25q-raw-commands` — SPI буде в секції 8). Їх місце — у секції 5 разом із `when-memory-runs-out`/`choosing-memory`.
- **#7 `power-fail-safety`** — brown-out і рятування стану: потребує МК, прошивку, NVS — секції 7/9+. Тут випадкова.
- **Головна дірка секції: транзисторів немає.** Секція «напівпровідники» не містить BJT/MOSFET, хоча ними користуються з секції 2. Сюди просяться ref-и `electronics/transistor-idea`, `bjt-operation`, `bjt-switch`, `mosfet-modes`, `mosfet-switch` + наявні `bjt-vs-mosfet`, `datasheet-bjt`.

### С5. `cyfra-pamyat` — Цифра й пам'ять (11 тем)

- **#1 `electronics/shift-register`** — перша тема «цифри», а самої цифри нема: у курсі НІДЕ не вводяться двійкова система, логічні рівні, вентилі, тригер. Зсувний регістр складається з тригерів, яких читач не бачив. Кандидати-містки: **`programming/bits-bytes-endianness`** (біти/байти), **`electronics/logic-levels-as-ranges`** («Рівні "0" і "1"»), **`electronics/logic-gates-symbols`**, `logic-families`; тригер — треба або book-стаття, або власний крок.
- **#4 `fpga-vs-mcu`** — порівняння з мікроконтролером за дві секції до введення МК (секція 7). Перенести після основ МК.
- **#11 `custom-instruction`** — кастомні інструкції процесора до введення процесора/ISA (это mk #2 `risc-cisc`, а по-хорошому — `programming/isa`). Перенести після МК-модуля.
- **#5 `when-memory-runs-out`, #6 `choosing-memory`** — сюди ж стягнути весь пам'ятевий кластер: `memory-cell-physics` (з С1), `nor-vs-nand`, `eeprom-fram`, `mram-rram-pcm` (з С4). Тоді секція набуває форми: цифрова логіка → програмована логіка (PAL→FPGA) → пам'яті.
- **#8 `communications/transmission-lines`, #9 `signal-integrity`, #10 `ddr-signal-integrity`** — потребують імпеданс (не введений, див. С2 #29). Після введення імпедансу блок стоїть логічно (високошвидкісна цифра — вінець секції).

### С6. `zhyvlennia` — Живлення (29 тем)

- **#1 `topology-map` («Вибір топології»)** — вибір між LDO/buck/boost/flyback до того, як читач бачив хоч один стабілізатор. Вступна за змістом тема **#10 `linear-vs-switching`** має бути першою, і навіть перед нею — ref-и **`electronics/ldo`, `electronics/buck`, `electronics/boost`** (усі є в книзі). Потім `topology-map` як зведення.
- **#25 `power-tree-reading`, #27 `power-budget`** — вступні навички («прочитати дерево живлення», «порахувати бюджет») стоять у хвості секції. Підняти в перші кроки.
- **#2 `usb-power-map`, #3 `pd-sink-design`, #4 `usb-cables-field`, #26 `usb-cc-adc-circuit`, #23 `fast-charging-protocols`** — цілий USB-кластер без введення USB як шини (що таке хост/пристрій, VBUS, ролі). Кандидати: **`programming/usb-overview`** (+ `usb-physical`, `usb-power`), **`communications/usb-device-basics`**. `usb-cc-adc-circuit` додатково потребує АЦП — не введений (див. С7 #8).
- **#9 `board-consumption`, #18 `sleep-current-audit`** — споживання плати з режимами сну МК до введення МК (секція 7) і режимів сну (**`programming/sleep-modes`, `wakeup-sources`** — готові). Перенести за МК-модуль.
- **#21 `loop-gain-measurement`** — вимірювання петлевого підсилення стабілізатора: потребує зворотний зв'язок, запаси стійкості, Боде — це секція 12 (`keruvannia` #11 `loop-stability`). Найдальший «стрибок у майбутнє» в курсі. Перенести після модуля керування.
- **#11 `power-supply-filtering` стоїть ДО #14 `bridge-rectifier-design`** — згладжування пульсацій випрямляча до випрямляча. Поміняти.
- Батарейний кластер (#5 `battery-chemistries`, #15 `bms-architecture`, #16 `active-balancing`, #17 `battery-pack-thermal`, #29 `thermal-runaway-protection`) — сам по собі впорядкований добре, лише розкиданий по секції; зібрати підряд.

### С7. `mk` — Мікроконтролер і процесор (33 теми)

Найперевантаженіша секція: тут і процесор, і відлагодження, і енергетика, і — несподівано — дрони.

- **#1 `von-neumann-harvard`** — перша тема про архітектури пам'яті програм/даних, але «що таке процесор, програма, інструкція» не вводилось ніде. Готові містки в `programming/computer-architecture`: **`what-is-processor`, `processor-parts`, `fetch-decode-execute`, `isa`, `clock-frequency`** (усі basic done). І головне — перед усім цим потрібен модуль входу в програмування (розділ 3 звіту).
- **«Що таке мікроконтролер»** — теж нема (одразу порівняння #3 `esp32-vs-8bit`). Кандидати: **`programming/microcontroller`, `programming/mcu-blocks`, `programming/esp32-architecture`**.
- **GPIO не введений** — а #7 `polling-vs-interrupts`, #24 `pin-mux`, LED-миготіння тощо на ньому стоять. Кандидат: **`programming/gpio-registers`** (+ `memory-mapped-io`).
- **#8 `dma-adc`** — АЦП ніде не введений. Кандидати: **`electronics/adc`, `adc-resolution`, `adc-types`, `adc-quantization`, `electronics/dac`**.
- **#9 `dma-spi-i2s`** — DMA по SPI до введення SPI (секція 8, ПІЗНІШЕ). Периферійні шини мають передувати DMA-темам.
- **#6 `jtag-swd-tools`, #14 `openocd-gdb`, #15 `core-dump`** — відлагодження прошивки до першої прошивки: кроку «перша програма → компіляція → прошивання → запуск» нема. #27 `esptool-workflow` (прошивання) стоїть аж 27-м — а це частина першого циклу розробки. Кандидати: **`programming/flashing`, `bootloader`, `why-debugger`, `toolchain` (pending)**.
- **#16 `mavlink-commands`, #17 `autonomous-system`, #18 `mission-planning`, #26 `mission-planner-qgc`** — чотири дронові теми в секції МК. `autonomous-system` і `mission-planning` — це взагалі кульмінація курсу. Все — у фінальний модуль дронів; MAVLink-кластер при цьому розірваний із `zvyazok` #8–9 (`mavlink-from-ground`, `pymavlink`) — зібрати разом.
- **#22 `edge-inference`** — Edge AI до будь-якої згадки про ML (моделі — секція 14). У ML-кластер дронів.
- **#30 `wifi-fast-connect`** — кешування PMK до введення Wi-Fi (секція 13 #15 `802-11-versions`). Перенести в радіомодуль.
- **#28 `boot-time-budget`, #29 `reset-sequence`** — потребують bootloader і watchdog; **watchdog у курсі відсутній узагалі** (кандидат **`programming/watchdog`**), bootloader — теж (кандидат **`programming/bootloader`**).
- **#25 `ota-server`** — серверна частина OTA без клієнтської: «що таке OTA-оновлення» не введено (кандидати **`programming/ota-update`, `ota-slots`**); плюс потребує мережу/HTTP (секція 13+).
- Дублі вимірювання енергії: #20 `power-logger`, #21 `current-profiler-tools` (mk) проти `proshyvka` #4 `measure-consumption` і `zhyvlennia` #9/#18 — чотири теми про «виміряти споживання» у трьох секціях. Зібрати в один енергетичний розділ.

### С8. `peryferiia` — Периферія й шини (5 тем)

- Секція-огризок з 5 тем, ще й стоїть ПІСЛЯ mk, який уже ганяв DMA по SPI/I2S. Шини — це фундамент роботи з МК, місце — одразу після основ МК і до DMA/давачів/дисплеїв.
- **#2 `communications/rs-485`** — потребує UART, який **не введений ніде** (а на UART стоять і `usb-uart-bridge`, і вся MAVLink-телеметрія). Кандидати: **`communications/uart-frame`, `baud-rate`** (+ `half-duplex-uart`).
- **#3 `spi-vs-i2c`** — порівняння шин до введення кожної окремо. Кандидати: **`communications/spi-bus`, `spi-lines`, `spi-modes`; `i2c-bus`, `i2c-addressing`, `i2c-transaction`**.
- **CAN відсутній повністю** — для курсу з дронами дивно (ESC-телеметрія, автопілоти). Кандидати: **`communications/can-arbitration`, `can-frame-errors`, `dronecan`**.

### С9. `proshyvka` — Прошивка й відлагодження (19 тем)

Секція-мікс: третина — вимірювальні прилади, третина — software engineering, третина — власне прошивка.

- **#1 `electronics/kelvin-shunt`** — перша тема секції «Прошивка» — струмовимірювальний шунт (чиста електроніка вимірювань). Ламаний вхід.
- **#2 `sine-on-scope`** — перше знайомство з осцилографом аж у секції 9, хоча дивитися сигнали треба було ще з секції 2–3. **Мультиметр — базовий інструмент новачка — у курсі відсутній взагалі; логічний аналізатор теж** (при цьому в книзі готові **`electronics/multimeter`, `oscilloscope`, `logic-analyzer`**). Вимірювальний блок (мультиметр → осцилограф → шунт → полювання на заваду) підняти в перші модулі.
- **Немає кроку «перша прошивка / цикл розробки»** — а вже #5 `firmware-testing` (тестування того, чого не було).
- **#6 `error-codes-vs-exceptions`, #14 `solid-principles`, #16 `error-propagation-patterns`, #17 `memory-safety`** — програмістські теми без входу в програмування (SOLID — це взагалі про інтерфейси/ООП). Після модуля програмування.
- **#15 `gitflow-branching`** — стратегії гілкування до введення git (**`programming/version-control`** існує, але статус pending/pending — писати).
- **#18 `spinlock-mutex`** — примітиви синхронізації без задач і планувальника: **RTOS у курсі відсутня повністю** (super-loop-limits закінчується натяком «далі RTOS» — і нічого). Кандидати: **`programming/freertos`, `tasks`, `scheduler`, `task-ipc`, `task-stacks`, `atomicity-races`** (усі basic done).
- **#7 `fatfs-integration`** — без поняття файлової системи і SD (кандидати **`programming/flash-filesystems`, `fat-filesystem`, `microsd`**).
- **#13 `tpm-trustzone`** — апаратний корінь довіри без жодного слова про криптографію/secure boot (кандидат **`programming/secure-boot`**, done).
- **#10 `calibration-procedure`** — процедура калібрування давача ЗА СЕКЦІЮ ДО введення давачів (секція 10). Перенести за давачі, разом із #9 `adc-reference-calibration`.
- **#19 `frequency-measurement-methods`** — input capture без введення таймерів МК (**таймери в курсі не вводяться**; кандидати **`programming/timer-counter`, `capture-compare`, `timer-overflow`**).

### С10. `davachi` — Давачі (10 тем)

- **#1 `electronics/load-cell`** — вхід у секцію без місточка «що таке давач, аналоговий/цифровий, інтерфейси». Сам тензодавач вимогам відповідає (міст Вітстона й ІП були), але вступного кроку бракує.
- **#9 `stereo-vision`** — стереозір до введення камери як сенсора (`isp-pipeline` — секція 14 #10). Камерний блок зібрати в одному місці.
- **#10 `vibration-diagnostics`** — обвідна, спектри, частоти підшипників — це ЦОС із секції 12 (`why-frequency-domain`, FFT). Перенести після модуля сигналів.
- Сюди ж підтягнути `calibration-procedure`/`adc-reference-calibration` з С9 (після введення АЦП).

### С11. `dyspleyi` — Дисплеї (5 тем)

Внутрішній порядок нормальний (класи → вибір → ініціалізація → життєвий цикл → колір); `gram-init-sequence` потребує SPI/I2C і прошивку — за поточного порядку секцій це виконано. Як самостійний модуль замалий — природніше розділом у модулі периферії/взаємодії.

### С12. `keruvannia` — Керування й сигнали (24 теми)

- **Перші чотири теми стоять у зворотному порядку**: #1 `choosing-a-filter` (вибір фільтра) → #2 `fir-vs-iir` (порівняння) → #3 `signal-acquisition` (зчитування сигналу) → #4 `why-frequency-domain` (навіщо частота). Для новачка навпаки: signal-acquisition → why-frequency-domain → choosing-a-filter → fir-vs-iir.
- **Дискретизація/теорема відліків не введена** — а #16 `antialiasing-filter-design` уже проєктує анти-аліасинговий фільтр. Кандидати: **`communications/nyquist-aliasing`, `sampling-reconstruction`** — поставити одразу після `signal-acquisition`.
- **#5 `calculus-for-pid` стоїть перед #6 `open-vs-closed-loop`** — математика похідної/інтеграла до мотивації «навіщо взагалі зворотний зв'язок». Поміняти.
- **PID-кластер розриває фільтровий**: фільтри #1–2, потім PID #5–11, потім знову фільтри #12–14, 16. Згрупувати: сигнали+фільтри підряд, потім керування підряд.
- **#20 `pi-controller-tuning`** відірвана від #8 `integral-control` дванадцятьма темами (між ними SLAM і навігація). До PID-кластера.
- **#23 `kalman-filter` стоїть ПІСЛЯ #17 `inertial-navigation` і #19 `attitude-estimation`**, які на злитті даних і стоять. Калман — перед ними.
- **#18 `slam-navigation`** — дронова тема (лідар+камера+граф поз) — у фінальний модуль.

### С13. `zvyazok` — Зв'язок і радіо (22 теми)

- **#1 `communications/ip-routing`** — перша тема секції — маршрутизація, а «що таке мережа, пакет, IP, TCP/UDP» не вводилось ніде. Мережевий стек треба збирати явно: **`communications/ethernet-frame`, `packet-design`, `tcp-vs-udp`, `programming/sockets-tcp-udp`** → і лише тоді `ip-routing`. Зараз це найламаніший вхід секції в курсі поряд із `drony`.
- **Модуляція не введена** — а #3 `jamming-fhss` (розширення спектра) і половина радіотем на ній стоять. Кандидати: **`communications/modulation`, `am-fm`, `fsk-psk`**.
- **Децибели** — link-budget, підсилення антен, RF-тракт оперують дБ/дБм; окремого кроку нема ніде (перевірити, чи вводить його `link-budget`; якщо ні — потрібен місточок).
- **#17 `propagation-modes`** («Режими поширення радіохвиль» — основи) стоїть ПІСЛЯ #4 `link-budget` і #16 `itu-r-propagation-models`, які на ньому будуються. Підняти перед link-budget.
- **#8 `mavlink-from-ground`, #9 `pymavlink`** — MAVLink розірваний із mk #16 (`mavlink-commands`) і mk #26 (`mission-planner-qgc`); `pymavlink` ще й потребує Python, якого в курсі нема (як і жодної мови). Зібрати кластер у дроновому модулі після UART/мережі.
- **#12 `fpv-video-systems`, #14 `video-streaming-protocols`** — відеотеми до введення кодеків (`mjpeg-vs-h264` — секція 14 #1): відеокластер розірваний між двома секціями. Зібрати: кодеки → FPV-системи → протоколи стрімінгу.
- Антенний блок (#5 `esp32-antenna`, #10 `pcb-antenna-layout`, #22 `rf-frontend`) — без базового «що таке антена» (кандидати **`communications/antenna`, `antennas`, `antenna-gain`**).

### С14. `drony` — Дрони й автономність (11 тем)

- **#1 `mjpeg-vs-h264`** — фінальний модуль курсу про автономні дрони відкривається... порівнянням відеокодеків. А тем **«що таке мультикоптер, як він літає» (тяга, пропелери, чому 4 мотори), «політний контролер», «режими польоту», «arming/failsafe» — у курсі немає взагалі**. У книзі `programming/embedded-systems` готові: **`flight-controller`, `ardupilot-layers`, `params-gcs`, `fc-vs-companion`, `failsafe`** (done) + pending-и `manual-stabilized-modes`, `position-modes`, `arming-checks`, `first-bringup`, `end-to-end-mission`, `capstone-task`.
- **#3 `output-mixing`** (міксер моторів) стоїть ДО #9 `esc-bldc-driver` (регулятор обертів) — і обидва до введення моторів: **DC-мотор/BLDC/крокові в курсі відсутні** (кандидати **`electronics/bldc-motor`, `stepper-motor`, `servo`, `bldc-commutation`**). Порядок: мотори → ESC → серво (#8 `servo-sizing`) → міксер.
- **#4 `model-zoo`** — зоопарк моделей детекції без введення нейромереж: **«що таке нейронна мережа/CNN/інференс» нема ніде** (це стосується і mk #22 `edge-inference`). Потрібен місточок перед усім ML-кластером (#4–7: model-zoo, benchmarking, export, training-data).
- **#10 `isp-pipeline`** — конвеєр обробки зображення без кроку «як працює камерний сенсор». Місточок або book-стаття.
- Фінал курсу зараз — `image-stabilization`; кульмінаційні `autonomous-system` і `mission-planning` застрягли в mk (#17, #18). Логічний фінал: політний стек → MAVLink/наземна станція → місії → автономність → AI → капстоун.

---

## 2. Глобальний порядок: пропозиція структури модулів

### Чому поточний порядок секцій ламається (згори)

1. `kola` (2) використовує C, L, транзистори, ОП — компоненти з (3), напівпровідники з (4), а ОП не вводиться ніде.
2. `komponenty` (3) використовує діоди з (4) і містить МК-даташит із (7).
3. `cyfra-pamyat` (5) порівнює FPGA з МК із (7); пам'яті при цьому наполовину в (4) і (1).
4. `zhyvlennia` (6) використовує сон МК із (7), АЦП (ніде), теорію керування з (12).
5. `mk` (7) використовує шини з (8) і містить дронові теми з (14).
6. `proshyvka` (9) містить прилади, потрібні з (2)–(3), і програмування без входу в нього.
7. `davachi` (10) потрібні для калібрування з (9) і використовують ЦОС із (12).
8. `zvyazok` (13) без мереж і модуляції; `drony` (14) без моторів, польоту й ML-бази.

### Пропонований скелет (модуль → розділи по ~4–10 кроків)

1. **Електрика (фізичний фундамент)** — розділи: «Заряд і поле» (charge → coulomb → field → potential → voltage → field-and-potential) · «Струм і опір» (current → … → resistance-temperature) · «Енергія й тепло» (power → joule → **heat-transfer** → thermal-resistance) · «Джерело й коло» (closed-circuit → **emf-sources**) · «Електростатика в житті» (triboelectricity → air-breakdown → lightning-protection → faraday-cage → electrostatics-summary).
2. **Перші кола й інструменти** — «Схема як мова» (**reading-schematics**, net-labels-buses) · «Резистор» (resistor, marking, potentiometer) · «Закони» (ohms-law → series/parallel → дільники → KCL/KVL → nodes) · «Прилади новачка» (**+electronics/multimeter**, kelvin-shunt) · «Теореми» (superposition, thevenin, norton, power-matching, wheatstone) · circuit-analysis.
3. **Змінний струм, C і L** — «AC» (dc-vs-ac, sine-wave, amplitude-frequency, rms, frequency-wavelength) · «Конденсатор» (capacitor, dielectrics, supercap, RC) · «Котушка» (inductor, types, RL, ferrite, mutual, transformer) · «Фаза й імпеданс» (phase-shift, **+reactance, +impedance**, capacitor-parasitics) · «Перші фільтри» (cascaded-rc-filters, filter-families) · «Магнетизм» (magnetic-field … hall-effect) · «Шум і наводки» (noise-interference, thermal-noise, capacitive/inductive-coupling) · «Осцилограф» (**sine-on-scope**, noise-hunting).
4. **Напівпровідники** — «Діод» (diodes, **+diode-iv-curve, +diode-types**, zener-schottky) · «BJT» (**+transistor-idea, +bjt-operation, +bjt-switch**, bjt-load-driving, datasheet-bjt, darlington-vs-sziklai) · «MOSFET» (**+mosfet-modes, +mosfet-switch**, bjt-vs-mosfet, flyback-protection, inductive-load-switching/clamp) · «Крихкість» (esd-damage, surge-protection-cascade) · «Матеріали» (sic-gan).
5. **Аналогові схеми** — «ОП» (**+electronics/opamp**, kcl-opamp-analysis, single-supply, feedback-topologies, opamp-input-types) · «Підсилювачі» (dc-ac-bias, multistage, tail-current-source, instrumentation-amp, signal-conditioning) · «Генератори й опорні частоти» (**+crystal/quartz-resonator**, pierce-oscillator-design, ceramic-mems, tcxo-ocxo) · impedance-matching-networks.
6. **Практика заліза** — «Даташити» (datasheet-practice) · «Захист і теплo» (fuses-ptc, active-inrush, thermal-budget, energy-density) · «PCB» (місточок «що таке плата» → pcb-assembly-methods → smd-rework → pcb-thermal-design).
7. **Цифрова логіка й пам'ять** — «Біти й вентилі» (**+programming/bits-bytes-endianness, +electronics/logic-levels-as-ranges, +logic-gates-symbols**, місточок «тригер», shift-register, synchronous-reset) · «Програмована логіка» (pal-to-fpga, fpga-flow) · «Пам'яті» (**memory-cell-physics** ← з С1, nor-vs-nand, eeprom-fram, mram-rram-pcm ← з С4, when-memory-runs-out, choosing-memory) · «Швидка цифра» (transmission-lines, signal-integrity, ddr).
8. **Вхід у програмування (НОВИЙ)** — див. розділ 3.
9. **Мікроконтролер** — «Що це» (**+programming/microcontroller, +mcu-blocks, +esp32-architecture**, von-neumann-harvard, risc-cisc, pic-architecture, esp32-vs-8bit, esp32-family, **datasheet-mcu** ← з С3) · «Перша прошивка» (baremetal-vs-framework, hal-ll-registers, esptool-workflow, **+flashing, +bootloader**) · «GPIO й таймери» (**+gpio-registers, +timer-counter, +pwm**, pin-mux, frequency-measurement-methods) · «Переривання» (polling-vs-interrupts, **+interrupts/isr**) · «АЦП» (**+electronics/adc, +dac**, adc-reference-calibration) · «DMA» (dma-adc — після шин: dma-spi-i2s) · «Життєвий цикл» (super-loop-limits, **+watchdog**, reset-sequence, boot-time-budget, memory-budget-mcu) · «Вибір» (mcu-selection, mcu-checklist) · fpga-vs-mcu, custom-instruction (← з С5).
10. **Шини й периферія** — «UART» (**+uart-frame, +baud-rate**, usb-uart-bridge) · «SPI/I2C» (**+spi-bus, +i2c-bus**, spi-vs-i2c, pullup-resistor-design, dma-spi-i2s) · «Диференційні» (differential-pair, rs-485, **+CAN/dronecan**) · «Дисплеї» (5 тем С11) · «Логічний аналізатор» (**+electronics/logic-analyzer**).
11. **Живлення** — «Стабілізатори» (linear-vs-switching → **+ldo/buck/boost** → ldo-post-regulator → topology-map → power-tree-reading → power-budget) · «Мережа й випрямлення» (bridge-rectifier → power-supply-filtering → ac-switch-need → emi-filter) · «USB» (**+usb-overview**, usb-power-map, pd-sink, cables, cc-adc, fast-charging) · «Батареї» (chemistries, bms, balancing, pack-thermal, runaway) · «Захисти» (reverse-polarity, esd-protection-circuits) · «Енергоощадність» (board-consumption, **+sleep-modes**, sleep-current-audit, duty-cycle-current, power-logger/current-profiler/measure-consumption — злити кластер) · «Інженерія» (pwm-power-control, flyback-transformer-design, power-spec-template; loop-gain-measurement — після модуля 13).
12. **Прошивка як інженерія** — «Код» (error-codes, error-propagation, memory-safety, solid, **+version-control**, gitflow) · «RTOS» (**+freertos, +tasks, +scheduler, +task-ipc**, spinlock-mutex) · «Відлагодження» (jtag-swd, openocd-gdb, core-dump, addr2line, debug-io-comparison, fault-injection) · «Зберігання» (**+flash-filesystems**, fatfs, power-fail-safety ← з С4, **+nvs/ota-update**, ota-server) · «Безпека» (**+secure-boot**, tpm-trustzone) · «Надійність» (firmware-testing, fmea) · led-animation-patterns.
13. **Давачі** — місточок «що таке давач» → load-cell → contactless-distance → error-budget-ranging → imu-barometer → barometric-altimeter → imu-mounting → onboard-sensors → lidar → calibration-procedure (← з С9).
14. **Сигнали й керування** — «Сигнал у цифру» (signal-acquisition, **+nyquist-aliasing**, antialiasing-filter-design) · «Частотна область» (why-frequency-domain, tone-detection) · «Фільтри» (choosing-a-filter, fir-vs-iir, filter-specification, fir-design, latency-budget) · «Зворотний зв'язок» (open-vs-closed-loop → calculus-for-pid → P → I → pi-tuning → D → pid-tuning-cascade → loop-stability → lead-lag → loop-gain-measurement ← з С6) · «Оцінювання» (kalman-filter → sensor-fault-detection → attitude-estimation → inertial-navigation → vibration-diagnostics ← з С10) · anc.
15. **Зв'язок і радіо** — «Радіооснови» (місточок дБ, **+modulation/am-fm/fsk-psk**, propagation-modes, link-budget, itu-r) · «Антени» (**+antenna**, esp32-antenna, pcb-antenna-layout, rf-frontend, esp32-module) · «Надійність лінку» (data-reliability, arq, multiple-access, jamming-fhss, frequency-budget) · «Стандарти» (802-11, wifi-fast-connect ← з С7, lpwan, thread-matter-zigbee, nfc-rfid) · «Мережі» (**+ethernet-frame, +tcp-vs-udp, +sockets-tcp-udp**, ip-routing, rpc-embedded).
16. **Дрони й автономність** — «Політ» (місточок «як літає», **+flight-controller/ardupilot-layers/failsafe**) · «Привід» (**+bldc-motor/servo**, esc-bldc-driver, servo-sizing, output-mixing) · «Зв'язок із землею» (mavlink-commands ← з С7, mavlink-from-ground, pymavlink, mission-planner-qgc ← з С7) · «Місії й автономія» (mission-planning ← з С7, autonomous-system ← з С7, slam-navigation ← з С12, where-to-compute) · «Зір» (isp-pipeline, image-stabilization, stereo-vision ← з С10, mjpeg-vs-h264, fpv-video-systems ← з С13, video-streaming-protocols ← з С13) · «AI на борту» (місточок «нейромережі», edge-inference ← з С7, model-zoo, training-data-pipeline, model-export, on-device-benchmarking) · капстоун.

### Місточки, яких бракує на входах модулів (підсумок)

- М4: «звідки береться напівпровідник» (якщо `diodes` не покриває).
- М6: «що таке друкована плата».
- М7: «тригер і регістр» (між вентилями та shift-register).
- М8: весь модуль — місток (розділ 3).
- М9: «що таке мікроконтролер» + «перша прошивка».
- М10: «навіщо шини: як чипи розмовляють».
- М13: «що таке давач».
- М14: «дискретизація й Найквіст».
- М15: «децибели» і «модуляція».
- М16: «як літає мультикоптер», «як працює камера», «що таке нейромережа».

---

## 3. Вхід у програмування: зараз його НЕМАЄ

**Факт**: у курсі жодного кроку про програмування як таке. Перші програмні поняття падають на читача так: `proj-base-drive-firmware` (вставка у `kola` #21, секція 2!), `baremetal-vs-framework` (mk #5 — «фреймворк» без поняття «програма»), `jtag-swd-tools`/`openocd-gdb` (відлагодження неіснуючої прошивки), `solid-principles`/`memory-safety`/`error-codes-vs-exceptions` (`proshyvka`) — без мови C, без компіляції, без поняття змінної. `pymavlink` потребує Python. **Guide не має жодного `ref` на книгу `programming`** — хоча саме там лежить найбільший запас готових статей.

**Де стояти**: окремий модуль «Вхід у програмування» ПІСЛЯ цифрової логіки (біти вже знайомі) і ПЕРЕД модулем «Мікроконтролер» (див. М8 вище). Частина тем (RTOS, git, інженерія коду) — другою порцією в модулі «Прошивка як інженерія».

**Готові статті-кандидати з `book/programming/manifest.js`** (усі перелічені — `basic: done`, якщо не позначено):

*Розділ «Як машина рахує» (галузь `computer-architecture`):*
- `what-is-processor` («Що таке процесор»), `processor-parts`, `fetch-decode-execute` («Цикл виконання»), `isa` («Набір інструкцій»), `clock-frequency`;
- `bits-bytes-endianness`, `ascii-utf8`;
- числа: `integer-types-c` («Цілі типи в C/C++»), `sign-extension`, `overflow-wraparound`, `fixed-point`, `floating-point` (нові v5-статті: також `integer-promotion`, `saturating-arithmetic`, `fpu`, `half-precision` — це вже поглиблення, не в місток);
- поглиблення архітектури на потім (не для входу): `pipeline`, `cache`, `microcode`, `branch-prediction`, `superscalar`, `out-of-order-execution`, `multicore`, `tlb`, `dvfs`, `power-wall`, `ahb-apb-bus`, `bus-arbitration`, `calling-convention`, `cpu-exception-handling`, `control-unit`.

*Розділ «Від коду до прошивки» (галузь `languages` + `systems`):*
- `compilation` («Компіляція»), `compiler-stages`, `linking`;
- `memory-as-array`, `memory-map`, `flash-vs-ram`, `addresses-pointers`, `stack-lifo`, `heap-dynamic-memory`, `stack-overflow`;
- `firmware-image` («Образ прошивки»), `c-runtime`; `volatile` — пізніше, поряд із перериваннями.

*Розділ «Інструменти» (галузь `code` + `embedded-systems`):*
- `version-control` («Контроль версій і git») — **статус pending/pending, треба написати**;
- `toolchain` — **pending**; `debug-vscode`, `why-debugger` — done (для модуля МК).

*Для наступних модулів (галузь `embedded-systems`, усе done)*: `microcontroller`, `mcu-blocks`, `esp32-architecture`, `memory-mapped-io`, `gpio-registers`, `flashing`, `bootloader`, `interrupts`, `isr`, `interrupt-priorities`, `timer-counter`, `timer-overflow`, `capture-compare`, `millis-micros`, `nonblocking-time`, `pwm`, `hardware-pwm`, `watchdog`, `rtc`, `super-loop`, `freertos`, `realtime-determinism`, `sleep-modes`, `wakeup-sources`, `nvs`, `partition-table`, `ota-slots`, `ota-update`, `safe-mode`, `brownout`, `flight-controller`, `ardupilot-layers`, `failsafe` та ін.

**Чого не вистачає навіть у book/programming**: базового «C з нуля» — змінні, типи, функції, умови, цикли, масиви, перша програма. У галузі `languages` є компіляція/лінкування/volatile, але немає синтаксичного входу в мову (грепи по `c-basics|variables|functions|loops|hello` — порожньо). Це кумулятивна навчальна матерія — за залізним правилом репо їй місце у **власних статтях курсу** (3–5 кроків типу `guide/embedded/prohramuvannia/c-first-steps`, `c-control-flow`, `c-functions-arrays`), а не в book. Python для `pymavlink` — або один власний крок-місток «Python для наземних скриптів», або переписати крок так, щоб не припускав знання Python.

---

## 4. Топ-10 виправлень за впливом на новачка

1. **Створити модуль «Вхід у програмування»** (М8) перед МК: ~12–15 ref-ів з `programming` + 3–5 власних кроків «C з нуля»; дописати `version-control`, `toolchain` (обидва pending у book).
2. **Ввести транзистор і ОП** (ref-и `electronics/transistor-idea`, `bjt-operation`, `bjt-switch`, `mosfet-modes`, `opamp`) перед усім аналоговим блоком нинішньої `kola`.
3. **Переплести `kola`+`komponenty`+`napivprovidnyky`**: R → закони → C/L → RC/RL/фаза → діоди → зенер/Шотткі; `datasheet-mcu` — у модуль МК.
4. **Цифрова логіка перед `shift-register`**: біти → рівні → вентилі → тригер; пам'ятевий кластер зібрати в одному модулі (зокрема забрати `memory-cell-physics` з `osnovy`).
5. **Витягти з `mk` чужі теми**: mavlink-commands, autonomous-system, mission-planning, mission-planner-qgc, edge-inference, wifi-fast-connect — у модулі 15–16; шини (М10) — перед DMA.
6. **Полагодити входи секцій**: `linear-vs-switching` перед `topology-map`; `signal-acquisition` перед `choosing-a-filter`; мережевий стек перед `ip-routing`; «як літає дрон» перед усім модулем 16; місток «що таке давач» перед `load-cell`.
7. **Прилади на початок**: мультиметр (нема — ref `electronics/multimeter`), осцилограф (`sine-on-scope`) — у модулі 2–3, а не в секції 9.
8. **RTOS-кластер** (`freertos`, `tasks`, `scheduler`, `task-ipc`) перед `spinlock-mutex`; watchdog/bootloader — перед reset/boot-темами.
9. **Радіо-база**: модуляція + дБ + `propagation-modes` перед `link-budget`/`jamming-fhss`; АЦП/ЦАП (ref-и electronics) перед `dma-adc`/`usb-cc-adc-circuit`/`signal-acquisition`.
10. **Мотори й ML-місток у дронах**: bldc/servo (ref-и electronics) перед `esc-bldc-driver`/`output-mixing`; крок «що таке нейромережа» перед `model-zoo`/`edge-inference`; `kalman-filter` перед `attitude-estimation`/`inertial-navigation`.

Дрібніше, але варте уваги: дубль `noise-interference` (ref+own) в `osnovy`; чотири теми про вимірювання споживання в трьох секціях (`power-logger`, `current-profiler-tools`, `measure-consumption`, `sleep-current-audit`) — звести в один розділ; `pcb-antenna-layout`/`esp32-module`/`pcb-thermal-design` натякають, що курсу бракує маленького PCB-розділу; CAN/DroneCAN відсутні (є готові статті в `communications`).

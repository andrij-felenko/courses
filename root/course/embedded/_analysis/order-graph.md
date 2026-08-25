# Граф залежностей між секціями курсу «embedded» (рівень модулів)

Джерело: `E:/develop/courses/guide/embedded/manifest.js` (прочитано повністю, 335 рядків).
Чинний порядок 14 секцій (індекс = позиція в маніфесті):

| # | slug | назва | тем |
|---|------|-------|-----|
| 1 | osnovy | Основи: заряд, струм, поле, тепло | 47 |
| 2 | kola | Кола й закони | 36 |
| 3 | komponenty | Пасивні компоненти | 28 |
| 4 | napivprovidnyky | Напівпровідники й діоди | 7 |
| 5 | cyfra-pamyat | Цифра й памʼять | 11 |
| 6 | zhyvlennia | Живлення | 29 |
| 7 | mk | Мікроконтролер і процесор | 34 |
| 8 | peryferiia | Периферія й шини | 5 |
| 9 | proshyvka | Прошивка й відлагодження | 19 |
| 10 | davachi | Давачі | 10 |
| 11 | dyspleyi | Дисплеї | 5 |
| 12 | keruvannia | Керування й сигнали | 24 |
| 13 | zvyazok | Звʼязок і радіо | 22 |
| 14 | drony | Дрони й автономність | 11 |

Ребро **X→Y** = «Y потребує знань із X». Кожне ребро — зі свідченням (тема Y ← тема X).

---

## 1. Прямі ребра (узгоджені з чинним порядком)

- **osnovy→kola**: `ref:electronics/ohms-law` ← `ref:physics/voltage`, `ref:physics/electric-current`, `ref:physics/resistance`.
- **osnovy→komponenty**: `ref:electronics/inductor-coil` ← `ref:physics/electromagnetic-induction`; `ref:electronics/capacitor` ← `ref:physics/electric-field`; `own:fuses-ptc` ← `ref:physics/joule-heating`.
- **osnovy→napivprovidnyky**: `own:diodes` ← `ref:physics/resistance-origin` (провідність/носії); `ref:electronics/esd-damage` ← `ref:physics/triboelectricity`, `ref:physics/air-breakdown`.
- **osnovy→cyfra-pamyat**: `own:signal-integrity` ← `own:frequency-wavelength`, `ref:physics/signal-speed`.
- **osnovy→proshyvka**: `own:noise-hunting` ← `own:noise-interference`, `ref:physics/capacitive-coupling`.
- **osnovy→zvyazok**: `own:link-budget`, `own:propagation-modes` ← `own:frequency-wavelength`.
- **kola→komponenty**: `ref:electronics/capacitor-parasitics` ← `ref:electronics/phase-shift`; `own:active-inrush-limiter` ← `ref:electronics/rc-time-constant`, `own:bjt-vs-mosfet`.
- **kola→napivprovidnyky**: `own:diodes` (аналіз лінії навантаження) ← `ref:electronics/ohms-law`, `ref:electronics/kvl`.
- **kola→zhyvlennia**: `own:ldo-post-regulator` ← `own:feedback-topologies`; `own:usb-cc-adc-circuit` ← `ref:electronics/voltage-divider`.
- **kola→davachi**: `ref:electronics/load-cell` ← `ref:electronics/wheatstone-bridge`, `ref:electronics/instrumentation-amp`.
- **kola→zvyazok**: `own:esp32-antenna` (math-pi-matching) ← `own:impedance-matching-networks`.
- **kola→keruvannia**: `own:choosing-a-filter` ← `own:filter-families`, `own:cascaded-rc-filters`.
- **komponenty→zhyvlennia**: `own:flyback-transformer-design` ← `ref:electronics/transformer`; `own:emi-filter-design` ← `ref:electronics/ferrite-bead`.
- **komponenty→peryferiia**: `own:pullup-resistor-design` (math-rise-time) ← `ref:electronics/resistor`, `ref:electronics/capacitor`.
- **napivprovidnyky→cyfra-pamyat**: `own:choosing-memory` ← `own:nor-vs-nand`, `own:eeprom-fram`, `own:mram-rram-pcm`.
- **napivprovidnyky→zhyvlennia**: `own:bridge-rectifier-design` ← `own:diodes`.
- **cyfra-pamyat→mk**: `own:memory-budget-mcu` ← `own:when-memory-runs-out`, `own:choosing-memory`; `own:esptool-workflow` (читання Flash) ← `own:nor-vs-nand` (через napivprovidnyky) + `own:choosing-memory`.
- **zhyvlennia→mk**: `own:duty-cycle-current` ← `own:board-consumption`; `own:power-logger` ← `own:sleep-current-audit` (концепт струму спокою).
- **zhyvlennia→drony**: `own:esc-bldc-driver` ← `own:pwm-power-control`; батарейний блок ← `own:bms-architecture`, `own:battery-pack-thermal`.
- **mk→peryferiia**: `own:spi-vs-i2c` (proj-bus-abstraction, хост = МК) ← `own:polling-vs-interrupts`, `own:pin-mux`.
- **mk→proshyvka**: `own:addr2line-workflow` ← `own:core-dump`, `own:openocd-gdb`; `own:firmware-testing` ← `own:baremetal-vs-framework`.
- **mk→dyspleyi**: `own:gram-init-sequence` ← `own:dma-spi-i2s` (SPI-дисплей, comp-spi-display).
- **mk→zvyazok**: `own:esp32-module` ← `own:esp32-family`; `own:pymavlink` ← `own:mavlink-commands`.
- **mk→drony**: `own:model-zoo`, `own:on-device-benchmarking`, `own:model-export` ← `own:edge-inference`.
- **peryferiia→davachi**: `own:imu-barometer`, `own:onboard-sensors` (шини датчиків) ← `own:spi-vs-i2c`.
- **peryferiia→dyspleyi**: `own:display-selection`, `own:gram-init-sequence` ← `own:spi-vs-i2c`.
- **proshyvka→davachi**: `own:contactless-distance` (proj-echo-picking), `own:error-budget-ranging` ← `own:sine-on-scope`, `own:measure-consumption` (навички вимірювань).
- **davachi→keruvannia**: `own:signal-acquisition` ← `ref:electronics/load-cell`; `own:attitude-estimation`, `own:inertial-navigation`, `own:kalman-filter` ← `own:imu-barometer`; `own:slam-navigation` ← `own:lidar-architecture`, `own:stereo-vision`.
- **keruvannia→drony**: `own:output-mixing` ← `own:pid-tuning-cascade`; `own:image-stabilization` ← `own:attitude-estimation`.
- **zvyazok→drony**: `own:where-to-compute` (край/земля) ← `own:link-budget`, `own:arq-strategies`.

## 2. ЗВОРОТНІ ребра (секція стоїть раніше за ту, від якої залежить) — зламані місця

1. **napivprovidnyky(4)→osnovy(1)**: `own:memory-cell-physics` (Фізика комірок: плаваючий затвор, SRAM-margin) вимагає розуміння транзистора/MOSFET — вводяться лише в `own:diodes`(4) і `own:bjt-vs-mosfet`(2). Тема фізики флеш-комірки стоїть у модулі 1, де читач ще не бачив жодного напівпровідника.
2. **komponenty(3)→kola(2)**: `ref:electronics/rc-time-constant`, `ref:electronics/rl-time-constant`, `own:cascaded-rc-filters`, `own:filter-families`, `own:pierce-oscillator-design` вимагають `ref:electronics/capacitor`, `ref:electronics/inductor-coil`, `own:ceramic-mems-resonators` (кварц/резонатори) — усе це у секції 3, ПІСЛЯ кола.
3. **napivprovidnyky(4)→kola(2)**: `own:bjt-load-driving`, `own:bjt-vs-mosfet`, `own:darlington-vs-sziklai`, `own:opamp-input-types` (типи входів BJT/JFET/CMOS) вимагають PN-перехід/діод — `own:diodes`(4). Половина секції «Кола» — транзисторно-ОП-схемотехніка без уведених напівпровідників.
4. **napivprovidnyky(4)→komponenty(3)**: `own:zener-schottky` (зворотний пробій, бар'єр Шотткі) і `own:flyback-protection` (зворотний діод) ← `own:diodes`.
5. **zhyvlennia(6)→komponenty(3)**: `own:energy-density-comparison` («конденсатор, суперконденсатор, акумулятор») ← `own:battery-chemistries`(6) — порівняння з акумулятором до того, як акумулятори пояснені.
6. **mk(7)→komponenty(3)**: `own:datasheet-mcu` (Практикум даташитів: мікроконтролер) ← `own:mcu-selection`, `own:von-neumann-harvard` — читання даташита МК за 4 модулі до того, як пояснено, що таке МК.
7. **mk(7)→cyfra-pamyat(5)**: `own:fpga-vs-mcu` («FPGA чи МК») і `own:custom-instruction` (кастомні інструкції, proj-riscv-custom) ← `own:risc-cisc`, `own:von-neumann-harvard`.
8. **mk(7)→zhyvlennia(6)**: `own:usb-cc-adc-circuit` («АЦП, фільтрація, гістерезис»), `own:sleep-current-audit` (режими сну, proj-sleep-audit-firmware), `own:pd-sink-design` (state machine у прошивці), `own:pwm-power-control` (таймери/PWM МК) ← `own:dma-adc`, `own:duty-cycle-current`, `own:baremetal-vs-framework`.
9. **keruvannia(12)→zhyvlennia(6)**: `own:loop-gain-measurement` (петлеве підсилення, запас фази, Middlebrook) ← `own:loop-stability` (Найквіст/Боде, запаси) — вимірювати запас стійкості вчать за 6 модулів до поняття запасу стійкості.
10. **peryferiia(8)→mk(7)**: `own:dma-spi-i2s` ← `own:spi-vs-i2c`(8); `own:jtag-swd-tools` («Serial…») ← `own:usb-uart-bridge`(8)/UART. DMA по шині до самої шини.
11. **proshyvka(9)→mk(7)**: `own:power-logger` (comp-current-sense-adc — вимір струму шунтом) ← `ref:electronics/kelvin-shunt`(9). Також дубль-площина: `own:current-profiler-tools`(7) ≈ `own:measure-consumption`(9).
12. **keruvannia(12)→mk(7)**: `own:autonomous-system` (math-loop-stability, proj-control-loop) ← `own:open-vs-closed-loop`, `own:pid-tuning-cascade`, `own:loop-stability`. Автопілот із контурами керування — за 5 модулів до ПІД.
13. **davachi(10)→mk(7)**: `own:autonomous-system`, `own:mission-planning` ← `own:onboard-sensors` (GPS), `own:imu-barometer` — автономний політ до давачів апарата.
14. **zvyazok(13)→mk(7)**: `own:wifi-fast-connect` (PMK-кешування) ← `own:802-11-versions`; `own:ota-server` ← `ref:communications/ip-routing`, `own:data-reliability`; `own:mavlink-commands` ← `own:mavlink-from-ground` (лінк із землею взагалі).
15. **keruvannia(12)→proshyvka(9)**: `own:adc-reference-calibration` ← `own:signal-acquisition` (тракт зчитування, sample-hold); корінь — відсутня тема «основи АЦП» узагалі (див. діри).
16. **davachi(10)→proshyvka(9)**: `own:calibration-procedure` («калібрування давача», math-point-placement) ← самих давачів (`ref:electronics/load-cell`, `own:imu-barometer`) ще не було.
17. **keruvannia(12)→davachi(10)**: `own:vibration-diagnostics` (math-bearing-frequencies, proj-envelope-analysis — спектральний аналіз) ← `own:why-frequency-domain`, `own:fir-vs-iir`.
18. **drony(14)→zvyazok(13)**: `own:fpv-video-systems` (аналог vs DJI O3/HDZero) і `own:video-streaming-protocols` (RTP/WebRTC/SRT) ← `own:mjpeg-vs-h264` (що таке кодек) — стрімінг H.264 до пояснення H.264.

## 3. Цикли взаємних залежностей

- **A. kola ↔ komponenty**: kola потребує C/L/кварц (ребро №2), komponenty потребує законів кіл (`ref:electronics/capacitor-parasitics` ← `ref:electronics/phase-shift`; `own:active-inrush-limiter` ← `ref:electronics/rc-time-constant`). **Розрив:** перенести `ref:electronics/rc-time-constant`, `ref:electronics/rl-time-constant`, `ref:electronics/phase-shift`, `own:cascaded-rc-filters`, `own:filter-families`, `own:pierce-oscillator-design` з kola ПІСЛЯ komponenty (хвіст komponenty або окремий блок «RC/RL і фільтри»).
- **B. kola ↔ napivprovidnyky**: `own:diodes` ← Ом/КВЛ (kola), а транзисторні теми kola ← `own:diodes` (ребро №3). **Розрив:** ядро napivprovidnyky (`ref:electronics/esd-damage`, `own:diodes`, `own:sic-gan-comparison`) поставити одразу після DC-законів kola; транзисторно-ОП-блок kola (`own:bjt-load-driving` … `own:opamp-input-types`, `own:multistage-amplifier`, `own:feedback-topologies`, `own:single-supply-opamp`, `own:kcl-opamp-analysis`) винести в окремий блок «Аналогова схемотехніка» після діодів.
- **C. cyfra-pamyat ↔ mk**: №7 проти прямого `own:memory-budget-mcu` ← `own:choosing-memory`. **Розрив:** перенести `own:fpga-vs-mcu` і `own:custom-instruction` у кінець mk (або окремий FPGA-хвіст після mk); пам'ять лишити до mk.
- **D. zhyvlennia ↔ mk**: №8 проти прямого `own:duty-cycle-current` ← `own:board-consumption`. **Розрив:** MCU-залежні теми живлення (`own:usb-cc-adc-circuit`, `own:sleep-current-audit`, `own:pd-sink-design`) перенести після mk («Живлення розумного пристрою»); аналогове ядро живлення лишити до mk.
- **E. mk ↔ peryferiia**: №10 проти `own:spi-vs-i2c` ← основи МК. **Розрив:** перенести `own:dma-adc`, `own:dma-spi-i2s` з mk у peryferiia (після `own:spi-vs-i2c`), peryferiia лишити одразу після mk.
- **F. mk ↔ proshyvka**: №11 проти `own:addr2line-workflow` ← `own:core-dump`. **Розрив:** `ref:electronics/kelvin-shunt` перенести в komponenty (це пасивний компонент-вимірювач); `own:power-logger`, `own:current-profiler-tools` — у proshyvka поряд з `own:measure-consumption` (заодно прибрати дубль).
- **G. mk ↔ zvyazok**: №14 проти `own:esp32-module` ← `own:esp32-family`, `own:pymavlink` ← `own:mavlink-commands`. **Розрив:** винести з mk увесь автономно-мережевий кластер — `own:mavlink-commands`, `own:autonomous-system`, `own:mission-planning`, `own:mission-planner-qgc`, `own:ota-server`, `own:wifi-fast-connect` — у нову секцію «Автономність і телеметрія» після zvyazok (або в drony). Це водночас лікує ребра №12–14.
- **H. davachi ↔ keruvannia**: №17 проти `own:attitude-estimation` ← `own:imu-barometer`. **Розрив:** `own:vibration-diagnostics` перенести в keruvannia (застосування спектрального аналізу) або після нього.
- **I. davachi ↔ proshyvka**: №16 проти навичок вимірювань для давачів. **Розрив:** `own:calibration-procedure` перенести в davachi (після `own:error-budget-ranging`).

**Діагноз-ядро:** mk бере участь у 5 циклах (C–G), бо секція на 34 теми змішує 4 домени: архітектура/отладка (своє), живлення-профілювання (proshyvka/zhyvlennia), мережа (zvyazok), автономність/дрони (drony). Другий вузол — kola, що містить транзисторно-ОП-схемотехніку до напівпровідників.

## 4. Топологічно коректний порядок

Ключовий факт: **порядок самих 14 секцій майже валідний** — усі 18 зворотних ребер породжені неправильно приписаними ТЕМАМИ, а не порядком блоків. Свопи секцій без переносу тем циклів не лікують.

**Варіант 1 — мінімальний (лишити чинний порядок 1–14, перенести ~17 тем):** переноси з §3 (A–I) + `own:memory-cell-physics` → napivprovidnyky, `own:datasheet-mcu` → mk, `own:energy-density-comparison` → zhyvlennia, `own:fpv-video-systems`+`own:video-streaming-protocols` → drony. Після цього чинний порядок секцій стає топологічно коректним.

**Варіант 2 — рекомендований для новачка (переноси + 2 нові блоки):**
1. osnovy → 2. kola (DC-закони) → 3. komponenty → 4. napivprovidnyky (+аналоговий блок BJT/ОП із kola) → 5. zhyvlennia (аналогове ядро) → 6. **new:цифрові-основи** (біти, вентилі, тригери) + cyfra-pamyat (пам'ять; FPGA-хвіст після mk) → 7. **new:програмування-C** → 8. mk (очищений) → 9. peryferiia (+DMA) → 10. proshyvka (+RTOS-тема) → 11. davachi (+calibration) → 12. dyspleyi → 13. keruvannia (+vibration) → 14. zvyazok (+wifi/ota) → 15. drony (+мотори, MAVLink/автономність, відео).
Найкращий для новачка: «нуль програмування» отримує C і двійкову логіку ДО прошивки; вся автономність — фінал, куди сходяться керування+зв'язок+давачі.

**Варіант 3 — якщо нових секцій не можна:** чинний порядок, але dyspleyi посунути після davachi (11↔10 нейтрально), cyfra-pamyat — після zhyvlennia (5↔6 нейтрально, ближче до mk). Виграш мінімальний; головне однаково — переноси тем.

## 5. Діри покриття домену (цілі області), з пріоритетами

1. **КРИТИЧНО — Програмування (C для МК)**: аудиторія «нуль програмування», але `own:baremetal-vs-framework`(7), `own:error-codes-vs-exceptions`(9), `own:solid-principles`(9), `own:memory-safety`(9) припускають володіння C/C++. Потрібен блок: new:c-variables-types, new:functions-stack, new:pointers-memory, new:bit-operations, new:compile-link-flash.
2. **КРИТИЧНО — Двійкова система й цифрова логіка**: перед cyfra-pamyat/mk немає бітів, вентилів, тригерів; `ref:electronics/shift-register` і `own:pal-to-fpga` висять без бази. new:binary-numbers, new:logic-gates, new:flip-flops-registers.
3. **ВИСОКО — Основи АЦП/ЦАП** (дискретизація, розрядність, квантування, опора): перші вживання — `own:dma-adc`(7), `own:usb-cc-adc-circuit`(6), `own:adc-reference-calibration`(9) — усі «з розгону». new:adc-dac-basics (перед mk).
4. **ВИСОКО — Електродвигуни й актуатори**: курс веде до дронів, але немає жодної теми про мотор; `own:esc-bldc-driver`(14) і `own:servo-sizing`(14) припускають BLDC/серво. new:dc-motor, new:bldc-commutation, new:stepper-servo (після zhyvlennia).
5. **ВИСОКО — RTOS/багатозадачність**: `own:spinlock-mutex`(9) про примітиви синхронізації без задач/планувальника; `own:super-loop-limits`(7) обіцяє продовження, якого нема. new:rtos-tasks-scheduler, new:queues-semaphores.
6. **ВИСОКО — Основи операційного підсилювача**: жоден крок не вводить ОП, а `ref:electronics/instrumentation-amp`(2), `own:kcl-opamp-analysis`(2), `own:single-supply-opamp`(2), `own:signal-acquisition`(12) на ньому стоять. ref:electronics/opamp (чи new:opamp-basics) перед ними.
7. **СЕРЕДНЬО — UART і USB-дані**: `own:usb-uart-bridge`(8) і `ref:communications/rs-485`(8) без тем про UART-кадр/бодрейт і USB-енумерацію/CDC. new:uart-basics, new:usb-data-basics.
8. **СЕРЕДНЬО — Криптографія для embedded** (хеш, підпис, TLS): `own:tpm-trustzone`(9) перевіряє підписи, `own:ota-server`(7) підписує образи — без бази. new:crypto-basics-embedded (перед tpm/ota).
9. **СЕРЕДНЬО — PCB-проєктування як цілісний блок**: розкидано (`own:pcb-thermal-design`(3), `own:pcb-assembly-methods`(3), `own:pcb-antenna-layout`(13), `ref:communications/transmission-lines`(5)); немає grounding/shielding/EMC-компонування. new:pcb-design-flow, new:grounding-shielding.
10. **СЕРЕДНЬО — Камера/сенсор зображення**: `own:stereo-vision`(10) і `own:isp-pipeline`(14) без теми «як працює камера». new:image-sensor-basics (davachi).
11. **НИЗЬКО — Польова механіка дрона**: тяга/пропелери/рама, failsafe-регламенти — drony фактично «відео+ML», політ як система лишається в `own:autonomous-system`(7). new:multicopter-flight-basics.

## 6. Дрібніші дублі, помічені між секціями (для перевірки секційними агентами)

- `own:current-profiler-tools`(7) ≈ `own:measure-consumption`(9) + `own:power-logger`(7) — три теми про вимір споживання у двох секціях.
- `hist-mavlink-origin`(7, mavlink-commands) ≈ `hist-mavlink-birth`(13, mavlink-from-ground) — два історичні нариси про походження MAVLink.
- `own:sleep-current-audit`(6) ≈ `own:duty-cycle-current`(7) ≈ `own:board-consumption`(6) — площина «середній струм/сон» розмазана.
- `own:esd-protection-circuits`(6) проти `ref:electronics/esd-damage`(4) і `own:surge-protection-cascade`(3) — захисна тематика в трьох місцях без наскрізного порядку.

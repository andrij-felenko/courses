# Курс «Вбудована електроніка й автономні системи» — аналіз рівня модулів

Метод: розділ 1 (ідеал) спроєктовано ДО читання маніфесту, з власної експертизи; розділи 2–3 — після повного читання `guide/embedded/manifest.js`.

---

## 1. ІДЕАЛ З НУЛЯ: 24 модулі від заряду до автономного дрона

Позначення: M# — модуль; «залежить» — які попередні модулі мусять бути пройдені.

| # | Модуль | Зміст (один рядок) | Залежить від |
|---|--------|--------------------|--------------|
| M1 | Фізика електрики | Заряд, струм, напруга, опір, енергія/потужність, закон Ома — що таке електрика фізично | — |
| M2 | Кола постійного струму | Послідовно/паралельно, закони Кірхгофа, подільник напруги, джерела, «земля», вимірювання мультиметром | M1 |
| M3 | Пасивні компоненти і практика монтажу | R, C, L як реальні деталі, перехідні процеси RC/RL, читання схем, макетка, паяння, інструменти | M2 |
| M4 | Змінний струм і сигнали | Синусоїда, частота/амплітуда/фаза, імпеданс, RC-фільтри НЧ/ВЧ, інтуїція спектра | M3 |
| M5 | Напівпровідники | p-n перехід, діоди, світлодіоди, BJT/MOSFET як ключ, інтуїція підсилення | M3 (M4 частк.) |
| M6 | Цифрова логіка | Біти, двійкова/шістнадцяткова, доповняльний код, булева алгебра, вентилі, тригери, регістри, лічильники | M5 |
| M7 | Від логіки до комп'ютера | Пам'ять, шини, АЛП, керуючий автомат, фон Нейман, такт, цикл виконання інструкції, машинний код | M6 |
| M8 | Основи програмування (C) | Змінні, типи, розгалуження/цикли, функції, масиви, вказівники, модель пам'яті, тулчейн компіляції | M7 (можна частково паралельно) |
| M9 | Мікроконтролер зсередини | MCU = CPU+Flash+RAM+периферія, регістри, memory map, GPIO, тактування, датасіт; перший blink, прошивання, налагодження | M7, M8 |
| M10 | Таймери, переривання, PWM | Полінг vs переривання, ISR, таймери/лічильники, генерація PWM, watchdog | M9 |
| M11 | Аналоговий інтерфейс | Дискретизація, квантування, ADC/DAC, операційні підсилювачі й кондиціювання сигналу, читання аналогових сенсорів | M5, M10 |
| M12 | Послідовні протоколи | UART, SPI, I2C: кадри, швидкість, адресація; підключення модулів; USB-інтуїція | M9, M10 |
| M13 | Живлення вбудованих систем | Батареї (LiPo!), лінійні vs імпульсні стабілізатори, розв'язувальні конденсатори, бюджет енергії, режими сну, brownout | M3, M5 (практично після M9) |
| M14 | Архітектура вбудованого ПЗ | Суперцикл vs подієва модель, стейт-машини, неблокуючий код, шари драйвер/HAL, volatile, ISR-safe патерни | M10, M12 |
| M15 | RTOS | Задачі, планувальник, витіснення, черги/семафори/м'ютекси, пріоритети та інверсія; FreeRTOS практично | M14 |
| M16 | Сенсори й актуатори поглиблено | IMU (акс/гіро/магн), барометр, GPS, дальноміри, енкодери; мотори DC/BLDC/серво/крокові, H-міст, ESC | M11, M12, M10 |
| M17 | Обробка сигналів і фільтрація | Шум, ковзне середнє, інтуїція IIR/FIR, калібрування сенсорів, комплементарний фільтр | M11, M16 |
| M18 | Теорія керування | Відкритий/закритий контур, зворотний зв'язок, PID практично з тюнінгом, інтуїція стійкості, каскадні контури | M17 |
| M19 | Бездротовий зв'язок | Основи RF, Wi-Fi, BLE, ISM-радіо, MQTT/HTTP для IoT, RC-лінки (PPM/SBUS/CRSF), інтуїція антен | M12, M14 |
| M20 | Оцінка стану і злиття сенсорів | Системи координат, Ейлер/кватерніони, AHRS, фільтр Калмана/EKF, злиття GPS+IMU | M17, M18 |
| M21 | Платформа дрона: рама і пропульсія | Аеродинаміка пропелера, тяга, динаміка квадрокоптера, ESC-протоколи (DShot), підбір моторів/батареї, збирання рами | M13, M16, M18 |
| M22 | Політний контролер | Контури rate/attitude, польотні режими, arming/failsafe, Betaflight/ArduPilot/PX4, тюнінг PID у польоті | M18, M20, M21 |
| M23 | Автономність і навігація | Waypoint-місії, планування шляху, уникнення перешкод, MAVLink, companion computer, інтро в CV/SLAM | M20, M22, M19 |
| M24 | Інтеграція, надійність, безпека + капстоун | EMI/EMC, джгути/роз'єми, інтро в PCB, телеметрія/логування, відмовостійкість, регуляції дронів; капстоун — автономний дрон | усі |

Наскрізна нитка (не окремий модуль, а вставки): математика — тригонометрія й вектори перед M16–M20, комплексні числа перед M4, лінійна алгебра перед M20.

Ключові інваріанти залежностей ідеалу:
- I1: PWM (M10) і ADC (M11) — ДО моторів і сенсорів (M16).
- I2: PID (M18) — ДО польотного контролера (M22); фільтрація (M17) — ДО PID-тюнінгу на реальних сенсорах.
- I3: Кватерніони/EKF (M20) — ДО автономності (M23).
- I4: C і модель пам'яті (M8) — ДО будь-якого firmware (M9+).
- I5: Живлення (M13) — ДО збирання дрона (M21), бо LiPo небезпечні.
- I6: Логіка (M6) → комп'ютер (M7) → MCU (M9) — єдина вісь «зрозуміти до дна».

---

## 2. ДИФФ: ідеал ↔ чинний курс

### 2.0 Знімок чинного курсу (14 секцій, ~288 тем)

1. `osnovy` «Основи: заряд, струм, поле, тепло» — 47 тем (39 ref:physics/* + 8 own)
2. `kola` «Кола й закони» — 37 тем (18 ref:electronics/* + 19 own)
3. `komponenty` «Пасивні компоненти» — 27 тем
4. `napivprovidnyky` «Напівпровідники й діоди» — 7 тем
5. `cyfra-pamyat` «Цифра й памʼять» — 11 тем
6. `zhyvlennia` «Живлення» — 29 тем
7. `mk` «Мікроконтролер і процесор» — 34 теми
8. `peryferiia` «Периферія й шини» — 5 тем
9. `proshyvka` «Прошивка й відлагодження» — 19 тем
10. `davachi` «Давачі» — 10 тем
11. `dyspleyi` «Дисплеї» — 5 тем
12. `keruvannia` «Керування й сигнали» — 25 тем
13. `zvyazok` «Звʼязок і радіо» — 22 теми
14. `drony` «Дрони й автономність» — 11 тем

### 2а. Мої ідеальні модулі, які в курсі Є

| Ідеал | Де в курсі | Коментар |
|---|---|---|
| M1 Фізика електрики | `osnovy` (ref:physics/electric-charge … ref:physics/joule-heating) | Покрито надлишково і якісно — найсильніша секція |
| M2 Кола DC | `kola` (ref:electronics/ohms-law, ref:electronics/kcl, ref:electronics/kvl, ref:electronics/thevenin…) | Ядро є; але секція перевантажена транзисторно-опамповим хвостом (див. 2в) |
| M3 Пасивні компоненти + монтаж | `komponenty` (ref:electronics/resistor…transformer, own:datasheet-practice, own:pcb-assembly-methods, own:smd-rework) | Є, включно з паянням SMD |
| M4 Змінний струм і сигнали | розмазано: `osnovy` (ref:physics/sine-wave, ref:physics/rms-value), `kola` (ref:electronics/phase-shift, own:filter-families, own:cascaded-rc-filters) | Модуля-цілого нема, але зміст присутній |
| M5 Напівпровідники | розколото: діоди в `napivprovidnyky` (own:diodes) і `komponenty` (own:zener-schottky), транзистори/ОП — у `kola` (own:bjt-load-driving, own:bjt-vs-mosfet, own:single-supply-opamp…) | Порушення порядку, див. 2в-1 |
| M7 Від логіки до комп'ютера | фрагменти: `mk` (own:von-neumann-harvard, own:risc-cisc), `cyfra-pamyat` (own:when-memory-runs-out, own:choosing-memory) | Без фундаменту M6; у book/programming/computer-architecture щойно з'явились статті (control-unit, microcode, branch-prediction, tlb…) — готовий матеріал для ref-кроків |
| M9 Мікроконтролер зсередини | `mk` (own:esp32-family, own:baremetal-vs-framework, own:pin-mux, own:memory-budget-mcu, own:esptool-workflow, own:hal-ll-registers) | Є, але без явних тем «GPIO базово», «перший blink» |
| M10 Переривання | `mk` (own:polling-vs-interrupts, own:dma-adc, own:dma-spi-i2s) | Переривання+DMA є; таймери/PWM-периферія — нема (2б) |
| M11 Аналоговий інтерфейс | `keruvannia` (own:signal-acquisition, own:antialiasing-filter-design), `proshyvka` (own:adc-reference-calibration, own:calibration-procedure), `kola` (own:signal-conditioning, ref:electronics/instrumentation-amp) | Розмазано; немає стрижневої теми «ADC/DAC як периферія» (DAC відсутній взагалі) |
| M12 Послідовні протоколи | `peryferiia` (own:spi-vs-i2c, own:pullup-resistor-design, own:usb-uart-bridge, ref:communications/rs-485, ref:communications/differential-pair) | Найтонша секція курсу (5 тем): порівняння SPI/I2C є, а базових «UART», «I2C», «SPI» — нема |
| M13 Живлення | `zhyvlennia` (own:topology-map, own:battery-chemistries, own:linear-vs-switching, own:bms-architecture, own:power-budget…) | Є і глибше за ідеал (BMS, PD, flyback-дизайн) |
| M14 Архітектура вбудованого ПЗ | `mk` (own:super-loop-limits) + `proshyvka` (own:solid-principles, own:error-codes-vs-exceptions, own:error-propagation-patterns, own:memory-safety, own:firmware-testing) | Є по шматках, без стейт-машин як теми (лише proj-вставки) |
| M16-сенсори | `davachi` (own:imu-barometer, own:barometric-altimeter, own:contactless-distance, own:lidar-architecture, own:stereo-vision, ref:electronics/load-cell) | Сенсорна половина є; актуаторної нема (2б) |
| M17 Фільтрація | `keruvannia` (own:choosing-a-filter, own:fir-vs-iir, own:fir-design, own:why-frequency-domain) | Є, добротно |
| M18 Теорія керування | `keruvannia` (own:open-vs-closed-loop, own:proportional-control, own:integral-control, own:derivative-control, own:pid-tuning-cascade, own:loop-stability, own:calculus-for-pid) | Є, повний PID-ланцюг — сильний блок |
| M19 Бездротовий зв'язок | `zvyazok` (own:link-budget, own:esp32-antenna, own:802-11-versions, own:lpwan, own:thread-matter-zigbee, own:fpv-video-systems) | Є, з ухилом у радіофізику й IoT; без BLE і MQTT (2б) |
| M20 Оцінка стану | `keruvannia` (own:kalman-filter, own:attitude-estimation, own:inertial-navigation, own:slam-navigation) | Є як хвіст секції керування; без систем координат/кватерніонів як окремої теми |
| M23 Автономність | фрагменти: `mk` (own:autonomous-system, own:mission-planning, own:edge-inference), `zvyazok` (own:mavlink-from-ground, own:pymavlink), `drony` (own:where-to-compute, own:model-zoo) | Зміст є, але розсипаний по трьох секціях і стоїть частково В СЕРЕДИНІ курсу (2в-3) |
| M24 Надійність (частково) | `proshyvka` (own:fmea-embedded, own:fault-injection-testing), `keruvannia` (own:sensor-fault-detection), `zhyvlennia` (own:esd-protection-circuits, own:emi-filter-design) | Розкидано; регуляцій і капстоуна нема |

### 2б. Відсутні ЯК ЦІЛЕ або лише уривками

1. **M8 Основи програмування (C) — ВІДСУТНІЙ ПОВНІСТЮ. Діра №1.** У курсі жодної теми «змінні/цикли/функції/вказівники/тулчейн». При цьому `proshyvka` вимагає C вільно (own:solid-principles, own:memory-safety, own:error-propagation-patterns), `mk` — own:hal-ll-registers, `keruvannia` — proj-фірмварі всюди. Для заявленого «нуль програмування» курс непрохідний. Немає жодного ref: на book/programming. → new:c-basics, new:c-pointers-memory, new:c-toolchain (або ref:programming/* — у book/programming/computer-architecture уже є integer-types-c, integer-promotion, sign-extension, calling-convention).
2. **M6 Цифрова логіка — відсутня як ціле.** `cyfra-pamyat` стартує одразу з own:pal-to-fpga і own:signal-integrity; біти/двійкова система/вентилі/тригери/лічильники — нема (лише ref:electronics/shift-register). → new:binary-numbers, new:logic-gates, new:flip-flops-counters.
3. **M15 RTOS — відсутній як ціле.** Є лише own:super-loop-limits (`mk`) і own:spinlock-mutex (`proshyvka`). Задачі/планувальник/черги/пріоритети/інверсія — нема. Для ESP32 (ESP-IDF = FreeRTOS) це критична діра. → new:rtos-tasks-scheduler, new:rtos-queues-sync, new:rtos-priorities-inversion.
4. **Мотори й актуатори — відсутні як модуль.** Уривки: own:esc-bldc-driver і own:servo-sizing (обидва аж у `drony`), own:pwm-power-control (`zhyvlennia`). Нема: DC-мотор, BLDC-принцип, кроковий, H-міст, енкодери. Автономна система без модуля приводів. → new:dc-motor, new:bldc-principle, new:h-bridge, new:stepper-motor, new:encoders.
5. **M21 Платформа дрона — відсутня як ціле.** Нема аеродинаміки пропелера, тяги, динаміки квадрокоптера, підбору мотор/пропелер/батарея, збирання рами. `drony` — це ML/відео, а не політ. → new:propeller-thrust, new:quadcopter-dynamics, new:powertrain-sizing, new:frame-build.
6. **M22 Політний контролер — уривками.** own:autonomous-system + own:output-mixing + own:mission-planner-qgc + MAVLink-теми розкидані по `mk`/`zvyazok`/`drony`; нема цілісного модуля: контури rate/attitude, польотні режими, arming/failsafe, ArduPilot vs PX4 vs Betaflight, тюнінг у польоті. → new:flight-modes-failsafe, new:rate-attitude-loops, new:ardupilot-px4-overview, new:flight-tuning.
7. **Базова периферія MCU — уривками:** нема тем «таймери/лічильники», «PWM як периферія (LEDC)», «watchdog», «GPIO базово», «UART базово», «I2C базово», «SPI базово», «DAC». (own:frequency-measurement-methods і own:pullup-resistor-design припускають, що це вже відомо.) → new:gpio-basics, new:timers-counters, new:pwm-peripheral, new:watchdog, new:uart-basics, new:i2c-basics, new:spi-basics.
8. Дрібніші цілі прогалини: **BLE** (нуль згадок — дивно для ESP32; → new:ble-basics), **GNSS глибше** (лише own:onboard-sensors + hist-gps; для автономності треба new:gnss-how-it-works, new:rtk), **path planning / уникнення перешкод** (→ new:path-planning, new:obstacle-avoidance), **системи координат і кватерніони** (→ new:reference-frames-quaternions, перед own:attitude-estimation), **регуляції польотів і безпека** (→ new:drone-regulations), **капстоун** (→ new:capstone-autonomous-mission), **інтро в PCB-флоу** (уривки own:pcb-thermal-design, own:pcb-assembly-methods, own:pcb-antenna-layout, ref:communications/transmission-lines — без стрижня new:pcb-design-intro).

### 2в. Конфлікти порядку секцій з залежностями ідеалу

1. **Транзистори й опампи (секція 2) ДО напівпровідників (секція 4).** own:bjt-load-driving, own:bjt-vs-mosfet, own:multistage-amplifier, own:darlington-vs-sziklai, own:single-supply-opamp, own:opamp-input-types, own:feedback-topologies сидять у `kola`, а own:diodes (p-n, перший напівпровідник) — двома секціями пізніше. Порушує M3→M5: читач керує затвором MOSFET до того, як бачив p-n перехід. (Паралельний секційний агент, імовірно, бачить це зсередини; на рівні модулів — треба або перенести транзисторний хвіст `kola` у/після `napivprovidnyky`, або зробити `napivprovidnyky` секцією 3.)
2. **`napivprovidnyky` і `cyfra-pamyat` (4–5) — насправді про пам'яті й high-speed, і стоять ДО мікроконтролера (7).** own:nor-vs-nand, own:eeprom-fram, own:mram-rram-pcm, own:power-fail-safety (це firmware-тема!), own:signal-integrity, own:ddr-signal-integrity, own:custom-instruction, own:fpga-vs-mcu — усі залежать від розуміння MCU/CPU, якого ще нема. Інверсія M9→(пам'яті, SI).
3. **Найгрубіше: автономність усередині секції 7 `mk`.** own:mavlink-commands, own:autonomous-system, own:mission-planning, own:mission-planner-qgc, own:edge-inference стоять ДО периферії (8), давачів (10), керування (12) і зв'язку (13). За ідеалом це M22–M23 (кінець курсу): «автономна система» без PID, IMU і радіолінка — порожня декларація. Перенести в кінець (модулі 19–20 з розд. 3).
4. **Приводи після мозку: own:esc-bldc-driver і own:servo-sizing аж у секції 14** — ПІСЛЯ всього блоку керування (12). PID-практика (proj-pid-production, proj-p-controller-firmware) у секції 12 не має на чому крутитися. Мотори мають передувати керуванню (M16→M18).
5. **Firmware-залежні теми до прошивки:** own:power-fail-safety (4), own:sleep-current-audit (6, proj-sleep-audit-firmware), own:pwm-power-control (6, proj-slow-pwm-thermostat) — прошивкові практики за 1–3 секції до появи MCU і коду. Наслідок відсутності M8: ці теми нікуди «легально» поставити.
6. **Інструменти вимірювань пізно:** own:sine-on-scope, own:noise-hunting (осцилограф) — секція 9, після того як читач «збирав» підсилювачі й імпульсні перетворювачі в секціях 2–6. Мультиметра як теми нема взагалі. Інструментальний мінімум має бути в M2–M3.
7. **Дубль-розкид MAVLink:** own:mavlink-commands (7) ↔ own:mavlink-from-ground, own:pymavlink (13) — одна тема, розірвана шістьма секціями.
8. Порядок `dyspleyi` (11) між давачами й керуванням — не шкодить (гілка), але розриває природний ланцюг давачі→фільтри→PID.

### 2г. Є в курсі, нема в ідеалі — спеціалізація (не мінус)

- **ESP32-екосистема наскрізь:** own:esp32-vs-8bit, own:esp32-family, own:esp32-module, own:esp32-antenna, own:esptool-workflow, own:wifi-fast-connect, own:pin-mux, own:ota-server (+ own:hal-ll-registers STM32, own:pic-architecture як контраст). Легітимний хребет курсу.
- **Edge AI/ML-підмодуль:** own:edge-inference, own:model-zoo, own:model-export, own:on-device-benchmarking, own:training-data-pipeline, own:where-to-compute — у моєму ідеалі лише «інтро в CV»; тут повноцінний трек (дрони з комп'ютерним зором).
- **Відеотракт:** own:mjpeg-vs-h264, own:isp-pipeline, own:image-stabilization, own:video-streaming-protocols, own:fpv-video-systems — FPV/камерна спеціалізація.
- **Дисплеї (уся секція 11)** — ухил у загальну embedded/HMI-розробку, поза дроновою віссю.
- **FPGA-трек:** own:pal-to-fpga, own:fpga-flow, own:fpga-vs-mcu, own:custom-instruction.
- **Глибина живлення:** own:pd-sink-design, own:fast-charging-protocols, own:flyback-transformer-design, own:loop-gain-measurement, own:bms-architecture, own:active-balancing — силова електроніка глибше за потреби дрона (але BMS дронам доречний).
- **Радіо-глибина:** own:itu-r-propagation-models, own:multiple-access-methods, own:nfc-rfid, own:rf-frontend, own:jamming-fhss (глушіння — укр. контекст, дуже доречно).
- **DSP-застосунки збоку:** own:vibration-diagnostics, own:active-noise-cancellation, own:tone-detection.
- Фізичні цікавинки: ref:physics/faraday-cage, ref:physics/triboelectricity, own:lightning-protection.

---

## 3. РЕКОМЕНДОВАНИЙ ПОРЯДОК МОДУЛІВ

(чинні секції ± перекомпоновка + нові модулі; напівжирним — нове)

1. `osnovy` — фізика електрики й сигналів (як є)
2. `kola` — закони кіл, ЛИШЕ пасивна частина (транзисторно-опамповий хвіст → у п.4)
3. `komponenty` — пасивні компоненти, датасіти, монтаж/паяння + **вимірювальний мінімум** (мультиметр; сюди ж own:sine-on-scope, own:noise-hunting з `proshyvka`)
4. `napivprovidnyky` (розширена) — p-n, own:diodes, own:zener-schottky + перенесені BJT/MOSFET/ОП-теми з `kola`; пам'яті (own:nor-vs-nand, own:eeprom-fram, own:mram-rram-pcm) → у п.6
5. **new:tsyfrova-lohika** — біти, системи числення, вентилі, тригери, лічильники (ref:electronics/shift-register сюди)
6. `cyfra-pamyat` → «Від логіки до комп'ютера» — own:von-neumann-harvard і own:risc-cisc (з `mk`) + пам'яті (з п.4) + ref:programming/computer-architecture/* (нові статті book); FPGA/SI/DDR-хвіст лишити тут наприкінці як гілку
7. **new:prohramuvannia-c** — від змінних до вказівників і тулчейна (можливі ref:programming/*)
8. `zhyvlennia` — як є, мінус firmware-практики (own:sleep-current-audit → п.11)
9. `mk` — мікроконтролер: залишити платформено-прошивкове ядро + **new:gpio-basics, new:timers-counters, new:pwm-peripheral, new:watchdog**; ЗАБРАТИ own:mavlink-commands, own:autonomous-system, own:mission-planning, own:mission-planner-qgc (→ п.19–20), own:edge-inference (→ п.20)
10. `peryferiia` — розширити: **new:uart-basics, new:i2c-basics, new:spi-basics**, потім own:spi-vs-i2c, RS-485, USB
11. `proshyvka` — інженерія прошивки (SOLID, тестування, налагодження, git) + повернуті firmware-практики живлення
12. **new:rtos-freertos** — задачі/черги/пріоритети (own:super-loop-limits як міст, own:spinlock-mutex сюди)
13. `davachi` — сенсори + **new:gnss-rtk**
14. **new:motory-aktuatory** — DC/BLDC/крокові/серво, H-міст, енкодери; сюди own:esc-bldc-driver, own:servo-sizing з `drony`
15. `keruvannia` — фільтри → PID → оцінка стану (додати **new:reference-frames-quaternions** перед own:attitude-estimation)
16. `zvyazok` — радіо/мережі + **new:ble-basics**; MAVLink-пару (own:mavlink-from-ground, own:pymavlink) тримати тут наприкінці або злити в п.19
17. `dyspleyi` — як гілка (місце некритичне, можна лишити де є)
18. **new:platforma-drona** — пропелер/тяга, динаміка квадро, підбір пропульсії, збирання, LiPo-практика (спирається на п.8, 13, 14)
19. **new:polit-kontroler** — ArduPilot/PX4/Betaflight, own:output-mixing, контури rate/attitude, режими/failsafe, MAVLink-стек (own:mavlink-commands, own:mission-planner-qgc сюди), тюнінг
20. `drony` → «Автономність і зір» — own:where-to-compute, own:autonomous-system, own:mission-planning, ML-трек (own:model-zoo…), відеотракт, own:slam-navigation-застосування + **new:path-planning, new:obstacle-avoidance**
21. **new:nadiinist-bezpeka-kapstoun** — FMEA/fault-injection (консолідація), EMC-підсумок, **new:drone-regulations**, **new:capstone-autonomous-mission**

## 4. Топ дір за пріоритетом

- **P0** — new:prohramuvannia-c (модуль 7): без нього курс непрохідний для цільової аудиторії «нуль програмування»; ~половина курсу (секції 7–14) читає C-код.
- **P0** — new:tsyfrova-lohika (модуль 5): міст фізика→процесор зараз обірваний.
- **P0** — new:rtos-freertos (модуль 12): ESP-IDF стоїть на FreeRTOS, курс мовчить.
- **P1** — new:platforma-drona + new:polit-kontroler (модулі 18–19): курс обіцяє автономні дрони, але польотної механіки/стека в ньому нема — лише ML/відео.
- **P1** — new:motory-aktuatory (модуль 14): актуатори — половина «автономної системи».
- **P1** — базова периферія: new:uart/i2c/spi-basics, new:gpio-basics, new:timers-counters, new:pwm-peripheral, new:watchdog.
- **P2** — new:ble-basics, new:gnss-rtk, new:path-planning, new:reference-frames-quaternions, new:drone-regulations, new:pcb-design-intro, new:capstone-autonomous-mission.
- **Перекомпоновки без нового письма:** транзистори/ОП з `kola` → після діодів; пам'яті з `napivprovidnyky` → до комп'ютерного модуля; MAVLink/автономність із `mk` → у кінець; own:esc-bldc-driver, own:servo-sizing з `drony` → до керування; осцилограф із `proshyvka` → у `komponenty`.

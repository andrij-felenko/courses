# Курс «Вбудована електроніка й автономні системи» — покриття областей домену (рівень цілого курсу)

Аналіз: `guide/embedded/manifest.js` (14 секцій-модулів) проти повного домену вбудованих систем «від фізики заряду до автономних дронів і продакшена». Наявність готових ref-статей перевірено по маніфестах книг (`electronics`, `physics`, `programming`, `communications`, `algorithms`). Статуси ref: **(done)** = стаття готова, лишається вписати крок у guide; **(pending)** = стаття запланована в книзі, ще не написана.

Поточні модулі: 1 osnovy · 2 kola · 3 komponenty · 4 napivprovidnyky · 5 cyfra-pamyat · 6 zhyvlennia · 7 mk · 8 peryferiia · 9 proshyvka · 10 davachi · 11 dyspleyi · 12 keruvannia · 13 zvyazok · 14 drony.

---

## Зведена таблиця областей

| # | Область | Вердикт | Пріоритет діри |
|---|---------|---------|----------------|
| 1 | Фізика електрики й магнетизму | ПОКРИТА | — |
| 2 | Аналогові кола (закони, RC/RL, фільтри, транзистори, ОП) | ПОКРИТА (з застереженням про місце в порядку) | — |
| 3 | Пасивні компоненти | ПОКРИТА | — |
| 4 | Напівпровідники як прилади (PN, будова BJT/MOSFET, CMOS) | ЧАСТКОВА | важливо |
| 5 | **Цифрова логіка (вентилі→тригери→лічильники→FSM)** | **ВІДСУТНЯ** | **критично** |
| 6 | Архітектура компʼютера (процесор, ISA, конвеєр, кеш, DMA) | ЧАСТКОВА | важливо |
| 7 | **Числа й дані в машині (біти, endianness, fixed/float)** | **ВІДСУТНЯ** | **критично** |
| 8 | **Мова C і базове програмування** | **ВІДСУТНЯ** (і в книгах теж) | **критично** |
| 9 | Тулчейн: компіляція, лінкер, memory map, startup | ЧАСТКОВА | критично |
| 10 | **Периферія МК: GPIO, таймери, PWM, АЦП, watchdog, RTC** | **ВІДСУТНЯ як блок** | **критично** |
| 11 | Шини: UART, I2C, SPI, CAN, USB-device | ЧАСТКОВА (модуль з 5 тем) | критично |
| 12 | Переривання глибоко (ISR, пріоритети, гонки, NVIC) | ЧАСТКОВА | важливо |
| 13 | **RTOS і паралельність (FreeRTOS: задачі, черги, семафори)** | ЧАСТКОВА (майже відсутня) | **критично** |
| 14 | Прошивка як інженерія (архітектура коду, тести, git) | ПОКРИТА (діра: CI/HIL) | важливо |
| 15 | Bootloader / OTA / персистентність (NVS, розділи) | ЧАСТКОВА | важливо |
| 16 | Безпека (secure boot, шифрування, TLS, захист лінка) | ЧАСТКОВА | важливо |
| 17 | Живлення й батареї (топології, USB-PD, BMS) | ПОКРИТА | — |
| 18 | Давачі | ПОКРИТА (дрібні діри: магнітометр, енкодери, GNSS) | важливо |
| 19 | Дисплеї | ПОКРИТА | — |
| 20 | DSP (дискретизація, фільтри, спектр) | ПОКРИТА (дрібне: крок FFT) | пізніше |
| 21 | Теорія керування (PID, стійкість, Калман) | ПОКРИТА | — |
| 22 | Навігація й автономність (fusion, INS, SLAM, GNSS, план шляху) | ЧАСТКОВА | важливо |
| 23 | **Мотори й привода (DC, H-міст, BLDC, крокові, серво)** | ЧАСТКОВА (майже відсутня) | **критично** |
| 24 | Звʼязок і радіо (RF, антени, лінк, MAVLink) | ПОКРИТА | — |
| 25 | **Мережі для IoT (Wi-Fi/BLE/TCP/сокети/MQTT на ESP32)** | **ВІДСУТНЯ як блок** | **критично** |
| 26 | PCB-проєктування (схема→layout→гербери, землі, розвʼязка) | ЧАСТКОВА | важливо |
| 27 | EMC/ESD і сертифікація (CE/FCC, радіосертифікація) | ЧАСТКОВА | пізніше |
| 28 | Надійність і functional safety | ЧАСТКОВА | пізніше |
| 29 | Виробництво й тестування серії (DFM, джиги, провізіонування) | ВІДСУТНЯ | пізніше (але потрібна для мети «до продакшена») |
| 30 | Налагодження як дисципліна | ПОКРИТА | — |
| 31 | Інструменти вимірювань (мультиметр, осцилограф, лог. аналізатор) | ЧАСТКОВА | важливо |

---

## Деталі по областях

### 1. Фізика електрики — ПОКРИТА
Модуль osnovy: ~47 тем від ref:physics/electric-charge до ref:physics/air-breakdown + власні зведення (own:field-and-potential, own:electrostatics-summary, own:noise-interference, own:memory-cell-physics). Найповніший модуль курсу.

### 2. Аналогові кола — ПОКРИТА, але з порушенням модульного порядку
kola: закони (ref:electronics/ohms-law … ref:electronics/wheatstone-bridge), динаміка (ref:electronics/rc-time-constant, rl-time-constant, phase-shift), транзисторні каскади (own:bjt-load-driving, own:bjt-vs-mosfet, own:multistage-amplifier, own:darlington-vs-sziklai), ОП (own:single-supply-opamp, own:kcl-opamp-analysis, own:opamp-input-types, own:feedback-topologies, ref:electronics/instrumentation-amp), фільтри (own:filter-families, own:cascaded-rc-filters).
**Проблема порядку:** транзисторні й ОП-теми стоять у модулі 2, а напівпровідники пояснюються в модулі 4. Для новачка BJT зʼявляється до PN-переходу. На рівні модулів: або перенести активну частину kola після napivprovidnyky, або перенести napivprovidnyky перед kola. Дрібні відсутні кроки: ref:electronics/comparator (done), ref:electronics/schmitt-trigger (done), ref:electronics/lc-resonance / bode-plot / frequency-response (done) — легко додати ref-ами.

### 4. Напівпровідники як прилади — ЧАСТКОВА
Є: ref:electronics/esd-damage, own:diodes, own:sic-gan-comparison; але секція одразу стрибає у флеш-памʼять (own:nor-vs-nand, own:eeprom-fram, own:mram-rram-pcm — це радше тема модуля «памʼять», дублює нішу cyfra-pamyat).
Бракує: PN-перехід і легування — ref:physics/semiconductor (done), ref:physics/doping (done), ref:physics/pn-junction (done); будова приладів — ref:electronics/bjt-structure (done), ref:electronics/mosfet-structure (done), ref:electronics/nmos-pmos (done), ref:electronics/cmos (done); за бажання глибше — ref:physics/band-theory (pending), ref:physics/fermi-level (pending).
Вердикт: розширити модуль ref-ами (усі ключові — done), флеш-теми віддати cyfra-pamyat. Пріоритет: важливо.

### 5. Цифрова логіка — ВІДСУТНЯ (найбільша «дешева» діра)
cyfra-pamyat починається з ref:electronics/shift-register і одразу own:pal-to-fpga / own:fpga-flow. Вентилі, тригери, лічильники, автомати — ніде. Новачок не зможе прочитати FPGA-теми, синхронне скидання (own:synchronous-reset) чи зрозуміти, що таке регістр периферії.
У книзі electronics/digital ГОТОВИЙ повний ланцюг (усі basic done): ref:electronics/why-digital, logic-levels-as-ranges, noise-margin, logic-families, edges-rise-time, threshold-schmitt, basic-gates, nand-nor, xor-comparison, cmos-gate, combinational-circuits, gates-to-functions, state-memory, sr-latch, d-flip-flop, edge-vs-level, register, clock-signal, counters, metastability-timing, finite-state-machines, programmable-logic + рівні узгодження ref:electronics/level-shifter (done), gpio-expander (done).
Вердикт: **окремий розділ «Цифрова логіка» на початку cyfra-pamyat (або власний модуль перед ним) — збирається майже цілком з готових ref. Критично.**

### 6. Архітектура компʼютера — ЧАСТКОВА
У mk є own:von-neumann-harvard, own:risc-cisc, own:pic-architecture (done). Але свіжа секція book/programming/computer-architecture не вписана: ref:programming/what-is-processor, processor-parts, fetch-decode-execute, isa, clock-frequency, pipeline, cache, mcu-blocks, interrupt-vector, dma-problem, dma-controller, dma-channels (усі done) — це саме той місток «від логіки до процесора», якого новачку бракує перед von-neumann-harvard. Глибші (done): cache-coherence, tlb, branch-prediction, superscalar, fpu, calling-convention, microcode, ahb-apb-bus.
Вердикт: додати вступний ланцюг ref-ами у mk (або окремий розділ «Як працює процесор»). Важливо.

### 7. Числа й дані в машині — ВІДСУТНЯ
Ніде в курсі: двійкова/шістнадцяткова система, біти/байти, endianness, переповнення, fixed/float. Без цього не читаються регістри, протоколи, АЦП.
Готові ref (усі done): ref:programming/bits-bytes-endianness, ref:programming/overflow-wraparound, ref:programming/sign-extension, ref:programming/integer-types-c, ref:programming/fixed-point, ref:programming/floating-point, ref:programming/ascii-utf8, ref:programming/saturating-arithmetic, ref:programming/half-precision.
Вердикт: **розділ «Числа в машині» перед програмуванням/МК. Критично.**

### 8. Мова C і базове програмування — ВІДСУТНЯ повністю
Аудиторія «нуль програмування», а перші фрагменти коду зʼявляються вже у вставках модуля zhyvlennia (proj-sleep-firmware, proj-pd-state-machine) і масово в mk. Жодної теми «змінні, типи, цикли, функції, масиви, структури, бітові операції». У book/programming C-основ теж немає (languages починається з compilation; systems — з памʼяті).
Вердикт: **новий модуль «Мова C для заліза» — треба ПИСАТИ нові статті курсу**: new:c-first-program, new:c-variables-types, new:c-control-flow, new:c-functions, new:c-arrays-strings, new:c-structs-enums, new:c-bit-operations, new:c-preprocessor, new:c-modules-headers. Поруч лягають готові ref:programming/addresses-pointers (done), ref:programming/function-pointers (pending), ref:programming/volatile (done). **Критично — найбільший обсяг нового письма.**

### 9. Тулчейн і память програми — ЧАСТКОВА
Є: own:memory-budget-mcu, own:addr2line-workflow, own:esptool-workflow, own:boot-time-budget, own:hal-ll-registers.
Готові ref (done): ref:programming/compilation, compiler-stages, linking, memory-as-array, memory-map, flash-vs-ram, stack-lifo, heap-dynamic-memory, stack-overflow, firmware-image, c-runtime, memory-mapped-io. Pending у книзі: toolchain, linker-script, startup-code, vector-table, elf-format, mcu-startup-sequence, cmsis, platformio.
Вердикт: розділ «Що відбувається з кодом: від .c до Flash» — половина з готових ref, решту дописати. Критично (це хребет розуміння прошивки).

### 10. Периферія МК (GPIO/таймери/PWM/АЦП) — ВІДСУТНЯ як блок
Парадокс курсу: у mk є own:dma-adc, own:dma-spi-i2s, own:pin-mux — а базових «що таке GPIO», «таймер», «PWM», «АЦП» кроків немає взагалі. peryferiia (5 тем) цього не дає.
Готові ref (done): ref:programming/gpio-registers, module-model (кнопки/матриці), timer-counter, timer-overflow, capture-compare, millis-micros, nonblocking-time, periodic-scheduling, pwm, hardware-pwm, pwm-resolution, watchdog, rtc, double-buffering, clock-power; АЦП: ref:electronics/adc-errors (done), ref:electronics/voltage-reference (done), own:signal-acquisition уже в keruvannia; pending: sar-adc-internals, dac-r-2r, pcnt-pulse-counter, rmt-peripheral, mcpwm-peripheral, interrupt-driven-io.
Вердикт: **розгорнути peryferiia у повний модуль «Периферія МК» (GPIO → переривання → таймери → PWM → АЦП/ЦАП → watchdog/RTC) — 80% з готових ref. Критично.**

### 11. Шини і протоколи — ЧАСТКОВА
Є: own:spi-vs-i2c, own:pullup-resistor-design, own:usb-uart-bridge, ref:communications/differential-pair, ref:communications/rs-485.
Бракує основ, які ВЖЕ готові (done): ref:communications/async-serial, uart-frame, baud-rate, i2c-bus, i2c-addressing, start-stop-ack, i2c-transaction, register-map, spi-bus, spi-lines, cpol-cpha, chip-select, spi-speed, clock-stretch-arbitration; USB-пристрій: ref:programming/usb-overview, usb-physical, usb-enumeration, usb-endpoints, usb-device-classes, esp32-usb, tinyusb-device (усі done).
CAN — повністю відсутній і в guide, і написаний: ref:communications/can-arbitration (pending), can-frame-errors (pending), dronecan (pending) — для дронової тематики (ESC-телеметрія, GPS по DroneCAN) це помітна діра. Також pending: modbus, i2s-bus, sd-card-protocol, qspi.
Вердикт: розширити модуль шин ref-ами (UART/I2C/SPI — задарма), CAN/DroneCAN — дописати. Критично (основи) / важливо (CAN).

### 12. Переривання глибоко — ЧАСТКОВА
Є own:polling-vs-interrupts (з math-isr-budget). Готові ref (done): ref:programming/interrupts, isr, interrupt-priorities, interrupt-vector, atomicity-races, dma-cache-races. Pending: nvic-cortex-m, interrupt-latency, critical-sections, nmi-exceptions, fpu-context-isr. Вердикт: ланцюг з 4–5 готових ref у модуль периферії/МК. Важливо.

### 13. RTOS і паралельність — майже ВІДСУТНЯ (для ESP32-курсу — критично)
Є лише own:super-loop-limits (mk) і own:spinlock-mutex (proshyvka). ESP-IDF = FreeRTOS, без цього половина практики висить у повітрі.
Готові ref (done): ref:programming/super-loop, tasks, scheduler, task-ipc (черги/семафори/deadlock/priority inheritance), task-stacks, freertos (з comp-dual-core), realtime-determinism (rate-monotonic), atomicity-races. Pending: priority-inversion, context-switch, task-priorities, event-groups, task-notification, message-buffer, freertos-heap, task-states, wcrt-analysis.
Вердикт: **розділ «RTOS» (у mk або окремо перед прошивкою) — ядро збирається з готових ref. Критично.**

### 14. Прошивка як інженерія — ПОКРИТА з однією дірою
Є: own:firmware-testing, own:solid-principles, own:error-codes-vs-exceptions, own:error-propagation-patterns, own:memory-safety, own:gitflow-branching, own:fmea-embedded, own:fault-injection-testing. Доступні підсилення (done): ref:programming/static-analysis, profiling, assert-panic, defensive-programming, error-handling, fuzzing, code-review, design-by-contract, sitl-simulation.
Діра: **CI для прошивки** (збірка на сервері, автопрошивка, HIL-стенд) — немає ні в guide, ні в книгах → new:firmware-ci, new:hil-testing; ref:programming/version-control (pending). Важливо.

### 15. Bootloader / OTA — ЧАСТКОВА
Є own:ota-server, own:esptool-workflow, own:reset-sequence, own:boot-time-budget. Готові ref (done): ref:programming/bootloader, partition-table, flashing, ota-slots, ota-update, nvs, write-integrity, why-persist, flash-internals, wear-leveling, reset-causes, reboot-strategy, reboot-counter, safe-mode. Pending: ota-rollback, delta-ota, ota-image-signing.
Вердикт: розділ «Життєвий цикл прошивки» з готових ref. Важливо.

### 16. Безпека — ЧАСТКОВА
Є own:tpm-trustzone (+proj-esp32-secure-boot). Готовий ref:programming/secure-boot (done). Далі все pending: flash-encryption, nvs-encryption, ota-image-signing, mavlink-v2-signing, wpa-security, ble-security, rfid-security; TLS/крипто на MCU відсутні і в книгах → new:tls-mbedtls-mcu, new:crypto-basics-embedded (або algorithms/cryptographic-algorithms — секція є, релевантних готових тем не видно).
Вердикт: для дронів (ворожий ефір, перехоплення керування) — важливо; частину доведеться писати.

### 18. Давачі — ПОКРИТА для дронового ухилу, дрібні діри
Є: IMU (own:imu-barometer, own:imu-mounting-materials), барометр, LiDAR, стерео, ультразвук, тензо, вібро. Діри: магнітометр/компас — ref:electronics/magnetometer (done), калібрування компаса — new або ref:electronics/imu-calibration (pending); енкодери (потрібні для роверів/моторів): ref:electronics/optical-incremental-encoder (done), quadrature (pending), hall-magnetic-encoders (pending), absolute-encoder-gray-code (pending); температура: ref:electronics/ntc-thermistor (done), thermocouple (pending); загальний вступ: ref:electronics/what-is-a-sensor, sensor-characteristics, drift-hysteresis-noise (done). GNSS глибоко — див. 22. Важливо (магнітометр+енкодери), решта пізніше.

### 20–21. DSP і керування — ПОКРИТІ
keruvannia — найцільніший модуль (PID-ланцюг, стійкість, фільтри, Калман). Дрібне: крок про FFT — ref:algorithms/fft (done); передискретизація/децимація (pending у communications). Пізніше.

### 22. Навігація й автономність — ЧАСТКОВА
Є: own:inertial-navigation, own:slam-navigation, own:attitude-estimation, own:kalman-filter, own:mission-planning (mk), own:autonomous-system (mk). Готові ref (done): ref:algorithms/sensor-fusion, complementary-filter, kalman-ekf, odometry, motion-model, predict-vs-measure, stabilization-cascade, roll-pitch-yaw-control, motor-mixer; ref:communications/gnss (done).
Бракує: GNSS глибоко/RTK — ref:communications/sbas-corrections (pending), ref:algorithms/rtk-integer-ambiguity (pending), new:gnss-receiver-integration (NMEA/UBX у прошивці); планування шляху — ref:algorithms/dijkstra (pending), a-star/RRT відсутні в книгах → new:path-planning-grid, new:obstacle-avoidance; geofence — ref:programming/geofence (pending), ref:algorithms/geofence-algorithm (pending); pure pursuit (pending).
Вердикт: розділ «Навігація» перед drony: fusion-ланцюг з готових ref + дописати GNSS/планування. Важливо.

### 23. Мотори й привода — ЧАСТКОВА, майже відсутня (критично для «автономних апаратів»)
У курсі лише own:servo-sizing і own:esc-bldc-driver (drony) + own:pwm-power-control (zhyvlennia). Немає: як працює DC-мотор, H-міст, комутація BLDC, кроковий, серво зсередини, редуктори, струм заклинювання.
Готові ref (done): ref:electronics/brushed-dc-motor, bldc-motor, stepper-motor, hobby-servo, servo, gearmotor, dc-motor-driver, stepper-driver, motor-current-stall-heat, gears-transmission, solenoid-relay, relay-driver. Pending: foc-control, back-emf, actuator-selection, closed-loop-stepper, motor-torque-speed-curve.
Вердикт: **новий модуль «Мотори й привода» (між давачами/керуванням і дронами) — ядро з готових ref. Критично: це виконавча ланка будь-якого автономного апарата.**

### 25. Мережі для IoT — ВІДСУТНЯ як блок (для ESP32-курсу — критично)
У zvyazok радіо/RF покриті добре, але прикладного мережевого стека немає: єдине — ref:communications/ip-routing і own:wifi-fast-connect (mk), own:802-11-versions.
Готові ref (done): ref:communications/wifi, mac-ip-arp, channel-band-packet, tcp-vs-udp, reliable-link, **mqtt (basic+detailed done)**, ble-gatt, bluetooth-spp, on-chip-radio, latency-reliability, bandwidth-loss; ref:programming/sockets-tcp-udp, web-server-mcu, esp-hosted, ethernet-on-mcu. Pending: esp-now, dhcp-dns, nat, wpa-security, ble-gap/att/security, lwip-internals, socket-api, ntp-sync.
Вердикт: **розділ «ESP32 у мережі» (Wi-Fi → TCP/UDP/сокети → MQTT/HTTP → BLE → ESP-NOW) — переважно з готових ref. Критично: це головна причина обирати ESP32.**

### 26. PCB-проєктування — ЧАСТКОВА
Розкидано: own:pcb-thermal-design, own:pcb-assembly-methods, own:smd-rework (komponenty), own:pcb-antenna-layout (zvyazok), own:signal-integrity, ref:communications/transmission-lines (cyfra-pamyat), own:reading-schematics, own:net-labels-buses (kola).
Бракує цілого циклу «схема → плата»: ref:electronics/eda-tools (pending), ground-plane (pending), current-return-path (pending), pcb-stackup-rf (pending), via-inductance (pending), creepage-clearance (pending), pdn-impedance (pending), common-ground (status не перевірявся), + нові практичні: new:kicad-schematic-to-layout, new:decoupling-placement, new:gerber-and-ordering, new:footprint-libraries.
Вердикт: тягне на окремий модуль «Плата: від схеми до замовлення» ближче до кінця курсу. Важливо (курс практичний — читач муситиме зробити плату).

### 27. EMC/ESD і сертифікація — ЧАСТКОВА
Фізика завад (osnovy), own:esd-protection-circuits, own:emi-filter-design, own:surge-protection-cascade, own:lightning-protection — є. Бракує: EMC як дисципліна — ref:electronics/electromagnetic-compatibility (pending), cable-emi (pending), сертифікація — ref:communications/emc-certification (pending), regulatory-radio-certification (pending), + new:precompliance-testing. Пізніше (але обовʼязково для продакшен-мети).

### 28. Надійність / functional safety — ЧАСТКОВА
Є: FMEA, fault-injection, sensor-fault-detection, ref-и book done: redundancy, failsafe, safe-mode, graceful-degradation, watchdog. Бракує: стандарти functional safety (IEC 61508 / DO-178 оглядово) → new:functional-safety-overview; WCET/schedulability — ref:programming/wcet-analysis (pending). Пізніше.

### 29. Виробництво серії — ВІДСУТНЯ
Немає: DFM/DFT, панелізація, тест-джиги (bed-of-nails), заводська прошивка/провізіонування, серіалізація, burn-in, конформне покриття, корпуси/IP-рейтинг. У книгах лише ref:electronics/testing-binning (IC-рівень), ref:programming/isp-programming (pending). Все — нові статті: new:dfm-basics, new:test-jig-design, new:factory-provisioning, new:enclosure-ip-rating. Пізніше, але без цього заявлена мета «до продакшена» не закрита.

### 31. Інструменти вимірювань — ЧАСТКОВА
Є практика осцилографа (own:sine-on-scope, own:noise-hunting, own:measure-consumption). Бракує вступних кроків, які потрібні вже в модулях 2–3: ref:electronics/multimeter (done), oscilloscope (done), logic-analyzer (done), lab-power-supply (done), electronic-load (done), first-power-up-check (status?), fault-finding (status?). Вердикт: міні-розділ «Інструменти» ПЕРЕД серединою курсу (зараз усе живе в модулі 9). Важливо.

---

## Порядок модулів — рекомендація

Поточні модульні проблеми порядку:
1. **Транзистори/ОП (kola, м.2) до напівпровідників (м.4).**
2. **mk (м.7) використовує DMA+АЦП/SPI/I2S до того, як peryferiia (м.8) вводить самі шини**; базових GPIO/таймерів немає ніде.
3. **MAVLink/автономія/місії сидять у mk (м.7)** — own:mavlink-commands, own:autonomous-system, own:mission-planning, own:mission-planner-qgc, own:ota-server — задовго до zvyazok (м.13) і drony (м.14), де їхнє природне місце.
4. Флеш-технології в napivprovidnyky дублюють нішу cyfra-pamyat.
5. Інструменти вимірювань замкнені в proshyvka (м.9), а потрібні з м.2.
6. Жодного модуля програмування перед mk — а прошивочні proj-вставки починаються вже в zhyvlennia (м.6).

Рекомендований скелет (нові блоки позначено ★):
1. Основи (фізика) → 2. Кола (пасивна частина) → 3. Пасивні компоненти → 4. Напівпровідники (розширені ref-ами) → 5. Активна схемотехніка (транзистори, ОП — з kola) → 6. ★Цифрова логіка + цифра-памʼять/FPGA → 7. Живлення → 8. ★Числа в машині + мова C + тулчейн → 9. МК і архітектура процесора → 10. ★Периферія МК (GPIO/переривання/таймери/PWM/АЦП) → 11. Шини (UART/I2C/SPI/CAN/USB) → 12. ★RTOS → 13. Прошивка як інженерія + bootloader/OTA/безпека → 14. Інструменти й налагодження → 15. Давачі → 16. Дисплеї → 17. DSP і керування → 18. ★Мотори й привода → 19. Звʼязок і радіо + ★мережі IoT → 20. Навігація й автономність → 21. Дрони: політний стек і капстоун → 22. ★PCB від схеми до плати → 23. ★Надійність, EMC, сертифікація, виробництво.

Окреме спостереження для м.21: у book/programming/embedded-systems уже заплановано цілий фінальний дроновий блок, не вписаний у guide: ref:programming/flight-controller (done), ardupilot-layers (done), params-gcs (done), failsafe (done), fc-vs-companion (done), redundancy (done) + pending: manual-stabilized-modes, position-modes, arming-checks, mode-state-machine, first-bringup, preflight-safety, end-to-end-mission, capstone-task. Це готовий каркас завершального модуля курсу.

---

## Топ дір за пріоритетом

**Критично (без цього курс не веде новачка до мети):**
1. Мова C + числа в машині + тулчейн — новий модуль; числа/тулчейн з ref (done), C-основи писати (new:c-*). Найбільший обсяг нового письма.
2. Периферія МК (GPIO/переривання/таймери/PWM/АЦП) — розгорнути peryferiia; майже все з ref:programming/* (done).
3. Цифрова логіка — розділ перед FPGA; цілком з ref:electronics/* (done).
4. RTOS/FreeRTOS — розділ; ядро з ref:programming/* (done).
5. Мережі IoT на ESP32 (Wi-Fi/сокети/MQTT/BLE) — розділ у zvyazok; переважно ref (done, mqtt навіть detailed).
6. Мотори й привода — новий модуль; ядро з ref:electronics/electromechanics (done).
7. Основи шин UART/I2C/SPI — ref (done); CAN/DroneCAN — писати (pending).

**Важливо:** архітектура процесора вступно (ref done); переривання глибоко (ref done); bootloader/OTA (ref done); напівпровідники-прилади (ref done); інструменти вимірювань раніше (ref done); PCB-модуль (ref pending + new); навігація: GNSS/RTK/план шляху (pending + new); безпека: TLS/шифрування (new + pending); CI/HIL (new); магнітометр/енкодери (частина ref done).

**Пізніше:** EMC-сертифікація; functional safety стандарти; виробництво серії (DFM/джиги/провізіонування — все new); FFT-крок; DAC; аудіо.

**Ключова добра новина:** ~70% критичних дір закриваються вписуванням ГОТОВИХ book-статей (status done) ref-кроками — нового письма найбільше потребують лише C-основи, CAN, PCB-цикл, виробництво і TLS/безпека.

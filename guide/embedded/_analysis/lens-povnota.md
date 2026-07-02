# Лінза «Повнота домену» — guide/embedded («Вбудована електроніка й автономні системи»)

Аналіз за назвами тем маніфесту `guide/embedded/manifest.js` (335 рядків, 14 секцій, ~289 кроків) проти канонічної мапи домену та проти наявних статей у 7 предметних книгах (`book/*/manifest.js`, разом 2418 тем).

Позначення: **(done)** — стаття книги готова, ref можна ставити одразу; **(pending)** — тема заведена в book-маніфесті, але ще не написана; **new:** — теми немає ніде, треба заводити. Пріоритети: **КРИТ** = критично-для-новачка, **ВАЖЛ** = важливо, **ПІЗН** = пізніше.

---

## 1. Знімок курсу

| # | Секція | Кроків | ref | власних | Зміст фактично |
|---|--------|--------|-----|---------|----------------|
| 1 | osnovy | 47 | 39 | 8 | фізика: заряд→струм→опір→AC→магнетизм→шум |
| 2 | kola | 36 | 18 | 18 | закони кіл + читання схем + **BJT/MOSFET/ОП (просунуте)** |
| 3 | komponenty | 27 | 12 | 15 | RLC-пасив, захисти, датащит-практикуми, резонатори, монтаж |
| 4 | napivprovidnyky | 7 | 1 | 6 | ESD, діоди, flash/EEPROM/FRAM/MRAM (!), power-fail |
| 5 | cyfra-pamyat | 11 | 2 | 9 | PAL→FPGA, вибір пам'яті, signal integrity |
| 6 | zhyvlennia | 30 | 0 | 30 | топології, USB-PD, батареї, BMS, захисти |
| 7 | mk | 34 | 0 | 34 | архітектури, ESP32, DMA, налагодження, **OTA-сервер, MAVLink, місії (!)** |
| 8 | peryferiia | 5 | 2 | 3 | диф.пара, RS-485, spi-vs-i2c, підтяжка, USB-UART |
| 9 | proshyvka | 21 | 1 | 20 | осцилограф, тестування, помилки, FMEA, SOLID, git-flow |
| 10 | davachi | 10 | 1 | 9 | далекоміри, IMU/барометр, LiDAR, стерео |
| 11 | dyspleyi | 5 | 0 | 5 | класи, вибір, ініціалізація, колір |
| 12 | keruvannia | 24 | 0 | 24 | фільтри, PID-каскад, Калман, SLAM, орієнтація |
| 13 | zvyazok | 21 | 1 | 20 | лінк-бюджет, антена ESP32, FHSS, LPWAN, FPV, відеострімінг |
| 14 | drony | 11 | 0 | 11 | кодеки, edge-ML, ESC, ISP, стабілізація зображення |

**Разом:** ~289 кроків = 77 ref + 212 власних. Майже все написано (єдиний `pending` basic — `kola/net-labels-buses`), тобто знайдені діри — це справді **відсутні кроки**, а не недописані.

**Ключовий системний факт:** усі 77 ref ідуть лише у 3 книги — physics (39), electronics (34), communications (4). **Жодного ref у `programming/` (356 тем, з них `embedded-systems` — 177, десятки зі статусом done), жодного в `algorithms/` і `math/`.** Половина канону embedded-курсу вже написана в книгах і просто не підключена до курсу.

---

## 2. Канонічна мапа домену і статус покриття

| Область канону | Статус у курсі | Де |
|---|---|---|
| Фізика електрики й тепла | ✔ повно | osnovy |
| Кола DC | ✔ повно | kola |
| Кола AC: реактивність, імпеданс, резонанс, RC-фільтри | ✖ **діра** (є лише сталі часу і фаза) | → G15 |
| Пасивні компоненти | ✔ повно | komponenty |
| Інструменти й перша практика (мультиметр, макетка, пайка) | ✖ **діра** (осцилограф аж у §9) | → G13 |
| Напівпровідники: PN → діод → транзистор | ◐ частково (BJT «вискакує» в kola без введення) | → G14 |
| Аналогові вузли: компаратор, ОП-основи, 555, генератори | ◐ лише просунуте | → G15 |
| Цифрова логіка: вентилі → тригери → лічильники → FSM | ✖ **ціла область відсутня** | → G2 |
| Двійкове подання чисел | ✖ діра | → G1/G2 |
| Мова C і програмування з нуля | ✖ **ціла область відсутня** | → G1 |
| Тулчейн: компіляція → лінк → образ → карта пам'яті | ◐ (є esptool, openocd-gdb, бюджети — без бази) | → G8 |
| Процесор зсередини (до RISC/CISC) | ◐ | → G16 |
| GPIO, переривання, таймери, PWM, АЦП/ЦАП | ✖ **діра** (є лише polling-vs-interrupts, DMA+АЦП) | → G3 |
| Шини: UART, I2C, SPI, CAN, USB | ✖ слабко (5 кроків; UART-теми немає) | → G4 |
| Прошивка: super-loop → FSM → RTOS | ✖ RTOS відсутній повністю | → G5 |
| Watchdog, reset, brown-out, safe-mode | ✖ діра | → G7 |
| Bootloader, партиції, NVS, OTA-клієнт | ✖ діра (є лише OTA-**сервер**) | → G6 |
| Живлення | ✔ найповніша | zhyvlennia (дрібні діри) |
| Сон і низьке споживання (основи) | ◐ (є аудити, нема основ) | → G21 |
| Давачі (основи, IMU-складові, енкодери) | ◐ | → G22, G12 |
| Дисплеї | ✔ достатньо | dyspleyi |
| DSP і керування | ✔ сильна | keruvannia (дрібні діри) |
| Зв'язок: модуляція, антени-основи, стек TCP/IP, IoT-протоколи | ◐ (радіоінженерія є, основ і MQTT/BLE нема) | → G10 |
| Мотори й приводи | ✖ **майже відсутня область** | → G9 |
| RC-керування (апаратура, S.BUS/CRSF) | ✖ діра | → G11 |
| GNSS | ✖ діра (лише hist-GPS) | → G12 |
| Політ-фізика мультикоптера | ✖ діра | → G23 |
| Автопілот: політні режими, arming, failsafe | ◐ (MAVLink/місії є, режимів нема) | → G23 |
| Edge-ML | ✔ | mk + drony |
| PCB-проєктування як процес | ◐ шматки | → G17 |
| Безпека: secure boot, шифрування, підписи | ◐ (лише TPM/TrustZone) | → G18 |
| Тести, git, CI | ◐ (git-flow без git-основ; CI нема) | → G19 |
| EMC, сертифікація, функційна безпека, регуляторка БпЛА | ✖ | → G24 (ПІЗН) |

---

## 3. Діри рівня «ціла область»

### G1. Мова C і основи програмування — найбільша діра курсу — **КРИТ**
Аудиторія «нуль програмування», але перший код з'являється у вставках (`proj-base-drive-firmware` у kola!) і власних статтях mk без жодного введення: у курсі ніде немає змінних, типів, розгалужень, циклів, функцій, масивів, рядків, структур, покажчиків, бітових операцій (без яких регістри МК читати неможливо).
**Готових refs немає** — `programming/languages` починається одразу з компіляції. Пропозиція: новий модуль «Мова C» (~12 кроків), як власні статті курсу або нові теми `book/programming/languages`:
- new: `c-first-program` (перша програма і як її запустити), `c-variables-types`, `c-operators-expressions`, `c-control-flow`, `c-functions`, `c-arrays-strings`, `c-structs-enums`, `c-pointers-intro`, `c-bit-operations` (строго перед GPIO-регістрами), `c-preprocessor-headers`, `c-modules-build`
- готові суміжні refs у той самий модуль: `programming/computer-architecture/bits-bytes-endianness` (done), `integer-types-c` (done), `overflow-wraparound` (done), `sign-extension` (done), `integer-promotion` (done), `fixed-point` (done), `floating-point` (done); `programming/systems/memory-as-array` (done), `addresses-pointers` (done)
**Місце:** новий модуль після цифрової логіки (G2), строго перед mk/proshyvka.

### G2. Цифрова логіка — ціла область відсутня — **КРИТ**
`cyfra-pamyat` стрибає з одного ref (`electronics/shift-register`) одразу в PAL→FPGA. Читач не бачив ні вентиля, ні тригера. Уся база готова в `electronics/digital` (done):
`why-digital`, `logic-levels-as-ranges`, `noise-margin`, `basic-gates`, `nand-nor`, `xor-comparison`, `cmos-gate`, `combinational-circuits`, `multiplexer`, `state-memory`, `sr-latch`, `d-flip-flop`, `edge-vs-level`, `register`, `clock-signal`, `counters`, `frequency-divider`, `finite-state-machines`, `metastability-timing`, `threshold-schmitt`, `twos-complement`, `logic-families`, `logic-74`, `level-shifter`, `hi-z-state` — усі (done); + `math/logic-foundations/boolean-algebra` (done).
**Місце:** нова секція «Цифрова логіка» між напівпровідниками і теперішньою cyfra-pamyat (FPGA-теми курсу стають її другою половиною; `synchronous-reset` курсу — туди ж).

### G3. Базова периферія МК: GPIO, переривання, таймери, PWM, АЦП — **КРИТ**
У курсі немає кроку «GPIO» (є одразу `pin-mux`), немає таймерів (є вимірювання частоти), немає PWM-периферії (є силовий `pwm-power-control`), немає АЦП-основ (є одразу `dma-adc`). Все готово (done, `programming/embedded-systems` якщо не вказано інше):
- **GPIO:** `microcontroller`, `memory-mapped-io`, `gpio-registers`; `electronics/digital/push-pull-output`, `open-drain`, `floating-pullups`, `pin-drive-limits`, `contact-debounce`, `esd-gpio-protection` (усі done)
- **Переривання:** `interrupts`, `isr`, `interrupt-priorities` (done); `programming/computer-architecture/interrupt-vector` (done); глибше: `nvic-cortex-m`, `critical-sections`, `interrupt-latency` (pending)
- **Таймери:** `timer-counter`, `timer-overflow`, `capture-compare`, `millis-micros`, `nonblocking-time`, `periodic-scheduling`, `rtc` (усі done)
- **PWM:** `pwm`, `hardware-pwm`, `pwm-resolution` (done)
- **АЦП/ЦАП:** `electronics/digital/adc`, `dac`, `sampling-quantization`, `adc-resolution`, `adc-types` (done); `electronics/metrology/adc-errors`, `voltage-reference` (done) — перед курсовими `adc-reference-calibration`, `usb-cc-adc-circuit`
- **Тактування:** `clock-power` (done), `peripheral-clock-enable`, `clock-tree` (pending)
**Місце:** розділи всередині mk («перша прошивка: GPIO» → «переривання» → «таймери/PWM» → «АЦП» → потім наявні DMA-теми). Сюди ж new: `first-blink-project` (перший наскрізний проєкт) — у курсі немає жодного «hello world» кроку.

### G4. Шини: UART / I2C / SPI (+CAN, USB) — **КРИТ**
`peryferiia` = 5 кроків на область, де книга (`communications/buses`) має 56 тем. **UART як тема відсутня взагалі** (є лише `usb-uart-bridge`), I2C/SPI подані тільки порівнянням `spi-vs-i2c`. Готові (done):
- **UART:** `communications/buses/async-serial`, `uart-frame`; `communications/synchronization/baud-rate`; `electronics/digital/ttl-rs232`
- **I2C:** `i2c-bus`, `i2c-addressing`, `start-stop-ack`, `i2c-transaction`, `register-map` (потім наявний курсовий `pullup-resistor-design`)
- **SPI:** `spi-bus`, `spi-lines`, `cpol-cpha`, `chip-select`, `spi-speed`
- **CAN/DroneCAN** (для дронової частини — ВАЖЛ): `can-arbitration`, `can-frame-errors`, `dronecan` (pending)
- **USB-пристрій** (ВАЖЛ): `programming/peripherals/usb-overview`, `usb-physical`, `usb-enumeration`, `usb-endpoints`, `usb-device-classes`, `esp32-usb`, `tinyusb-device`, `usb-host` (усі done)
- 1-Wire (DS18B20/DHT): немає ніде → new: `communications/buses/one-wire` — ПІЗН.

### G5. RTOS і багатозадачність — область відсутня — **КРИТ**
Курс має `super-loop-limits` (глухий кут показано) і `spinlock-mutex` (примітив без контексту), але самого RTOS немає. Готові (done): `programming/embedded-systems/freertos`, `realtime-determinism`; `programming/systems/tasks`, `scheduler`, `task-ipc` (черги/семафори), `task-stacks`, `atomicity-races`, `dma-cache-races`. Розширення (pending): `task-states`, `task-priorities`, `context-switch`, `priority-inversion`, `event-groups`, `task-notification`, `freertos-heap`, `wcrt-analysis`.
**Місце:** новий розділ «Багатозадачність» після `super-loop-limits`; курсові `spinlock-mutex`, `memory-safety`, `error-propagation-patterns` — у нього.

### G6. Bootloader, Flash-система, NVS, OTA-клієнт — **КРИТ**
Курс має `esptool-workflow`, `fatfs-integration`, `boot-time-budget` і… `ota-server` (серверний бік без клієнтського!). Відсутній весь системний шар — готові (done): `programming/embedded-systems/bootloader`, `flashing`, `why-persist`, `flash-internals`, `wear-leveling`, `partition-table`, `nvs`, `write-integrity`, `ota-slots`, `ota-update`; (pending): `ota-rollback`, `delta-ota`, `flash-filesystem`, `mcu-startup-sequence`, `vector-table`, `linker-script`.
**Місце:** розділ «Пам'ять і оновлення» у proshyvka/mk; `ota-server` курсу — після `ota-update`.

### G7. Watchdog і надійність виконання — **КРИТ**
Канон embedded, у курсі немає: `programming/embedded-systems/watchdog` (done), `reset-causes` (done), `brownout` (done), `safe-mode` (done), `reboot-strategy` (done), `reboot-counter` (done), `graceful-degradation` (done), `hardfault` (done). Курсові `reset-sequence`, `core-dump`, `fault-injection-testing`, `fmea-embedded` отримають фундамент.

### G8. Тулчейн, образ прошивки, карта пам'яті — **КРИТ**
Курсові `memory-budget-mcu`, `addr2line-workflow`, `openocd-gdb` висять без бази «як текст стає прошивкою»: `programming/languages/compilation` (done), `compiler-stages` (done), `linking` (done), `volatile` (done); `programming/systems/memory-map` (done), `flash-vs-ram` (done), `stack-lifo` (done), `heap-dynamic-memory` (done), `stack-overflow` (done), `firmware-image` (done), `c-runtime` (done); (pending): `toolchain`, `elf-image`, `linker-script`, `startup-code`. Налагодження: `why-debugger`, `breakpoints-watchpoints`, `step-debugging`, `swd-jtag-internals`, `semihosting`, `rtt`, `trace-itm-swo`, `debug-vscode` (усі done) — перед/довкола курсових `jtag-swd-tools`, `openocd-gdb`.

### G9. Мотори й приводи — майже відсутня область — **КРИТ** (це курс про автономні системи)
У курсі: `bjt-load-driving`, `pwm-power-control`, `servo-sizing`, `esc-bldc-driver`, `output-mixing` — а самих моторів немає. Готові (done): `electronics/electromechanics/brushed-dc-motor`, `gearmotor`, `bldc-motor`, `stepper-motor`, `hobby-servo`, `servo`, `solenoid-relay`, `relay-driver`, `motor-current-stall-heat`, `gears-transmission`; `electronics/power-electronics/h-bridge`, `dc-motor-driver`, `gate-driver` (done). Енкодери: `electronics/sensors/optical-incremental-encoder` (done), `quadrature`, `hall-magnetic-encoders` (pending). Глибше (pending): `foc-control`, `back-emf`, `closed-loop-stepper`, `pwm-servo-protocol`.
**Місце:** нова секція «Мотори й привід» між zhyvlennia/PWM і drony.

### G10. Зв'язок: основи перед радіоінженерією — **КРИТ→ВАЖЛ**
`zvyazok` стартує одразу з маршрутизації, надійності даних і FHSS-під-глушінням. Бракує сходинок (усі done, якщо не вказано):
- **Модуляція:** `communications/modulation/why-modulation`, `am-fm`, `fsk-psk`, `spread-spectrum` — строго перед `jamming-fhss`
- **Антени-основи:** `communications/antennas/antenna`, `resonance-dipole`, `antenna-gain`, `antenna-polarization` — перед `esp32-antenna`/`link-budget`
- **Коди/CRC:** `communications/coding-theory/parity-bit`, `checksums`, `crc`, `hamming-distance`, `hamming-code` — перед `data-reliability`
- **Стек мереж:** `communications/networks/channel-band-packet`, `mac-ip-arp`, `latency-reliability`, `bandwidth-loss`; `communications/protocols/tcp-vs-udp`; `programming/networking/sockets-tcp-udp`; (pending: `dhcp-dns`, `nat`, `wpa-security`)
- **Wi-Fi/BLE як кроки:** `communications/networks/wifi`, `bluetooth-spp`, `communications/protocols/ble-gatt` (done) — курс на ESP32 без жодного Wi-Fi/BLE-кроку (лише `wifi-fast-connect` у mk і `802-11-versions`)
- **IoT-протоколи:** `communications/protocols/mqtt` (done, detailed теж done!), `programming/networking/web-server-mcu` (done), `packet-design`, `flow-control`, `reliable-link` (done) — перед курсовим `rpc-embedded`
- **Телеметрія/MAVLink базіс:** `communications/protocols/control-telemetry`, `telemetry-stream`, `rc-link`, `mavlink-packet` (done) — перед курсовими `mavlink-from-ground`/`mavlink-commands`

### G11. RC-керування — **КРИТ для drony**
FPV/дрон-курс без теми «RC-апаратура і протоколи приймача»: `communications/protocols/rc-link` (done); (pending): `rc-signal-protocol` (PWM/PPM/S.BUS), `crsf-protocol`, `rc-failsafe-modes`, `communications/radio-engineering/elrs-architecture`. Місце: drony, перед `output-mixing`.

### G12. GNSS — **ВАЖЛ**
GPS у курсі існує лише як історична вставка `hist-gps`. Ref: `communications/synchronization/gnss` (done); глибше (pending): `pps-pulse`, `sbas-corrections`, `algorithms/signal-robotics/rtk-integer-ambiguity`. Місце: davachi (поруч `onboard-sensors`) — перед `inertial-navigation`/`slam-navigation` у keruvannia.

### G13. Інструменти й перша практика новачка — **КРИТ**
Перший вимірювальний крок курсу — осцилограф у §9. Новачку треба на старті (після kola): `electronics/metrology/multimeter` (done), `lab-power-supply` (done), `measurement-errors` (done), `min-typ-max` (done), `oscilloscope` (done, зараз неявно через `sine-on-scope`), `logic-analyzer` (done); (pending): `basic-soldering`, `first-power-up-check`, `fault-finding`, `electronics/pcb/datasheet-pinout`, `cables-connectors`; new: `breadboard-prototyping` (макетка — теми немає в жодній книзі). Сюди ж new: `si-units-prefixes` або ref `physics/mechanics/si-base-units` (pending) — мілі/мікро/кіло на самому початку.

### G14. Напівпровідники: фізика і транзистор зсередини — **КРИТ**
Секція `napivprovidnyky` починається з ESD і не вводить ані PN-переходу, ані транзистора, — а `kola` вже ганяє BJT/MOSFET. Готові (done): `physics/condensed-matter-physics/conductors-insulators`, `doping`, `pn-junction`; `electronics/components/diode-bias`, `diode-iv-curve`; `electronics/microelectronics/bjt`, `bjt-structure`, `mosfet-structure`, `mosfet-threshold`, `nmos-pmos`, `cmos`, `body-diode`; `electronics/optoelectronics/led`, `led-photodiode`, `optocoupler`. (pending: `band-theory` — глибше.)
Це водночас лікує «ламаний порядок»: транзисторні теми kola зможуть переїхати ПІСЛЯ введеного транзистора.

### G15. Аналогова база: AC-кола, RC-фільтри, ОП, 555 — **КРИТ**
Курс має каскади, топології ЗЗ і однополярний ОП — але не має жодного кроку «що таке ОП» чи «RC-ФНЧ». Готові (done, `electronics/analog`): `reactance`, `capacitive-reactance`, `inductive-reactance`, `rc-low-pass`, `rc-high-pass`, `rc-filter`, `lc-resonance`, `series-resonance`, `parallel-resonance`, `ac-coupling`, `comparator`, `opamp`, `ideal-opamp`, `inverting-noninverting`, `real-opamp-limits`, `schmitt-trigger`, `opamp-integrator-differentiator`, `relaxation-oscillator`, `555-internals`, `555-astable`, `555-monostable`, `pierce-oscillator` (перед курсовим `pierce-oscillator-design`).

### G16. Процесор зсередини — **ВАЖЛ**
`mk` стартує з фон Неймана/RISC-CISC без «що таке процесор». Готові (done, `programming/computer-architecture`): `what-is-processor`, `processor-parts`, `fetch-decode-execute`, `isa`, `clock-frequency`, `pipeline`, `cache`, `mcu-blocks` (склад МК).

### G17. PCB-проєктування як процес — **ВАЖЛ**
Є фрагменти (тепло, монтаж, антена, транс-лінії), нема наскрізного «схема → розміщення → трасування → земля → DFM → замовлення». Refs: `electronics/pcb/common-ground` (done), `ground-loops` (done), `shielding` (done), `packaging` (done); (pending): `eda-tools`, `ground-plane`, `current-return-path`, `pcb-stackup-rf`, `creepage-clearance`, `thermal-vias`; new: `pcb-layout-flow` (наскрізний процес, якщо не збирати з pending).

### G18. Безпека пристрою — **ВАЖЛ**
У курсі лише `tpm-trustzone` + `memory-safety`. Готово: `programming/security/secure-boot` (done). (pending): `programming/embedded-systems/flash-encryption`, `nvs-encryption`, `ota-image-signing`; `programming/security/buffer-overflow-security`, `aes-xts`; `communications/networks/wpa-security`, `communications/protocols/ble-security`, `mavlink-v2-signing`, `communications/cryptographic-comm/mavlink-security`. TLS на МК — немає ніде → new: `tls-embedded` (важливо для OTA/MQTT).

### G19. Git-основи, тести, CI — **ВАЖЛ**
Курс має `gitflow-branching` без введення git: `programming/code/version-control` (pending — треба написати або зробити власний крок). Готові refs: `programming/software-engineering/static-analysis` (done), `assert-panic` (done), `defensive-programming` (done), `fuzzing` (done), `sitl-simulation` (done — курс ніде не реферить SITL, хоч для дронів це канон). Немає ніде → new: `firmware-ci` (CI для прошивки: build-matrix, артефакти), `hil-testing` (hardware-in-the-loop).

### G20. Структури даних прошивки — **ВАЖЛ**
Кільцевий буфер — канон UART/DMA, у курсі відсутній: `algorithms/data-structures/ring-buffer` (pending), `queue-fifo` (pending); `programming/embedded-systems/stream-parser` (done), `state-machine-embedded` (pending; базовий FSM є як `electronics/digital/finite-state-machines` done), `driver-pattern` (pending), `data-serialization` (pending), `programming/software-engineering/lookup-table` (pending).

### G21. Сон і низьке споживання: основи — **ВАЖЛ**
Курс має аудити (`board-consumption`, `sleep-current-audit`, `duty-cycle-current`) без основ: `programming/embedded-systems/sleep-modes` (done), `wakeup-sources` (done), `battery-budget` (done), `current-paths` (done), `ulp-coprocessor` (done), `rtc-memory` (done), `clock-power` (done).

### G22. Давачі: основи й пропущені класи — **ВАЖЛ**
`davachi` стартує одразу з далекомірів. Основи (done): `electronics/sensors/what-is-a-sensor`, `transducer-classes`, `sensor-characteristics`, `drift-hysteresis-noise`, `sensor-input-matching`, `mems`, `accelerometer`, `gyroscope`, `magnetometer`, `imu`, `imu-noise-bias-drift` — перед курсовим `imu-barometer`. Пропущені класи: `ntc-thermistor` (done), `photo-sensors` (done), `environment-sensors` (done), енкодери (G9), давач струму `electronics/metrology/current-monitor` (done), камера як давач: `electronics/optoelectronics/image-sensor` (done), `rolling-shutter` (done) — перед `isp-pipeline` у drony.

### G23. Політ-фізика і автопілот — **ВАЖЛ**
Як дрон літає — фізики немає; теми вже заведені в book (усі pending): `physics/mechanics/thrust-vs-weight`, `reaction-torque`, `frame-configurations`, `propeller-geometry`, `fixed-wing-lift`, `vtol-transition`. Автопілот як система (done): `programming/embedded-systems/flight-controller`, `ardupilot-layers`, `params-gcs`, `failsafe`, `redundancy`, `fc-vs-companion`; (pending): `manual-stabilized-modes`, `position-modes`, `arming-checks`, `geofence`, `first-bringup`. Каскад стабілізації (done): `algorithms/signal-robotics/instability-stabilization`, `roll-pitch-yaw-control`, `stabilization-cascade`, `motor-mixer` — опора для курсових `output-mixing`/`attitude-estimation`. Зауваження меж: `autonomous-system`, `mission-planning`, `mavlink-commands`, `mission-planner-qgc` зараз лежать у секції «МК» — за змістом це drony.

### G24. Пізніше (свідомо відкласти, але тримати в плані)
- **EMC/сертифікація:** `electronics/pcb/electromagnetic-compatibility` (pending), `cable-emi` (pending), `communications/radio-engineering/emc-certification` (pending), `communications/protocols/regulatory-radio-certification` (pending), `electronics/metrology/measurement-safety-cat` (pending)
- **Ethernet/PoE:** `programming/embedded-systems/ethernet-on-mcu` (done), `communications/networks/ethernet-frame`, `poe` (pending)
- **Аудіо:** `electronics/electromechanics/microphone-speaker` (done), `communications/buses/i2s-bus` (pending), `electronics/sensors/mems-microphone` (pending)
- **GUI/фреймбуфер:** new: `framebuffer-rendering`, `lvgl-gui`
- **Час/RTC-годинник:** `programming/embedded-systems/rtc` (done), `uptime-clock-sync` (pending), `communications/protocols/ntp-sync` (pending)
- **Функційна безпека / регуляторка БпЛА:** немає ніде → new: `functional-safety-intro` (IEC 61508/DO-178 оглядово), `drone-regulations` — ПІЗН
- **1-Wire** (див. G4), **CAN глибше**, **Modbus** `communications/buses/modbus` (pending) — індустріальний кут, ПІЗН.

---

## 4. Точкові діри всередині наявних секцій

| Секція | Відсутній крок | Ref / new | Пріоритет |
|---|---|---|---|
| komponenty | Кварцовий резонатор (перед `tcxo-ocxo`, `ceramic-mems-resonators` і `pierce-oscillator-design` у kola) | `electronics/components/crystal` (done), `quartz-resonator` (done), `quartz-rlc-model` (done) | КРИТ |
| komponenty | Кнопка/перемикач + брязкіт | `electronics/digital/contact-debounce` (done) | КРИТ |
| komponenty | LED як перший вихід | `electronics/optoelectronics/led` (done), `addressable-leds` (done — ВАЖЛ до `led-animation-patterns`) | КРИТ |
| komponenty | Реле як компонент | `electronics/electromechanics/solenoid-relay`, `relay-driver` (done) | ВАЖЛ |
| komponenty | Оптопара/ізоляція | `electronics/optoelectronics/optocoupler` (done) | ВАЖЛ |
| zhyvlennia | Заряджання Li-ion (є хімії, BMS — а заряду нема) | `electronics/power-electronics/li-ion-charger` (done), `lipo-swelling-chemistry` (done) | ВАЖЛ |
| zhyvlennia | Розв'язувальний конденсатор як крок (перед `power-supply-filtering`) | `electronics/components/decoupling` (done) | КРИТ |
| zhyvlennia | LDO/buck/boost поіменно (перед `topology-map`/`linear-vs-switching`) | `electronics/power-electronics/ldo`, `buck`, `boost`, `buck-boost` (done) | ВАЖЛ |
| napivprovidnyky | Секція різношерста: flash-теми (`nor-vs-nand`, `eeprom-fram`, `mram-rram-pcm`) — це «пам'ять», `power-fail-safety` — прошивка/живлення; самих напівпровідникових основ нема (G14) | — | ВАЖЛ (межі) |
| proshyvka | git-основи перед `gitflow-branching` | `programming/code/version-control` (pending) | ВАЖЛ |
| proshyvka | Логування/printf-канал; глибше налагодження | `programming/embedded-systems/semihosting`, `rtt`, `trace-itm-swo` (done) | ВАЖЛ |
| keruvannia | Комплементарний фільтр + злиття давачів (перед `attitude-estimation`, `kalman-filter`) | `algorithms/signal-robotics/complementary-filter` (done), `sensor-fusion` (done), `kalman-ekf` (done — після курсового `kalman-filter`) | ВАЖЛ |
| keruvannia | FFT як опора `why-frequency-domain` | `algorithms/signal-robotics/fft` (done), `fir-filter`/`iir-filter` (done — дублюють курсовий `fir-vs-iir`, узгодити) | ПІЗН |
| zvyazok | MQTT, веб-сервер на МК, BLE GATT (ESP32-курс!) | `communications/protocols/mqtt` (done+done), `programming/networking/web-server-mcu` (done), `ble-gatt` (done) | КРИТ/ВАЖЛ |
| zvyazok | LoRa поіменно (є LPWAN-огляд) | `communications/radio-engineering/lora` (done) | ПІЗН |
| drony | Камера як давач перед `isp-pipeline` | `electronics/optoelectronics/image-sensor`, `cmos-matrix`, `rolling-shutter` (done) | ВАЖЛ |
| drony | CV-базис перед `model-zoo`/`stereo-vision` (davachi) | `algorithms/computer-vision/image-as-data`, `convolution-filters`, `edge-detection`, `object-detection`, `tracking`, `compute-cost` (усі done+detailed done) | ВАЖЛ |
| mk | Edge-ML базис перед `edge-inference` | `algorithms/machine-learning/what-is-ml`, `train-vs-inference`, `neuron-layer`, `cnn`, `tinyml` (done) | ВАЖЛ |

---

## 5. Зведення пріоритетів

**Критично-для-новачка (без цього курс не «з нуля»):**
1. **G1 Мова C** — ціла область, refs немає, ~12 нових статей (найбільший обсяг нового письма).
2. **G2 Цифрова логіка** — ціла область, ~20 готових done-refs, письма не треба.
3. **G14 Напівпровідники-основи** + **G15 Аналогова база (AC, RC-фільтри, ОП, 555)** — ~35 готових refs; водночас лагодять зламаний порядок kola.
4. **G3 GPIO/переривання/таймери/PWM/АЦП** — ~25 готових refs + new `first-blink-project`.
5. **G4 UART/I2C/SPI** — ~15 готових refs (UART зараз відсутній як клас).
6. **G8 Тулчейн/карта пам'яті** + **G16 процесор** — ~18 готових refs.
7. **G5 RTOS**, **G6 bootloader/NVS/OTA-клієнт**, **G7 watchdog/reset** — ~25 готових refs.
8. **G9 Мотори й приводи**, **G10 радіо/мережі-основи (модуляція, антени, CRC, Wi-Fi/BLE/MQTT)**, **G11 RC-лінк**, **G13 інструменти й перша практика** — переважно готові refs + кілька pending/new.

**Важливо:** G12 GNSS; G17 PCB-flow; G18 безпека (secure-boot done); G19 git/CI/SITL; G20 ring buffer/FSM; G21 сон-основи; G22 давачі-основи; G23 політ-фізика (теми вже заведені pending у physics/mechanics); USB-пристрій; CAN/DroneCAN; точкові діри §4.

**Пізніше:** EMC/сертифікація, Ethernet/PoE, аудіо/I2S, GUI/LVGL, NTP/час, функційна безпека, регуляторка БпЛА, 1-Wire, Modbus.

**Головний важіль:** курс не використовує жодної статті книг `programming/` (177 готових embedded-тем), `algorithms/`, `math/` — більшість критичних дір закривається **готовими done-refs без нового письма**; нового письма вимагає насамперед модуль «Мова C» (G1) і поодинокі new-теми (макетка, TLS, CI/HIL, PCB-flow, регуляторка).

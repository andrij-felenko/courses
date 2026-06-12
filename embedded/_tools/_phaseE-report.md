# Phase E — фінальний звіт

## Полагоджені биті лінки

- hist-mosfet.md: mosfet.md -> ../bjt/bjt.md (посилання «Розділ 2.6» про біполярний транзистор вело на поточний розділ замість розділу BJT)
- hist-cmos.md: mosfet.md -> hist-mosfet.md (посилання «історія до розділу» про те, як FET чекав на матеріали, вело на головний файл розділу замість історичної вставки про MOSFET)
- graphics-pipeline.md: `r02-s1-history-alto.md` -> `hist-alto.md` (битий вказівник на наявний файл історії в тій самій теці; справжнє ім'я з _status.md)
- graphics-pipeline.md: `r02-s2-m-rgb565.md` -> `math-rgb565.md` (вирівняно під заплановане ім'я ⬜-вставки з _status.md, бо старе ім'я не зрезолвиться ніколи)
- graphics-pipeline.md: `r02-s3-a-bresenham.md` -> `proj-bresenham.md` (вирівняно під заплановане ім'я ⬜-вставки з _status.md)
- graphics-pipeline.md: `r02-s4-a-font-render.md` -> `proj-font-render.md` (вирівняно під заплановане ім'я ⬜-вставки з _status.md)

## Додані крос-лінки

- math-vectors.md: координати (components) -> book:math/vector-components
- math-vectors.md: додавання стрілок (правило голова-до-хвоста/паралелограм) -> book:math/vector-addition
- math-work-integral.md: інтеграл (площа під кривою) -> book:math/integral
- math-gradient.md: похідна (нахил вздовж осі) -> book:math/derivative
- voltage-current-conduction.md: шунт -> book:components/shunt-current-monitor (§1.2.1, опис амперметра через шунт)
- voltage-current-conduction.md: фоторезистор -> book:components/light-sensors (§1.2.8, давачі від освітлення)
- voltage-current-conduction.md: NTC-терморезистори -> book:components/ntc-thermistor (§1.2.10, давачі температури)
- resistance-power-heat.md: похідну (Фур'є §1.3.10, 🧮-нота) -> book:math/derivative
- kirchhoff-circuit-analysis.md (§1.4.6 читання давачів): термістор -> book:components/ntc-thermistor
- kirchhoff-circuit-analysis.md (§1.4.6 читання давачів): фоторезистор/LDR -> book:components/light-sensors
- kirchhoff-circuit-analysis.md (§1.4.9 ряд.712): інструментальний підсилювач -> book:components/instrumentation-amp
- math-matrix-machine.md (ряд.43, §5.8.1): матрицями повороту -> book:math/rotation-matrices
- math-derivative-max.md: похідну -> book:math/derivative
- equivalent-circuits.md: похідну (§1.5.6) -> book:math/derivative
- math-accuracy.md: переносити похибки -> book:math/error-budget
- schematics-measurement.md (§1.6.8): усереднення випадкової похибки -> book:math/averaging-gain
- math-cross-product.md: скалярний добуток -> book:math/dot-product
- math-hysteresis-loop.md: інтеграл (∮ H dB) -> book:math/integral
- proj-biot-savart.md: інтеграл -> book:math/integral
- comp-clamp-meter.md: шунтовий амперметр -> book:components/shunt-current-monitor
- comp-clamp-meter.md: давачі струму на ефекті Холла -> book:components/hall-current-sensor
- reactance-resonance.md: фазорна діаграма (§2.3.4) -> book:math/phasors
- math-risetime-bandwidth.md: "теорія згорток" -> book:math/convolution
- comp-input-rc.md: "термістор" -> book:components/ntc-thermistor
- diode-pn-junction.md: Термістор -> book:components/ntc-thermistor
- diode-pn-junction.md: Фоторезистор -> book:components/light-sensors
- math-gate-charge.md: інтеграл -> book:math/integral
- math-square-law.md: Продиференціювавши (gm = dId/dVgs) -> book:math/derivative
- comp-h-bridge-board.md: Драйвер мотора -> book:components/dc-motor-driver
- opamp-comparator.md: вимірювальні підсилювачі (§2.8.6) -> book:components/instrumentation-amp
- opamp-comparator.md: інтегрувати (§2.8.6 натяк) -> book:math/integral
- opamp-comparator.md: диференціювання (§2.8.6 натяк) -> book:math/derivative
- math-noise-budget.md: бюджет похибки -> book:math/error-budget
- proj-light-threshold.md: фототранзистор -> book:components/light-sensors
- reading-datasheets.md: TVS-діод -> book:components/tvs-esd
- comp-abs-max-failures.md: TVS-діод -> book:components/tvs-esd
- math-tolerance-statistics.md: міра розкиду (σ / стандартне відхилення) -> book:math/mean-variance
- comp-tcxo.md: GNSS (приймачах GNSS) -> book:components/gnss-module
- comp-tcxo.md: термісторів (аналоговий TCXO) -> book:components/ntc-thermistor
- resonators-references.md: GPS-приймачі (§2.10.9) -> book:components/gnss-module
- proj-measure-drift.md: регресію (буфер точок під регресію) -> book:math/least-squares
- ac-power-switching.md: «Інтегруючи синусоїду в квадраті» (§2.11.4) -> book:math/integral
- math-phase-power.md: «інтеграл миттєвої потужності» (розд. «Апарат») -> book:math/integral
- comp-inamp-bridge.md: Інструментальний підсилювач -> book:components/instrumentation-amp
- legendary-analog-ics.md: інструментальним підсилювачем (§2.12.7 intro) -> book:components/instrumentation-amp
- logic-levels.md: σ·√N (накопичення шуму) -> book:math/mean-variance
- logic-levels.md: зсувач рівнів -> book:components/level-shifter
- comp-74-families.md: 8-бітний зсувний регістр (74595) -> book:components/shift-register
- proj-cordic.md: обертати вектор -> book:math/rotation-matrices
- math-phasor.md: формула Ейлера -> book:math/euler-formula
- hist-steinmetz.md: формула Ейлера -> book:math/euler-formula

## Створені стаби

### math

- vector-analysis/_status.md — Розділ 2.6 «Градієнт» · `vector-analysis/gradient/`
- vector-analysis/_status.md — Розділ 2.7 «Векторний добуток (cross product)» · `vector-analysis/cross-product/`
- trigonometry-phasors/_status.md — Розділ 3.5 «Діюче значення (RMS)» · `trigonometry-phasors/rms/`
- trigonometry-phasors/_status.md — Розділ 3.6 «Децибели: логарифмічна міра відношень (дБ)» · `trigonometry-phasors/decibels/`
- trigonometry-phasors/_status.md — Розділ 3.7 «Геометрія тріангуляції: подібні трикутники й d = f·b/x» · `trigonometry-phasors/triangulation/`
- trigonometry-phasors/_status.md — Розділ 3.8 «Фазовий ToF: фазовий зсув, заплутування фази й неоднозначна дальність» · `trigonometry-phasors/phase-tof/`
- calculus/_status.md — Розділ 4.5 «Ряд Фур'є» · `calculus/fourier-series/`
- calculus/_status.md — Розділ 4.6 «Перетворення Фур'є: розклад сигналу на частоти (косинусні хвилі)» · `calculus/fourier-transform/`
- linear-algebra/_status.md — Розділ 1.5 «Поле Галуа GF(2)» · `linear-algebra/galois-field-gf2/`
- linear-algebra/_status.md — Розділ 1.6 «Код Рід–Соломона» · `linear-algebra/reed-solomon/`
- linear-algebra/_status.md — Розділ 1.7 «CRC: циклічний надлишковий код» · `linear-algebra/crc-checksum/`
- linear-algebra/_status.md — Розділ 1.8 «Циклічний надлишковий код (CRC): ділення за модулем 2» · `linear-algebra/crc-cyclic-redundancy/`
- linear-algebra/_status.md — Розділ 1.9 «Криві Безьє» · `linear-algebra/bezier-curves/`
- statistics-errors/_status.md — Розділ 5.6 «Теорема Шеннона (межа пропускної здатності каналу)» · `statistics-errors/shannon-theorem/`
- statistics-errors/_status.md — Розділ 5.7 «Межа Шеннона-Гартлі (C = B·log2(1+S/N))» · `statistics-errors/shannon-hartley-limit/`
- statistics-errors/_status.md — Розділ 5.8 «Фільтр Кальмана» · `statistics-errors/kalman-filter/`
- statistics-errors/_status.md — Розділ 5.9 «Коваріація та коваріаційна матриця» · `statistics-errors/covariance-matrix/`

### components

- sensors/_status.md — Розділ 1.10 «I2S MEMS-мікрофон (INMP441-клас)» · `sensors/i2s-mic/`
- sensors/_status.md — Розділ 1.11 «PIR-модуль руху (HC-SR501-клас): піроелемент і лінза Френеля» · `sensors/pir-module/`
- sensors/_status.md — Розділ 1.12 «IR-тріангуляційний далекомір (Sharp GP2Y-клас): нелінійний аналоговий вихід» · `sensors/sharp-ir-rangefinder/`
- sensors/_status.md — Розділ 1.13 «IR-давач перешкоди й лінії (TCRT5000-клас): фотопара, поріг, контраст» · `sensors/ir-obstacle-line/`
- sensors/_status.md — Розділ 1.14 «Барометр (давач тиску/висоти)» · `sensors/barometer-sensor/`
- sensors/_status.md — Розділ 1.15 «Магнітометр (електронний компас)» · `sensors/magnetometer-compass/`
- sensors/_status.md — Розділ 1.16 «Термопарний (ІЧ) давач горизонту» · `sensors/thermopile-horizon-sensor/`
- power/_status.md — Розділ 2.5 «Силовий дросель (power inductor)» · `power/power-inductor/`
- power/_status.md — Розділ 2.6 «Трансформатор» · `power/transformer/`
- power/_status.md — Розділ 2.7 «IGBT (біполярний транзистор з ізольованим затвором)» · `power/igbt/`
- power/_status.md — Розділ 2.8 «Джерело опорної напруги (бандгап/стабілітрон)» · `power/voltage-reference/`
- power/_status.md — Розділ 2.9 «TL431 — програмований стабілітрон» · `power/tl431-shunt-regulator/`
- power/_status.md — Розділ 2.10 «Bandgap-джерело опорної напруги» · `power/bandgap-reference/`
- power/_status.md — Розділ 2.11 «Load switch (high-side ключ живлення)» · `power/load-switch/`
- power/_status.md — Розділ 2.12 «BMS (Battery Management System)» · `power/bms-board/`
- power/_status.md — Розділ 2.13 «Анти-іскровий роз'єм (м'який старт)» · `power/anti-spark-connector/`
- comms/_status.md — Розділ 3.4 «Фазове автопідстроювання частоти (PLL)» · `comms/pll/`
- comms/_status.md — Розділ 3.5 «Варікап (варакторний діод)» · `comms/varactor-diode/`
- actuators/_status.md — Розділ 4.6 «Пара Дарлінгтона (складений транзистор)» · `actuators/darlington-pair/`
- actuators/_status.md — Розділ 4.7 «Твердотільне реле (SSR)» · `actuators/solid-state-relay/`
- actuators/_status.md — Розділ 4.8 «ESC — регулятор обертів безколекторного мотора» · `actuators/brushless-esc/`
- interfaces/_status.md — Розділ 6.4 «Компаратор-мікросхема (LM393/LM339)» · `interfaces/comparator-ic/`
- interfaces/_status.md — Розділ 6.5 «Тригер Шмітта (мікросхема, 74HC14)» · `interfaces/schmitt-trigger-ic/`
- interfaces/_status.md — Розділ 6.6 «Таймер 555 (NE555/TLC555)» · `interfaces/timer-555/`
- interfaces/_status.md — Розділ 6.7 «Аналоговий мультиплексор/ключ 4051/4066» · `interfaces/analog-mux-4051/`
- interfaces/_status.md — Розділ 6.8 «SPI TFT-дисплей (ILI9341/ST7789-клас)» · `interfaces/spi-display/`
- interfaces/_status.md — Розділ 6.9 «Зовнішній RTC-модуль з alarm-виходом (DS3231/PCF8563)» · `interfaces/rtc-module/`
- interfaces/_status.md — Розділ 6.10 «USB-UART міст (CP210x / CH340 / FT232)» · `interfaces/usb-uart-bridge/`
- protection/_status.md — Розділ 7.4 «Варистор (MOV)» · `protection/varistor-mov/`
- protection/_status.md — Розділ 7.5 «Феритова намистина / EMI-бусина» · `protection/ferrite-bead/`

## Поверхневі 🧮 — на переписування Opus-глибоко

_(жодного)_

## Примітки

- Усі 46 понять зі вхідного JSON отримали стаби; дублікатів за slug не виявлено (перевірено `grep` по всіх `_status.md`).
- Концептуальні дублі з різними slug додано як окремі стаби (умова «не дублюй за slug»): `crc-checksum` + `crc-cyclic-redundancy` (обидва — CRC, GF(2)-ділення за модулем 2); `voltage-reference` + `bandgap-reference` (обидва — джерело опорної напруги). Варто пізніше об'єднати чи перехресно злінкувати.
- `brushless-esc` віднесено до сектора actuators (регулятор обертів мотора — привод), а не comms.
- `usb-uart-bridge` віднесено до interfaces (дротовий host-міст), а не comms (де згруповано бездротові модулі).
- `decibels` віднесено до trigonometry-phasors як логарифмічна міра амплітуди/потужності сигналу — найближча наявна секція; жодна секція не пасує ідеально.
- Цей звіт замінює попередню чернетку Phase E з порожнім входом (`[]`); крос-лінки `euler-formula` з тієї чернетки збережено.

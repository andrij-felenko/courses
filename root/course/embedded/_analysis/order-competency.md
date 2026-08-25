# Компетентності випускника — аудит курсу guide/embedded «від кінця»

Метод: чотири цільові сценарії розкладено на конкретні вміння; кожне вміння зіставлено з темами маніфесту (`E:/develop/courses/guide/embedded/manifest.js`, 14 секцій). Позначення: **✔** — покрито, **◐** — частково, **✘** — нема покриття. Посилання: `ref:<книга>/<slug>`, `own:<slug>` (точно як у маніфесті), пропозиції — `new:<slug>`.

Секції курсу в поточному порядку: 1 `osnovy` → 2 `kola` → 3 `komponenty` → 4 `napivprovidnyky` → 5 `cyfra-pamyat` → 6 `zhyvlennia` → 7 `mk` → 8 `peryferiia` → 9 `proshyvka` → 10 `davachi` → 11 `dyspleyi` → 12 `keruvannia` → 13 `zvyazok` → 14 `drony`.

---

## Сценарій А. Прилад з нуля: датчик + МК + батарея + прошивка + корпус

| # | Вміння | Покриття | Теми / чого бракує |
|---|--------|----------|--------------------|
| А1 | Сформулювати вимоги/ТЗ на пристрій | ◐ | `own:power-spec-template` (zhyvlennia) — лише вузол живлення. Нема ТЗ на пристрій цілком: `new:device-requirements-spec` |
| А2 | Скласти блок-схему/архітектуру пристрою | ✘ | Нема кроку «системна архітектура: блоки, інтерфейси, дерево живлення як частина» — `new:system-block-diagram`. Дотично `own:power-tree-reading` |
| А3 | Обрати МК під задачу | ✔ | `own:mcu-selection`, `own:mcu-checklist`, `own:esp32-vs-8bit`, `own:esp32-family` (mk); `own:datasheet-mcu` (komponenty) |
| А4 | Обрати датчик під задачу (тип, інтерфейс, точність, струм) | ◐ | davachi дає конкретні класи (`own:contactless-distance`, `own:imu-barometer`, `ref:electronics/load-cell`), але нема оглядового «як обрати давач» і нема побутових класів: температура/вологість/освітленість — `new:sensor-selection`, `new:temperature-humidity-sensors` |
| А5 | Намалювати власну схему в EDA | ◐ | `own:reading-schematics` (+comp-eda-schematic-capture), `own:net-labels-buses` (pending) — читання є, власне креслення лише у вставці. `new:schematic-capture-practice` |
| А6 | Розрахувати живлення від батареї (вибір хімії, стабілізатор, бюджет) | ✔ | `own:battery-chemistries`, `own:topology-map`, `own:linear-vs-switching`, `own:board-consumption`, `own:power-budget`, `own:sleep-current-audit` (zhyvlennia) |
| А7 | Зарядка одної Li-ion комірки в пристрої (charger IC, fuel gauge) | ◐ | `own:fast-charging-protocols` (протоколи), `own:bms-architecture` (великі пакети). Нема простого «зарядний вузол малого пристрою: TP4056/BQ, fuel gauge» — `new:single-cell-charger` |
| А8 | Зібрати прототип на макетці/perfboard | ✘ | Слова «макетка/breadboard» у курсі відсутні. Для новачка це перший фізичний крок — `new:breadboard-prototyping` |
| А9 | Розвести плату: шари, полігони, DRC, gerber, замовлення | ✘ | Є лише вузькі аспекти: `own:pcb-thermal-design`, `own:pcb-antenna-layout`, `ref:communications/transmission-lines`, `own:signal-integrity`. Нема наскрізного PCB-флоу — `new:pcb-layout-basics`, `new:pcb-fab-ordering` |
| А10 | Запаяти плату (THT + SMD) | ✔ | `own:pcb-assembly-methods`, `own:smd-rework` (komponenty) |
| А11 | Написати код: основи мови (C/C++), збірка, типи | ✘ | **Курс не має жодного кроку програмування-з-нуля і жодного ref на book/programming.** Теми mk/proshyvka (`own:hal-ll-registers`, `own:solid-principles`, `own:memory-safety`, `own:error-codes-vs-exceptions`) припускають, що C уже відомий. Для аудиторії «нуль програмування» — найбільша діра курсу. `new:` цілий модуль (див. Діри-модулі M1) |
| А12 | Налаштувати середовище: toolchain, збірка, перша прошивка, blink | ◐ | `own:esptool-workflow`, `own:baremetal-vs-framework` — але нема «hello world»: встановлення IDE/SDK, перший blink — `new:first-firmware-blink` |
| А13 | GPIO: кнопка, дребезг, світлодіод | ✘ | Є лише `own:pin-mux` (просунуте) і `own:polling-vs-interrupts`. Нема елементарного GPIO/debounce — `new:gpio-button-debounce` |
| А14 | Зчитати датчик по I2C/SPI/UART у коді | ◐ | `own:spi-vs-i2c`, `own:pullup-resistor-design`, `own:usb-uart-bridge`, `own:dma-adc`, `own:dma-spi-i2s`. Нема окремої теми UART як протоколу і «драйвер датчика з даташита» — `new:uart-protocol`, `new:sensor-driver-from-datasheet` |
| А15 | Периферія МК: таймери/PWM, ADC як периферія, watchdog | ◐ | PWM — `own:pwm-power-control` (силовий кут); ADC — `own:signal-acquisition`, `own:adc-reference-calibration`; таймери/лічильники окремо — нема (`new:timers-counters-pwm`); watchdog лише вставкою proj-heartbeat-watchdog — `new:watchdog-timer` |
| А16 | Структура прошивки: super-loop → RTOS | ◐ | `own:super-loop-limits` (+proj-cooperative-scheduler), `own:spinlock-mutex` — але **RTOS (FreeRTOS: задачі, черги, пріоритети) у курсі відсутній** попри ESP32-центричність. `new:rtos-basics`, `new:rtos-queues-sync` |
| А17 | Відлагодити прошивку (JTAG/GDB, логування, аварії) | ✔ | `own:jtag-swd-tools`, `own:openocd-gdb`, `own:core-dump`, `own:addr2line-workflow`, `own:debug-io-comparison` (mk/proshyvka) |
| А18 | Виміряти: мультиметр, осцилограф, споживання | ◐ | Осцилограф — `own:sine-on-scope`, `own:noise-hunting`; споживання — `own:measure-consumption`, `own:current-profiler-tools`, `ref:electronics/kelvin-shunt`. Мультиметра як теми нема — `new:multimeter-basics` |
| А19 | Корпус: 3D-друк/готовий, IP-захист, кріплення, введення кабелів | ✘ | Механіки нема взагалі (лише `own:imu-mounting-materials` — віброкріплення IMU). `new:enclosure-design`, `new:ip-rating-sealing`, `new:connectors-cabling` |
| А20 | Bring-up нової плати: перший запуск, перевірка живлення, дим-тест | ✘ | Фрагменти є (`own:power-tree-reading`, proj-fault-detect), процедури нема — `new:board-bring-up` |

**Разом А:** ядро (МК, живлення, вимірювання, налагодження) — сильне; **початок (програмування, макетка, перші кроки) і кінець (PCB-флоу, корпус) — провалені.**

## Сценарій Б. Автономний дрон із MAVLink і місіями

| # | Вміння | Покриття | Теми / чого бракує |
|---|--------|----------|--------------------|
| Б1 | Розуміти BLDC-мотор: принцип, kV, комутація | ✘ | Є лише `own:esc-bldc-driver` (регулятор). Самого мотора (і моторів як класу: DC, BLDC, кроковий) нема — `new:bldc-motor`, `new:dc-motors-h-bridge`, `new:stepper-motors` |
| Б2 | Підібрати пропульсію: тяга/вага, пропелери, C-rating батареї, час польоту | ✘ | Нема нічого про тягу, гвинти, розрахунок польотного часу — `new:propulsion-sizing` |
| Б3 | Обрати/зібрати раму, компонування, центр мас | ✘ | `new:airframe-assembly` |
| Б4 | ESC: протоколи (PWM/DShot), калібрування | ◐ | `own:esc-bldc-driver` (basic done, hist-dshot); калібрування/налаштування — частково. Разом з `own:output-mixing` ✔ на виході FC |
| Б5 | Прошити й налаштувати політний контролер (ArduPilot/PX4), калібрування IMU/компаса/ESC | ✘ | `own:autonomous-system` (архітектура), hist-ardupilot — але кроку «первинне налаштування FC: прошивка, майстри калібрування, параметри» нема — `new:fc-setup-calibration` |
| Б6 | RC-лінк: пульт, приймач, протоколи (SBUS/CRSF/ELRS), бінд, failsafe при втраті RC | ✘ | Жодної теми про радіокерування (ELRS/SBUS/CRSF відсутні в маніфесті) — `new:rc-link-protocols` |
| Б7 | MAVLink: телеметрія, команди, heartbeat | ✔ | `own:mavlink-commands` (mk), `own:mavlink-from-ground`, `own:pymavlink` (zvyazok), proj-heartbeat-watchdog |
| Б8 | GCS: Mission Planner / QGroundControl | ✔ | `own:mission-planner-qgc` (mk) |
| Б9 | Спланувати й виконати місію (вейпойнти) | ✔ | `own:mission-planning` (mk), proj-mission-builder |
| Б10 | Бортові давачі: IMU, барометр, GPS, компас | ◐ | `own:onboard-sensors` (+hist-gps), `own:imu-barometer`, `own:barometric-altimeter` — сильно. GNSS глибше (типи fix, RTK, геометрія) і магнітометр/девіація — нема: `new:gnss-navigation`, `new:magnetometer-compass` |
| Б11 | Оцінка орієнтації і навігація | ✔ | `own:attitude-estimation`, `own:kalman-filter`, `own:inertial-navigation`, `own:slam-navigation` (keruvannia) |
| Б12 | Контури керування: PID-каскади, стійкість | ✔ | Ланцюг keruvannia: `own:calculus-for-pid` → `own:proportional-control`/`own:integral-control`/`own:derivative-control` → `own:pid-tuning-cascade` → `own:loop-stability`; math-loop-stability в `own:autonomous-system` |
| Б13 | Віброзахист FC/IMU | ✔ | `own:imu-mounting-materials`, `own:vibration-diagnostics` (davachi) |
| Б14 | Радіолінк: бюджет, антени, завади | ✔ | `own:link-budget`, `own:esp32-antenna`, `own:jamming-fhss`, `own:frequency-budget-analysis` (zvyazok) |
| Б15 | FPV/відео | ✔ | `own:fpv-video-systems`, `own:video-streaming-protocols`, `own:mjpeg-vs-h264` |
| Б16 | Failsafe-конфігурація: RTL, geofence, arming checks | ◐ | proj-failsafe-state-machine (вставка `own:autonomous-system`) — принцип є, конфігурації автопілота нема — `new:failsafe-configuration` |
| Б17 | Безпечний перший політ: передпольотний чеклист, майданчик, процедура | ✘ | `new:preflight-checklist-first-flight`. (Правові рамки польотів — свідомо поза курсом? Якщо ні — `new:drone-regulations`) |
| Б18 | Аналіз польотних логів (dataflash/tlog) після польоту | ✘ | Ключовий інструмент дронобудівника; нема — `new:flight-log-analysis` |
| Б19 | Companion computer / бортовий інференс | ✔ | `own:where-to-compute`, `own:edge-inference`, `own:model-zoo`, `own:model-export`, `own:rpc-embedded` |

**Разом Б:** «мозок» (оцінювання, керування, MAVLink, зв'язок, зір) — покритий добре; **«тіло» (мотори, пропульсія, рама, RC) і польова процедура (налаштування FC, перший політ, логи) — діри.** Курс навчає керувати дроном, який хтось уже зібрав і налаштував.

## Сценарій В. Польова діагностика несправного пристрою

| # | Вміння | Покриття | Теми / чого бракує |
|---|--------|----------|--------------------|
| В1 | Систематична методика пошуку (поділ навпіл, від живлення до сигналу, гіпотеза→перевірка) | ✘ | Є лише кейси (`own:noise-hunting`, proj-field-diagnostics у `own:usb-cables-field`). Загальної методики нема — `new:troubleshooting-methodology` |
| В2 | «Не вмикається»: пройти дерево живлення | ◐ | `own:power-tree-reading`, `own:reverse-polarity` (proj-fault-detect), `own:power-fail-safety` — шматки є, наскрізного walkthrough нема (закривається `new:troubleshooting-methodology` + `new:board-bring-up`) |
| В3 | Виміряти мультиметром у полі (напруги, прозвонка, обриви) | ✘ | `new:multimeter-basics` (та сама діра, що А18) |
| В4 | «Жере батарею»: аудит струму спокою | ✔ | `own:sleep-current-audit`, `own:measure-consumption`, `own:power-logger`, `own:current-profiler-tools`, `own:board-consumption` — найсильніше місце курсу |
| В5 | «Зависає»: watchdog, core dump, декодування аварії | ✔/◐ | `own:core-dump`, `own:addr2line-workflow`, `own:fault-injection-testing`, `own:reset-sequence`, `own:power-fail-safety`. Бракує окремої теми апаратного watchdog (`new:watchdog-timer`) |
| В6 | «Втрачає зв'язок»: RSSI, бюджет лінії, завади, антена | ✔ | `own:link-budget`, `own:jamming-fhss`, `own:esp32-antenna`, `own:wifi-fast-connect`, `own:arq-strategies`, `own:frequency-budget-analysis` |
| В7 | Переміжні дефекти: холодна пайка, роз'єми, вібрація, корозія | ◐ | `own:smd-rework` (пайка), `own:vibration-diagnostics`; роз'єми/кабелі як клас відсутні — `new:connectors-cabling`, `new:intermittent-faults` |
| В8 | Теплові проблеми | ✔ | `own:thermal-budget`, `own:pcb-thermal-design`, `ref:physics/thermal-resistance` |
| В9 | Розпізнати ESD/перенапругу | ✔ | `ref:electronics/esd-damage`, `own:surge-protection-cascade`, `own:esd-protection-circuits` |
| В10 | Відновлення прошивки: bootloader, recovery, відкат | ◐ | `own:esptool-workflow` (читання flash), `own:boot-time-budget` — самого завантажувача і recovery-процедури нема: `new:bootloader-recovery` |
| В11 | Волога/середовище: conformal coating, герметизація | ✘ | `new:ip-rating-sealing` (діра корпусного модуля) |
| В12 | Діагностика дрона за польотними логами | ✘ | `new:flight-log-analysis` (та сама діра Б18) |

**Разом В:** окремі симптоми (батарея, зависання, лінк) закриті добре, але **парасольної методики і найпростішого інструмента (мультиметр) нема** — новачок має шматки без алгоритму.

## Сценарій Г. Від прототипа до малої серії

| # | Вміння | Покриття | Теми / чого бракує |
|---|--------|----------|--------------------|
| Г1 | DFM: пристосувати плату до виробництва | ✘ | `new:design-for-manufacturing` |
| Г2 | BOM: закупівля, аналоги, доступність, EOL | ◐ | proj-selection-checklist у `own:datasheet-practice` — лише вибір; керування BOM/sourcing нема — `new:bom-sourcing` |
| Г3 | Замовити виготовлення+монтаж (gerber, панелізація, трафарет, PnP) | ✘ | `new:pcb-fab-ordering` (спільна з А9) |
| Г4 | Масове прошивання і провіжининг (серійники, секрети, ключі) | ◐ | `own:esptool-workflow` — одиничне; серійне+ідентичність пристрою нема — `new:production-flashing-provisioning` |
| Г5 | Заводський функціональний тест (джиг, bed-of-nails, self-test) | ✘ | `own:firmware-testing` — юніт-рівень; виробничого тесту нема — `new:production-test-jig`, `new:factory-self-test` |
| Г6 | Калібрування на виробництві | ✔ | `own:calibration-procedure`, `own:adc-reference-calibration` (proshyvka) |
| Г7 | Захист прошивки: secure boot, шифрування flash | ✔ | `own:tpm-trustzone` (+proj-esp32-secure-boot) |
| Г8 | OTA-оновлення в полі: розділи A/B, відкат, підпис | ◐ | `own:ota-server` — лише сервер; клієнтської механіки (партиції, rollback, підпис образу) нема — `new:ota-client-rollback` |
| Г9 | CI/CD: відтворювані збірки, версіонування релізів | ◐ | `own:gitflow-branching` є; CI, артефакти, reproducible builds — нема: `new:firmware-ci-cd` |
| Г10 | Трасованість: серійні номери, журнал виробництва, RMA-аналіз | ✘ | `new:traceability-rma` |
| Г11 | Сертифікація: EMC/радіо (CE/FCC), pre-compliance | ◐ | `own:emi-filter-design` — лише дизайн фільтра; випробування і вимоги — нема: `new:emc-precompliance` |
| Г12 | Надійнісні випробування: burn-in, термоцикли, HALT | ◐ | `own:fmea-embedded` (аналіз), `own:fault-injection-testing` (софт); середовищних випробувань нема — `new:reliability-testing` |
| Г13 | Серійний корпус: лиття vs 3D-друк, кріплення плати | ✘ | Діра корпусного модуля — `new:enclosure-design` |
| Г14 | Виробнича документація: інструкція збірки, тест-процедура | ✘ | Дотично proj-spec-as-code (`own:power-spec-template`); нема — закривається темами Г-модуля |

**Разом Г:** сценарій **не покритий як ціль узагалі** — є лише острівці (калібрування, secure boot, напівOTA). Це найбільша відсутня *область* курсу.

---

## Зведення дір

### Рівень 1 — відсутні цілі модулі (нові секції)

- **M1. `new-module:prohramuvannia` «Програмування з нуля для МК»** — P0. Аудиторія «нуль програмування», а в курсі нема ані基 C (типи, вказівники, пам'ять, збірка), ані жодного `ref:programming/...` (book/programming уже наповнюється — integer-types-c, integer-promotion тощо готові для ref-ів). Ставити перед секцією `mk`. Закриває А11, передумова А12–А16.
- **M2. `new-module:aktuatory` «Мотори й актуатори»** — P0. DC-мотор + H-міст, кроковий + драйвер, BLDC + комутація, соленоїди; зараз лише `own:servo-sizing` і `own:esc-bldc-driver` у drony. Без нього і прилад (А), і дрон (Б1–Б2) висять у повітрі. Місце: після `keruvannia` або перед `drony`.
- **M3. `new-module:vyrobnytstvo` «Від прототипа до серії»** — P1. DFM, BOM/закупівля, замовлення плат+монтаж, серійне прошивання/провіжининг, тест-джиг, OTA-клієнт з відкатом, EMC/сертифікація, трасованість/RMA (Г1–Г14). Остання секція курсу.
- **M4. `new-module:korpus` «Корпус і механіка»** (або великий блок у M3) — P1. Корпуси, 3D-друк, IP/герметизація, роз'єми й кабелі, кріплення, віброзахист (А19, В7, В11, Г13).

### Рівень 2 — відсутні кроки в наявних секціях

- **P0**: RTOS-базис (2–3 кроки в `mk` або `proshyvka`: `new:rtos-basics`, `new:rtos-queues-sync`) — ESP32-центричний курс без FreeRTOS; базова цифрова логіка перед FPGA-темами `cyfra-pamyat` (`new:binary-and-logic-gates`, `new:flip-flops-counters` — зараз секція починається зі зсувного регістра і стрибає в PAL/FPGA); перші кроки прошивки в `mk` (`new:first-firmware-blink`, `new:gpio-button-debounce`); наскрізний PCB-флоу в `komponenty`/`kola` (`new:pcb-layout-basics`, `new:pcb-fab-ordering`) + `new:breadboard-prototyping`.
- **P1**: дроновий bring-up у `drony` (`new:fc-setup-calibration`, `new:rc-link-protocols`, `new:propulsion-sizing`, `new:failsafe-configuration`, `new:preflight-checklist-first-flight`, `new:flight-log-analysis`); польова діагностика в `proshyvka` (`new:troubleshooting-methodology`, `new:multimeter-basics`, `new:board-bring-up`); `new:watchdog-timer`, `new:bootloader-recovery`, `new:ota-client-rollback` (пара до `own:ota-server`).
- **P2**: `peryferiia` радикально тонка (5 тем): `new:uart-protocol`, `new:timers-counters-pwm`, `new:can-bus` (DroneCAN/CAN для дронів), `new:onewire`; давачі: `new:sensor-selection`, `new:temperature-humidity-sensors`, `new:gnss-navigation`, `new:magnetometer-compass`; живлення: `new:single-cell-charger`; схемотехніка: `new:schematic-capture-practice`, `new:sensor-driver-from-datasheet`, `new:device-requirements-spec`, `new:system-block-diagram`.

### Рівень 3 — структурні зауваги до порядку модулів

1. **`napivprovidnyky` стоїть після тем, які його потребують**: транзисторні теми (`own:bjt-load-driving`, `own:bjt-vs-mosfet`) живуть у `kola` (секція 2), діоди (`own:zener-schottky`, `own:flyback-protection`) — у `komponenty` (секція 3), а фізика напівпровідників — аж секція 4. На рівні модулів: або підняти `napivprovidnyky` між `kola` і `komponenty`, або (краще, але це вже міжсекційний перенос) винести транзисторно-діодні теми з `kola`/`komponenty` у `napivprovidnyky`.
2. **`cyfra-pamyat` перед `zhyvlennia`** — цифра/FPGA раніше за живлення нелогічно для траєкторії «зібрати пристрій»; живлення потрібне раніше.
3. **`proshyvka` (і взагалі код) без модуля програмування** — M1 має стати перед `mk`.
4. `napivprovidnyky` змішує діоди з flash/EEPROM/FRAM (`own:nor-vs-nand`, `own:eeprom-fram`, `own:mram-rram-pcm`) — пам'ять природніше в `cyfra-pamyat` (міжсекційний перенос, поза моїм мандатом — фіксую).

**Рекомендований порядок модулів (цільовий):**
`osnovy` → `kola` → `komponenty` → `napivprovidnyky` → `zhyvlennia` → *[цифрова логіка]* + `cyfra-pamyat` → **M1 програмування** → `mk` (+RTOS) → `peryferiia` (розширена) → `proshyvka` (+діагностика) → `davachi` → **M2 мотори й актуатори** → `dyspleyi` → `keruvannia` → `zvyazok` → `drony` (+bring-up-блок) → **M4 корпус** → **M3 виробництво**.

### Підсумкова оцінка покриття сценаріїв

| Сценарій | Покриття | Головний блокер |
|---|---|---|
| А. Прилад з нуля | ~55% | нема програмування-з-нуля, PCB-флоу, корпуса, перших кроків (макетка/blink) |
| Б. Дрон | ~65% | нема «тіла»: мотори/пропульсія/рама/RC-лінк; нема процедури налаштування і першого польоту |
| В. Польова діагностика | ~60% | нема парасольної методики і мультиметра; симптоми поодинці закриті добре |
| Г. Мала серія | ~20% | модуля виробництва не існує; лише калібрування, secure boot і пів-OTA |

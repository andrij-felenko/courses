# Аналіз модуля «peryferiia» — «Периферія й шини» (guide/embedded)

## 0. Поточний стан

Модуль — 5 тем, без розділів:

1. `ref:communications/differential-pair` — Диференційна пара
2. `ref:communications/rs-485` — RS-485
3. `own:spi-vs-i2c` — SPI проти I2C (basic done, detailed done)
4. `own:pullup-resistor-design` — Розрахунок підтяжки (basic done)
5. `own:usb-uart-bridge` — Перетворювач USB↔UART (basic done)

**Головний діагноз: це заглушка.** «Периферія й шини» — тематичне серце embedded-курсу, а тут нема ані GPIO, ані таймерів, ані UART, ані власне SPI/I2C як шин (є лише порівняння), ані CAN, ані USB як шини даних, ані АЦП/ЦАП. При цьому предметні книги (communications, programming, electronics) уже містять **готові атоми практично на все** — у секції «Шини» книги communications лежить ~50 статей (uart-frame, i2c-bus, spi-bus, can-arbitration, dronecan, register-map…), у programming — секція «Периферія» (usb-overview…esp32-usb, timer-counter, watchdog, gpio-registers), в electronics — логічні рівні, open-drain, брязкіт контактів, АЦП/ЦАП. Курс їх просто не підключив.

## 1. Порушення порядку (за поточним станом)

1. **«RS-485» (крок 2) вимагає UART, якого в курсі нема взагалі.** RS-485 — це фізичний рівень, яким зазвичай їдуть кадри UART; читач же ще ніде не бачив ні асинхронної передачі, ні кадру, ні baud. Перша згадка «serial» — mk/jtag-swd-tools (попередня секція), теж без пояснення.
2. **«SPI проти I2C» (крок 3) — порівняння шин до знайомства з ними.** Стаття написана коректно як «вибір» і сама інлайн-лінкує `book:communications/spi-bus` та `book:communications/i2c-bus` як опору (перевірено в тексті `guide/embedded/peryferiia/spi-vs-i2c/spi-vs-i2c.md`, рядок 3) — але цих статей у курсі нема. Читач порівнює те, чого не вчив.
3. **«Розрахунок підтяжки» (крок 4) вимагає open-drain і логічних рівнів** — ні `electronics/open-drain`, ні `electronics/logic-levels-as-ranges` у курсі ніде нема. (RC-стала з kola — є, ок.)
4. **«Перетворювач USB↔UART» (крок 5) вимагає і UART (нема), і USB як шини даних (нема).** У zhyvlennia USB подано лише як живлення (usb-power-map, pd-sink-design); хост/енумерація/класи (CDC!) ніде не з'являлись.
5. **«Диференційна пара» як перший крок модуля — дидактично не на місці.** Формальні пререквізити покриті (шум і наводки в osnovy, лінії передачі в cyfra-pamyat), але мотивація «навіщо диференціювати» народжується лише після односторонніх шин та їхніх меж. Правильне місце — після UART/SPI/I2C, у розділі про довгі лінії, поруч із `communications/single-ended-line-limits`.
6. **Крос-секційне (задом наперед):** mk/dma-adc і mk/dma-spi-i2s (секція mk, ПЕРЕД периферією) вже використовують АЦП, SPI та I2S — теми, які периферія дає лише тепер (АЦП та I2S зараз не дає взагалі). Так само mk/jtag-swd-tools, mk/debug-io-comparison, mk/esptool-workflow користуються UART-консоллю і USB-UART-мостом до їх введення.
7. **Крос-секційне (вперед):** davachi (наступна секція) читає IMU/барометр по I2C/SPI через реєстрові карти — а модуль зараз не дає ні `communications/register-map`, ні транзакцій I2C, ні chip-select.

## 2. Пропонована структура — 8 розділів, 55 кроків

Логіка наскрізна: **ніжка → час → аналог ↔ цифра → перший послідовний зв'язок (UART) → шини на платі (SPI/I2C) → довгі лінії (диф. пари, RS-485, CAN) → USB → потоки даних без процесора (DMA) і карта шин цілого пристрою.** Кожен розділ спирається лише на попереднє: MOSFET/RC з kola, кварци з komponenty, зсувний регістр і лінії передачі з cyfra-pamyat, PWM із zhyvlennia, переривання/регістри/ESP32 з mk.

### Розділ 1. Ніжка мікроконтролера: GPIO (10)
1. `new:gpio-pin` — власна кумулятивна стаття-вступ: пін як програмований контакт; вхід/вихід/режими (ДОДАТИ). Це «нитка», що з'єднує mk (регістри, ESP32) з електрикою з kola.
2. `ref:electronics/logic-levels-as-ranges` «Рівні «0» і «1»» (ДОДАТИ; basic done) — цифра як діапазони напруг, VIL/VIH.
3. `ref:electronics/push-pull-output` «Push-pull вихід» (ДОДАТИ; done) — спирається на bjt-vs-mosfet із kola.
4. `ref:electronics/open-drain` «Open-drain» (ДОДАТИ; done) — база для підтяжки, I2C і CAN далі.
5. `own:pullup-resistor-design` «Розрахунок підтяжки» (існує) — тепер після open-drain; RC-стала з kola вже є.
6. `ref:electronics/threshold-schmitt` «Поріг і Шмітт» (ДОДАТИ; done) — повільні фронти, гістерезис входів.
7. `ref:electronics/contact-debounce` «Брязкіт контактів» (ДОДАТИ; done) — перша реальна задача входу (кнопка).
8. `ref:programming/interrupt-driven-io` «Переривання від зовнішніх подій: EXTI і INT-входи» (ДОДАТИ; pending) — polling-vs-interrupts з mk уже пройдено.
9. `ref:electronics/level-shifting` «Зсув рівнів» (ДОДАТИ; done) — стик 3.3/5 В, класична стіна новачка.
10. `own:pin-mux` «Мультиплексування пінів (IO_MUX / GPIO matrix)» — **move_in із mk**: це про те, як периферія дістається ніжок; місток до всіх наступних розділів.

### Розділ 2. Таймери: час у залізі (6)
1. `ref:programming/timer-counter` «Таймер-лічильник» (ДОДАТИ; done) — кварци з komponenty вже пройдені.
2. `ref:programming/timer-overflow` «Період і переповнення» (ДОДАТИ; done).
3. `ref:programming/capture-compare` «Захоплення й порівняння» (ДОДАТИ; done) — input capture/output compare; на це далі обіпреться proshyvka/frequency-measurement-methods.
4. `ref:programming/pwm-hardware-timer` «Апаратний таймер для PWM» (ДОДАТИ; pending) — PWM-як-ідея вже була в zhyvlennia/pwm-power-control; тут — хто його генерує.
5. `ref:programming/watchdog` «Watchdog» (ДОДАТИ; done) — критично для автономних систем, у курсі відсутній взагалі.
6. `ref:electronics/rtc-timekeeping` «RTC і точний відлік часу» (ДОДАТИ; pending) — замикає на watch-crystal/TCXO з komponenty.

### Розділ 3. Аналог ↔ цифра: АЦП і ЦАП (5)
1. `ref:electronics/adc` «АЦП» (ДОДАТИ; done).
2. `ref:electronics/adc-resolution` «Роздільність АЦП» (ДОДАТИ; done).
3. `ref:electronics/adc-types` «Типи АЦП» (ДОДАТИ; done) — SAR/sigma-delta оглядово.
4. `ref:electronics/dac` «ЦАП» (ДОДАТИ; done).
5. `ref:electronics/pwm-dac-filter` «ШІМ як ЦАП: RC-фільтр і пульсації» (ДОДАТИ; done) — гарний місток від розділу 2; RC із kola.
Без цього розділу mk/dma-adc і keruvannia/signal-acquisition висять у повітрі; глибока теорія дискретизації лишиться в keruvannia — тут лише периферійний мінімум.

### Розділ 4. Перший послідовний зв'язок: UART (5)
1. `ref:communications/async-serial` «Асинхронна передача» (ДОДАТИ; done).
2. `ref:communications/uart-frame` «Кадр UART» (ДОДАТИ; done) — зсувний регістр із cyfra-pamyat стає механізмом.
3. `ref:communications/baud-rate` «Швидкість baud» (ДОДАТИ; done).
4. `ref:communications/clock-tolerance-uart` «Допуск годинника UART» (ДОДАТИ; pending) — замикає на кварци/резонатори; пояснює «чому сміття на неправильному baud».
5. `ref:communications/flow-control` «Керування потоком» (ДОДАТИ; done; proj-ring-buffer — саме embedded-контекст).

### Розділ 5. Шини на платі: SPI та I2C (8)
1. `ref:communications/spi-bus` «Шина SPI» (ДОДАТИ; done) — пара зсувних регістрів.
2. `ref:communications/cpol-cpha` «Режими CPOL/CPHA» (ДОДАТИ; done).
3. `ref:communications/chip-select` «Вибір кристала» (ДОДАТИ; done).
4. `ref:communications/i2c-bus` «Шина I2C» (ДОДАТИ; done) — open-drain з розділу 1 працює.
5. `ref:communications/i2c-addressing` «Адресація I2C» (ДОДАТИ; done).
6. `ref:communications/start-stop-ack` «Старт, стоп, ACK» (ДОДАТИ; done).
7. `ref:communications/register-map` «Регістрова карта» (ДОДАТИ; done) — ключ до давачів у секції davachi.
8. `own:spi-vs-i2c` «SPI проти I2C» (існує) — нарешті на своєму місці: порівняння ПІСЛЯ знайомства; її book:-лінки тепер ведуть на пройдене.

### Розділ 6. Довгі лінії: диференційні пари й польові шини (7)
1. `ref:communications/single-ended-line-limits` «Межі односторонніх ліній» (ДОДАТИ; pending) — мотивація всього розділу.
2. `ref:communications/differential-pair` «Диференційна пара» (існує; перенесено з 1-ї позиції модуля сюди).
3. `ref:communications/rs-485` «RS-485» (існує) — тепер після UART: зрозуміло, ЩО їде по парі.
4. `ref:communications/modbus` «Modbus» (ДОДАТИ; pending) — протокол поверх RS-485, промислова класика.
5. `ref:communications/can-frame-errors` «Кадр CAN» (ДОДАТИ; pending) — CAN у курсі відсутній повністю.
6. `ref:communications/can-arbitration` «Арбітраж CAN» (ДОДАТИ; pending) — wired-AND виростає з open-drain (розділ 1).
7. `ref:communications/dronecan` «DroneCAN» (ДОДАТИ; pending) — пряме живлення секції drony.

### Розділ 7. USB зсередини (7)
1. `ref:programming/usb-overview` «USB огляд» (ДОДАТИ; done) — хост-центрична шина; живлення вже було в zhyvlennia.
2. `ref:programming/usb-physical` «USB фізично» (ДОДАТИ; done) — D+/D− як диференційна пара (розділ 6).
3. `ref:programming/usb-enumeration` «Енумерація USB» (ДОДАТИ; done).
4. `ref:programming/usb-endpoints` «Кінцеві точки USB» (ДОДАТИ; done).
5. `ref:programming/usb-device-classes` «Класи USB» (ДОДАТИ; done) — CDC/HID/MSC.
6. `own:usb-uart-bridge` «Перетворювач USB↔UART» (існує) — тепер обидва боки моста відомі (UART розд. 4, CDC щойно).
7. `ref:programming/esp32-usb` «USB в ESP32» (ДОДАТИ; done) — «а тепер без моста»; платформа курсу.

### Розділ 8. Потоки даних: периферія без процесора (7)
1. `ref:programming/dma-problem` «Проблема потоку даних» (ДОДАТИ; done).
2. `ref:programming/dma-controller` «DMA-контролер» (ДОДАТИ; done).
3. `own:dma-adc` «DMA + АЦП» — **move_in із mk**: тепер АЦП (розділ 3) і DMA (щойно) відомі.
4. `ref:communications/i2s-bus` «Шина I2S» (ДОДАТИ; pending) — інакше I2S у наступному кроці нізвідки.
5. `own:dma-spi-i2s` «DMA + SPI/I2S» — **move_in із mk**: SPI з розділу 5, I2S щойно.
6. `ref:communications/sd-card-protocol` «Протокол SD/SDIO» (ДОДАТИ; pending) — швидка периферія; ґрунт під proshyvka/fatfs-integration.
7. `new:bus-map-of-a-device` — власна стаття-замикання: карта шин одного реального пристрою (політний контролер: IMU на SPI, барометр на I2C, GPS на UART, ESC по PWM/DShot, SD на SDIO, USB для конфігурації) (ДОДАТИ). Кумулятивний фінал модуля, місток до davachi/drony.

**Перевірка: всі 5 поточних тем розкладені** (pullup → р.1, spi-vs-i2c → р.5, differential-pair і rs-485 → р.6, usb-uart-bridge → р.7); жодної не загублено; move_out нема.

## 3. Чуже/своє

**move_out: нема.** Усі 5 тем модуля тематично свої — проблема не в зайвому, а у відсутньому й у порядку.

**move_in (3):**
- `own:pin-mux` із mk — «мультиплексування пінів» це історія про GPIO і доступ периферії до ніжок; у mk стояла серед тулінгу без ґрунту. Тут — завершення GPIO-розділу.
- `own:dma-adc` із mk — у mk порушувала пререквізити (АЦП ще не було). Тут стає в розділ 8 після АЦП і DMA-вступу.
- `own:dma-spi-i2s` із mk — у mk використовувала SPI/I2S до їх появи. Тут — після розділу 5 і ref-а про I2S.

## 4. Прогалини (усі перевірені по маніфестах книг; статуси вказано)

Для новачка (без цього — стіна): logic-levels-as-ranges, push-pull-output, open-drain, threshold-schmitt, contact-debounce, level-shifting, gpio-pin (new), async-serial, uart-frame, baud-rate, spi-bus, i2c-bus, i2c-addressing, start-stop-ack, usb-overview…usb-device-classes.
Для повноти модуля: таймери (timer-counter, timer-overflow, capture-compare, pwm-hardware-timer), watchdog, rtc-timekeeping, АЦП/ЦАП (adc, adc-resolution, adc-types, dac, pwm-dac-filter), register-map, cpol-cpha, chip-select, clock-tolerance-uart, flow-control, single-ended-line-limits, modbus, CAN-трійка (can-frame-errors, can-arbitration, dronecan), esp32-usb, dma-problem, dma-controller, i2s-bus, sd-card-protocol, interrupt-driven-io, bus-map-of-a-device (new).

Повний перелік із «як» — у структурованому виводі (47 позицій: 45 ref на готові book-атоми + 2 new). З 45 ref-ів ~33 уже basic:done (читабельні одразу), решта pending — вони й так у черзі письма книг: single-ended-line-limits, can-arbitration, can-frame-errors, dronecan, clock-tolerance-uart, modbus, i2s-bus, sd-card-protocol, interrupt-driven-io, pwm-hardware-timer, rtc-timekeeping.

Свідомо НЕ включено (щоб не роздувати): 1-Wire (нішева; за бажання пізніше new:one-wire-bus), Ethernet MAC/PHY (домен zvyazok, там уже є ethernet-frame/ethernet-link-phy), паралельні інтерфейси дисплеїв (домен dyspleyi/gram-init-sequence), i2c-transaction і spi-lines (дрібніші атоми, покриті сусідніми кроками).

## 5. Органічність ref/own

- Зараз модуль відкривається «стіною» з 2 ref без жодної власної нитки — і обидва ref стоять не на місці.
- `spi-vs-i2c` — взірець правильної own-статті: порівняння ПОВЕРХ book-атомів, з інлайн-лінками на них; курсу бракувало лише самих атомів. Після перестановки все зростається.
- У новій структурі розділи 1, 5, 7, 8 закінчуються own-статтями (синтез), а 2, 3, 4, 6 — чисті ref-ряди по 5–7 кроків. Це прийнятно (стиль osnovy такий самий), але за бажання наступним заходом можна дати короткі own-вступи до розділів 2 і 6. Додано лише 2 нові own-статті (gpio-pin — вступна нитка, bus-map-of-a-device — фінальний синтез); решта потреб закривається готовими ref.
- Дублікати в книгах, помічені дорогою (обирав по одному з пари, книгам потрібна дедуплікація): communications: cpol-cpha vs spi-modes; clock-stretching vs i2c-clock-stretching; smbus vs smbus-protocol; quad-spi vs qspi-multi-lane; usb-device-basics (дублює цілу серію programming/usb-*); i2c-bus-capacity перекривається з курсовою own pullup-resistor-design. electronics: logic-levels-as-ranges vs logic-thresholds; level-shifting vs level-shifter; threshold-schmitt vs schmitt-trigger.

## 6. Модуль як ціле

- **Назва влучна** («Периферія й шини»), відповідає наповненню після ремонту.
- **Глобальне місце (8-ма секція, після mk) правильне:** переривання, регістри (hal-ll-registers), платформа ESP32 з mk потрібні тут; kola/komponenty/cyfra-pamyat/zhyvlennia дають фізичний ґрунт. Модуль повинен лишитися ПЕРЕД proshyvka/davachi/dyspleyi — вони всі споживають шини.
- **Але:** тулінгові теми mk (jtag-swd-tools, debug-io-comparison, esptool-workflow, openocd-gdb) споживають UART/USB-міст до периферії. Це зона аналітика mk; природний вихід — перенести їх у proshyvka (йде одразу після периферії). Мій move_in dma-тем закриває другу половину цього конфлікту.
- **Розмір:** після наповнення ~55 кроків / 8 розділів — найбільший модуль курсу. Якщо це забагато, природний шов: «Периферія мікроконтролера» (розділи 1–3: GPIO, таймери, АЦП/ЦАП; 21 крок) + «Шини і з'єднання» (розділи 4–8: UART, SPI/I2C, довгі лінії, USB, DMA-потоки; 34 кроки). DMA-розділ при поділі лишається в другій частині (потребує SPI/I2S). Не зливати з іншими модулями.

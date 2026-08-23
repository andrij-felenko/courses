# Том 3. Мікроконтролери

Курс «Вбудована електроніка й автономні системи», том 3 із 15.

**Читач на вході.** Пройшов том 1 (заряд, струм, напруга, деталі, прилади, мультиметр)
і том 2 (аналогові й цифрові пристрої, сигнали, логічні рівні, вентилі, тригери,
регістри, скінченні автомати, типи пам'яті, поняття АЦП). Він уміє зібрати схему,
що робить одне й те саме. Він жодного разу не запускав нічого програмованого
й, найімовірніше, не вміє програмувати.

**Читач на виході.** На чужій платі він упевнений: вибирає чип під задачу й знаходить
відповідь у його reference manual; ставить тулчейн, збирає, заливає й відлагоджує
прошивку; знає, де саме в чипі живе його програма і чому вона падає; керує ніжками,
тактом, перериваннями, таймерами, АЦП і DMA прямо з регістрів; будує прошивку як
головний цикл, як автомат станів або як набір задач RTOS; читає HardFault і знає, чим
зняти профіль часу.

**Чого том навмисно не дає.** Нічого, що приєднується ззовні (том 4), нічого про радіо
й мережі (том 5), нічого про енергетичний бюджет (том 6), нічого про архітектуру
програми, що переживає другий пристрій і другого програміста (том 10), нічого про
завантажувач, оновлення й корінь довіри (том 15).

**Вага:** 13 розділів, ≈130 кроків. Це один із найважчих томів курсу — і мусить бути:
все, що йде далі, спирається на нього цілком.

---

## Розділи

### 1. Будова мікроконтролера

Що це за річ, з чого складається, чим відрізняється від процесора, SoC і FPGA,
які сімейства існують і як вибрати чип під задачу, не покладаючись на моду.
**Спирається на:** том 2 — вентилі, тригери, регістри, скінченні автомати, типи
пам'яті; том 1 — живлення й корпуси деталей. **Вага:** ~13 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Мікроконтролер | `наявна` |
| Що таке процесор | `наявна` · **СПІРНА** |
| Складові процесора | `наявна` · **СПІРНА** |
| Цикл виконання | `наявна` · **СПІРНА** |
| Набір інструкцій | `наявна` |
| Кодування інструкцій: як команда стає числом | `+ref programming/computer-architecture/isa-encoding` |
| Складові МК | `наявна` |
| Фон Нейман і Гарвард | `наявна` |
| RISC і CISC | `наявна` |
| Розрядність процесора й режими сумісності | `+ref programming/computer-architecture/processor-word-size` |
| Система-на-кристалі (SoC) | `+ref electronics/microelectronics/system-on-chip` |
| FPGA чи МК | `наявна` |
| Архітектура DSP-процесора | `+ref programming/computer-architecture/dsp-architecture` |
| SRAM-комірка | `+ref electronics/microelectronics/sram-cell` |
| NOR Flash: комірка, побайтове читання, блокове стирання | `+ref electronics/microelectronics/nor-flash-cell` |
| Корпусування | `+ref electronics/pcb/packaging` |
| ESP32 проти 8-біт | `наявна` |
| Сімейство ESP32 · Архітектура ESP32 | `наявна` ×2 |
| Архітектура PIC | `наявна` |
| AVR-клас | `+ref programming/embedded-systems/avr` |
| ARM Cortex-M | `+ref programming/embedded-systems/cortex-m` |
| STM32-клас | `+ref programming/embedded-systems/stm32` |
| nRF-клас | `+ref programming/embedded-systems/nrf-radio-mcu` |
| ESP32-P4 | `+ref programming/embedded-systems/esp32-p4` |
| Екосистема МК | `+ref programming/embedded-systems/mcu-ecosystem` |
| Вибір МК · Чеклист вибору МК | `наявна` ×2 |
| Практикум даташитів: мікроконтролер | `наявна` |
| Документація чипа: даташит, reference manual, errata, приклади | **ВЛАСНА** |
| Плата розробника: що на ній крім чипа | **ВЛАСНА** |

**СПІРНА · «Що таке процесор» / «Складові процесора» / «Цикл виконання» — суперник: том 2.**
Том 2 має право сказати, що процесор — це вінець цифрової логіки: автомат, який
дістає свою наступну дію з пам'яті, і після тригерів та скінченних автоматів це
природний фінал. Моя відповідь: беру, бо **до вміння потрібна причина** (правило 13) —
цикл виконання щось важить лише для того, хто зараз писатиме інструкції. Якщо
проєктувальник тому 2 наполягає, я віддаю **вентильний погляд** («процесор як автомат
із тригерів») і лишаю собі **погляд програміста** («що чип робить із моїм кодом»);
дублювання тут не станеться, бо це різні питання.

---

### 2. Перша прошивка

Від порожньої плати до світлодіода, що блимає, і до відлагоджувача, зупиненого
на потрібному рядку: тулчейн, збірка, заливка, SWD, точки зупину.
**Спирається на:** розділ 1 — читач уже знає, що в чипі є ядро, флеш і периферія.
**Вага:** ~12 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Перша програма: пишемо, збираємо, запускаємо | `наявна` |
| Тулчейн | `наявна` |
| Крос-компіляція: хост, ціль, чому компілятор для ПК не годиться | **НОВА** |
| Стадії компілятора | `+ref programming/languages/compiler-stages` |
| Компіляція · Лінкування | `наявна` ×2 |
| Що робить система збірки | `наявна` |
| Граф залежностей і порядок робіт | `+ref build-systems/fundamentals/dependency-graph` |
| Інкрементальна збірка | `наявна` |
| Файл тулчейна: як CMake дізнається про чужу платформу | `+ref build-systems/cmake/cmake-toolchain-file` |
| ESP-IDF: структура проєкту, компоненти, menuconfig | `кандидат` |
| Прошивка у Flash | `наявна` |
| esptool: прошивання й читання Flash | `наявна` |
| Способи залити прошивку: SWD, DFU, UART-завантажувач, накопичувач | **ВЛАСНА** |
| Перший проєкт: світлодіод блимає | `наявна` |
| Голе залізо vs фреймворк | `наявна` |
| HAL, LL і голі регістри в STM32 | `наявна` |
| Навіщо відлагоджувач | `наявна` |
| Serial, JTAG/SWD | `наявна` |
| SWD і JTAG зсередини | `+ref programming/embedded-systems/swd-jtag-internals` |
| JTAG і граничне сканування | `+ref electronics/digital/jtag-boundary-scan` |
| OpenOCD і GDB | `наявна` |
| Налагодження у VS Code | `+ref programming/embedded-systems/debug-vscode` |
| Кроком по коду | `+ref programming/embedded-systems/step-debugging` |
| Брейкпоінти й вотчпоінти | `+ref programming/embedded-systems/breakpoints-watchpoints` |
| Перетворювач USB↔UART | `наявна` |

**СПІРНА · «Мова CMakeLists», «Цілі й властивості CMake» — суперник: том 10.**
Віддаю тому 10: писати `CMakeLists.txt` руками треба тоді, коли проєкт має більше
однієї цілі й більше одного автора. Собі лишаю рівно те, без чого не збереться перший
проєкт: що таке тулчейн, що робить система збірки, файл тулчейна.

---

### 3. Мова прошивки

C і C++ рівно в тій підмножині, яку нав'язує чип: типи фіксованої ширини, вказівники,
біти, структури, `const`/`volatile`, відмова від купи, RAII і шаблони як безкоштовна
абстракція — і чіткий перелік того, чого в прошивку не тягнуть.
**Спирається на:** розділ 2 — читач уже бачив працюючу програму й хоче зрозуміти,
що в ній написано. **Вага:** ~15 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Змінні й типи · Розгалуження й цикли · Функції | `наявна` ×3 |
| Область видимості змінної | `+ref programming/languages/variable-scope` |
| Масиви й рядки | `наявна` |
| Масив · Зв'язаний список | `+ref algorithms/data-structures/array`, `+ref algorithms/data-structures/linked-list` |
| Структури й перелічення | `наявна` |
| Покажчики: перше знайомство · Адреси й покажчики | `наявна` ×2 |
| Цілі типи в C/C++ | `наявна` |
| Просування цілих типів у C/C++ | `+ref programming/computer-architecture/integer-promotion` |
| Знакове розширення · Доповняльний код | `+ref programming/computer-architecture/sign-extension`, `+ref programming/representation/twos-complement` |
| Переповнення · Беззнакове переповнення й модульна арифметика | `наявна`, `+ref programming/languages/unsigned-overflow` |
| Насичувальна арифметика | `+ref programming/computer-architecture/saturating-arithmetic` |
| Бітові операції · Побітові операції та маски · Бітова множина | `наявна`, `+ref programming/computer-architecture/bitwise-operations`, `+ref programming/representation/bitset` |
| Пошук крайнього одиничного біта (CLZ/CTZ) · popcount | `+ref programming/computer-architecture/bit-scan-clz-ctz`, `+ref programming/computer-architecture/popcount` |
| Фіксована кома · Реалізація fixed-point | `наявна`, `+ref algorithms/signal-robotics/fixed-point-implementation` |
| Плаваюча кома · Блок дробових чисел (FPU) · Напівточність | `наявна`, `+ref programming/computer-architecture/fpu`, `+ref programming/computer-architecture/half-precision` |
| Препроцесор і заголовки · Препроцесор і макроси | `наявна`, `+ref programming/languages/preprocessor-macros` |
| Модулі й збірка проєкту · Одиниця трансляції: static, extern, inline | `наявна`, `+ref programming/languages/translation-unit` |
| Слабкі символи | `+ref programming/languages/weak-symbols` |
| Невизначена поведінка (UB) · Суворе аліасування | `+ref programming/languages/undefined-behavior`, `+ref programming/languages/strict-aliasing` |
| Вартові значення: як позначити «нічого» всередині типу | `+ref programming/representation/sentinel-values` |
| Чому C++ на мікроконтролері | `кандидат` |
| Класи, час життя й RAII · Конструктор і деструктор | `кандидат`, `+ref programming/languages/raii`, `+ref programming/languages/constructors-destructors` |
| Шаблони й нульова вартість абстракції | `кандидат`, `+ref programming/languages/zero-cost-abstractions` |
| constexpr: обчислення на етапі компіляції | `кандидат`, `+ref programming/languages/constexpr` |
| Що з C++ не тягнуть у прошивку: винятки, RTTI, купа, віртуальні виклики | `кандидат` |
| Коди помилок проти винятків | `наявна` |
| std-типи без купи: array, span, string_view, optional | `кандидат` |
| Об'єктна система поверх C: клас, примірник, реєстрація типу | `+ref programming/languages/object-system-in-c` |

**СПІРНА · увесь розділ — суперника немає, і це проблема курсу.** Див. «Заперечення» —
цей розділ стоїть тут не тому, що він тут доречний, а тому, що курс не має тому,
де вчать програмувати. Позиція розділу третьою — навмисна: спершу працюючий світлодіод
(правило «довгий теоретичний розгін без результату вбиває курс»), і аж тоді мова.
Правило корпусу «є C — має бути й C++» тут не додаток, а причина тримати обидві мови
в одному розділі: вкладка C++ стоїть поруч із кожним прикладом C, отже дві мови
викладаються разом, а не одна після одної.

---

### 4. Пам'ять і образ програми

Де саме в чипі лежить кожен байт написаного: карта пам'яті, секції образу, стек,
купа, скрипт лінкера, стартовий код, і чому регістр периферії — це просто адреса.
**Спирається на:** розділ 3 — без типів і вказівників це порожні слова; розділ 1 —
флеш і SRAM уже названі. **Вага:** ~14 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Пам'ять як масив | `наявна` |
| Карта пам'яті | `наявна` |
| Flash і RAM | `наявна` |
| Ієрархія пам'яті | `+ref electronics/digital/memory-hierarchy` |
| Образ прошивки (.text, .rodata, .data, .bss) | `наявна` |
| ELF-формат прошивки | `+ref programming/languages/elf-format` |
| Скрипт лінкера: як секції лягають в адреси | **НОВА** |
| Map-файл: що з'їло флеш і RAM | **НОВА** |
| Стартовий код: від Reset_Handler до main | **ВЛАСНА** |
| C-рантайм | `наявна` |
| Стек · Переповнення стека | `наявна` ×2 |
| Угода про виклик (ABI) · ABI та calling convention | `+ref programming/computer-architecture/calling-convention`, `+ref programming/languages/abi-calling-convention` |
| Купа: чому на МК її здебільшого немає | `наявна` |
| Бюджет пам'яті мікроконтролера | `наявна` |
| Вирівнювання даних у пам'яті · апаратні вимоги | `+ref programming/computer-architecture/memory-alignment`, `+ref programming/systems/alignment-hardware` |
| Біти й порядок байтів | `наявна` |
| Memory-mapped IO · Port-mapped IO | `наявна`, `+ref programming/computer-architecture/port-mapped-io` |
| Адресна дешифрація шини · Системна шина | `+ref electronics/digital/address-decoding`, `+ref electronics/digital/system-bus` |
| CMSIS: стандартний інтерфейс ПЗ для Cortex-M | `+ref programming/embedded-systems/cmsis` |
| XIP: виконання коду з флеші на місці | `+ref programming/computer-architecture/xip-memory-mapped-flash` |
| Flash зсередини · Запис у власну флеш із програми | `наявна` |
| NVS: де зберегти калібрування, щоб пережило скидання | `наявна` |
| Блок захисту пам'яті (MPU) в Cortex-M | `+ref electronics/digital/mpu-cortex-m` |
| Кільця захисту й рівні привілеїв · Розділення адресних просторів | `+ref programming/computer-architecture/protection-rings`, `+ref programming/computer-architecture/address-space-separation` |
| Коли чип падає: причина скидання й HardFault з першого погляду | **ВЛАСНА** · *спіраль, глибоко — розділ 13* |

**СПІРНА · «Навіщо зберігати», «Wear leveling», «Цілісність запису» — суперник: том 10.**
Собі лишаю два кроки: **запис у власну флеш** і **NVS як місце для калібрування**, бо
без них том 7 не має де тримати калібрування IMU. Знос, журнальне сховище й цілісність
запису віддаю тому 10: відповідь на них міняється, щойно з'являється друга версія
формату або другий пристрій із чужим станом.

---

### 5. Такт і скидання

Життя чипа від подачі живлення: звідки він бере такт, чим його множить і ділить,
що змушує його стартувати спочатку і що вирішує, звідки саме він почне.
**Спирається на:** розділ 4 — таблиця векторів і стартовий код уже відомі; том 1 —
кварц і генератори. **Вага:** ~12 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Мінімальна обв'язка МК: живлення, скидання, boot-піни, кварц | `кандидат` · **СПІРНА** |
| Причини reset | `наявна` |
| Brown-out | `наявна` |
| Strapping-піни й режими завантаження | `кандидат` |
| ROM-завантажувач: як чип приймає прошивку, коли в нього ще нічого немає | **ВЛАСНА** |
| Фьюзи, option bytes і як не зробити цеглинку | **ВЛАСНА** |
| Кільцевий генератор (внутрішній RC) | `+ref electronics/digital/ring-oscillator` |
| Дерево тактування МК: джерела, PLL, дільники, увімкнення периферії | `кандидат` |
| Тактова частота і тактовий домен | `+ref electronics/digital/clock-domain` |
| Дільник частоти · Прескейлер і синтез частоти | `+ref electronics/digital/frequency-divider`, `+ref electronics/digital/prescaler` |
| Частота процесора | `наявна` |
| Затримки читання флеш-пам'яті й тактова частота | **НОВА** |
| Конвеєр · Кеш | `наявна` ×2 |
| Тактування й живлення | `+ref programming/embedded-systems/clock-power` |
| Тактове стробування · Power gating і clock gating | `+ref electronics/digital/clock-gating`, `+ref electronics/microelectronics/power-gating` |
| Режими сну · Джерела пробудження | `наявна` ×2 · **СПІРНА** |
| Динамічне масштабування напруги і частоти (DVFS) | `+ref programming/computer-architecture/dvfs` |
| ULP-співпроцесор · RTC-память | `+ref programming/embedded-systems/ulp-coprocessor`, `+ref programming/embedded-systems/rtc-memory` |
| Домен живлення RTC в SoC | `+ref electronics/digital/rtc-domain-power` |
| Watchdog | `наявна` |
| Лічильник перезавантажень | `+ref programming/embedded-systems/reboot-counter` |
| Модуляція тактового спектру (SSC) | `+ref electronics/digital/spread-spectrum-clocking` |

**СПІРНА · «Режими сну», «Джерела пробудження» — суперник: том 6 «Керування живленням».**
Ділю так: **механізм** мій (сон — це стан тактування, а не стан батареї; прокидання —
це переривання), **бюджет** — тому 6 («Цикл і середній струм», «Споживання плати»,
«Аудит струму спокою», уся вимірювальна частина). Без двох кроків тут том 5 не зможе
пояснити, чому радіомодуль спить між пакетами.

**СПІРНА · «Мінімальна обв'язка МК» — суперник: том 14 «Власні плати та пристрої».**
Лишаю тут **один оглядовий крок**: читач має розуміти, чому плата розробника виглядає
саме так і що з неї доведеться повторити. Розрахунок, розведення й декаплінг — том 14.
Це та сама «тема рано коротко, глибоко пізніше», яку правило 14 дозволяє.

---

### 6. Цифрові виводи

Найпростіша периферія чипа й перша, де він упирається в фізику: режими виводу,
підтяжки, альтернативні функції, скільки міліампер ніжка справді дає і що її вб'є.
**Спирається на:** розділ 4 — регістр як адреса; розділ 5 — без такту порт не працює;
том 2 — логічні рівні й пороги; том 1 — струм і межі.
**Вага:** ~11 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| GPIO — вивід загального призначення | `+ref electronics/digital/gpio` |
| GPIO-регістри | `наявна` |
| Push-pull вихід | `наявна` |
| Open-drain · Відкритий колектор · Монтажне «АБО» | `наявна`, `+ref electronics/digital/open-collector`, `+ref electronics/digital/wired-or` |
| Стан високого опору (Hi-Z) | `+ref electronics/digital/hi-z-state` |
| Підтяжки | `наявна` |
| Active-low: логіка «0 = увімкнено» | `+ref electronics/digital/active-low` |
| Мультиплексування пінів (IO_MUX / GPIO matrix) | `наявна` |
| Розкладка виводів: конфлікти альтернативних функцій | **ВЛАСНА** |
| Навантажувальна здатність · Сила виходу GPIO | `+ref electronics/digital/pin-drive-limits`, `+ref electronics/digital/drive-strength` |
| Slew rate виходу: швидкість і шум | `+ref electronics/digital/slew-rate-gpio` |
| Захист входів GPIO від перенапруги | `+ref electronics/digital/esd-gpio-protection` |
| Поріг і Шмітт | `+ref electronics/digital/threshold-schmitt` |
| Брязкіт контактів | `наявна` |

---

### 7. Переривання

Момент, коли програма перестає бути одним потоком: як чип кидає роботу заради події,
що при цьому можна й чого не можна, і чому дані, поділені з обробником, псуються.
**Спирається на:** розділ 4 — таблиця векторів і стек; розділ 6 — є чому переривати
(кнопка); розділ 3 — `volatile` без пам'яті не пояснити.
**Вага:** ~11 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Polling vs переривання | `наявна` |
| Переривання · ISR | `наявна` ×2 |
| Контролер і вектор | `+ref programming/computer-architecture/interrupt-vector` |
| Обробка виключень у процесорі | `+ref programming/computer-architecture/cpu-exception-handling` |
| Фронт і рівень | `+ref electronics/digital/edge-vs-level` |
| Пріоритети переривань | `наявна` |
| Латентність переривання: від фронту до першої інструкції | **НОВА** |
| Дисципліна обробника: що в ISR робити не можна | **ВЛАСНА** |
| Атомарність і гонки · Перегони даних і замки | `наявна`, `+ref programming/systems/data-races-locks` |
| Критична секція на МК: як правильно вимкнути переривання | **ВЛАСНА** |
| volatile | `+ref programming/languages/volatile` |
| volatile, бар'єри й доступ до регістрів з C | `кандидат` |
| Упорядкування пам'яті та бар'єри · Інструкції DMB/DSB/ISB | `+ref programming/systems/memory-ordering-barriers`, `+ref programming/computer-architecture/memory-barrier-instructions` |
| std::atomic і порядок пам'яті | `+ref programming/languages/std-atomic` · **СПІРНА** |
| Кільцевий буфер: ISR пише, головний цикл читає | `кандидат`, `+ref algorithms/data-structures/ring-buffer` |
| Черга: FIFO і кільцевий буфер | `+ref algorithms/data-structures/queue-fifo` |

**СПІРНА · «std::atomic і порядок пам'яті» — суперник: том 10.**
Беру, але вузько: на одноядерному Cortex-M атомарність — це «переривання не влізе між
читанням і записом», і це кусає на першому ж лічильнику, поділеному з ISR. Формальні
моделі впорядкування, lock-free структури й когерентність між ядрами — том 10.

---

### 8. Таймери

Єдиний блок, що дає прошивці час і рух: лічильник, порівняння, ШІМ, захоплення входу —
і чому `delay()` у робочому коді не буває.
**Спирається на:** розділ 5 — таймер тактується від дерева; розділ 7 — переповнення
приходить перериванням; розділ 6 — вихід ШІМ іде на ніжку через альтернативну функцію.
**Вага:** ~12 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Таймер-лічильник | `наявна` |
| Таймери | `+ref programming/embedded-systems/timers` |
| Синхронний лічильник | `+ref electronics/digital/synchronous-counter` |
| Період і переповнення | `наявна` |
| Точний час | `наявна` |
| Неблокуючий час | `наявна` |
| Періодичні події | `+ref programming/embedded-systems/periodic-scheduling` |
| Колесо таймерів: багато програмних таймерів на одному апаратному | `+ref algorithms/data-structures/timer-wheel` |
| Захоплення й порівняння | `наявна` |
| Тіньовий регістр (preload) | `+ref electronics/digital/shadow-register` |
| ШІМ · Апаратний PWM | `наявна` ×2 |
| ШІМ на мікроконтролері · Шпаруватість і роздільність | `+ref programming/embedded-systems/pwm-on-mcu`, `+ref programming/embedded-systems/pwm-resolution` |
| Комплементарний ШІМ і мертвий час | **НОВА** · **СПІРНА** |
| Методи вимірювання частоти | `наявна` |
| Енкодерний режим таймера · Код Грея | `наявна` (частково), `+ref electronics/digital/gray-code` |
| Зв'язані таймери: майстер, підлеглий, внутрішній тригер | **НОВА** |
| RTC | `+ref programming/embedded-systems/rtc` |
| RTC і календарний час: батарейка, дрейф, мітки часу | `кандидат` · **СПІРНА** |

**СПІРНА · «Комплементарний ШІМ і мертвий час» — суперник: том 7 «Положення в просторі».**
Лишаю тут як **можливість таймера** (два комплементарні виходи, апаратна пауза між
ними), бо це рядок у reference manual і налаштування регістра. Навіщо це мосту й BLDC —
том 7, разом із самими моторами.

**СПІРНА · «RTC і календарний час» — суперник: том 5 «Комунікація».**
Апаратний RTC, резервний домен, батарейка й дрейф — мої. Синхронізація годинника
мережею (NTP/SNTP, PTP, мітки телеметрії) — том 5, там для цього є мережа.

---

### 9. Аналог у чипі

АЦП, ЦАП і компаратор як периферія мікроконтролера: не «як влаштований АЦП» (це було
в томі 2), а чому саме твоє вимірювання шумить і що з цим робити регістрами.
**Спирається на:** том 2 — дискретизація, квантування, типи АЦП; розділ 5 — час
вибірки рахується в тактах; розділ 7 — готовність приходить перериванням; розділ 8 —
запуск від таймера. **Вага:** ~11 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| АЦП | `наявна` |
| Типи АЦП · Конвеєрний АЦП | `наявна`, `+ref electronics/digital/pipeline-adc` |
| Вибірка і зберігання в АЦП | `+ref electronics/digital/adc-sample-hold` |
| Час вибірки АЦП і опір джерела | **НОВА** |
| Роздільність АЦП | `наявна` |
| ENOB: скільки розрядів справді працюють | `+ref electronics/digital/enob` |
| Похибки АЦП | `наявна` |
| Опорна напруга | `наявна` |
| Калібрування АЦП зовнішньою опорою | `наявна` |
| Внутрішні джерела АЦП: опора, датчик температури, VBAT | **НОВА** |
| Аналоговий мультиплексор і черга каналів | `+ref electronics/analog/analog-mux` |
| Апертурна невизначеність (jitter) | `+ref electronics/digital/aperture-jitter` |
| Передискретизація й децимація | `+ref electronics/digital/oversampling-decimation` |
| Аналогові блоки в МК: компаратор, ОП, програмований поріг | **НОВА** |
| ЦАП | `наявна` |
| DMA + АЦП | `наявна` |

---

### 10. Контролери обміну

Апаратні блоки, що возять байти замість процесора: DMA, його канали й пастки —
і периферійні контролери UART, SPI, I2C, USB з боку чипа, з регістрами, FIFO
й прапорцями помилок.
**Спирається на:** розділ 4 — адреси й вирівнювання; розділ 7 — переривання
завершення; розділ 9 — перший великий потік даних (безперервний АЦП).
**Вага:** ~14 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Проблема потоку даних | `наявна` |
| DMA-контролер | `наявна` |
| Канали й дескриптори | `+ref programming/computer-architecture/dma-channels` |
| GDMA: загальний пул каналів | `+ref programming/computer-architecture/dma-channels-gdma` |
| Scatter-gather DMA | `+ref algorithms/data-structures/scatter-gather` |
| Подвійна буферизація | `+ref programming/embedded-systems/double-buffering` |
| Шинна ієрархія AHB/APB · Матриця шин · Арбітраж шини | `+ref programming/computer-architecture/ahb-apb-bus`, `+ref programming/computer-architecture/bus-matrix`, `+ref programming/computer-architecture/bus-arbitration` |
| Пастки DMA · Когерентність кеша і DMA · Кеш-коерентність у МК | `+ref programming/systems/dma-cache-races`, `+ref programming/computer-architecture/cache-coherency-dma`, `+ref electronics/digital/cache-coherency-mcu` |
| UART: апаратний модуль і периферійний контролер | `+ref communications/interfaces/uart` |
| Швидкість baud · Baud проти біт/с · Допуск годинника UART | `наявна`, `+ref communications/buses/baud-vs-bitrate`, `+ref communications/buses/clock-tolerance-uart` |
| FIFO-регістри · Асинхронна черга FIFO | `+ref communications/buses/fifo-register`, `+ref electronics/digital/async-fifo` |
| Напівдуплекс UART · Break-сигнал UART | `+ref communications/buses/half-duplex-uart`, `+ref communications/buses/break-signal-uart` |
| SPI й I2C як блоки мікроконтролера: регістри, ведучий/ведений, прапорці помилок | **ВЛАСНА** |
| DMA + SPI/I2S | `наявна` |
| Розбір потоку | `+ref programming/embedded-systems/stream-parser` |
| CRC у прошивці | `+ref programming/embedded-systems/crc-in-firmware` |
| Подієва матриця: периферія запускає периферію | **НОВА** |
| RP2040 і PIO: програмована периферія | `+ref programming/embedded-systems/rp2040-pio` |
| Пристрій на шині USB: хост, енумерація, кінцеві точки | `+ref communications/buses/usb-device-basics` · **СПІРНА** |
| Кінцеві точки USB · USB в ESP32 | `+ref programming/peripherals/usb-endpoints`, `+ref programming/peripherals/esp32-usb` |
| Зовнішня пам'ять контролером: QSPI-флеш, PSRAM, FMC | `+ref communications/buses/quad-spi`, `+ref programming/peripherals/spi-flash`, `+ref programming/peripherals/psram`, `+ref electronics/digital/external-memory-interface` |
| Ethernet на МК | `+ref programming/embedded-systems/ethernet-on-mcu` · **СПІРНА** |

**СПІРНА · USB і Ethernet — суперники: том 4 і том 5.**
Мій крок — **блок усередині чипа**: він потребує рівно 48 МГц, він з'являється в карті
пам'яті, у нього кінцеві точки й DMA. Що таке хост, як влаштована енумерація, класи
USB, TinyUSB, стек TCP/IP — том 5. Роз'єм, кабель, диференційна пара, живлення з USB —
том 4. Беру мінімум, бо без нього незрозуміло, чому плата з'являється в системі
як COM-порт.

---

### 11. Будова прошивки

Коли периферії стало більше, ніж одна: чому `while(1)` із затримками ламається,
як живе неблокуючий цикл, автомат станів і черга подій, і скільки часу насправді
триває твій виток.
**Спирається на:** розділи 6–10 — є що складати разом; том 2 — скінченні автомати
вже відомі як апаратне поняття. **Вага:** ~9 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Super-loop | `+ref programming/embedded-systems/super-loop` |
| Межі super-loop | `наявна` |
| Блокуючий і неблокуючий ввід-вивід | `+ref programming/systems/blocking-vs-nonblocking-io` |
| Автомат станів і черга подій у прошивці | `кандидат` **ВЛАСНА** |
| Стан (патерн) | `+ref programming/design-patterns/state` |
| Цикл подій | `+ref programming/systems/event-loop` |
| Виробник–споживач · Черга з пріоритетом | `+ref programming/systems/producer-consumer`, `+ref algorithms/data-structures/priority-queue` |
| Backpressure: що робити, коли не встигаєш | `+ref programming/systems/backpressure-local` |
| Модель модуля | `+ref programming/embedded-systems/module-model` |
| Профіль часу виконання: цикли, переривання, джитер | `кандидат` **ВЛАСНА** |
| Деградація з гідністю | `+ref programming/embedded-systems/graceful-degradation` |

---

### 12. Багатозадачність

Другий спосіб зробити кілька справ одразу — віддати перемикання планувальнику:
задачі, пріоритети, черги, м'ютекси, стеки — і чесна відповідь, коли RTOS не потрібна.
**Спирається на:** розділ 11 — читач уже вперся в межі одного циклу; розділ 7 —
критичні секції й гонки; розділ 4 — стек у кожної задачі свій.
**Вага:** ~12 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Задачі | `наявна` |
| Процеси й потоки · Потоки настільної ОС проти задач RTOS | `+ref programming/systems/process-vs-thread`, `кандидат` |
| Планувальник | `наявна` |
| Перемикання контексту | `+ref programming/systems/context-switch` |
| Тик планувальника й режим без тику (tickless) | **НОВА** |
| Стеки задач | `наявна` |
| Черги й семафори | `наявна` |
| Спінлок і м'ютекс: вибір і ціна | `наявна` |
| Інверсія пріоритетів | `+ref programming/systems/priority-inversion` |
| Дедлок · Багато читачів, один письменник | `+ref programming/systems/deadlock`, `+ref programming/systems/readers-writer-lock` |
| Виклики RTOS із переривання (FromISR) | **НОВА** |
| Детермінованість | `наявна` |
| FreeRTOS | `наявна` |
| Вибір: голий цикл, FreeRTOS, Zephyr | **ВЛАСНА** |
| Багатоядерні процесори · Багатоядерні МК | `+ref programming/computer-architecture/multicore` · **СПІРНА** |
| Без замків | `+ref programming/systems/lock-free-basics` · **СПІРНА** |

**СПІРНА · багатоядерність і lock-free — суперник: том 10.**
Беру по одному оглядовому кроку (RP2040 і ESP32 двоядерні, і читач це побачить одразу),
але справжня модель пам'яті між ядрами, lock-free черги й когерентність — том 10.
Якщо том 10 забирає обидва — не заперечую.

---

### 13. Пошук помилок

Розділ про те, що кусає: HardFault без жодної підказки, зіпсований чужим переповненням
глобал, «у debug працює — у release падає», сторожовий таймер, що перезавантажує плату
під час зупинки, і чим це все ловлять.
**Спирається на:** усі попередні — це закриття тому; розділ 2 дав відлагоджувач,
розділ 4 — стек і причину скидання, розділ 5 — watchdog.
**Вага:** ~12 кроків.

**Розкладка:**

| тема | статус |
|---|---|
| Систематичний пошук несправності | `наявна` |
| Розбір HardFault | `наявна` |
| Посмертний аналіз | `наявна` |
| Декодування адрес аварії: addr2line та символи | `наявна` |
| Читання дизасемблера: від рядка C до інструкцій | **НОВА** |
| Вбудований асемблер у C/C++ | `+ref programming/languages/inline-assembly` |
| «Працює в debug, падає в release» | **ВЛАСНА** |
| Оптимізації компілятора · Правило «ніби» · Оптимізація на етапі лінкування | `+ref programming/languages/compiler-optimizations`, `+ref programming/languages/as-if-rule`, `+ref programming/languages/link-time-optimization` |
| Безпека роботи з пам'яттю | `наявна` |
| Динамічні санітайзери: ASan, UBSan | `+ref programming/languages/dynamic-sanitizers` |
| Налагодження на хості: gdb і санітайзери | `кандидат` |
| Assert і паніка · Захисне програмування | `наявна` ×2 |
| Жодна помилка не мовчить | `+ref programming/software-engineering/error-handling` |
| Порівняння каналів налагоджувального виводу | `наявна` |
| printf на пристрої: послідовний монітор і його ціна | `кандидат` |
| Семіхостинг · RTT · Трасування: ITM, SWO, ETM | `+ref programming/embedded-systems/semihosting`, `+ref programming/embedded-systems/rtt`, `+ref programming/embedded-systems/trace-itm-swo` |
| Профілювання | `+ref programming/software-engineering/profiling` |
| Логічний аналізатор | `наявна` · **СПІРНА** |
| Внутрішня логіка декодера протоколів | `+ref electronics/digital/protocol-decoder-internals` |
| Errata: коли винен чип, а не ти | **ВЛАСНА** |

**СПІРНА · «Логічний аналізатор» — суперник: том 4.**
Прилад приходить тоді, коли ним є що робити (правило 15): тут читач дивиться **свої
власні ніжки** — чи справді ШІМ 20 кГц, чи справді ISR укладається. Декодування чужої
шини (I2C-транзакція, кадр SPI) — том 4, і там прилад повертається вже з декодерами.

---

## Не лягло нікуди — куди йде

### → Том 2 «Аналогові й цифрові пристрої та сигнали»
- Скінченні автомати · Метастабільність · Тактовий сигнал · Лічильники — апаратний бік, до мене приходять уже відомими.
- Фізика комірок · NOR і NAND · EEPROM і FRAM · MRAM, RRAM і PCM · Коли пам'яті мало · Вибір пам'яті.
- Від PAL до FPGA · Потік розробки · HDL — я лишаю лише «FPGA чи МК» як крок вибору.
- `+ref electronics/digital/clock-domain-crossing`, `electronics/digital/sampling-quantization`.

### → Том 4 «Периферія МК»
- Як чипи розмовляють: навіщо шини · Асинхронна передача · Кадр UART · Шина I2C · Адресація I2C · Транзакція I2C · Регістрова карта · Розрахунок підтяжки · Шина SPI · Лінії SPI · Режими CPOL/CPHA · Вибір кристала · SPI проти I2C · Перетворювач рівнів · Диференційна пара · RS-485 · Арбітраж CAN.
- Увесь резерв `communications/buses/*` (40 статей: `spi-modes`, `i2c-bus-timing`, `i2c-bus-capacity`, `clock-stretching`, `daisy-chain-spi`, `one-wire`, `i3c`, `smbus`, `sd-card-protocol`, `drdy-pattern`, `burst-read`…) — це «двоє домовилися», не «чип уміє говорити».
- Матрична клавіатура · GPIO-розширювач (`+ref electronics/digital/gpio-expander`) · 74HC595 / 74HC165 / 74HC138 · Адресні світлодіоди · дисплеї.
- SD-карта, зовнішня QSPI-флеш і PSRAM як **пристрої** (контролер у чипі — мій, деталь на платі — його).
- Драйвер чипа: від регістрової карти до значення в SI `кандидат`.

### → Том 5 «Комунікація»
- Енумерація USB · Класи USB · TinyUSB: пристрій · Веб-сервер на МК · TLS на мікроконтролері · RPC у вбудованих системах.
- Синхронізація часу в мережі: NTP і мітки телеметрії `кандидат`.

### → Том 6 «Керування живленням»
- Цикл і середній струм · Споживання плати · Аудит струму спокою плати · Виміряти споживання · Логер споживання · Вимірювання профілю струму.
- `+ref electronics/microelectronics/subthreshold-leakage`, `programming/embedded-systems/battery-budget`, `current-paths`.

### → Том 7 «Положення в просторі»
- Оптичний енкодер як пристрій (енкодерний режим таймера — мій) · H-міст і BLDC (мертвий час — мій).

### → Том 9 «Безпека і перешкоди»
- Безпечний стан · Послідовність graceful reset · Перезавантаження · Захист від зникнення живлення: brown-out і рятування стану.
- Тестування відмовостійкості: fault injection · FMEA у вбудованих системах.
- `+ref algorithms/data-structures/single-event-upset`, `algorithms/data-structures/ecc-memory`, `algorithms/data-structures/bit-flips`.

### → Том 10 «Архітектура IoT» (глибоке програмування)
- Контроль версій і git · Стратегії гілкування в git · Гілки, ребейз і пошук регресії — **СПІРНА**, див. нижче.
- Мова CMakeLists · Цілі й властивості CMake · увесь резерв `build-systems/cmake/*`.
- Тестування прошивки · Модульний тест · Дублери: стаб, мок, фейк · Статичний аналіз · CI для прошивки · HIL-стенд · Python для автоматизації тестування.
- Принципи SOLID · Патерни поширення помилок · увесь резерв `programming/software-design/*` (шарова архітектура, зчеплення й зв'язність, дизайн API, глобальний стан) і `programming/design-patterns/*`.
- Навіщо зберігати · Wear leveling · Цілісність запису · Інтеграція FatFs · `+ref programming/systems/flash-filesystems`, `log-structured-storage`, `persistent-storage`.
- Модель акторів · Канали і CSP · Пул потоків · async/await · Thread-per-core.
- Вбудований Linux: коли МК замало `кандидат` · Архітектура прошивки: шари, події, межі модулів `кандидат` · Журналювання на борту `кандидат` · Параметри пристрою: дефолти, валідація, міграція `кандидат`.

### → Том 15 «Продукт»
- Bootloader · Таблиця розділів · Бюджет часу завантаження · OTA-слоти · OTA-оновлення · Серверна частина OTA · Secure boot · TPM і TrustZone.
- Версіювання прошивки й сумісність протоколу `кандидат` · Читання прошивки з чипа `кандидат` · `+ref programming/software-engineering/semantic-versioning`.
- *(ROM-завантажувач, BOOT-піни й option bytes лишаються в мене — це механізм чипа, а не політика оновлень.)*

---

## Діри — чого том потребує, а курс цього не веде

### `+ref` — стаття вже написана, треба лише завести крок

Резерв закрив більше, ніж я сподівався: **164 різні статті** з `pool-embedded.md`, зокрема
цілі вузли, які попередній прохід оголосив би дірами:

| що вважалося дірою | насправді написано |
|---|---|
| кільцевий буфер між ISR і циклом | `algorithms/data-structures/ring-buffer`, `algorithms/data-structures/queue-fifo` |
| DMA глибше за «є такий контролер» | `programming/computer-architecture/dma-channels`, `dma-channels-gdma`, `cache-coherency-dma`, `programming/systems/dma-cache-races`, `algorithms/data-structures/scatter-gather`, `programming/embedded-systems/double-buffering` |
| внутрішні шини чипа | `programming/computer-architecture/ahb-apb-bus`, `bus-matrix`, `bus-arbitration`, `electronics/digital/system-bus`, `address-decoding` |
| UART з боку чипа | `communications/interfaces/uart`, `communications/buses/clock-tolerance-uart`, `fifo-register`, `half-duplex-uart`, `break-signal-uart`, `baud-vs-bitrate` |
| канали налагоджувального виводу | `programming/embedded-systems/rtt`, `semihosting`, `trace-itm-swo`, `swd-jtag-internals`, `breakpoints-watchpoints`, `step-debugging`, `debug-vscode` |
| межі ніжки GPIO | `electronics/digital/pin-drive-limits`, `drive-strength`, `slew-rate-gpio`, `esd-gpio-protection`, `hi-z-state`, `active-low`, `wired-or` |
| дерево тактування (частини) | `electronics/digital/clock-domain`, `frequency-divider`, `prescaler`, `ring-oscillator`, `clock-gating`, `spread-spectrum-clocking`, `rtc-domain-power`, `electronics/microelectronics/power-gating` |
| якість АЦП | `electronics/digital/adc-sample-hold`, `enob`, `aperture-jitter`, `oversampling-decimation`, `pipeline-adc` |
| мова прошивки | `programming/languages/volatile`, `undefined-behavior`, `strict-aliasing`, `unsigned-overflow`, `raii`, `constexpr`, `zero-cost-abstractions`, `translation-unit`, `weak-symbols`, `elf-format`, `preprocessor-macros`, `abi-calling-convention` та ще 8 |
| RTOS зсередини | `programming/systems/context-switch`, `priority-inversion`, `deadlock`, `readers-writer-lock`, `process-vs-thread`, `lock-free-basics`, `data-races-locks`, `memory-ordering-barriers` |
| захист пам'яті на МК | `electronics/digital/mpu-cortex-m`, `programming/computer-architecture/protection-rings`, `address-space-separation` |

### `НОВА` — теми немає ніде, вона самодостатня

| тема | куди завести | чому атом |
|---|---|---|
| Крос-компіляція: хост, ціль, sysroot | `reference/build-systems` / `toolchains` | питання «а в якій версії GCC?» доречне — це рукотворний інструмент |
| Скрипт лінкера: як секції лягають в адреси | `reference/build-systems` / `toolchains` | формат і мова GNU ld, самодостатньо |
| Map-файл: що з'їло флеш і RAM | `reference/build-systems` / `toolchains` | артефакт лінкера, читається однаково скрізь |
| Затримки читання флеш-пам'яті й тактова частота | `book/electronics` / `digital` | явище: час доступу пам'яті проти періоду такту |
| Латентність переривання: від фронту до першої інструкції | `book/programming` / `embedded-systems` | вимірне явище будь-якого ядра |
| Зв'язані таймери: майстер, підлеглий, внутрішній тригер | `book/programming` / `embedded-systems` | механізм периферії, не залежить від курсу |
| Комплементарний ШІМ і мертвий час | `book/programming` / `embedded-systems` | самодостатній режим таймера |
| Час вибірки АЦП і опір джерела | `book/electronics` / `digital` | RC-заряд конденсатора вибірки — чиста фізика вимірювання |
| Внутрішні джерела АЦП: опора, датчик температури, VBAT | `book/programming` / `embedded-systems` | типовий блок будь-якого МК |
| Аналогові блоки в МК: компаратор, ОП, програмований поріг | `book/programming` / `embedded-systems` | периферія, що є майже скрізь |
| Подієва матриця: периферія запускає периферію | `book/programming` / `embedded-systems` | механізм (EVSYS / DMAMUX / TRGO), самодостатній |
| Тик планувальника й режим без тику (tickless) | `book/programming` / `embedded-systems` | механізм RTOS, не залежить від курсу |
| Виклики RTOS із переривання (FromISR) | `book/programming` / `embedded-systems` | правило будь-якої RTOS |
| Читання дизасемблера: від рядка C до інструкцій | `book/programming` / `languages` | навичка мови, поруч із `inline-assembly` |

### `ВЛАСНА` — тему може дати лише курс

| тема | розділ | чому атом цього не може |
|---|---|---|
| Документація чипа: даташит, reference manual, errata, приклади | 1 | це не знання, а **порядок дій у конкретному завалі паперу**; стаття мусить вести читача крізь уже знайомий йому чип і вже поставлене питання |
| Плата розробника: що на ній крім чипа | 1 | зшиває живлення (том 1), кварц (том 2), USB↔UART, кнопки й перемички — атом мусив би переказати чотири теми |
| Способи залити прошивку: SWD, DFU, UART-завантажувач, накопичувач | 2 | вибір, а не механізм: залежить від того, що читач уже має на столі |
| Стартовий код: від Reset_Handler до main | 4 | зшиває таблицю векторів, секції, лінкер і C-рантайм в один наскрізний прохід по конкретному файлу |
| Коли чип падає: причина скидання й HardFault з першого погляду | 4 | ранній короткий дотик, свідомо неповний; повне розкриття — розділ 13 (правило 14) |
| ROM-завантажувач: як чип приймає прошивку, коли в ньому ще нічого немає | 5 | у кожного сімейства свій; курс дає **спільну картину** й порядок дій |
| Фьюзи, option bytes і як не зробити цеглинку | 5 | практична пересторога з наслідками, а не опис регістра |
| Розкладка виводів: конфлікти альтернативних функцій | 6 | наскрізна вправа: розкласти периферію проєкту по ніжках і побачити зіткнення |
| Дисципліна обробника: що в ISR робити не можна | 7 | перелік заборон, кожна з яких має причину в іншій темі (стек, м'ютекс, printf, DMA) |
| Критична секція на МК: як правильно вимкнути переривання | 7 | зшиває пріоритети, `volatile`, бар'єри й RAII в один прийом |
| SPI й I2C як блоки мікроконтролера | 10 | навмисно **не** про шину: лише регістри, прапорці, помилки й прив'язка до ніжок — атом такого зрізу не має |
| Автомат станів і черга подій у прошивці | 11 | зшиває таймери, переривання, кільцевий буфер і патерн State у працюючий каркас |
| Профіль часу виконання: цикли, переривання, джитер | 11 | цілісний практичний вклад: виміряти власний цикл і назвати винного |
| Вибір: голий цикл, FreeRTOS, Zephyr | 12 | рішення, що спирається на пройдені розділи 11 і 12 |
| «Працює в debug, падає в release» | 13 | одна історія з чотирьох тем: оптимізації, UB, `volatile`, стек |
| Errata: коли винен чип, а не ти | 13 | навичка й порядок дій, а не явище |

**Разом: 164 `+ref`, 14 `НОВА`, 16 `ВЛАСНА`.**

Пропорція навмисна й важлива: **резерв покриває майже все**, чого том потребує понад
наявні кроки курсу. Дір, які довелося вигадувати, лише тридцять — і це переважно
речі, яких у підручниках справді немає: option bytes і цеглинка, конфлікт альтернативних
функцій ніжки, час вибірки АЦП проти опору джерела, errata, «працює в debug — падає
в release».

---

## Заперечення

### 1. Межа «прошивка базово тут / глибоке програмування в томі 10» — приймаю критерій і додаю друге сито

Критерій попереднього проходу — **«якщо відповідь міняється, коли з'являється другий
пристрій або другий програміст, це том 10»** — робочий, і я його беру. У ньому є одна
дірка: він мовчить про глибину. За ним виходить, ніби складне належить томові 10,
а просте — томові 3, і тоді скрипт лінкера, дерево тактів і розбір HardFault (усе
складне, усе на одному чипі й одному авторі) поїде не туди.

Тому додаю **друге сито, про природу знання, а не про його вагу**:

> **Знання, прив'язане до кремнію в руках, — том 3, хай яке глибоке.** Карта регістрів,
> дерево тактів, стартовий код, скрипт лінкера, регістри фолту, errata, час вибірки
> АЦП, латентність переривання.
>
> **Знання про те, як не зіпсувати чужу й майбутню роботу, — том 10, хай яке просте.**
> Межі модулів, шари, портовність, тести, версії, дизайн API, гіт-процес.

І **розв'язання нічиєї**, коли сита розходяться: перемагає питання **«що зупиняє першу
плату цього тижня»**. Воно в томі 3.

Три перевірки на місці:
- *Гонка з обробником переривання.* Один чип, один автор — перше сито мовчить. Друге:
  це поведінка ядра й компілятора → том 3. Тижнева перевірка: так, зупиняє. ✔
- *Шарова архітектура драйверів.* Один чип, один автор — перше сито мовчить, але
  питання існує лише тому, що завтра буде другий давач і другий автор → том 10. ✔
- *RTOS.* Автор прямо сказав «там і ртос» — і сита погоджуються: задача, планувальник,
  черга, м'ютекс потрібні, щоб **цей** чип робив дві справи одразу (том 3), а от
  проєктування системи задач і подій під продукт — том 10.

**Одна СПІРНА, де я не згоден із власним ситом: git.** За обома ситами контроль версій —
том 10. Але «вчора працювало» — це найчастіше питання відлагодження на світі,
і `git diff` відповідає на нього швидше за будь-який брейкпоінт. Пропоную: **том 10
бере гілкування, ребейз і процес**, а мені лишити **один крок у розділі 13** — коміт,
diff, revert, bisect як інструмент пошуку помилки. Якщо том 10 не погодиться —
поступаюся, це не смертельно.

### 2. Шини — том 4 має рацію, і я уточнюю межу

Начерк автора дав «шини» мені, а «протоколи» томові 4. Заперечення тому 4 —
**шину неможливо показати на одному чипі** — правильне, і я його приймаю. Але сама
пара «шина / протокол» межі не проводить: це одне й те саме на двох рівнях, і сперечатися
про слова можна нескінченно.

Пропоную межу за **джерелом відповіді**:

> **Том 3 — усе, що написано в reference manual МОГО чипа.** Регістри блоку, дільник
> швидкості й похибка від мого такту, глибина FIFO, прапорці помилок, лінії запиту DMA,
> прив'язка до ніжок через мультиплексор, електричні межі виводу.
>
> **Том 4 — усе, що написано в даташиті ЧУЖОГО чипа або в специфікації шини.**
> Адресація й арбітраж, CPOL/CPHA як домовленість із веденим, підтяжки й ємність лінії,
> зсув рівнів, топологія, кадр, CRC, пошук пристроїв.

Коротко: **том 3 — «чип уміє говорити», том 4 — «двоє домовилися».** Резерв підтвердив
межу сам собою: 40 статей `communications/buses/*` — це майже суцільно другий стовпчик,
а `communications/interfaces/uart` («апаратний модуль і периферійний контролер») —
перший.

Спіраль там, де межа розмита: **CPOL/CPHA** я даю як два біти регістра, том 4 — як
питання «звідки взяти правильний режим для цього давача». **USB** беру рівно як блок
у карті пам'яті; хост, енумерація й класи — том 5.

### 3. Курс не має тому, де вчать програмувати. Це справжня діра, і я її не закриваю — я її позначаю

У переліку п'ятнадцяти томів немає жодного про програмування. Корпус має близько
тридцяти написаних тем мови й моделі пам'яті. Попередній прохід узяв їх сюди, бо іншого
місця немає. Я роблю так само — і вважаю це найслабшим місцем усього тому.

**Чому все-таки беру.** Правило 12 залізне: крок не має права вимагати того, чого читач
не бачив. Читач тому 3 після другого розділу мусить написати рядок C. Том 10 стоїть
через шість томів після — усі вони потребують коду. Отже мова мусить бути тут, іншого
місця в межах правил немає.

**Чому це погано.** Том зветься «Мікроконтролери», а один із тринадцяти його розділів —
підручник мови. Це дзеркало помилки, за яку автор бив шість разів: **назва не сміє
обіцяти те, чого в томі немає — але й том не сміє містити те, чого назва не обіцяє.**
І це не «мікрокнига всередині тому», а чужорідне тіло: розділ 3 єдиний, який можна
вийняти й читати окремо, нічого не втративши.

**Що пропоную авторові.** Один із двох ходів:

1. **Окремий том «Програмування» між томами 2 і 3** — 8–10 розділів: мова, пам'ять,
   структури даних, збірка, інструмент, гіт. Тоді мій розділ 3 зникає, том 3 має
   12 розділів і чесну назву, а том 10 отримує справжню базу, на яку спиратися.
2. **Вхідна умова курсу** — «читач уміє писати найпростіші програми будь-якою мовою».
   Тоді мій розділ 3 стискається з ~15 кроків до ~7 і стає тим, чим має бути:
   **«C і C++ очима чипа»** — типи фіксованої ширини, `volatile`, біти, відсутність
   купи, ціна C++.

Мій голос — за **другий варіант**. Обіцянка курсу — «людина без освіти **в електроніці**»,
а не «людина, що ніколи не бачила коду»; курс уже й так найдовший із трьох у репозиторії.
Але рішення авторове, і поки його немає, розділ стоїть у повному вигляді, бо порушити
правило 12 гірше, ніж мати чужорідний розділ.

### 4. Дрібніше заперечення: «периферія як виходи з МК» у начерку — це два різні розділи

Автор написав про том 3: «шини, периферія як виходи з МК чи щось таке». Під цим
ховаються дві незалежні речі, які я розвів навмисно: **ніжка як електричний вихід**
(розділ 6 — струм, підтяжка, відкритий стік, захист) і **блок як контролер обміну**
(розділ 10 — регістри, FIFO, DMA). Об'єднати їх в один розділ означало б або назву-перелік,
або 25 кроків. Це саме той випадок, коли «назва виходить переліком» сигналить,
що межу треба переробити, а не назву добирати.

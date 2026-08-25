# План перебудови курсу «Вбудована електроніка й автономні системи»

**Статус: ЗАСТОСОВАНО 2026-07-02.** Маніфест переписано у v5-схему (modules → chapters → steps, 33 модулі), 95 тек власних статей перенесено (git mv) у теки нових модулів, img-шляхи переписано, нові статті отримали basic:pending. Тексти статей не змінювались. Цей файл — довідка про структуру і черга нового письма.

Це результат багатоагентного аналізу (14 агентів — по одному на кожну поточну секцію, 6 наскрізних: «новачок», «повнота домену», «області», «ідеальний курикулум», «граф залежностей», «компетентності випускника»; усі — Fable-max). Зведення й фінальні рішення — головна сесія.

**Позначення кроків:**
- `[ref: книга/slug]` — чинна тема курсу (посилання на статтю книги), лишається/переїжджає;
- `[own: slug]` — чинна власна стаття курсу;
- `[add: книга/slug]` — ДОДАТИ ref на **вже наявну** статтю книги (у дужках: done — стаття готова, pending — заведена в книзі, але не написана);
- `[new: slug]` — ДОДАТИ **нову власну статтю курсу** (писати з нуля);
- `⟵ секція` — тема переїжджає з указаної поточної секції.

Пріоритети додавань: **(крит)** — без цього новачок не пройде; **(важл)** — помітна діра; **(пізн)** — на виріст.

---

## 1. Діагноз (чому курс зараз «ламається»)

1. **Теми вимагають ще не поданих знань** — системно, а не точково. Найяскравіше: транзисторні й ОП-теми сидять у секції 2 «Кола», хоча напівпровідники з'являються лише в секції 4, а операційний підсилювач **не вводиться ніде**; `datasheet-mcu` (даташит мікроконтролера) стоїть у секції 3 — за чотири секції до появи МК; MAVLink, автономні місії та Edge AI сидять у середині курсу (секція 7 «МК») — до периферії, давачів, PID і радіо.
2. **Цілих шарів бази немає, хоча курс ними користується:** мова C і вхід у програмування (аудиторія — «нуль програмування», а перші proj-вставки з кодом — уже в секції 2!), цифрова логіка (вентилі, тригери — а курс одразу дає зсувний регістр і FPGA), GPIO/таймери/PWM/АЦП як кроки, UART, RTOS/FreeRTOS (для ESP32-курсу!), watchdog, bootloader/OTA-клієнт, мотори, мережевий стек (Wi-Fi/сокети/MQTT — головна причина обирати ESP32), «як літає дрон».
3. **Секції — пласкі списки по 5–47 тем** без розділів; межі розмиті (прошивка = осцилограф + SOLID + FMEA упереміш), кластери розірвані (пам'яті розкидані по 3 секціях, вимірювання споживання — по 4 темах у 3 секціях, MAVLink — по 2 секціях).
4. **Курс не використовує книгу `programming/` взагалі** (жодного ref при 356 темах, з них ~177 у галузі embedded-systems, десятки готових done) — а також `algorithms/` і `math/`. Це головний важіль: **більшість критичних дір закривається готовими done-статтями книг, без нового письма.**

Добра новина: сам матеріал сильний (аналогова частина, живлення, керування/DSP — глибші за канон), проблема — **розкладка й відсутні сходинки**, не якість статей.

## 2. Принципи нової структури

1. **Строга кумулятивність:** кожен крок спирається лише на пройдене; кожен модуль відкривається «місточком», що зшиває з попереднім, а не найважчою темою.
2. **Десять частин курсу** — аналоговий світ → цифровий світ → прошивка → взаємодія зі світом → зв'язок і дані → медіа → машинне навчання → автономність → платформи → виріб. Усередині частини модулі теж строго впорядковані.
   Автономність — **не лише дрони**: спільне ядро (автопілот, канал керування, MAVLink, навігація й місії) одне для коптера, літака, ровера/НРК і стаціонарного домашнього вузла; платформи розведені окремими модулями (дім · земля · небо) з капстоуном на обраній платформі.
3. **Модуль = 10–30 кроків, розділ = 4–10 кроків.** Розділи — новий рівень (див. §7 «Технічна примітка»).
4. **Вертикалі зібрані:** компонент вводиться там, де вперше потрібен колу; всі пам'яті — в одному модулі; все вимірювання споживання — в одному розділі; весь MAVLink — у дроновому модулі.
5. **Інструменти — рано:** мультиметр і макетка з'являються в модулі 2, осцилограф — у модулі 3 (зараз усе це в секції 9).
6. **ref-и вплетені, а не стіною:** довгі черги ref-ів розбиті власними статтями-зшивками курсу; де курсу потрібна кумулятивна розповідь — стоїть own, де досить атома — ref.

## 3. Нова мапа модулів (огляд)

| № | Модуль | З чого складається | Кроків ≈ |
|---|--------|--------------------|----------|
| **Частина I. Електрика й аналоговий світ** | | | |
| 1 | Електрика: заряд, струм, енергія | ядро osnovy | 29 |
| 2 | Перші кола й інструменти | kola (DC-ядро) + резистор з komponenty + прилади | 24 |
| 3 | Змінний струм, конденсатор і котушка | AC/магнетизм/шуми з osnovy + пасив з komponenty + RC/RL з kola | 36 |
| 4 | Напівпровідники: діод і транзистор | napivprovidnyky + діодне з komponenty + транзисторне з kola | 25 |
| 5 | Аналогові схеми: ОП і генератори | ОП-блок з kola + резонатори з komponenty | 26 |
| 6 | Компоненти на практиці: даташити, захист, тепло, монтаж | практичні теми komponenty | 14 |
| 7 | Живлення | zhyvlennia (аналогове ядро) | 31 |
| **Частина II. Цифровий світ** | | | |
| 8 | Цифрова логіка й пам'ять | НОВИЙ каркас (ref-и) + cyfra-pamyat + пам'яті з napivprovidnyky | 31 |
| 9 | Вхід у програмування: числа, C, тулчейн | **НОВИЙ** (ref-и programming + нові C-статті) | 33 |
| 10 | Мікроконтролер: знайомство й перша прошивка | ядро mk | 19 |
| 11 | Периферія МК: GPIO, таймери, АЦП, DMA | теми mk + НОВИЙ каркас (ref-и) | 33 |
| 12 | Шини й з'єднання | peryferiia + шинні ref-и + dma-spi-i2s з mk | 24 |
| **Частина III. Прошивка** | | | |
| 13 | Системний шар: RTOS, зберігання, оновлення, сон | НОВИЙ каркас (ref-и) + теми з proshyvka/mk/zhyvlennia | 31 |
| 14 | Налагодження й вимірювання пристрою | дебаг-теми з mk + вимірювання з proshyvka/mk | 16 |
| 15 | Інженерія якості прошивки | інженерні теми proshyvka | 15 |
| **Частина IV. Взаємодія зі світом** | | | |
| 16 | Дисплеї й індикація | dyspleyi + led-animation | 10 |
| 17 | Давачі | davachi + вступні ref-и | 22 |
| 18 | Мотори й привід | **НОВИЙ** (ref-и) + servo/esc з drony | 15 |
| 19 | Сигнали й керування | keruvannia + vibration з davachi + loop-gain з zhyvlennia | 29 |
| **Частина V. Зв'язок і дані** | | | |
| 20 | Радіо: фізика лінка й антени | радіо-ядро zvyazok + децибели/модуляція/антени ref-ами | 16 |
| 21 | Передача даних і мережі | **новий розділ «Передача даних»** + стандарти й стек із zvyazok | 23 |
| **Частина VI. Медіа** | | | |
| 22 | Звук на пристрої | **НОВИЙ**: мікрофон/динамік/клас D + цифровий звук + обробка + запис | 12 |
| 23 | Зображення й відео | камера → демозаїка → класична обробка (CV-галузь algorithms) → глибина → кодеки/стрімінг | 23 |
| **Частина VII. Машинне навчання** | | | |
| 24 | Машинне навчання: основи | ML-галузь algorithms (7 done + pending): нейромережа, навчання, дані | 16 |
| 25 | Машинне навчання на мікроконтролері | квантування → інференс → детекція/KWS/аномалії; edge-inference/моделі з mk і drony | 16 |
| **Частина VIII. Автономність** | | | |
| 26 | Автопілот: бортовий мозок | архітектура FC + безпека (arming/failsafe/geofence) + налаштування й логи | 13 |
| 27 | Канал керування й зв'язок із землею | RC-протоколи (PWM/PPM/SBUS/CRSF/ELRS) + стабілізація/мікшування + MAVLink/GCS | 17 |
| 28 | Навігація й місії | GNSS глибше/RTK + EKF/кватерніони + планування шляху + місії й автономія | 18 |
| **Частина IX. Платформи** | | | |
| 29 | Стаціонарні пристрої і розумний дім | **НОВИЙ**: вузол + ESP-NOW + провізіонування + інтеграція HA/Matter | 5 |
| 30 | Наземні: ровер і НРК | **НОВИЙ**: шасі + кінематика + керування рухом + телекерування + вода | 6 |
| 31 | Повітряні: коптер, літак, VTOL | **НОВИЙ**: фізика польоту + пропульсія + перший політ + літак/VTOL | 11 |
| 32 | Капстоун: автономна місія | **НОВИЙ**: наскрізний проєкт на обраній платформі + документація | 4 |
| **Частина X. Виріб** | | | |
| 33 | Виріб: плата, серія, сертифікація | **НОВИЙ, на виріст** (переважно pending/new) | 11 |

Разом: 285 чинних кроків збережено (жоден живий не викинуто; 1 битий ref physics/noise-interference — цілі не існує — замінено на physics/shot-flicker-noise), 306 додавань ref-ами наявних статей книг, 52 нові статті курсу (з них критичних ~15) — усього 643 кроки. Числа звірено скриптом.

---

## 4. Нова структура — повний зміст

### Модуль 1 — Електрика: заряд, струм, енергія
*Фізичний фундамент. Читач ще нічого не знає; тут — тільки якісна фізика без схемотехніки. Після модуля: розуміє заряд, поле, напругу, струм, опір, потужність і тепло.*

**1. Заряд і поле**
- [ref:physics/electric-charge] Електричний заряд
- [ref:physics/elementary-charge] Елементарний заряд і квантування
- [ref:physics/charge-conservation] Закон збереження заряду
- [ref:physics/coulomb-law] Закон Кулона
- [ref:physics/electric-field] Електричне поле
- [ref:physics/electric-potential] Електричний потенціал
- [ref:physics/voltage] Напруга як різниця потенціалів
- [own:field-and-potential] Поле й потенціал *(зшивка блоку — впритул до свого матеріалу, зараз стоїть після магнетизму)*
- [own:electrostatics-summary] Зведення електростатики *(закриває блок перед струмом)*

**2. Струм**
- [ref:physics/electric-current] Електричний струм
- [ref:physics/current-direction] Напрямок струму: технічний і реальний
- [ref:physics/electron-drift] Дрейф електронів
- [ref:physics/signal-speed] Швидкість сигналу проти дрейфу носіїв
- [ref:physics/current-continuity] Неперервність струму
- [ref:physics/ionic-conduction] Іонна провідність

**3. Опір**
- [ref:physics/resistance-origin] Природа опору
- [ref:physics/resistivity] Питомий опір і провідність
- [ref:physics/resistance] Електричний опір
- [ref:physics/resistance-temperature] Опір і температура

**4. Енергія і тепло**
- [ref:physics/electric-power] Електрична потужність
- [ref:physics/joule-heating] Джоулеве тепло
- [own:heat-transfer] Передача тепла *(підняти: зараз стоїть ПІСЛЯ теплового опору, який на ній будується)*
- [ref:physics/thermal-resistance] Тепловий опір і відведення тепла

**5. Джерело й коло**
- [ref:physics/closed-circuit] Замкнене коло й джерело ЕРС
- [own:emf-sources] Типи ЕРС: хімічна, теплова, світлова, індукційна *(зараз відірвана в кінці секції)*

**6. Електрика довкола нас**
- [ref:physics/triboelectricity] Трибоелектрика й заряд тіла
- [ref:physics/air-breakdown] Пробій повітря й іскра
- [own:lightning-protection] Захист від блискавки
- [ref:physics/faraday-cage] Клітка Фарадея *(тепер після струму/провідності, яких потребує)*

*Виїхали з osnovy: змінний струм і синусоїда (→ М3.1), магнетизм (→ М3.3), шуми й наводки (→ М3.7, бо потребують C і L), memory-cell-physics (→ М8.5, бо потребує транзистор і логіку).*

### Модуль 2 — Перші кола й інструменти
*Перша схемотехніка: тільки резистори і джерело — все, що вже відомо. Тут же читач бере в руки мультиметр і макетку. Після модуля: читає прості схеми, рахує будь-яку резистивну мережу, вміряє напругу/струм/опір.*

**1. Схема як мова**
- [own:reading-schematics] Читання схем *(підняти на самий початок — зараз стоїть 20-м кроком, хоча всі теми подано схемами)*
- [own:net-labels-buses] З'єднання без дротів: мітки, шини й міжаркушеві зв'язки

**2. Резистор у руках**
- [ref:electronics/resistor] Резистор ⟵ komponenty
- [ref:electronics/resistor-marking] Номінали й допуск ⟵ komponenty
- [ref:electronics/potentiometer] Потенціометр і підлаштовник ⟵ komponenty

**3. Закони кола**
- [ref:electronics/ohms-law] Закон Ома
- [ref:electronics/series-connection] Послідовне з'єднання *(перед дільниками — дільник і є послідовне з'єднання)*
- [ref:electronics/parallel-connection] Паралельне з'єднання
- [ref:electronics/voltage-divider] Дільник напруги
- [ref:electronics/current-divider] Дільник струму
- [ref:electronics/internal-resistance] Внутрішній опір джерела
- [ref:electronics/nodes-branches-loops] Вузли, вітки й контури
- [ref:electronics/kcl] Закон струмів Кірхгофа
- [ref:electronics/kvl] Закон напруг Кірхгофа

**4. Інструменти новачка**
- [add:electronics/multimeter] Мультиметр — (done) (крит: базовий інструмент, зараз у курсі відсутній узагалі)
- [add:electronics/lab-power-supply] Лабораторний блок живлення — (done) (важл)
- [new:breadboard-prototyping] Макетка й перший монтаж — (крит: теми немає в жодній книзі)
- [ref:electronics/kelvin-shunt] Струмовимірювальний шунт ⟵ proshyvka
- [add:electronics/measurement-errors] Похибки вимірювань — (done) (важл)

**5. Теореми й методи**
- [ref:electronics/superposition] Принцип суперпозиції
- [ref:electronics/thevenin] Теорема Тевеніна
- [ref:electronics/norton] Теорема Нортона
- [ref:electronics/power-matching] Узгодження навантаження за потужністю
- [ref:electronics/wheatstone-bridge] Міст Вітстона
- [own:circuit-analysis] Аналіз кіл *(зведення модуля)*

### Модуль 3 — Змінний струм, конденсатор і котушка
*Час і частота входять у гру. Компонент з'являється поруч із явищем: конденсатор — після синусоїди, котушка — після магнетизму. Тут-таки перший осцилограф: він потрібен, щоб ПОБАЧИТИ змінний сигнал. Після модуля: RC/RL-перехідні, фаза, імпеданс, перші фільтри, розуміння наводок.*

**1. Змінний струм**
- [ref:physics/dc-vs-ac] Постійний і змінний струм ⟵ osnovy
- [ref:physics/sine-wave] Синусоїда ⟵ osnovy
- [ref:physics/amplitude-frequency] Амплітуда, частота й період ⟵ osnovy
- [ref:physics/rms-value] Діюче значення ⟵ osnovy
- [own:frequency-wavelength] Частота й довжина ⟵ osnovy

**2. Конденсатор**
- [ref:electronics/capacitor] Конденсатор ⟵ komponenty
- [ref:electronics/capacitor-dielectrics] Діелектрики конденсаторів ⟵ komponenty
- [ref:electronics/supercapacitor] Суперконденсатор ⟵ komponenty
- [ref:electronics/rc-time-constant] Стала часу RC ⟵ kola *(тепер конденсатор уже введено)*

**3. Магнетизм**
- [ref:physics/magnetic-field] Магнітне поле ⟵ osnovy
- [ref:physics/oersted-experiment] Магнітне поле струму ⟵ osnovy
- [ref:physics/ampere-force] Сила Ампера ⟵ osnovy
- [ref:physics/electromagnet] Електромагніт ⟵ osnovy
- [ref:physics/ferromagnetism] Феромагнетизм і гістерезис ⟵ osnovy
- [ref:physics/electromagnetic-induction] Електромагнітна індукція ⟵ osnovy
- [ref:physics/hall-effect] Ефект Холла ⟵ osnovy

**4. Котушка і трансформатор**
- [ref:electronics/inductor-coil] Котушка ⟵ komponenty
- [ref:electronics/inductor-types] Осердя й насичення ⟵ komponenty
- [ref:electronics/ferrite-bead] Феритова намистина ⟵ komponenty
- [ref:electronics/rl-time-constant] Стала часу RL ⟵ kola
- [ref:electronics/mutual-inductance] Зв'язані котушки ⟵ komponenty
- [ref:electronics/transformer] Трансформатор ⟵ komponenty

**5. Фаза, реактивність, імпеданс**
- [ref:electronics/phase-shift] Фаза й зсув фаз ⟵ kola
- [add:electronics/reactance] Реактивність — (done) (крит: імпеданс ніде не вводиться, а на ньому стоять фільтри, узгодження, лінії передачі)
- [add:electronics/impedance] Імпеданс — (done) (крит)
- [ref:electronics/capacitor-parasitics] Паразити конденсатора ⟵ komponenty *(тепер ESL зрозуміла — котушка вже була)*

**6. Перші фільтри й резонанс**
- [add:electronics/rc-low-pass] RC-фільтр низьких частот — (done) (крит: «що таке фільтр» ніде не вводиться)
- [add:electronics/rc-high-pass] RC-фільтр високих частот — (done) (крит)
- [add:electronics/lc-resonance] LC-резонанс — (done) (важл)
- [own:cascaded-rc-filters] Каскадовані RC-ланки ⟵ kola
- [own:filter-families] Родини фільтрів: Баттерворт, Чебишов, Бесель ⟵ kola

**7. Шум і наводки**
- [ref:physics/thermal-noise] Тепловий шум ⟵ osnovy
- [add:physics/shot-flicker-noise] Дробовий шум — (done) (важл; замінює битий ref physics/noise-interference — такої цілі не існує в жодній книзі)
- [ref:physics/capacitive-coupling] Ємнісна наводка ⟵ osnovy *(тепер ємність відома)*
- [ref:physics/inductive-coupling] Індуктивна наводка ⟵ osnovy
- [own:noise-interference] Шум і завади *(інженерне зведення; стоїть поруч із ref-тезкою — узгодити назви, напр. «Шум і завади в пристрої»)* ⟵ osnovy

**8. Осцилограф**
- [add:electronics/oscilloscope] Осцилограф — (done) (крит: перший погляд на сигнал зараз аж у секції 9)
- [own:sine-on-scope] Синусоїда на осцилографі ⟵ proshyvka
- [own:noise-hunting] Полювання на заваду ⟵ proshyvka

### Модуль 4 — Напівпровідники: діод і транзистор
*Ключовий ремонт курсу: транзистор і діод вводяться ДО того, як ними користуються схеми. Після модуля: p-n перехід, діоди і їх застосування, BJT/MOSFET як ключі, оптоелектроніка, ESD.*

**1. Фізика напівпровідника**
- [add:physics/semiconductor] Напівпровідник — (done) (крит: зараз секція «напівпровідники» не містить напівпровідників)
- [add:physics/doping] Легування — (done) (крит)
- [add:physics/pn-junction] p-n перехід — (done) (крит)

**2. Діод**
- [own:diodes] Діоди *(стаття сама припускає пройдені zener-schottky і pn-junction — тепер це виконано)*
- [add:electronics/diode-iv-curve] ВАХ діода — (done) (важл)
- [own:zener-schottky] Діоди Зенера ⟵ komponenty
- [add:electronics/led] Світлодіод — (done) (крит: курс доходить до OLED-дисплеїв, жодного разу не ввівши світлодіод)

**3. Біполярний транзистор**
- [add:electronics/transistor-idea] Ідея транзистора — (done) (крит: транзистор ніде не вводиться, а вживається з секції 2)
- [add:electronics/bjt-operation] Як працює BJT — (done) (крит)
- [add:electronics/bjt-switch] BJT як ключ — (done) (крит)
- [own:bjt-load-driving] BJT: навантаження ⟵ kola
- [own:darlington-vs-sziklai] Пара Дарлінгтона проти Sziklai ⟵ kola
- [own:datasheet-bjt] Практикум даташитів: BJT ⟵ komponenty

**4. MOSFET і CMOS**
- [add:electronics/mosfet-structure] Будова MOSFET — (done) (крит)
- [add:electronics/mosfet-switch] MOSFET як ключ — (done) (крит)
- [own:bjt-vs-mosfet] BJT проти MOSFET ⟵ kola
- [add:electronics/nmos-pmos] NMOS і PMOS — (done) (важл)
- [add:electronics/cmos] CMOS — (done) (важл: місток до цифрової логіки М8)

**5. Оптоелектроніка й ізоляція**
- [add:electronics/led-photodiode] Фотодіод і фототранзистор — (done) (важл)
- [add:electronics/optocoupler] Оптопара — (done) (важл)

**6. Крихкість і захист**
- [ref:electronics/esd-damage] Електростатичний розряд
- [own:flyback-protection] Захист flyback ⟵ komponenty *(тепер діод і ключ відомі)*
- [own:surge-protection-cascade] Каскадний захист від перенапруги ⟵ komponenty

**7. Нові матеріали**
- [own:sic-gan-comparison] SiC і GaN: відмінності від кремнію

*Виїхали з napivprovidnyky: nor-vs-nand, eeprom-fram, mram-rram-pcm (→ М8.5 «Пам'яті» — це теми про пам'ять, не про діоди), power-fail-safety (→ М13.3 — потребує МК і прошивку).*

### Модуль 5 — Аналогові схеми: ОП і генератори
*Другий ремонт: операційний підсилювач нарешті вводиться. Після модуля: ОП-схеми, зворотний зв'язок, каскади, компаратор, генератори й тактові опори.*

**1. Операційний підсилювач**
- [add:electronics/opamp] Операційний підсилювач — (done) (крит: ОП не вводиться ніде, а на ньому стоїть шість тем курсу)
- [add:electronics/ideal-opamp] Ідеальний ОП — (done) (крит)
- [add:electronics/inverting-noninverting] Інвертувальний і неінвертувальний — (done) (крит)
- [own:kcl-opamp-analysis] KCL у вузлах схем на ОП ⟵ kola
- [add:electronics/real-opamp-limits] Межі реального ОП — (done) (важл)
- [own:opamp-input-types] Типи входів ОП: BJT, JFET, CMOS ⟵ kola
- [own:single-supply-opamp] ОП на однополярному живленні ⟵ kola

**2. Компаратор і поріг**
- [add:electronics/comparator] Компаратор — (done) (важл)
- [add:electronics/schmitt-trigger] Тригер Шмітта — (done) (важл: потрібен і кнопкам, і АЦП, і цифрі)

**3. Зворотний зв'язок і каскади**
- [own:feedback-topologies] Топології зворотного зв'язку ⟵ kola
- [own:dc-ac-bias] DC-зміщення і AC-сигнал у підсилювачі ⟵ kola
- [own:multistage-amplifier] Багатокаскадний підсилювач ⟵ kola
- [own:tail-current-source] Джерело струму хвоста: від резистора до каскоду ⟵ kola
- [ref:electronics/instrumentation-amp] Інструментальний підсилювач ⟵ kola
- [own:signal-conditioning] Кондиціонування сигналу ⟵ kola

**4. Генератори й тактові опори**
- [add:electronics/relaxation-oscillator] Релаксаційний генератор — (done) (важл)
- [add:electronics/555-astable] Таймер 555 — (done) (пізн: класика, гарний місток до генераторів)
- [add:electronics/crystal] Кварцовий резонатор — (done) (крит: кварц ніде не вводиться, а на ньому Пірс, TCXO і все тактування МК)
- [add:electronics/quartz-rlc-model] Еквівалентна схема кварцу — (done) (важл)
- [own:pierce-oscillator-design] Генератор Пірса: схема й розрахунок обв'язки кварцу ⟵ kola
- [own:ceramic-mems-resonators] Керамічні резонатори ⟵ komponenty
- [own:tcxo-ocxo] TCXO та OCXO ⟵ komponenty

**5. Узгодження**
- [own:impedance-matching-networks] Схеми узгодження імпедансів ⟵ kola *(імпеданс введено в М3.5)*

### Модуль 6 — Компоненти на практиці: даташити, захист, тепло, монтаж
*Практичний блок «залізо в руках»: як читати документацію, захищати схему, відводити тепло, паяти. Після модуля: читач упевнено бере незнайомий компонент і плату.*

**1. Даташити**
- [own:datasheet-practice] Практикум даташитів
- [add:electronics/min-typ-max] Min/typ/max і кутові випадки — (done) (важл)
- [own:energy-density-comparison] Щільність енергії та потужності: конденсатор, суперконденсатор, акумулятор

**2. Захисні компоненти**
- [own:fuses-ptc] Запобіжники
- [own:active-inrush-limiter] Активний обмежувач пускового струму
- [add:electronics/solenoid-relay] Реле й соленоїд — (done) (важл: реле ніде не вводиться)
- [add:electronics/relay-driver] Драйвер реле — (done) (важл)

**3. Друкована плата: перше знайомство**
- [new:pcb-intro] Що таке друкована плата: шари, доріжки, перехідні отвори — (крит: PCB-теми йдуть без введення самої плати)
- [own:pcb-assembly-methods] Методи монтажу плат (THT і SMD)
- [own:smd-rework] Ручне паяння SMD
- [add:electronics/basic-soldering] Базове паяння — (pending: заведено в книзі, ще не написано) (важл)

**4. Тепловий розрахунок**
- [own:thermal-budget] Тепловий бюджет системи
- [own:pcb-thermal-design] Тепловідведення на PCB

### Модуль 7 — Живлення
*Аналогове ядро живлення: все, що потрібно, вже введено (діоди, транзистори, ОП, трансформатор). Порядок «від простого до системи»: спершу що таке стабілізатор, потім топології, потім USB/батареї. Після модуля: читач проєктує вузол живлення пристрою.*

**1. Карта живлення пристрою**
- [own:power-tree-reading] Читання дерева живлення *(вступна навичка — з хвоста секції на початок)*
- [own:power-budget] Бюджет потужності пристрою

**2. Стабілізатори**
- [add:electronics/ldo] Лінійний стабілізатор (LDO) — (done) (крит: зараз «Вибір топології» стоїть до знайомства бодай з одним стабілізатором)
- [add:electronics/buck] Понижувальний перетворювач (buck) — (done) (крит)
- [add:electronics/boost] Підвищувальний перетворювач (boost) — (done) (крит)
- [own:linear-vs-switching] Лінійний vs імпульсний
- [own:ldo-post-regulator] LDO-постстабілізатор
- [own:topology-map] Вибір топології *(тепер це зведення після знайомства з топологіями)*

**3. Від мережі: випрямлення й фільтрація**
- [own:bridge-rectifier-design] Місток Гретца: схема і розрахунок
- [add:electronics/decoupling] Розв'язувальний конденсатор — (done) (крит)
- [own:power-supply-filtering] Фільтрація живлення: згладжувач і розв'язка разом
- [own:ac-switch-need] Ключі для мережі
- [own:emi-filter-design] Вхідний EMI-фільтр перетворювача

**4. Комутація навантажень**
- [own:pwm-power-control] Керування потужністю
- [own:inductive-load-switching] Комутація індуктивного навантаження
- [own:inductive-clamp-design] Розрахунок клампу для індуктивного навантаження

**5. Живлення через USB**
- [add:programming/usb-overview] USB: хост, пристрій, VBUS — (done) (крит: USB-кластер зараз іде без введення USB)
- [own:usb-power-map] Живлення через USB
- [own:pd-sink-design] PD у пристрої
- [own:usb-cables-field] Кабелі й сумісність
- [own:fast-charging-protocols] Протоколи швидкої зарядки

**6. Батареї і BMS**
- [own:battery-chemistries] Хімії батарей
- [add:electronics/li-ion-charger] Заряджання Li-ion — (done) (важл: хімії і BMS є, а самого заряду нема)
- [own:bms-architecture] Архітектура BMS: монітор комірок, ізоляція, контактор
- [own:active-balancing] Активне балансування: топології і вибір
- [own:battery-pack-thermal] Тепловий менеджмент батарейного пакета
- [own:thermal-runaway-protection] Захист від теплової втечі

**7. Захист входу живлення**
- [own:reverse-polarity] Захист переполюсування
- [own:esd-protection-circuits] ESD-захист у схемах

**8. Інженерія вузла живлення**
- [own:flyback-transformer-design] Проектування трансформатора flyback
- [own:power-spec-template] Шаблон ТЗ на вузол живлення

*Виїхали: usb-cc-adc-circuit (→ М11.7 — потребує АЦП), board-consumption і sleep-current-audit (→ М13.5 — потребують МК і режими сну), loop-gain-measurement (→ М19.4 — потребує теорію стійкості).*

### Модуль 8 — Цифрова логіка й пам'ять
*Третій ремонт: перед FPGA і зсувним регістром нарешті з'являється сама цифра — рівні, вентилі, тригери. Каркас цілком збирається з готових done-статей electronics/digital. Після модуля: від вентиля до FPGA і до розуміння, що таке пам'ять.*

**1. Навіщо цифра**
- [add:electronics/why-digital] Навіщо цифра — (done) (крит: зараз секція стартує зі зсувного регістра без жодного вентиля)
- [add:electronics/logic-levels-as-ranges] Рівні «0» і «1» як діапазони — (done) (крит)
- [add:electronics/noise-margin] Запас завадостійкості — (done) (важл)
- [add:math/boolean-algebra] Булева алгебра — (done) (важл)

**2. Вентилі й комбінаційні схеми**
- [add:electronics/basic-gates] Базові вентилі — (done) (крит)
- [add:electronics/nand-nor] NAND і NOR як універсальні — (done) (важл)
- [add:electronics/cmos-gate] Вентиль у кремнії: CMOS — (done) (важл; спирається на М4.4)
- [add:electronics/combinational-circuits] Комбінаційні схеми — (done) (важл)

**3. Тригери, такт, автомати**
- [add:electronics/state-memory] Пам'ять стану — (done) (крит)
- [add:electronics/sr-latch] SR-засувка — (done) (важл)
- [add:electronics/d-flip-flop] D-тригер — (done) (крит)
- [add:electronics/register] Регістр — (done) (крит)
- [ref:electronics/shift-register] Зсувний регістр *(нарешті після тригерів, з яких складається)*
- [add:electronics/clock-signal] Тактовий сигнал — (done) (крит)
- [add:electronics/counters] Лічильники — (done) (важл)
- [own:synchronous-reset] Синхронне й асинхронне скидання в цифрових схемах
- [add:electronics/metastability-timing] Метастабільність і таймінги — (done) (важл)
- [add:electronics/finite-state-machines] Скінченні автомати — (done) (крит: FSM — хребет прошивок далі)

**4. Програмована логіка**
- [own:pal-to-fpga] Від PAL до FPGA
- [own:fpga-flow] Потік розробки

**5. Пам'яті (зібраний кластер)**
- [own:memory-cell-physics] Фізика комірок ⟵ osnovy *(потребує транзистор і логіку — тепер вони є)*
- [own:nor-vs-nand] NOR і NAND ⟵ napivprovidnyky
- [own:eeprom-fram] EEPROM і FRAM ⟵ napivprovidnyky
- [own:mram-rram-pcm] MRAM, RRAM і PCM: нові нелеткі пам'яті ⟵ napivprovidnyky
- [own:when-memory-runs-out] Коли пам'яті мало
- [own:choosing-memory] Вибір пам'яті

**6. Швидка цифра**
- [ref:communications/transmission-lines] Лінія передачі на PCB: імпеданс і термінація *(імпеданс введено в М3.5)*
- [own:signal-integrity] Цілісність сигналу (signal integrity)
- [own:ddr-signal-integrity] Цілісність сигналу DDR-шини

*Виїхали: fpga-vs-mcu і custom-instruction (→ М10 — порівнюють із МК/процесором, яких ще не було).*

### Модуль 9 — Вхід у програмування: числа, C, тулчейн — **НОВИЙ МОДУЛЬ**
*Найбільша діра курсу: аудиторія «нуль програмування», а перший код зараз з'являється у вставках секції 2. Числа й «від коду до прошивки» збираються з готових ref-ів programming; сам вхід у мову C — нові статті курсу (у book їх немає, і за правилом «кумулятивне → guide» їм місце тут). Після модуля: читач пише, збирає і розуміє просту C-програму, знає, як вона стає прошивкою.*

**1. Як машина рахує**
- [add:programming/bits-bytes-endianness] Біти, байти, endianness — (done) (крит)
- [add:programming/ascii-utf8] Текст у машині: ASCII і UTF-8 — (done) (важл)
- [add:programming/what-is-processor] Що таке процесор — (done) (крит)
- [add:programming/processor-parts] З чого складається процесор — (done) (важл)
- [add:programming/fetch-decode-execute] Цикл виконання інструкції — (done) (крит)
- [add:programming/isa] Набір інструкцій (ISA) — (done) (важл)
- [add:programming/clock-frequency] Тактова частота — (done) (важл)

**2. Мова C: перші кроки** *(нові статті курсу — найбільший обсяг нового письма, все крит)*
- [new:c-first-program] Перша програма: пишемо, збираємо, запускаємо
- [new:c-variables-types] Змінні й типи
- [new:c-control-flow] Розгалуження й цикли
- [new:c-functions] Функції
- [new:c-arrays-strings] Масиви й рядки
- [new:c-structs-enums] Структури й перелічення
- [new:c-pointers-intro] Покажчики: перше знайомство
- [new:c-bit-operations] Бітові операції *(строго перед регістрами МК)*
- [new:c-preprocessor-headers] Препроцесор і заголовки
- [new:c-modules-build] Модулі й збірка проєкту

**3. Числа в C**
- [add:programming/integer-types-c] Цілі типи в C — (done) (крит)
- [add:programming/overflow-wraparound] Переповнення — (done) (важл)
- [add:programming/fixed-point] Числа з фіксованою комою — (done) (важл)
- [add:programming/floating-point] Числа з рухомою комою — (done) (важл)

**4. Від коду до прошивки**
- [add:programming/compilation] Компіляція — (done) (крит)
- [add:programming/linking] Лінкування — (done) (важл)
- [add:programming/memory-as-array] Пам'ять як масив — (done) (крит)
- [add:programming/addresses-pointers] Адреси й покажчики — (done) (крит)
- [add:programming/memory-map] Карта пам'яті — (done) (крит)
- [add:programming/flash-vs-ram] Flash проти RAM — (done) (крит)
- [add:programming/stack-lifo] Стек — (done) (важл)
- [add:programming/heap-dynamic-memory] Купа й динамічна пам'ять — (done) (важл)
- [add:programming/stack-overflow] Переповнення стека — (done) (важл)
- [add:programming/firmware-image] Образ прошивки — (done) (крит)
- [add:programming/c-runtime] Що відбувається до main() — (done) (важл)

**5. Інструменти розробника**
- [add:programming/version-control] Контроль версій і git — (pending: статтю в book ще писати) (важл)
- [add:programming/toolchain] Тулчейн — (pending) (важл)

### Модуль 10 — Мікроконтролер: знайомство й перша прошивка
*МК як цілісний пристрій: що всередині, які бувають, як залити першу програму. Після модуля: читач має живий ESP32, що блимає світлодіодом, і розуміє, що при цьому відбулося.*

**1. Що таке мікроконтролер**
- [add:programming/microcontroller] Мікроконтролер — (done) (крит: зараз секція стартує з фон Неймана без поняття «процесор у чипі»)
- [add:programming/mcu-blocks] З чого складається МК — (done) (крит)
- [own:von-neumann-harvard] Фон Нейман і Гарвард
- [own:risc-cisc] RISC і CISC
- [add:programming/memory-mapped-io] Периферія через пам'ять (MMIO) — (done) (крит)

**2. Сімейства й вибір**
- [own:esp32-vs-8bit] ESP32 проти 8-біт
- [own:esp32-family] Сімейство ESP32
- [add:programming/esp32-architecture] Архітектура ESP32 — (done) (важл)
- [own:pic-architecture] Архітектура PIC
- [own:fpga-vs-mcu] FPGA чи МК ⟵ cyfra-pamyat *(тепер обидві сторони порівняння відомі)*
- [own:datasheet-mcu] Практикум даташитів: мікроконтролер ⟵ komponenty *(найяскравіший приклад теми не на місці — стояла за 4 секції до МК)*
- [own:mcu-selection] Вибір МК
- [own:mcu-checklist] Чеклист вибору МК

**3. Перша прошивка**
- [own:baremetal-vs-framework] Голе залізо vs фреймворк
- [own:hal-ll-registers] HAL, LL і голі регістри в STM32
- [add:programming/flashing] Прошивання — (done) (крит)
- [own:esptool-workflow] esptool: прошивання й читання Flash
- [new:first-blink-project] Перший проєкт: світлодіод блимає — (крит: у курсі немає жодного «hello world»-кроку)

**4. Зазирнути глибше** *(необов'язкова гілка)*
- [own:custom-instruction] Кастомні інструкції процесора ⟵ cyfra-pamyat
- [add:programming/pipeline] Конвеєр — (done) (пізн)
- [add:programming/cache] Кеш — (done) (пізн)

### Модуль 11 — Периферія МК: GPIO, таймери, АЦП, DMA
*Парадокс поточного курсу: є DMA+АЦП і pin-mux, але немає самих GPIO, таймерів, PWM і АЦП. Каркас — з готових ref-ів programming/embedded-systems. Після модуля: читач керує залізом навколо МК.*

**1. GPIO**
- [add:programming/gpio-registers] GPIO через регістри — (done) (крит)
- [own:pin-mux] Мультиплексування пінів (IO_MUX / GPIO matrix)
- [add:electronics/push-pull-output] Push-pull вихід — (done) (важл)
- [add:electronics/open-drain] Відкритий стік — (done) (важл)
- [add:electronics/floating-pullups] Плаваючий вхід і підтяжки — (done) (важл)
- [add:electronics/contact-debounce] Кнопка і брязкіт контактів — (done) (крит)

**2. Переривання**
- [add:programming/interrupts] Переривання — (done) (крит)
- [add:programming/isr] Обробник переривання (ISR) — (done) (крит)
- [own:polling-vs-interrupts] Polling vs переривання
- [add:programming/interrupt-priorities] Пріоритети переривань — (done) (важл)
- [add:programming/atomicity-races] Атомарність і гонки — (done) (важл)

**3. Таймери**
- [add:programming/timer-counter] Таймер-лічильник — (done) (крит)
- [add:programming/timer-overflow] Переповнення таймера — (done) (важл)
- [add:programming/capture-compare] Capture/Compare — (done) (важл)
- [add:programming/millis-micros] Час у прошивці: millis/micros — (done) (крит)
- [add:programming/nonblocking-time] Неблокуючий код на часі — (done) (крит)
- [own:frequency-measurement-methods] Методи вимірювання частоти ⟵ proshyvka *(input capture тепер введено)*

**4. PWM**
- [add:programming/pwm] ШІМ — (done) (крит)
- [add:programming/hardware-pwm] Апаратний ШІМ — (done) (важл)

**5. АЦП і ЦАП**
- [add:electronics/adc] АЦП — (done) (крит: АЦП ніде не вводиться, а вживається з секції 6)
- [add:electronics/adc-resolution] Розрядність і крок — (done) (важл)
- [add:electronics/adc-types] Типи АЦП — (done) (важл)
- [add:electronics/adc-errors] Похибки АЦП — (done) (важл)
- [add:electronics/voltage-reference] Опорна напруга — (done) (важл)
- [own:adc-reference-calibration] Калібрування АЦП зовнішньою опорою ⟵ proshyvka
- [add:electronics/dac] ЦАП — (done) (пізн)
- [own:usb-cc-adc-circuit] Схема зчитування CC: АЦП, фільтрація, гістерезис ⟵ zhyvlennia

**6. DMA**
- [add:programming/dma-problem] Навіщо DMA — (done) (важл)
- [add:programming/dma-controller] DMA-контролер — (done) (важл)
- [own:dma-adc] DMA + АЦП

**7. Скидання і живучість**
- [add:programming/watchdog] Watchdog — (done) (крит: у курсі відсутній узагалі)
- [add:programming/reset-causes] Причини скидання — (done) (важл)
- [own:reset-sequence] Послідовність graceful reset ⟵ mk
- [add:programming/brownout] Brown-out — (done) (важл)
- [own:power-fail-safety] Захист від зникнення живлення: brown-out і рятування стану ⟵ napivprovidnyky
- [own:memory-budget-mcu] Бюджет пам'яті мікроконтролера ⟵ mk

### Модуль 12 — Шини й з'єднання
*Зараз це секція-заглушка з 5 тем. Розгортаємо в повний модуль: UART (якого немає взагалі!), I2C, SPI, диференційні, CAN, USB-дані. Після модуля: читач підключає будь-який чип і бачить обмін логічним аналізатором.*

**1. Навіщо шини**
- [new:why-buses] Як чипи розмовляють: навіщо шини — (важл: місточок-вхід модуля)
- [add:electronics/logic-analyzer] Логічний аналізатор — (done) (крит: головний інструмент цього модуля)
- [add:electronics/level-shifter] Узгодження рівнів 3.3В/5В — (done) (важл)

**2. UART**
- [add:communications/async-serial] Асинхронна послідовна передача — (done) (крит: UART зараз відсутній як тема, а на ньому стоїть уся телеметрія)
- [add:communications/uart-frame] Кадр UART — (done) (крит)
- [add:communications/baud-rate] Швидкість і бодрейт — (done) (важл)
- [own:usb-uart-bridge] Перетворювач USB↔UART

**3. I2C**
- [add:communications/i2c-bus] Шина I2C — (done) (крит)
- [add:communications/i2c-addressing] Адресація I2C — (done) (важл)
- [add:communications/i2c-transaction] Транзакція I2C — (done) (важл)
- [add:communications/register-map] Карта регістрів пристрою — (done) (важл)
- [own:pullup-resistor-design] Розрахунок підтяжки

**4. SPI**
- [add:communications/spi-bus] Шина SPI — (done) (крит)
- [add:communications/spi-lines] Лінії SPI — (done) (важл)
- [add:communications/cpol-cpha] Режими CPOL/CPHA — (done) (важл)
- [add:communications/chip-select] Chip Select — (done) (важл)
- [own:spi-vs-i2c] SPI проти I2C *(тепер це зведення після знайомства з обома)*
- [own:dma-spi-i2s] DMA + SPI/I2S ⟵ mk *(тепер SPI введено)*

**5. Диференційні й польові**
- [ref:communications/differential-pair] Диференційна пара
- [ref:communications/rs-485] RS-485 *(тепер після UART, на якому стоїть)*
- [add:communications/can-arbitration] CAN: арбітраж — (pending: статтю писати) (важл для дронової тематики)
- [add:communications/dronecan] DroneCAN — (pending) (важл)

**6. USB як шина даних**
- [add:programming/usb-enumeration] Енумерація USB — (done) (важл)
- [add:programming/usb-device-classes] Класи USB-пристроїв — (done) (важл)
- [add:programming/tinyusb-device] TinyUSB-пристрій — (done) (пізн)

### Модуль 13 — Системний шар: RTOS, зберігання, оновлення, сон
*Для ESP32-курсу RTOS — не опція: ESP-IDF = FreeRTOS. Зараз у курсі це діра. Плюс зібраний життєвий цикл прошивки: NVS, bootloader, OTA (зараз є лише OTA-сервер без клієнта). Після модуля: багатозадачна прошивка, що безпечно оновлюється і спить.*

**1. Багатозадачність і RTOS**
- [own:super-loop-limits] Межі super-loop ⟵ mk *(природний вхід: глухий кут показано — тепер вихід)*
- [add:programming/tasks] Задачі — (done) (крит)
- [add:programming/scheduler] Планувальник — (done) (крит)
- [add:programming/task-ipc] Черги, семафори, м'ютекси — (done) (крит)
- [add:programming/task-stacks] Стеки задач — (done) (важл)
- [add:programming/freertos] FreeRTOS на ESP32 — (done) (крит)
- [add:programming/realtime-determinism] Реальний час і детермінізм — (done) (важл)
- [own:spinlock-mutex] Спінлок і м'ютекс: вибір і ціна ⟵ proshyvka *(тепер є задачі й планувальник)*

**2. Постійна пам'ять**
- [add:programming/why-persist] Навіщо зберігати стан — (done) (важл)
- [add:programming/flash-internals] Flash зсередини — (done) (важл)
- [add:programming/wear-leveling] Wear leveling — (done) (важл)
- [add:programming/nvs] NVS — (done) (крит)
- [add:programming/write-integrity] Цілісність запису — (done) (важл)
- [own:fatfs-integration] Інтеграція FatFs у вбудований проєкт ⟵ proshyvka

**3. Завантаження й оновлення**
- [add:programming/bootloader] Bootloader — (done) (крит: reset/boot-теми курсу висіли без нього)
- [add:programming/partition-table] Таблиця розділів — (done) (крит)
- [own:boot-time-budget] Бюджет часу завантаження ⟵ mk
- [add:programming/ota-slots] OTA-слоти — (done) (важл)
- [add:programming/ota-update] OTA-оновлення — (done) (крит: зараз є лише серверний бік)
- [own:ota-server] Серверна частина OTA ⟵ mk
- [add:programming/safe-mode] Safe mode — (done) (важл)
- [add:programming/reboot-strategy] Стратегія перезавантажень — (done) (пізн)

**4. Безпека пристрою**
- [add:programming/secure-boot] Secure boot — (done) (важл)
- [own:tpm-trustzone] TPM і TrustZone: апаратний корінь довіри ⟵ proshyvka
- [new:tls-embedded] TLS на мікроконтролері — (важл: теми немає в жодній книзі, а без неї OTA/MQTT незахищені)

**5. Сон і енергоощадність**
- [add:programming/sleep-modes] Режими сну — (done) (крит: аудити споживання зараз ідуть без основ)
- [add:programming/wakeup-sources] Джерела пробудження — (done) (важл)
- [own:duty-cycle-current] Цикл і середній струм ⟵ mk
- [own:board-consumption] Споживання плати ⟵ zhyvlennia
- [own:sleep-current-audit] Аудит струму спокою плати ⟵ zhyvlennia

### Модуль 14 — Налагодження й вимірювання пристрою
*Зібране докупи налагодження (зараз розкидане по mk і proshyvka) + єдиний розділ вимірювання споживання (зараз 4 теми в 3 секціях). Після модуля: читач систематично знаходить причину «не працює».*

**1. Дебагер**
- [add:programming/why-debugger] Навіщо дебагер — (done) (важл)
- [own:jtag-swd-tools] Serial, JTAG/SWD ⟵ mk
- [own:openocd-gdb] OpenOCD і GDB ⟵ mk
- [own:debug-io-comparison] Порівняння каналів налагоджувального виводу ⟵ mk

**2. Аварії**
- [add:programming/hardfault] HardFault і винятки процесора — (done) (важл)
- [own:core-dump] Посмертний аналіз ⟵ mk
- [own:addr2line-workflow] Декодування адрес аварії: addr2line та символи ⟵ proshyvka

**3. Вимірювання споживання (зібраний кластер)**
- [own:measure-consumption] Виміряти споживання ⟵ proshyvka
- [own:power-logger] Логер споживання ⟵ mk
- [own:current-profiler-tools] Вимірювання профілю струму ⟵ mk

**4. Пошук несправностей**
- [new:troubleshooting-methodology] Систематичний пошук несправності — (важл: «не вмикається / зависає / жере батарею» — методики в курсі нема)
- [own:fault-injection-testing] Тестування відмовостійкості: fault injection ⟵ mk

### Модуль 15 — Інженерія якості прошивки
*Software engineering прошивки: зараз ці теми звалені в proshyvka впереміш із осцилографом. Після модуля: читач пише код, який можна супроводжувати й тестувати.*

**1. Помилки і стійкість коду**
- [own:error-codes-vs-exceptions] Коди помилок проти винятків
- [own:error-propagation-patterns] Патерни поширення помилок
- [own:memory-safety] Безпека роботи з пам'яттю
- [own:solid-principles] Принципи SOLID

**2. Процес розробки**
- [own:gitflow-branching] Стратегії гілкування в git *(git-основи — М9.5)*

**3. Тестування**
- [own:firmware-testing] Тестування прошивки
- [add:programming/static-analysis] Статичний аналіз — (done) (важл)
- [add:programming/assert-panic] Assert і panic — (done) (важл)
- [add:programming/defensive-programming] Захисне програмування — (done) (важл)
- [add:programming/sitl-simulation] SITL-симуляція — (done) (важл: канон дронової розробки, у курсі не згадано)
- [new:firmware-ci] CI для прошивки — (важл: збірка на сервері, автопрошивка — теми немає ніде)
- [new:hil-testing] HIL-стенд — (пізн)

**4. Надійність як дисципліна**
- [own:fmea-embedded] FMEA у вбудованих системах

### Модуль 16 — Дисплеї й індикація
*Від найпростішого виходу (LED, стрічки) до дисплеїв. Світлодіод уже введено (М4.2), SPI/I2C і прошивка є. Після модуля: читач обирає і запускає дисплей.*

**1. Світлодіодна індикація**
- [add:electronics/addressable-leds] Адресні світлодіоди (WS2812) — (done) (важл)
- [own:led-animation-patterns] Анімаційні патерни LED ⟵ proshyvka

**2. Дисплеї**
- [own:display-classes] Класи дисплеїв
- [own:display-selection] Вибір дисплея
- [own:gram-init-sequence] Ініціалізація контролера дисплея
- [new:framebuffer-basics] Кадр у пам'яті: framebuffer і RGB565 — (важл: color-management посилається на «Колір у пам'яті», якого в курсі немає)
- [own:display-lifecycle] Керування життєвим циклом дисплея
- [own:color-management] Управління кольором: колірні профілі та гама

### Модуль 17 — Давачі
*Вхід «що таке давач» (зараз секція стартує одразу з тензодавача), далі від простих чуттів до набору автономного апарата. Після модуля: читач підключає, читає і калібрує давачі.*

**1. Що таке давач**
- [add:electronics/what-is-a-sensor] Що таке давач — (done) (крит: місточок-вхід)
- [add:electronics/sensor-characteristics] Характеристики давачів — (done) (важл)
- [add:electronics/drift-hysteresis-noise] Дрейф, гістерезис, шум — (done) (важл)

**2. Прості вимірювання**
- [add:electronics/ntc-thermistor] Термістор NTC — (done) (важл)
- [ref:electronics/load-cell] Тензодавач
- [add:electronics/current-monitor] Давач струму — (done) (пізн)

**3. Відстань**
- [own:contactless-distance] Безконтактна відстань
- [own:error-budget-ranging] Бюджет похибок далекоміра
- [own:lidar-architecture] Архітектури LiDAR

**4. Інерціальні давачі**
- [add:electronics/accelerometer] Акселерометр — (done) (важл)
- [add:electronics/gyroscope] Гіроскоп — (done) (важл)
- [add:electronics/magnetometer] Магнітометр — (done) (важл: компас потрібен навігації, у курсі його нема)
- [add:electronics/imu] IMU як вузол — (done) (важл)
- [own:imu-barometer] IMU й барометр
- [own:barometric-altimeter] Барометр-альтиметр
- [own:imu-mounting-materials] Матеріали для кріплення IMU

**5. Позиція й набір апарата**
- [add:communications/gnss] GNSS — (done) (важл: GPS зараз існує лише як історична вставка)
- [own:onboard-sensors] Давачі апарата *(камера як давач — у М23.1, разом із рештою камерного блоку)*

**6. Калібрування**
- [own:calibration-procedure] Процедура калібрування давача ⟵ proshyvka *(стояла ЗА СЕКЦІЮ ДО введення давачів)*

*Виїхали: vibration-diagnostics (→ М19.5 — стоїть на частотному аналізі), stereo-vision (→ М22.1 — камерний блок).*

### Модуль 18 — Мотори й привід — **НОВИЙ МОДУЛЬ**
*Курс про «автономні системи» без моторів: зараз є лише servo-sizing і esc-bldc-driver. Виконавча ланка збирається з готових done-статей electronics. Стоїть перед керуванням — щоб PID мав чим керувати. Після модуля: читач обирає і драйвить DC/кроковий/BLDC/серво.*

**1. DC-мотор і драйвер**
- [add:electronics/brushed-dc-motor] Колекторний DC-мотор — (done) (крит)
- [add:electronics/gearmotor] Мотор-редуктор — (done) (важл)
- [add:electronics/motor-current-stall-heat] Струм, заклинювання, нагрів — (done) (важл)
- [add:electronics/h-bridge] H-міст — (done) (крит)
- [add:electronics/dc-motor-driver] Драйвер DC-мотора — (done) (важл)

**2. Крокові мотори й енкодери**
- [add:electronics/stepper-motor] Кроковий мотор — (done) (крит)
- [add:electronics/stepper-driver] Драйвер крокового — (done) (важл)
- [add:electronics/optical-incremental-encoder] Інкрементальний енкодер — (done) (важл: зворотний зв'язок за положенням)

**3. BLDC і серво**
- [add:electronics/bldc-motor] BLDC-мотор — (done) (крит)
- [own:esc-bldc-driver] Регулятор обертів (ESC) ⟵ drony
- [add:electronics/hobby-servo] Хобі-серво — (done) (важл)
- [own:servo-sizing] Вибір сервопривода: момент, швидкість, маса ⟵ drony

### Модуль 19 — Сигнали й керування
*Найцільніший модуль курсу — лишається майже цілим, лагодиться лише внутрішній порядок: спершу сигнал і дискретизація, потім фільтри, потім PID-ланцюг без розривів, потім оцінювання стану. Після модуля: читач фільтрує сигнали і замикає стійкі контури керування.*

**1. Сигнал у цифру**
- [own:signal-acquisition] Зчитування сигналу *(вхід модуля — зараз стоїть третім після «вибору фільтра»)*
- [add:communications/nyquist-aliasing] Дискретизація й аліасинг — (done) (крит: антиаліасинговий фільтр зараз проєктується без теореми відліків)
- [own:antialiasing-filter-design] Проєктування антиаліасингового фільтра

**2. Частотна область**
- [own:why-frequency-domain] Навіщо частота
- [add:algorithms/fft] FFT — (done) (пізн)
- [own:tone-detection] Виявлення тонів

**3. Цифрові фільтри**
- [own:choosing-a-filter] Вибір фільтра
- [own:fir-vs-iir] КІХ проти БІХ
- [own:filter-specification] Специфікація фільтра
- [own:fir-design] Проєктування КІХ-фільтрів
- [own:filter-latency-budget] Бюджет затримки фільтра

**4. Зворотний зв'язок і PID** *(ланцюг без розривів — зараз PID-кластер розірваний фільтровим)*
- [own:open-vs-closed-loop] Зворотний зв'язок *(перед математикою — мотивація)*
- [own:calculus-for-pid] Похідна й інтеграл для PID
- [own:proportional-control] П-регулятор
- [own:integral-control] І-складова
- [own:pi-controller-tuning] Налаштування ПІ-регулятора *(зараз відірвана від І-складової дванадцятьма темами)*
- [own:derivative-control] Д-складова
- [own:pid-tuning-cascade] Налаштування ПІД
- [own:loop-stability] Запас стійкості
- [own:lead-lag-compensator] Lead/lag-компенсатор
- [own:loop-gain-measurement] Вимірювання петлевого підсилення ⟵ zhyvlennia *(найдальший «стрибок у майбутнє» старого порядку — тепер стоїть після теорії стійкості)*

**5. Оцінювання стану**
- [own:kalman-filter] Фільтр Калмана *(перед темами, що ним користуються, — зараз стоїть після)*
- [add:algorithms/complementary-filter] Комплементарний фільтр — (done) (важл)
- [add:algorithms/sensor-fusion] Злиття давачів — (done) (важл)
- [own:attitude-estimation] Оцінка орієнтації (attitude estimation)
- [own:inertial-navigation] Інерціальна навігація
- [own:sensor-fault-detection] Виявлення відмови давача
- [own:vibration-diagnostics] Вібродіагностика ⟵ davachi *(стоїть на спектрах і обвідній — тепер вони пройдені)*

**6. Активне гасіння**
- [own:active-noise-cancellation] Активне гасіння шуму

*Виїхала: slam-navigation (→ М21.4 — дронова навігація).*

### Модуль 20 — Радіо: фізика лінка й антени
*Радіо як фізика й інженерія: модуляція (зараз FHSS стоїть на модуляції, якої нема), антена, бюджет лінка, стійкість під глушінням. Що саме летить через лінк — то вже наступний модуль. Після модуля: читач рахує лінк і розуміє антенну частину плати.*

**1. Радіо-основи**
- [add:communications/power-decibels] Потужність і децибели — (done) (крит: link-budget оперує дБ/дБм, а децибели ніде не вводились)
- [add:communications/why-modulation] Навіщо модуляція — (done) (крит: FHSS і половина радіотем стоять на модуляції, якої нема)
- [add:communications/am-fm] AM і FM — (done) (важл)
- [add:communications/fsk-psk] FSK і PSK — (done) (важл)
- [add:communications/spread-spectrum] Розширення спектра — (done) (важл)
- [own:propagation-modes] Режими поширення радіохвиль *(підняти: зараз стоїть ПІСЛЯ link-budget, який на ньому будується)*

**2. Антени й RF-тракт**
- [add:communications/antenna] Що таке антена — (done) (крит)
- [add:communications/antenna-gain] Підсилення антени — (done) (важл)
- [own:esp32-antenna] Антена ESP32
- [own:pcb-antenna-layout] Топологія антени на PCB: keep-out, заземлення, розведення
- [own:esp32-module] ESP32-модуль
- [own:rf-frontend] RF-тракт: підсилювачі, перемикач і балун

**3. Бюджет і стійкість лінка**
- [own:link-budget] Бюджет лінії
- [own:itu-r-propagation-models] Моделі розповсюдження ITU-R і 3GPP
- [own:frequency-budget-analysis] Частотний бюджет у системах зв'язку
- [own:jamming-fhss] Лінк під глушінням

### Модуль 21 — Передача даних і мережі
*Що і як летить через лінк: пакети, надійна доставка, потоки телеметрії (новий розділ «Передача даних» — раніше ці сходинки були пропущені), далі стандарти і мережевий стек — головна причина обирати ESP32, зараз відсутня як блок (перша тема секції — маршрутизація без поняття «пакет»). Після модуля: читач жене телеметрію через радіомодем і MQTT через Wi-Fi.*

**1. Передача даних**
- [add:communications/packet-design] Пакет і кадр: як пакувати дані — (done) (крит)
- [add:communications/crc] CRC — (done) (важл)
- [own:data-reliability] Надійність даних
- [add:communications/flow-control] Керування потоком — (done) (важл)
- [add:communications/reliable-link] Надійна доставка поверх ненадійного лінка — (done) (важл)
- [own:arq-strategies] Стратегії ARQ
- [own:multiple-access-methods] Методи множинного доступу
- [add:communications/control-telemetry] Канал керування й телеметрії — (done) (важл)
- [add:communications/telemetry-stream] Потік телеметрії — (done) (важл)
- [add:programming/data-serialization] Серіалізація даних — (pending: статтю писати) (важл)

**2. Бездротові стандарти**
- [add:communications/wifi] Wi-Fi — (done) (крит: ESP32-курс без жодного Wi-Fi-кроку)
- [own:802-11-versions] Стандарти 802.11: від b/g/n до Wi-Fi 7
- [own:wifi-fast-connect] Швидке підключення Wi-Fi: кешування PMK і IP ⟵ mk
- [own:lpwan] LPWAN
- [own:thread-matter-zigbee] Thread, Zigbee і Matter: стек розумного дому на 802.15.4
- [own:nfc-rfid] NFC/RFID

**3. Мережевий стек і IoT-протоколи**
- [add:communications/tcp-vs-udp] TCP проти UDP — (done) (крит)
- [add:programming/sockets-tcp-udp] Сокети — (done) (крит)
- [ref:communications/ip-routing] Маршрутизація *(тепер після стека — зараз це ПЕРША тема секції)*
- [add:communications/mqtt] MQTT — (done, є навіть detailed) (крит)
- [add:programming/web-server-mcu] Веб-сервер на МК — (done) (важл)
- [add:communications/ble-gatt] BLE і GATT — (done) (важл)
- [own:rpc-embedded] RPC у вбудованих системах

### Модуль 22 — Звук на пристрої
*Аудіо-гілка курсу, якої не було взагалі: від мікрофона до обробки й запису. Спирається на DSP (М19: дискретизація, фільтри) і шини (М12: DMA). У книгах гілка поки тонка — done лише перетворювачі й підсилювач класу D, решта pending/new.*

**1. Звук і перетворювачі**
- [add:electronics/microphone-speaker] Мікрофон і динамік — (done) (важл)
- [add:electronics/mems-microphone] MEMS-мікрофон — (pending) (пізн)
- [add:electronics/class-d-amplifier] Підсилювач класу D — (done) (важл: як пристрій «говорить» назовні)
- [add:electronics/acoustic-enclosure] Акустичне оформлення динаміка — (pending) (пізн)

**2. Цифровий звук**
- [add:communications/i2s-bus] Шина I2S — (pending: статтю писати; DMA+I2S уже у М12) (важл)
- [new:audio-capture-pipeline] Захоплення звуку: від мікрофона до буфера — (важл)
- [new:audio-playback-path] Відтворення: I2S/ЦАП/PDM-виходи — (важл)

**3. Обробка звуку**
- [new:audio-processing-basics] Обробка на МК: фільтрація, рівень, AGC — (важл)
- [new:audio-events-detection] Детекція подій у звуці (VAD, пороги, енергія) — (важл)
- [add:algorithms/audio-time-scaling] Зміна темпу без зміни висоти тону — (pending) (пізн)

**4. Стиснення й запис**
- [new:audio-recording-storage] Запис звуку: WAV, кільцевий буфер, SD — (важл)
- [new:audio-compression-mcu] Стиснення звуку на МК: ADPCM, Opus — (пізн)

### Модуль 23 — Зображення й відео
*Повний шлях кадру: сенсор → сирі дані → картинка → класична обробка → глибина → кодек → ефір. Галузь computer-vision у книзі algorithms уже багата (десяток done+detailed статей) — модуль здебільшого збирається з готового. Нейромережні методи — далі, у частині ML.*

**1. Камера**
- [add:electronics/image-sensor] Камерний сенсор — (done) (важл) ⟵ був у М17
- [add:electronics/cmos-matrix] CMOS-матриця — (done, є навіть detailed) (важл)
- [add:electronics/rolling-shutter] Rolling shutter — (done) (пізн) ⟵ був у М17
- [new:camera-interfaces-mcu] Підключення камери до МК: DVP, MIPI-CSI, SPI-камери — (важл)

**2. Від сирих даних до картинки**
- [add:algorithms/bayer-demosaic] Демозаїка Байєра — (done+detailed) (важл)
- [add:algorithms/pixel-formats] Формати пікселів і буферів — (pending) (важл)
- [own:isp-pipeline] ISP-пайплайн
- [add:algorithms/white-balance] Баланс білого — (pending) (пізн)

**3. Класична обробка зображення**
- [add:algorithms/image-as-data] Зображення як дані — (done+detailed) (важл)
- [add:algorithms/histogram] Гістограма — (done+detailed) (важл)
- [add:algorithms/convolution-filters] Згортки й фільтри — (done+detailed) (важл)
- [add:algorithms/edge-detection] Виділення меж — (done+detailed) (важл)
- [add:algorithms/threshold-morphology] Пороги й морфологія — (done+detailed) (важл)
- [own:image-stabilization] Стабілізація зображення
- [add:algorithms/optical-flow] Оптичний потік — (pending) (пізн)

**4. Глибина й орієнтири**
- [own:stereo-vision] Стереозір ⟵ davachi
- [add:algorithms/corner-detection] Детектори кутів — (pending) (пізн)
- [add:algorithms/feature-matching] Зіставлення ключових точок — (pending) (пізн)
- [add:algorithms/aruco-apriltag] Фідуційні мітки ArUco/AprilTag — (pending) (важл: точна посадка, докінг)

**5. Кодеки й стрімінг**
- [add:algorithms/jpeg-intra] JPEG зсередини — (done) (важл)
- [own:mjpeg-vs-h264] MJPEG vs H.264
- [own:fpv-video-systems] FPV-відеосистеми: аналог vs DJI O3/HDZero/Walksnail ⟵ zvyazok
- [own:video-streaming-protocols] Протоколи відеострімінгу ⟵ zvyazok

### Модуль 24 — Машинне навчання: основи
*ML тепер окрема частина: він потрібен зору, звуку, вібродіагностиці й домашнім пристроям. Цей модуль — мова і механіка ML без прив'язки до заліза. Галузь machine-learning у книзі algorithms уже заведена широко (7 done + ~20 pending) — модуль здебільшого збирається ref-ами.*

**1. Що таке машинне навчання**
- [add:algorithms/what-is-ml] Що таке машинне навчання — (done) (крит для цієї частини)
- [add:algorithms/supervised-learning] Навчання з учителем — (pending) (важл)
- [add:algorithms/unsupervised-learning] Навчання без учителя — (pending) (пізн)
- [add:algorithms/reinforcement-learning] Навчання з підкріпленням — (pending) (пізн)
- [add:algorithms/train-vs-inference] Навчання проти інференсу — (done) (важл)

**2. Нейромережа зсередини**
- [add:algorithms/neuron-layer] Нейрон і шар — (done) (важл)
- [add:algorithms/activation-functions] Функції активації — (pending) (важл)
- [add:algorithms/loss-functions] Функції втрат — (pending) (пізн)
- [add:algorithms/gradient-descent] Градієнтний спуск — (done) (важл)
- [add:algorithms/backpropagation] Зворотне поширення помилки — (pending) (важл)
- [add:algorithms/cnn] Згорткові мережі — (done) (важл)

**3. Навчання без пасток**
- [add:algorithms/overfitting] Перенавчання — (done) (важл)
- [add:algorithms/regularization] Регуляризація — (pending) (пізн)
- [add:algorithms/data-augmentation] Аугментація даних — (pending) (важл)
- [add:algorithms/cross-validation] Крос-валідація — (pending) (пізн)
- [own:training-data-pipeline] Підготовка навчальних даних

### Модуль 25 — Машинне навчання на мікроконтролері
*Модель — у кишеню: стискання, конвертація, інференс і реальні застосунки на краю. Після модуля: читач жене детекцію, ключові слова і аномалії вібрацій на МК і вміє виміряти, скільки це коштує.*

**1. Модель у кишеню**
- [add:algorithms/tinyml] TinyML — (done) (важл)
- [add:algorithms/model-quantization] Квантування нейромереж — (pending) (важл)
- [add:algorithms/transfer-learning] Transfer learning — (pending) (важл)
- [add:algorithms/weight-pruning] Прорідження мережі — (pending) (пізн)
- [add:algorithms/knowledge-distillation] Дистиляція знань — (pending) (пізн)

**2. Інференс на борту**
- [own:edge-inference] Інференс на пристрої (Edge AI) ⟵ mk
- [own:model-export] Експорт і розгортання моделей ML
- [add:algorithms/inference-latency] Латентність інференсу — (pending) (важл)
- [add:algorithms/compute-cost] Вартість обчислень — (done+detailed) (важл)
- [own:on-device-benchmarking] Бенчмаркінг на пристрої

**3. Застосунки на краю**
- [add:algorithms/object-detection] Виявлення об'єктів — (done+detailed) (важл)
- [add:algorithms/nn-detectors] Нейродетектори — (done+detailed) (важл)
- [own:model-zoo] Зоопарк моделей детекції
- [add:algorithms/tracking] Трекінг — (done+detailed) (важл)
- [new:audio-kws] Ключові слова й події у звуці (KWS) — (важл: зв'язка з М22)
- [new:vibration-anomaly-ml] Аномалії вібрацій через ML — (пізн: зв'язка з М19)

### Модуль 26 — Автопілот: бортовий мозок
*Серце будь-якої автономної платформи. Зараз «як влаштована автономна система» в курсі нема. Каркас — done-статті programming/embedded-systems; безпекові кроки (arming, preflight) заведені в книзі як pending. Після модуля: читач розуміє архітектуру автопілота і безпечно його налаштовує.*

**1. Архітектура автопілота**
- [add:programming/flight-controller] Політний контролер — (done) (крит)
- [add:programming/ardupilot-layers] Шари ArduPilot — (done) (важл)
- [add:programming/fc-vs-companion] FC і компаньйон-комп'ютер — (done) (важл)
- [own:where-to-compute] Де рахувати ⟵ drony

**2. Безпека виконання**
- [add:programming/failsafe] Failsafe — (done) (крит)
- [add:programming/redundancy] Надлишковість — (done) (важл)
- [add:programming/arming-checks] Arming-перевірки — (pending) (важл)
- [add:programming/preflight-safety] Безпека до запуску — (pending) (важл)
- [add:programming/geofence] Геозона (geofence) — (pending) (важл)

**3. Налаштування й діагностика**
- [add:programming/params-gcs] Параметри й GCS — (done) (важл)
- [new:fc-setup-calibration] Первинне налаштування: калібрування давачів і радіо — (важл)
- [new:flight-log-analysis] Аналіз логів польоту/поїздки — (важл)
- [add:programming/preflight-checklists] Передстартові чеклисти — (pending) (пізн)

### Модуль 27 — Канал керування й зв'язок із землею
*Дві лінії між оператором і бортом: RC-керування (протоколи приймача — зараз відсутні в курсі як клас) і MAVLink-телеметрія (зараз розірвана між mk і zvyazok). Після модуля: читач приймає RC, мікшує виходи і ганяє команди з наземної станції.*

**1. RC-керування**
- [add:communications/rc-link] RC-лінк — (done) (важл)
- [add:communications/rc-signal-protocol] RC-сигнал: PWM, PPM і S.BUS — (pending) (важл)
- [add:communications/crsf-protocol] Протокол CRSF — (pending) (пізн)
- [add:communications/rc-failsafe-modes] Режими failsafe RC — (pending) (важл)
- [add:communications/elrs-architecture] Архітектура ExpressLRS — (pending) (пізн)

**2. Стабілізація і мікшування**
- [add:algorithms/instability-stabilization] Нестійкість і стабілізація — (done) (важл)
- [add:algorithms/roll-pitch-yaw-control] Керування по крену, тангажу, рисканню — (done) (важл)
- [add:algorithms/stabilization-cascade] Каскад стабілізації — (done) (важл)
- [add:algorithms/motor-mixer] Міксер моторів — (done) (важл)
- [own:output-mixing] Узгодження сигналів керування ⟵ drony *(тепер після моторів М18 і каскаду)*

**3. MAVLink і наземна станція**
- [add:communications/mavlink-packet] Пакет MAVLink — (done) (важл)
- [own:mavlink-commands] Команди MAVLink ⟵ mk
- [own:mavlink-from-ground] MAVLink із землі ⟵ zvyazok
- [new:python-ground-scripts] Python для наземних скриптів — (важл: місток перед pymavlink, Python у курсі не вводився)
- [own:pymavlink] pymavlink ⟵ zvyazok
- [own:mission-planner-qgc] Mission Planner і QGroundControl: порівняння GCS ⟵ mk
- [add:communications/telemetry-link] Канал земля–борт — (pending) (пізн)

### Модуль 28 — Навігація й місії
*Де я, куди їду/лечу, як туди дістатись і що робити дорогою. Оцінка стану вже пройдена (М19); тут — позиція, маршрут і місії. Кульмінаційна тема курсу (autonomous-system) нарешті стоїть у фіналі, а не в середині секції МК.*

**1. Позиція: GNSS глибше**
- [new:gnss-receiver-integration] GNSS-приймач у прошивці: NMEA і UBX — (важл; сам GNSS введено в М17)
- [add:communications/sbas-corrections] Супутникові доповнення (SBAS) — (pending) (пізн)
- [add:algorithms/rtk-integer-ambiguity] RTK: сантиметрова точність — (pending) (пізн)
- [add:communications/pps-pulse] PPS-імпульс і точний час — (pending) (пізн)

**2. Оцінка руху**
- [add:algorithms/predict-vs-measure] Передбачення проти виміру — (done) (важл)
- [add:algorithms/kalman-ekf] Розширений фільтр Калмана (EKF) — (done) (важл)
- [add:algorithms/odometry] Одометрія — (done) (важл)
- [add:algorithms/motion-model] Модель руху — (done) (важл)
- [add:math/quaternions] Кватерніони — (done) (важл: орієнтація без gimbal lock)
- [add:algorithms/quaternion-attitude-control] Кватерніонне керування орієнтацією — (pending) (пізн)
- [add:algorithms/visual-inertial-odometry] Візуально-інерціальна одометрія — (pending) (пізн)

**3. Маршрут**
- [add:algorithms/dijkstra] Алгоритм Дейкстри — (pending) (важл)
- [new:path-planning-grid] Планування шляху: сітка і A* — (важл)
- [new:obstacle-avoidance] Обхід перешкод — (важл)
- [add:algorithms/pure-pursuit-navigation] Слідування траєкторії (pure pursuit) — (pending) (важл)

**4. Місії й автономія**
- [own:mission-planning] Проєктування місії (вейпойнти) ⟵ mk
- [own:autonomous-system] Автономна система ⟵ mk *(кульмінаційна тема курсу)*
- [own:slam-navigation] SLAM: одночасне картографування й локалізація ⟵ keruvannia

### Модуль 29 — Платформа: стаціонарні пристрої і розумний дім — **НОВИЙ МОДУЛЬ**
*Найдоступніша платформа: без моторів і польотів, зате з мережею, інтеграцією і побутовою надійністю. Більшість цеглин уже пройдено (MQTT, Thread/Matter, сон) — тут вони складаються в пристрій.*

**1. Домашній вузол**
- [new:smart-home-node] Вузол розумного дому: давач + MQTT + автономна логіка — (важл)
- [add:communications/esp-now] ESP-NOW: локальний зв'язок вузлів — (pending) (важл)
- [new:device-provisioning] Перше налаштування пристрою: SoftAP і BLE-провізіонування — (важл)

**2. Інтеграція і побут**
- [new:home-device-integration] Інтеграція: Home Assistant і Matter — (пізн)
- [new:home-device-power] Живлення побутового пристрою: від мережі, безпечно, з малим standby — (пізн)

### Модуль 30 — Платформа: наземні (ровер, НРК) — **НОВИЙ МОДУЛЬ**
*Наземні роботи — ровери, НРК, платформи для дому й поля. Кінематика й телекерування — своя специфіка, якої нема ні в коптера, ні в стаціонарного вузла.*

**1. Шасі і привід**
- [new:ugv-platform] Шасі ровера/НРК: компонування, прохідність, енергетика — (важл)
- [new:differential-drive-kinematics] Кінематика диференціального приводу — (важл)
- [add:electronics/gears-transmission] Редуктори й передачі — (done) (важл)

**2. Керування рухом**
- [add:algorithms/rover-steering] Керування ровером — (pending) (важл)
- [new:teleoperation-latency] Телекерування: затримки, відеоканал, втрата лінка — (важл: специфіка НРК)

**3. Інші середовища**
- [add:algorithms/boat-underwater] Човен і підводні апарати — (pending) (пізн)

### Модуль 31 — Платформа: повітряні (коптер, літак, VTOL) — **НОВИЙ МОДУЛЬ**
*Літаючі платформи: фізика польоту (статті вже заведені в physics/mechanics як pending), підбір пропульсії, перший політ, літак і гібриди.*

**1. Фізика мультикоптера**
- [add:physics/thrust-vs-weight] Тяга проти ваги — (pending) (важл)
- [add:physics/reaction-torque] Реактивний момент: чому гвинти крутяться в різні боки — (pending) (важл)
- [add:physics/propeller-geometry] Гвинт: крок і діаметр — (pending) (пізн)
- [add:physics/frame-configurations] Рами й конфігурації — (pending) (пізн)

**2. Пропульсія**
- [new:propulsion-sizing] Підбір пропульсії: мотор + гвинт + батарея під злітну масу — (важл)

**3. Перший політ**
- [add:programming/manual-stabilized-modes] Ручні режими польоту — (pending) (важл)
- [add:programming/position-modes] Режими з утриманням позиції — (pending) (пізн)
- [add:programming/first-bringup] Перший запуск апарата — (pending) (важл)

**4. Літак і VTOL**
- [add:physics/fixed-wing-lift] Крило і підйомна сила — (pending) (важл)
- [new:fixed-wing-control-surfaces] Керування літаком: елерони, руль, мікшування — (важл)
- [add:physics/vtol-transition] VTOL і перехідний політ — (pending) (пізн)

### Модуль 32 — Капстоун: автономна місія — **НОВИЙ МОДУЛЬ**
*Фінальний проєкт, що зшиває весь курс. Платформу читач обирає сам — домашній вузол, ровер, коптер чи літак; місія проходить повний цикл: ТЗ → збірка → налаштування → виконання → аналіз логів → документація.*

**1. Фінальний проєкт**
- [add:programming/capstone-task] Капстоун-завдання — (pending) (важл)
- [add:programming/end-to-end-mission] Місія від початку до кінця — (pending) (важл)
- [new:capstone-autonomous-mission] Капстоун на обраній платформі: дім / ровер / коптер / літак — (важл)
- [new:project-documentation] Документація проєкту: README, схема, BOM, журнал змін — (важл)

### Модуль 33 — Виріб: плата, серія, сертифікація — **НОВИЙ МОДУЛЬ (на виріст)**
*Заявлена мета курсу — «до продакшена», але шляху до виробу зараз немає: сценарій «мала серія» покритий на ~20%. Модуль майже цілком із нових/pending тем — свідомо позначений як друга черга письма.*

**1. Плата всерйоз**
- [new:pcb-layout-flow] Від схеми до замовлення: розводка, гербери, виробник — (важл)
- [add:electronics/common-ground] Спільна земля — (done) (важл)
- [add:electronics/ground-loops] Земляні петлі — (done) (важл)
- [add:electronics/shielding] Екранування — (done) (пізн)

**2. Мала серія**
- [new:dfm-basics] DFM: проєктувати так, щоб можна було виготовити — (пізн)
- [new:factory-provisioning] Заводське прошивання й провізіонування — (пізн)
- [new:test-jig-design] Тест-джиг — (пізн)

**3. Корпус і механіка**
- [new:enclosure-ip-rating] Корпус, IP-захист, роз'єми — (пізн)

**4. Сертифікація й регуляції**
- [add:communications/emc-certification] EMC-сертифікація — (pending) (пізн)
- [new:drone-regulations] Регуляції БпЛА — (пізн)
- [new:functional-safety-overview] Функційна безпека: огляд стандартів — (пізн)

---

## 5. Обґрунтування

### 5.1 Головні переїзди (значущі; повний перелік видно з позначок ⟵ у змісті)

| Що | Звідки → Куди | Чому |
|----|---------------|------|
| Транзисторно-ОП блок (13 тем) | kola → М4/М5 | BJT/ОП вживалися ДО напівпровідників; ОП не вводився ніде |
| RC/RL-сталі, фаза, фільтри | kola → М3 | конденсатор і котушка вводились ПІЗНІШЕ за свої сталі часу |
| resistor/capacitor/inductor-блоки | komponenty → М2/М3 | компонент має з'являтися там, де вперше потрібен колу |
| Пам'яті (nor-vs-nand, eeprom-fram, mram-rram-pcm, memory-cell-physics) | napivprovidnyky+osnovy → М8.5 | кластер був розірваний по 3 секціях; фізика комірок вимагає транзистора й логіки |
| datasheet-mcu | komponenty → М10.2 | стояв за 4 секції до появи МК |
| MAVLink-кластер (4 теми) | mk+zvyazok → М27.3 | кластер був розірваний між двома секціями |
| autonomous-system, mission-planning | mk → М28.4 | кульмінація курсу сиділа в середині секції МК |
| edge-inference | mk → М25.2 | Edge AI до будь-якої згадки про ML |
| wifi-fast-connect | mk → М21.2 | кешування PMK до введення Wi-Fi |
| Дебаг-блок (jtag, openocd, core-dump, debug-io) | mk → М14 | відлагодження прошивки до першої прошивки; тепер після системного шару |
| Вимірювання споживання (4 теми) | mk+proshyvka+zhyvlennia → М13.5/М14.3 | один сюжет у трьох секціях |
| Осцилограф (sine-on-scope, noise-hunting) | proshyvka → М3.8 | дивитися сигнали треба з модуля 3, а не з секції 9 |
| Інженерні теми (solid, memory-safety, error-*) | proshyvka → М15 | програмування без входу в програмування; тепер після М9 |
| calibration-procedure | proshyvka → М17.6 | калібрування давача ЗА СЕКЦІЮ ДО введення давачів |
| loop-gain-measurement | zhyvlennia → М19.4 | вимірювання петлі вимагає теорії стійкості (була через 6 секцій) |
| usb-cc-adc-circuit | zhyvlennia → М11.5 | потребує АЦП |
| board-consumption, sleep-current-audit | zhyvlennia → М13.5 | потребують МК і режимів сну |
| servo-sizing, esc-bldc-driver | drony → М18 | мотори тепер вводяться до дронів |
| stereo-vision | davachi → М23.4 | блок обробки зображень зібрано разом |
| vibration-diagnostics | davachi → М19.5 | стоїть на спектрах/обвідній |
| slam-navigation | keruvannia → М28.4 | навігація автономних платформ |
| kelvin-shunt | proshyvka → М2.4 | вимірювальний інструмент новачка |
| fpga-vs-mcu, custom-instruction | cyfra-pamyat → М10 | порівнюють із МК/процесором, яких ще не було |

### 5.2 Прогалини — зведення за пріоритетом

**Критично (без цього новачок курс не пройде):**
1. **Вхід у програмування (М9)** — найбільша діра: ~10 нових C-статей курсу + ~24 готові ref-и programming. Єдина критична діра, що вимагає великого нового письма.
2. **Цифрова логіка (М8.1–8.3)** — ~14 готових done-ref-ів electronics/digital, письма не треба.
3. **Транзистор/ОП/діод як введення (М4–М5)** — ~15 done-ref-ів; водночас лагодить зламаний порядок kola.
4. **Периферія МК (М11)** — GPIO/переривання/таймери/PWM/АЦП/watchdog: ~20 done-ref-ів + new:first-blink-project.
5. **Шини (М12)** — UART (зараз відсутній як клас!)/I2C/SPI: ~12 done-ref-ів; CAN/DroneCAN — pending, писати.
6. **RTOS (М13.1)** — ~6 done-ref-ів; для ESP32-курсу критично.
7. **Bootloader/NVS/OTA-клієнт (М13.2–13.3)** — ~10 done-ref-ів.
8. **Мережі й IoT (М21.3)** — Wi-Fi/TCP-UDP/сокети/MQTT: done-ref-и (MQTT навіть detailed).
9. **Мотори (М18)** — ~10 done-ref-ів.
10. **Автономне ядро (М26–М27)** — flight-controller/failsafe/redundancy/params-gcs done; фізика польоту й платформи (М29–М31) — pending у physics + нові статті.
11. **Інструменти новачка рано (М2.4, М3.8)** — multimeter/oscilloscope/lab-power-supply done + new:breadboard-prototyping.

**Важливо:** реактивність/імпеданс (done); кварц (done); Шмітт/компаратор (done); LED/оптопара/реле (done); LDO/buck/boost поіменно + decoupling + li-ion-charger (done); числа fixed/float (done); дебагер-вступ, hardfault (done); давачі-вступ + IMU-складові + магнітометр + GNSS (done); комплементарний фільтр/sensor-fusion (done); Найквіст (done); децибели/модуляція/антени/CRC (done); **передача даних (М21.1: packet-design/flow-control/reliable-link/telemetry — done)**; RC-лінк (done) + RC-протоколи PWM/PPM/SBUS/CRSF (pending); SITL (done); **медіа (М22–М23): камера/демозаїка/CV-класика done, аудіо-конвеєр — new**; **ML (М24–М25): 7 done + широкий pending-хвіст у algorithms**; **навігація (М28): EKF/кватерніони/одометрія done, RTK/планування шляху — pending/new**; платформи (М29–М31): rover-steering/boat-underwater/політ-фізика pending, вузол дому/кінематика/пропульсія — new; TLS на МК (new — писати); CI (new); troubleshooting-methodology (new); framebuffer (new); why-buses (new); pcb-intro (new); version-control/toolchain (pending у book — дописати).

**Пізніше:** М33 цілком (виріб/серія/сертифікація); pending-гілки платформ (літак/VTOL, човен/підводні, home-integration); аудіо-стиснення й акустичне оформлення; глибокий CV-хвіст (optical-flow, corner-detection, feature-matching); глибокий ML-хвіст (regularization, cross-validation, distillation, pruning); RTK/SBAS/PPS; 555; ЦАП; FFT-крок; функційна безпека; drone-regulations; hil-testing; pipeline/cache (гілка М10.4).

### 5.3 Дублі й перетини (розв'язані в новій структурі)

- **Вимірювання споживання ×4** (power-logger, current-profiler-tools — mk; measure-consumption — proshyvka; sleep-current-audit — zhyvlennia) → М13.5 (режими+аудити) і М14.3 (інструменти вимірювання). Кандидати на злиття: power-logger ↔ current-profiler-tools (перевірити перетин при виконанні).
- **noise-interference ×2** (ref physics + own курсу в одній секції) → обидві в М3.7 поруч, з розведенням назв (фізика / інженерне зведення).
- **MAVLink ×4** у двох секціях → один кластер М27.3.
- **Пам'яті** по секціях 1/4/5 → один кластер М8.5.
- **PCB-фрагменти** (тепло/монтаж/антена/SI) → знайомство в М6.3, глибина в М33.1, антена лишається в радіо М20.2.
- **Даташит-практикуми** розкидані (BJT — komponenty, MCU — komponenty, загальний — komponenty) → кожен їде до свого предмета: загальний М6.1, BJT М4.3, MCU М10.2.

### 5.4 Технічна примітка: як реалізувати «розділи»

Чинна схема guide дворівнева: `sections[]` (модуль) → `topics[]` (крок); нумерацію рушій рахує з позиції. Два шляхи:

1. **Без зміни рушія:** кожен модуль плану = `section`, розділи — ні на що не мапляться (або тимчасово як коментарі в маніфесті). 23 секції по 10–35 кроків — уже величезне покращення проти 14×47, і мігрувати можна поступово.
2. **Розширити рушій третім рівнем:** `sections[] → chapters[] → topics[]` (нумерація Модуль.Розділ.Крок). Схема AUTHORING §2 і рушій `book.js` потребують правки; виграш — читач бачить структуру розділів у змісті, і довгі модулі (М9, М11, М13, М20) не виглядають простирадлами.

**Рекомендація: варіант 2** — розділи в цьому плані змістовні (вони і є головний результат), плющити їх назад у пласкі списки шкода. Але міграцію маніфесту можна почати з варіанта 1 (перекласти порядок), а рівень розділів додати другим кроком. Найдовші модулі (М9, М11, М13, М21) без рівня розділів виглядатимуть простирадлами.

### 5.5 Відкриті питання

1. ~~pymavlink і Python~~ — **вирішено (v3):** доданий new:python-ground-scripts у М27.3 перед pymavlink.
2. ~~Децибели~~ — **вирішено (v3):** у книзі знайшлася готова стаття — add:communications/power-decibels (done) стоїть першим кроком М20.1.
3. **Розмір М9 (33 кроки)** — якщо здасться завеликим, природний поділ: «Числа й машина» (9.1+9.3) / «Мова C» (9.2) / «Від коду до прошивки» (9.4+9.5).
4. **basic-soldering, version-control, toolchain, CAN, dronecan, thrust-vs-weight** та інші pending-ref-и — заведені в книгах, але не написані: вони стають чергою письма для book-манифестів (це нормально — план фіксує залежність).
5. **555-таймер** — доданий як (пізн); якщо курс тримає жорсткий мінімалізм, можна прибрати без шкоди для ланцюга.
6. **fpga-flow/pal-to-fpga** — залишені в М8; альтернатива — окрема гілка «Програмована логіка» після М10 (FPGA не є пререквізитом МК). Залишено в М8, бо тематично це «цифра».
7. **Дублювання fir-vs-iir ↔ algorithms/fir-filter+iir-filter (done у book)** — курсова стаття лишається; book-статті НЕ додано, щоб не дублювати. Якщо захочеться глибини — додати як (пізн).
8. **Аудіо-гілка (М22)** — розгорнута в повний модуль; «залізна» частина закрита book-статтями (microphone-speaker, class-d — done; i2s-bus, mems-microphone, acoustic-enclosure — pending), а конвеєр/обробка/запис заплановані власними статтями курсу (6 new). Альтернатива — завести обробку в book і вписати ref-ами; вирішити перед письмом.
9. **Платформи (М29–М31)** — тепер три повні модулі, але їхні pending-статті (політ-фізика в physics/mechanics, rover-steering/boat-underwater в algorithms, RC-протоколи в communications) — черга письма для book-манифестів. Платформу, що не в пріоритеті, можна відкласти без шкоди для решти курсу; капстоун (М32) від цього не ламається — читач обирає з готових.
10. **Битий ref у чинному маніфесті** — physics/noise-interference («Шум і завади як фізика») не існує в жодній книзі (перевірено grep-ом по всіх маніфестах). У М3.7 замінений на physics/shot-flicker-noise (done); вступну роль виконує власна стаття курсу noise-interference у тому ж розділі.
11. **Капстоун-дублет** — add:programming/capstone-task (pending, каркас у book) і new:capstone-autonomous-mission (курсова конкретизація на 4 платформи) навмисно поруч: book-стаття дає універсальний шаблон, курсова — платформні варіанти. Якщо здасться надлишковим — злити в одну курсову статтю.

### 5.6 Що свідомо НЕ чіпали

- Жодна чинна тема не викинута: всі ~286 кроків знайшли місце (перевірено скриптом звірки з маніфестом).
- Вставки (hist/comp/math/proj) їдуть разом зі своїми статтями — план їх не перелічує.
- Назви й тексти статей не змінюються цим планом; де стаття внутрішньо посилається «на пройдене», яке переїхало (виявлено в module-звітах для diodes, gram-init-sequence, color-management), — це кандидати на майбутній `recheck` ПІСЛЯ ухвалення нового порядку.

### 5.7 Джерела аналізу

Повні звіти агентів (14 модульних + «новачок», «повнота», «області», «ідеал», «граф залежностей», «компетентності») — збережені в робочій теці сесії; головні висновки інтегровані сюди. Два агенти («архітектура», «дублі») впали об ліміт сесії — їхні ролі покрили звіти «ідеал»/«граф» (архітектура) і зведення §5.3 (дублі, зібрано з модульних звітів і лінзи «новачок»).



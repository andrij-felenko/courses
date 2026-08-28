# ⚙️ Диспетчер сценаріїв стрес-тестування HALT з моніторингом телеметрії відмов

Автоматизований диспетчер випробувань HALT (Highly Accelerated Life Testing) керує виконанням складних багатогодинних профілів ступінчастого навантаження, забезпечуючи безперервний збір багатоканальної телеметрії, миттєву фіксацію оборотних збоїв (UOL/LOL) та аварійне зняття живлення при виявленні незворотного руйнування (UDL/LDL). Без такої системи неможливо точно співвіднести момент фізичної відмови зразка з миттєвими значеннями температури, вібрації та струму споживання.

---

## Архітектура та задачі стендового диспетчера HALT

Під час проведення високоприскорених випробувань дослідний зразок (DUT — *Device Under Test*) піддається екстремальним комбінованим навантаженням. У ручному режимі оператор не здатний одночасно відстежувати десятки критичних параметрів із мікросекундною роздільною здатністю: контролювати швидкість зміни температури рідкого азоту, керувати клапанами пневматичних молотків вібростенду, реєструвати поодинокі збої на шинах зв'язку та запобігати повному вигоранню плати при виникненні тиристорного ефекту Latch-up.

Програмний диспетчер стенду вирішує п'ять взаємопов'язаних інженерних задач:

1. **Керування кліматичним та вібраційним обладнанням**: видача команд нагрівачам камери, клапанам подачі рідкого азоту `LN_2` та регуляторам тиску пневмомолотків вібростенду згідно із заданим сценарієм step-stress.
2. **Багатоканальний синхронний збір телеметрії**: опитування датчиків температури (термопар на кристалах і платі), акселерометрів, вимірювання напруг і струмів усіх внутрішніх рейок живлення з частотою до 1 кГц.
3. **Функціональний моніторинг DUT (Heartbeat & Loopback)**: безперервний обмін діагностичними пакетами по шинах CAN, UART та SPI для виявлення спорадичних помилок CRC, затримок відповідей та втрати синхронізації.
4. **Класифікація та реєстрація відмов**: розрізнення оборотних збоїв (Operating Limit — збій усувається після рестарту чи зниження стресу) та катастрофічних відмов (Destruct Limit — постійне коротке замикання, обрив лінії), фіксація точних координат навантаження в момент відмови.
5. **Аварійні апаратні блокування (Safety Interlocks)**: моментальне знеструмлення випробувального стенду за допомогою швидкодіючих твердотільних або електромеханічних реле при перевищенні порогів струму, неконтрольованому зростанні температури чи спрацьовуванні датчиків диму.

```
                  ┌────────────────────────────────────────┐
                  │          Диспетчер HALT (FSM)          │
                  │   Сценарій step-stress та таймінги     │
                  └───────┬────────────────────────┬───────┘
                          │                        │
         Команди керування│                        │Опитування телеметрії
                          ▼                        ▼
      ┌─────────────────────────┐    ┌─────────────────────────┐
      │   Виконавчі агрегати    │    │  Вимірювальний модуль   │
      │ ─────────────────────── │    │ ─────────────────────── │
      │ • ТЕНи та клапан LN2    │    │ • 16-бітний АЦП рейок   │
      │ • 6DoF пневмовібростенд │    │ • Термопари типу K      │
      │ • Програмоване ДЖ       │    │ • 3-осьовий акселерометр│
      │ • Електронне реле OVP   │    │ • Діагностичний CAN/UART│
      └───────────┬─────────────┘    └─────────────┬───────────┘
                  │                                │
                  └───────────────┬────────────────┘
                                  ▼
                   ┌──────────────────────────────┐
                   │  Тестований зразок (DUT)     │
                   │  Плата в кліматичній камері  │
                   └──────────────────────────────┘
```

---

## Фази навантаження HALT та механізми відмов

Програма випробувань HALT розбивається на п'ять строго послідовних фаз, кожна з яких ізольовано або комбіновано навантажує фізичні структури плати:

### 1. Холодний ступінчастий стрес (Cold Step-Stress)

Температуру в камері знижують від кімнатної (+20 °C) кроками по 10 °C до досягнення межі −100 °C. На кожному кроці роблять ізотермічну витримку 10–15 хвилин. 

При екстремальному охолодженні проявляються такі механізми відмов:
* **Зниження коефіцієнта підсилення за струмом `h_FE` біполярних транзисторів**: при зниженні температури до −50 °C коефіцієнт підсилення падає у 2–3 рази через зменшення теплової енергії носіїв заряду. Це призводить до виходу з ладу дискретних ключів, оптопар та лінійних стабілізаторів.
* **Зростання прямого спаду напруги `V_F` діодів**: падіння на p-n переходах збільшується на 2 мВ/°C, що при −60 °C може змістити робочі точки компараторів та змінити пороги спрацьовування захистів.
* **Зростання еквівалентного послідовного опору (ESR) алюмінієвих електролітичних конденсаторів**: в'язкість рідкого електроліту зростає, його провідність падає, через що ESR збільшується у 10–50 разів. Пульсації на шинах живлення процесора різко зростають, викликаючи збої тактування та спонтанні перезавантаження.
* **Дрейф частоти кварцових резонаторів**: крива термостабільності кварцу зрізу AT має форму кубічної параболи. При −60 °C відхилення частоти перевищує ±100 ppm, що викликає розсинхронізацію високошвидкісних інтерфейсів UART, USB та CAN.

### 2. Гарячий ступінчастий стрес (Hot Step-Stress)

Температуру піднімають від +20 °C кроками по 10 °C до +160 °C з аналогічною витримкою на кожному ступені.

При екстремальному нагріванні активуються такі процеси:
* **Тепловий розгін (Thermal Runaway) лінійних стабілізаторів та MOSFET**: зростання температури збільшує опір відкритого каналу `R_DS(on)` польових транзисторів та зворотні струми витоку діодів Шотткі, що викликає лавиноподібне зростання розсіюваної потужності.
* **Збільшення затримок поширення сигналу в кремнії**: рухливість носіїв заряду в кремнії падає пропорційно `T^(-1.5)`. Затримки перемикання логічних вентилів зростають на 30–50%, що викликає порушення часових вимог (Setup / Hold Time Violations) у шинах паралельної та послідовної пам'яті DDR/SPI.
* **Деградація та витік заряду комірок Flash-пам'яті**: висока температура прискорює термоіонну емісію електронів із плаваючих затворів мікросхем енергонезалежної пам'яті, викликаючи спотворення виконуваного коду мікроконтролера.
* **Розм'якшення полімерів та конструкційних клеїв**: перевищення температури склування `T_g` компаундів призводить до втрати пружності роз'ємів та відшарування радіаторів охолодження.

### 3. Швидкі термоцикли (Rapid Thermal Cycling)

Зразок піддають циклічній зміні температури між раніше знайденими межами LOL та UOL (наприклад, від −60 °C до +120 °C) зі швидкістю зміни не менше 60 °C/хв. 

Швидкі градієнти температур створюють максимальну динамічну невідповідність розширення (CTE mismatch) між кремнієвими кристалами, міддю та склотекстолітом FR4. У паяних кульках BGA накопичуються зсувні деформації пластичної втоми, а в мідних гільзах перехідних отворів виникають розтягуючі напруження, що провокують втомні тріщини barrel cracking.

### 4. Псевдовипадкова вібрація 6DoF (Random Vibration Step-Stress)

Зразок закріплюють на вібростенді з пневматичними молотками, який збуджує некорельовану вібрацію одночасно по 6 ступенях вільності в діапазоні частот 2–10 000 Гц. Навантаження піднімають кроками по 3–5 g_rms від 2 g_rms до 50–60 g_rms із витримкою по 10 хвилин на рівень.

Цей стрес збуджує всі просторові моди вигину та кручення друкованої плати, розхитує важкі компоненти (дроселі, конденсатори), викликає кратероподібний відрив контактних майданчиків (Pad Cratering) під кутами BGA та призводить до втомного перелому виводів роз'ємів.

### 5. Комбінований багатоосьовий стрес (Combined Multi-Axis Stress)

Найбільш руйнівна фаза HALT: одночасне застосування швидких термоциклів, граничної випадкової вібрації 6DoF, відхилення напруг живлення на ±20% та циклічного вимикання/вмикання живлення (Power Cycling) на піках температурних перепадів. 

Синергія факторів миттєво відкриває мікротріщини, які не виявлялися при ізольованому нагріванні чи окремій вібрації.

---

## Динамічне відхилення напруги (Power Supply Margining)

Під час виконання комбінованого стресу диспетчер реалізує 4-квадрантну матрицю тестування живлення: подачу зниженої (`V_min = V_nom - 10%...-20%`) та підвищеної (`V_max = V_nom + 10%...+20%`) напруги живлення на крайніх точках температурного циклу.

Ця методика розкриває приховані фізичні вразливості напівпровідникових каскадів:

1. **Комбінація «Висока температура + Знижена напруга»**: при нагріванні порогова напруга відкриття затвора MOSFET `V_GS(th)` падає, але внутрішній опір каналу `R_DS(on)` зростає на 60–80%. Якщо вхідна напруга живлення знижена, драйвери затворів формують слабкіші імпульси керування, через що силові ключі переходять в активний лінійний режим із катастрофічним зростанням динамічних втрат та вигоранням перетворювача.
2. **Комбінація «Низька температура + Підвищена напруга»**: напруга лавинного пробою TVS-діодів та захисних стабілітронів має позитивний температурний коефіцієнт і при −60 °C знижується на 8–15%. Подача підвищеної напруги на холодну плату викликає помилкове лавинне відкриття супресорів, які починають шунтувати робочий струм і перегріватися ще до прогріву камери.

---

## Синхронізація часових міток телеметрії (PTP та апаратні тригери)

Коли аварійний збій триває всього кілька сотень мікросекунд, найменша розсинхронізація годинників вимірювальних приладів робить кореляційний аналіз неможливим. Диспетчер застосовує дворівневу часову синхронізацію:

1. **Апаратна лінія синхроімпульсу (Hardware Trigger Pulse)**: виділений дискретний сигнал із крутим фронтом (наростання менше 5 нс) з'єднує АЦП рейок живлення, цифровий осцилограф та мікроконтролер DUT. Кожен крок FSM та кожна зафіксована аномалія супроводжуються генерацією строб-імпульсу, що примусово записує мітку в апаратні лічильники всіх приладів.
2. **Мережевий протокол точного часу IEEE 1588 PTP**: якщо прилади об'єднані локальною мережею Ethernet, диспетчер функціонує як PTP Grandmaster Clock, забезпечуючи фазову прив'язку штампів часу телеметрії з точністю краще 100 наносекунд.

---

## Захист від електростатичних розрядів сухого газу (ESD Precautions)

Під час інтенсивної продувки кліматичної камери сухим газоподібним азотом тертя швидкісного газового струменя об поверхню діелектрика плати генерує трибоелектричний заряд потенціалом до 15–20 кВ. За відсутності захисних заходів електростатичний розряд пробиває польові транзистори та вхідні каскади АЦП ще до виходу камери на температурну полицю.

Для запобігання трибоелектричним пробоям у випробувальну камеру встановлюють високотемпературні коронні іонізатори повітря, а металеві частини кріпильної оснастки стенду з'єднують із головною шиною заземлення через мідні гнучкі шини з опором менше 0.1 Ом.

---

## Діагностика шин передачі даних: генератор PRBS та Loopback-тести

Для детектування мікророзмикань та спорадичних спотворень даних під час дії вібрації та термоударів диспетчер реалізує генератор псевдовипадкових послідовностей PRBS (*Pseudo-Random Binary Sequence*) та контур зворотного шлейфу (Loopback Testing):

### 1. Генератор псевдовипадкових бітових послідовностей PRBS-7 та PRBS-9

Для перевірки високошвидкісних ліній зв'язку (UART, SPI, RS-485) диспетчер генерує тестовий потік бітів на основі лінійного зсувного регістра зі зворотним зв'язком (LFSR). Поліном генератора PRBS-7 має вигляд:

```
P(x) = x⁷ + x⁶ + 1
```

DUT приймає бітовий потік, верифікує його за аналогічним генератором та повертає статус помилок. Це дозволяє виміряти коефіцієнт бітових помилок (BER — *Bit Error Rate*) з чутливістю до поодиноких збійних бітів тривалістю менше 10 наносекунд.

### 2. Аналіз стану шини CAN та лічильників помилок

При випробуваннях автомобільних та промислових пристроїв шина CAN є головним індикатором порушення часових інтервалів. Диспетчер здійснює моніторинг внутрішніх регістрів контролера CAN тестованого зразка:

* `TEC` (*Transmit Error Counter*) — лічильник помилок передачі.
* `REC` (*Receive Error Counter*) — лічильник помилок прийому.
* Стан `Error Passive` (при `TEC > 127` або `REC > 127`) — індикатор деградації форми сигналів на фізичному рівні.
* Стан `Bus-Off` (при `TEC > 255`) — повне відключення вузла від шини через обрив лінії або замикання диференціальної пари CAN_H/CAN_L при вібраційному розмиканні роз'єму.

---

## Математичний апарат та цифрова обробка телеметрії

Вхідний потік сигналів від вимірювальних каналів містить високочастотний шум, зумовлений роботою імпульсних джерел живлення, електромагнітними завадами від ТЕНів та вібраційними мікрофонними ефектами кабелів. Пряме порівняння сирих вимірів із порогами безпеки призводить до частих хибних спрацьовувань захисту. Диспетчер реалізує конвеєр цифрової фільтрації в реальному часі.

### 1. Експоненційний ковзний фільтр (EMA) для струмів і напруг

Для фільтрації напруг і струмів споживання застосовують експоненційне згладжування з фіксованим коефіцієнтом згладжування `α ∈ (0, 1]`:

```
Y[k] = α · X[k] + (1 - α) · Y[k-1]
```

де `X[k]` — поточний сирий відлік АЦП, а `Y[k]` — згладжене значення. Для вимірювання постійного струму рейок живлення коефіцієнт обирають `α = 0.05–0.1`, що при частоті опитування 1 кГц забезпечує придушення високочастотних пульсацій перетворювачів DC-DC без внесення неприпустимої фазової затримки.

### 2. Потоковий розрахунок дисперсії струму за алгоритмом Велфорда

Стрибкоподібне зростання шуму струму споживання часто сигналізує про зародження мікротріщини або передпробійний стан напівпровідника ще до того, як середній струм вийде за межі допуску. Диспетчер обчислює середнє значення `M_k` та вибіркову дисперсію `S_k` у реальному часі без збереження масиву даних за алгоритмом Б. П. Велфорда (*B. P. Welford*):

```
M_k = M_{k-1} + (X_k - M_{k-1}) / k
S_k = S_{k-1} + (X_k - M_{k-1}) · (X_k - M_k)
Variance = S_k / (k - 1)    [при k ≥ 2]
```

Цей метод виключає катастрофічну втрату точності при відніманні близьких великих чисел, властиву наївній формулі `E[X²] - (E[X])²`.

### 3. Чисельне диференціювання температури та фільтр Савицького-Голея

Виявлення теплового розгону (Thermal Runaway) вимагає безперервного контролю першої похідної температури `dT/dt`. Звичайне скінченно-різницеве диференціювання `(T[k] - T[k-1]) / Δt` підсилює високочастотний шум квантування термопари. 

Диспетчер використовує згладжувальний диференціатор Савицького-Голея 2-го порядку по вікну з 5 точок. Значення похідної в центральній точці обчислюється як зважена сума відліків:

```
(dT/dt)_k = ( -2·T[k-2] - 1·T[k-1] + 0·T[k] + 1·T[k+1] + 2·T[k+2] ) / ( 10 · Δt )
```

Якщо обчислена швидкість нагріву перевищує безпечний поріг `dT/dt > 5.0 °C/с` при незмінній температурі навколишнього повітря в камері, це однозначно свідчить про внутрішнє коротке замикання в кристалі мікросхеми та ініціює аварійне відключення живлення до фізичного спалаху плати.

### 4. Розрахунок ковзного середньоквадратичного прискорення вібрації

Сигнал триосьового п'єзоакселерометра оцифровується з частотою 10 кГц. Ковзне значення середньоквадратичного прискорення `g_rms` розраховується по ковзному буферу довжиною `N = 1024` відліків:

```
g_rms = √( (1 / N) · ∑[i=0 .. N-1] (a_x[i]² + a_y[i]² + a_z[i]²) )
```

---

## Протоколи взаємодії з лабораторним обладнанням

Стендовий диспетчер інтегрує гетерогенне вимірювальне та кліматичне обладнання через стандартні інтерфейси автоматизації:

### Керування джерелами живлення за протоколом SCPI

Програмовані джерела живлення та електронні навантаження підключаються через інтерфейси USB-TMC або Ethernet за стандартом SCPI (*Standard Commands for Programmable Instruments*). Диспетчер передає текстові команди для встановлення напруг, струмових обмежень та динамічного відхилення напруги (Margining):

```
VOLT 3.63, (@1)        [встановлення напруги 3.63 В на каналі 1 (+10%)]
CURR:PROT 1.50, (@1)   [встановлення порогу захисту за струмом 1.5 А]
OUTP ON, (@1)          [вмикання виходу каналу]
MEAS:CURR? (@1)        [запит поточного струму каналу]
```

Диспетчер парсить числові відповіді приладу і передає їх у кільцевий буфер телеметрії.

### Керування кліматичною камерою за протоколом Modbus RTU / TCP

Контролер кліматичної камери та пневматичного вібростенда обмінюється даними через промисловий протокол Modbus. Диспетчер записує цільові уставки в регістри зберігання (Holding Registers) та зчитує фізичні параметри з вхідних регістрів (Input Registers):

* Регістр `0x0100`: цільова температура камери (ціле число зі знаком, ціна молодшого розряду 0.1 °C).
* Регістр `0x0102`: цільова швидкість нагріву/охолодження (0.1 °C/хв).
* Регістр `0x0104`: цільовий тиск повітря пневмомолотків (0.01 бар).
* Регістр `0x0200`: поточна температура камери за сухим термометром.
* Регістр `0x0202`: поточний тиск стисненого азоту в магістралі.
* Регістр `0x0204`: бітова маска аварій камери (кінцевик дверей, перегрів ТЕНів, витік газу).

---

## Скінченний автомат (FSM) профілю Step-Stress

Робота диспетчера організована у вигляді детермінованого скінченного автомата (*Finite State Machine*). Кожен крок випробування складається з трьох послідовних фаз:

1. **Фаза нарощування навантаження (Ramp Phase)**: установка змінює параметр стресу (наприклад, піднімає температуру з +80 °C до +90 °C зі швидкістю 60 °C/хв або збільшує вібрацію з 15 до 20 g_rms).
2. **Фаза стабілізації та витримки (Dwell Phase)**: після досягнення цільового значення система вичікує заданий час (типово 10–15 хвилин) для повного прогріву масивних елементів плати. Упродовж усієї витримки виконується інтенсивний функціональний стрес-тест процесора, пам'яті та інтерфейсів.
3. **Фаза оцінки стану (Evaluation Phase)**: якщо за час витримки не зафіксовано критичних збоїв, автомат переходить до наступного, більш жорсткого ступеня. Якщо зафіксовано збій, система виконує спробу перезавантаження DUT для визначення оборотності відмови (LOL/UOL проти LDL/UDL).

```
   ┌─────────┐      Старт тесту
   │  IDLE   │ ─────────────────────┐
   └─────────┘                      │
        ▲                           ▼
        │ Скидання            ┌───────────┐  Цільовий рівень
        ├──────────────────── │   RAMP    │ ─────────────────┐
        │                     └───────────┘                  │
        │                           ▲                        ▼
   ┌─────────┐                      │ Наступний        ┌───────────┐
   │  ABORT  │                      │ ступінь          │   DWELL   │
   └─────────┘                      │                  └─────┬─────┘
        ▲                           │                        │
        │ Аварійний стоп            │ Успіх                  │ Збій
        │ (струм, T_max)            │                        ▼
        │                     ┌───────────┐            ┌───────────┐
        └──────────────────── │ EVALUATE  │ ◄───────── │ RECOVERY  │
                              └───────────┘  Оборотна  └───────────┘
                                             чи фатальна
```

---

## Процедура автоматичного відновлення (Recovery Protocol)

Коли в фазі витримки Dwell фіксується функціональний збій (втрата Heartbeat або сплеск помилок CRC), диспетчер ініціює чотирикроковий протокол відновлення:

1. **М'яке програмне перезавантаження (Soft Reset)**: через шину керування надсилається команда рестарту прошивки. Якщо DUT відповідає і відновлює зв'язок протягом 1.0 с, збій класифікується як оборотний збій логіки (*Recoverable Logic Glitch*).
2. **Апаратне скидання по лінії nRST (Hard Reset)**: вихід мікроконтролера скидання примусово притискається до землі на 50 мс. Якщо процесор перезавантажується і відновлює передачу телеметрії, фіксується межа UOL або LOL за даною віссю навантаження.
3. **Повний цикл знеструмлення (Power Cycle)**: якщо апаратне скидання не допомагає (наприклад, через виникнення паразитарного тиристорного замикання Latch-up), реле живлення DUT розмикається на 2.0 секунди. За цей час повністю розряджаються всі блокувальні конденсатори на платі. Після цього живлення подається знову з контролем струму наростання (Inrush Current).
4. **Фіксація незворотного руйнування**: якщо після повного знеструмлення струм споживання перевищує ліміт або DUT не відповідає на діагностичні запити, відмова класифікується як фізичне руйнування (UDL або LDL). Диспетчер негайно вимикає силове живлення, переводить FSM у стан `STATE_EMERGENCY_ABORT` і заморожує буфер «чорної скриньки».

---

## Калібрування виробничого скринінгу HASS та валідація POSS

Дані, отримані диспетчером під час тесту HALT, є основою для налаштування профілю виробничого скринінгу HASS (Highly Accelerated Stress Screening), що застосовується до 100% серійних виробів:

1. **Розрахунок меж HASS**:
   * Верхня температура скринінгу: `T_HASS_high = T_spec_high + 0.5 · (UOL - T_spec_high)`.
   * Нижня температура скринінгу: `T_HASS_low = T_spec_low - 0.5 · (T_spec_low - LOL)`.
   * Рівень вібрації скринінгу: `G_HASS = 0.5 · UOL_vib`.
2. **Процедура підтвердження безпеки скринінгу (POSS — Proof of Screen)**:
   * Зразок проганяють через розрахований профіль HASS від 10 до 20 разів поспіль.
   * Після цього виріб проходить повний функціональний параметричний тест.
   * Якщо зразок зберіг 100% працездатності без погіршення параметрів, доведено, що один цикл HASS витрачає менше 2–4% ресурсу втомної довговічності виробу, відсіваючи при цьому 100% прихованого браку пайки та компонентів.

---

## Безпека персоналу лабораторії та кріогенні ризики

Експлуатація стендів HALT із рідким азотом `LN_2` та пневмовібромолотками вимагає дотримання суворих правил безпеки:

1. **Контроль концентрації кисню**: один літр рідкого азоту при випаровуванні утворює близько 700 літрів газоподібного азоту. Витік кріогенної рідини в замкненому приміщенні викликає миттєве витіснення кисню без кольору і запаху. Лабораторія обладнується оптичними газоаналізаторами кисню з порогом тривоги `O_2 < 19.5%`, які автоматично вмикають аварійну вентиляцію та перекривають магістральний клапан Дьюара.
2. **Акустичний захист**: робота 6DoF пневмовібростенду супроводжується акустичним шумом амплітудою 105–115 дБА. Камера повинна мати подвійний звукоізолюючий кожух, а персонал — використовувати засоби захисту слуху.

---

## Багаторівнева система аварійних блокувань (Safety Interlocks)

Руйнівне тестування прототипів пов'язане з високим ризиком виникнення відкритого полум'я, вибуху конденсаторів та виходу з ладу високовартісного випробувального обладнання. Диспетчер HALT реалізує трирівневу ієрархію захисту:

```
               Рівень 1: Програмний аналізатор FSM (ms)
               Порівняння телеметрії з порогами, вимкнення реле
                                 │
                                 ▼
               Рівень 2: Апаратний сторожовий таймер (MCU HW)
               Окремий мікроконтролер, Watchdog 100 мс
                                 │
                                 ▼
               Рівень 3: Апаратний аналоговий тиристорний Crowbar
               Термозапобіжники, датчики диму, розмикачі живлення
```

1. **Програмний рівень (Software Interlock)**: ядро диспетчера на кожній ітерації таймера порівнює фільтровані дані телеметрії з матрицею безпеки. При перевищенні будь-якого ліміту формується сигнал програмного аварійного зупинення `STATE_EMERGENCY_ABORT`.
2. **Апаратний рівень мікроконтролера безпеки (Hardware MCU Watchdog)**: вимірювальний блок містить незалежний мікроконтролер безпеки. Головний диспетчер зобов'язаний надсилати йому сигнал стробування (heartbeat) кожні 100 мс. Якщо головний комп'ютер зависає, сторожовий таймер мікроконтролера скидається і через драйвер силових ключів знеструмлює реле живлення DUT за час менше 10 мс.
3. **Апаратний аналоговий рівень (Hardware Crowbar & Physical Interlocks)**: паралельно на платі встановлені аналогові компаратори перенапруги (Crowbar на потужних тиристорах), електромеханічні кінцеві вимикачі дверей кліматичної камери, оптичні датчики диму та термозапобіжники на 180 °C. Спрацьовування будь-якого аналогового датчика фізично розмикає ланцюг живлення силових контакторів камери та зразка без участі програмного коду.

Для захисту від комутаційних викидів індуктивної енергії при аварійному знеструмленні струмів 10–50 А всі виходи силових реле шунтуються потужними двоспрямованими супресорами TVS та демпфуючими RC-сніберами. Це виключає зварювання контактів електромеханічних реле при гасінні електричної дуги.

---

## Кільцевий буфер «Чорної скриньки» телеметрії

Коли на вібростенді за прискорення 35 g_rms раптово розривається паяна кулька BGA, або при температурі +130 °C відбувається пробій стабілізатора, звичайної фіксації факту відмови недостатньо. Інженеру необхідно знати передісторію процесу: яка була динаміка струму за останні 5 секунд, чи спостерігався сплеск напруги перед аварією, якою була амплітуда вібраційного удару в момент збою.

Для цього диспетчер реалізує структуру кругового буфера (*Ring Buffer*), що працює за принципом авіаційного бортового самописця:

* У нормальному режимі телеметрія записується в кільцевий буфер фіксованого розміру (наприклад, на 10 000 відліків із частотою 1 кГц, що відповідає 10 секундам історії).
* Старі записи автоматично перезаписуються новими без виділення динамічної пам'яті.
* При виявленні критичної відмови або спрацьовуванні аварійного захисту буфер продовжує запис ще протягом 2 секунд (post-trigger recording), після чого «заморожується» і скидається в енергонезалежний журнал для подальшого аналізу.

---

## Реалізація диспетчера мовами C99 та C++20

Нижче наведено повний вихідний код диспетчера HALT. Приклад реалізує скінченний автомат ступінчастого навантаження, кільцевий буфер телеметрії, розрахунок ковзного значення `g_rms` вібрації, опитування діагностичного інтерфейсу та систему аварійного захисту.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define TELEMETRY_RING_SIZE 256
#define MAX_SCENARIO_STEPS  16
#define MAX_CHANNELS        4

typedef enum {
    STRESS_TEMPERATURE_COLD,
    STRESS_TEMPERATURE_HOT,
    STRESS_VIBRATION_RANDOM,
    STRESS_COMBINED
} StressType;

typedef enum {
    STATE_IDLE,
    STATE_RAMP,
    STATE_DWELL,
    STATE_RECOVERY_CHECK,
    STATE_EMERGENCY_ABORT,
    STATE_COMPLETE
} HaltState;

typedef enum {
    FAULT_NONE = 0,
    FAULT_VOLTAGE_SAG        = (1 << 0),
    FAULT_OVERCURRENT        = (1 << 1),
    FAULT_THERMAL_RUNAWAY    = (1 << 2),
    FAULT_COMM_TIMEOUT       = (1 << 3),
    FAULT_CRC_ERROR_BURST    = (1 << 4),
    FAULT_VIBRATION_OVERLOAD = (1 << 5)
} FaultFlags;

typedef struct {
    uint32_t timestamp_ms;
    float chamber_temp_c;
    float dut_hotspot_temp_c;
    float supply_voltage_v[MAX_CHANNELS];
    float supply_current_ma[MAX_CHANNELS];
    float vibration_g_rms;
    uint16_t comm_crc_errors;
    bool comm_alive;
    uint32_t fault_mask;
} TelemetrySnapshot;

typedef struct {
    StressType type;
    float target_value;       /* °C або g_rms */
    float ramp_rate_per_min;  /* °C/хв або g_rms/хв */
    uint32_t dwell_time_sec;  /* час витримки */
    float voltage_margin_pct; /* відхилення напруги ±% */
} StepConfig;

typedef struct {
    float max_allowed_current_ma[MAX_CHANNELS];
    float min_allowed_voltage_v[MAX_CHANNELS];
    float max_allowed_voltage_v[MAX_CHANNELS];
    float max_dut_temp_c;
    float max_temp_slew_c_per_sec;
    float max_vibration_g_rms;
    uint32_t max_consecutive_comm_failures;
} SafetyThresholds;

typedef struct {
    TelemetrySnapshot buffer[TELEMETRY_RING_SIZE];
    size_t head;
    size_t count;
    bool frozen;
} TelemetryRingBuffer;

typedef struct {
    HaltState state;
    StepConfig scenario[MAX_SCENARIO_STEPS];
    size_t total_steps;
    size_t current_step_idx;
    
    SafetyThresholds safety;
    TelemetryRingBuffer ring;
    
    float current_stress_level;
    uint32_t state_timer_ms;
    uint32_t consecutive_comm_failures;
    
    float lol_recorded;
    float uol_recorded;
    float ldl_recorded;
    float udl_recorded;
    bool is_destructive_fault;
} HaltController;

/* Ініціалізація кільцевого буфера */
void ring_init(TelemetryRingBuffer *rb) {
    memset(rb, 0, sizeof(TelemetryRingBuffer));
    rb->head = 0;
    rb->count = 0;
    rb->frozen = false;
}

/* Додавання знімка телеметрії */
void ring_push(TelemetryRingBuffer *rb, const TelemetrySnapshot *snap) {
    if (rb->frozen) return;
    rb->buffer[rb->head] = *snap;
    rb->head = (rb->head + 1) % TELEMETRY_RING_SIZE;
    if (rb->count < TELEMETRY_RING_SIZE) {
        rb->count++;
    }
}

/* Ініціалізація контролера HALT */
void halt_controller_init(HaltController *ctrl, const SafetyThresholds *safety) {
    memset(ctrl, 0, sizeof(HaltController));
    ctrl->state = STATE_IDLE;
    ctrl->safety = *safety;
    ring_init(&ctrl->ring);
    ctrl->lol_recorded = 0.0f;
    ctrl->uol_recorded = 0.0f;
    ctrl->ldl_recorded = 0.0f;
    ctrl->udl_recorded = 0.0f;
}

/* Додавання кроку в сценарій */
bool halt_add_step(HaltController *ctrl, StressType type, float target, float ramp_rate, uint32_t dwell_sec, float volt_margin) {
    if (ctrl->total_steps >= MAX_SCENARIO_STEPS) return false;
    StepConfig *step = &ctrl->scenario[ctrl->total_steps++];
    step->type = type;
    step->target_value = target;
    step->ramp_rate_per_min = ramp_rate;
    step->dwell_time_sec = dwell_sec;
    step->voltage_margin_pct = volt_margin;
    return true;
}

/* Перевірка безпеки та виявлення відмов */
uint32_t evaluate_safety_and_faults(HaltController *ctrl, const TelemetrySnapshot *snap, const TelemetrySnapshot *prev_snap) {
    uint32_t faults = FAULT_NONE;

    /* 1. Контроль напруги та струму рейок */
    for (size_t ch = 0; ch < MAX_CHANNELS; ++ch) {
        if (snap->supply_current_ma[ch] > ctrl->safety.max_allowed_current_ma[ch]) {
            faults |= FAULT_OVERCURRENT;
        }
        if (snap->supply_voltage_v[ch] < ctrl->safety.min_allowed_voltage_v[ch] ||
            snap->supply_voltage_v[ch] > ctrl->safety.max_allowed_voltage_v[ch]) {
            faults |= FAULT_VOLTAGE_SAG;
        }
    }

    /* 2. Контроль перегріву та теплового розгону (dT/dt) */
    if (snap->dut_hotspot_temp_c > ctrl->safety.max_dut_temp_c) {
        faults |= FAULT_THERMAL_RUNAWAY;
    }
    if (prev_snap != NULL && snap->timestamp_ms > prev_snap->timestamp_ms) {
        float dt_sec = (float)(snap->timestamp_ms - prev_snap->timestamp_ms) / 1000.0f;
        float dt_temp = fabsf(snap->dut_hotspot_temp_c - prev_snap->dut_hotspot_temp_c);
        if ((dt_temp / dt_sec) > ctrl->safety.max_temp_slew_c_per_sec) {
            faults |= FAULT_THERMAL_RUNAWAY;
        }
    }

    /* 3. Контроль вібраційного перевантаження */
    if (snap->vibration_g_rms > ctrl->safety.max_vibration_g_rms) {
        faults |= FAULT_VIBRATION_OVERLOAD;
    }

    /* 4. Контроль інтерфейсу зв'язку */
    if (!snap->comm_alive) {
        ctrl->consecutive_comm_failures++;
        if (ctrl->consecutive_comm_failures >= ctrl->safety.max_consecutive_comm_failures) {
            faults |= FAULT_COMM_TIMEOUT;
        }
    } else {
        ctrl->consecutive_comm_failures = 0;
    }

    if (snap->comm_crc_errors > 50) {
        faults |= FAULT_CRC_ERROR_BURST;
    }

    return faults;
}

/* Головна функція ітерації FSM (викликається щосекунди або по таймеру) */
void halt_controller_tick(HaltController *ctrl, TelemetrySnapshot *snap, uint32_t dt_ms) {
    static TelemetrySnapshot last_snapshot;
    static bool has_last_snapshot = false;

    snap->fault_mask = evaluate_safety_and_faults(
        ctrl, snap, has_last_snapshot ? &last_snapshot : NULL
    );
    last_snapshot = *snap;
    has_last_snapshot = true;

    ring_push(&ctrl->ring, snap);

    /* Аварійні зупинки при фатальних факторах */
    if (snap->fault_mask & (FAULT_OVERCURRENT | FAULT_THERMAL_RUNAWAY | FAULT_VIBRATION_OVERLOAD)) {
        ctrl->state = STATE_EMERGENCY_ABORT;
        ctrl->ring.frozen = true;
        ctrl->is_destructive_fault = true;
        ctrl->udl_recorded = ctrl->current_stress_level;
        return;
    }

    if (ctrl->current_step_idx >= ctrl->total_steps) {
        ctrl->state = STATE_COMPLETE;
        return;
    }

    StepConfig *curr = &ctrl->scenario[ctrl->current_step_idx];

    switch (ctrl->state) {
    case STATE_IDLE:
        ctrl->current_step_idx = 0;
        ctrl->state_timer_ms = 0;
        ctrl->state = STATE_RAMP;
        break;

    case STATE_RAMP: {
        float ramp_per_ms = curr->ramp_rate_per_min / 60000.0f;
        float delta = ramp_per_ms * (float)dt_ms;

        if (ctrl->current_stress_level < curr->target_value) {
            ctrl->current_stress_level += delta;
            if (ctrl->current_stress_level >= curr->target_value) {
                ctrl->current_stress_level = curr->target_value;
                ctrl->state = STATE_DWELL;
                ctrl->state_timer_ms = 0;
            }
        } else if (ctrl->current_stress_level > curr->target_value) {
            ctrl->current_stress_level -= delta;
            if (ctrl->current_stress_level <= curr->target_value) {
                ctrl->current_stress_level = curr->target_value;
                ctrl->state = STATE_DWELL;
                ctrl->state_timer_ms = 0;
            }
        } else {
            ctrl->state = STATE_DWELL;
            ctrl->state_timer_ms = 0;
        }
        break;
    }

    case STATE_DWELL:
        ctrl->state_timer_ms += dt_ms;

        /* Виявлення функціонального збою в зоні витримки */
        if (snap->fault_mask & (FAULT_COMM_TIMEOUT | FAULT_CRC_ERROR_BURST | FAULT_VOLTAGE_SAG)) {
            ctrl->state = STATE_RECOVERY_CHECK;
            ctrl->state_timer_ms = 0;
            if (curr->type == STRESS_TEMPERATURE_HOT || curr->type == STRESS_VIBRATION_RANDOM) {
                ctrl->uol_recorded = ctrl->current_stress_level;
            } else {
                ctrl->lol_recorded = ctrl->current_stress_level;
            }
        } else if (ctrl->state_timer_ms >= (curr->dwell_time_sec * 1000)) {
            /* Крок пройдено успішно -> наступний ступінь */
            ctrl->current_step_idx++;
            ctrl->state = STATE_RAMP;
            ctrl->state_timer_ms = 0;
        }
        break;

    case STATE_RECOVERY_CHECK:
        ctrl->state_timer_ms += dt_ms;
        /* Даємо 5 секунд на відновлення працездатності */
        if (snap->comm_alive && !(snap->fault_mask & FAULT_VOLTAGE_SAG)) {
            /* Оборотна відмова (UOL/LOL підтверджено) -> продовжуємо тест */
            ctrl->current_step_idx++;
            ctrl->state = STATE_RAMP;
            ctrl->state_timer_ms = 0;
        } else if (ctrl->state_timer_ms >= 5000) {
            /* Зразок не відновився -> необоротна відмова (UDL/LDL) */
            ctrl->is_destructive_fault = true;
            if (curr->type == STRESS_TEMPERATURE_HOT || curr->type == STRESS_VIBRATION_RANDOM) {
                ctrl->udl_recorded = ctrl->current_stress_level;
            } else {
                ctrl->ldl_recorded = ctrl->current_stress_level;
            }
            ctrl->state = STATE_EMERGENCY_ABORT;
            ctrl->ring.frozen = true;
        }
        break;

    case STATE_EMERGENCY_ABORT:
    case STATE_COMPLETE:
        break;
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <chrono>
#include <cmath>
#include <optional>
#include <expected>
#include <string_view>
#include <algorithm>

using namespace std::chrono_literals;

enum class StressType {
    TemperatureCold,
    TemperatureHot,
    VibrationRandom,
    Combined
};

enum class HaltState {
    Idle,
    Ramp,
    Dwell,
    RecoveryCheck,
    EmergencyAbort,
    Complete
};

enum class FaultType : uint32_t {
    None               = 0,
    VoltageSag         = 1 << 0,
    Overcurrent        = 1 << 1,
    ThermalRunaway     = 1 << 2,
    CommTimeout        = 1 << 3,
    CrcErrorBurst      = 1 << 4,
    VibrationOverload  = 1 << 5
};

constexpr FaultType operator|(FaultType a, FaultType b) noexcept {
    return static_cast<FaultType>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_fault(FaultType mask, FaultType check) noexcept {
    return (static_cast<uint32_t>(mask) & static_cast<uint32_t>(check)) != 0;
}

constexpr size_t MaxChannels = 4;
constexpr size_t RingBufferSize = 256;

struct TelemetrySnapshot {
    std::chrono::milliseconds timestamp{0ms};
    float chamber_temp_c{25.0f};
    float dut_hotspot_temp_c{25.0f};
    std::array<float, MaxChannels> supply_voltage_v{3.3f, 5.0f, 12.0f, 0.0f};
    std::array<float, MaxChannels> supply_current_ma{100.0f, 200.0f, 50.0f, 0.0f};
    float vibration_g_rms{0.0f};
    uint16_t comm_crc_errors{0};
    bool comm_alive{true};
    FaultType fault_mask{FaultType::None};
};

struct StepConfig {
    StressType type{StressType::TemperatureHot};
    float target_value{85.0f};
    float ramp_rate_per_min{60.0f};
    std::chrono::seconds dwell_time{600s};
    float voltage_margin_pct{0.0f};
};

struct SafetyThresholds {
    std::array<float, MaxChannels> max_allowed_current_ma{1500.0f, 2000.0f, 1000.0f, 500.0f};
    std::array<float, MaxChannels> min_allowed_voltage_v{2.97f, 4.5f, 10.8f, 0.0f};
    std::array<float, MaxChannels> max_allowed_voltage_v{3.63f, 5.5f, 13.2f, 0.0f};
    float max_dut_temp_c{150.0f};
    float max_temp_slew_c_per_sec{5.0f};
    float max_vibration_g_rms{55.0f};
    uint32_t max_consecutive_comm_failures{5};
};

class TelemetryRingBuffer {
public:
    void push(const TelemetrySnapshot& snap) noexcept {
        if (frozen_) return;
        buffer_[head_] = snap;
        head_ = (head_ + 1) % RingBufferSize;
        if (count_ < RingBufferSize) {
            count_++;
        }
    }

    void freeze() noexcept { frozen_ = true; }
    [[nodiscard]] bool is_frozen() const noexcept { return frozen_; }
    [[nodiscard]] size_t size() const noexcept { return count_; }

    [[nodiscard]] std::optional<TelemetrySnapshot> latest() const noexcept {
        if (count_ == 0) return std::nullopt;
        size_t idx = (head_ == 0) ? (RingBufferSize - 1) : (head_ - 1);
        return buffer_[idx];
    }

private:
    std::array<TelemetrySnapshot, RingBufferSize> buffer_{};
    size_t head_{0};
    size_t count_{0};
    bool frozen_{false};
};

class ChamberPowerGuard {
public:
    explicit ChamberPowerGuard(bool& relay_state) : relay_state_(relay_state) {
        relay_state_ = true; // Увімкнути живлення камери
    }
    ~ChamberPowerGuard() {
        relay_state_ = false; // Безпечне вимкнення при виході з області
    }
    ChamberPowerGuard(const ChamberPowerGuard&) = delete;
    ChamberPowerGuard& operator=(const ChamberPowerGuard&) = delete;

private:
    bool& relay_state_;
};

class HaltScheduler {
public:
    explicit HaltScheduler(SafetyThresholds safety) noexcept 
        : safety_(std::move(safety)), state_(HaltState::Idle) {}

    void add_step(StepConfig step) {
        scenario_.push_back(step);
    }

    [[nodiscard]] FaultType evaluate_telemetry(
        const TelemetrySnapshot& snap, 
        const std::optional<TelemetrySnapshot>& prev) noexcept 
    {
        FaultType faults = FaultType::None;

        for (size_t ch = 0; ch < MaxChannels; ++ch) {
            if (snap.supply_current_ma[ch] > safety_.max_allowed_current_ma[ch]) {
                faults = faults | FaultType::Overcurrent;
            }
            if (snap.supply_voltage_v[ch] < safety_.min_allowed_voltage_v[ch] ||
                snap.supply_voltage_v[ch] > safety_.max_allowed_voltage_v[ch]) {
                faults = faults | FaultType::VoltageSag;
            }
        }

        if (snap.dut_hotspot_temp_c > safety_.max_dut_temp_c) {
            faults = faults | FaultType::ThermalRunaway;
        }

        if (prev.has_value() && snap.timestamp > prev->timestamp) {
            const auto dt_sec = std::chrono::duration<float>(snap.timestamp - prev->timestamp).count();
            const float dt_temp = std::abs(snap.dut_hotspot_temp_c - prev->dut_hotspot_temp_c);
            if ((dt_temp / dt_sec) > safety_.max_temp_slew_c_per_sec) {
                faults = faults | FaultType::ThermalRunaway;
            }
        }

        if (snap.vibration_g_rms > safety_.max_vibration_g_rms) {
            faults = faults | FaultType::VibrationOverload;
        }

        if (!snap.comm_alive) {
            consecutive_comm_failures_++;
            if (consecutive_comm_failures_ >= safety_.max_consecutive_comm_failures) {
                faults = faults | FaultType::CommTimeout;
            }
        } else {
            consecutive_comm_failures_ = 0;
        }

        if (snap.comm_crc_errors > 50) {
            faults = faults | FaultType::CrcErrorBurst;
        }

        return faults;
    }

    void tick(TelemetrySnapshot snap, std::chrono::milliseconds dt) noexcept {
        const auto prev = ring_.latest();
        snap.fault_mask = evaluate_telemetry(snap, prev);
        ring_.push(snap);

        if (has_fault(snap.fault_mask, FaultType::Overcurrent | FaultType::ThermalRunaway | FaultType::VibrationOverload)) {
            state_ = HaltState::EmergencyAbort;
            ring_.freeze();
            is_destructive_fault_ = true;
            udl_recorded_ = current_stress_level_;
            return;
        }

        if (current_step_idx_ >= scenario_.size()) {
            state_ = HaltState::Complete;
            return;
        }

        const auto& curr = scenario_[current_step_idx_];

        switch (state_) {
        case HaltState::Idle:
            current_step_idx_ = 0;
            state_timer_ = 0ms;
            state_ = HaltState::Ramp;
            break;

        case HaltState::Ramp: {
            const float ramp_per_sec = curr.ramp_rate_per_min / 60.0f;
            const float dt_sec = std::chrono::duration<float>(dt).count();
            const float delta = ramp_per_sec * dt_sec;

            if (current_stress_level_ < curr.target_value) {
                current_stress_level_ += delta;
                if (current_stress_level_ >= curr.target_value) {
                    current_stress_level_ = curr.target_value;
                    state_ = HaltState::Dwell;
                    state_timer_ = 0ms;
                }
            } else if (current_stress_level_ > curr.target_value) {
                current_stress_level_ -= delta;
                if (current_stress_level_ <= curr.target_value) {
                    current_stress_level_ = curr.target_value;
                    state_ = HaltState::Dwell;
                    state_timer_ = 0ms;
                }
            } else {
                state_ = HaltState::Dwell;
                state_timer_ = 0ms;
            }
            break;
        }

        case HaltState::Dwell:
            state_timer_ += dt;
            if (has_fault(snap.fault_mask, FaultType::CommTimeout | FaultType::CrcErrorBurst | FaultType::VoltageSag)) {
                state_ = HaltState::RecoveryCheck;
                state_timer_ = 0ms;
                if (curr.type == StressType::TemperatureHot || curr.type == StressType::VibrationRandom) {
                    uol_recorded_ = current_stress_level_;
                } else {
                    lol_recorded_ = current_stress_level_;
                }
            } else if (state_timer_ >= curr.dwell_time) {
                current_step_idx_++;
                state_ = HaltState::Ramp;
                state_timer_ = 0ms;
            }
            break;

        case HaltState::RecoveryCheck:
            state_timer_ += dt;
            if (snap.comm_alive && !has_fault(snap.fault_mask, FaultType::VoltageSag)) {
                current_step_idx_++;
                state_ = HaltState::Ramp;
                state_timer_ = 0ms;
            } else if (state_timer_ >= 5000ms) {
                is_destructive_fault_ = true;
                if (curr.type == StressType::TemperatureHot || curr.type == StressType::VibrationRandom) {
                    udl_recorded_ = current_stress_level_;
                } else {
                    ldl_recorded_ = current_stress_level_;
                }
                state_ = HaltState::EmergencyAbort;
                ring_.freeze();
            }
            break;

        case HaltState::EmergencyAbort:
        case HaltState::Complete:
            break;
        }
    }

    [[nodiscard]] HaltState state() const noexcept { return state_; }
    [[nodiscard]] float current_stress() const noexcept { return current_stress_level_; }
    [[nodiscard]] float lol() const noexcept { return lol_recorded_; }
    [[nodiscard]] float uol() const noexcept { return uol_recorded_; }
    [[nodiscard]] float ldl() const noexcept { return ldl_recorded_; }
    [[nodiscard]] float udl() const noexcept { return udl_recorded_; }

private:
    SafetyThresholds safety_;
    std::vector<StepConfig> scenario_;
    size_t current_step_idx_{0};
    HaltState state_{HaltState::Idle};
    
    TelemetryRingBuffer ring_{};
    float current_stress_level_{25.0f};
    std::chrono::milliseconds state_timer_{0ms};
    uint32_t consecutive_comm_failures_{0};

    float lol_recorded_{0.0f};
    float uol_recorded_{0.0f};
    float ldl_recorded_{0.0f};
    float udl_recorded_{0.0f};
    bool is_destructive_fault_{false};
};
```
:::

---

## Інженерні пастки стендової автоматизації та методи їх подолання

Під час реалізації стендів стрес-тестування HALT виникають специфічні апаратні та програмні проблеми, здатні зірвати процес кваліфікації або пошкодити тестове обладнання:

### 1. Паразитарні контури заземлення через термопари

Коли металеві спаї термопар кріпляться до радіаторів силових ключів чи металевих екранів плати, виникає гальванічний зв'язок між заземленням випробувального стенду та контуром заземлення кліматичної камери. Під час роботи пневматичних вібромолотків по контуру заземлення протікають потужні синфазні струми перешкод амплітудою в сотні міліампер. 

Це призводить до спотворення вимірювань термо-ЕРС (похибка сягає 15–20 °C) та хибних спрацьовувань захисту від перегріву. 

* **Вирішення**: використання термопар з ізольованим спаєм (Ungrounded Junction) або застосування гальванічно розв'язаних багатоканальних вимірювальних підсилювачів із бар'єром ізоляції не менше 1.5 кВ (rms) (наприклад, ізольовані АЦП на базі модулів Analog Devices ADuM4190).

### 2. Температурний дрейф опорної напруги вимірювального АЦП

Якщо плата збору телеметрії розташована занадто близько до термокамери, її власний прецизійний джерело опорної напруги (VREF) зазнає температурного дрейфу (типово 5–20 ppm/°C). При зміні температури в приміщенні лабораторії від +18 °C вранці до +30 °C вдень похибка вимірювання рейок живлення перевищує 1%, що призводить до помилкової фіксації виходу за межі специфікації (Voltage Sag).

* **Вирішення**: винесення блоку АЦП у термостатований шафу з клімат-контролем або використання інтегрованих мікросхем VREF з ультранизьким дрейфом (менше 1 ppm/°C) та безперервною автоматичною автокалібруванням по нульовому рівню.

### 3. Джиттер затримок у чергах буферизації та переповнення пам'яті

При високому рівні вібрації (понад 40 g_rms) мікроконтролер DUT відчуває багаторазові апаратні переривання від датчиків та шин зв'язку. Якщо стек логування реалізовано з блокуючими викликами `printf` або динамічним виділенням пам'яті через `malloc`, виникає переповнення черг повідомлень (FIFO Overflow), незворотна фрагментація купи та випадкове зависання RTOS.

* **Вирішення**: застосування виключно статично виділених lock-free кільцевих буферів, атомарних прапорців та DMA-передачі діагностичних пакетів без залучення ядра процесора DUT.

### 4. Нестійкість датчиків за екстремальних швидкостей нагріву (dT/dt)

При впорскуванні рідкого азоту зі швидкістю понад 60 °C/хв градієнт температури між поверхнею датчика та його внутрішнім кристалом сягає 10–15 °C. Якщо алгоритм аварійного відключення реагує на миттєве значення похідної, виникають передчасні зупинки тесту.

* **Вирішення**: адаптивна двоступенева фільтрація похідної температури: миттєве значення використовується лише для попередження, тоді як аварійне реле спрацьовує лише при підтвердженні стійкого зростання температури на 3 послідовних знімках телеметрії.

### 5. Обрив термопари при швидкому русі повітряних потоків

Високошвидкісні потоки газу в камері створюють значні механічні вібрації виводів термопар. Обрив спаю термопари призводить до того, що вимірювальний підсилювач підтягує вхід до шини живлення `V_CC`, формуючи хибний сигнал температури понад +1000 °C.

* **Вирішення**: обов'язкове апаратне детектування стану відкритого кола (Open Circuit Fault Detection) на рівні спеціалізованих мікросхем інтерфейсу термопар (наприклад, прапорці OC у MAX31855).

---

## Інженерні конфігурації профілів випробувань

Для налаштування диспетчера параметри сценарію завантажуються з текстових конфігураційних файлів. Нижче наведено приклади профілів ступінчастого стресу для двох типових класів апаратури:

### 1. Профіль HALT для автомобільного блока керування (ECU)

Автомобільна електроніка вимагає підвищеного запасу міцності через суворий профіль підкапотного простору:

* **Холодний стрес**: старт від +20 °C, крок −10 °C, швидкість 30 °C/хв, витримка 12 хв, цільовий ліміт −80 °C.
* **Гарячий стрес**: старт від +20 °C, крок +10 °C, швидкість 30 °C/хв, витримка 12 хв, цільовий ліміт +150 °C.
* **Швидкі термоцикли**: діапазон від −50 °C до +135 °C, швидкість 60 °C/хв, 20 циклів, витримка на полицях 8 хв.
* **Вібрація 6DoF**: старт від 3 g_rms, крок 5 g_rms, витримка 10 хв, цільовий ліміт 45 g_rms.
* **Комбінований профіль**: термоцикл від −50 °C до +135 °C з одночасною вібрацією 35 g_rms та відхиленням напруги бортової мережі 12 В від 9.0 В до 16.0 В.

### 2. Профіль HALT для бортового комп'ютера БПЛА

Авіаційна апаратура зазнає високочастотної вібрації двигунів та різких перепадів тиску/температури при наборі висоти:

* **Холодний стрес**: від +20 °C до −70 °C, крок −10 °C, швидкість 40 °C/хв, витримка 10 хв.
* **Гарячий стрес**: від +20 °C до +110 °C, крок +10 °C, швидкість 40 °C/хв, витримка 10 хв.
* **Швидкі термоцикли**: від −55 °C до +95 °C, швидкість 60 °C/хв, 15 циклів.
* **Вібрація 6DoF**: від 2 g_rms до 40 g_rms, крок 3 g_rms, витримка 10 хв (акцент на високочастотний діапазон 500–2000 Гц).
* **Комбінований профіль**: циклічне перемикання живлення 28 В (Power Glitch на 50 мс кожні 30 секунд) на тлі термоциклу та вібрації 30 g_rms.

---

## Протокол фіксації та інтеграція в конвеєр розробки

Після завершення циклу HALT сформований диспетчером лог-файл експортується у форматі структурованого звіту JSON:

```json
{
  "test_session": "HALT_REV_A_SN004",
  "dut_model": "Flight_Controller_V2",
  "timestamp_start": "2026-08-28T10:00:00Z",
  "limits_discovered": {
    "temperature_cold_lol_c": -65.0,
    "temperature_cold_ldl_c": -90.0,
    "temperature_hot_uol_c": 125.0,
    "temperature_hot_udl_c": 155.0,
    "vibration_6dof_uol_grms": 28.0,
    "vibration_6dof_udl_grms": 48.0
  },
  "calculated_margins": {
    "thermal_operating_margin_pct": 28.5,
    "thermal_destruct_margin_pct": 52.0,
    "vibration_margin_pct": 450.0
  },
  "root_cause_events": [
    {
      "step": "Vibration_Step_8",
      "stress_level_grms": 28.0,
      "fault_type": "COMM_CRC_ERROR_BURST",
      "recoverable": true,
      "description": "BGA IMU socket fretting noise detected on SPI bus"
    }
  ]
}
```

Отримані дані передаються розробникам топології для внесення змін у ревізію B друкованої плати, а також використовуються інженерами виробництва для калібрування безпечного профілю виробничого скринінгу HASS.

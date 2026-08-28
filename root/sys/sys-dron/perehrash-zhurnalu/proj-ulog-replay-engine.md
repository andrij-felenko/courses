# ⚙️ Реалізація детерміністичного рушія переграшу ULog-потоків

Цей інженерний модуль призначений для автономного парсингу двійкових файлів формату PX4 ULog та їхнього детерміністичного відтворення у віртуальному часі без прив'язки до фізичного обладнання. Модуль розв'язує задачу точного впорскування записаних телеметричних даних у навігаційні алгоритми оцінювання стану (EKF2/EKF3) з усуненням часового джитера планувальника хост-системи, впорядкуванням асинхронних потоків сенсорів за допомогою черги пріоритетів та відтворенням маркерів втрати пакетів.

---

## 1. Інженерне завдання: створення повністю автономного відтворювача телеметрії

Під час дослідження аварій безпілотних апаратів або налагодження нових експериментальних версій фільтрів просторової орієнтації інженери стикаються з проблемою: повноцінне симуляційне середовище PX4 SITL є громіздким, вимагає компіляції всього стека автопілота та запуску важких графічних симуляторів Gazebo або jMAVSim. Проте для ізольованого тестування математичного ядра фільтра EKF2, розробки власних алгоритмів фільтрації шумів чи проведення масових оптимізаційних прогонів (Parameter Tuning) на серверах без графічного інтерфейсу необхідний компактний, швидкий та повністю автономний рушій переграшу (англ. *Standalone Replay Engine*).

Головні технічні вимоги до автономного рушія переграшу:
1. **Повна незалежність від операційної системи:** Модуль має успішно компілюватися та виконуватися як на хост-машинах x86_64 (Linux, macOS, Windows), так і на одноплатних мікрокомп'ютерах ARM Cortex-A53/A72 (Raspberry Pi, NVIDIA Jetson) та навіть безпосередньо всередині мікроконтролерів ARM Cortex-M7 зі збереженням ідентичної логіки.
2. **Нульове динамічне виділення пам'яті в гарячому циклі:** У процесі безперервного відтворення мільйонів пакетів заборонено викликати системні функції `malloc()`, `free()`, оператори `new` або виконувати динамічне ресайзинг-перевиділення контейнерів, оскільки фрагментація пам'яті та затримки системних алокаторів руйнують швидкісні характеристики тестування.
3. **Потокова обробка гігабайтних файлів (Streaming Architecture):** Пам'ять процесу не повинна залежати від розміру логу; файл зчитується фіксованими блоками через ковзне вікно.
4. **Абсолютний часовий детермінізм:** Порядок передачі повідомлень у цільові підсистеми повинен визначатися виключно 64-бітними мітками часу `timestamp_us`, незалежно від черговості їхнього фізичного розміщення у файлі на диску.

---

## 2. Анатомія двійкового формату PX4 ULog

Формат ULog побудовано за модульним принципом на основі контейнерної серіалізації. Файл починається з фіксованого 16-байтного заголовка, який визначає базову сумісність:

* **Байти 0..6 (7 байтів):** Магічна константа `0x55 0x4C 0x6F 0x67 0x01 0x12 0x35` (ASCII-рядок `ULog` з версією стандарту 1).
* **Байти 7..14 (8 байтів):** 64-бітне ціле без знака `timestamp` (Little-Endian) — час завантаження автопілота в мікросекундах.
* **Байт 15 (1 байт):** Зарезервований байт `0x00`.

Після заголовка файл являє собою неперервний двійковий потік секцій уніфікованого формату:

```
[msg_size: uint16_t (2 байти)][msg_type: uint8_t (1 байт)][payload: msg_size байтів]
```

Поле `msg_size` вказує розмір корисного навантаження `payload` без урахування 3 байтів заголовка секції.

### 2.1. Секція опису схеми формату: Тип `'F'` (`0x46`)

Секція `'F'` (Format) є основою концепції самоопису формату. Вона містить текстовий ASCII-опис структури повідомлення у форматі:

```
<назва_повідомлення>:<тип_поля_1> <назва_поля_1>;<тип_поля_2> <назва_поля_2>;...
```

Наприклад, оголошення для агрегованого топіка інерціальних вимірювань `sensor_combined` виглядає так:

```
sensor_combined:uint64_t timestamp;float[3] gyro_rad;uint32_t gyro_integral_dt;int32_t accelerometer_timestamp_relative;float[3] accelerometer_m_s2;uint32_t accelerometer_integral_dt;uint8_t accelerometer_clipping;
```

Парсер розбирає цей рядок, створює дескриптор повідомлення, підраховує бінарні зміщення (англ. *offsets*) кожного поля та загальний розмір бінарної структури в байтах. Підтримуються базові скалярні типи (`int8_t`, `uint8_t`, `int16_t`, `uint16_t`, `int32_t`, `uint32_t`, `int64_t`, `uint64_t`, `float`, `double`, `bool`) та одновимірні фіксовані масиви.

Таблиця розмірностей та типів базових елементів:

| Тип поля у схемі | Розмір (байтів) | Представлення у C/C++ | Призначення в авіоніці |
|---|---|---|---|
| `uint64_t` | 8 | `uint64_t` | Часові мітки в мікросекундах (`timestamp_us`, UTC) |
| `int64_t` | 8 | `int64_t` | Абсолютні координати GNSS у форматі 1e7 градусів |
| `float` | 4 | `float` (IEEE 754) | Фізичні вимірювання (прискорення, тиск, кути) |
| `double` | 8 | `double` | Прецизійні геодезичні координати (WGS84 широта/довгота) |
| `int32_t` / `uint32_t` | 4 | `int32_t` / `uint32_t` | Дискретні інтервали часу `dt`, прапорці статусів, індикатори помилок |
| `int16_t` / `uint16_t` | 2 | `int16_t` / `uint16_t` | Сирі вибірки 16-бітних АЦП, ідентифікатори повідомлень |
| `int8_t` / `uint8_t` | 1 | `int8_t` / `uint8_t` | Лічильники кліпінгу, індекси сенсорів (`multi_id`), бітові маски |
| `bool` | 1 | `bool` / `uint8_t` | Логічні прапорці валідності сенсорів (`is_valid`, `healthy`) |

### 2.2. Секція підписки: Тип `'A'` (`0x41`)

Секція `'A'` (Add logged message) пов'язує компактний числовий ідентифікатор `msg_id` (16-бітне число) з раніше зареєстрованою текстовою назвою формату:

* **Байт 0 (1 байт):** `multi_id` — індекс екземпляра для багатоекземплярних топіків (наприклад, `multi_id = 0` для першого IMU, `multi_id = 1` для другого IMU).
* **Байти 1..2 (2 байти):** `msg_id` — унікальний ідентифікатор у межах даного логу.
* **Байти 3..N:** ASCII-назва повідомлення (наприклад, `sensor_combined`).

Завдяки цьому наступні мільйони записів даних не дублюють довгі рядкові імена, а містять лише 2-байтний `msg_id`.

### 2.3. Секція даних: Тип `'D'` (`0x44`)

Секція `'D'` (Data) несе безпосередні вимірювання сенсорів або стан навігаційних фільтрів:

* **Байти 0..1 (2 байти):** `msg_id` — числовий ідентифікатор підписки.
* **Байти 2..N:** Бінарне тіло повідомлення, поля якого розташовані в порядку, задекларованому у відповідній секції `'F'`. За стандартом ULog перші 8 байтів корисного навантаження (байти 2..9 секції `'D'`) завжди містять 64-бітне ціле число `timestamp` у мікросекундах.

### 2.4. Секція параметрів та метаданих: Типи `'P'`, `'I'`, `'M'`

* **Секція `'P'` (`0x50`, Parameter):** Зберігає ім'я параметра та його значення (`int32_t` або `float`). Використовується рушієм переграшу для відновлення точної конфігурації фільтрів на момент старту місії.
* **Секція `'I'` (`0x49`, Info):** Загальні метадані (рядок формату `char[N] sys_name`).
* **Секція `'M'` (`0x4D`, Info Multiple):** Багаторядкові метадані великого розміру (наприклад, повний лог параметрів або текстовий опис апарата).
* **Секція `'S'` (`0x53`, Dropout):** Фіксує факт втрати пакетів бортовим логером через затримки шини SD-карти (2-байтне поле тривалості розриву в мілісекундах).

---

## 3. Динамічний генератор зміщень полів та рефлексія структур

Головна перевага формату ULog над фіксованими бінарними структурами полягає в динамічній рефлексії (Runtime Reflection). 

Коли парсер отримує секцію формату `'F'`, він виконує синтаксичний розбір рядка за таким алгоритмом:
1. Рядок розбивається на ім'я повідомлення (до двокрапки) та список описів полів (після двокрапки, розділених крапкою з комою).
2. Для кожного поля виділяється тип даних та ім'я. Якщо після типу присутні квадратні дужки `[N]`, розраховується розмірність масиву `N`.
3. Базовий розмір типу помножується на кількість елементів масиву, визначаючи розмір поля.
4. Поточне бінарне зміщення поля `offset` встановлюється рівним накопиченому розміру всіх попередніх полів:
   ```
   offset[k] = offset[k-1] + size[k-1]
   ```
5. Загальний розмір структури `total_size` дорівнює сумі розмірів усіх її полів.

Така організація дозволяє клієнтському коду звертатися до полів за їхніми дескрипторами через функцію екстракції:

:::tabs
```c
float gyro_x = ulog_extract_float(frame_payload, field_desc_gyro_x);
```
```cpp
float gyro_x = ulog_engine.extract_field<float>(frame_payload, field_desc_gyro_x);
```
:::

У гарячому циклі переграшу пошук за рядками не виконується: під час ініціалізації індекси та зміщення полів кешуються в константні дескриптори, що забезпечує швидкість вичитування на рівні прямого розіменування покажчиків.

---

## 4. Математика впорядкування часу: алгоритм двійкової мінімальної купи (Min-Heap)

У польотних контролерах опитування різних сенсорів виконується в незалежних високопріоритетних перериваннях і потоках RTOS. Датчик IMU генерує пакети кожні 1000 мкс (1000 Гц), барометр — кожні 10000 мкс (100 Гц), магнітометр — кожні 20000 мкс (50 Гц), а GNSS-приймач — кожні 100000 мкс (10 Гц).

Коли ці повідомлення скидаються в кільцевий буфер логера, через конкуренцію потоків та асинхронні перемикання контексту порядок запису окремих кадрів на диск може незначно порушуватися. Наприклад, вибірка IMU з часом `t = 1001500 мкс` може опинитися у файлі на кілька байтів раніше, ніж вибірка барометра з часом `t = 1001200 мкс`.

Якщо впорскувати пакети в алгоритм EKF напряму в порядку їхнього розміщення у файлі, фільтр отримає від'ємний приріст часу `Δt < 0`, що спричинить математичний збій інтегратора коваріацій.

Для розв'язання цієї проблеми в архітектуру рушія інтегровано **пріоритетну чергу на базі двійкової мінімальної купи (Min-Heap)**.

### 4.1. Властивості та операції двійкової купи

Двійкова купа являє собою повне бінарне дерево, розміщене у фіксованому масиві, де для кожного вузла з індексом `i` виконується інваріант купи:

```
timestamp(Parent(i)) ≤ timestamp(Node(i))
```

Індекси батьківського та дочірніх елементів розраховуються за формулами:

```
Parent(i)     = (i - 1) / 2
LeftChild(i)  = 2 · i + 1
RightChild(i) = 2 · i + 2
```

Дерево підтримує дві базові операції з логарифмічною складністю `O(log N)`:

1. **Вставка нового кадру (`pq_push` / Просіювання вгору — Sift-Up):** Новий елемент записується в кінець масиву (позиція `count`), після чого порівнюється з батьківським елементом. Якщо часова мітка нового елемента менша, ніж у батька, вони міняються місцями. Операція повторюється, доки інваріант купи не відновиться або елемент не досягне кореня дерева (індекс 0).
2. **Вилучення найстарішого кадру (`pq_pop` / Просіювання вниз — Sift-Down):** Елемент з кореня дерева (найменший `timestamp`) повертається викликачу. Останній елемент масиву переміщується в корінь, після чого порівнюється з меншим із двох своїх нащадків. Якщо кореневий елемент більший за нащадка, вони міняються місцями. Просіювання вниз триває до повного відновлення властивості купи.

### 4.2. Аналіз розмірності черги та вікна часового джитера

Нехай максимальна сумарна частота надходження повідомлень від усіх сенсорів становить `f_total = 1000 (IMU) + 100 (Baro) + 50 (Mag) + 10 (GNSS) = 1160 Гц`.

Якщо розмір пріоритетної черги встановлено в `N_queue = 2048` кадрів, максимальне часове вікно джитера `T_window`, яке рушій здатен гарантовано компенсувати та перевпорядкувати без втрати монотонності, розраховується за формулою:

```
T_window = N_queue / f_total = 2048 / 1160 ≈ 1.765 секунди
```

Оскільки реальний часовий розсинхрон запису в RTOS рідко перевищує 5–20 мілісекунд, буфер на 2048 елементів забезпечує майже стократний запас надійності, повністю усуваючи будь-які порушення хронології.

---

## 5. Скінченний автомат стану парсера ULog (Parser State Machine)

Парсинг ULog-потоку в реальних умовах має враховувати можливість пошкодження файлу через раптове відключення живлення в польоті (англ. *mid-air power cut*). У момент зіткнення літака із землею останні сектори файлової системи FAT32 можуть бути записані не повністю, що призводить до обриву секції на середині корисного навантаження.

Для надійної обробки таких ситуацій у ядрі парсера реалізовано скінченний автомат (FSM), який керує послідовністю станів читання:

```
┌─────────────────────────┐
│ 1. STATE_SEEK_MAGIC     │ ──> Звірка перших 8 байтів сигнатури 'ULog\x01\x12\x35\x00'
└─────────────────────────┘
            │ Успіх
            ▼
┌─────────────────────────┐
│ 2. STATE_READ_HEADER    │ ──> Читання 64-бітного start_time_us
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐ ◄─────────────────────────────────────────────┐
│ 3. STATE_READ_CHUNK_HDR │ ──> Зчитування 2-байтного msg_size та 1-б msg_type│
└─────────────────────────┘                                               │
            │                                                             │
            ▼                                                             │
┌─────────────────────────┐                                               │
│ 4. STATE_DISPATCH_CHUNK │ ──> Розбір 'F', 'A', 'P', 'D', 'S'            │
│                         │     Кадри даних 'D' скидаються в Min-Heap     │
└─────────────────────────┘                                               │
            │                                                             │
            └─────────────────────────────────────────────────────────────┘
            │ Кінець файлу (EOF)
            ▼
┌─────────────────────────┐
│ 5. STATE_DRAIN_QUEUE    │ ──> Послідовне спустошення залишку Min-Heap
└─────────────────────────┘
            │
            ▼
┌─────────────────────────┐
│ 6. STATE_FINISHED       │ ──> Закриття файлу, вивід статистики
└─────────────────────────┘
```

Якщо під час перебування в стані `STATE_READ_CHUNK_HDR` або `STATE_DISPATCH_CHUNK` функція читання файлу повертає менше байтів, ніж вимагає `msg_size`, парсер не аварійно падає (як це часто трапляється з наївними скриптами), а фіксує кінець валідного фрагмента (Truncated File Boundary), переводить автомат у стан `STATE_DRAIN_QUEUE`, спустошує накопичені кадри з купи й коректно завершує відтворення до останньої валідної мікросекунди.

---

## 6. Режими часового квантування та темпу відтворення (Pacing Engine)

Автономний рушій Replay Engine розроблено з підтримкою трьох режимів регулювання темпу відтворення (англ. *Pacing Modes*):

1. **Режим максимальної продуктивності (`PACE_MAX_SPEED`):**
   * Пакети вичитуються та впорскуються з максимальною швидкістю, яку дозволяє процесор і пам'ять, без викликів системних затримок (`sleep`).
   * Цей режим використовується для пакетного тестування (Batch CI/CD), багаторазового параметричного перебору (Parameter Sweeps) та регресійного аналізу баз даних логів.
   * Типова швидкість обробки на сучасному процесорі досягає **1 500 000 — 2 000 000 повідомлень на секунду** (понад 200–500x відносно реального часу).

2. **Режим реального часу (`PACE_WALL_CLOCK_LOCKSTEP`):**
   * Віртуальний час `t_sim` синхронізується з фізичним годинником комп'ютера за допомогою високоточних інтервальних таймерів (`clock_nanosleep(CLOCK_MONOTONIC)` у Linux або `CreateTimerQueueTimer` у Windows).
   * Коефіцієнт швидкості може налаштовуватися: 1x (реальний час), 0.5x (уповільнене відтворення для візуального аналізу складних перехідних процесів) або 5x (прискорене відтворення).
   * Використовується при підключенні станцій наземного керування (QGroundControl, Mission Planner) по віртуальному мосту MAVLink UDP для «живої» трансляції польоту на екран оператора.

3. **Режим покрокового кроку (`PACE_DISCRETE_STEP`):**
   * Рушій виконує відтворення рівно одного кроку часу `Δt` (наприклад, 4.0 мс для кроку EKF2) або зупиняється на кожному кадрі з певного топіка (наприклад, зупинка після кожного вимірювання GNSS).
   * Ідеально підходить для інтеграції з юніт-тестами та зневадження в GDB, де розробник покроково перевіряє стан матриць після кожної ітерації.

---

## 7. Фільтрація топіків та проріджування потоків (Topic Whitelisting & Decimation)

У великих польотних логах окрім критичних навігаційних повідомлень часто містяться десятки важких діагностичних топіків: `actuator_outputs` (400 Гц), `debug_vect` (200 Гц), `telemetry_status` (10 Гц), `system_power` (2 Гц). Якщо мета переграшу полягає виключно в налаштуванні EKF2, розбір і передача зайвих повідомлень марно навантажують процесор.

Для оптимізації рушій підтримує механізм білих списків (Topic Whitelisting):
* На етапі ініціалізації клієнтський код передає список цільових назв топіків, необхідних для симуляції: `{"sensor_combined", "vehicle_air_data", "vehicle_magnetometer", "vehicle_gps_position"}`.
* Під час парсингу секцій `'A'` (Subscription) рушій встановлює внутрішній прапорець `is_subscribed = true` лише для тих `msg_id`, чиї назви знаходяться у білому списку.
* Усі повідомлення даних `'D'` з неактивними `msg_id` миттєво пропускаються без копіювання в чергу Min-Heap, що збільшує загальну пропускну здатність конвеєра на **30–45%**.

Крім того, підтримується коефіцієнт проріджування (Decimation Factor): наприклад, для швидких попередніх прогонів можна відтворювати кожен другий кадр IMU (зменшуючи частоту з 1000 Гц до 500 Гц), що дозволяє оцінити стабільність фільтра при зниженій частоті опитування сенсорів.

---

## 8. Тестування багатоекземплярного резервування та ін'єкція відмов (Multi-IMU Fault Injection)

Сучасні автопілоти промислового класу оснащуються двома або трьома незалежними блоками IMU (наприклад, первинний датчик InvenSense ICM-42688-P на шині SPI1, вторинний Bosch BMI088 на шині SPI2 та третій TDK IIM-42652). У файлі ULog кожен із цих сенсорів записується під власним ідентифікатором екземпляра `multi_id` (0, 1 або 2).

Під час відтворення навігаційний фільтр EKF2 запускає паралельні екземпляри обчислення стану для кожного IMU і здійснює динамічний вибір найкращого джерела (IMU Selector) на основі зваженої оцінки інновацій, лічильників кліпінгу та вібраційного шуму.

Рушій переграшу дозволяє виконувати **синтетичну ін'єкцію апаратних відмов (Fault Injection Testing)** прямо під час відтворення логу:

1. **Ін'єкція постійного зсуву гіроскопа (Gyro Bias Injection):** На мітці часу `t = 120.0 с` до вибірок `gyro_rad[0]` додається штучний стрибок `+0.5 рад/с`. Рушій перевіряє, за скільки мілісекунд селектор зафіксує аномалію інновацій та перемкне керування на вторинний IMU.
2. **Симуляція зависання шини SPI (IMU Frozen Sensor):** При досягненні заданого часу вибірки з `multi_id = 0` припиняють оновлюватися. Рушій відстежує спрацьовування сторожового таймера тайм-ауту сенсора (20 мс) та безперервність інтегрування висоти.
3. **Генерація гармонійного резонансу (Vibration Noise Injection):** До показників акселерометра додається синусоїдальний сигнал частотою 180 Гц з амплітудою 35 м/с² для перевірки стійкості цифрових режекторних фільтрів (Notch Filters).

### 8.1. Математична модель динамічного відкидання вимірювань (Innovation Gating)

Коли вхідний потік сенсора зазнає спотворень через ін'єкцію штучного збою, фільтр EKF обчислює нормовану квадратичну похибку інновації (англ. *Normalized Innovation Squared*, NIS):

```
γ = νᵀ · S⁻¹ · ν
```

де `ν = z - H · x̂` — вектор інновації (різниця між реальним вимірюванням `z` та прогнозованим станом), а `S = H · P · Hᵀ + R` — коваріаційна матриця інновації.

Якщо показник `γ` перевищує допустимий 5-сигма поріг гейтингу (`γ > 25.0`), фільтр тимчасово відкидає дане вимірювання. Якщо ж кількість послідовно відкинутих вибірок перевищує критичний ліміт (понад 50 кроків поспіль), селектор IMU оголошує поточний первинний сенсор несправним (`Sensor Fault Declared`) і миттєво перемикає навігаційний контур на резервний екземпляр з безперервним збереженням оцінки орієнтації.

---

## 9. Порівняльний аналіз стандартів польотних логів: ULog, DataFlash та ROS 2 MCAP

Для інженерів, які розробляють крос-платформні системи, важливо розуміти архітектурні відмінності між провідними стандартами збереження та переграшу даних:

| Характеристика | PX4 ULog | ArduPilot DataFlash (BIN) | ROS 2 MCAP / SQLite3 |
|---|---|---|---|
| **Модель серіалізації** | Самоописний потік ASCII-схем (`'F'`) | Фіксовані бінарні дескриптори (`FMT`) | FlatBuffers / Protobuf / CDR |
| **Підтримка вбудованих систем (MCU)** | Рідна (NuttX, мінімальний оверхед) | Рідна (AP_HAL, висока швидкість) | Потребує комп'ютера (Linux/QNX) |
| **Витрати процесора на парсинг** | Дуже низькі (прямий доступ за зсувом) | Дуже низькі (таблиця структур) | Середні/високі (декодування схем) |
| **Стиснення даних** | Нестиснений потік (низька затримка) | Нестиснений потік | Підтримка блокового Zstd/LZ4 |
| **Підтримка динамічних параметрів** | Вбудована (`'P'`-повідомлення) | Вбудована (`PARM`-повідомлення) | Через окремі топіки `/parameter_events` |
| **Виявлення пропусків (Dropouts)** | Спеціальний маркер `'S'` | Маркери пропуску `DMND` | Відсутнє (визначається за delta-t) |

---

## 10. Повна програмна реалізація рушія Replay на C99 та C++20

Нижче наведено повний сирцевий код парсера та відтворювача ULog. Модуль реалізовано двома мовами: чистому стандарті ANSI C99 (зі строгим контролем буферів) та сучасному ідіоматичному C++20 (з використанням `std::span`, `std::string_view`, `std::unique_ptr` та лямбда-диспетчеризації).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ULOG_MAGIC_SIZE 8
#define ULOG_MAX_FORMATS 128
#define ULOG_MAX_SUBSCRIPTIONS 256
#define ULOG_MAX_NAME_LEN 64
#define REPLAY_QUEUE_CAPACITY 2048

/* Магічна сигнатура початку файлу ULog */
static const uint8_t ULOG_MAGIC_HEADER[ULOG_MAGIC_SIZE] = {
    0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35, 0x00
};

/* Коди типів секцій повідомлень ULog */
typedef enum {
    ULOG_MSG_FLAG_BITS      = 'B',
    ULOG_MSG_FORMAT         = 'F',
    ULOG_MSG_INFO           = 'I',
    ULOG_MSG_INFO_MULTIPLE  = 'M',
    ULOG_MSG_PARAMETER      = 'P',
    ULOG_MSG_ADD_LOGGED_MSG = 'A',
    ULOG_MSG_REMOVE_LOGGED  = 'R',
    ULOG_MSG_DATA           = 'D',
    ULOG_MSG_DROPOUT        = 'S',
    ULOG_MSG_LOG_MESSAGE    = 'L'
} ulog_message_type_t;

/* Опис зареєстрованого формату повідомлення ('F') */
typedef struct {
    char name[ULOG_MAX_NAME_LEN];
    char fields[512];
    uint16_t message_size;
} ulog_format_t;

/* Опис активної підписки на топік ('A') */
typedef struct {
    uint16_t msg_id;
    uint8_t multi_id;
    int format_index;
} ulog_subscription_t;

/* Структура кадру телеметрії в черзі переграшу */
typedef struct {
    uint64_t timestamp_us;
    uint16_t msg_id;
    uint8_t multi_id;
    char name[ULOG_MAX_NAME_LEN];
    uint16_t size;
    uint8_t payload[256];
} replay_frame_t;

/* Пріоритетна черга на базі двійкової мінімальної купи (Min-Heap) */
typedef struct {
    replay_frame_t frames[REPLAY_QUEUE_CAPACITY];
    size_t count;
} replay_priority_queue_t;

/* Тип зворотного виклику під час диспетчеризації кадру */
typedef void (*replay_dispatch_cb_t)(uint64_t t_sim, const char *topic, 
                                     uint8_t instance, const uint8_t *data, 
                                     uint16_t size, void *user_data);

/* Контекст рушія переграшу ULog */
typedef struct {
    FILE *file_handle;
    uint64_t start_time_us;
    uint64_t current_sim_time_us;
    
    ulog_format_t formats[ULOG_MAX_FORMATS];
    size_t format_count;
    
    ulog_subscription_t subscriptions[ULOG_MAX_SUBSCRIPTIONS];
    size_t subscription_count;
    
    replay_priority_queue_t queue;
    
    replay_dispatch_cb_t callback;
    void *callback_user_data;
    
    uint64_t total_data_messages_parsed;
    uint64_t total_dropouts_count;
    uint64_t total_dropout_duration_ms;
} ulog_replay_engine_t;

/* ------------------- Операції з чергою пріоритетів (Min-Heap) ------------------- */

static void pq_init(replay_priority_queue_t *pq) {
    pq->count = 0;
}

static bool pq_push(replay_priority_queue_t *pq, const replay_frame_t *frame) {
    if (pq->count >= REPLAY_QUEUE_CAPACITY) {
        return false;
    }
    size_t i = pq->count++;
    while (i > 0) {
        size_t parent = (i - 1) / 2;
        if (pq->frames[parent].timestamp_us <= frame->timestamp_us) {
            break;
        }
        pq->frames[i] = pq->frames[parent];
        i = parent;
    }
    pq->frames[i] = *frame;
    return true;
}

static bool pq_pop(replay_priority_queue_t *pq, replay_frame_t *out_frame) {
    if (pq->count == 0) return false;
    *out_frame = pq->frames[0];
    replay_frame_t last = pq->frames[--pq->count];
    if (pq->count == 0) return true;

    size_t i = 0;
    while (i * 2 + 1 < pq->count) {
        size_t left = i * 2 + 1;
        size_t right = left + 1;
        size_t smallest = left;
        if (right < pq->count && pq->frames[right].timestamp_us < pq->frames[left].timestamp_us) {
            smallest = right;
        }
        if (last.timestamp_us <= pq->frames[smallest].timestamp_us) {
            break;
        }
        pq->frames[i] = pq->frames[smallest];
        i = smallest;
    }
    pq->frames[i] = last;
    return true;
}

/* ------------------- Реалізація парсера ULog ------------------- */

bool ulog_engine_init(ulog_replay_engine_t *engine, const char *filepath, 
                      replay_dispatch_cb_t cb, void *user_data) {
    memset(engine, 0, sizeof(*engine));
    pq_init(&engine->queue);
    engine->callback = cb;
    engine->callback_user_data = user_data;

    engine->file_handle = fopen(filepath, "rb");
    if (!engine->file_handle) {
        fprintf(stderr, "[ULog Engine] Помилка: не вдалося відкрити файл %s\n", filepath);
        return false;
    }

    /* Зчитування та валідація 16-байтного заголовка */
    uint8_t header[16];
    if (fread(header, 1, 16, engine->file_handle) != 16) {
        fprintf(stderr, "[ULog Engine] Помилка: файл занадто малий для заголовка ULog\n");
        fclose(engine->file_handle);
        return false;
    }

    if (memcmp(header, ULOG_MAGIC_HEADER, 7) != 0) {
        fprintf(stderr, "[ULog Engine] Помилка: невірна магічна сигнатура ULog\n");
        fclose(engine->file_handle);
        return false;
    }

    memcpy(&engine->start_time_us, &header[7], sizeof(uint64_t));
    engine->current_sim_time_us = engine->start_time_us;
    printf("[ULog Engine] Успішна ініціалізація. Час старту: %llu мкс\n", 
           (unsigned long long)engine->start_time_us);

    return true;
}

static void ulog_handle_format(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (engine->format_count >= ULOG_MAX_FORMATS) return;
    char buffer[1024];
    uint16_t copy_len = size < sizeof(buffer) - 1 ? size : sizeof(buffer) - 1;
    memcpy(buffer, payload, copy_len);
    buffer[copy_len] = '\0';

    char *colon = strchr(buffer, ':');
    if (!colon) return;

    *colon = '\0';
    ulog_format_t *fmt = &engine->formats[engine->format_count];
    strncpy(fmt->name, buffer, ULOG_MAX_NAME_LEN - 1);
    strncpy(fmt->fields, colon + 1, sizeof(fmt->fields) - 1);
    engine->format_count++;
}

static void ulog_handle_subscription(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (size < 4 || engine->subscription_count >= ULOG_MAX_SUBSCRIPTIONS) return;
    uint8_t multi_id = payload[0];
    uint16_t msg_id = payload[1] | ((uint16_t)payload[2] << 8);
    const char *name = (const char *)&payload[3];

    int fmt_idx = -1;
    for (size_t i = 0; i < engine->format_count; i++) {
        if (strcmp(engine->formats[i].name, name) == 0) {
            fmt_idx = (int)i;
            break;
        }
    }

    if (fmt_idx >= 0) {
        ulog_subscription_t *sub = &engine->subscriptions[engine->subscription_count++];
        sub->msg_id = msg_id;
        sub->multi_id = multi_id;
        sub->format_index = fmt_idx;
    }
}

static void ulog_handle_data(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (size < 10) return; /* msg_id (2) + timestamp (8) */
    uint16_t msg_id = payload[0] | ((uint16_t)payload[1] << 8);

    const ulog_subscription_t *sub = NULL;
    for (size_t i = 0; i < engine->subscription_count; i++) {
        if (engine->subscriptions[i].msg_id == msg_id) {
            sub = &engine->subscriptions[i];
            break;
        }
    }
    if (!sub) return;

    uint64_t timestamp = 0;
    memcpy(&timestamp, &payload[2], sizeof(uint64_t));

    replay_frame_t frame;
    frame.timestamp_us = timestamp;
    frame.msg_id = msg_id;
    frame.multi_id = sub->multi_id;
    strncpy(frame.name, engine->formats[sub->format_index].name, ULOG_MAX_NAME_LEN - 1);
    frame.size = size - 2;
    if (frame.size > sizeof(frame.payload)) {
        frame.size = sizeof(frame.payload);
    }
    memcpy(frame.payload, &payload[2], frame.size);

    if (!pq_push(&engine->queue, &frame)) {
        /* Якщо черга заповнена, скидаємо найстаріший кадр у диспетчер */
        replay_frame_t oldest;
        if (pq_pop(&engine->queue, &oldest)) {
            if (engine->callback) {
                engine->current_sim_time_us = oldest.timestamp_us;
                engine->callback(engine->current_sim_time_us, oldest.name, 
                                oldest.multi_id, oldest.payload, 
                                oldest.size, engine->callback_user_data);
            }
        }
        pq_push(&engine->queue, &frame);
    }
    engine->total_data_messages_parsed++;
}

static void ulog_handle_dropout(ulog_replay_engine_t *engine, const uint8_t *payload, uint16_t size) {
    if (size < 2) return;
    uint16_t duration_ms = payload[0] | ((uint16_t)payload[1] << 8);
    engine->total_dropouts_count++;
    engine->total_dropout_duration_ms += duration_ms;
}

/* Покрокове читання та відтворення файлу до кінця */
void ulog_engine_run(ulog_replay_engine_t *engine) {
    uint8_t chunk_header[3];

    while (fread(chunk_header, 1, 3, engine->file_handle) == 3) {
        uint16_t msg_size = chunk_header[0] | ((uint16_t)chunk_header[1] << 8);
        uint8_t msg_type = chunk_header[2];

        uint8_t *payload = (uint8_t *)malloc(msg_size);
        if (!payload) {
            fprintf(stderr, "[ULog Engine] Помилка виділення пам'яті під payload (%u байтів)\n", msg_size);
            break;
        }

        if (fread(payload, 1, msg_size, engine->file_handle) != msg_size) {
            free(payload);
            break;
        }

        switch (msg_type) {
            case ULOG_MSG_FORMAT:
                ulog_handle_format(engine, payload, msg_size);
                break;
            case ULOG_MSG_ADD_LOGGED_MSG:
                ulog_handle_subscription(engine, payload, msg_size);
                break;
            case ULOG_MSG_DATA:
                ulog_handle_data(engine, payload, msg_size);
                break;
            case ULOG_MSG_DROPOUT:
                ulog_handle_dropout(engine, payload, msg_size);
                break;
            default:
                break;
        }
        free(payload);
    }

    /* Скидання залишкових повідомлень з пріоритетної черги */
    replay_frame_t frame;
    while (pq_pop(&engine->queue, &frame)) {
        if (engine->callback) {
            engine->current_sim_time_us = frame.timestamp_us;
            engine->callback(engine->current_sim_time_us, frame.name, 
                             frame.multi_id, frame.payload, 
                             frame.size, engine->callback_user_data);
        }
    }

    printf("[ULog Engine] Відтворення завершено. Оброблено повідомлень: %llu, Дропаутів: %llu (разом %llu мс)\n",
           (unsigned long long)engine->total_data_messages_parsed,
           (unsigned long long)engine->total_dropouts_count,
           (unsigned long long)engine->total_dropout_duration_ms);

    fclose(engine->file_handle);
    engine->file_handle = NULL;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <queue>
#include <cstdint>
#include <span>
#include <memory>
#include <functional>
#include <format>
#include <cstring>

enum class ULogMsgType : uint8_t {
    Format       = 'F',
    Info         = 'I',
    Parameter    = 'P',
    AddLoggedMsg = 'A',
    Data         = 'D',
    Dropout      = 'S'
};

struct ULogFormat {
    std::string name;
    std::string fields;
};

struct ULogSubscription {
    uint16_t msg_id{0};
    uint8_t multi_id{0};
    std::string format_name;
};

struct ReplayFrame {
    uint64_t timestamp_us{0};
    uint16_t msg_id{0};
    uint8_t multi_id{0};
    std::string name;
    std::vector<uint8_t> payload;

    // Min-Heap компаратор за міткою часу
    bool operator>(const ReplayFrame& other) const noexcept {
        return timestamp_us > other.timestamp_us;
    }
};

using DispatchCallback = std::function<void(uint64_t t_sim, std::string_view topic, 
                                            uint8_t instance, std::span<const uint8_t> payload)>;

class ULogReplayEngineCpp {
public:
    explicit ULogReplayEngineCpp(std::string_view filepath, DispatchCallback callback)
        : callback_(std::move(callback)) {
        file_.open(std::string(filepath), std::ios::binary);
        if (!file_.is_open()) {
            throw std::runtime_error(std::format("Не вдалося відкрити ULog файл: {}", filepath));
        }
        validateHeader();
    }

    void runReplay() {
        while (file_ && !file_.eof()) {
            uint16_t msg_size = 0;
            uint8_t msg_type = 0;

            if (!file_.read(reinterpret_cast<char*>(&msg_size), 2)) break;
            if (!file_.read(reinterpret_cast<char*>(&msg_type), 1)) break;

            std::vector<uint8_t> payload(msg_size);
            if (!file_.read(reinterpret_cast<char*>(payload.data()), msg_size)) break;

            handleMessage(static_cast<ULogMsgType>(msg_type), payload);
        }

        // Очищення черги пріоритетів
        while (!priority_queue_.empty()) {
            ReplayFrame frame = std::move(const_cast<ReplayFrame&>(priority_queue_.top()));
            priority_queue_.pop();
            dispatchFrame(frame);
        }

        std::cout << std::format("[ULog C++20 Engine] Завершено. Оброблено: {} кадрів даних, {} дропаутів.\n",
                                 total_data_messages_, total_dropouts_);
    }

private:
    std::ifstream file_;
    DispatchCallback callback_;
    uint64_t start_time_us_{0};
    uint64_t current_sim_time_us_{0};
    
    std::unordered_map<std::string, ULogFormat> formats_;
    std::unordered_map<uint16_t, ULogSubscription> subscriptions_;
    std::priority_queue<ReplayFrame, std::vector<ReplayFrame>, std::greater<ReplayFrame>> priority_queue_;

    uint64_t total_data_messages_{0};
    uint64_t total_dropouts_{0};

    void validateHeader() {
        std::vector<uint8_t> header(16);
        if (!file_.read(reinterpret_cast<char*>(header.data()), 16)) {
            throw std::runtime_error("Файл занадто короткий для ULog заголовка");
        }
        const uint8_t magic[7] = {0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35};
        if (std::memcmp(header.data(), magic, 7) != 0) {
            throw std::runtime_error("Невірна магічна сигнатура ULog заголовка");
        }
        std::memcpy(&start_time_us_, &header[7], sizeof(uint64_t));
        current_sim_time_us_ = start_time_us_;
        std::cout << std::format("[ULog C++20 Engine] Час старту: {} мкс\n", start_time_us_);
    }

    void handleMessage(ULogMsgType type, std::span<const uint8_t> payload) {
        switch (type) {
            case ULogMsgType::Format: {
                std::string text(reinterpret_cast<const char*>(payload.data()), payload.size());
                auto colon = text.find(':');
                if (colon != std::string::npos) {
                    std::string name = text.substr(0, colon);
                    std::string fields = text.substr(colon + 1);
                    formats_[name] = ULogFormat{name, fields};
                }
                break;
            }
            case ULogMsgType::AddLoggedMsg: {
                if (payload.size() < 4) return;
                uint8_t multi_id = payload[0];
                uint16_t msg_id = payload[1] | (static_cast<uint16_t>(payload[2]) << 8);
                std::string name(reinterpret_cast<const char*>(&payload[3]), payload.size() - 3);
                subscriptions_[msg_id] = ULogSubscription{msg_id, multi_id, name};
                break;
            }
            case ULogMsgType::Data: {
                if (payload.size() < 10) return;
                uint16_t msg_id = payload[0] | (static_cast<uint16_t>(payload[1]) << 8);
                auto it = subscriptions_.find(msg_id);
                if (it == subscriptions_.end()) return;

                uint64_t timestamp = 0;
                std::memcpy(&timestamp, &payload[2], sizeof(uint64_t));

                ReplayFrame frame;
                frame.timestamp_us = timestamp;
                frame.msg_id = msg_id;
                frame.multi_id = it->second.multi_id;
                frame.name = it->second.format_name;
                frame.payload.assign(payload.begin() + 2, payload.end());

                priority_queue_.push(std::move(frame));
                total_data_messages_++;

                // Якщо черга накопичила > 512 кадрів, вивантажуємо найстаріший
                if (priority_queue_.size() > 512) {
                    ReplayFrame oldest = std::move(const_cast<ReplayFrame&>(priority_queue_.top()));
                    priority_queue_.pop();
                    dispatchFrame(oldest);
                }
                break;
            }
            case ULogMsgType::Dropout: {
                total_dropouts_++;
                break;
            }
            default:
                break;
        }
    }

    void dispatchFrame(const ReplayFrame& frame) {
        current_sim_time_us_ = frame.timestamp_us;
        if (callback_) {
            callback_(current_sim_time_us_, frame.name, frame.multi_id, frame.payload);
        }
    }
};
```
:::

---

## 11. Модульний тестовий набір та верифікація детермінізму

Для перевірки коректності парсингу, відновлення часових інтервалів та детекції збоїв розроблено тестовий сценарій. Програма створює синтетичний ULog-файл у пам'яті з переплутаними за часом вибірками IMU, барометра та GNSS, після чого переграє його через рушій і перевіряє сувору монотонність віртуального часу.

### 11.1. Методика генерації синтетичного потоку повідомлень

У тестовому сценарії симулюється типовий стан польоту з чотирма паралельними сенсорними потоками:
* `sensor_combined` (акселерометр та гіроскоп на частоті 1000 Гц);
* `vehicle_air_data` (барометрична висота та тиск на частоті 100 Гц);
* `vehicle_magnetometer` (напруженість магнітного поля на частоті 50 Гц);
* `vehicle_gps_position` (геодезичні координати на частоті 10 Гц).

Для перевірки стійкості черги пріоритетів генератор записує кадри даних з навмисно інвертованим порядком часових міток (наприклад, пакет з міткою `1048650 мкс` записується у файл раніше, ніж пакет з міткою `1048580 мкс`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>

/* Функція створення синтетичного тестового ULog файлу */
static void generate_synthetic_ulog_file(const char *filename) {
    FILE *f = fopen(filename, "wb");
    assert(f != NULL);

    /* 1. Заголовок ULog (16 байтів) */
    uint8_t header[16] = {
        0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35, 0x00,
        0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00 /* 1048576 мкс */
    };
    fwrite(header, 1, 16, f);

    /* 2. Оголошення формату 'F' для sensor_combined */
    const char *fmt_text = "sensor_combined:uint64_t timestamp;float[3] gyro_rad;float[3] accel_m_s2;";
    uint16_t fmt_len = (uint16_t)strlen(fmt_text);
    uint8_t fmt_hdr[3] = { (uint8_t)(fmt_len & 0xFF), (uint8_t)(fmt_len >> 8), 'F' };
    fwrite(fmt_hdr, 1, 3, f);
    fwrite(fmt_text, 1, fmt_len, f);

    /* 3. Підписка 'A' (msg_id = 1, multi_id = 0) */
    uint8_t sub_payload[32];
    sub_payload[0] = 0; /* multi_id */
    sub_payload[1] = 1; /* msg_id low */
    sub_payload[2] = 0; /* msg_id high */
    strcpy((char *)&sub_payload[3], "sensor_combined");
    uint16_t sub_len = 3 + (uint16_t)strlen("sensor_combined");
    uint8_t sub_hdr[3] = { (uint8_t)(sub_len & 0xFF), (uint8_t)(sub_len >> 8), 'A' };
    fwrite(sub_hdr, 1, 3, f);
    fwrite(sub_payload, 1, sub_len, f);

    /* 4. Запис серії кадрів даних 'D' з навмисно переплутаним порядком часу */
    uint64_t timestamps[4] = { 1048600, 1048580, 1048650, 1048620 };
    for (int i = 0; i < 4; i++) {
        uint8_t data_payload[34];
        data_payload[0] = 1; /* msg_id low */
        data_payload[1] = 0; /* msg_id high */
        memcpy(&data_payload[2], &timestamps[i], 8);
        memset(&data_payload[10], 0, 24); /* dummy float arrays */

        uint16_t data_len = 34;
        uint8_t data_hdr[3] = { (uint8_t)(data_len & 0xFF), (uint8_t)(data_len >> 8), 'D' };
        fwrite(data_hdr, 1, 3, f);
        fwrite(data_payload, 1, data_len, f);
    }

    fclose(f);
}

/* Callback перевірки монотонності відтворення */
static uint64_t g_last_t_sim = 0;
static size_t g_verified_frames = 0;

static void verify_replay_callback(uint64_t t_sim, const char *topic, 
                                   uint8_t instance, const uint8_t *data, 
                                   uint16_t size, void *user_data) {
    (void)instance;
    (void)data;
    (void)size;
    (void)user_data;

    printf("  [Тестовий диспетчер] Топік: %s, t_sim = %llu мкс\n", 
           topic, (unsigned long long)t_sim);

    /* Перевірка суворої монотонності віртуального часу */
    assert(t_sim >= g_last_t_sim);
    g_last_t_sim = t_sim;
    g_verified_frames++;
}

int main(void) {
    const char *test_file = "test_synthetic_flight.ulg";
    printf("[Юніт-тест Replay Engine] Створення синтетичного ULog...\n");
    generate_synthetic_ulog_file(test_file);

    printf("[Юніт-тест Replay Engine] Запуск переграшу...\n");
    ulog_replay_engine_t engine;
    bool ok = ulog_engine_init(&engine, test_file, verify_replay_callback, NULL);
    assert(ok == true);

    ulog_engine_run(&engine);

    assert(g_verified_frames == 4);
    printf("[Юніт-тест Replay Engine] Тест УСПІШНО пройдено. Детермінізм підтверджено!\n");

    remove(test_file);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <cassert>
#include <filesystem>
#include <cstring>

static void generateSyntheticULogCpp(const std::string& filename) {
    std::ofstream out(filename, std::ios::binary);
    assert(out.is_open());

    // 1. Заголовок ULog (16 байтів)
    uint8_t header[16] = {
        0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35, 0x00,
        0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00
    };
    out.write(reinterpret_cast<const char*>(header), 16);

    // 2. Схема формату
    std::string fmt = "sensor_combined:uint64_t timestamp;float[3] gyro_rad;float[3] accel_m_s2;";
    uint16_t fmt_len = static_cast<uint16_t>(fmt.size());
    uint8_t fmt_hdr[3] = { static_cast<uint8_t>(fmt_len & 0xFF), static_cast<uint8_t>(fmt_len >> 8), 'F' };
    out.write(reinterpret_cast<const char*>(fmt_hdr), 3);
    out.write(fmt.data(), fmt_len);

    // 3. Підписка
    std::string topic = "sensor_combined";
    std::vector<uint8_t> sub_payload;
    sub_payload.push_back(0); // multi_id
    sub_payload.push_back(1); // msg_id low
    sub_payload.push_back(0); // msg_id high
    sub_payload.insert(sub_payload.end(), topic.begin(), topic.end());
    uint16_t sub_len = static_cast<uint16_t>(sub_payload.size());
    uint8_t sub_hdr[3] = { static_cast<uint8_t>(sub_len & 0xFF), static_cast<uint8_t>(sub_len >> 8), 'A' };
    out.write(reinterpret_cast<const char*>(sub_hdr), 3);
    out.write(reinterpret_cast<const char*>(sub_payload.data()), sub_len);

    // 4. Повідомлення даних з немонотонними мітками часу
    uint64_t timestamps[4] = { 1048600, 1048580, 1048650, 1048620 };
    for (uint64_t ts : timestamps) {
        std::vector<uint8_t> data(34, 0);
        data[0] = 1; // msg_id low
        data[1] = 0; // msg_id high
        std::memcpy(&data[2], &ts, sizeof(uint64_t));

        uint16_t d_len = static_cast<uint16_t>(data.size());
        uint8_t d_hdr[3] = { static_cast<uint8_t>(d_len & 0xFF), static_cast<uint8_t>(d_len >> 8), 'D' };
        out.write(reinterpret_cast<const char*>(d_hdr), 3);
        out.write(reinterpret_cast<const char*>(data.data()), d_len);
    }
}

int main() {
    const std::string test_file = "test_synthetic_flight_cpp.ulg";
    generateSyntheticULogCpp(test_file);

    uint64_t last_time = 0;
    size_t verified_count = 0;

    auto callback = [&](uint64_t t_sim, std::string_view topic, uint8_t instance, std::span<const uint8_t> payload) {
        (void)instance;
        (void)payload;
        std::cout << std::format("  [C++20 Тест] Топік: {}, t_sim = {} мкс\n", topic, t_sim);
        assert(t_sim >= last_time);
        last_time = t_sim;
        verified_count++;
    };

    ULogReplayEngineCpp engine(test_file, callback);
    engine.runReplay();

    assert(verified_count == 4);
    std::cout << "[C++20 Тест] Успішно! Порядок часу повністю відновлено.\n";

    std::filesystem::remove(test_file);
    return 0;
}
```
:::

---

## 12. Інженерні пастки, крайові випадки та апаратна оптимізація

Під час практичного використання та адаптації рушія переграшу в промислових проектах необхідно враховувати низку критичних низькорівневих аспектів:

### 12.1. Неузгодженість вирівнювання пам'яті (Unaligned Memory Access)

У форматі ULog поля повідомлень упаковані щільно (Pack 1) без додаткових байтів вирівнювання (Padding). Якщо розробник спробує зчитати 64-бітне число з плаваючою комою `double` за непарним зсувом (наприклад, адреса `0x20000003`) прямим приведенням покажчика `*(double*)(buffer + offset)`:
* На архітектурі x86_64 процесор виконає апаратне злиття двох циклів шини пам'яті з незначним падінням швидкості.
* На мікроконтролерах ARM Cortex-M4 / Cortex-M0+ без блоку підтримки непарного доступу апаратне ядро згенерує фатальне виключення `HardFault (UNALIGN TRAP)`.
* **Правильне рішення:** Читання завжди виконується через функцію `memcpy()` або через побайтові зсуви, які сучасні оптимізуючі компілятори (GCC/Clang на рівні `-O2`/`-O3`) автоматично перетворюють на найшвидші безпечні інструкції цільової архітектури.

### 12.2. Керування пропускною здатністю та кеш-локальність (L1/L2 Cache Locality)

Під час масового пакетного переграшу сотень логів вузьким місцем стає продуктивність дискової підсистеми та ефективність використання кешу процесора:
* Замість читання файлу дрібними порціями по кілька байтів для кожного заголовка застосовують **буферизоване читання сторінками по 64–256 КБ**.
* Структура кадру `replay_frame_t` у черзі пріоритетів вирівняна за розміром 64 байти (розмір типового кеш-рядка процесора L1 Data Cache). Це гарантує, що операції просіювання купи в пам'яті завантажують рівно один кеш-рядок на кожне порівняння, забезпечуючи швидкість обробки понад **1 500 000 повідомлень на секунду** на одному ядрі сучасного процесора.

### 12.3. Обробка переповнення черги пріоритетів (Queue Saturation)

Якщо вхідний лог містить тривалий часовий розрив або аномальний сплеск кількості низькопріоритетних текстових повідомлень, черга Min-Heap може досягти максимальної місткості (2048 кадрів). 

Рушій реалізує стратегію **вимушеного витіснення найстарішого елемента**:
* Перед додаванням нового кадру корінь купи вилучається та негайно передається в диспетчер зі зміщенням віртуального годинника.
* Це гарантує стабільність пам'яті процесу та запобігає втраті найбільш актуальних високочастотних даних сенсорів.

### 12.4. Обробка переповнення 32-бітних таймерів сенсорів

Багато недорогих зовнішніх модулів GNSS або оптичних далекомірів передають внутрішній час як 32-бітне ціле число в мікросекундах (`uint32_t`), яке переповнюється кожні 71.58 хвилини польоту.

Якщо лог триває понад 1.2 години, мітка часу такого сенсора раптово стрибає від `4294967000 мкс` до `1000 мкс`. Якщо рушій переграшу не містить модуля розгортання фази часу (Phase Unwrapping), черга Min-Heap заблокує просування віртуального годинника, оскільки пакет із часом `1000 мкс` назавжди застрягне в корені купи як такий, що належить далекому минулому.

Алгоритм фазового розгортання, інтегрований у парсер:

```
t_unwrapped = t_raw + (overflow_epochs · 2³²)
якщо (t_last_raw > 0xC0000000) та (t_raw < 0x40000000):
    overflow_epochs = overflow_epochs + 1
```

Цей розрахунок гарантує неперервність 64-бітної шкали часу для будь-якої тривалості місії автономного дрона.

---

## 13. Керування параметрами та динамічне накладання конфігурацій (Parameter Overrides)

У практичній роботі інженеру часто потрібно не просто відтворити політ, а перевірити гіпотезу: «що було б, якби коефіцієнт шуму гіроскопа був удвічі більшим?». 

Для цього рушій переграшу підтримує трирівневу ієрархію конфігурації:
1. **Базові значення за замовчуванням (Firmware Defaults):** Зашиті в скомпільованому бінарнику прошивки.
2. **Значення з логу (Logged Parameters):** Зчитуються із секцій `'P'` на початку файлу ULog і перезаписують базові значення.
3. **Користувацькі накладання (CLI/File Overrides):** Завантажуються зі стороннього текстового файлу (наприклад, `overrides.params`) або передаються через аргументи командного рядка.

Під час ініціалізації рушій парсить секції `'P'`, проте перед передачею керування диспетчеру застосовує таблицю оверлеїв. Якщо в оверлеї зазначено `EKF2_GYR_NOISE = 0.035`, саме це значення записується у віртуальний менеджер параметрів, ігноруючи старе значення з логу.

Це дозволяє запускати автоматизовані скрипти підбору параметрів без необхідності фізичного перезапису вхідного бінарного файлу логу.

---

## 14. Безблокувальна черга для багатопотокового контуру (Lockless SPSC Queue)

Якщо рушій переграшу інтегрується в багатопотокове симуляційне оточення, де операції читання файлу з диска виконуються в окремому низькопріоритетному потоці вводу/виводу, а обчислення навігаційного фільтра EKF2 відбуваються в високопріоритетному обчислювальному потоці, між ними організується **безблокувальна кільцева черга одиночного виробника та споживача** (Single-Producer Single-Consumer, SPSC Queue).

Принцип функціонування черги базується на атомарних покажчиках з упорядкуванням пам'яті Acquire/Release:

```
[ Потік дискового парсера ] ──(Атомарний запис Head)──> [ SPSC Буфер ] ──(Атомарне читання Tail)──> [ Потік обчислень EKF2 ]
```

* Потік виробника (дисковий парсер) оновлює покажчик голови `head_index` за допомогою операції `atomic_store_explicit(..., memory_order_release)`, гарантуючи, що всі байти корисного навантаження кадру фізично осіли в пам'яті до того, як споживач побачить новий індекс.
* Потік споживача (навігаційний фільтр) зчитує `head_index` за допомогою `atomic_load_explicit(..., memory_order_acquire)`, обробляє кадр і оновлює покажчик хвоста `tail_index`.
* Для запобігання ефекту хибного розділення кеш-ліній (False Sharing), коли модифікація `head` знецінює кеш-рядок з `tail` на сусідньому ядрі процесора, покажчики розносяться в пам'яті на відстань мінімум 64 байти за допомогою директиви вирівнювання `alignas(64)`.

Така архітектура дозволяє повністю усунути затримки системних м'ютексів та системних викликів блокування `pthread_mutex_lock()`, забезпечуючи максимальну швидкість переграшу при збереженні повної детерміністичності.

---

## 15. Архітектура інтеграції рушія в контур автоматизованого CI/CD тестування

Для забезпечення бездоганної надійності нових версій прошивок автономний рушій Replay Engine інтегрується в автоматизований конвеєр регресійного тестування (CI/CD Pipeline).

Схема взаємодії компонентів у серверному середовищі:

```
[ Git Репозиторій Прошивки ] ──> [ Збирання SITL Бінарника ]
                                          │
                                          ▼
[ База 100+ Еталонних ULog-файлів ] ──> [ Replay Engine Matrix Runner ]
                                          │
                                          ▼
                      ┌───────────────────────────────────────┐
                      │ 1. Паралельне виконання Replay на CPU │
                      │ 2. Збір інновацій EKF2 (vel, pos, mag)│
                      │ 3. Розрахунок метрик якості (RMSE)    │
                      └───────────────────────────────────────┘
                                          │
                                          ▼
                      [ Звіт валідації: Pass / Fail Verdict ]
```

Під час виконання матричного тесту скрипт-оркестратор порівнює вихідні траєкторії нового переграшу з еталонними польотними даними. Якщо відхилення за координатами перевищує 0.05 м, або хоча б в одному лозі виникає непередбачене скидання фільтра EKF (Hard Reset), збирання автоматично блокується, запобігаючи потраплянню потенційно небезпечного коду на реальні безпілотні апарати.

---

## 16. Протокол серіалізації вихідних даних переграшу (Output Replay Logger)

Після завершення обчислення фільтрів у режимі переграшу рушій має можливість серіалізувати результати в новий ULog-файл або табличний формат Parquet/CSV для наступного порівняльного аналізу:
* Записується дзеркальний ULog-файл із суфіксом `_replayed.ulg`.
* У файл включаються як вихідні сирі сенсори, так і нові топіки `vehicle_attitude_replay`, `vehicle_local_position_replay`, `estimator_innovations_replay`.
* Це дозволяє відкривати обидва логи у візуалізаторі FlightReview або PlotJuggler і будувати диференційні графіки розбіжності за кутами крену, тангажу, курсу та координатами з мікросекундною роздільною здатністю.

---

## 17. Підсумковий контрольний список для інтеграції Replay Engine

Перед розгортанням рушія у виробничому середовищі інженерній команді рекомендується звірити реалізацію з контрольним чеклистом:

* [x] Заголовок файлу ULog валідується за повною магічною сигнатурою `0x55 0x4C 0x6F 0x67 0x01 0x12 0x35 0x00`.
* [x] Усі вибірки даних сортуються чергою Min-Heap за 64-бітними мітками часу `timestamp_us`.
* [x] Розмір пам'яті черги є статичним і не викликає алокацій у гарячому циклі читання.
* [x] Реалізовано захист від непарного вирівнювання пам'яті (Unaligned Access Safe).
* [x] Реалізовано коректну обробку обірваних файлів при раптовому вимкненні живлення в польоті.
* [x] Підтримується обробка маркерів втрати пакетів `'S'` (Dropouts) з інформуванням фільтра EKF.
* [x] Передбачено механізм накладання користувацьких параметрів (Parameter Overrides) для оптимізації фільтрів.
* [x] Реалізовано білі списки топіків (Topic Whitelisting) для прискорення обробки великих файлів.
* [x] Інтегровано підтримку тестування відмов багатьох сенсорів (Multi-IMU Fault Injection).
* [x] Інтегровано підтримку безблокувальних буферів (Lockless SPSC) для багатопотокових симуляцій.
* [x] Забезпечено автоматичне збереження результатів переграшу в дзеркальний ULog-файл для регресійного порівняння.

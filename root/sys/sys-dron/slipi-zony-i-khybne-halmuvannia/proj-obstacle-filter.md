# ⚙️ Фільтр фантомних перешкод та компенсатор сліпих зон

У контурі автономного польоту безпілотного апарата бортовий комп'ютер (Companion Computer під керуванням Linux/ROS 2 або RTOS) бере на себе задачі просторового картографування та планування безпечних траєкторій. Головним джерелом інформації про геометрію навколишнього середовища виступають просторові сенсори глибини: твердотілі лідари (Solid-State LiDAR), оптичні матриці Time-of-Flight (ToF) та активні стереокамери. Ці сенсори генерують масивні потоки тривимірних точок (від 20 000 до 200 000 точок на секунду з частотою 20–50 Гц).

Пряме передавання сирих точок у воксельну карту або локальний планувальник руху (DWA, TEB, EGO-Planner) призводить до критичних збоїв:
1. **Фантомні стіни та пилові кластери**: поодинокі сонячні відблиски, краплі дощу та пил, піднятий гвинтовим потоком повітря, утворюють локальні згустки точок на відстані 1–3 метри перед дроном, що провокує безпідставне аварійне гальмування з перевантаженнями до `2g`.
2. **Сліпі зони при маневруванні**: при нахилі корпусу на кут тангажу `25°` вертикальне поле зору зміщується вниз, повністю затінюючи верхній сектор простору прямо по курсу польоту.
3. **Обчислювальний дефіцит**: класичні алгоритми статистичної фільтрації на базі k-d дерев вимагають `O(N · log N)` або `O(N²)` операцій, що перевантажує процесори вбудованого класу (ARM Cortex-A53/A72) і викликає зрив часового детермінізму контуру керування.

Нижче наведено повну інженерну реалізацію високоефективного детермінованого модуля фільтрації та динамічної оцінки безпеки, оптимізованого для польотних комп'ютерів.

```
                  ┌─────────────────────────────────────────┐
                  │        Сирий потік точок (Raw)          │
                  │         20–50 Гц (LiDAR / ToF)          │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    1. Трансформація координат (Ext)     │
                  │        Sensor -> Body -> World ENU      │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    2. Швидкий SOR-фільтр (Spatial Hash) │
                  │         Відсікання розрідженого шуму    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    3. Воксельна персистентність у часі  │
                  │         Накопичення хітів / Згасання    │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │    4. Компенсатор сліпих зон та безпека │
                  │         Коридор D_stop / Ліміт швидкості│
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │       Вихід до планувальника руху       │
                  │    Очищена карта + Обмеження швидкості  │
                  └─────────────────────────────────────────┘
```

## Архітектура часової синхронізації та апаратні інтерфейси

Один із найпідступніших факторів, що призводить до появи фантомних перешкод у контурі автономії — це **часова розсинхронізація** (Hardware Timestamp Jitter) між вимірювальним ядром далекоміра та інерційною навігаційною системою польотного контролера.

Коли дрон рухається з лінійною швидкістю `10 м/с` та одночасно обертається по курсу зі швидкістю `60°/с`, часова затримка між оптичним кадрируванням лідара та оцінкою орієнтації `q(t)` у `20 мс` породжує лінійне зміщення точок на `20 см` і кутове спотворення на `1.2°`. На відстані 10 метрів це призводить до зміщення стін на `21 см`, що змушує алгоритм персистентності фіксувати уявне розширення перешкоди.

Для досягнення субмілісекундної точності на борту застосовуються три взаємодоповнюючі рівні синхронізації:

```
 ┌──────────────────────┐         PPS (1 Гц Pulse-Per-Second)        ┌──────────────────────┐
 │   GNSS-приймач       ├───────────────────────────────────────────►│  Лідар (Livox / Ouster)
 │ (Абсолютний час UTC) │                                            │   Внутрішній таймер  │
 └──────────┬───────────┘                                            └──────────────────────┘
            │                                                                   ▲
            │ UART (NMEA ZDA / GPRMC)                                           │ PTP / gPTP
            ▼                                                                   │ (IEEE 1588)
 ┌──────────────────────┐        Ethernet / UART (MAVLink TIMESYNC)  ┌──────────┴───────────┐
 │ Польотний контролер  ├───────────────────────────────────────────►│  Бортовий комп'ютер   │
 │ (FCU STM32 / EKF2)   │                                            │ (Companion Computer) │
 └──────────────────────┘                                            └──────────────────────┘
```

1. **Апаратний імпульс PPS (Pulse-Per-Second)**:
   GNSS-модуль генерує фізичний прямокутний імпульс на початку кожної секунди UTC з точністю `±20 нс`. Цей імпульс апаратно скидає внутрішній лічильник наносекунд у процесорі лідара та на таймері захоплення мікроконтролера польотного контролера.
2. **Протокол PTP (Precision Time Protocol, IEEE 1588-2008 / 802.1AS)**:
   При використанні Ethernet-підключення між лідаром та бортовим комп'ютером мережеві карти виконують апаратне штампування часу пакетів (Hardware Timestamping на рівні PHY-трансівера), що усуває затримки стека ОС Linux та гарантує синхронізацію годинників із точністю краще `1 мкс`.
3. **MAVLink TIMESYNC Protocol**:
   Для обміну станом між FCU та Companion по послідовній шині UART використовується циклічний протокол вимірювання кругової затримки (Round-Trip Time, RTT). Бортовий комп'ютер безперервно коригує зміщення власного монотонного таймера `CLOCK_MONOTONIC` відносно мікросекундного часу `hrt_absolute_time()` автопілота.

## Математична модель та архітектура обробки

Модуль обробки функціонує як детермінований конвеєр із фіксованим бюджетом пам'яті, що виключає динамічні алокації (`malloc` / `new`) під час польоту.

### 1. Калібрувальна трансформація та інтерполяція одометрії

Кожна точка `p_S = [x_S, y_S, z_S]`, зафіксована сенсором у момент часу `t_scan`, повинна бути переведена у світову систему відліку ENU (East-North-Up). Сенсор має власну оптичну систему координат (наприклад, вісь `Z` спрямована вперед вздовж оптичної осі, `X` — праворуч, `Y` — донизу), яка відрізняється від стандартизованої тілофіксованої системи координат дрона FRD (Forward-Right-Down) або FLU (Forward-Left-Up).

Трансформація виконується через статичну матрицю калібрування `T_BS = [R_BS | t_BS]` та миттєвий стан навігації апарата:

```
p_W = R(q_WB(t)) · (R_BS · p_S + t_BS) + p_WB(t)
```

де `q_WB(t)` — кватерніон просторової орієнтації, а `p_WB(t)` — просторові координати дрона за оцінкою фільтра EKF2. 

Якщо частота оновлення далекоміра становить 20 Гц (період 50 мс), а одометрія надходить на частоті 100 Гц (період 10 мс), точний просторовий стан на момент зчитування `t_scan` обчислюється через сферичну лінійну інтерполяцію кватерніона (SLERP):

```
q(t) = (sin((1 - u) · Ω) ÷ sin(Ω)) · q_k + (sin(u · Ω) ÷ sin(Ω)) · q_{k+1}
u = (t_scan - t_k) ÷ (t_{k+1} - t_k)
```

де `cos(Ω) = q_k · q_{k+1}`. Це виключає розмиття контурів об'єктів під час швидкого кутового маневрування.

### 2. Алгоритм просторового хешування (Spatial Hash Grid)

Замість побудови складних динамічних структур даних (ієрархічних k-d дерев або октадерев), простір квантується на регулярну тривимірну сітку з розміром комірки `r_cell = 0.40 м`. 

Індекси комірки розраховуються за формулою:

```
i_x = floor(x_W ÷ r_cell)
i_y = floor(y_W ÷ r_cell)
i_z = floor(z_W ÷ r_cell)
```

Хеш-функція перетворює тривимірний кортеж `(i_x, i_y, i_z)` на індекс комірки у фіксованій таблиці розміром `M = 4099` (просте число):

```
Hash(i_x, i_y, i_z) = ((i_x · 73856093) XOR (i_y · 19349663) XOR (i_z · 83492791)) MOD M
```

Для кожної точки пошук `k` найближчих сусідів виконується суто в межах поточної та 26 сусідніх комірок сітки. Це гарантує лінійну обчислювальну складність `O(N)` та чудову просторову локальність даних у кеш-пам'яті процесора L1/L2.

#### Числовий приклад роботи SOR-фільтра

Розглянемо хмару точок, де на плоскій вертикальній стіні на відстані 5.0 м зафіксовано групу з 8 точок із взаємною відстанню `0.15 м`, а на відстані 1.8 м у повітрі висить 2 ізольовані шумові точки від сонячного відблиску.

1. Для точок стіни середня дистанція до `k=4` сусідів становить:
   ```
   d_wall = (0.15 + 0.15 + 0.21 + 0.21) ÷ 4   [середня відстань між сусідніми точками поверхні]
          = 0.18 м                             [підсумок для щільного кластера стіни]
   ```
2. Для ізольованих шумових точок найближчі сусіди розташовані на стіні за 3.2 м, тому:
   ```
   d_noise = (3.20 + 3.21 + 3.22 + 3.23) ÷ 4   [середня відстань від шуму до найближчих об'єктів]
           = 3.215 м                            [підсумок для ізольованого викиду]
   ```
3. По всій вибірці з 10 точок середнє арифметичне становить:
   ```
   μ = (8 · 0.18 + 2 · 3.215) ÷ 10   [зважене середнє для всієї сукупності]
     = 0.787 м                       [глобальне математичне сподівання]
   ```
4. Стандартне відхилення:
   ```
   σ = sqrt((8 · (0.18 - 0.787)² + 2 · (3.215 - 0.787)²) ÷ 10)   [середньоквадратичне відхилення вибірки]
     = 1.211 м                                                     [дисперсія просторової щільності]
   ```
5. При виборі коефіцієнта `α = 1.2` поріг відсікання становить:
   ```
   Threshold = μ + α · σ            [розрахунок статистичної межі відсікання]
             = 0.787 + 1.2 · 1.211   [підстановка коефіцієнта селективності 1.2]
             = 2.240 м               [гранична відстань для збереження точки]
   ```

Оскільки для точок стіни `d_wall = 0.18 м ≤ 2.24 м`, вони повністю зберігаються. Для шумових точок `d_noise = 3.215 м > 2.24 м`, тому вони миттєво відкидаються на першому ж етапі.

### 3. Просторово-часова персистентність у циклічній воксельній сітці

Відфільтровані точки проектуються у глобальну тривимірну воксельну сітку персистентності з розміром ребра `s_voxel = 0.20 м`. 

Кожна комірка зберігає безперервну вагу достовірності `w` в діапазоні від 0 до `w_max`. На кожному такті конвеєра:
- Усі активні комірки втрачають вагу за експоненційним або лінійним законом згасання:
  ```
  w(t + Δt) = max(0, w(t) - λ_decay · Δt)
  ```
- При надходженні нової точки у воксель його вага зростає:
  ```
  w(t + Δt) = min(w_max, w(t) + Δw_hit)
  ```
- Воксель вважається підтвердженою фізичною перешкодою лише за умови `w ≥ T_occupied` (зазвичай `T_occupied = 3.0`).

Час придушення короткочасного шуму (False Positive Suppression Time) визначається відношенням порогу до частоти сенсора:

```
T_suppress = T_occupied ÷ f_sensor
```

При частоті сенсора 30 Гц поодинокий спалах шуму тривалістю до 66 мс (2 кадри) ніколи не досягне порогу `T_occupied = 3` і буде повністю проігнорований планувальником.

### 4. Компенсація сліпих зон та розрахунок коридору гальмування

Модуль оцінює кут тангажу дрона `θ` та вертикальне поле зору `VFOV`. Кут верхнього просвіту огляду розраховується як:

```
α_clearance = (VFOV ÷ 2) + θ
```

Якщо `α_clearance < 0.05 рад` (близько `3°`), дрон втрачає огляд верхнього простору через сильний нахил уперед на високій швидкості. Модуль формує динамічне обмеження швидкості `v_safe`, яке передається локальному планувальнику.

Одночасно вздовж поточного вектору лінійної швидкості `v = [v_x, v_y, v_z]` будується захисний циліндр гальмування. Його довжина `D_stop` визначається формулою:

```
D_stop = (||v||² ÷ (2 · a_max_brake)) + ||v|| · (τ_sensor_latency + τ_fcu_lag) + d_margin
```

де `τ_sensor_latency ≈ 0.05 с` (затримка формування кадру), `τ_fcu_lag ≈ 0.05 с` (затримка відпрацювання моменту автопілотом), а `d_margin = 1.2 м` — гарантований запас зупинки.

Якщо всередині циліндра радіусом `R_corridor = 1.1 м` виявляється хоча б один персистентний воксель, модуль активує сигнал тривоги гальмування.

### 5. Очищення вільного простору методом трасування променів (Ray-Casting Carving)

Окрім накопичення ваги в точках безпосереднього зіткнення, повноцінний фільтр персистентності повинен активно очищати простір між сенсором і виявленою перешкодою. Якщо людина або інший дрон перетнули поле зору і вийшли з нього, звичайне пасивне згасання вокселів триватиме кілька секунд.

Для прискореного видалення застарілих слідів динамічних об'єктів застосовується модифікований 3D-алгоритм Брезенхема (Ray-Casting):
- Від оптичного центру сенсора `p_sensor` до кінцевої точки відбиття `p_hit` проводиться цифровий промінь;
- Усі проміжні вокселі на шляху променя гарантовано є порожніми в момент зняття кадру, тому їхня вага миттєво зменшується на штрафний коефіцієнт:
  ```
  w_free = max(0, w_current - Δw_free_carve)
  ```
  де `Δw_free_carve = 0.5` (швидке очищення вільного простору);
- Кінцевий воксель `p_hit` отримує позитивний приріст `+1.0`.

Таке поєднання дозволяє розчищати шлейфи рухомих об'єктів за 1–2 цикли сканування, запобігаючи «залипанню» фантомних коридорів у воксельній карті.

### 6. Вирівнювання пам'яті та оптимізація кеш-ліній (Cache Line Alignment)

На вбудованих процесорах архітектури ARMv8 (Cortex-A53 / A72 / A78) розмір кеш-лінії L1 Data Cache становить 64 байти. Якщо структури точок `Point3D` (16 байтів: три `float` по 4 байти + `intensity` 4 байти) розміщуються у неперервному масиві, одна 64-байтна транзакція шини завантажує рівно чотири точки одночасно.

Для забезпечення максимальної швидкодії векторних інструкцій SIMD:
1. Буфери хмар точок вирівнюються за 16-байтною або 64-байтною межею за допомогою директив `alignas(16)` у C++ або функції `posix_memalign()` у C;
2. У циклі обробки застосовується апаратне попереднє вибирання даних у кеш (Hardware Prefetching) через інструкцію `__builtin_prefetch(&points[i + 8], 0, 3)`;
3. Структура `HashCell` оптимізована за розміром, щоб кожен запис хеш-таблиці вкладався у ціле число кеш-ліній, усуваючи паразитні промахи кешу (False Sharing / Cache Misses).

### 7. Багатопотокова архітектура та подвійна буферизація (Lock-Free Pipeline)

Для забезпечення стабільної частоти обробки 50 Гц без затримок введення-виведення конвеєр розділений на три паралельні потоки виконання:

```
 ┌────────────────────────┐    Ping-Pong Buffer #1    ┌────────────────────────┐
 │ Потік захоплення (Ingest)├─────────────────────────►│  Потік фільтрації (SOR) │
 │ Кадри далекоміра 50 Гц  │                           │  Воксельна сітка хітів │
 └────────────────────────┘                           └───────────┬────────────┘
                                                                  │ Ping-Pong #2
                                                                  ▼
                                                      ┌────────────────────────┐
                                                      │ Потік публікації (Pub) │
                                                      │ uORB / MAVLink / ROS 2 │
                                                      └────────────────────────┘
```

1. **Потік прийому даних (Ingestion Thread)**:
   Приймає пакети з шини Ethernet або драйвера V4L2/USB3, виконує миттєве копіювання сирих байтів у вільний слот подвійного буфера (Ping-Pong Buffer) та прив'язує мікросекундну мітку часу. Потік працює з найвищим пріоритетом реального часу (`SCHED_FIFO`, пріоритет 80).
2. **Потік обробки та фільтрації (Processing Worker Thread)**:
   Зчитує заповнений буфер, виконує трансформацію координат, статистичний аналіз SOR через просторовий хеш та оновлює ваги вокселів. Використовує векторні інструкції SIMD і не здійснює системних викликів введення-виведення.
3. **Потік безпеки та публікації (Safety & Publishing Thread)**:
   Оцінює зайнятість коридору гальмування `D_stop`, формує повідомлення `obstacle_distance` і публікує його в шину uORB автопілота з детермінованим періодом 20 мс (50 Гц).

Обмін даними між потоками організовано через атомарні покажчики `std::atomic<BufferSlot*>` у C++ або `stdatomic.h` у C без використання важких м'ютексів операційної системи, що повністю усуває проблему інверсії пріоритетів (Priority Inversion).

## Повний вихідний код конвеєра фільтрації

Нижче наведено повну реалізацію ядра фільтра на мовах C та C++.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#include <stdint.h>

#define MAX_RAW_POINTS      8192
#define MAX_FILTERED_POINTS 4096
#define HASH_TABLE_SIZE     4099    /* Просте число для хешування */
#define MAX_VOXEL_CELLS     16384
#define VOXEL_SIZE          0.20f   /* 20 см ребро вокселя */
#define CELL_NEIGHBORS_MAX  64

/* Структура просторової точки */
typedef struct {
    float x;
    float y;
    float z;
    float intensity;
} Point3D;

/* Кватерніон орієнтації [w, x, y, z] */
typedef struct {
    float w, x, y, z;
} Quaternion;

/* Стан навігації та кінематики апарата */
typedef struct {
    float x, y, z;          /* Позиція в ENU (м) */
    float vx, vy, vz;       /* Лінійна швидкість (м/с) */
    Quaternion q;           /* Орієнтація у просторі */
    float roll, pitch, yaw; /* Кути Ейлера (рад) */
} VehicleState;

/* Елемент просторової хеш-таблиці для швидкого SOR */
typedef struct {
    int32_t point_indices[CELL_NEIGHBORS_MAX];
    uint16_t count;
    int32_t key_x, key_y, key_z;
    bool active;
} HashCell;

/* Осередок сітки часової персистентності */
typedef struct {
    int32_t vx, vy, vz;
    float weight;
    float last_time_sec;
    bool occupied;
} VoxelEntry;

/* Повний конвеєр фільтрації */
typedef struct {
    HashCell hash_table[HASH_TABLE_SIZE];
    VoxelEntry voxel_grid[MAX_VOXEL_CELLS];
    size_t voxel_count;

    /* Параметри SOR */
    int k_neighbors;
    float alpha_factor;
    float hash_cell_size;

    /* Параметри персистентності */
    float decay_rate;
    float max_weight;
    float occ_threshold;

    /* Параметри безпеки */
    float max_brake_accel;
    float sensor_vfov_rad;
    float safe_margin_m;
} ObstacleFilterPipeline;

/* Ініціалізація структури конвеєра */
void filter_init(ObstacleFilterPipeline* pipe) {
    memset(pipe, 0, sizeof(ObstacleFilterPipeline));
    pipe->k_neighbors = 8;
    pipe->alpha_factor = 1.5f;
    pipe->hash_cell_size = 0.40f;

    pipe->decay_rate = 2.5f;        /* Ваги на секунду */
    pipe->max_weight = 10.0f;
    pipe->occ_threshold = 3.0f;

    pipe->max_brake_accel = 4.0f;   /* м/с^2 */
    pipe->sensor_vfov_rad = 58.0f * (float)M_PI / 180.0f;
    pipe->safe_margin_m = 1.2f;
}

/* Обчислення хеш-ключа */
static inline uint32_t compute_hash(int32_t ix, int32_t iy, int32_t iz) {
    uint32_t h = (uint32_t)(ix * 73856093 ^ iy * 19349663 ^ iz * 83492791);
    return h % HASH_TABLE_SIZE;
}

/* Обертання вектора кватерніоном */
static inline Point3D rotate_vector_by_quat(Point3D v, Quaternion q) {
    float tx = 2.0f * (q.y * v.z - q.z * v.y);
    float ty = 2.0f * (q.z * v.x - q.x * v.z);
    float tz = 2.0f * (q.x * v.y - q.y * v.x);

    Point3D out;
    out.x = v.x + q.w * tx + (q.y * tz - q.z * ty);
    out.y = v.y + q.w * ty + (q.z * tx - q.x * tz);
    out.z = v.z + q.w * tz + (q.x * ty - q.y * tx);
    out.intensity = v.intensity;
    return out;
}

/* 1. Трансформація хмари точок у світову систему координат */
size_t filter_transform_to_world(const Point3D* in_pts, size_t n_pts, 
                                 const VehicleState* state, 
                                 Point3D* out_pts) {
    size_t valid = 0;
    for (size_t i = 0; i < n_pts && valid < MAX_RAW_POINTS; ++i) {
        float r_sq = in_pts[i].x * in_pts[i].x + in_pts[i].y * in_pts[i].y + in_pts[i].z * in_pts[i].z;
        if (r_sq < 0.09f || r_sq > 400.0f) continue; /* Відкидаємо пропелери та нескінченність */

        Point3D rotated = rotate_vector_by_quat(in_pts[i], state->q);
        out_pts[valid].x = rotated.x + state->x;
        out_pts[valid].y = rotated.y + state->y;
        out_pts[valid].z = rotated.z + state->z;
        out_pts[valid].intensity = in_pts[i].intensity;
        valid++;
    }
    return valid;
}

/* 2. Статистичний фільтр викидів (Spatial Hash SOR) */
size_t filter_statistical_outliers(ObstacleFilterPipeline* pipe, 
                                   const Point3D* in_pts, size_t n_pts, 
                                   Point3D* out_pts) {
    if (n_pts < (size_t)pipe->k_neighbors || n_pts == 0) return 0;

    memset(pipe->hash_table, 0, sizeof(pipe->hash_table));
    float inv_cell = 1.0f / pipe->hash_cell_size;

    /* Заповнення просторового хешу */
    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ix = (int32_t)floorf(in_pts[i].x * inv_cell);
        int32_t iy = (int32_t)floorf(in_pts[i].y * inv_cell);
        int32_t iz = (int32_t)floorf(in_pts[i].z * inv_cell);

        uint32_t slot = compute_hash(ix, iy, iz);
        for (size_t probe = 0; probe < 8; ++probe) {
            uint32_t s = (slot + probe) % HASH_TABLE_SIZE;
            if (!pipe->hash_table[s].active) {
                pipe->hash_table[s].active = true;
                pipe->hash_table[s].key_x = ix;
                pipe->hash_table[s].key_y = iy;
                pipe->hash_table[s].key_z = iz;
                pipe->hash_table[s].count = 0;
            }
            if (pipe->hash_table[s].key_x == ix && 
                pipe->hash_table[s].key_y == iy && 
                pipe->hash_table[s].key_z == iz) {
                if (pipe->hash_table[s].count < CELL_NEIGHBORS_MAX) {
                    pipe->hash_table[s].point_indices[pipe->hash_table[s].count++] = (int32_t)i;
                }
                break;
            }
        }
    }

    /* Пошук k найближчих сусідів та розрахунок середніх відстаней */
    float mean_distances[MAX_RAW_POINTS];
    double sum_mean = 0.0;

    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ix = (int32_t)floorf(in_pts[i].x * inv_cell);
        int32_t iy = (int32_t)floorf(in_pts[i].y * inv_cell);
        int32_t iz = (int32_t)floorf(in_pts[i].z * inv_cell);

        float dists[CELL_NEIGHBORS_MAX * 4];
        size_t n_found = 0;

        for (int32_t dx = -1; dx <= 1; ++dx) {
            for (int32_t dy = -1; dy <= 1; ++dy) {
                for (int32_t dz = -1; dz <= 1; ++dz) {
                    uint32_t slot = compute_hash(ix + dx, iy + dy, iz + dz);
                    for (size_t probe = 0; probe < 8; ++probe) {
                        uint32_t s = (slot + probe) % HASH_TABLE_SIZE;
                        if (!pipe->hash_table[s].active) break;
                        if (pipe->hash_table[s].key_x == (ix + dx) && 
                            pipe->hash_table[s].key_y == (iy + dy) && 
                            pipe->hash_table[s].key_z == (iz + dz)) {
                            for (uint16_t c = 0; c < pipe->hash_table[s].count; ++c) {
                                int32_t idx = pipe->hash_table[s].point_indices[c];
                                if ((size_t)idx == i) continue;
                                float ddx = in_pts[i].x - in_pts[idx].x;
                                float ddy = in_pts[i].y - in_pts[idx].y;
                                float ddz = in_pts[i].z - in_pts[idx].z;
                                dists[n_found++] = sqrtf(ddx * ddx + ddy * ddy + ddz * ddz);
                                if (n_found >= (CELL_NEIGHBORS_MAX * 4 - 1)) goto sort_k;
                            }
                            break;
                        }
                    }
                }
            }
        }

    sort_k:
        if (n_found < (size_t)pipe->k_neighbors) {
            mean_distances[i] = 999.0f;
            continue;
        }

        /* Знаходження k найменших відстаней */
        float sum_k = 0.0f;
        for (int k = 0; k < pipe->k_neighbors; ++k) {
            size_t min_idx = (size_t)k;
            for (size_t m = (size_t)k + 1; m < n_found; ++m) {
                if (dists[m] < dists[min_idx]) min_idx = m;
            }
            float tmp = dists[k];
            dists[k] = dists[min_idx];
            dists[min_idx] = tmp;
            sum_k += dists[k];
        }
        mean_distances[i] = sum_k / (float)pipe->k_neighbors;
        sum_mean += mean_distances[i];
    }

    double global_mu = sum_mean / (double)n_pts;
    double sum_sq_diff = 0.0;
    for (size_t i = 0; i < n_pts; ++i) {
        if (mean_distances[i] < 900.0f) {
            double diff = mean_distances[i] - global_mu;
            sum_sq_diff += diff * diff;
        }
    }
    double global_sigma = sqrt(sum_sq_diff / (double)n_pts);
    float threshold = (float)(global_mu + (double)pipe->alpha_factor * global_sigma);

    /* Фільтрація точок за порогом */
    size_t out_count = 0;
    for (size_t i = 0; i < n_pts; ++i) {
        if (mean_distances[i] <= threshold && out_count < MAX_FILTERED_POINTS) {
            out_pts[out_count++] = in_pts[i];
        }
    }
    return out_count;
}

/* 3. Просторово-часова персистентність */
void filter_update_persistence(ObstacleFilterPipeline* pipe, 
                               const Point3D* pts, size_t n_pts, 
                               float time_sec) {
    for (size_t i = 0; i < pipe->voxel_count; ++i) {
        float dt = time_sec - pipe->voxel_grid[i].last_time_sec;
        if (dt > 0.02f) {
            pipe->voxel_grid[i].weight -= pipe->decay_rate * dt;
            pipe->voxel_grid[i].last_time_sec = time_sec;
            if (pipe->voxel_grid[i].weight <= 0.0f) {
                pipe->voxel_grid[i] = pipe->voxel_grid[pipe->voxel_count - 1];
                pipe->voxel_count--;
                i--;
                continue;
            }
        }
        pipe->voxel_grid[i].occupied = (pipe->voxel_grid[i].weight >= pipe->occ_threshold);
    }

    float inv_vox = 1.0f / VOXEL_SIZE;
    for (size_t i = 0; i < n_pts; ++i) {
        int32_t ivx = (int32_t)floorf(pts[i].x * inv_vox);
        int32_t ivy = (int32_t)floorf(pts[i].y * inv_vox);
        int32_t ivz = (int32_t)floorf(pts[i].z * inv_vox);

        bool found = false;
        for (size_t j = 0; j < pipe->voxel_count; ++j) {
            if (pipe->voxel_grid[j].vx == ivx && 
                pipe->voxel_grid[j].vy == ivy && 
                pipe->voxel_grid[j].vz == ivz) {
                pipe->voxel_grid[j].weight += 1.0f;
                if (pipe->voxel_grid[j].weight > pipe->max_weight) {
                    pipe->voxel_grid[j].weight = pipe->max_weight;
                }
                pipe->voxel_grid[j].last_time_sec = time_sec;
                pipe->voxel_grid[j].occupied = (pipe->voxel_grid[j].weight >= pipe->occ_threshold);
                found = true;
                break;
            }
        }

        if (!found && pipe->voxel_count < MAX_VOXEL_CELLS) {
            VoxelEntry* v = &pipe->voxel_grid[pipe->voxel_count++];
            v->vx = ivx;
            v->vy = ivy;
            v->vz = ivz;
            v->weight = 1.0f;
            v->last_time_sec = time_sec;
            v->occupied = false;
        }
    }
}

/* 4. Компенсація сліпих зон та перевірка коридору безпеки */
bool filter_evaluate_safety(const ObstacleFilterPipeline* pipe, 
                            const VehicleState* state, 
                            float* out_max_safe_speed) {
    float speed = sqrtf(state->vx * state->vx + state->vy * state->vy + state->vz * state->vz);
    
    /* Оцінка кута нахилу та обмеження швидкості */
    float pitch_angle = state->pitch;
    float half_vfov = pipe->sensor_vfov_rad * 0.5f;
    float upper_clearance = half_vfov + pitch_angle;

    float max_speed_fov = 15.0f;
    if (upper_clearance < 0.05f) {
        max_speed_fov = 3.0f;
    } else if (upper_clearance < 0.20f) {
        max_speed_fov = 3.0f + (upper_clearance / 0.20f) * 7.0f;
    }
    *out_max_safe_speed = max_speed_fov;

    if (speed < 0.15f) return false;

    /* Розрахунок коридору гальмування */
    float stop_dist = (speed * speed) / (2.0f * pipe->max_brake_accel) + speed * 0.15f + pipe->safe_margin_m;
    float dir_x = state->vx / speed;
    float dir_y = state->vy / speed;
    float dir_z = state->vz / speed;

    for (size_t i = 0; i < pipe->voxel_count; ++i) {
        if (!pipe->voxel_grid[i].occupied) continue;

        float wx = ((float)pipe->voxel_grid[i].vx + 0.5f) * VOXEL_SIZE;
        float wy = ((float)pipe->voxel_grid[i].vy + 0.5f) * VOXEL_SIZE;
        float wz = ((float)pipe->voxel_grid[i].vz + 0.5f) * VOXEL_SIZE;

        float rx = wx - state->x;
        float ry = wy - state->y;
        float rz = wz - state->z;

        float proj = rx * dir_x + ry * dir_y + rz * dir_z;
        if (proj > 0.0f && proj <= stop_dist) {
            float px = rx - proj * dir_x;
            float py = ry - proj * dir_y;
            float pz = rz - proj * dir_z;
            float lateral_r = sqrtf(px * px + py * py + pz * pz);

            if (lateral_r < 1.1f) {
                return true;
            }
        }
    }
    return false;
}
```

@tab cpp
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <span>
#include <unordered_map>
#include <optional>
#include <chrono>

struct Point3D {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float intensity{0.0f};
};

struct Quaternion {
    float w{1.0f}, x{0.0f}, y{0.0f}, z{0.0f};

    [[nodiscard]] Point3D rotate(const Point3D& v) const noexcept {
        const float tx = 2.0f * (y * v.z - z * v.y);
        const float ty = 2.0f * (z * v.x - x * v.z);
        const float tz = 2.0f * (x * v.y - y * v.x);

        return Point3D{
            v.x + w * tx + (y * tz - z * ty),
            v.y + w * ty + (z * tx - x * tz),
            v.z + w * tz + (x * ty - y * tx),
            v.intensity
        };
    }
};

struct VehicleKinematics {
    float x{0.0f}, y{0.0f}, z{0.0f};
    float vx{0.0f}, vy{0.0f}, vz{0.0f};
    Quaternion orientation{};
    float pitch_rad{0.0f};

    [[nodiscard]] float speed() const noexcept {
        return std::sqrt(vx * vx + vy * vy + vz * vz);
    }
};

struct VoxelCoord {
    int32_t x{0}, y{0}, z{0};

    bool operator==(const VoxelCoord& o) const noexcept {
        return x == o.x && y == o.y && z == o.z;
    }
};

struct VoxelCoordHash {
    std::size_t operator()(const VoxelCoord& v) const noexcept {
        return static_cast<std::size_t>(v.x * 73856093 ^ v.y * 19349663 ^ v.z * 83492791);
    }
};

struct VoxelData {
    float weight{0.0f};
    float last_time_sec{0.0f};
    bool is_occupied{false};
};

class ObstacleFilterPipeline {
public:
    struct Config {
        int k_neighbors{8};
        float alpha_factor{1.5f};
        float hash_cell_size{0.40f};
        float voxel_size{0.20f};
        float decay_rate{2.5f};
        float max_weight{10.0f};
        float occ_threshold{3.0f};
        float max_brake_accel{4.0f};
        float sensor_vfov_rad{58.0f * 0.0174532925f};
        float safety_margin_m{1.2f};
    };

    explicit ObstacleFilterPipeline(Config cfg = {}) : cfg_(cfg) {}

    struct ProcessResult {
        std::vector<Point3D> filtered_points;
        float max_safe_speed{15.0f};
        bool braking_threat{false};
    };

    [[nodiscard]] ProcessResult process(std::span<const Point3D> raw_points, 
                                        const VehicleKinematics& kin, 
                                        float current_time_sec) {
        ProcessResult result;

        // 1. Трансформація у світову систему координат ENU
        std::vector<Point3D> world_points;
        world_points.reserve(raw_points.size());
        for (const auto& pt : raw_points) {
            const float r_sq = pt.x * pt.x + pt.y * pt.y + pt.z * pt.z;
            if (r_sq < 0.09f || r_sq > 400.0f) continue;

            Point3D rotated = kin.orientation.rotate(pt);
            world_points.push_back(Point3D{
                rotated.x + kin.x,
                rotated.y + kin.y,
                rotated.z + kin.z,
                pt.intensity
            });
        }

        // 2. Статистичний фільтр викидів (Spatial Hash SOR)
        result.filtered_points = remove_statistical_outliers(world_points);

        // 3. Оновлення воксельної сітки часової персистентності
        update_persistence(result.filtered_points, current_time_sec);

        // 4. Оцінка безпеки та компенсація сліпих зон
        result.max_safe_speed = calculate_safe_speed(kin);
        result.braking_threat = evaluate_braking_threat(kin);

        return result;
    }

private:
    Config cfg_;
    std::unordered_map<VoxelCoord, VoxelData, VoxelCoordHash> voxel_map_;

    [[nodiscard]] std::vector<Point3D> remove_statistical_outliers(std::span<const Point3D> points) const {
        if (points.size() < static_cast<size_t>(cfg_.k_neighbors)) return {};

        std::unordered_map<VoxelCoord, std::vector<size_t>, VoxelCoordHash> spatial_hash;
        const float inv_cell = 1.0f / cfg_.hash_cell_size;

        for (size_t i = 0; i < points.size(); ++i) {
            VoxelCoord key{
                static_cast<int32_t>(std::floor(points[i].x * inv_cell)),
                static_cast<int32_t>(std::floor(points[i].y * inv_cell)),
                static_cast<int32_t>(std::floor(points[i].z * inv_cell))
            };
            spatial_hash[key].push_back(i);
        }

        std::vector<float> mean_distances(points.size(), 999.0f);
        double sum_mean = 0.0;

        for (size_t i = 0; i < points.size(); ++i) {
            const int32_t ix = static_cast<int32_t>(std::floor(points[i].x * inv_cell));
            const int32_t iy = static_cast<int32_t>(std::floor(points[i].y * inv_cell));
            const int32_t iz = static_cast<int32_t>(std::floor(points[i].z * inv_cell));

            std::vector<float> dists;
            dists.reserve(64);

            for (int32_t dx = -1; dx <= 1; ++dx) {
                for (int32_t dy = -1; dy <= 1; ++dy) {
                    for (int32_t dz = -1; dz <= 1; ++dz) {
                        auto it = spatial_hash.find(VoxelCoord{ix + dx, iy + dy, iz + dz});
                        if (it == spatial_hash.end()) continue;

                        for (size_t idx : it->second) {
                            if (idx == i) continue;
                            const float ddx = points[i].x - points[idx].x;
                            const float ddy = points[i].y - points[idx].y;
                            const float ddz = points[i].z - points[idx].z;
                            dists.push_back(std::sqrt(ddx * ddx + ddy * ddy + ddz * ddz));
                        }
                    }
                }
            }

            if (dists.size() < static_cast<size_t>(cfg_.k_neighbors)) continue;

            std::nth_element(dists.begin(), dists.begin() + cfg_.k_neighbors, dists.end());
            float sum_k = 0.0f;
            for (int k = 0; k < cfg_.k_neighbors; ++k) sum_k += dists[k];

            mean_distances[i] = sum_k / static_cast<float>(cfg_.k_neighbors);
            sum_mean += mean_distances[i];
        }

        const double mu = sum_mean / static_cast<double>(points.size());
        double sum_sq = 0.0;
        for (float d : mean_distances) {
            if (d < 900.0f) sum_sq += (d - mu) * (d - mu);
        }
        const double sigma = std::sqrt(sum_sq / static_cast<double>(points.size()));
        const float threshold = static_cast<float>(mu + cfg_.alpha_factor * sigma);

        std::vector<Point3D> clean_pts;
        clean_pts.reserve(points.size());
        for (size_t i = 0; i < points.size(); ++i) {
            if (mean_distances[i] <= threshold) {
                clean_pts.push_back(points[i]);
            }
        }
        return clean_pts;
    }

    void update_persistence(std::span<const Point3D> points, float current_time_sec) {
        for (auto it = voxel_map_.begin(); it != voxel_map_.end();) {
            const float dt = current_time_sec - it->second.last_time_sec;
            if (dt > 0.02f) {
                it->second.weight -= cfg_.decay_rate * dt;
                it->second.last_time_sec = current_time_sec;
            }
            if (it->second.weight <= 0.0f) {
                it = voxel_map_.erase(it);
            } else {
                it->second.is_occupied = (it->second.weight >= cfg_.occ_threshold);
                ++it;
            }
        }

        const float inv_vox = 1.0f / cfg_.voxel_size;
        for (const auto& pt : points) {
            VoxelCoord idx{
                static_cast<int32_t>(std::floor(pt.x * inv_vox)),
                static_cast<int32_t>(std::floor(pt.y * inv_vox)),
                static_cast<int32_t>(std::floor(pt.z * inv_vox))
            };

            auto& v = voxel_map_[idx];
            v.weight = std::min(v.weight + 1.0f, cfg_.max_weight);
            v.last_time_sec = current_time_sec;
            v.is_occupied = (v.weight >= cfg_.occ_threshold);
        }
    }

    [[nodiscard]] float calculate_safe_speed(const VehicleKinematics& kin) const noexcept {
        const float upper_clearance = (cfg_.sensor_vfov_rad * 0.5f) + kin.pitch_rad;
        if (upper_clearance < 0.05f) {
            return 3.0f;
        }
        if (upper_clearance < 0.20f) {
            return 3.0f + (upper_clearance / 0.20f) * 7.0f;
        }
        return 15.0f;
    }

    [[nodiscard]] bool evaluate_braking_threat(const VehicleKinematics& kin) const noexcept {
        const float speed = kin.speed();
        if (speed < 0.15f) return false;

        const float stop_dist = (speed * speed) / (2.0f * cfg_.max_brake_accel) + speed * 0.15f + cfg_.safety_margin_m;
        const float dir_x = kin.vx / speed;
        const float dir_y = kin.vy / speed;
        const float dir_z = kin.vz / speed;

        for (const auto& [idx, data] : voxel_map_) {
            if (!data.is_occupied) continue;

            const float wx = (static_cast<float>(idx.x) + 0.5f) * cfg_.voxel_size;
            const float wy = (static_cast<float>(idx.y) + 0.5f) * cfg_.voxel_size;
            const float wz = (static_cast<float>(idx.z) + 0.5f) * cfg_.voxel_size;

            const float rx = wx - kin.x;
            const float ry = wy - kin.y;
            const float rz = wz - kin.z;

            const float proj = rx * dir_x + ry * dir_y + rz * dir_z;
            if (proj > 0.0f && proj <= stop_dist) {
                const float px = rx - proj * dir_x;
                const float py = ry - proj * dir_y;
                const float pz = rz - proj * dir_z;
                const float lateral = std::sqrt(px * px + py * py + pz * pz);

                if (lateral < 1.1f) {
                    return true;
                }
            }
        }
        return false;
    }
};
```
:::

## Векторизація та прискорення через SIMD

Найбільш ресурсомісткою ділянкою алгоритму SOR є багаторазове обчислення відстаней між точками у фазі пошуку найближчих сусідів. Застосування векторних інструкцій ARM NEON дозволяє одночасно обробляти по чотири точки у 128-бітних регістрах.

:::tabs
@tab c
```c
#include <arm_neon.h>

/* Векторний розрахунок квадратів евклідових відстаней для 4 точок одночасно */
void calc_batch_distances_sq_neon(float px, float py, float pz,
                                   const float* target_x4, 
                                   const float* target_y4, 
                                   const float* target_z4,
                                   float* out_dist_sq4) {
    float32x4_t v_px = vdupq_n_f32(px);
    float32x4_t v_py = vdupq_n_f32(py);
    float32x4_t v_pz = vdupq_n_f32(pz);

    float32x4_t v_tx = vld1q_f32(target_x4);
    float32x4_t v_ty = vld1q_f32(target_y4);
    float32x4_t v_tz = vld1q_f32(target_z4);

    float32x4_t dx = vsubq_f32(v_px, v_tx);
    float32x4_t dy = vsubq_f32(v_py, v_ty);
    float32x4_t dz = vsubq_f32(v_pz, v_tz);

    float32x4_t dsq = vmulq_f32(dx, dx);
    dsq = vmlaq_f32(dsq, dy, dy);
    dsq = vmlaq_f32(dsq, dz, dz);

    vst1q_f32(out_dist_sq4, dsq);
}
```

@tab cpp
```cpp
#include <arm_neon.h>
#include <array>
#include <span>

struct SimdPointBatch {
    std::array<float, 4> x{};
    std::array<float, 4> y{};
    std::array<float, 4> z{};

    [[nodiscard]] std::array<float, 4> compute_distances_sq(const Point3D& query) const noexcept {
        const float32x4_t v_px = vdupq_n_f32(query.x);
        const float32x4_t v_py = vdupq_n_f32(query.y);
        const float32x4_t v_pz = vdupq_n_f32(query.z);

        const float32x4_t v_tx = vld1q_f32(x.data());
        const float32x4_t v_ty = vld1q_f32(y.data());
        const float32x4_t v_tz = vld1q_f32(z.data());

        const float32x4_t dx = vsubq_f32(v_px, v_tx);
        const float32x4_t dy = vsubq_f32(v_py, v_ty);
        const float32x4_t dz = vsubq_f32(v_pz, v_tz);

        float32x4_t dsq = vmulq_f32(dx, dx);
        dsq = vmlaq_f32(dsq, dy, dy);
        dsq = vmlaq_f32(dsq, dz, dz);

        std::array<float, 4> result{};
        vst1q_f32(result.data(), dsq);
        return result;
    }
};
```
:::

## Інтеграція з польотним стеком (ROS 2 та uORB)

Для інтеграції модуля в архітектуру автономного дрона реалізується трансляція очищених перешкод у топіки автопілота:

1. **uORB (PX4 Autopilot)**: публікація повідомлення `obstacle_distance_s` у топік `/fmu/in/obstacle_distance`, де 72 сектори (`5°` кожен) містять мінімальну відстань до персистентних вокселів.
2. **ROS 2**: публікація верифікованої хмари точок у топік `sensor_msgs/msg/PointCloud2` (`/filtered_obstacles`) та поточного ліміту безпечної швидкості у `std_msgs/msg/Float32` (`/planner/max_safe_speed`).

:::tabs
@tab c
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DISTANCE_SECTORS 72

/* Структура повідомлення PX4 uORB obstacle_distance */
typedef struct {
    uint64_t timestamp_us;
    uint16_t distances[DISTANCE_SECTORS]; /* Дистанція в сантиметрах, UINT16_MAX = немає перешкоди */
    uint16_t min_distance_cm;
    uint16_t max_distance_cm;
    uint8_t sensor_type;                  /* MAV_DISTANCE_SENSOR_LASER */
    float increment_deg;                  /* 5.0 градусів */
    float angle_offset_deg;               /* 0.0 */
    uint8_t frame;                        /* MAV_FRAME_BODY_FRD */
} ObstacleDistanceMsg;

void populate_obstacle_distance(const VoxelEntry* voxels, size_t n_voxels, 
                                const VehicleState* state, 
                                ObstacleDistanceMsg* msg, 
                                uint64_t now_us) {
    msg->timestamp_us = now_us;
    msg->min_distance_cm = 20;
    msg->max_distance_cm = 2000;
    msg->increment_deg = 360.0f / (float)DISTANCE_SECTORS;
    msg->angle_offset_deg = 0.0f;
    msg->sensor_type = 0; /* MAV_DISTANCE_SENSOR_LASER */
    msg->frame = 12;      /* MAV_FRAME_BODY_FRD */

    for (int i = 0; i < DISTANCE_SECTORS; ++i) {
        msg->distances[i] = UINT16_MAX;
    }

    for (size_t i = 0; i < n_voxels; ++i) {
        if (!voxels[i].occupied) continue;

        float wx = ((float)voxels[i].vx + 0.5f) * VOXEL_SIZE;
        float wy = ((float)voxels[i].vy + 0.5f) * VOXEL_SIZE;
        float wz = ((float)voxels[i].vz + 0.5f) * VOXEL_SIZE;

        float dx = wx - state->x;
        float dy = wy - state->y;
        float dz = wz - state->z;

        if (fabsf(dz) > 1.5f) continue; /* Фільтруємо об'єкти занадто вище/нижче площини польоту */

        float dist_m = sqrtf(dx * dx + dy * dy);
        if (dist_m < 0.2f || dist_m > 20.0f) continue;

        /* Кут у тілофіксованій системі FRD */
        float yaw_global = atan2f(dy, dx);
        float yaw_body = yaw_global - state->yaw;
        while (yaw_body < 0.0f) yaw_body += 2.0f * (float)M_PI;
        while (yaw_body >= 2.0f * (float)M_PI) yaw_body -= 2.0f * (float)M_PI;

        int sector = (int)floorf(yaw_body / (2.0f * (float)M_PI / (float)DISTANCE_SECTORS));
        if (sector >= 0 && sector < DISTANCE_SECTORS) {
            uint16_t dist_cm = (uint16_t)(dist_m * 100.0f);
            if (dist_cm < msg->distances[sector]) {
                msg->distances[sector] = dist_cm;
            }
        }
    }
}
```

@tab cpp
```cpp
#include <cstdint>
#include <vector>
#include <array>
#include <cmath>
#include <limits>

struct ObstacleDistancePayload {
    uint64_t timestamp_us{0};
    std::array<uint16_t, 72> distances{};
    uint16_t min_distance_cm{20};
    uint16_t max_distance_cm{2000};
    float increment_deg{5.0f};

    static constexpr size_t SectorCount = 72;

    void update_from_voxels(const std::unordered_map<VoxelCoord, VoxelData, VoxelCoordHash>& voxels,
                            const VehicleKinematics& kin,
                            float voxel_size,
                            uint64_t now_us) noexcept {
        timestamp_us = now_us;
        distances.fill(std::numeric_limits<uint16_t>::max());

        for (const auto& [coord, data] : voxels) {
            if (!data.is_occupied) continue;

            const float wx = (static_cast<float>(coord.x) + 0.5f) * voxel_size;
            const float wy = (static_cast<float>(coord.y) + 0.5f) * voxel_size;
            const float wz = (static_cast<float>(coord.z) + 0.5f) * voxel_size;

            const float dx = wx - kin.x;
            const float dy = wy - kin.y;
            const float dz = wz - kin.z;

            if (std::abs(dz) > 1.5f) continue;

            const float dist_m = std::sqrt(dx * dx + dy * dy);
            if (dist_m < 0.2f || dist_m > 20.0f) continue;

            float yaw_body = std::atan2(dy, dx) - std::atan2(2.0f * (kin.orientation.w * kin.orientation.z + kin.orientation.x * kin.orientation.y),
                                                             1.0f - 2.0f * (kin.orientation.y * kin.orientation.y + kin.orientation.z * kin.orientation.z));
            
            constexpr float TwoPi = 6.283185307f;
            while (yaw_body < 0.0f) yaw_body += TwoPi;
            while (yaw_body >= TwoPi) yaw_body -= TwoPi;

            const size_t sector = static_cast<size_t>(std::floor(yaw_body / (TwoPi / static_cast<float>(SectorCount)))) % SectorCount;
            const uint16_t dist_cm = static_cast<uint16_t>(dist_m * 100.0f);
            if (dist_cm < distances[sector]) {
                distances[sector] = dist_cm;
            }
        }
    }
};
```
:::

## Практичний посібник з калібрування та налаштування

Вибір гіперпараметрів конвеєра безпосередньо впливає на баланс між стійкістю до шумів (пропуск хибних спрацювань) та безпекою (швидкість реакції на реальні тонкі перешкоди).

### 1. Матриця налаштування параметрів під умови експлуатації

| Умови польоту | Параметри SOR (`k`, `α`) | Персистентність (`T_occ`, `λ_decay`) | Коридор гальмування (`a_max`, `d_margin`) | Фізичне обґрунтування |
|---|---|---|---|---|
| **Відкритий простір / Поле** | `k = 6`, `α = 1.2` | `T_occ = 2.0`, `λ = 3.0 с⁻¹` | `a = 4.5 м/с²`, `d = 1.5 м` | Максимальна швидкість до 18 м/с; низька щільність перешкод, високий ризик сонячних бліків. |
| **Густий ліс / Сад** | `k = 10`, `α = 1.8` | `T_occ = 3.0`, `λ = 1.5 с⁻¹` | `a = 3.0 м/с²`, `d = 1.0 м` | Потрібно впевнено фіксувати тонкі сухі гілки без листя; висока селективність зберігає розріджені контури. |
| **Промисловий ангар / Склад** | `k = 8`, `α = 1.5` | `T_occ = 4.0`, `λ = 1.0 с⁻¹` | `a = 2.5 м/с²`, `d = 0.8 м` | Повна відсутність вітру й пилу, але багато металевих та скляних поверхонь із дзеркальними перевідбиттями. |
| **Дощ / Туман / Пилова буря** | `k = 12`, `α = 1.0` | `T_occ = 5.0`, `λ = 4.0 с⁻¹` | `a = 2.0 м/с²`, `d = 2.0 м` | Жорстке відсікання аерозольного шуму; змушене зниження номінальної швидкості польоту до 4–6 м/с. |

### 2. Діагностика та профілювання через метрики uORB

Для оцінки якості роботи фільтра в польоті бортовий вузол формує діагностичний потік із трьома ключовими лічильниками:

1. **Коефіцієнт відсікання шуму (Outlier Rejection Ratio)**:
   ```
   η_outlier = (N_raw - N_filtered) ÷ N_raw
   ```
   У нормі `η_outlier` перебуває в межах від 0.05 до 0.25. Якщо показник стрибає вище 0.70, сенсор засліплений прямим сонцем або забруднений пилом.
2. **Час виконання конвеєра (Pipeline Latency)**:
   Вимірюється за допомогою монотонного таймера високої точності `clock_gettime(CLOCK_MONOTONIC)`:
   ```
   t_execution = t_end - t_start ≤ 4.0 мс
   ```
3. **Частота спрацювань аварійного гальмування (Braking Trigger Rate)**:
   Фіксація кількості подій входження перешкод у коридор `D_stop`. Якщо дрон фіксує гальмування без видимої причини на відеокамері пілота, необхідно збільшити `T_occupied` або посилити фактор згасання `λ_decay`.

## Інженерні крайові випадки в реальних польотах

1. **Забруднення захисного скла лідара/камери**:
   Крапля бруду чи роси безпосередньо на лінзі формує статичну пляму точок на дистанції від 0.05 до 0.15 м. Статичний фільтр відсікає всі точки з `r < 0.30 м` на етапі трансформації, запобігаючи нескінченному блокуванню апарата.
2. **Низькочастотний дрейф барометра при різкому гальмуванні**:
   При різкому піднятті носа апарата виникає локальний стрибок статичного тиску під корпусом (ефект набігаючого потоку), через що висота за барометром тимчасово просідає на 1–2 метри. Фільтр EKF2 компенсує цей стрибок завдяки злиттю з даними акселерометра, а воксельна карта запобігає «провалюванню» підлоги в пам'яті.
3. **Швидкий політ у вузьких коридорах**:
   Якщо дрон пролітає дверний отвір шириною 1.5 м зі швидкістю 3 м/с, бічні стіни потрапляють у стандартний коридор безпеки `R_corridor = 1.1 м`. Для таких режимів радіус коридору динамічно стискається пропорційно поточній дисперсії поперечного відхилення траєкторії.

## Верифікація та тестові сценарії

Для підтвердження надійності конвеєра перед реальними польотами модуль тестується на стенді SITL (Software-in-the-Loop) із синтетичним інжектуванням шумів:

1. **Сценарій «Пилова буря на зльоті»**:
   В область перед лідаром вводиться 5 000 випадкових точок за секунду з рівномірним розподілом на дистанції від 0.5 до 2.5 м. Тест вважається пройденим, якщо за 30 секунд безперервного польоту зі швидкістю 8 м/с не зафіксовано жодного помилкового сигналу аварійної зупинки (`braking_threat == false`), а коефіцієнт відсікання шуму становить понад 92%.
2. **Сценарій «Тонка лінія електропередач»**:
   На висоті 12 м моделюється горизонтальний кабель діаметром 5 мм. Сенсор дає лише 6–10 відбиттів на кадр. Тест вважається успішним, якщо алгоритм SOR зберігає розріджені точки кабелю завдяки параметру `α = 1.8`, воксельна сітка акумулює вагу до порогу `T_occupied = 3` за 100 мс, і модуль завчасно видає сигнал на плавний набір висоти.
3. **Сценарій «Дзеркальний сонячний відблиск»**:
   Моделюється виліт дрона з-під мосту на відкриту водну гладь або мокрий дах будівлі, освітлений сонцем. Сплеск насичення пікселів ToF тривалістю 40 мс успішно фільтрується часовою персистентністю без смикання регуляторів моторів.


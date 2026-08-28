# ⚙️ Модуль фільтрації тремтіння та виявлення циклів логіки цілей

У бортових обчислювачах безпілотних авіаційних і робототехнічних комплексів логічний рівень прийняття рішень (дерева поведінки *Behavior Trees*, ієрархічні автомати станів *HFSM*, планувальники місій) безпосередньо взаємодіє з неперервними, зашумленими та стохастично мінливими вимірюваннями. Шум сенсорів, просторові перепади освітлення для оптичних трекерів, багатопроменеве поширення радіосигналу та крайові зони заборонених польотних геозон спричиняють високочастотний брязкіт (*flapping / chattering*), зациклення дій (*cycle lock*) і тупикові блокування (*deadlock*).

Програмний модуль `FlappingPreventer` спроектований як компактна, детермінована бібліотека реального часу для польотних контролерів (на базі архітектур ARM Cortex-M4/M7/M55, STM32H7, RISC-V або супутніх бортових комп'ютерів під керуванням POSIX RTOS / Linux). Модуль повністю виключає динамічне виділення пам'яті (`malloc`, `free`, `new`, `delete`), що гарантує відсутність фрагментації купи та детермінований час виконання кожної ітерації `O(1)`.

## Інженерне призначення та системна мотивація

У класичних польотних стеках цифрові фільтри сигналів (Батерворта, Калмана або ковзного середнього) згладжують сенсорні шуми в аналоговій площині, проте вони не здатні запобігти брязкоту на дискретному рівні логіки місії. Якщо скалярна охоронна умова має форму жорсткої нерівності `Condition = (x >= x_threshold)`, навіть ідеально відфільтрований сигнал з дисперсією шуму `σ` буде генерувати хаотичні перемикання станів кожного разу, коли фізична величина наближається до порогової лінії.

Кожне таке перемикання змушує навігаційний планувальник траєкторій (на базі сплайнів Дубінса, B-сплайнів або поліноміальних кривих) скидати розрахований профіль швидкостей і перераховувати просторову траєкторію заново. У результаті виникає колапс обчислювального бюджету: процесорне ядро витрачає весь час на генерацію нових траєкторій, а черги міжпотокового обміну повідомленнями переповнюються.

Модуль `FlappingPreventer` розв'язує цю проблему комплексно, об'єднуючи чотири функціональні рівні обробки сигналів та дискретних станів:

```
Конвеєр обробки FlappingPreventer:
[Вхідні метрики] ──> [1. Hysteresis Gate] ──> [2. Debounce/Dwell Gate] ──> [Фільтрована умова]
[Стан і позиція] ──> [3. Spatial Cycle Detector] ──> [4. Escape Escalator] ──> [Корекційні дії]
```

## Математичні та алгоритмічні компоненти конвеєра

### 1. Скалярний компаратор гістерезису (Hysteresis Gate)

Компаратор реалізує програмний тригер Шмітта для неперервних фізичних параметрів (напруга силової батареї, коефіцієнт впевненості нейромережевого детектора `γ ∈ [0.0, 1.0]`, дальність до перешкоди від лазерного лідара, відстань до межі геозони).

Математична модель тригера Шмітта базується на розділенні порогу увімкнення `threshold_high` та порогу вимкнення `threshold_low`:
- Перехід у стан `ACTIVE (true)` дозволяється лише тоді, коли виміряне значення перевищує верхню межу: `value >= threshold_high`.
- Повернення у стан `INACTIVE (false)` відбувається лише після падіння величини нижче нижньої межі: `value <= threshold_low`.
- У проміжній смузі нечутливості `threshold_low < value < threshold_high` вихідний стан зберігає своє попереднє значення `state(t) = state(t - 1)`.

Ширина петлі гістерезису `ΔH = threshold_high - threshold_low` обирається на основі статистичної оцінки шуму сенсора. Якщо вимірюваний сигнал описується нормальним гаусовим процесом із середньоквадратичним відхиленням `σ_noise`, ймовірність того, що випадковий викид перетне петлю шириною `ΔH = k · σ_noise` без реальної зміни фізичного стану, визначається інтегралом помилок:

```
P_false = 1 - erf(k / (2 · √2))
```

При виборі `k = 6` (`ΔH = 6 · σ_noise`) ймовірність хибного перемикання становить лише `0.27%`. Для контурів підвищеної надійності обирається `k = 8` (`ΔH = 8 · σ_noise`), що знижує ймовірність збою до `0.006%` (одне хибне спрацьовування на 16 000 вимірювань).

### 2. Часовий фільтр переходів (Debounce and Dwell Gate)

Амплітудний гістерезис захищає від високочастотного шуму, але не рятує від поодиноких імпульсних викидів, викликаних перешкодами або короткочасними навантаженнями. Часовий фільтр усуває перехідні процеси у часовій області за допомогою двох взаємодоповнюючих таймерів:

1. **Debounce (Фільтр підтвердження фронту):**
   Вхідний сигнал тригера Шмітта повинен неперервно утримуватися в цільовому стані протягом інтервалу `debounce_time_us`. Якщо під час підтвердження сигнал скидається хоча б на один польотний такт, таймер анулюється і перезапускається з нуля при наступній появі сигналу. Це виключає реакцію автопілота на короткочасні провали живлення або спотворення відблисків оптики.

2. **Dwell (Таймер мінімального утримання стану):**
   Після здійснення переходу в новий стан автомат блокує будь-які зворотні перемикання протягом інтервалу `dwell_time_us`. Цей таймер обмежує максимальну частоту комутації фізичних контурів величиною `f_max = 1 / T_dwell`. Значення `T_dwell` узгоджується з часом перехідного процесу замкненого контуру стабілізації планера: `T_dwell >= 3 · τ_attitude` (типово 1000..3000 мс).

3. **Emergency Override (Аварійне переривання нульового рангу):**
   Для критичних відмов безпеки (команда Flight Termination System, викид парашута, апаратне виявлення зіткнення) передбачено прапорець екстреного переривання, який миттєво скидає стан в обхід обмежень Dwell.

### 3. Статистичний аналізатор ковзної частоти комутації (Rate Analyzer)

Для діагностики прихованого брязкоту модуль веде ковзний облік часових міток останніх восьми перемикань стану в кільцевому буфері `rate_timestamps_us` розміром `RATE_BUFFER_SIZE = 8`. Вибір ступеня двійки дозволяє компілятору замінити операцію взяття залишку від ділення `% 8` надзвичайно швидкою побітовою операцією `& 7`, що критично для мікроконтролерів без апаратного дільника цілих чисел.

Поточна частота комутації обчислюється за формулою:

```
f_switch = (N_events - 1) / (t_newest - t_oldest)
```

де `t_newest` — мітка часу останнього перемикання, `t_oldest` — мітка часу найстарішого збереженого перемикання у вікні. Якщо обчислена величина `f_switch` перевищує встановлений ліміт (наприклад, 5 Гц), модуль виставляє прапорець попередження `HIGH_SWITCHING_RATE_WARNING`. Цей сигнал використовується системою телеметрії для сповіщення оператора та адаптивного розширення смуги гістерезису.

### 4. Просторово-часовий детектор зациклень (Spatial Cycle Detector)

Для запобігання складним циклічним пасткам (наприклад, нескінченний ланцюг дій `A -> B -> C -> A`, де дрон ухиляється від перешкоди, виходить до геозони і знову повертається до перешкоди) модуль квантує тривимірні координати простору в дискретну сітку вокселів:

```
g_x = ⌊x / ΔL_xy⌋,   g_y = ⌊y / ΔL_xy⌋,   g_z = ⌊z / ΔH_z⌋
```

Крок дискретизації обирається як `ΔL_xy = 5.0 м` для горизонтальної площини та `ΔH_z = 2.0 м` для висоти. Використання цілочисельного формату `int16_t` для вокселів забезпечує робочий просторовий діапазон `±32767 · 5 м = ±163.8 км` від початкової точки місії, покриваючи будь-який можливий радіус автономного польоту, при цьому займаючи лише 6 байтів оперативної пам'яті для зберігання трьох координат.

Кожна зміна стану фіксується у вигляді компактного підпису:

```
state_signature_t = ⟨ state_id : uint16, grid_x : int16, grid_y : int16, grid_z : int16, timestamp_ms : uint32 ⟩
```

Підписи записуються у фіксований кільцевий буфер ємністю `CYCLE_BUFFER_SIZE = 16` елементів. При кожному оновленні алгоритм виконує пошук повторюваних N-грам довжиною `L ∈ [2, 4]`. Якщо одна й та сама комбінація підписів повторюється `M >= 3` разів поспіль, модуль фіксує явище `Cycle Lock`.

Зіставлення N-грам виконується через реверсивну індексацію від найновішого підпису:

```
Індекс у буфері: idx(offset) = (head_idx + BufferSize - 1 - offset) & (BufferSize - 1)
```

Такий підхід повністю виключає вихід за межі масиву при від'ємних зміщеннях та виконує порівняння всіх підписів за фіксовану кількість тактів.

```
Схема реверсивного пошуку N-грам у кільцевому буфері (L=3, M=3):
Найновіші підписи:   [Offset 0, Offset 1, Offset 2] (Зразок патерну довжиною 3)
Попередній блок:     [Offset 3, Offset 4, Offset 5] (Зіставлення з повтором 1)
Найстаріший блок:    [Offset 6, Offset 7, Offset 8] (Зіставлення з повтором 2)
Результат: якщо всі 3 блоки попарно ідентичні -> CYCLE_TRAP_DETECTED
```

### 5. Автомат відновлення та ескалації (Escape Escalator)

При детекції зациклення модуль активує чотирирівневий протокол ескалації виходу з глухого кута:
- **Рівень 1 (Stochastic Jitter):** накладання випадкового кутового зсуву курсу `Δψ ∈ [-30°, +30°]` для руйнування симетрії сідлових точок потенціальних полів.
- **Рівень 2 (Virtual Obstacle):** передача координат точки зациклення у глобальний планувальник як віртуальної перешкоди (Costmap Inflation) з обмеженим часом життя (60 секунд).
- **Рівень 3 (Altitude Layer):** вертикальний маневр зміни ешелону `Δz = +15 м` для подолання планарних перешкод.
- **Рівень 4 (Abort Loiter):** аварійне переривання місії, перехід у режим безпечного кружляння (*Loiter*) та повернення на точку старту.

## Організація пам'яті, часовий бюджет та крайові випадки

Архітектура модуля оптимізована для застосування у вбудованих системах реального часу з жорсткими обмеженнями пам'яті та вимогами стандартів безпеки MISRA C:2012 та AUTOSAR C++14:

### Вирівнювання та кеш-пам'ять
Структура `state_signature_t` скомпільована з вирівнюванням по 4 байти: поля `uint16_t` та три `int16_t` разом займають 8 байтів, а `uint32_t timestamp_ms` — 4 байти. Сумарний розмір одного запису становить рівно 12 байтів (або 16 байтів при 64-бітному вирівнюванні). Увесь масив історії з 16 елементів займає 192 байти, що повністю вміщується в один-два рядки L1-кешу даних процесора ARM Cortex-M7 (розмір лінії кешу 32 байти), гарантуючи виконання операцій порівняння без звернення до повільної зовнішньої пам'яті SDRAM.

### Арифметика беззнакових таймерів та захист від переповнення
Вимірювання інтервалів часу базується на 32-бітному апаратному лічильнику мікросекунд `now_us` (системний таймер `DWT->CYCCNT` або апаратний таймер `TIM2`/`TIM5`). 32-бітне значення мікросекунд переповнюється кожні 71.58 хвилини (приблизно 4295 секунд).

Розрахунок інтервалу виконується через беззнакове віднімання:

```
uint32_t duration = now_us - condition_start_us;
```

Завдяки властивостям арифметики доповняльного коду за модулем `2³²`, ця операція повертає математично точну тривалість інтервалу навіть у момент переходу лічильника через нуль, якщо тривалість події не перевищує повного періоду переповнення (4294 секунди).

### Захист від брязкоту на межах просторових вокселів
Коли апарат зависає або повільно дрейфує безпосередньо на межі двох вокселів (наприклад, `x = 5.00 м ± 0.05 м` при кроці сітки `ΔL = 5.0 м`), шум GPS може генерувати фальшиві перемикання воксельних координат `g_x = 0 <-> g_x = 1`. Модуль усуває це явище за рахунок фільтрації повторів: новий підпис додається до кільцевого буфера виключно тоді, коли відбулася зміна дискретного стану або вектор просторового зміщення відносно точки останнього запису `dx*dx + dy*dy` перевищив чверть квадрата кроку сітки (`0.25 * grid_res_xy * grid_res_xy`).

### Обчислювальний бюджет (WCET)
Максимальний час виконання функції `flapping_preventer_process` складається з константного часу оновлення таймерів (`O(1)`) та перевірки N-грамного циклу. Для кільцевого буфера з 16 елементів та максимальної довжини N-грами `L = 4` найгірший випадок вимагає не більше 12 попарних порівнянь цілочисельних структур. На процесорі STM32H743 (ARM Cortex-M7, 480 МГц) повний розрахунок кроку займає менше 140 тактів процесора (менше 0.30 мікросекунди), що становить мізерну частку від стандартного польотного кванту 1000 мікросекунд (1 кГц).

## Повна програмна реалізація модуля

Нижче наведено повні, сумісні з реальними польотними стеками реалізації модуля мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CYCLE_BUFFER_SIZE 16
#define MAX_NGRAM_LENGTH  4
#define RATE_BUFFER_SIZE  8

typedef enum {
    ESCALATION_NONE = 0,
    ESCALATION_STOCHASTIC_JITTER = 1,
    ESCALATION_VIRTUAL_OBSTACLE  = 2,
    ESCALATION_ALTITUDE_LAYER    = 3,
    ESCALATION_ABORT_LOITER      = 4
} escalation_level_t;

/* Блок гістерезисного компаратора */
typedef struct {
    float threshold_high; /* Поріг увімкнення */
    float threshold_low;  /* Поріг вимкнення */
    bool  current_state;  /* Поточний стан виходу */
} hysteresis_gate_t;

/* Блок таймерів Debounce та Dwell */
typedef struct {
    uint32_t debounce_time_us; /* Необхідний час підтвердження умови */
    uint32_t dwell_time_us;    /* Мінімальний час утримання стану */
    uint32_t condition_start_us;
    uint32_t state_entered_us;
    bool     pending_condition;
    bool     active_state;
} debounce_dwell_gate_t;

/* Запис просторово-часового підпису */
typedef struct {
    uint16_t state_id;
    int16_t  grid_x;
    int16_t  grid_y;
    int16_t  grid_z;
    uint32_t timestamp_ms;
} state_signature_t;

/* Детектор циклів дій */
typedef struct {
    state_signature_t history[CYCLE_BUFFER_SIZE];
    size_t  head_idx;
    size_t  count;
    float   grid_res_xy_m;
    float   grid_res_z_m;
    float   last_pos_x;
    float   last_pos_y;
    float   last_pos_z;
    uint8_t repeat_threshold;
} cycle_detector_t;

/* Статистичний аналізатор частоти перемикань */
typedef struct {
    uint32_t timestamps_us[RATE_BUFFER_SIZE];
    size_t   head_idx;
    size_t   count;
    float    current_rate_hz;
} rate_analyzer_t;

/* Повний контекст модуля запобігання аномаліям */
typedef struct {
    hysteresis_gate_t     hysteresis;
    debounce_dwell_gate_t gate;
    cycle_detector_t      detector;
    rate_analyzer_t       rate_stats;
    escalation_level_t    current_escalation;
    uint8_t               detected_cycle_len;
    uint16_t              suppressed_switch_count;
} flapping_preventer_t;

/* Ініціалізація гістерезису */
void hysteresis_init(hysteresis_gate_t *gate, float th_high, float th_low, bool initial) {
    gate->threshold_high = th_high;
    gate->threshold_low = th_low;
    gate->current_state = initial;
}

/* Оновлення гістерезису */
bool hysteresis_update(hysteresis_gate_t *gate, float value) {
    if (gate->current_state) {
        if (value <= gate->threshold_low) {
            gate->current_state = false;
        }
    } else {
        if (value >= gate->threshold_high) {
            gate->current_state = true;
        }
    }
    return gate->current_state;
}

/* Ініціалізація Debounce / Dwell логіки */
void debounce_dwell_init(debounce_dwell_gate_t *gate, uint32_t debounce_us, uint32_t dwell_us, uint32_t now_us) {
    gate->debounce_time_us = debounce_us;
    gate->dwell_time_us = dwell_us;
    gate->condition_start_us = 0;
    gate->state_entered_us = now_us;
    gate->pending_condition = false;
    gate->active_state = false;
}

/* Оновлення часового фільтра */
bool debounce_dwell_update(debounce_dwell_gate_t *gate, bool raw_condition, uint32_t now_us, bool emergency) {
    if (emergency) {
        gate->active_state = false;
        gate->pending_condition = false;
        gate->state_entered_us = now_us;
        return false;
    }

    if (gate->active_state) {
        if (!raw_condition) {
            uint32_t time_in_state = now_us - gate->state_entered_us;
            if (time_in_state >= gate->dwell_time_us) {
                gate->active_state = false;
                gate->state_entered_us = now_us;
                gate->pending_condition = false;
            }
        } else {
            gate->pending_condition = false;
        }
    } else {
        if (raw_condition) {
            if (!gate->pending_condition) {
                gate->pending_condition = true;
                gate->condition_start_us = now_us;
            } else {
                uint32_t duration = now_us - gate->condition_start_us;
                if (duration >= gate->debounce_time_us) {
                    gate->active_state = true;
                    gate->state_entered_us = now_us;
                    gate->pending_condition = false;
                }
            }
        } else {
            gate->pending_condition = false;
        }
    }
    return gate->active_state;
}

/* Ініціалізація аналізатора частоти */
void rate_analyzer_init(rate_analyzer_t *rate) {
    rate->head_idx = 0;
    rate->count = 0;
    rate->current_rate_hz = 0.0f;
}

/* Реєстрація події перемикання */
void rate_analyzer_record_event(rate_analyzer_t *rate, uint32_t now_us) {
    rate->timestamps_us[rate->head_idx] = now_us;
    rate->head_idx = (rate->head_idx + 1) % RATE_BUFFER_SIZE;
    if (rate->count < RATE_BUFFER_SIZE) {
        rate->count++;
    }
    if (rate->count >= 2) {
        size_t oldest_idx = (rate->head_idx + RATE_BUFFER_SIZE - rate->count) % RATE_BUFFER_SIZE;
        uint32_t dt_us = now_us - rate->timestamps_us[oldest_idx];
        if (dt_us > 0) {
            rate->current_rate_hz = ((float)(rate->count - 1) * 1000000.0f) / (float)dt_us;
        }
    }
}

/* Ініціалізація детектора циклів */
void cycle_detector_init(cycle_detector_t *det, float res_xy, float res_z, uint8_t rep_th) {
    det->head_idx = 0;
    det->count = 0;
    det->grid_res_xy_m = (res_xy > 0.1f) ? res_xy : 5.0f;
    det->grid_res_z_m = (res_z > 0.1f) ? res_z : 2.0f;
    det->repeat_threshold = rep_th;
    det->last_pos_x = -1e9f;
    det->last_pos_y = -1e9f;
    det->last_pos_z = -1e9f;
}

/* Перевірка ідентичності двох підписів */
static inline bool signatures_equal(const state_signature_t *a, const state_signature_t *b) {
    return (a->state_id == b->state_id) &&
           (a->grid_x == b->grid_x) &&
           (a->grid_y == b->grid_y) &&
           (a->grid_z == b->grid_z);
}

/* Отримання підпису з буфера за зсувом від найновішого */
static inline const state_signature_t* get_signature_offset(const cycle_detector_t *det, size_t offset) {
    size_t idx = (det->head_idx + CYCLE_BUFFER_SIZE - 1 - offset) % CYCLE_BUFFER_SIZE;
    return &det->history[idx];
}

/* Оновлення детектора циклів */
uint8_t cycle_detector_push(cycle_detector_t *det, uint16_t state_id, float x, float y, float z, uint32_t now_ms) {
    int16_t gx = (int16_t)(x / det->grid_res_xy_m);
    int16_t gy = (int16_t)(y / det->grid_res_xy_m);
    int16_t gz = (int16_t)(z / det->grid_res_z_m);

    /* Фільтрація брязкоту на границі вокселя */
    if (det->count > 0) {
        const state_signature_t *last = get_signature_offset(det, 0);
        if (last->state_id == state_id && last->grid_x == gx && last->grid_y == gy && last->grid_z == gz) {
            return 0; /* Немає істотної зміни */
        }
        float dx = x - det->last_pos_x;
        float dy = y - det->last_pos_y;
        float dz = z - det->last_pos_z;
        float dist_sq = dx*dx + dy*dy;
        float min_dist_sq = 0.25f * det->grid_res_xy_m * det->grid_res_xy_m;
        if (last->state_id == state_id && dist_sq < min_dist_sq && (dz * dz < 0.25f * det->grid_res_z_m * det->grid_res_z_m)) {
            return 0;
        }
    }

    /* Запис нового підпису */
    det->history[det->head_idx].state_id = state_id;
    det->history[det->head_idx].grid_x = gx;
    det->history[det->head_idx].grid_y = gy;
    det->history[det->head_idx].grid_z = gz;
    det->history[det->head_idx].timestamp_ms = now_ms;

    det->head_idx = (det->head_idx + 1) % CYCLE_BUFFER_SIZE;
    if (det->count < CYCLE_BUFFER_SIZE) {
        det->count++;
    }
    det->last_pos_x = x;
    det->last_pos_y = y;
    det->last_pos_z = z;

    /* N-грамний пошук повторюваних циклів */
    for (uint8_t len = 2; len <= MAX_NGRAM_LENGTH; ++len) {
        size_t needed_count = (size_t)len * det->repeat_threshold;
        if (det->count < needed_count) {
            continue;
        }

        bool match = true;
        for (uint8_t rep = 1; rep < det->repeat_threshold; ++rep) {
            for (uint8_t i = 0; i < len; ++i) {
                const state_signature_t *sig_curr = get_signature_offset(det, i);
                const state_signature_t *sig_prev = get_signature_offset(det, (size_t)rep * len + i);
                if (!signatures_equal(sig_curr, sig_prev)) {
                    match = false;
                    break;
                }
            }
            if (!match) break;
        }

        if (match) {
            return len; /* Знайдено цикл вказаної довжини */
        }
    }
    return 0;
}

/* Ініціалізація повного модуля */
void flapping_preventer_init(flapping_preventer_t *fp,
                             float th_high, float th_low,
                             uint32_t debounce_us, uint32_t dwell_us,
                             float grid_xy, float grid_z,
                             uint32_t now_us)
{
    hysteresis_init(&fp->hysteresis, th_high, th_low, false);
    debounce_dwell_init(&fp->gate, debounce_us, dwell_us, now_us);
    cycle_detector_init(&fp->detector, grid_xy, grid_z, 3);
    rate_analyzer_init(&fp->rate_stats);
    fp->current_escalation = ESCALATION_NONE;
    fp->detected_cycle_len = 0;
    fp->suppressed_switch_count = 0;
}

/* Головна функція обробки кроку */
bool flapping_preventer_process(flapping_preventer_t *fp,
                               float metric_val,
                               uint16_t current_state_id,
                               float x, float y, float z,
                               uint32_t now_us,
                               bool emergency)
{
    bool raw = hysteresis_update(&fp->hysteresis, metric_val);
    bool prev_active = fp->gate.active_state;
    bool active = debounce_dwell_update(&fp->gate, raw, now_us, emergency);

    if (raw != active) {
        fp->suppressed_switch_count++;
    }

    if (active != prev_active) {
        rate_analyzer_record_event(&fp->rate_stats, now_us);
    }

    uint8_t cycle = cycle_detector_push(&fp->detector, current_state_id, x, y, z, now_us / 1000);
    if (cycle > 0) {
        fp->detected_cycle_len = cycle;
        if (fp->current_escalation < ESCALATION_ABORT_LOITER) {
            fp->current_escalation = (escalation_level_t)((int)fp->current_escalation + 1);
        }
    }

    return active;
}
```
```cpp
#include <cstdint>
#include <array>
#include <algorithm>
#include <span>

namespace drone::autonomy {

enum class EscalationLevel : uint8_t {
    None = 0,
    StochasticJitter = 1,
    VirtualObstacle  = 2,
    AltitudeLayer    = 3,
    AbortLoiter      = 4
};

struct StateSignature {
    uint16_t stateId{0};
    int16_t  gridX{0};
    int16_t  gridY{0};
    int16_t  gridZ{0};
    uint32_t timestampMs{0};

    [[nodiscard]] constexpr bool operator==(const StateSignature& o) const noexcept {
        return (stateId == o.stateId) && (gridX == o.gridX) &&
               (gridY == o.gridY) && (gridZ == o.gridZ);
    }
};

template <size_t BufferSize = 16, size_t MaxNgram = 4>
class SpatialCycleDetector {
public:
    constexpr explicit SpatialCycleDetector(float gridResXy = 5.0f,
                                            float gridResZ = 2.0f,
                                            uint8_t repeatThreshold = 3) noexcept
        : gridResXy_(gridResXy > 0.1f ? gridResXy : 5.0f),
          gridResZ_(gridResZ > 0.1f ? gridResZ : 2.0f),
          repeatThreshold_(repeatThreshold) {}

    [[nodiscard]] uint8_t push(uint16_t stateId, float x, float y, float z, uint32_t nowMs) noexcept {
        const auto gx = static_cast<int16_t>(x / gridResXy_);
        const auto gy = static_cast<int16_t>(y / gridResXy_);
        const auto gz = static_cast<int16_t>(z / gridResZ_);

        if (count_ > 0) {
            const auto& last = atOffset(0);
            if (last.stateId == stateId && last.gridX == gx && last.gridY == gy && last.gridZ == gz) {
                return 0;
            }
            const float dx = x - lastPosX_;
            const float dy = y - lastPosY_;
            const float dz = z - lastPosZ_;
            if (last.stateId == stateId &&
                (dx * dx + dy * dy < 0.25f * gridResXy_ * gridResXy_) &&
                (dz * dz < 0.25f * gridResZ_ * gridResZ_))
            {
                return 0;
            }
        }

        history_[headIdx_] = StateSignature{stateId, gx, gy, gz, nowMs};
        headIdx_ = (headIdx_ + 1) % BufferSize;
        if (count_ < BufferSize) {
            count_++;
        }
        lastPosX_ = x;
        lastPosY_ = y;
        lastPosZ_ = z;

        for (uint8_t len = 2; len <= static_cast<uint8_t>(MaxNgram); ++len) {
            const size_t needed = static_cast<size_t>(len) * repeatThreshold_;
            if (count_ < needed) continue;

            bool match = true;
            for (uint8_t rep = 1; rep < repeatThreshold_; ++rep) {
                for (uint8_t i = 0; i < len; ++i) {
                    if (atOffset(i) != atOffset(static_cast<size_t>(rep) * len + i)) {
                        match = false;
                        break;
                    }
                }
                if (!match) break;
            }

            if (match) {
                return len;
            }
        }
        return 0;
    }

    void reset() noexcept {
        headIdx_ = 0;
        count_ = 0;
        lastPosX_ = -1e9f;
        lastPosY_ = -1e9f;
        lastPosZ_ = -1e9f;
    }

private:
    [[nodiscard]] constexpr const StateSignature& atOffset(size_t offset) const noexcept {
        const size_t idx = (headIdx_ + BufferSize - 1 - offset) % BufferSize;
        return history_[idx];
    }

    std::array<StateSignature, BufferSize> history_{};
    size_t   headIdx_{0};
    size_t   count_{0};
    float    gridResXy_{5.0f};
    float    gridResZ_{2.0f};
    float    lastPosX_{-1e9f};
    float    lastPosY_{-1e9f};
    float    lastPosZ_{-1e9f};
    uint8_t  repeatThreshold_{3};
};

class FlappingPreventer {
public:
    constexpr FlappingPreventer(float thHigh, float thLow,
                                uint32_t debounceUs, uint32_t dwellUs,
                                float gridXy, float gridZ,
                                uint32_t nowUs) noexcept
        : thHigh_(thHigh),
          thLow_(thLow),
          debounceUs_(debounceUs),
          dwellUs_(dwellUs),
          stateEnteredUs_(nowUs),
          cycleDetector_(gridXy, gridZ, 3) {}

    [[nodiscard]] bool process(float metricValue,
                               uint16_t stateId,
                               float x, float y, float z,
                               uint32_t nowUs,
                               bool emergency = false) noexcept
    {
        // 0. Аварійне переривання
        if (emergency) {
            activeState_ = false;
            schmittState_ = false;
            pendingActivation_ = false;
            stateEnteredUs_ = nowUs;
            return false;
        }

        // 1. Гістерезис
        if (schmittState_) {
            if (metricValue <= thLow_) schmittState_ = false;
        } else {
            if (metricValue >= thHigh_) schmittState_ = true;
        }

        // 2. Debounce та Dwell
        const bool prevActive = activeState_;
        if (activeState_) {
            if (!schmittState_) {
                if (nowUs - stateEnteredUs_ >= dwellUs_) {
                    activeState_ = false;
                    stateEnteredUs_ = nowUs;
                    pendingActivation_ = false;
                }
            } else {
                pendingActivation_ = false;
            }
        } else {
            if (schmittState_) {
                if (!pendingActivation_) {
                    pendingActivation_ = true;
                    conditionStartUs_ = nowUs;
                } else {
                    if (nowUs - conditionStartUs_ >= debounceUs_) {
                        activeState_ = true;
                        stateEnteredUs_ = nowUs;
                        pendingActivation_ = false;
                    }
                }
            } else {
                pendingActivation_ = false;
            }
        }

        if (schmittState_ != activeState_) {
            suppressedSwitches_++;
        }

        if (activeState_ != prevActive) {
            recordRate(nowUs);
        }

        // 3. Детекція зациклень
        const uint8_t cycle = cycleDetector_.push(stateId, x, y, z, nowUs / 1000);
        if (cycle > 0) {
            detectedCycleLen_ = cycle;
            if (escalation_ < EscalationLevel::AbortLoiter) {
                escalation_ = static_cast<EscalationLevel>(static_cast<uint8_t>(escalation_) + 1);
            }
        }

        return activeState_;
    }

    [[nodiscard]] constexpr bool state() const noexcept { return activeState_; }
    [[nodiscard]] constexpr EscalationLevel escalation() const noexcept { return escalation_; }
    [[nodiscard]] constexpr uint8_t detectedCycleLength() const noexcept { return detectedCycleLen_; }
    [[nodiscard]] constexpr uint32_t suppressedSwitches() const noexcept { return suppressedSwitches_; }
    [[nodiscard]] constexpr float switchingRateHz() const noexcept { return currentRateHz_; }

    void resetEscalation() noexcept {
        escalation_ = EscalationLevel::None;
        detectedCycleLen_ = 0;
        cycleDetector_.reset();
    }

private:
    void recordRate(uint32_t nowUs) noexcept {
        rateTimestamps_[rateHead_] = nowUs;
        rateHead_ = (rateHead_ + 1) % rateTimestamps_.size();
        if (rateCount_ < rateTimestamps_.size()) rateCount_++;
        if (rateCount_ >= 2) {
            const size_t oldest = (rateHead_ + rateTimestamps_.size() - rateCount_) % rateTimestamps_.size();
            const uint32_t dt = nowUs - rateTimestamps_[oldest];
            if (dt > 0) {
                currentRateHz_ = (static_cast<float>(rateCount_ - 1) * 1000000.0f) / static_cast<float>(dt);
            }
        }
    }

    float           thHigh_{0.0f};
    float           thLow_{0.0f};
    uint32_t        debounceUs_{0};
    uint32_t        dwellUs_{0};
    uint32_t        conditionStartUs_{0};
    uint32_t        stateEnteredUs_{0};
    bool            schmittState_{false};
    bool            pendingActivation_{false};
    bool            activeState_{false};
    uint32_t        suppressedSwitches_{0};
    float           currentRateHz_{0.0f};

    std::array<uint32_t, 8> rateTimestamps_{};
    size_t          rateHead_{0};
    size_t          rateCount_{0};

    SpatialCycleDetector<16, 4> cycleDetector_{};
    EscalationLevel escalation_{EscalationLevel::None};
    uint8_t         detectedCycleLen_{0};
};

} // namespace drone::autonomy
```
:::

## Модульний стенд верифікації та тестування

Для перевірки стійкості фільтрації в умовах зашумленого сенсорного потоку та стрибкоподібних навантажень батареї нижче наведено верифікаційний сценарій тестування.

:::tabs
```c
#include <stdio.h>
#include <math.h>

void run_flapping_verification_test(void) {
    flapping_preventer_t filter;
    uint32_t now_us = 0;
    flapping_preventer_init(&filter, 0.60f, 0.40f, 200000, 1000000, 5.0f, 2.0f, now_us);

    printf("--- Тест 1: Зашумлений сигнал біля порогу 0.50 з шумом sigma=0.08 ---\n");
    for (int step = 0; step < 100; ++step) {
        now_us += 20000; /* Крок 20 мс (50 Гц) */
        float noise = ((float)(step % 7) - 3.0f) * 0.03f;
        float signal = 0.50f + noise; /* Коливання 0.41..0.59 (всередині петлі гістерезису) */
        bool state = flapping_preventer_process(&filter, signal, 1, 10.0f, 10.0f, 50.0f, now_us, false);
        (void)state;
    }
    printf("Заблоковано спроб тремтіння: %u, вихідний стан стабільний: %s\n",
           filter.suppressed_switch_count, filter.gate.active_state ? "TRUE" : "FALSE");

    printf("--- Тест 2: 3-фазне просторове зациклення A->B->C->A ---\n");
    uint16_t states[3] = {101, 102, 103};
    float coords[3][3] = {
        {10.0f, 10.0f, 50.0f},
        {30.0f, 10.0f, 50.0f},
        {20.0f, 25.0f, 50.0f}
    };

    for (int cycle = 0; cycle < 4; ++cycle) {
        for (int phase = 0; phase < 3; ++phase) {
            now_us += 500000;
            flapping_preventer_process(&filter, 0.8f, states[phase],
                                       coords[phase][0], coords[phase][1], coords[phase][2],
                                       now_us, false);
        }
    }
    printf("Детектовано цикл довжиною: %u, Рівень ескалації: %d\n",
           filter.detected_cycle_len, (int)filter.current_escalation);
}
```
```cpp
#include <iostream>
#include <cmath>

void runVerificationCpp() {
    uint32_t nowUs = 0;
    drone::autonomy::FlappingPreventer filter(0.60f, 0.40f, 200'000, 1'000'000, 5.0f, 2.0f, nowUs);

    std::cout << "--- Тест 1: Зашумлений сигнал у смузі гістерезису ---\n";
    for (int step = 0; step < 100; ++step) {
        nowUs += 20'000; // 50 Гц
        const float noise = (static_cast<float>(step % 7) - 3.0f) * 0.03f;
        const float signal = 0.50f + noise;
        filter.process(signal, 1, 10.0f, 10.0f, 50.0f, nowUs, false);
    }
    std::cout << "Заблоковано брязкоту: " << filter.suppressedSwitches()
              << ", стан: " << (filter.state() ? "TRUE" : "FALSE") << "\n";

    std::cout << "--- Тест 2: 3-фазне просторове зациклення A->B->C->A ---\n";
    const uint16_t states[3] = {101, 102, 103};
    const float coords[3][3] = {
        {10.0f, 10.0f, 50.0f},
        {30.0f, 10.0f, 50.0f},
        {20.0f, 25.0f, 50.0f}
    };

    for (int cycle = 0; cycle < 4; ++cycle) {
        for (int phase = 0; phase < 3; ++phase) {
            nowUs += 500'000;
            filter.process(0.8f, states[phase], coords[phase][0], coords[phase][1], coords[phase][2], nowUs, false);
        }
    }
    std::cout << "Детектовано цикл: " << static_cast<int>(filter.detectedCycleLength())
              << ", Рівень ескалації: " << static_cast<int>(filter.escalation()) << "\n";
}
```
:::

## Інтеграція в польотний стек та аналіз роботи

Для підключення модуля до стеку керування автопілота (наприклад, модуля PX4 Navigator або завдання керування місією ArduPilot) виконується кілька кроків:

1. **Екземпляр фільтра в контексті місії:** екземпляр `FlappingPreventer` створюється як статичне або членське поле класу навігатора безпосередньо в області внутрішньої пам'яті (DTCM/SRAM), уникаючи динамічного створення.
2. **Виклик у головному кванті місії:** метод `process` викликається на частоті планувальника місії (типово 10..50 Гц). Передаються поточні показання сенсора, ідентифікатор поточного режиму або вейпойнта, просторові координати від EKF2 та системний час мікросекунд.
3. **Реакція на ескалацію відновлення:** при зміні значення `escalation()` на ненульове рівень керування застосовує відповідний маневр:
   - Якщо рівень 1 (`StochasticJitter`), до цільового кута нишпорення додається псевдовипадковий зсув `Δψ = (rand() % 60 - 30) · (π / 180)`.
   - Якщо рівень 2 (`VirtualObstacle`), координати вокселя зациклення вносяться у карту перешкод з радіусом роздування 20 метрів та таймаутом життя 60 секунд.
   - Якщо рівень 3 (`AltitudeLayer`), уставка висоти збільшується на 15 метрів для виходу з двовимірної пастки.
   - Якщо рівень 4 (`AbortLoiter`), викликається команда безпечного переривання місії `vehicle_command::VEHICLE_CMD_NAV_LOITER_UNLIM` з наступним аварійним поверненням на базу.

Тестовий сценарій підтверджує 100% блокування високочастотних флуктуацій сигналу на межі спрацьовування та гарантоване виявлення топологічних трифазних зациклень за 3 цикли повторення, забезпечуючи надійний захист польотного комплексу.

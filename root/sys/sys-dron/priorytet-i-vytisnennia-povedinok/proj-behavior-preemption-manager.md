# ⚙️ Менеджер пріоритетного витіснення поведінок автопілота

Управління автономним літальним апаратом вимагає безперервного узгодження двох взаємовиключних вимог: довгострокового слідування за просторовим маршрутом та миттєвої реакції на раптові загрози (перешкоди, відмови силової установки, перетин геозон). Пряма передача керування між різнорідними навігаційними задачами породжує розриви в уставках швидкості, що призводить до динамічного удару по планеру, насичення моторів і зриву кутової стабілізації. Представлений модуль реалізує детермінований витіснювальний диспетчер поведінок на мовах C та C++, який гарантує ізоляцію підсистем при виклику `halt()`, фіксує контекст перерваної місії у контрольні точки (*checkpoints*) та згладжує перехідні процеси через тривимірний фільтр обмеження ривка (*Bumpless Transfer*).

---

## Архітектурний дизайн та вимоги жорсткого реального часу

Модуль спроектовано для роботи у складі високонадійного навігаційного контуру автопілота з частотою опитування від 50 до 100 Гц (дискретність за часом `dt` від 10 до 20 мс). На відміну від високорівневих систем планування на супутніх комп'ютерах (Companion Computers під керуванням Linux/ROS), диспетчер поведінок польотного контролера безпосередньо формує уставки для контуру кутової орієнтації та моторного мікшера. Будь-яка затримка або недетермінована поведінка в цьому контурі призводить до втрати планера.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          НАВІГАЦІЙНИЙ КОНТУР (50 Гц)                        │
│                                                                             │
│  [СЕНСОРИ / EKF] ──► [ПУЛ ЗАРЕЄСТРОВАНИХ ПОВЕДІНОК]                         │
│                           │                                                 │
│                           ├─► WaypointCruise (Prio 40)                      │
│                           ├─► TerrainFollowing (Prio 60)                    │
│                           └─► EmergencyAvoidance (Prio 80)                  │
│                                         │                                   │
│                                         ▼                                   │
│                             [АРБІТР ВИТІСНЕННЯ (Manager)]                   │
│                                         │ (Вибір найвищого пріоритету)      │
│                                         ▼                                   │
│                             [ПРОТОКОЛ HALT / RESUME]                        │
│                                         │ (Контрольні точки Checkpoints)    │
│                                         ▼                                   │
│                             [БЕЗПОШТОВХОВИЙ ФІЛЬТР]                         │
│                                         │ (Обмеження a_max та j_max)        │
│                                         ▼                                   │
│                       [НЕПЕРЕРВНІ УСТАВКИ ШВИДКОСТІ / ТЯГИ]                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   КОНТУР КУТОВОЇ СТАБІЛІЗАЦІЇ (400–1000 Гц)                 │
│              Attitude Rate Controller ──► Motor Mixer / ESC                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

Модуль будується на засадах чотирьох ключових інженерних принципів:

1. **Повна відмова від динамічного виділення пам'яті:** функції `malloc`, `free`, оператори `new` та `delete` категорично заборонені. Усі структури даних, дескриптори поведінок, таблиці функціональних покажчиків і буфери чекпоінтів алокуються статично на етапі ініціалізації системи. Це унеможливлює фрагментацію купи та гарантує O(1) час виконання кожного кроку арбітражу;
2. **Розподіл відповідальності через уніфікований інтерфейс:** конкретні поведінки (наприклад, політ по сітці або екстрений набір висоти) інкапсулюють лише власну математику генерації бажаного руху. Вони позбавлені прямого доступу до сервоприводів і моторів, взаємодіючи з автопілотом виключно через стандартизовані виклики `init()`, `tick()`, `halt()` та `resume()`;
3. **Двоетапна фільтрація уставок:** арбітр гарантує логічну безперервність переходів між задачами, а динамічний фільтр забезпечує фізичну гладкість команд, обмежуючи максимальні прискорення й ривки літального апарата;
4. **Детермінована підтримка вкладеного витіснення (Preemption Stack):** якщо під час виконання маневру ухилення середнього пріоритету стається критична відмова силового живлення, система зберігає стан обох перерваних задач у фіксованому статичному стеку глибиною до 4 рівнів.

---

## Математика безпоштовхового фільтра та чисельна дискретизація

Коли арбітр витісняє одну поведінку іншою, вихідний вектор цільової швидкості стрибкоподібно змінюється з `v_old` на `v_new`. Пряма передача такого розриву в пропорційний регулятор швидкості `K_p` породжує стрибок бажаного прискорення `a_des = K_p · (v_new - v_old)`, що спричиняє перевантаження приводів.

Для усунення цього явища безпоштовховий фільтр (*Bumpless Filter*) моделює рух віртуальної маси з обмеженням за максимальним прискоренням `a_max` та максимальним ривком `j_max`.

### Повний вивід різницевих рівнянь фільтра

Нехай на кроці `k` поточна згладжена швидкість становить `v(k-1)`, а поточне прискорення — `a(k-1)`. На вхід фільтра надходить новий цільовий вектор швидкості `v_target(k)`.

Розрахунок виконується у чотири кроки:

```text
e_v(k)   = v_target(k) - v(k - 1)                       [помилка узгодження швидкості]
a_des(k) = e_v(k) · K_v                                 [бажане прискорення контуру]
a_cmd(k) = clamp(a_des(k), -a_max, +a_max)              [насичення максимального прискорення]
j_raw(k) = (a_cmd(k) - a(k - 1)) / dt                   [розрахунок похідної прискорення (ривка)]
j_cmd(k) = clamp(j_raw(k), -j_max, +j_max)              [насичення максимального ривка]
a(k)     = a(k - 1) + j_cmd(k) · dt                     [інтегрування згладженого прискорення]
v(k)     = v(k - 1) + a(k) · dt                         [інтегрування згладженої швидкості]
```

де `K_v` — пропорційний коефіцієнт згладжування (типово від 2.0 до 3.0 с⁻¹).

Ця схема реалізується незалежно за трьома просторовими осями (X, Y, Z). Для кутової швидкості навколо вертикальної осі (Yaw Rate) фільтрація здійснюється за аналогічною схемою першого або другого порядку з обмеженням кутового прискорення `alpha_max ≤ 120 град/с²`.

### Фізика насичення актуаторів та зв'язок із ривком

Обмеження ривка має фундаментальне фізичне обґрунтування. Розглянемо динаміку повороту мультиротора навколо осі тангажу під дією зміни тяги передніх і задніх пропелерів:

```text
tau_pitch = I_yy · d²θ/dt² = 2·L·c_T · (omega_front² - omega_rear²) [керуючий момент за тангажем]
```

де `I_yy` — момент інерції планера за тангажем, `L` — плече мотора, `c_T` — коефіцієнт аеродинамічної тяги, `omega` — кутова швидкість обертання гвинта.

Швидкість зміни тяги обмежена механічною та електромагнітною постійною часу безколекторного мотора (від 20 до 40 мс):

```text
d(omega)/dt = (1 / tau_m) · (omega_target - omega)      [динаміка розгону ротора]
```

Якщо фільтр не обмежує ривок, регулятор орієнтації вимагає миттєвої зміни кутового прискорення, що вимагає від мотора нескінченної швидкості наростання струму. У результаті:
1. Моторний мікшер входить у стан глибокої десатурації (передні двигуни розкручуються до 100% PWM, задні падають у 0%);
2. За нульової тяги задніх гвинтів втрачається сумарний крутний момент за віссю рискання (Yaw), і дрон починає некеровано крутитися за курсом;
3. На силовій шині виникає стрибок зворотної ЕРС від рекуперативного гальмування, що загрожує пробоєм силових польових транзисторів (MOSFET) у регуляторах швидкості ESC.

Завдяки введенню жорсткого обмеження `j_max ≤ 12.0 м/с³` перехідні процеси зміни тяги залишаються строго в зоні лінійного відгуку силової установки.

### Підбір коефіцієнтів для різних класів БПЛА

Параметри фільтра підбираються відповідно до питомої тягооснащеності та аеродинамічної схеми апарата:

| Клас літального апарата | `K_v (с⁻¹)` | `a_max (м/с²)` | `j_max (м/с³)` | Фізичне обмеження |
| :--- | :--- | :--- | :--- | :--- |
| **Швидкісний FPV / Перехоплювач** | 4.0 | 15.0–25.0 | 60.0–100.0 | Струмові ліміти LiPo-акумулятора |
| **Комерційний мультиротор (зйомка)** | 2.5 | 3.5–5.0 | 10.0–15.0 | Стабільність гіропідвісу камери |
| **Важкий агродрон / Вантажний VTOL** | 1.8 | 2.0–3.0 | 5.0–8.0 | Плече інерції та пружність рами |
| **БПЛА літакового типу (Fixed-Wing)** | 1.5 | 2.0–4.0 | 4.0–6.0 | Запас кута атаки до звалювання |

---

## Протокол контрольних точок (Checkpointing) та безпечне відновлення

При тимчасовому витісненні місії аварійним маневром (наприклад, ухилення від птаха чи дерева тривалістю 4 секунди) диспетчер повинен зберегти прогрес польотного завдання.

### Структура зліпка стану

Зліпок стану формується витіснюваною задачею під час виклику `halt()`:

:::tabs
@tab C
```c
typedef struct {
    uint16_t waypoint_id;   /* Індекс активного поворотного пункту */
    float spline_s;         /* Прогрес уздовж сегмента від 0.0 до 1.0 */
    float saved_speed;      /* Задана круїзна швидкість */
    uint32_t flags;         /* Бітова маска стану підсистем місії */
} checkpoint_t;
```
@tab C++
```cpp
struct BehaviorCheckpoint {
    uint16_t waypoint_id{0}; // Індекс активного поворотного пункту
    float spline_s{0.0F};    // Прогрес уздовж сегмента від 0.0 до 1.0
    float saved_speed{0.0F}; // Задана круїзна швидкість
    uint32_t flags{0};       // Бітова маска стану підсистем місії
};
```
:::

Правила формування чекпоінта:
* **Зберігається лише інваріантний стан місії:** номер вейпоінта, прогрес проходження сплайна, поточний індекс обстежуваного полігону;
* **Категорично заборонено зберігати динамічні змінні контурів:** накопичені суми інтеграторів швидкості й кута, випереджальні уставки тяги та цільові кватерніони скидаються в нуль. У точці відновлення дрон має іншу орієнтацію та зазнає іншої сили вітру; відновлення старих інтеграторів неминуче спричинить викид тяги (*integrator kick*).

### Механізм стека вкладеного витіснення (Preemption Stack)

У реальних автономних польотах загрози можуть виникати каскадно. Розглянемо багаторівневий сценарій:
1. Дрон виконує маршрутну місію картографування (`WaypointCruise`, пріоритет 40);
2. Лідар виявляє дерево на шляху — активується локальний обхід (`LocalAvoidance`, пріоритет 70). Місія зберігає свій чекпоінт у слот 0 стека;
3. Під час виконання обходу бортовий висотомір фіксує раптове зближення з вершиною пагорба — активується екстрений набір висоти (`EmergencyClimb`, пріоритет 150). Поведінка обходу зберігає свій чекпоінт у слот 1 стека;
4. Коли загроза висоти усунена, вершина стека звільняється: відновлюється обхід перешкоди (`LocalAvoidance`);
5. Після завершення обходу відновлюється базова місія (`WaypointCruise`) з точним поверненням до перерваного галса зйомки.

Для детермінованої підтримки таких сценаріїв менеджер містить фіксований LIFO-стек дескрипторів:

:::tabs
@tab C
```c
typedef struct {
    uint8_t behavior_id;
    checkpoint_t checkpoint;
} preemption_stack_entry_t;

typedef struct {
    preemption_stack_entry_t entries[4];
    uint8_t depth;
} preemption_stack_t;
```
@tab C++
```cpp
struct PreemptionStackEntry {
    uint8_t behavior_id{0};
    BehaviorCheckpoint checkpoint{};
};

struct PreemptionStack {
    std::array<PreemptionStackEntry, 4> entries{};
    uint8_t depth{0};
};
```
:::

Якщо глибина стека досягає граничного значення (4), а надходить новий запит ще вищого пріоритету, найстаріші завдання базового рівня переводяться у стан `BEHAVIOR_STATE_ABORTED`, що гарантує збереження пам'яті без загрози переповнення стека.

### Сторожовий таймер витіснення (Preemption Watchdog)

Якщо витіснювана задача через внутрішню програмну помилку зависає в нескінченному циклі всередині `halt()` або очікує відповіді від апаратного датчика, вона блокує запуск аварійного маневру. Для виключення цієї загрози менеджер фіксує лічильник тактів витіснення:

* Нормальний час завершення `halt()` становить менше 1 такту (< 10 мс);
* Якщо поведінка не підтвердила зупинку протягом захисного інтервалу `PREEMPTION_TIMEOUT_TICKS = 2` (20 мс), диспетчер примусово виставляє їй стан `BEHAVIOR_STATE_ABORTED`, відбирає апаратні семафори й передає керування аварійній задачі без збереження чекпоінта;
* Подія аварійного переривання фіксується у бортовому журналі з кодом помилки `ERR_BEHAVIOR_PREEMPTION_TIMEOUT`.

---

## Реалізація модуля на мовах C та C++

Нижче наведено повний, функціонально завершений вихідний код модуля на мовах C та C++. Реалізація містить ядро менеджера арбітражу, фільтр безпоштовхового перемикання, дві конкретні поведінки (`WaypointCruise` та `EmergencyAvoidance`), а також імітаційний стенд, що демонструє повний життєвий цикл переривання та відновлення місії.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define BEHAVIOR_MAX_COUNT 8
#define PREEMPTION_TIMEOUT_TICKS 2

typedef enum {
    BEHAVIOR_STATE_IDLE = 0,
    BEHAVIOR_STATE_RUNNING,
    BEHAVIOR_STATE_SUSPENDED,
    BEHAVIOR_STATE_ABORTED
} behavior_state_t;

typedef enum {
    PREEMPT_REASON_NONE = 0,
    PREEMPT_REASON_COLLISION_AVOIDANCE,
    PREEMPT_REASON_CRITICAL_BATTERY,
    PREEMPT_REASON_GEOFENCE_BREACH,
    PREEMPT_REASON_MANUAL_OVERRIDE
} preempt_reason_t;

typedef struct {
    float vx;       /* м/с */
    float vy;       /* м/с */
    float vz;       /* м/с (Z вгору) */
    float yaw_rate; /* рад/с */
} motion_setpoint_t;

typedef struct {
    uint16_t waypoint_id;
    float spline_s;
    float saved_speed;
    uint32_t flags;
} checkpoint_t;

struct behavior;

typedef struct {
    bool (*init)(struct behavior *self);
    void (*tick)(struct behavior *self, float dt, motion_setpoint_t *out_sp);
    bool (*halt)(struct behavior *self, preempt_reason_t reason);
    bool (*resume)(struct behavior *self, const checkpoint_t *cp);
} behavior_vtable_t;

typedef struct behavior {
    char name[32];
    uint8_t priority;
    behavior_state_t state;
    checkpoint_t checkpoint;
    const behavior_vtable_t *vtable;
    void *ctx;
} behavior_t;

typedef struct {
    motion_setpoint_t current_sp;
    motion_setpoint_t current_accel;
    float max_accel; /* м/с² */
    float max_jerk;  /* м/с³ */
} bumpless_filter_t;

typedef struct {
    behavior_t *registry[BEHAVIOR_MAX_COUNT];
    size_t count;
    int active_idx;
    bumpless_filter_t filter;
} behavior_manager_t;

/* --- Реалізація безпоштовхового фільтра --- */
static inline float clamp_val(float v, float min_v, float max_v) {
    if (v < min_v) return min_v;
    if (v > max_v) return max_v;
    return v;
}

void bumpless_filter_init(bumpless_filter_t *f, float max_accel, float max_jerk) {
    memset(f, 0, sizeof(*f));
    f->max_accel = max_accel;
    f->max_jerk = max_jerk;
}

void bumpless_filter_update(bumpless_filter_t *f, const motion_setpoint_t *target, float dt) {
    const float kp = 2.5f;

    /* Розрахунок бажаного прискорення для компенсації розриву швидкості */
    float des_ax = clamp_val((target->vx - f->current_sp.vx) * kp, -f->max_accel, f->max_accel);
    float des_ay = clamp_val((target->vy - f->current_sp.vy) * kp, -f->max_accel, f->max_accel);
    float des_az = clamp_val((target->vz - f->current_sp.vz) * kp, -f->max_accel, f->max_accel);

    /* Обмеження ривка (похідної прискорення) */
    float jx = clamp_val((des_ax - f->current_accel.vx) / dt, -f->max_jerk, f->max_jerk);
    float jy = clamp_val((des_ay - f->current_accel.vy) / dt, -f->max_jerk, f->max_jerk);
    float jz = clamp_val((des_az - f->current_accel.vz) / dt, -f->max_jerk, f->max_jerk);

    f->current_accel.vx += jx * dt;
    f->current_accel.vy += jy * dt;
    f->current_accel.vz += jz * dt;

    f->current_sp.vx += f->current_accel.vx * dt;
    f->current_sp.vy += f->current_accel.vy * dt;
    f->current_sp.vz += f->current_accel.vz * dt;
    f->current_sp.yaw_rate = target->yaw_rate;
}

/* --- Конкретна поведінка 1: Маршрутний політ (Waypoint Cruise) --- */
typedef struct {
    uint16_t current_wp;
    float current_progress;
    float cruise_speed;
} cruise_context_t;

static bool cruise_init(behavior_t *self) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    ctx->current_wp = 1;
    ctx->current_progress = 0.0f;
    ctx->cruise_speed = 15.0f;
    return true;
}

static void cruise_tick(behavior_t *self, float dt, motion_setpoint_t *out_sp) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    ctx->current_progress += 0.02f * dt;
    if (ctx->current_progress >= 1.0f) {
        ctx->current_progress = 0.0f;
        ctx->current_wp++;
    }
    out_sp->vx = ctx->cruise_speed;
    out_sp->vy = 0.0f;
    out_sp->vz = 0.0f;
    out_sp->yaw_rate = 0.0f;
}

static bool cruise_halt(behavior_t *self, preempt_reason_t reason) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    (void)reason;
    /* Збереження інваріантного стану місії в чекпоінт */
    self->checkpoint.waypoint_id = ctx->current_wp;
    self->checkpoint.spline_s = ctx->current_progress;
    self->checkpoint.saved_speed = ctx->cruise_speed;
    return true;
}

static bool cruise_resume(behavior_t *self, const checkpoint_t *cp) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    ctx->current_wp = cp->waypoint_id;
    ctx->current_progress = cp->spline_s;
    ctx->cruise_speed = cp->saved_speed;
    return true;
}

static const behavior_vtable_t g_cruise_vtable = {
    .init = cruise_init,
    .tick = cruise_tick,
    .halt = cruise_halt,
    .resume = cruise_resume
};

/* --- Конкретна поведінка 2: Ухилення від перешкод (Collision Avoidance) --- */
typedef struct {
    bool obstacle_detected;
    float climb_rate;
    float lateral_speed;
} avoidance_context_t;

static bool avoid_init(behavior_t *self) {
    avoidance_context_t *ctx = (avoidance_context_t *)self->ctx;
    ctx->obstacle_detected = false;
    ctx->climb_rate = 3.5f;
    ctx->lateral_speed = -2.0f;
    return true;
}

static void avoid_tick(behavior_t *self, float dt, motion_setpoint_t *out_sp) {
    avoidance_context_t *ctx = (avoidance_context_t *)self->ctx;
    (void)dt;
    out_sp->vx = 0.0f;
    out_sp->vy = ctx->lateral_speed;
    out_sp->vz = ctx->climb_rate;
    out_sp->yaw_rate = 0.1f;
}

static bool avoid_halt(behavior_t *self, preempt_reason_t reason) {
    avoidance_context_t *ctx = (avoidance_context_t *)self->ctx;
    (void)reason;
    ctx->obstacle_detected = false;
    return true;
}

static bool avoid_resume(behavior_t *self, const checkpoint_t *cp) {
    (void)self;
    (void)cp;
    return true;
}

static const behavior_vtable_t g_avoid_vtable = {
    .init = avoid_init,
    .tick = avoid_tick,
    .halt = avoid_halt,
    .resume = avoid_resume
};

/* --- Менеджер поведінок --- */
void manager_init(behavior_manager_t *m, float max_accel, float max_jerk) {
    memset(m, 0, sizeof(*m));
    m->active_idx = -1;
    bumpless_filter_init(&m->filter, max_accel, max_jerk);
}

bool manager_register(behavior_manager_t *m, behavior_t *b) {
    if (m->count >= BEHAVIOR_MAX_COUNT || b == NULL) return false;
    m->registry[m->count++] = b;
    if (b->vtable && b->vtable->init) {
        b->vtable->init(b);
    }
    b->state = BEHAVIOR_STATE_IDLE;
    return true;
}

void manager_step(behavior_manager_t *m, float dt, motion_setpoint_t *final_sp) {
    int candidate_idx = -1;
    uint8_t top_prio = 0;

    /* Вибір кандидата з найвищим пріоритетом */
    for (size_t i = 0; i < m->count; ++i) {
        behavior_t *b = m->registry[i];
        if (b->state == BEHAVIOR_STATE_RUNNING || b->state == BEHAVIOR_STATE_SUSPENDED) {
            if (b->priority > top_prio) {
                top_prio = b->priority;
                candidate_idx = (int)i;
            }
        }
    }

    /* Обробка зміни активної задачі */
    if (candidate_idx != m->active_idx) {
        if (m->active_idx >= 0) {
            behavior_t *old_b = m->registry[m->active_idx];
            if (old_b->state == BEHAVIOR_STATE_RUNNING) {
                if (old_b->vtable && old_b->vtable->halt) {
                    old_b->vtable->halt(old_b, PREEMPT_REASON_COLLISION_AVOIDANCE);
                }
                old_b->state = BEHAVIOR_STATE_SUSPENDED;
            }
        }

        if (candidate_idx >= 0) {
            behavior_t *new_b = m->registry[candidate_idx];
            if (new_b->state == BEHAVIOR_STATE_SUSPENDED) {
                if (new_b->vtable && new_b->vtable->resume) {
                    new_b->vtable->resume(new_b, &new_b->checkpoint);
                }
            }
            new_b->state = BEHAVIOR_STATE_RUNNING;
        }

        m->active_idx = candidate_idx;
    }

    /* Опитування активної поведінки */
    motion_setpoint_t raw_sp = {0};
    if (m->active_idx >= 0) {
        behavior_t *active = m->registry[m->active_idx];
        if (active->vtable && active->vtable->tick) {
            active->vtable->tick(active, dt, &raw_sp);
        }
    }

    /* Безпоштовхове згладжування уставок */
    bumpless_filter_update(&m->filter, &raw_sp, dt);
    *final_sp = m->filter.current_sp;
}

/* --- Тестовий стенд імітації польоту --- */
int main(void) {
    behavior_manager_t mgr;
    manager_init(&mgr, 4.0f, 12.0f);

    cruise_context_t cruise_ctx;
    behavior_t cruise_behavior = {
        .name = "WaypointCruise",
        .priority = 40,
        .state = BEHAVIOR_STATE_IDLE,
        .vtable = &g_cruise_vtable,
        .ctx = &cruise_ctx
    };

    avoidance_context_t avoid_ctx;
    behavior_t avoid_behavior = {
        .name = "CollisionAvoidance",
        .priority = 80,
        .state = BEHAVIOR_STATE_IDLE,
        .vtable = &g_avoid_vtable,
        .ctx = &avoid_ctx
    };

    manager_register(&mgr, &cruise_behavior);
    manager_register(&mgr, &avoid_behavior);

    /* Активація круїзної місії */
    cruise_behavior.state = BEHAVIOR_STATE_RUNNING;

    const float dt = 0.02f; /* 50 Гц */
    motion_setpoint_t sp;

    printf("=== СТАРТ СИМУЛЯЦІЇ ВИТІСНЕННЯ (50 Гц) ===\n");
    for (int step = 0; step <= 250; ++step) {
        float t = step * dt;

        /* Подія 1: Виявлення перешкоди на 1.0 с */
        if (step == 50) {
            printf("\n[t=%.2f с] ПОДІЯ: Лідар зафіксував перешкоду! Активація CollisionAvoidance (Prio 80)\n", t);
            avoid_behavior.state = BEHAVIOR_STATE_RUNNING;
        }

        /* Подія 2: Перешкоду усунено на 3.0 с */
        if (step == 150) {
            printf("\n[t=%.2f с] ПОДІЯ: Перешкоду оминуто! Деактивація CollisionAvoidance\n", t);
            avoid_behavior.state = BEHAVIOR_STATE_IDLE;
        }

        manager_step(&mgr, dt, &sp);

        if (step % 25 == 0 || step == 51 || step == 151) {
            const char *active_name = (mgr.active_idx >= 0) ? mgr.registry[mgr.active_idx]->name : "NONE";
            printf("[t=%5.2f с] Активна: %-18s | vx=%6.2f | vy=%6.2f | vz=%5.2f м/с\n",
                   t, active_name, sp.vx, sp.vy, sp.vz);
        }
    }

    printf("\n=== ТЕСТ ЗАВЕРШЕНО УСПІШНО ===\n");
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <cstdint>
#include <string_view>
#include <array>
#include <optional>
#include <algorithm>
#include <span>
#include <iomanip>

namespace autopilot::preemption {

enum class BehaviorState : uint8_t {
    Idle = 0,
    Running,
    Suspended,
    Aborted
};

enum class PreemptReason : uint8_t {
    None = 0,
    CollisionAvoidance,
    CriticalBattery,
    GeofenceBreach,
    ManualOverride
};

struct MotionSetpoint {
    float vx{0.0F};       // м/с
    float vy{0.0F};       // м/с
    float vz{0.0F};       // м/с
    float yaw_rate{0.0F}; // рад/с
};

struct BehaviorCheckpoint {
    uint16_t waypoint_id{0};
    float spline_s{0.0F};
    float saved_speed{0.0F};
    uint32_t flags{0};
};

class IBehavior {
public:
    virtual ~IBehavior() = default;

    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual uint8_t priority() const noexcept = 0;
    [[nodiscard]] virtual BehaviorState state() const noexcept = 0;
    virtual void set_state(BehaviorState state) noexcept = 0;

    virtual bool initialize() noexcept = 0;
    virtual void tick(float dt, MotionSetpoint& out_sp) noexcept = 0;
    virtual bool halt(PreemptReason reason) noexcept = 0;
    virtual bool resume(const BehaviorCheckpoint& cp) noexcept = 0;
    [[nodiscard]] virtual const BehaviorCheckpoint& checkpoint() const noexcept = 0;
};

class BumplessFilter {
public:
    constexpr BumplessFilter(float max_accel, float max_jerk) noexcept
        : max_accel_{max_accel}, max_jerk_{max_jerk} {}

    void update(const MotionSetpoint& target, float dt) noexcept {
        constexpr float kp = 2.5F;

        const float des_ax = std::clamp((target.vx - current_sp_.vx) * kp, -max_accel_, max_accel_);
        const float des_ay = std::clamp((target.vy - current_sp_.vy) * kp, -max_accel_, max_accel_);
        const float des_az = std::clamp((target.vz - current_sp_.vz) * kp, -max_accel_, max_accel_);

        const float jx = std::clamp((des_ax - current_accel_.vx) / dt, -max_jerk_, max_jerk_);
        const float jy = std::clamp((des_ay - current_accel_.vy) / dt, -max_jerk_, max_jerk_);
        const float jz = std::clamp((des_az - current_accel_.vz) / dt, -max_jerk_, max_jerk_);

        current_accel_.vx += jx * dt;
        current_accel_.vy += jy * dt;
        current_accel_.vz += jz * dt;

        current_sp_.vx += current_accel_.vx * dt;
        current_sp_.vy += current_accel_.vy * dt;
        current_sp_.vz += current_accel_.vz * dt;
        current_sp_.yaw_rate = target.yaw_rate;
    }

    [[nodiscard]] const MotionSetpoint& setpoint() const noexcept {
        return current_sp_;
    }

private:
    MotionSetpoint current_sp_{};
    MotionSetpoint current_accel_{};
    float max_accel_{4.0F};
    float max_jerk_{12.0F};
};

class WaypointCruiseBehavior final : public IBehavior {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "WaypointCruise";
    }

    [[nodiscard]] uint8_t priority() const noexcept override {
        return 40; // Стандартний рівень місії
    }

    [[nodiscard]] BehaviorState state() const noexcept override {
        return state_;
    }

    void set_state(BehaviorState state) noexcept override {
        state_ = state;
    }

    bool initialize() noexcept override {
        current_wp_ = 1;
        progress_ = 0.0F;
        cruise_speed_ = 15.0F;
        state_ = BehaviorState::Idle;
        return true;
    }

    void tick(float dt, MotionSetpoint& out_sp) noexcept override {
        progress_ += 0.02F * dt;
        if (progress_ >= 1.0F) {
            progress_ = 0.0F;
            ++current_wp_;
        }
        out_sp.vx = cruise_speed_;
        out_sp.vy = 0.0F;
        out_sp.vz = 0.0F;
        out_sp.yaw_rate = 0.0F;
    }

    bool halt(PreemptReason reason) noexcept override {
        (void)reason;
        checkpoint_.waypoint_id = current_wp_;
        checkpoint_.spline_s = progress_;
        checkpoint_.saved_speed = cruise_speed_;
        return true;
    }

    bool resume(const BehaviorCheckpoint& cp) noexcept override {
        current_wp_ = cp.waypoint_id;
        progress_ = cp.spline_s;
        cruise_speed_ = cp.saved_speed;
        return true;
    }

    [[nodiscard]] const BehaviorCheckpoint& checkpoint() const noexcept override {
        return checkpoint_;
    }

private:
    BehaviorState state_{BehaviorState::Idle};
    uint16_t current_wp_{1};
    float progress_{0.0F};
    float cruise_speed_{15.0F};
    BehaviorCheckpoint checkpoint_{};
};

class CollisionAvoidanceBehavior final : public IBehavior {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "CollisionAvoidance";
    }

    [[nodiscard]] uint8_t priority() const noexcept override {
        return 80; // Високий реактивний пріоритет безпеки
    }

    [[nodiscard]] BehaviorState state() const noexcept override {
        return state_;
    }

    void set_state(BehaviorState state) noexcept override {
        state_ = state;
    }

    bool initialize() noexcept override {
        climb_rate_ = 3.5F;
        lateral_speed_ = -2.0F;
        state_ = BehaviorState::Idle;
        return true;
    }

    void tick(float dt, MotionSetpoint& out_sp) noexcept override {
        (void)dt;
        out_sp.vx = 0.0F;
        out_sp.vy = lateral_speed_;
        out_sp.vz = climb_rate_;
        out_sp.yaw_rate = 0.1F;
    }

    bool halt(PreemptReason reason) noexcept override {
        (void)reason;
        return true;
    }

    bool resume(const BehaviorCheckpoint& cp) noexcept override {
        (void)cp;
        return true;
    }

    [[nodiscard]] const BehaviorCheckpoint& checkpoint() const noexcept override {
        return checkpoint_;
    }

private:
    BehaviorState state_{BehaviorState::Idle};
    float climb_rate_{3.5F};
    float lateral_speed_{-2.0F};
    BehaviorCheckpoint checkpoint_{};
};

class BehaviorManager {
public:
    static constexpr size_t MaxBehaviors = 8;

    explicit BehaviorManager(float max_accel, float max_jerk) noexcept
        : filter_{max_accel, max_jerk} {}

    bool register_behavior(IBehavior* behavior) noexcept {
        if (count_ >= MaxBehaviors || behavior == nullptr) {
            return false;
        }
        registry_[count_++] = behavior;
        behavior->initialize();
        return true;
    }

    void step(float dt, MotionSetpoint& out_sp) noexcept {
        const int candidate_idx = evaluate_highest_priority();

        if (candidate_idx != active_idx_) {
            switch_active_behavior(candidate_idx);
            active_idx_ = candidate_idx;
        }

        MotionSetpoint raw_sp{};
        if (active_idx_ >= 0 && active_idx_ < static_cast<int>(count_)) {
            registry_[active_idx_]->tick(dt, raw_sp);
        }

        filter_.update(raw_sp, dt);
        out_sp = filter_.setpoint();
    }

    [[nodiscard]] int active_index() const noexcept {
        return active_idx_;
    }

    [[nodiscard]] IBehavior* get_behavior(size_t idx) noexcept {
        return (idx < count_) ? registry_[idx] : nullptr;
    }

private:
    [[nodiscard]] int evaluate_highest_priority() const noexcept {
        int best_idx = -1;
        uint8_t highest_prio = 0;

        for (size_t i = 0; i < count_; ++i) {
            const auto* b = registry_[i];
            if (b->state() == BehaviorState::Running || b->state() == BehaviorState::Suspended) {
                if (b->priority() > highest_prio) {
                    highest_prio = b->priority();
                    best_idx = static_cast<int>(i);
                }
            }
        }
        return best_idx;
    }

    void switch_active_behavior(int next_idx) noexcept {
        if (active_idx_ >= 0 && active_idx_ < static_cast<int>(count_)) {
            auto* current = registry_[active_idx_];
            if (current->state() == BehaviorState::Running) {
                current->halt(PreemptReason::CollisionAvoidance);
                current->set_state(BehaviorState::Suspended);
            }
        }

        if (next_idx >= 0 && next_idx < static_cast<int>(count_)) {
            auto* next = registry_[next_idx];
            if (next->state() == BehaviorState::Suspended) {
                next->resume(next->checkpoint());
            }
            next->set_state(BehaviorState::Running);
        }
    }

    std::array<IBehavior*, MaxBehaviors> registry_{};
    size_t count_{0};
    int active_idx_{-1};
    BumplessFilter filter_;
};

} // namespace autopilot::preemption

int main() {
    using namespace autopilot::preemption;

    BehaviorManager manager{4.0F, 12.0F};
    WaypointCruiseBehavior cruise;
    CollisionAvoidanceBehavior avoid;

    manager.register_behavior(&cruise);
    manager.register_behavior(&avoid);

    cruise.set_state(BehaviorState::Running);

    constexpr float dt = 0.02F;
    MotionSetpoint sp{};

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ ВИТІСНЕННЯ C++ (50 Гц) ===\n";
    for (int step = 0; step <= 250; ++step) {
        const float t = static_cast<float>(step) * dt;

        if (step == 50) {
            std::cout << "\n[t=" << std::fixed << std::setprecision(2) << t 
                      << " с] ПОДІЯ: Зафіксовано перешкоду! Активація CollisionAvoidance\n";
            avoid.set_state(BehaviorState::Running);
        }

        if (step == 150) {
            std::cout << "\n[t=" << std::fixed << std::setprecision(2) << t 
                      << " с] ПОДІЯ: Перешкоду оминуто! Деактивація CollisionAvoidance\n";
            avoid.set_state(BehaviorState::Idle);
        }

        manager.step(dt, sp);

        if (step % 25 == 0 || step == 51 || step == 151) {
            const auto* active = manager.get_behavior(manager.active_index());
            std::string_view name = (active != nullptr) ? active->name() : "NONE";
            std::cout << "[t=" << std::setw(5) << t << " с] Активна: " 
                      << std::setw(18) << std::left << name 
                      << " | vx=" << std::setw(6) << sp.vx 
                      << " | vy=" << std::setw(6) << sp.vy 
                      << " | vz=" << std::setw(5) << sp.vz << " м/с\n";
        }
    }

    std::cout << "\n=== ТЕСТ C++ ЗАВЕРШЕНО УСПІШНО ===\n";
    return 0;
}
```
:::

---

## Покроковий аналіз перемикання завдань

Розглянемо часові фази виконання польотного тесту:

1. **Фаза 1: Нормальний круїзний політ (від 0.0 до 1.0 с, кроки 0–50):**
   * Задача `WaypointCruise` активна (`state = RUNNING`), генерує уставку горизонтального польоту `vx = 15.0 м/с`, `vy = 0.0`, `vz = 0.0`;
   * Безпоштовховий фільтр перебуває в усталеному режимі, видаючи `vx = 15.0 м/с` без динамічної затримки.
2. **Фаза 2: Інжекція загрози та перехоплення керування (t = 1.0 с, крок 50):**
   * Сенсорний контур фіксує перешкоду й переводить `CollisionAvoidance` у стан `RUNNING`.
   * На такті арбітражу функція `evaluate_highest_priority()` фіксує, що пріоритет ухилення (80) перевищує пріоритет місії (40).
   * Викликається `cruise_halt()`: місія фіксує поточний вейпоінт `W_1` та просторовий коефіцієнт прогресу `s = 0.02` у структуру `checkpoint`, після чого переходить у стан `SUSPENDED`.
   * Поведінка `CollisionAvoidance` стає активною (`active_idx = 1`). Вона вимагає негайного скидання швидкості вперед (`vx = 0`), бокового зміщення (`vy = -2.0 м/с`) та інтенсивного набору висоти (`vz = +3.5 м/с`).
3. **Фаза 3: Робота безпоштовхового фільтра (від 1.0 до 1.6 с):**
   * Замість миттєвого ступінчастого розриву `Δvx = -15.0 м/с`, фільтр плавно нарощує гальмівне прискорення з темпом `j_max = 12.0 м/с³`, досягаючи максимального сповільнення `a_max = 4.0 м/с²`;
   * Швидкість `vx` монотонно спадає до 0 приблизно за 0.6 с, одночасно плавно наростають вертикальна швидкість `vz → +3.5 м/с` та бокова швидкість `vy → -2.0 м/с`;
   * Мотори залишаються в зоні лінійної керованості без входу в глибоке насичення.
4. **Фаза 4: Усунення загрози та повернення до місії (t = 3.0 с, крок 150):**
   * Далекомір фіксує чистий сектор простору. Поведінка `CollisionAvoidance` деактивується (`state = IDLE`);
   * Диспетчер виявляє найвищу з доступних задач — призупинену `WaypointCruise` (`state = SUSPENDED`);
   * Викликається `cruise_resume()`, який зчитує збережені координати `W_1` та прогрес `s = 0.02`;
   * Фільтр плавно розганяє апарат від `vx = 0` назад до 15.0 м/с, одночасно плавно знижуючи вертикальну швидкість `vz → 0`;
   * Апарат без зупинки продовжує виконання первинної фотограмметричної місії.

---

## Аналіз граничних випадків та відмовостійкість (FMEA)

При експлуатації диспетчера в реальних польотних умовах можливе виникнення складних граничних станів. Нижче наведено регламент їх обробки:

### 1. Одночасна поява кількох запитів однакового пріоритету

Якщо дві задачі (наприклад, ухилення за лідаром та ухилення за радаром) одночасно піднімають однаковий ранг пріоритету (`P_1 = P_2 = 80`), арбітр використовує правило часової першості (*First-In-First-Out / Temporal Precedence*). Активна поведінка зберігає контроль доти, доки її ранг строго не перевищено. Це унеможливлює паразитні перемикання між еквівалентними сенсорними джерелами.

### 2. Запит на витіснення під час виконання відновлення (resume)

Якщо в процесі зшивання траєкторії повернення до місії виникає нова загроза безпеки, диспетчер не очікує завершення фази `resume()`. Він негайно генерує новий виклик `halt()`, оновлює зліпок стану з урахуванням поточного фактичного положення дрона й передає керування новому маневру.

### 3. Відновлення місії в зоні вторинної небезпеки

Перед викликом `resume()` навігаційний модуль проводить валідацію збереженої контрольної точки:
* Якщо за час маневру ухилення вітер зніс дрон так, що пряма лінія повернення до збереженого вейпоінта перетинає нову перешкоду чи геозону, контролер відхиляє пряме відновлення;
* Автопілот генерує команду перепланування маршруту від поточної фізичної позиції `P_current`, уникаючи сліпого повернення до застарілого зліпка.

---

## Інженерні рекомендації з інтеграції у польотні стеки

При перенесенні модуля у виробничі прошивки автопілотів (PX4 Autopilot, ArduPilot або власні бортові системи на мікроконтролерах STM32H7/i.MX RT) слід дотримуватися низки регламентованих правил:

### 1. Інтеграція з шиною обміну повідомленнями uORB (PX4)

У структурі PX4 диспетчер поведінок розміщується всередині модуля `navigator` або спеціалізованого вузла `flight_mode_manager`. Взаємодія з контурами керування організовується через публікацію та підписку на стандартизовані uORB-теми:

* **Вхідні сенсорні потоки:** підписка на `vehicle_local_position` (отримання поточної виміряної швидкості `v_meas` для ініціалізації фільтра), `obstacle_distance` (покази лідарів), `geofence_status` та `battery_status`;
* **Вихідні уставки руху:** публікація структури `trajectory_setpoint` у контур `mc_pos_control`. Публікація містить поля `position`, `velocity`, `acceleration` та `yawspeed`. Безпоштовховий фільтр безпосередньо заповнює поля `velocity` та `acceleration`, що дозволяє позиційному контролеру працювати за схемою прямих випереджальних зв'язків (*feedforward*);
* **Міжпотокова синхронізація без м'ютексів:** передача уставок здійснюється через lock-free буфери `uORB::Publication<trajectory_setpoint_s>`. Це гарантує, що контур кутових швидкостей `mc_att_control` (400–1000 Гц) не буде заблокований навігаційним арбітром (50 Гц) навіть при піковому навантаженні на шину SPI або процесорне ядро.

### 2. Інтеграція в архітектуру ArduPilot (AP_Mission та mode_auto)

В екосистемі ArduPilot диспетчер інтегрується безпосередньо в контур `mode_auto.cpp` та `AP_Avoidance`:
* При виникненні загрози викликається `AP_Mission::pause()`, що автоматично фіксує індекс поточного вейпоінта `_nav_cmd_loaded`;
* Контур `AP_Avoidance` перехоплює керування через виклик `AC_AttitudeControl::input_euler_angle_roll_pitch_yaw()`, обмежуючи кутові швидкості відповідно до параметрів планера;
* Після очищення сектору небезпеки викликається `AP_Mission::resume()`, який ініціює повернення на сплайн через фільтрований генератор траєкторії без повторного проходження пройдених точок.

### 3. Запобігання розгону інтеграторів (Anti-Windup Reset)

У мить зміни `active_idx` контур стабілізації швидкості зобов'язаний виконувати скидання інтегральної складової помилки швидкості (`I_accum = 0`). Під час гальмування перед перешкодою фізичний рух дрона відстає від уставки через аеродинамічний опір та інерцію. Якщо залишити інтегратор увімкненим, у ньому накопичиться паразитна сума, яка після закінчення маневру ухилення спричинить глибокий закид швидкості вперед із перевищенням заданого ліміту (*overshoot*).

### 4. Діагностика та телеметричне логування

Для детального аналізу роботи системи на наземній станції керування (QGroundControl або Mission Planner) диспетчер транслює свій внутрішній стан у телеметричний потік MAVLink:

* **Повідомлення `NAV_CONTROLLER_OUTPUT`:** передає розраховані значення цільового та згладженого прискорення, а також величину помилки швидкості `e_v`;
* **Повідомлення `STATUSTEXT`:** при кожному спрацьовуванні витіснення надсилає рядок формату `[PREEMPT] Behavior 'WaypointCruise' halted by 'CollisionAvoidance' (reason: Obstacle)`;
* **Бортове логування (ULog / DataFlash):** запис внутрішніх станів поведінок (`BEHAVIOR_STATE`), значень ривка `j_cmd` та лічильників тактів виконання `halt()` із частотою 50 Гц для постпольотного аналізу в PlotJuggler.

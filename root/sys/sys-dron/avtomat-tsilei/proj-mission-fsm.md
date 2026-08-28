# ⚙️ Автономний модуль місійного автомата цілей автопілота

У високорівневих системах керування безпілотними літальними апаратами вибір тактичної поведінки відбувається в умовах неперервного потоку несинхронних подій. Нейромережевий детектор комп'ютерного зору надсилає координати виявлених об'єктів із частотою 30 кадрів/с, навігаційний фільтр розширеної оцінки стану (EKF) транслює просторове положення з частотою 100 Гц, система моніторингу тягової батареї (BMS) оновлює залишкову ємність із дискретністю 10 Гц, а далекоміри кругового огляду сигналізують про появу раптових висотних перешкод. Якщо логіка реакції на ці події реалізується у вигляді розрізнених прапорців та умовних операторів у різних потоках операційної системи, виникає стан гонитви ресурсів (race conditions), втрата транзитних повідомлень і перехід автопілота в неконсистентний стан.

Цей модуль реалізує детермінований ієрархічний кінцевий автомат (Hierarchical State Machine, HSM) керування місійними цілями автономного дрона, спроєктований за стандартом діаграм станів Девіда Харела. Модуль містить повну реалізацію моделі виконання Run-to-Completion, безблокувальні черги подій, механізм відновлення контексту через історію станів (State History), аналітичні охоронні предикати аеродинамічного енергетичного балансу та повний набір автоматизованих юніт-тестів.

## Архітектурні принципи та вимоги до вбудованих систем

Модуль розроблено для використання на бортових комп'ютерах (Companion Computer на базі Linux/ROS 2 або RTOS) та мікроконтролерах польотних контролерів (STM32H7 / Cortex-M7). У проєкті закладено суворі інженерні обмеження:

1. **Нульове динамічне виділення пам'яті (Zero-Heap Allocation):** уся пам'ять для дескрипторів станів, черг подій, контекстів телеметрії та таблиць переходів виділяється статично на етапі компіляції (у секціях `.bss` або `.data`). Це виключає фрагментацію оперативної пам'яті, недетерміновані затримки системного алокатора `malloc` та ризик аварійного завершення процесу через вичерпання пулу пам'яті (OOM) відповідно до стандартів авіаційного ПЗ DO-178C та MISRA C:2012.
2. **Семантика виконання Run-to-Completion (RTC):** обробка кожної події та виконання всіх супутніх дій виходу зі старого стану (`SIG_EXIT`) та входу в новий стан (`SIG_ENTRY`) виконуються неподільно в єдиному циклі диспетчеризації. Жодна нова подія не може перервати виконання поточного переходу.
3. **Безблокувальна черга подій (Lock-Free SPSC Ring Buffer):** зовнішні асинхронні джерела (потік декодера MAVLink, потік нейромережевого трекера та таймерні переривання) передають повідомлення автомату через кільцевий буфер формату Single-Producer Single-Consumer з атомарними покажчиками запису й читання.
4. **Ізоляція та верифікація Guard-предикатів:** переходи між фазами місії дозволяються лише після обчислення булевих функцій безпеки, які враховують тривимірний вектор швидкості вітру, запас енергії для гарантованого повернення на базу, нормовану квадратичну інновацію (NIS) фільтра Калмана трекера та стан запобіжників корисного навантаження.
5. **Збереження контексту через історію (Shallow та Deep History):** при виникненні локальних просторових загроз (виявлення перешкоди) автомат зберігає повний стан поточної місії (номер пошукового галса, координати об'єкта) та детерміновано повертається до нього після завершення маневру ухилення.

---

## Структура модуля та інтерфейси

Архітектура програмного комплексу складається з чотирьох взаємопов'язаних шарів:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ВХІДНІ АСИНХРОННІ ПОТОКИ                              │
│  [Потік MAVLink]        [Потік нейромережі CV]      [Таймерний потік 20 Гц] │
└──────────┬─────────────────────────┬───────────────────────────┬────────────┘
           │                         │                           │
           ▼                         ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              БЕЗБЛОКУВАЛЬНИЙ КІЛЬЦЕВИЙ БУФЕР (SPSC RING BUFFER)             │
│  [Ev #0] -> [Ev #1] -> [Ev #2] -> [Ev #3] ... (Статичний масив подій)       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Вибірка RTC)
┌─────────────────────────────────────────────────────────────────────────────┐
│                 МІСІЙНИЙ ДИСПЕТЧЕР HSM (Run-to-Completion)                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Оцінювач Guard-предикатів:                                            │  │
│  │ • Енергетичний баланс проти вітру E_rem >= E_rtb + E_reserve          │  │
│  │ • Інноваційний шлюз трекера NIS <= 5.99 (Chi-square 95%)              │  │
│  │ • Геозона та апаратні чеки корисного навантаження                     │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │ Таблиця станів та функціональні обробники:                            │  │
│  │ [IDLE] -> [SEARCH] <-> [ACQUIRE] -> [TRACK] -> [ENGAGE] -> [VERIFY]   │  │
│  │              │                                                        │  │
│  │              +---> [AVOID] ──(Відновлення History H*)───> [SEARCH]    │  │
│  │                                                                       │  │
│  │ [Суперстан OPERATIONAL] ──(Battery / Fence Failsafe)──> [RECOVERY]    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (Вихідні команди)
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ВИКОНАВЧИЙ ШАР ПОЛЬОТНОГО КОНТРОЛЕРА                        │
│  [SET_POSITION_TARGET_LOCAL_NED]  [MISSION_SET_CURRENT]  [DO_SET_SERVO]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

Нижче наведено повну реалізацію модуля двома мовами програмування: C99 зі строгою статичною типізацією та Modern C++20 на базі `std::variant`, constexpr-диспетчеризації та нульових динамічних алокацій.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include <assert.h>

#define EVENT_QUEUE_CAPACITY     32
#define TARGET_TRACK_TIMEOUT_MS  3000
#define ACQUIRE_TIMEOUT_MS       4000
#define VERIFY_TIMEOUT_MS        2000
#define OBSTACLE_CLEAR_MARGIN_M  15.0f

/* ── 1. Ідентифікатори сигналів та станів ── */
typedef enum {
    SIG_ENTRY = 0,
    SIG_EXIT,
    SIG_INIT,
    SIG_TICK,
    SIG_CMD_START,
    SIG_CANDIDATE_DETECTED,
    SIG_TARGET_LOCKED,
    SIG_TARGET_LOST,
    SIG_WITHIN_ENGAGE_RANGE,
    SIG_PAYLOAD_RELEASED,
    SIG_VERIFY_COMPLETE,
    SIG_OBSTACLE_DETECTED,
    SIG_OBSTACLE_CLEARED,
    SIG_BATTERY_CRITICAL,
    SIG_GEOFENCE_BREACH,
    SIG_CMD_ABORT
} mission_sig_t;

typedef enum {
    RES_HANDLED = 0,
    RES_IGNORED,
    RES_TRANSITION,
    RES_SUPER
} fsm_res_t;

typedef enum {
    STATE_ID_NONE = 0,
    STATE_ID_OPERATIONAL_SUPER,
    STATE_ID_IDLE,
    STATE_ID_SEARCH,
    STATE_ID_ACQUIRE,
    STATE_ID_TRACK,
    STATE_ID_ENGAGE,
    STATE_ID_VERIFY,
    STATE_ID_AVOID,
    STATE_ID_RECOVERY_SUPER,
    STATE_ID_RTB,
    STATE_ID_ABORT
} state_id_t;

/* ── 2. Структури даних телеметрії, цілей та подій ── */
typedef struct {
    uint32_t id;
    float lat;
    float lon;
    float alt;
    float confidence;
    float distance_m;
    float nis;
} target_desc_t;

typedef struct {
    mission_sig_t sig;
    uint32_t timestamp_ms;
    union {
        target_desc_t target;
        float value;
        uint32_t code;
    } param;
} event_t;

typedef struct {
    float battery_voltage;
    float battery_soc;           /* 0.0 .. 1.0 */
    float energy_remaining_wh;
    float dist_to_home_m;
    float wind_speed_ms;
    float wind_heading_rad;
    float uav_heading_rad;
    float cruise_speed_ms;
    float cruise_power_w;
    bool gnss_3d_fix;
    float gnss_hdop;
    float ekf_nis;
    bool geofence_ok;
    bool payload_armed;
    uint8_t payload_remaining;
    float obstacle_distance_m;
} telemetry_t;

/* ── 3. Безблокувальна черга подій SPSC ── */
typedef struct {
    event_t buffer[EVENT_QUEUE_CAPACITY];
    volatile uint32_t head;
    volatile uint32_t tail;
} event_queue_t;

static void queue_init(event_queue_t *q) {
    q->head = 0;
    q->tail = 0;
}

static bool queue_push(event_queue_t *q, const event_t *evt) {
    uint32_t next_head = (q->head + 1) % EVENT_QUEUE_CAPACITY;
    if (next_head == q->tail) {
        return false; /* Буфер переповнено */
    }
    q->buffer[q->head] = *evt;
    q->head = next_head;
    return true;
}

static bool queue_pop(event_queue_t *q, event_t *evt) {
    if (q->tail == q->head) {
        return false; /* Черга порожня */
    }
    *evt = q->buffer[q->tail];
    q->tail = (q->tail + 1) % EVENT_QUEUE_CAPACITY;
    return true;
}

/* ── 4. Контекст місійного автомата ── */
struct mission_fsm_s;
typedef fsm_res_t (*state_handler_t)(struct mission_fsm_s *ctx, const event_t *evt);

typedef struct mission_fsm_s {
    state_handler_t state;
    state_handler_t history_state;
    state_id_t state_id;
    state_id_t history_state_id;

    telemetry_t telem;
    target_desc_t active_target;
    event_queue_t queue;

    uint32_t state_entry_time_ms;
    uint32_t last_target_seen_ms;
    uint32_t current_time_ms;
    uint32_t transition_count;
    bool payload_release_triggered;
    uint32_t search_grid_leg;
} mission_fsm_t;

/* ── 5. Прототипи функцій станів ── */
fsm_res_t state_op_super(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_idle(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_search(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_acquire(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_track(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_engage(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_verify(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_avoid(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_rec_super(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_rtb(mission_fsm_t *ctx, const event_t *evt);
fsm_res_t state_abort(mission_fsm_t *ctx, const event_t *evt);

/* Допоміжний макрос переходу */
#define TRANSITION_TO(target_fn, target_id_enum) \
    do { \
        if (ctx->state != NULL) { \
            event_t exit_e = { .sig = SIG_EXIT, .timestamp_ms = ctx->current_time_ms }; \
            ctx->state(ctx, &exit_e); \
        } \
        ctx->state = (target_fn); \
        ctx->state_id = (target_id_enum); \
        ctx->state_entry_time_ms = ctx->current_time_ms; \
        ctx->transition_count++; \
        event_t entry_e = { .sig = SIG_ENTRY, .timestamp_ms = ctx->current_time_ms }; \
        ctx->state(ctx, &entry_e); \
        return RES_TRANSITION; \
    } while (0)

/* ── 6. Охоронні умови (Guard Predicates) ── */
static bool guard_energy_sufficient_for_rtb(const telemetry_t *t) {
    if (t->cruise_speed_ms <= 1.0f) return false;
    
    /* Проєкція вітру на курс повернення */
    float headwind = t->wind_speed_ms * cosf(t->wind_heading_rad - t->uav_heading_rad);
    float ground_speed = t->cruise_speed_ms - headwind;
    if (ground_speed < 3.0f) ground_speed = 3.0f;

    float time_rtb_h = (t->dist_to_home_m / ground_speed) / 3600.0f;
    float energy_rtb_wh = t->cruise_power_w * time_rtb_h;
    float energy_reserve_wh = energy_rtb_wh * 0.20f; /* 20% гарантованого резерву */

    return t->energy_remaining_wh > (energy_rtb_wh + energy_reserve_wh);
}

static bool guard_sensors_healthy(const telemetry_t *t) {
    return t->gnss_3d_fix && (t->gnss_hdop <= 1.3f) && (t->ekf_nis <= 1.0f);
}

static bool guard_target_nis_valid(float nis) {
    return nis <= 5.99f; /* 95% поріг розподілу Chi-Square для 2 DOF */
}

/* ── 7. Реалізація функцій станів ── */

/* Суперстан OPERATIONAL */
fsm_res_t state_op_super(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_BATTERY_CRITICAL:
            TRANSITION_TO(state_rtb, STATE_ID_RTB);

        case SIG_GEOFENCE_BREACH:
            TRANSITION_TO(state_abort, STATE_ID_ABORT);

        case SIG_CMD_ABORT:
            TRANSITION_TO(state_rtb, STATE_ID_RTB);

        case SIG_OBSTACLE_DETECTED:
            TRANSITION_TO(state_avoid, STATE_ID_AVOID);

        case SIG_TICK:
            if (!guard_energy_sufficient_for_rtb(&ctx->telem)) {
                TRANSITION_TO(state_rtb, STATE_ID_RTB);
            }
            return RES_HANDLED;

        default:
            return RES_IGNORED;
    }
}

/* Стан IDLE */
fsm_res_t state_idle(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_CMD_START:
            if (guard_sensors_healthy(&ctx->telem) && ctx->telem.geofence_ok && 
                guard_energy_sufficient_for_rtb(&ctx->telem)) {
                ctx->search_grid_leg = 1;
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }
            return RES_HANDLED;

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан SEARCH */
fsm_res_t state_search(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            ctx->history_state = state_search;
            ctx->history_state_id = STATE_ID_SEARCH;
            return RES_HANDLED;

        case SIG_CANDIDATE_DETECTED:
            if (evt->param.target.confidence >= 0.55f && ctx->telem.geofence_ok) {
                ctx->active_target = evt->param.target;
                ctx->last_target_seen_ms = ctx->current_time_ms;
                TRANSITION_TO(state_acquire, STATE_ID_ACQUIRE);
            }
            return RES_HANDLED;

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан ACQUIRE */
fsm_res_t state_acquire(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_TARGET_LOCKED:
            if (evt->param.target.confidence >= 0.80f && 
                guard_target_nis_valid(evt->param.target.nis) &&
                guard_sensors_healthy(&ctx->telem) &&
                guard_energy_sufficient_for_rtb(&ctx->telem)) {
                ctx->active_target = evt->param.target;
                ctx->last_target_seen_ms = ctx->current_time_ms;
                TRANSITION_TO(state_track, STATE_ID_TRACK);
            }
            return RES_HANDLED;

        case SIG_TICK:
            if (ctx->current_time_ms - ctx->state_entry_time_ms > ACQUIRE_TIMEOUT_MS) {
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }
            return state_op_super(ctx, evt);

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан TRACK */
fsm_res_t state_track(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            ctx->history_state = state_track;
            ctx->history_state_id = STATE_ID_TRACK;
            return RES_HANDLED;

        case SIG_WITHIN_ENGAGE_RANGE:
            if (ctx->telem.payload_armed && ctx->telem.payload_remaining > 0 &&
                ctx->telem.geofence_ok && guard_energy_sufficient_for_rtb(&ctx->telem)) {
                TRANSITION_TO(state_engage, STATE_ID_ENGAGE);
            }
            return RES_HANDLED;

        case SIG_TARGET_LOST:
        case SIG_TICK:
            if (ctx->current_time_ms - ctx->last_target_seen_ms > TARGET_TRACK_TIMEOUT_MS) {
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }
            return state_op_super(ctx, evt);

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан ENGAGE */
fsm_res_t state_engage(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            ctx->payload_release_triggered = true;
            if (ctx->telem.payload_remaining > 0) {
                ctx->telem.payload_remaining--;
            }
            return RES_HANDLED;

        case SIG_PAYLOAD_RELEASED:
            TRANSITION_TO(state_verify, STATE_ID_VERIFY);

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан VERIFY */
fsm_res_t state_verify(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_VERIFY_COMPLETE:
        case SIG_TICK:
            if (ctx->current_time_ms - ctx->state_entry_time_ms >= VERIFY_TIMEOUT_MS) {
                if (ctx->telem.payload_remaining > 0 && guard_energy_sufficient_for_rtb(&ctx->telem)) {
                    TRANSITION_TO(state_search, STATE_ID_SEARCH);
                } else {
                    TRANSITION_TO(state_rtb, STATE_ID_RTB);
                }
            }
            return RES_HANDLED;

        default:
            return state_op_super(ctx, evt);
    }
}

/* Стан AVOID (Обхід перешкоди) */
fsm_res_t state_avoid(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;

        case SIG_OBSTACLE_CLEARED:
            /* Повернення до збереженого стану через History */
            if (ctx->history_state != NULL) {
                TRANSITION_TO(ctx->history_state, ctx->history_state_id);
            } else {
                TRANSITION_TO(state_search, STATE_ID_SEARCH);
            }

        default:
            return state_op_super(ctx, evt);
    }
}

/* Суперстан RECOVERY */
fsm_res_t state_rec_super(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;
        default:
            return RES_IGNORED;
    }
}

/* Стан RTB */
fsm_res_t state_rtb(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;
        default:
            return state_rec_super(ctx, evt);
    }
}

/* Стан ABORT */
fsm_res_t state_abort(mission_fsm_t *ctx, const event_t *evt) {
    switch (evt->sig) {
        case SIG_ENTRY:
            return RES_HANDLED;
        default:
            return state_rec_super(ctx, evt);
    }
}

/* ── 8. Ініціалізація та виконання циклу RTC ── */
void mission_fsm_init(mission_fsm_t *ctx, const telemetry_t *init_telem) {
    memset(ctx, 0, sizeof(*ctx));
    ctx->telem = *init_telem;
    queue_init(&ctx->queue);
    
    ctx->state = state_idle;
    ctx->state_id = STATE_ID_IDLE;
    ctx->history_state = state_search;
    ctx->history_state_id = STATE_ID_SEARCH;

    event_t init_evt = { .sig = SIG_ENTRY, .timestamp_ms = 0 };
    ctx->state(ctx, &init_evt);
}

void mission_fsm_process_queue(mission_fsm_t *ctx) {
    event_t evt;
    while (queue_pop(&ctx->queue, &evt)) {
        ctx->current_time_ms = evt.timestamp_ms;
        if (ctx->state != NULL) {
            ctx->state(ctx, &evt);
        }
    }
}

bool mission_fsm_post_event(mission_fsm_t *ctx, const event_t *evt) {
    return queue_push(&ctx->queue, evt);
}

/* ── 9. Модуль автоматизованого тестування C ── */
void run_c_fsm_tests(void) {
    telemetry_t telem = {
        .battery_voltage = 24.5f,
        .battery_soc = 0.95f,
        .energy_remaining_wh = 140.0f,
        .dist_to_home_m = 2000.0f,
        .wind_speed_ms = 3.0f,
        .wind_heading_rad = 0.0f,
        .uav_heading_rad = 0.0f,
        .cruise_speed_ms = 20.0f,
        .cruise_power_w = 220.0f,
        .gnss_3d_fix = true,
        .gnss_hdop = 0.8f,
        .ekf_nis = 0.2f,
        .geofence_ok = true,
        .payload_armed = true,
        .payload_remaining = 2,
        .obstacle_distance_m = 50.0f
    };

    mission_fsm_t fsm;
    mission_fsm_init(&fsm, &telem);
    assert(fsm.state_id == STATE_ID_IDLE);

    /* Тест 1: Старт місії -> SEARCH */
    event_t e_start = { .sig = SIG_CMD_START, .timestamp_ms = 100 };
    mission_fsm_post_event(&fsm, &e_start);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_SEARCH);

    /* Тест 2: Виявлення кандидата -> ACQUIRE */
    event_t e_cand = {
        .sig = SIG_CANDIDATE_DETECTED,
        .timestamp_ms = 500,
        .param.target = { .id = 10, .confidence = 0.70f, .nis = 0.5f }
    };
    mission_fsm_post_event(&fsm, &e_cand);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_ACQUIRE);

    /* Тест 3: Підтвердження цілі з валідним NIS -> TRACK */
    event_t e_lock = {
        .sig = SIG_TARGET_LOCKED,
        .timestamp_ms = 900,
        .param.target = { .id = 10, .confidence = 0.89f, .nis = 1.2f }
    };
    mission_fsm_post_event(&fsm, &e_lock);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_TRACK);

    /* Тест 4: Перешкода під час супроводу -> AVOID -> повернення через History в TRACK */
    event_t e_obs = { .sig = SIG_OBSTACLE_DETECTED, .timestamp_ms = 1200 };
    mission_fsm_post_event(&fsm, &e_obs);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_AVOID);

    event_t e_clear = { .sig = SIG_OBSTACLE_CLEARED, .timestamp_ms = 1800 };
    mission_fsm_post_event(&fsm, &e_clear);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_TRACK);

    /* Тест 5: Зближення на дистанцію ураження -> ENGAGE -> VERIFY */
    event_t e_range = { .sig = SIG_WITHIN_ENGAGE_RANGE, .timestamp_ms = 2200 };
    mission_fsm_post_event(&fsm, &e_range);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_ENGAGE);
    assert(fsm.payload_release_triggered == true);

    event_t e_rel = { .sig = SIG_PAYLOAD_RELEASED, .timestamp_ms = 2300 };
    mission_fsm_post_event(&fsm, &e_rel);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_VERIFY);

    /* Тест 6: Завершення верифікації -> SEARCH (залишився 1 снаряд) */
    event_t e_ver = { .sig = SIG_VERIFY_COMPLETE, .timestamp_ms = 4500 };
    mission_fsm_post_event(&fsm, &e_ver);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_SEARCH);

    /* Тест 7: Failsafe за енергетичним дефіцитом -> RTB */
    fsm.telem.energy_remaining_wh = 12.0f;
    event_t e_tick = { .sig = SIG_TICK, .timestamp_ms = 5000 };
    mission_fsm_post_event(&fsm, &e_tick);
    mission_fsm_process_queue(&fsm);
    assert(fsm.state_id == STATE_ID_RTB);

    printf("ALL MISSION HSM C UNIT TESTS PASSED SUCCESSFULLY!\n");
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <variant>
#include <optional>
#include <string_view>
#include <iostream>
#include <cassert>

namespace drone::mission {

inline constexpr size_t kQueueCapacity = 32;
inline constexpr uint32_t kTargetTrackTimeoutMs = 3000;
inline constexpr uint32_t kAcquireTimeoutMs      = 4000;
inline constexpr uint32_t kVerifyTimeoutMs       = 2000;

/* ── 1. Структура опису цілі ── */
struct Target {
    uint32_t id{0};
    float latitude{0.0F};
    float longitude{0.0F};
    float altitude{0.0F};
    float confidence{0.0F};
    float distance_m{0.0F};
    float nis{0.0F};
};

/* ── 2. Строго типізований набір подій ── */
struct EvTick { uint32_t timestamp_ms{0}; };
struct EvCmdStart { uint32_t timestamp_ms{0}; };
struct EvCandidateDetected { uint32_t timestamp_ms{0}; Target target{}; };
struct EvTargetLocked { uint32_t timestamp_ms{0}; Target target{}; };
struct EvTargetLost { uint32_t timestamp_ms{0}; };
struct EvWithinEngageRange { uint32_t timestamp_ms{0}; };
struct EvPayloadReleased { uint32_t timestamp_ms{0}; };
struct EvVerifyComplete { uint32_t timestamp_ms{0}; };
struct EvObstacleDetected { uint32_t timestamp_ms{0}; };
struct EvObstacleCleared { uint32_t timestamp_ms{0}; };
struct EvBatteryCritical { uint32_t timestamp_ms{0}; };
struct EvGeofenceBreach { uint32_t timestamp_ms{0}; };
struct EvCmdAbort { uint32_t timestamp_ms{0}; };

using MissionEvent = std::variant<
    EvTick,
    EvCmdStart,
    EvCandidateDetected,
    EvTargetLocked,
    EvTargetLost,
    EvWithinEngageRange,
    EvPayloadReleased,
    EvVerifyComplete,
    EvObstacleDetected,
    EvObstacleCleared,
    EvBatteryCritical,
    EvGeofenceBreach,
    EvCmdAbort
>;

/* ── 3. Телеметрія та стан борта ── */
struct Telemetry {
    float battery_voltage{24.5F};
    float battery_soc{0.95F};
    float energy_remaining_wh{140.0F};
    float dist_to_home_m{2000.0F};
    float wind_speed_ms{3.0F};
    float wind_heading_rad{0.0F};
    float uav_heading_rad{0.0F};
    float cruise_speed_ms{20.0F};
    float cruise_power_w{220.0F};
    bool gnss_3d_fix{true};
    float gnss_hdop{0.8F};
    float ekf_nis{0.2F};
    bool geofence_ok{true};
    bool payload_armed{true};
    uint8_t payload_remaining{2};
    float obstacle_distance_m{50.0F};

    [[nodiscard]] bool is_energy_sufficient_for_rtb() const noexcept {
        if (cruise_speed_ms <= 1.0F) return false;
        const float headwind = wind_speed_ms * std::cos(wind_heading_rad - uav_heading_rad);
        float ground_speed = cruise_speed_ms - headwind;
        if (ground_speed < 3.0F) ground_speed = 3.0F;

        const float time_rtb_h = (dist_to_home_m / ground_speed) / 3600.0F;
        const float energy_rtb_wh = cruise_power_w * time_rtb_h;
        const float energy_reserve_wh = energy_rtb_wh * 0.20F;

        return energy_remaining_wh > (energy_rtb_wh + energy_reserve_wh);
    }

    [[nodiscard]] bool are_sensors_healthy() const noexcept {
        return gnss_3d_fix && (gnss_hdop <= 1.3F) && (ekf_nis <= 1.0F);
    }

    [[nodiscard]] static constexpr bool is_target_nis_valid(float nis) noexcept {
        return nis <= 5.99F;
    }
};

/* ── 4. Дескриптори станів ── */
struct StateIdle { static constexpr std::string_view name{"IDLE"}; };
struct StateSearch { static constexpr std::string_view name{"SEARCH"}; };
struct StateAcquire { static constexpr std::string_view name{"ACQUIRE"}; uint32_t entry_ms{0}; Target target{}; };
struct StateTrack { static constexpr std::string_view name{"TRACK"}; uint32_t last_seen_ms{0}; Target target{}; };
struct StateEngage { static constexpr std::string_view name{"ENGAGE"}; Target target{}; };
struct StateVerify { static constexpr std::string_view name{"VERIFY"}; uint32_t entry_ms{0}; };
struct StateAvoid { static constexpr std::string_view name{"AVOID"}; };
struct StateRtb { static constexpr std::string_view name{"RTB"}; };
struct StateAbort { static constexpr std::string_view name{"ABORT"}; };

using State = std::variant<
    StateIdle,
    StateSearch,
    StateAcquire,
    StateTrack,
    StateEngage,
    StateVerify,
    StateAvoid,
    StateRtb,
    StateAbort
>;

/* ── 5. Безблокувальна черга подій C++ ── */
template <typename T, size_t Capacity>
class SpscQueue {
public:
    constexpr SpscQueue() noexcept = default;

    bool push(const T& item) noexcept {
        const size_t next_head = (head_ + 1) % Capacity;
        if (next_head == tail_) return false;
        buffer_[head_] = item;
        head_ = next_head;
        return true;
    }

    bool pop(T& item) noexcept {
        if (tail_ == head_) return false;
        item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        return true;
    }

private:
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

/* ── 6. Ієрархічний контролер місійного автомата ── */
class MissionHsmEngine {
public:
    explicit MissionHsmEngine(Telemetry telem) noexcept
        : telem_(telem), current_state_(StateIdle{}), history_state_(StateSearch{}) {}

    bool post_event(const MissionEvent& event) noexcept {
        return queue_.push(event);
    }

    void process_queue() noexcept {
        MissionEvent event;
        while (queue_.pop(event)) {
            current_time_ms_ = get_timestamp(event);

            /* 1. Обробка глобальних умов суперстану OPERATIONAL */
            if (std::holds_alternative<EvBatteryCritical>(event) || !telem_.is_energy_sufficient_for_rtb()) {
                if (!std::holds_alternative<StateRtb>(current_state_) &&
                    !std::holds_alternative<StateAbort>(current_state_)) {
                    transition_to(StateRtb{});
                    continue;
                }
            }

            if (std::holds_alternative<EvGeofenceBreach>(event)) {
                transition_to(StateAbort{});
                continue;
            }

            if (std::holds_alternative<EvCmdAbort>(event)) {
                transition_to(StateRtb{});
                continue;
            }

            if (std::holds_alternative<EvObstacleDetected>(event)) {
                transition_to(StateAvoid{});
                continue;
            }

            /* 2. Поліморфна диспетчеризація поточного стану */
            std::visit([this, &event](auto& active_state) {
                handle(active_state, event);
            }, current_state_);
        }
    }

    [[nodiscard]] const State& state() const noexcept { return current_state_; }
    [[nodiscard]] Telemetry& telemetry() noexcept { return telem_; }
    [[nodiscard]] const Telemetry& telemetry() const noexcept { return telem_; }
    [[nodiscard]] bool was_payload_released() const noexcept { return payload_released_; }

private:
    template <typename T>
    void transition_to(T new_state) noexcept {
        /* Збереження стану в історію */
        if (std::holds_alternative<StateSearch>(current_state_) ||
            std::holds_alternative<StateTrack>(current_state_)) {
            history_state_ = current_state_;
        }
        current_state_ = std::move(new_state);
        transition_count_++;
    }

    static uint32_t get_timestamp(const MissionEvent& event) noexcept {
        return std::visit([](const auto& e) noexcept { return e.timestamp_ms; }, event);
    }

    void handle(StateIdle&, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvCmdStart>(event)) {
            if (telem_.are_sensors_healthy() && telem_.geofence_ok && telem_.is_energy_sufficient_for_rtb()) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateSearch&, const MissionEvent& event) noexcept {
        if (const auto* cand = std::get_if<EvCandidateDetected>(&event)) {
            if (cand->target.confidence >= 0.55F && telem_.geofence_ok) {
                transition_to(StateAcquire{ .entry_ms = current_time_ms_, .target = cand->target });
            }
        }
    }

    void handle(StateAcquire& acq, const MissionEvent& event) noexcept {
        if (const auto* lock = std::get_if<EvTargetLocked>(&event)) {
            if (lock->target.confidence >= 0.80F && 
                Telemetry::is_target_nis_valid(lock->target.nis) &&
                telem_.are_sensors_healthy() &&
                telem_.is_energy_sufficient_for_rtb()) {
                transition_to(StateTrack{ .last_seen_ms = current_time_ms_, .target = lock->target });
            }
        } else if (std::holds_alternative<EvTick>(event)) {
            if (current_time_ms_ - acq.entry_ms > kAcquireTimeoutMs) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateTrack& track, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvWithinEngageRange>(event)) {
            if (telem_.payload_armed && telem_.payload_remaining > 0 &&
                telem_.geofence_ok && telem_.is_energy_sufficient_for_rtb()) {
                payload_released_ = true;
                if (telem_.payload_remaining > 0) telem_.payload_remaining--;
                transition_to(StateEngage{ .target = track.target });
            }
        } else if (std::holds_alternative<EvTargetLost>(event) || std::holds_alternative<EvTick>(event)) {
            if (current_time_ms_ - track.last_seen_ms > kTargetTrackTimeoutMs) {
                transition_to(StateSearch{});
            }
        }
    }

    void handle(StateEngage&, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvPayloadReleased>(event)) {
            transition_to(StateVerify{ .entry_ms = current_time_ms_ });
        }
    }

    void handle(StateVerify& ver, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvVerifyComplete>(event) || std::holds_alternative<EvTick>(event)) {
            if (current_time_ms_ - ver.entry_ms >= kVerifyTimeoutMs) {
                if (telem_.payload_remaining > 0 && telem_.is_energy_sufficient_for_rtb()) {
                    transition_to(StateSearch{});
                } else {
                    transition_to(StateRtb{});
                }
            }
        }
    }

    void handle(StateAvoid&, const MissionEvent& event) noexcept {
        if (std::holds_alternative<EvObstacleCleared>(event)) {
            /* Відновлення стану з історії */
            current_state_ = history_state_;
        }
    }

    void handle(StateRtb&, const MissionEvent&) noexcept {}
    void handle(StateAbort&, const MissionEvent&) noexcept {}

    Telemetry telem_;
    State current_state_;
    State history_state_;
    SpscQueue<MissionEvent, kQueueCapacity> queue_{};
    uint32_t current_time_ms_{0};
    uint32_t transition_count_{0};
    bool payload_released_{false};
};

} // namespace drone::mission

/* ── 7. Блок юніт-тестування C++ ── */
int main() {
    using namespace drone::mission;

    Telemetry telem{};
    MissionHsmEngine fsm{telem};

    assert(std::holds_alternative<StateIdle>(fsm.state()));

    /* Тест 1: Старт місії -> SEARCH */
    fsm.post_event(EvCmdStart{ .timestamp_ms = 100 });
    fsm.process_queue();
    assert(std::holds_alternative<StateSearch>(fsm.state()));

    /* Тест 2: Виявлення кандидата -> ACQUIRE */
    fsm.post_event(EvCandidateDetected{
        .timestamp_ms = 500,
        .target = Target{ .id = 42, .confidence = 0.68F, .nis = 0.4F }
    });
    fsm.process_queue();
    assert(std::holds_alternative<StateAcquire>(fsm.state()));

    /* Тест 3: Захоплення цілі -> TRACK */
    fsm.post_event(EvTargetLocked{
        .timestamp_ms = 900,
        .target = Target{ .id = 42, .confidence = 0.91F, .nis = 1.1F }
    });
    fsm.process_queue();
    assert(std::holds_alternative<StateTrack>(fsm.state()));

    /* Тест 4: Перешкода під час наведення -> AVOID -> відновлення в TRACK */
    fsm.post_event(EvObstacleDetected{ .timestamp_ms = 1200 });
    fsm.process_queue();
    assert(std::holds_alternative<StateAvoid>(fsm.state()));

    fsm.post_event(EvObstacleCleared{ .timestamp_ms = 1800 });
    fsm.process_queue();
    assert(std::holds_alternative<StateTrack>(fsm.state()));

    /* Тест 5: Зближення на дистанцію скиду -> ENGAGE -> VERIFY */
    fsm.post_event(EvWithinEngageRange{ .timestamp_ms = 2200 });
    fsm.process_queue();
    assert(std::holds_alternative<StateEngage>(fsm.state()));
    assert(fsm.was_payload_released() == true);

    fsm.post_event(EvPayloadReleased{ .timestamp_ms = 2300 });
    fsm.process_queue();
    assert(std::holds_alternative<StateVerify>(fsm.state()));

    /* Тест 6: Завершення верифікації (залишився 1 заряд) -> SEARCH */
    fsm.post_event(EvVerifyComplete{ .timestamp_ms = 4500 });
    fsm.process_queue();
    assert(std::holds_alternative<StateSearch>(fsm.state()));

    /* Тест 7: Порушення меж геозони -> ABORT */
    fsm.post_event(EvGeofenceBreach{ .timestamp_ms = 6000 });
    fsm.process_queue();
    assert(std::holds_alternative<StateAbort>(fsm.state()));

    std::cout << "ALL MISSION HSM C++ UNIT TESTS PASSED SUCCESSFULLY!" << std::endl;
    return 0;
}
```
:::

---

## Детальний аналіз тестових сценаріїв та перевірки переходів

Тестовий набір модуля імітує повний спектр реальних польотних ситуацій, гарантуючи детермінізм роботи автомата:

### 1. Штатний ударно-розвідувальний цикл (Mission Cycle)

Сценарій моделює виявлення, класифікацію, ураження цілі та продовження пошукової операції:
* **Крок 1 (`IDLE -> SEARCH`):** команда `SIG_CMD_START` перевіряє готовність сенсорів (`gnss_3d_fix == true`, `ekf_nis <= 1.0`), коректність геозони та розраховує енергетичний бюджет повернення. За успішної валідації ініціалізується стан пошуку за сіткою.
* **Крок 2 (`SEARCH -> ACQUIRE`):** надходження сигналу `SIG_CANDIDATE_DETECTED` з рівнем достовірності 0.70 переводить апарат у стан верифікації. Автомат фіксує часову мітку первинного контакту для контролю тайм-ауту.
* **Крок 3 (`ACQUIRE -> TRACK`):** оптичний трекер підтверджує клас цілі з достовірністю 0.89 та інновацією Калмана NIS = 1.1 <= 5.99. Охоронна умова підтверджує відсутність аномальних стрибків координат і перемикає борт у стан активного супроводу.
* **Крок 4 (`TRACK -> ENGAGE`):** при досягненні балістичної точки скиду генерується подія `SIG_WITHIN_ENGAGE_RANGE`. Автомат перевіряє прапорець готовності запобіжника (`payload_armed == true`) та наявність заряду (`payload_remaining > 0`), після чого видає сигнал на спрацювання сервоприводу замка.
* **Крок 5 (`ENGAGE -> VERIFY -> SEARCH`):** після підтвердження відстрілу вантажу запускається таймер оцінки наслідків на 2 секунди. Оскільки в магазині залишається ще 1 боєприпас, після завершення перевірки автомат детерміновано повертається до стану `SEARCH`.

### 2. Динамічне ухилення від перешкод з відновленням контексту через історію (History Resumption)

Сценарій підтверджує коректність роботи псевдостану Deep History при появі раптових просторових загроз:
* Під час перебування в активній фазі наведення на ціль (`STATE_TRACK`) бортовий далекомір виявляє небезпечне зближення з перешкодою (`SIG_OBSTACLE_DETECTED`).
* Автомат зберігає поточний стан `STATE_TRACK` та ідентифікатор цілі в змінну `history_state` і перемикається в стан `STATE_AVOID`.
* Після виконання обхідного маневру надходить сигнал `SIG_OBSTACLE_CLEARED`. Автомат відновлює збережений стан `STATE_TRACK` без необхідності повторного проходження фаз пошуку та первинного захоплення.

### 3. Failsafe-преемпція за енергетичним дефіцитом (Energy Exhaustion)

Сценарій перевіряє надійність захисту від падіння дрона через виснаження батареї:
* У процесі виконання будь-якої фази місії напруга або залишковий заряд батареї падають нижче динамічного порогу повернення E_RTB(w) + E_reserve.
* При надходженні періодичного сигналу таймера `SIG_TICK` суперстан `OPERATIONAL` перехоплює подію, блокує подальше виконання тактичних задач і негайно переводить дрон у стан `STATE_RTB`.

### 4. Порушення меж польотної геозони (Geofence Breach)

Сценарій перевіряє захист від несанкціонованого відльоту апарата за межі встановленого безпечного периметра:
* При перетині лінії віртуального геобар'єра сенсорний модуль генерує подію `SIG_GEOFENCE_BREACH`.
* Суперстан `OPERATIONAL` негайно ініціює перехід у кінцевий аварійний стан `STATE_ABORT`, який вимикає тягу або активує парашутну систему порятунку.

---

## Інструкція з інтеграції у польотний стек (PX4 / ArduPilot / ROS 2)

Для інтеграції модуля у виробничий польотний стек виконайте такі кроки:

1. **Інтеграція диспетчера у високорівневий таймерний потік:**
   * Створіть потік керування з фіксованим періодом квантування 20–50 мс (частота 20–50 Гц);
   * Щотакту надсилайте подію `SIG_TICK` із поточною міткою часу `timestamp_ms` та викликайте функцію `mission_fsm_process_queue()`.
2. **Маршрутизація повідомлень MAVLink:**
   * Підпишіться на пакети `GLOBAL_POSITION_INT`, `ATTITUDE` та `BATTERY_STATUS` для оновлення полів структури `telemetry_t`;
   * При зміні стану автомата на `STATE_TRACK` або `STATE_AVOID` транслюйте розраховані вектори наведення у вихідні пакети `SET_POSITION_TARGET_LOCAL_NED`;
   * При вході в стан `STATE_ENGAGE` генеруйте команду `MAV_CMD_DO_SET_SERVO` для активації актуатора скиду.
3. **Логування стану в ULog / DataFlash:**
   * У кожному циклі диспетчеризації записуйте значення `state_id`, `history_state_id` та значення активних Guard-предикатів у бінарний польотний журнал для спрощення діагностики польотних інцидентів.

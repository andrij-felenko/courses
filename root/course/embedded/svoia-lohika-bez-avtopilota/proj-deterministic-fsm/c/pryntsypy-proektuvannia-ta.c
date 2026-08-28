#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/* --- 1. ТИПИ ПОДІЙ ТА СТРУКТУРА ПОДІЇ --- */
typedef enum {
    EV_NONE = 0,
    EV_ENTRY,            /* Системна: вхід у стан */
    EV_EXIT,             /* Системна: вихід зі стану */
    EV_TICK,             /* Періодичний такт планувальника */
    EV_START_MISSION,    /* Команда старту місії */
    EV_WAYPOINT_REACHED, /* Позицію досягнуто */
    EV_OBSTACLE_DETECTED,/* Далекомір ToF виявив перешкоду */
    EV_OBSTACLE_CLEARED, /* Шлях вільний */
    EV_GOAL_TIMEOUT,     /* Вичерпано ліміт часу на ціль */
    EV_BATTERY_LOW,      /* Напруга нижче першого порогу */
    EV_CRITICAL_FAULT    /* Аварія: обрив зв'язку, бампер, перегрів */
} EventId;

typedef struct {
    EventId id;
    uint32_t timestamp_ms;
    union {
        int32_t i32_val;
        float   f32_val;
        struct {
            int16_t x;
            int16_t y;
        } coords;
    } payload;
} Event;

/* --- 2. КІЛЬЦЕВА ЧЕРГА ПОДІЙ (STATIC RING BUFFER) --- */
#define EVENT_QUEUE_CAPACITY 16

typedef struct {
    Event buffer[EVENT_QUEUE_CAPACITY];
    volatile uint8_t head;
    volatile uint8_t tail;
    volatile uint8_t count;
    uint32_t dropped_events;
} EventQueue;

/* Платформозалежні макроси критичних секцій для запобігання гонитви даних */
#define ENTER_CRITICAL() uint32_t primask = __get_PRIMASK(); __disable_irq()
#define EXIT_CRITICAL()  if (!primask) { __enable_irq(); }

static inline void event_queue_init(EventQueue *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
    q->dropped_events = 0;
}

static inline bool event_queue_post(EventQueue *q, const Event *ev) {
    bool ok = false;
    ENTER_CRITICAL();
    if (q->count < EVENT_QUEUE_CAPACITY) {
        q->buffer[q->head] = *ev;
        q->head = (uint8_t)((q->head + 1) % EVENT_QUEUE_CAPACITY);
        q->count++;
        ok = true;
    } else {
        q->dropped_events++;
    }
    EXIT_CRITICAL();
    return ok;
}

static inline bool event_queue_pop(EventQueue *q, Event *ev) {
    bool ok = false;
    ENTER_CRITICAL();
    if (q->count > 0) {
        *ev = q->buffer[q->tail];
        q->tail = (uint8_t)((q->tail + 1) % EVENT_QUEUE_CAPACITY);
        q->count--;
        ok = true;
    }
    EXIT_CRITICAL();
    return ok;
}

/* --- 3. ІЄРАРХІЧНИЙ АВТОМАТ СТАНІВ (HSM) --- */
typedef enum {
    RES_HANDLED,   /* Подію оброблено */
    RES_IGNORED,   /* Подія не стосується стану */
    RES_SUPER,     /* Подію не оброблено, передати батьківському стану */
    RES_TRANSITION /* Відбувся перехід у новий стан */
} HsmResult;

struct Hsm;
typedef HsmResult (*StateHandler)(struct Hsm *me, const Event *e);

typedef struct Hsm {
    StateHandler current_state;
    StateHandler next_state;
    void *user_data;
} Hsm;

static inline void hsm_transition(Hsm *me, StateHandler target) {
    me->next_state = target;
}

void hsm_dispatch(Hsm *me, const Event *e) {
    StateHandler s = me->current_state;
    while (s != NULL) {
        HsmResult res = s(me, e);
        if (res == RES_HANDLED || res == RES_IGNORED) {
            break;
        }
        if (res == RES_TRANSITION) {
            /* Вихід зі старого стану */
            Event exit_ev = { .id = EV_EXIT, .timestamp_ms = e->timestamp_ms };
            me->current_state(me, &exit_ev);

            /* Зміна стану та вхід у новий */
            me->current_state = me->next_state;
            me->next_state = NULL;

            Event entry_ev = { .id = EV_ENTRY, .timestamp_ms = e->timestamp_ms };
            me->current_state(me, &entry_ev);
            break;
        }
        if (res == RES_SUPER) {
            /* Батьківський стан викликається наступною ітерацією */
            break;
        }
    }
}

/* --- 4. ЧЕРГА ЦІЛЕЙ ТА ДВИГУН ЗАВДАНЬ --- */
typedef enum {
    GOAL_NONE = 0,
    GOAL_NAV_WAYPOINT,
    GOAL_STATION_HOLD,
    GOAL_SURVEY_ACTION
} GoalType;

typedef struct {
    GoalType type;
    uint32_t timeout_ms;
    uint32_t start_time_ms;
    union {
        struct { int16_t x; int16_t y; float speed_mps; } nav;
        struct { uint32_t duration_ms; } hold;
        struct { uint8_t sensor_mask; } survey;
    } params;
} Goal;

#define GOAL_QUEUE_CAPACITY 8

typedef struct {
    Goal buffer[GOAL_QUEUE_CAPACITY];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    Goal active_goal;
    bool has_active_goal;
} GoalEngine;

void goal_engine_init(GoalEngine *ge) {
    memset(ge, 0, sizeof(GoalEngine));
}

bool goal_engine_push(GoalEngine *ge, const Goal *g) {
    if (ge->count >= GOAL_QUEUE_CAPACITY) return false;
    ge->buffer[ge->head] = *g;
    ge->head = (uint8_t)((ge->head + 1) % GOAL_QUEUE_CAPACITY);
    ge->count++;
    return true;
}

void goal_engine_abort_all(GoalEngine *ge) {
    /* Безпечне скидання активного кроку та очищення всієї черги */
    ge->head = 0;
    ge->tail = 0;
    ge->count = 0;
    ge->has_active_goal = false;
    memset(&ge->active_goal, 0, sizeof(Goal));
}

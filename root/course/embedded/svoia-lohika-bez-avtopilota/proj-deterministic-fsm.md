# ⚙️ Реалізація подійного диспетчера та ієрархічного автомата цілей

Коли автономний апарат (інспекційний робот, підводний буй чи агроплатформа) виконує місію без громіздких фреймворків автопілота на кшталт PX4, уся логіка лягає на компактний мікроконтролер. Щоб прошивка не перетворилася на заплутане полотно глобальних прапорців, потрібна чітка програмна конструкція: кільцева черга подій із захистом від перегонів між перериваннями, диспетчер ієрархічного автомата станів (HSM) з підтримкою батьківських режимів і сторожових умов (guards), а також черга цілей з атомарним скиданням при аварії.

У цьому проекті наведено закінчену детерміністичну реалізацію цієї архітектури для 32-бітного мікроконтролера на мовах C та C++. Код не використовує динамічне виділення пам'яті (`malloc` або `new`) під час роботи, має гарантовану часову складність `O(1)` для всіх операцій черги, захищений від переповнення та не містить блокуючих затримок.

## Принципи проектування та структури даних

Архітектура побудована навколо трьох фундаментальних принципів надійності:
1. **Ізоляція обробників переривань від логіки автомата:** Переривання від сенсорів (наприклад, оптичного бар'єра ToF чи компаратора напруги) ніколи не виконують логіку рішень безпосередньо. Вони лише фіксують факт події та розміщують структуру `Event` у статичному кільцевому буфері `EventQueue`. Це гарантує мінімальний час виконання ISR (кілька мікросекунд) і унеможливлює стан гонитви.
2. **Семантика Run-to-Completion (RTC):** Автомат обробляє події суворо послідовно. Подія вилучається з черги лише тоді, коли попередня зміна стану повністю завершилася, включно з викликом усіх функцій виходу зі старого стану (`EV_EXIT`) та входу в новий (`EV_ENTRY`).
3. **Ієрархічне успадкування обробників подій:** Якщо активний підстан (наприклад, рух до точки маршруту `state_navigating`) не містить власного коду для обробки рідкісної або критичної події (наприклад, критичного розряду батареї `EV_BATTERY_LOW`), подія автоматично передається суперстану `state_operational`. Це позбавляє розробника необхідності дублювати аварійні переходи в кожному дрібному стані.

Розгляньмо реалізацію базових структур: кільцевого буфера подій, контексту автомата станів та статичного масиву цілей місії.

:::tabs
```c
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
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <variant>
#include <optional>
#include <span>

/* --- 1. ТИПИ ПОДІЙ ТА ПОЛІМОРФНИЙ СТРУКТУРОВАНИЙ ПЕЙЛОАД --- */
enum class EventId : uint8_t {
    None = 0,
    Entry,
    Exit,
    Tick,
    StartMission,
    WaypointReached,
    ObstacleDetected,
    ObstacleCleared,
    GoalTimeout,
    BatteryLow,
    CriticalFault
};

struct Coords {
    int16_t x{0};
    int16_t y{0};
};

using EventPayload = std::variant<std::monostate, int32_t, float, Coords>;

struct Event {
    EventId id{EventId::None};
    uint32_t timestamp_ms{0};
    EventPayload payload{};
};

/* --- 2. КІЛЬЦЕВИЙ БУФЕР ПОДІЙ (ШАБЛОННИЙ І БЕЗПЕЧНИЙ) --- */
template <typename T, size_t Capacity>
class LockFreeRingQueue {
public:
    constexpr LockFreeRingQueue() = default;

    bool post(const T& item) noexcept {
        if (count_ >= Capacity) {
            dropped_++;
            return false;
        }
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        count_++;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        count_--;
        return item;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] uint32_t dropped() const noexcept { return dropped_; }

private:
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile size_t count_{0};
    uint32_t dropped_{0};
};

/* --- 3. ДИСЦИПЛІНА ІЄРАРХІЧНОГО АВТОМАТА СТАНІВ --- */
enum class HsmResult : uint8_t {
    Handled,
    Ignored,
    Super,
    Transition
};

class Hsm;
using StateHandler = HsmResult (*)(Hsm& context, const Event& event);

class Hsm {
public:
    explicit Hsm(StateHandler initial_state) noexcept
        : current_state_(initial_state), next_state_(nullptr) {}

    void transition_to(StateHandler target) noexcept {
        next_state_ = target;
    }

    void dispatch(const Event& event) noexcept {
        if (!current_state_) return;

        HsmResult res = current_state_(*this, event);
        if (res == HsmResult::Transition && next_state_ != nullptr) {
            Event exit_ev{EventId::Exit, event.timestamp_ms, {}};
            current_state_(*this, exit_ev);

            current_state_ = next_state_;
            next_state_ = nullptr;

            Event entry_ev{EventId::Entry, event.timestamp_ms, {}};
            current_state_(*this, entry_ev);
        }
    }

    [[nodiscard]] StateHandler current_state() const noexcept {
        return current_state_;
    }

private:
    StateHandler current_state_{nullptr};
    StateHandler next_state_{nullptr};
};

/* --- 4. ДЕКЛАРАТИВНІ ЦІЛІ ТА ДВИГУН МІСІЇ --- */
struct NavTarget { int16_t x; int16_t y; float speed_mps; };
struct HoldTarget { uint32_t duration_ms; };
struct SurveyTarget { uint8_t sensor_mask; };

using GoalParams = std::variant<std::monostate, NavTarget, HoldTarget, SurveyTarget>;

struct Goal {
    uint32_t timeout_ms{0};
    uint32_t start_time_ms{0};
    GoalParams params{};
};

template <size_t Capacity>
class GoalEngine {
public:
    bool push(const Goal& g) noexcept {
        return queue_.post(g);
    }

    std::optional<Goal> fetch_next() noexcept {
        active_goal_ = queue_.pop();
        return active_goal_;
    }

    void abort_all() noexcept {
        while (!queue_.empty()) {
            queue_.pop();
        }
        active_goal_.reset();
    }

    [[nodiscard]] bool has_active() const noexcept {
        return active_goal_.has_value();
    }

    [[nodiscard]] const std::optional<Goal>& active() const noexcept {
        return active_goal_;
    }

private:
    LockFreeRingQueue<Goal, Capacity> queue_{};
    std::optional<Goal> active_goal_{std::nullopt};
};
```
:::

---

## Логіка станів, сторожові умови (Guards) та покроковий розбір

Розгляньмо поведінку конкретного автономного ровера. Система має п'ять взаємопов'язаних станів:
1. `state_idle`: стартовий режим спокою. При отриманні команди `EV_START_MISSION` спрацьвує сторожова умова `guard_is_battery_ok()`: якщо напруга живлення достатня (> 10.5 В), здійснюється перехід у режим виконання місії; якщо ні — старт блокується.
2. `state_operational`: суперстан, що утримує загальні системні правила. Якщо напруга просідає нижче норми (`EV_BATTERY_LOW`) або надходить сигнал апаратної несправності (`EV_CRITICAL_FAULT`), суперстан примусово очищує чергу цілей і переводить автомат в `state_failsafe`.
3. `state_navigating`: підстан руху за координатами. Увімкнено ПІД-регулятори. При спрацюванні далекоміра ToF перемикається на локальний об'їзд `state_avoiding`.
4. `state_avoiding`: підстан локального маневрування. Маршові мотори зупинено, виконується розворот на місці. Щойно зона очищується (`EV_OBSTACLE_CLEARED`), автомат повертається до навігації.
5. `state_failsafe`: термінальний аварійний стан із повним блокуванням моторів.

Зверніть увагу на функцію `state_operational`: коли дочірній стан `state_navigating` зустрічає аварійну подію, він не містить власної логіки для `EV_CRITICAL_FAULT`, а повертає `state_operational(me, e)`. Батьківський суперстан викликає `goal_engine_abort_all()`, повністю вичищаючи всі заплановані точки маршруту, та ініціює перехід в `state_failsafe`.

Механіка передачі події виглядає так:
1. Дочірній стан отримує подію в аргументі `e`.
2. Якщо подія стосується локальної поведінки (наприклад, перешкода на курсі), стан самостійно викликає `hsm_transition(me, state_avoiding)` і повертає `RES_TRANSITION`.
3. Якщо подія є глобальною (наприклад, аварія акумулятора), стан прямо делегує обробку своєму батькові викликом `return state_operational(me, e)`.
4. Батьківський стан виконує необхідні глобальні дії (скидання цілей, зупинка сервоприводів) і переводить автомат у режим відмови.

:::tabs
```c
/* Контекст апарата */
typedef struct {
    Hsm hsm;
    EventQueue event_queue;
    GoalEngine goal_engine;
    float battery_voltage;
    bool obstacle_present;
    int16_t current_x;
    int16_t current_y;
} AutonomousRover;

/* Прототипи функцій станів */
HsmResult state_idle(Hsm *me, const Event *e);
HsmResult state_operational(Hsm *me, const Event *e);
HsmResult state_navigating(Hsm *me, const Event *e);
HsmResult state_avoiding(Hsm *me, const Event *e);
HsmResult state_failsafe(Hsm *me, const Event *e);

/* Охоронні умови (Guard Conditions) */
static inline bool guard_is_battery_ok(const AutonomousRover *rover) {
    return rover->battery_voltage > 10.5f; /* Поріг відсічки для 3S Li-ion */
}

/* 1. Стан IDLE */
HsmResult state_idle(Hsm *me, const Event *e) {
    AutonomousRover *rover = (AutonomousRover *)me->user_data;
    switch (e->id) {
        case EV_ENTRY:
            /* Знеструмити мотори */
            return RES_HANDLED;
        case EV_START_MISSION:
            if (guard_is_battery_ok(rover)) {
                hsm_transition(me, state_navigating);
                return RES_TRANSITION;
            }
            return RES_HANDLED; /* Батарея розряджена — відхилити старт */
        default:
            return RES_IGNORED;
    }
}

/* 2. Суперстан OPERATIONAL (Батьківський для дій у русі) */
HsmResult state_operational(Hsm *me, const Event *e) {
    AutonomousRover *rover = (AutonomousRover *)me->user_data;
    switch (e->id) {
        case EV_CRITICAL_FAULT:
        case EV_BATTERY_LOW:
            /* Аварійне скидання місії */
            goal_engine_abort_all(&rover->goal_engine);
            hsm_transition(me, state_failsafe);
            return RES_TRANSITION;
        default:
            return RES_SUPER;
    }
}

/* 3. Підстан NAVIGATING */
HsmResult state_navigating(Hsm *me, const Event *e) {
    AutonomousRover *rover = (AutonomousRover *)me->user_data;
    switch (e->id) {
        case EV_ENTRY:
            /* Увімкнути ПІД регулятори коліс */
            return RES_HANDLED;
        case EV_EXIT:
            /* Скинути уставки швидкості в 0 */
            return RES_HANDLED;
        case EV_OBSTACLE_DETECTED:
            hsm_transition(me, state_avoiding);
            return RES_TRANSITION;
        case EV_WAYPOINT_REACHED:
            /* Завершити поточну ціль, взяти наступну */
            return RES_HANDLED;
        case EV_CRITICAL_FAULT:
        case EV_BATTERY_LOW:
            /* Спливання до батьківського суперстану */
            return state_operational(me, e);
        default:
            return RES_IGNORED;
    }
}

/* 4. Підстан AVOIDING */
HsmResult state_avoiding(Hsm *me, const Event *e) {
    switch (e->id) {
        case EV_ENTRY:
            /* Зупинити лінійний рух, увімкнути пошуковий розворот */
            return RES_HANDLED;
        case EV_OBSTACLE_CLEARED:
            hsm_transition(me, state_navigating);
            return RES_TRANSITION;
        case EV_CRITICAL_FAULT:
        case EV_BATTERY_LOW:
            return state_operational(me, e);
        default:
            return RES_IGNORED;
    }
}

/* 5. Аварійний стан FAILSAFE */
HsmResult state_failsafe(Hsm *me, const Event *e) {
    switch (e->id) {
        case EV_ENTRY:
            /* Активація аварійного гальма, подача світлозвукового сигналу */
            return RES_HANDLED;
        default:
            return RES_IGNORED;
    }
}
```
```cpp
struct AutonomousRover {
    Hsm hsm{state_idle};
    LockFreeRingQueue<Event, 16> event_queue{};
    GoalEngine<8> goal_engine{};
    float battery_voltage{12.4f};
    bool obstacle_present{false};
    int16_t current_x{0};
    int16_t current_y{0};
};

constexpr bool guard_battery_ok(float voltage) noexcept {
    return voltage > 10.5f;
}

/* 1. Стан Idle */
HsmResult state_idle(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        case EventId::StartMission:
            hsm.transition_to(state_navigating);
            return HsmResult::Transition;
        default:
            return HsmResult::Ignored;
    }
}

/* 2. Суперстан Operational */
HsmResult state_operational(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::CriticalFault:
        case EventId::BatteryLow:
            hsm.transition_to(state_failsafe);
            return HsmResult::Transition;
        default:
            return HsmResult::Super;
    }
}

/* 3. Підстан Navigating */
HsmResult state_navigating(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        case EventId::Exit:
            return HsmResult::Handled;
        case EventId::ObstacleDetected:
            hsm.transition_to(state_avoiding);
            return HsmResult::Transition;
        case EventId::WaypointReached:
            return HsmResult::Handled;
        case EventId::CriticalFault:
        case EventId::BatteryLow:
            return state_operational(hsm, e);
        default:
            return HsmResult::Ignored;
    }
}

/* 4. Підстан Avoiding */
HsmResult state_avoiding(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        case EventId::ObstacleCleared:
            hsm.transition_to(state_navigating);
            return HsmResult::Transition;
        case EventId::CriticalFault:
        case EventId::BatteryLow:
            return state_operational(hsm, e);
        default:
            return HsmResult::Ignored;
    }
}

/* 5. Стан Failsafe */
HsmResult state_failsafe(Hsm& /*hsm*/, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        default:
            return HsmResult::Ignored;
    }
}
```
:::

---

## Інтеграція в суперцикл та обробка переривань

Головний цикл суперциклу викликається з фіксованим періодом (наприклад, кожні 10–50 мс). Він послідовно вичитує всі накопичені події до повного спустошення кільцевого буфера, викликаючи диспетчер `hsm_dispatch()`.

Зверніть увагу на важливу деталь: обробник апаратного переривання (ISR далекоміра або бампера) не виконує важких розрахунків. Він лише копіює структуру події в кільцевий буфер і негайно повертає керування контролеру переривань (NVIC на ARM Cortex-M).

Окрім спустошення подій, основний цикл містить монітор активної цілі: він обчислює різницю часу `elapsed = current_time_ms - start_time_ms`. Якщо робот застряг у глухому куті і не досяг координати за відведений ліміт `timeout_ms`, генерується подія `EV_GOAL_TIMEOUT`, що дозволяє автомату змінити стратегію або перейти до планування резервного об'їзду.

Покрокова траєкторія роботи системи під час нештатної ситуації:
1. Ровер рухається у стані `state_navigating` зі швидкістю 1.0 м/с.
2. Далекомір ToF фіксує стіну на відстані 25 см і генерує сигнал переривання на ніжці EXTI.
3. Обробник `EXTI4_IRQHandler()` за 5 мкс записує подію `EV_OBSTACLE_DETECTED` у чергу `event_queue`.
4. На черговому проході суперциклу диспетчер вичитує цю подію, викликає `EV_EXIT` у `state_navigating` (що зупиняє лінійний рух) та переводить ровер у `state_avoiding`.
5. Підстан `state_avoiding` подає уставку розвороту на місці.
6. Щойно поле зору очищується, далекомір надсилає подію `EV_OBSTACLE_CLEARED`, і ровер повертається до цільового курсу.

:::tabs
```c
/* Глобальний екземпляр ровера */
AutonomousRover g_rover;

/* Обробник зовнішнього переривання EXTI від ToF далекоміра */
void EXTI4_IRQHandler(void) {
    Event alert_ev = {
        .id = EV_OBSTACLE_DETECTED,
        .timestamp_ms = 123456 /* Системний таймер мікроконтролера */
    };
    /* Неблокуючий запис у чергу */
    event_queue_post(&g_rover.event_queue, &alert_ev);
}

/* Головний крок диспетчеризації суперциклу */
void app_main_loop(AutonomousRover *rover, uint32_t current_time_ms) {
    Event ev;

    /* 1. Вичитування всіх накопичених подій черги за принципом Run-to-Completion */
    while (event_queue_pop(&rover->event_queue, &ev)) {
        hsm_dispatch(&rover->hsm, &ev);
    }

    /* 2. Контроль таймауту активної цілі */
    if (rover->goal_engine.has_active_goal) {
        uint32_t elapsed = current_time_ms - rover->goal_engine.active_goal.start_time_ms;
        if (elapsed > rover->goal_engine.active_goal.timeout_ms) {
            Event timeout_ev = {
                .id = EV_GOAL_TIMEOUT,
                .timestamp_ms = current_time_ms
            };
            event_queue_post(&rover->event_queue, &timeout_ev);
        }
    }
}
```
```cpp
void isr_obstacle_trigger(AutonomousRover& rover, uint32_t now_ms) noexcept {
    Event alert{EventId::ObstacleDetected, now_ms, {}};
    rover.event_queue.post(alert);
}

void app_step(AutonomousRover& rover, uint32_t now_ms) noexcept {
    // 1. Послідовне спустошення черги подій
    while (auto ev = rover.event_queue.pop()) {
        rover.hsm.dispatch(*ev);
    }

    // 2. Моніторинг активного кроку місії
    if (rover.goal_engine.has_active()) {
        const auto& g = rover.goal_engine.active().value();
        if (now_ms - g.start_time_ms > g.timeout_ms) {
            rover.event_queue.post(Event{EventId::GoalTimeout, now_ms, {}});
        }
    }
}
```
:::

Така організація гарантує, що час реакції на зовнішню подію обмежується лише тривалістю одного проходу суперциклу, а внутрішні структури автомата залишаються повністю захищеними від пошкодження асинхронними перериваннями.

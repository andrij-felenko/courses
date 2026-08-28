# 📋 Інтерфейс диспетчера подій та черги автономних цілей

Цей документ описує відкритий програмний контракт (API, від англ. *Application Programming Interface*) та структуру даних ядра автономного прийняття рішень для вбудованих систем. Архітектура розрахована на мікроконтролери без використання важких сторонніх автопілотів (таких як PX4 чи ArduPilot) та забезпечує повний детермінізм виконання: нульове динамічне виділення пам'яті в робочому циклі, безпечний обмін даними між апаратними перериваннями (ISR) та основним потоком, а також сталу часову складність `O(1)` для всіх базових черг.

Інтерфейс розділено на три функціональні підсистеми:
1. **Підсистема черги подій (`EventQueue`):** асинхронна буферизація сигналів від датчиків і таймерів із захистом критичних секцій.
2. **Підсистема ієрархічного автомата станів (`HSM`):** диспетчеризація подій за моделлю Run-to-Completion із підтримкою вкладеності режимів, функцій входу/виходу та сторожових умов.
3. **Підсистема черги цілей місії (`GoalEngine`):** облік, валідація, запуск, моніторинг та безпечне аварійне скасування декларативних просторових завдань.

---

## 1. Типи даних та структура подій (Event System)

Подія в системі — це фіксована за розміром структура, яка передає факт виникнення явища (внутрішнього таймера чи зовнішнього сигналу сенсора) разом із міткою часу та параметричним корисним навантаженням.

Пріоритет події кодується полем `priority`: значення `0` зарезервовано для екстрених апаратних аварій (спрацювання бампера чи перевантаження за струмом), значення `128` використовується для штатних навігаційних подій, а значення `255` — для низькопріоритетної телеметрії. Структуроване об'єднання `union` у C або поліморфний `std::variant` у C++ гарантують, що розмір структури `Event` залишається строго сталим (16 байтів), унеможливлюючи фрагментацію стека або купи.

Кожна подія супроводжується монотонною міткою часу `timestamp_us`, яка зчитується з апаратного лічильника мікросекунд (наприклад, DWT-таймера ядра ARM Cortex-M). Це дозволяє диспетчеру відстежувати вік події та виявляти застарілі пакети, що затрималися в черзі довше допустимого дедлайну.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EV_SYS_NONE             = 0x00, /* Порожня подія (відсутність сигналу) */
    EV_SYS_ENTRY            = 0x01, /* Вхід у стан (викликається диспетчером) */
    EV_SYS_EXIT             = 0x02, /* Вихід зі стану */
    EV_SYS_INIT             = 0x03, /* Внутрішня ініціалізація підстанів */
    EV_CMD_START_MISSION    = 0x10, /* Команда запуску виконання черги цілей */
    EV_CMD_PAUSE_MISSION    = 0x11, /* Команда тимчасової зупинки на місці */
    EV_CMD_RESUME_MISSION   = 0x12, /* Поновлення раніше зупиненого руху */
    EV_CMD_ABORT_MISSION    = 0x13, /* Примусове аварійне скасування місії */
    EV_NAV_WAYPOINT_REACHED = 0x20, /* Цільову точку маршруту досягнуто */
    EV_NAV_HEADING_LOCKED   = 0x21, /* Кут курсу стабілізовано в межах допуску */
    EV_NAV_OBSTACLE_NEAR    = 0x22, /* Попередження далекоміра: зона маневрування */
    EV_NAV_OBSTACLE_STOP    = 0x23, /* Критична дистанція: екстрене зупинення */
    EV_NAV_PATH_CLEAR       = 0x24, /* Перешкода зникла з поля зору сенсорів */
    EV_FAIL_BATTERY_LOW     = 0x40, /* Напруга акумулятора нижче робочого порогу */
    EV_FAIL_SENSOR_TIMEOUT  = 0x41, /* Сенсор не надав відліку у відведений слот */
    EV_FAIL_ACTUATOR_STALL  = 0x42, /* Перевантаження або зупинка мотора за струмом */
    EV_FAIL_CRITICAL        = 0x4F  /* Загальна фатальна відмова обладнання */
} EventId;

typedef struct {
    uint8_t id;             /* Ідентифікатор події (тип EventId) */
    uint8_t priority;       /* Пріоритет: 0 — найвищий (ISR), 255 — фоновий */
    uint16_t reserved;      /* Вирівнювання структури до межі 4 байтів */
    uint32_t timestamp_us;  /* Системна мітка часу в мікросекундах */
    union {
        int32_t  i32;       /* Знаковий 32-бітний параметр */
        float    f32;       /* Значення з рухомою комою */
        uint32_t u32;       /* Беззнаковий параметр або бітова маска */
        struct {
            int16_t x_mm;   /* Координата X у міліметрах */
            int16_t y_mm;   /* Координата Y у міліметрах */
        } nav_pt;
        struct {
            uint16_t sensor_id;
            uint16_t error_code;
        } fault;
    } param;
} Event;
```
```cpp
#include <cstdint>
#include <variant>

enum class EventId : uint8_t {
    SysNone             = 0x00,
    SysEntry            = 0x01,
    SysExit             = 0x02,
    SysInit             = 0x03,
    CmdStartMission     = 0x10,
    CmdPauseMission     = 0x11,
    CmdResumeMission    = 0x12,
    CmdAbortMission     = 0x13,
    NavWaypointReached  = 0x20,
    NavHeadingLocked    = 0x21,
    NavObstacleNear     = 0x22,
    NavObstacleStop     = 0x23,
    NavPathClear        = 0x24,
    FailBatteryLow      = 0x40,
    FailSensorTimeout   = 0x41,
    FailActuatorStall   = 0x42,
    FailCritical        = 0x4F
};

struct Point2D {
    int16_t x_mm{0};
    int16_t y_mm{0};
};

struct FaultInfo {
    uint16_t sensor_id{0};
    uint16_t error_code{0};
};

using EventPayload = std::variant<std::monostate, int32_t, float, uint32_t, Point2D, FaultInfo>;

struct Event {
    EventId id{EventId::SysNone};
    uint8_t priority{128};
    uint32_t timestamp_us{0};
    EventPayload param{};
};
```
:::

---

## 2. Структури та дескриптори цілей місії (Goal Engine)

Ціль представляє високорівневе просторове або часове завдання. На відміну від миттєвої події, ціль має життєвий цикл і тривалість виконання. Кожна ціль містить вказівник на специфічний деструктор `on_abort_cleanup()`. Якщо ціль переривається через аварію або таймаут, цей хук викликається до зміни стану автомата, гарантуючи переведення апаратних вузлів (шпинделів, лазерних випромінювачів, захватів) у безпечний стан.

Дескриптор цілі має фіксований розмір і містить параметри навігації (координати цілі, швидкість круїзу, радіус допуску) або параметри інспекції (тривалість утримання, маска сканування).

:::tabs
```c
typedef enum {
    GOAL_TYPE_NONE          = 0,
    GOAL_TYPE_WAYPOINT      = 1, /* Рух у задану точку із заданою швидкістю */
    GOAL_TYPE_HOLD_HEADING  = 2, /* Стабілізація та утримання курсу впродовж часу */
    GOAL_TYPE_STATION_KEEP  = 3, /* Утримання позиції на місці з автопідрулюванням */
    GOAL_TYPE_INSPECT_SCAN  = 4, /* Сканування сектору датчиком або камерою */
    GOAL_TYPE_PAYLOAD_DROP  = 5  /* Активація механізму скидання вантажу */
} GoalType;

typedef enum {
    GOAL_STATUS_PENDING     = 0, /* Ціль очікує своєї черги у кільцевому буфері */
    GOAL_STATUS_ACTIVE      = 1, /* Ціль виконується в поточному стані */
    GOAL_STATUS_SUCCEEDED   = 2, /* Критерій досягнення успішно виконано */
    GOAL_STATUS_TIMEOUT     = 3, /* Перевищено граничний час виконання */
    GOAL_STATUS_ABORTED     = 4  /* Ціль примусово скасовано аварійним скиданням */
} GoalStatus;

typedef struct {
    uint8_t  type;               /* GoalType */
    uint8_t  status;             /* GoalStatus */
    uint16_t goal_id;            /* Унікальний ідентифікатор завдання */
    uint32_t timeout_ms;         /* Максимально допустимий час на виконання */
    uint32_t start_time_ms;      /* Момент старту кроку в мілісекундах */
    union {
        struct {
            int32_t target_x_mm;
            int32_t target_y_mm;
            float   cruise_speed_mps;
            float   acceptance_radius_mm;
        } waypoint;
        struct {
            uint32_t duration_ms;
            float    target_yaw_rad;
        } hold;
        struct {
            uint8_t  pattern_id;
            uint16_t sample_count;
        } scan;
    } args;
    /* Деструктор специфічного очищення при аварії */
    void (*on_abort_cleanup)(void *context);
} Goal;
```
```cpp
enum class GoalType : uint8_t {
    None = 0,
    Waypoint,
    HoldHeading,
    StationKeep,
    InspectScan,
    PayloadDrop
};

enum class GoalStatus : uint8_t {
    Pending = 0,
    Active,
    Succeeded,
    Timeout,
    Aborted
};

struct WaypointArgs {
    int32_t target_x_mm{0};
    int32_t target_y_mm{0};
    float cruise_speed_mps{1.0f};
    float acceptance_radius_mm{200.0f};
};

struct HoldArgs {
    uint32_t duration_ms{0};
    float target_yaw_rad{0.0f};
};

struct ScanArgs {
    uint8_t pattern_id{0};
    uint16_t sample_count{0};
};

using GoalArgs = std::variant<std::monostate, WaypointArgs, HoldArgs, ScanArgs>;

struct Goal {
    GoalType type{GoalType::None};
    GoalStatus status{GoalStatus::Pending};
    uint16_t goal_id{0};
    uint32_t timeout_ms{0};
    uint32_t start_time_ms{0};
    GoalArgs args{};
    void (*on_abort_cleanup)(void* context){nullptr};
};
```
:::

---

## 3. Контракт функцій черги подій (`EventQueue`)

Модуль черги подій надає статичний кільцевий буфер, оптимізований для атомарного додавання даних із переривань та послідовного вичитування в основному суперциклі.

### Правила взаємодії з апаратними перериваннями (Concurrency Rules)
1. **Функція `event_queue_post()`:** призначена для додавання подій із будь-якого контексту. На ядрах ARM Cortex-M функція зберігає стан регістра `PRIMASK` і вимикає глобальні переривання на час запису елемента в буфер (тривалість критичної секції ≤ 1.2 мкс при частоті 64 МГц).
2. **Функція `event_queue_pop()`:** викликається виключно в основному потоці виконання (суперцикл або задача RTOS). Виклик `pop()` з обробників переривань заборонений, оскільки обробка логіки повинна відбуватися детерміністично в межах чергового слота часу.
3. **Поведінка при переповненні:** якщо буфер заповнено на 100%, функція не блокує виконання й не викликає системних панік, а повертає `false` та інкрементує лічильник втрачених подій `overflow_drops`. Це дозволяє діагностувати сплески навантаження в логах телеметрії.
4. **Атомарність покажчиків:** оскільки змінні `head`, `tail` та `count` мають розмір 8 або 32 біти, на архітектурах ARM Cortex-M операції їхнього читання та запису є природно атомарними на рівні машинних інструкцій `LDR`/`STR`. Кваліфікатор `volatile` захищає покажчики від агресивної оптимізації компілятора та кешування в регістрах.

:::tabs
```c
typedef struct {
    Event *buffer;
    size_t capacity;
    volatile size_t head;
    volatile size_t tail;
    volatile size_t count;
    uint32_t overflow_drops;
} EventQueue;

void event_queue_init(EventQueue *q, Event *buffer, size_t capacity);
bool event_queue_post(EventQueue *q, const Event *ev);
bool event_queue_pop(EventQueue *q, Event *out_ev);
bool event_queue_peek(const EventQueue *q, Event *out_ev);
void event_queue_clear(EventQueue *q);
size_t event_queue_get_count(const EventQueue *q);
```
```cpp
#include <array>
#include <optional>
#include <span>

template <size_t Capacity>
class EventQueue {
public:
    constexpr EventQueue() = default;

    bool post(const Event& ev) noexcept;
    std::optional<Event> pop() noexcept;
    [[nodiscard]] std::optional<Event> peek() const noexcept;
    void clear() noexcept;
    [[nodiscard]] size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    [[nodiscard]] uint32_t drops() const noexcept;

private:
    std::array<Event, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile size_t count_{0};
    uint32_t overflow_drops_{0};
};
```
:::

---

## 4. Контракт ієрархічного автомата станів (`HSM`)

Диспетчер ієрархічного автомата забезпечує виклик обробників згідно з принципом Run-to-Completion.

### Семантика повернення `HsmResult`
Кожен обробник стану зобов'язаний повернути одне з чотирьох значень:
- **`RES_HANDLED`:** Подію повністю оброблено поточним станом. Жодних подальших дій або переходів не вимагається.
- **`RES_IGNORED`:** Подія не має значення для поточного стану. Диспетчер зупиняє обробку.
- **`RES_SUPER`:** Поточний підстан не знає, як обробити подію. Диспетчер автоматично піднімається по дереву ієрархії та викликає обробник батьківського суперстану.
- **`RES_TRANSITION`:** Поточний стан ініціював зміну режиму через `hsm_transition()`. Диспетчер послідовно виконує вихід зі старого стану (`EV_SYS_EXIT`), призначає новий активний вказівник і викликає обробник входу (`EV_SYS_ENTRY`).

Під час виконання переходу між станами заборонено викликати блокуючі функції очікування периферії (`delay`). Будь-яка дія, що вимагає часу (наприклад, розгін моторів чи калібрування компаса), оформлюється як окремий проміжний стан автомата.

:::tabs
```c
typedef enum {
    RES_HANDLED,
    RES_IGNORED,
    RES_SUPER,
    RES_TRANSITION
} HsmResult;

struct Hsm;
typedef HsmResult (*StateHandler)(struct Hsm *me, const Event *ev);

typedef struct Hsm {
    StateHandler current_state;
    StateHandler next_state;
    void *user_context;
} Hsm;

void hsm_init(Hsm *me, StateHandler initial_state, void *user_context);
void hsm_dispatch(Hsm *me, const Event *ev);
void hsm_transition(Hsm *me, StateHandler target_state);
```
```cpp
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
    explicit Hsm(StateHandler initial_state, void* context = nullptr) noexcept;
    void dispatch(const Event& ev) noexcept;
    void transition_to(StateHandler target) noexcept;
    [[nodiscard]] StateHandler current_state() const noexcept;
    [[nodiscard]] void* context() noexcept;

private:
    StateHandler current_state_{nullptr};
    StateHandler next_state_{nullptr};
    void* user_context_{nullptr};
};
```
:::

---

## 5. Контракт черги цілей (`GoalEngine`) та аварійного скасування

Модуль `GoalEngine` керує чергою просторових завдань і взаємодіє з автоматом станів через події досягнення мети (`EV_NAV_WAYPOINT_REACHED`) або вичерпання ліміту часу (`EV_FAIL_SENSOR_TIMEOUT` чи `EV_CMD_ABORT_MISSION`).

### Протокол безпечного скасування (Emergency Abort Protocol)
Коли стається критичний збій (аварійне спрацювання бампера, перегрів силової плати чи глибокий розряд батареї), викликається функція `goal_engine_abort_all()`:
1. Якщо в системі є активна мета, негайно викликається її індивідуальний деструктор `on_abort_cleanup()` (який скидає тиск, паркує захвати чи зупиняє шпинделі).
2. Кільцевий буфер цілей повністю очищується за час `O(1)`.
3. У чергу подій надсилається повідомлення `EV_FAIL_CRITICAL`, що переводить HSM в аварійний термінальний стан.

Функція `goal_engine_step()` викликається періодично в суперциклі. Вона перевіряє, чи не перевищив час виконання активної цілі ліміт `timeout_ms`. Якщо робот застряг перед непереборною перешкодою й не досяг радіусу допуску, функція автоматично публікує подію `EV_FAIL_SENSOR_TIMEOUT` або `EV_CMD_ABORT_MISSION` у вихідну чергу.

:::tabs
```c
typedef struct {
    Goal *buffer;
    size_t capacity;
    uint8_t head;
    uint8_t tail;
    uint8_t count;
    Goal active_goal;
    bool has_active_goal;
    void *context;
} GoalEngine;

void goal_engine_init(GoalEngine *ge, Goal *buffer, size_t capacity, void *ctx);
bool goal_engine_push(GoalEngine *ge, const Goal *goal);
bool goal_engine_fetch_next(GoalEngine *ge);
void goal_engine_step(GoalEngine *ge, uint32_t now_ms, EventQueue *out_queue);
void goal_engine_complete_active(GoalEngine *ge);
void goal_engine_abort_all(GoalEngine *ge);
```
```cpp
template <size_t Capacity>
class GoalEngine {
public:
    explicit GoalEngine(void* context = nullptr) noexcept;
    bool push(const Goal& goal) noexcept;
    std::optional<Goal> fetch_next() noexcept;
    void step(uint32_t now_ms, EventQueue<16>& out_queue) noexcept;
    void complete_active() noexcept;
    void abort_all() noexcept;
    [[nodiscard]] bool has_active() const noexcept;
    [[nodiscard]] const std::optional<Goal>& active() const noexcept;

private:
    std::array<Goal, Capacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
    std::optional<Goal> active_goal_{std::nullopt};
    void* context_{nullptr};
};
```
:::

---

## 6. Вимоги до пам'яті, детермінізму та апаратних ресурсів

Система спроєктована для виконання на 32-бітних мікроконтролерах із суворими апаратними рамками:

| Характеристика | Значення для конфігурації 16 подій + 8 цілей | Примітка |
|---|---|---|
| **Використання RAM (Static BSS)** | ~592 байти | Повна статична локалізація; купу (`heap`) не задіяно |
| **Використання Flash (Код)** | ~1.45 КБ | Компіляція з оптимізацією `-Os` під ARM Cortex-M4 |
| **Часова складність `push`/`pop`** | Строго `O(1)` | Без циклічного пошуку або динамічного ресайзингу |
| **Глибина викликів стека** | ≤ 144 байти | Заборонена непряма рекурсія в переходах станів |
| **Час блокування переривань** | ≤ 1.2 мкс | Час перебування всередині `ENTER_CRITICAL()` при 64 МГц |

### Інваріанти надійності та сумісність із MISRA C
- **Відсутність непрямої рекурсії:** Диспетчер HSM не дозволяє викликати `hsm_dispatch()` зсередини обробника стану. Усі вторинні події додаються в кінець черги.
- **Статичний детермінізм:** Розміри буферів задаються на етапі компіляції (`constexpr` / `#define`), що унеможливлює вичерпання пам'яті під час польоту або місії.
- **Ідемпотентність очищення:** Виклик `goal_engine_abort_all()` є безпечним за будь-якого стану черги, включно з порожнім буфером або відсутністю активного кроку.
- **Відсутність невизначеної поведінки при переповненні:** Кільцевий буфер відкидає нові події з фіксацією лічильника дропів, зберігаючи цілісність уже збережених критичних повідомлень.

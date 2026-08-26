# Автомат станів і черга подій у прошивці: детально

<preknowlist>
- [Super-loop](root:embedded/super-loop-limits) — межі лінійного неблокуючого циклу з millis(), затинка та комбінаторне зростання заплутаності перевірок.
- [Блокуючий і неблокуючий ввід-вивід](root:sf-tasks/blocking-vs-nonblocking-io) — чому delay() заморожує процесор і як розбивати операції на неподільні кроки.
- [Переривання](root:hw-arch/interrupts) — апаратні джерела сигналів, вимоги до мінімального часу виконання ISR та атомарність змінних.
- [Виробник–споживач](root:sf-tasks/producer-consumer) — організація кільцевої передачі даних між перериваннями та основним потоком виконання.
</preknowlist>

Уявімо контролер зарядної станції для електромобілів (EVSE). Пристрій комутує трифазну мережу 400 В струмом 32 А через силовий контактор, одночасно опитує аналоговий рівень лінії контрольного пілота (Control Pilot, CP), слухає зчитувач RFID-карток по шині UART, вимірює струм витоку трансформатором нульової послідовності та тримає на окремому вході кнопку аварійного вимкнення «Грибок». У наївному лінійному коді замикання силового контактора супроводжується паузою `delay(3000)` для очікування завершення перехідних процесів іскрогасіння та стабілізації напруги від лічильника енергії. У ці три секунди водій помічає задимлення зарядного кабелю і натискає кнопку аварійної зупинки. Але процесор мікроконтролера застряг усередині мертвого лічильного циклу: сигнал кнопки ігнорується, силове реле лишається замкненим, а через пошкоджений роз'єм продовжує текти струм у десятки ампер, спричиняючи відкриту пожежу.

Спроба «полагодити» цю проблему за допомогою розсипу глобальних змінних-прапорців (`bool is_authorized`, `bool relay_closed`, `bool timer_running`, `uint32_t t_start`) перетворює головний цикл на заплутане спагеті з вкладених умов `if-else`. Додавання лише одного нового режиму — наприклад, очікування зниженого нічного тарифу або вентиляції акумуляторного відсіку — вимагає переписування десятків взаємопов'язаних перевірок. Прошивка починає непередбачувано «залипати» в проміжних режимах, коли одна з двадцяти умов спрацьовує невчасно через електромагнітну заваду чи деренчання контактів.

Подійно-орієнтована архітектура (**Event-Driven Architecture**) на основі скінченних автоматів (**Finite State Machine**, FSM) та кільцевої черги подій докорінно змінює структуру програми: замість лінійного сценарію «що виконувати далі» прошивка формулюється як сукупність дискретних **станів**, які очікують на надходження асинхронних **подій** і реагують на них неподільними діями з фіксованим часом виконання.

![Порівняння лінійного блокуючого коду та подійно-орієнтованого автомата](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/img/spaghetti-vs-fsm.svg)
*Ліворуч — лінійний код із затримками, де процесор марнує час у delay() та пропускає аварійні події. Праворуч — неблокуючий цикл автомата, де кожна подія з черги виконується за лічені мікросекунди, забезпечуючи миттєву реакцію системи.*

---

### Чому спагеті з delay() та прапорців знищує надійність

Коли розробник викликає функцію `delay(5000)`, процесор мікроконтролера виконує мільйони порожніх інструкцій `NOP` у нескінченному лічильному циклі. Протягом цього інтервалу система залишається абсолютно сліпою до навколишнього світу, якщо не брати до уваги апаратні переривання. Але навіть якщо апаратне переривання від кнопки аварійної зупинки виставить прапорець `g_emergency_pressed = true`, головний потік виконання все одно не перевірить цей прапорець, доки не спливе весь 5-секундний інтервал затримки.

Найгірша затримка реакції системи (`L_worst`) у такій архітектурі дорівнює не часу опитування окремого давача, а сумі всіх блокуючих затримок та кроків обчислень усередині циклу:

```
L_worst = C_сенсори + delay(3000) + delay(2000) + C_дисплей ≈ 5000+ мс
```

Спроба позбутися `delay()` шляхом переходу на періодичні перевірки лічильника `millis()` або `SysTick` усуває затримку процесора, проте швидко виявляє іншу фундаментальну ваду — **комбінаторне розбухання простору станів**.

Якщо поведінка системи залежить від `M` незалежних булевих змінних-прапорців, кількість теоретично можливих конфігурацій становить:

```
Кількість конфігурацій = 2ᴹ
```

Уже при 8 прапорцях (`is_connected`, `is_charging`, `is_paused`, `is_fault`, `card_read`, `timer_active`, `overcurrent_latched`, `cable_locked`) прошивка має $2^8 = 256$ потенційних станів. Розробник здатний утримати в голові й протестувати від сили 10–15 типових сценаріїв. Решта 240 станів є «сірою зоною» — недокументованими конфігураціями, куди пристрій неминуче потрапляє через деренчання контактів, наведені електромагнітні завади чи несподіваний порядок надходження байтів з UART.

Скінченний автомат усуває цей хаос через примусове звуження простору станів: система **в будь-яку мить часу перебуває рівно в одному явно визначеному стані** зі строго обмеженого переліку.

---

### Математична модель скінченного автомата (FSM)

Формально скінченний автомат у дискретних вбудованих системах визначається як кортеж із п'яти елементів:

```
FSM = (S, E, δ, S₀, F)
```

де:
- `S` — скінченна множина взаємовиключних станів (`States`);
- `E` — скінченна множина вхідних сигналів або подій (`Events`);
- `δ` — функція переходів `δ : S × E → S`, що однозначно визначає наступний стан за парою «поточний стан + вхідна подія»;
- `S₀` — початковий стан системи (`Initial State`), у який вона переходить після скидання (Reset);
- `F` — множина кінцевих станів (для неперервно працюючих прошивок зазвичай порожня).

```
┌─────────────────────────────────────────────────────────────┐
│ Класичні типи автоматів:                                    │
│                                                             │
│ 1. Автомат Мура (Moore Machine):                            │
│    Вихідні сигнали залежать виключно від поточного стану:   │
│    Out = λ(S). Дія виконується протягом усього стану.       │
│                                                             │
│ 2. Автомат Мілі (Mealy Machine):                            │
│    Вихідні сигнали залежать від стану та вхідної події:     │
│    Out = λ(S, E). Дія прив'язана до моменту переходу.        │
│                                                             │
│ 3. Автомат з діями входу та виходу (Statecharts / UML FSM): │
│    Entry: гарантоване захоплення ресурсу при вході у стан.  │
│    Exit:  гарантоване звільнення ресурсу при виході зі стану│
└─────────────────────────────────────────────────────────────┘
```

#### Небезпека глітчів у моделі Мілі проти стабільності дій входу/виходу

У класичних автоматах Мілі дія виконується безпосередньо під час переходу між станами. Якщо апаратний вхідний сигнал зазнає короткочасного перешкодного сплеску (глітча), автомат може виконати дію (наприклад, подати імпульс на котушку контактора), навіть якщо перехід у новий стан не зафіксувався.

Найбільш надійною модифікацією для вбудованих систем є автомати з діями входу (**Entry Action**) та виходу (**Exit Action**). 

Уявімо стан `CHARGING`. Його апаратний інваріант простий: *силовий контактор замкнений, працює вентилятор охолодження*. Якщо перехід у стан аварії `FAULT` може статися через перегрів, перевищення струму, обрив пілота або натискання кнопки «Стоп», у класичному автоматі Мілі розробник мусив би прописати виклик `Relay_Open()` на **кожному окремому переході**. Забули вставити відключення реле в одному з п'яти обробників помилок — і в системі з'явилася смертельна дірка.

Дія виходу `Exit Action` виконується **завжди**, коли автомат покидає стан `CHARGING`, незалежно від того, яка саме подія спровокувала перехід. Дія входу `Entry Action` виконується **завжди**, коли автомат переходить у стан, гарантуючи правильну ініціалізацію апаратних вузлів.

![Анатомія кроку автомата: подія, перехід, дії входу та виходу](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/img/fsm-core-loop.svg)
*Порядок виконання операцій під час спрацьовування події EVT_START: спочатку відпрацьовує Exit-дія стану A, потім дія самого переходу, і нарешті Entry-дія стану B.*

Суворий порядок кроків під час переходу між станами:
1. Викликається `on_exit()` поточного стану `S_cur`;
2. Виконується дія самого переходу `action(e)` (якщо вона визначена);
3. Змінна поточного стану оновлюється: `current_state = S_next`;
4. Викликається `on_enter()` нового стану `S_next`.

Цей порядок гарантує збереження **інваріантів стану**: ресурси старого стану звільняються до того, як новий стан почне захоплювати свої ресурси.

---

### Три патерни реалізації автомата на C та C++

У практичній розробці мікроконтролерного ПЗ існує три основні способи реалізації FSM, кожен із яких має чіткий баланс між обсягом пам'яті, швидкодією та масштабованістю.

```
┌─────────────────┬────────────┬────────────┬─────────────────────────────┐
│ Патерн          │ Flash      │ RAM        │ Головна перевага            │
├─────────────────┼────────────┼────────────┼─────────────────────────────┤
│ 1. Switch-Case  │ Мінімальний│ 1 байт     │ Нульовий оверхед, простота  │
│ 2. Таблиця      │ Середній   │ 0 байтів   │ Декларативність, O(1) час   │
│ 3. Покажчики    │ Мінімальний│ 4-8 байтів │ Ідеальна інкапсуляція дій   │
└─────────────────┴────────────┴────────────┴─────────────────────────────┘
```

#### Патерн 1: Вкладений switch-case

Найбільш очевидний та розповсюджений підхід. Зовнішній `switch` перемикає стани, внутрішній — обробляє події.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATE_STANDBY,
    STATE_CONNECTED,
    STATE_CHARGING,
    STATE_FAULT
} FsmState;

typedef enum {
    EVT_PLUG_IN,
    EVT_AUTH_SUCCESS,
    EVT_UNPLUG,
    EVT_OVERCURRENT,
    EVT_RESET_BTN
} FsmEvent;

typedef struct {
    FsmState state;
    uint16_t current_ma;
    bool is_locked;
} EvseController;

void evse_fsm_dispatch(EvseController *ctx, FsmEvent evt) {
    switch (ctx->state) {
        case STATE_STANDBY:
            if (evt == EVT_PLUG_IN) {
                // Дія переходу
                ctx->is_locked = true;
                ctx->state = STATE_CONNECTED;
            }
            break;

        case STATE_CONNECTED:
            if (evt == EVT_AUTH_SUCCESS) {
                // Вмикаємо контактор
                ctx->state = STATE_CHARGING;
            } else if (evt == EVT_UNPLUG) {
                ctx->is_locked = false;
                ctx->state = STATE_STANDBY;
            }
            break;

        case STATE_CHARGING:
            if (evt == EVT_OVERCURRENT) {
                // Аварія: негайно розмикаємо реле
                ctx->state = STATE_FAULT;
            } else if (evt == EVT_UNPLUG) {
                ctx->is_locked = false;
                ctx->state = STATE_STANDBY;
            }
            break;

        case STATE_FAULT:
            if (evt == EVT_RESET_BTN) {
                ctx->state = STATE_STANDBY;
            }
            break;
    }
}
```
```cpp
#include <cstdint>

enum class FsmState : uint8_t {
    Standby,
    Connected,
    Charging,
    Fault
};

enum class FsmEvent : uint8_t {
    PlugIn,
    AuthSuccess,
    Unplug,
    Overcurrent,
    ResetBtn
};

class EvseController {
public:
    void dispatch(FsmEvent evt) noexcept {
        switch (state_) {
            case FsmState::Standby:
                if (evt == FsmEvent::PlugIn) {
                    is_locked_ = true;
                    state_ = FsmState::Connected;
                }
                break;

            case FsmState::Connected:
                if (evt == FsmEvent::AuthSuccess) {
                    state_ = FsmState::Charging;
                } else if (evt == FsmEvent::Unplug) {
                    is_locked_ = false;
                    state_ = FsmState::Standby;
                }
                break;

            case FsmState::Charging:
                if (evt == FsmEvent::Overcurrent) {
                    state_ = FsmState::Fault;
                } else if (evt == FsmEvent::Unplug) {
                    is_locked_ = false;
                    state_ = FsmState::Standby;
                }
                break;

            case FsmState::Fault:
                if (evt == FsmEvent::ResetBtn) {
                    state_ = FsmState::Standby;
                }
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return state_; }

private:
    FsmState state_{FsmState::Standby};
    uint16_t current_ma_{0};
    bool is_locked_{false};
};
```
:::

*Переваги:* мінімальний розмір двійкового коду, висока швидкість (компілятор зазвичай оптимізує плоский switch у пряму таблицю переходів асемблера `TBB`/`TBH` на ARM Cortex-M), відсутність непрямих викликів.
*Недоліки:* погана масштабованість. Коли автомат налічує понад 6 станів і десяток подій, функція перетворюється на нечиткий моноліт на сотні рядків, де складно контролювати парність дій Entry/Exit.

---

#### Патерн 2: Таблиця переходів (Декларативна матриця)

У цьому патерні граф переходів виноситься у статичну таблицю в Flash-пам'яті (через `const` або `constexpr`). Таблиця містить кортежі `[Поточний стан, Подія] -> [Наступний стан, Функція дії]`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATE_IDLE,
    STATE_ARMED,
    STATE_TRIGGERED,
    STATE_MAX
} SecurityState;

typedef enum {
    SIG_SENSOR_PIR,
    SIG_CODE_ENTERED,
    SIG_TIMEOUT,
    SIG_MAX
} SecuritySignal;

typedef struct SecurityFsm SecurityFsm;
typedef void (*TransitionAction)(SecurityFsm *fsm);

typedef struct {
    SecurityState next_state;
    TransitionAction action;
} TransitionEntry;

struct SecurityFsm {
    SecurityState state;
    bool siren_active;
};

// Дії переходів
static void act_sound_alarm(SecurityFsm *fsm) { fsm->siren_active = true; }
static void act_silence_alarm(SecurityFsm *fsm) { fsm->siren_active = false; }
static void act_arm_beep(SecurityFsm *fsm) { (void)fsm; /* короткий біп */ }

// Матриця переходів: рядок = стан, стовпчик = сигнал
static const TransitionEntry transition_table[STATE_MAX][SIG_MAX] = {
    [STATE_IDLE] = {
        [SIG_CODE_ENTERED] = { STATE_ARMED, act_arm_beep },
    },
    [STATE_ARMED] = {
        [SIG_SENSOR_PIR]   = { STATE_TRIGGERED, act_sound_alarm },
        [SIG_CODE_ENTERED] = { STATE_IDLE, NULL },
    },
    [STATE_TRIGGERED] = {
        [SIG_CODE_ENTERED] = { STATE_IDLE, act_silence_alarm },
        [SIG_TIMEOUT]      = { STATE_ARMED, act_silence_alarm },
    }
};

void security_fsm_dispatch(SecurityFsm *fsm, SecuritySignal sig) {
    if (fsm->state >= STATE_MAX || sig >= SIG_MAX) return;

    const TransitionEntry *t = &transition_table[fsm->state][sig];
    if (t->next_state != STATE_IDLE || t->action != NULL) {
        if (t->action) {
            t->action(fsm);
        }
        fsm->state = t->next_state;
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <functional>

enum class SecState : uint8_t {
    Idle,
    Armed,
    Triggered,
    Count
};

enum class SecSignal : uint8_t {
    SensorPir,
    CodeEntered,
    Timeout,
    Count
};

class SecurityFsm {
public:
    using ActionFn = void (*)(SecurityFsm&);

    struct Transition {
        SecState next{SecState::Idle};
        ActionFn action{nullptr};
        bool valid{false};
    };

    static void soundAlarm(SecurityFsm& fsm) noexcept { fsm.siren_active_ = true; }
    static void silenceAlarm(SecurityFsm& fsm) noexcept { fsm.siren_active_ = false; }

    void dispatch(SecSignal sig) noexcept {
        const auto& tr = table_[static_cast<size_t>(state_)][static_cast<size_t>(sig)];
        if (tr.valid) {
            if (tr.action) {
                tr.action(*this);
            }
            state_ = tr.next;
        }
    }

    [[nodiscard]] SecState state() const noexcept { return state_; }

private:
    SecState state_{SecState::Idle};
    bool siren_active_{false};

    static constexpr auto createTable() {
        std::array<std::array<Transition, static_cast<size_t>(SecSignal::Count)>, static_cast<size_t>(SecState::Count)> t{};
        
        t[static_cast<size_t>(SecState::Idle)][static_cast<size_t>(SecSignal::CodeEntered)] = 
            Transition{SecState::Armed, nullptr, true};
            
        t[static_cast<size_t>(SecState::Armed)][static_cast<size_t>(SecSignal::SensorPir)] = 
            Transition{SecState::Triggered, &SecurityFsm::soundAlarm, true};
        t[static_cast<size_t>(SecState::Armed)][static_cast<size_t>(SecSignal::CodeEntered)] = 
            Transition{SecState::Idle, nullptr, true};
            
        t[static_cast<size_t>(SecState::Triggered)][static_cast<size_t>(SecSignal::CodeEntered)] = 
            Transition{SecState::Idle, &SecurityFsm::silenceAlarm, true};
        t[static_cast<size_t>(SecState::Triggered)][static_cast<size_t>(SecSignal::Timeout)] = 
            Transition{SecState::Armed, &SecurityFsm::silenceAlarm, true};
            
        return t;
    }

    static constexpr auto table_ = createTable();
};
```
:::

*Переваги:* повна декларативність і наочність; граф переходів можна перевіряти статичними аналізаторами безпосередньо з матриці. Час обробки фіксований і становить O(1).
*Недоліки:* якщо матриця розріджена (багато станів ігнорують більшість подій), 2D-таблиця витрачає Flash-пам'ять на порожні клітинки.

---

#### Патерн 3: Покажчики на функцію стану (State-Handler Pattern)

У цьому патерні кожен стан є окремою самостійною функцією. Поточний стан автомата зберігається як звичайний покажчик на функцію (`StateFn`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EV_ENTRY,
    EV_EXIT,
    EV_BTN_PRESS,
    EV_TIMER_EXPIRED
} Signal;

typedef struct PumpController PumpController;
typedef void (*StateFn)(PumpController *me, Signal sig);

struct PumpController {
    StateFn state;
    uint32_t fill_level;
};

// Прототипи функцій станів
static void state_draining(PumpController *me, Signal sig);
static void state_filling(PumpController *me, Signal sig);

static void fsm_transition(PumpController *me, StateFn target) {
    if (me->state) me->state(me, EV_EXIT);
    me->state = target;
    if (me->state) me->state(me, EV_ENTRY);
}

static void state_filling(PumpController *me, Signal sig) {
    switch (sig) {
        case EV_ENTRY:
            // GPIO_SetHigh(VALVE_PIN);
            break;
        case EV_EXIT:
            // GPIO_SetLow(VALVE_PIN);
            break;
        case EV_TIMER_EXPIRED:
            fsm_transition(me, state_draining);
            break;
        default:
            break;
    }
}

static void state_draining(PumpController *me, Signal sig) {
    switch (sig) {
        case EV_ENTRY:
            // GPIO_SetHigh(PUMP_PIN);
            break;
        case EV_EXIT:
            // GPIO_SetLow(PUMP_PIN);
            break;
        case EV_BTN_PRESS:
            fsm_transition(me, state_filling);
            break;
        default:
            break;
    }
}

void pump_controller_init(PumpController *me) {
    me->state = NULL;
    me->fill_level = 0;
    fsm_transition(me, state_filling);
}
```
```cpp
#include <cstdint>

enum class Signal : uint8_t {
    Entry,
    Exit,
    BtnPress,
    TimerExpired
};

class PumpController {
public:
    using StateFn = void (PumpController::*)(Signal);

    PumpController() noexcept {
        transition(&PumpController::stateFilling);
    }

    void dispatch(Signal sig) noexcept {
        if (state_) {
            (this->*state_)(sig);
        }
    }

private:
    void transition(StateFn target) noexcept {
        if (state_) {
            (this->*state_)(Signal::Exit);
        }
        state_ = target;
        if (state_) {
            (this->*state_)(Signal::Entry);
        }
    }

    void stateFilling(Signal sig) noexcept {
        switch (sig) {
            case Signal::Entry:
                // OpenValve();
                break;
            case Signal::Exit:
                // CloseValve();
                break;
            case Signal::TimerExpired:
                transition(&PumpController::stateDraining);
                break;
            default:
                break;
        }
    }

    void stateDraining(Signal sig) noexcept {
        switch (sig) {
            case Signal::Entry:
                // StartPump();
                break;
            case Signal::Exit:
                // StopPump();
                break;
            case Signal::BtnPress:
                transition(&PumpController::stateFilling);
                break;
            default:
                break;
        }
    }

    StateFn state_{nullptr};
    uint32_t fill_level_{0};
};
```
:::

*Переваги:* найкраща інкапсуляція. Логіка одного стану (включно з його входом, виходом та обробкою подій) повністю локалізована в одній функції. Немає роздутих таблиць та гігантських `switch`.

---

### Кільцева черга подій та розв'язка з перериваннями (ISR)

Головне правило систем реального часу: **обробник переривання (ISR) ніколи не повинен виконувати бізнес-логіку або переходи автомата станів**.

Якщо викликати диспетчеризацію FSM всередині ISR, виникають три критичні загрози:
1. **Блокування інших переривань:** тривалість переходу в автоматі (зчитування давачів, оновлення дисплея) може перевищити сотні мікросекунд, що призведе до пропуску термінових імпульсів або переповнення буфера UART.
2. **Порушення реентрабельності:** якщо одне переривання витіснить інше і спробує змінити стан того самого автомата, внутрішні змінні FSM опиняться у розірваному, невалідному стані (data race).
3. **Невизначений порядок дій:** якщо кілька джерел переривань спрацювали одночасно, без черги події оброблятимуться у випадковому пріоритетному порядку контролера NVIC, а не в хронологічній послідовності їхнього виникнення.

Правильне інженерне рішення — **асинхронна розв'язка**: ISR лише формує компактний запис події (2–8 байтів) і розміщує його в атомарній кільцевій черзі (**Event Ring Buffer**). Головний цикл `super-loop` витягує події по одній і передає їх автомату за принципом **Run-To-Completion (RTC)** — кожна дія гарантовано завершується до того, як розпочнеться наступна.

![Архітектура розв'язки апаратних переривань та диспетчера подій](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/img/event-queue-architecture.svg)
*Апаратні переривання (кнопки, таймери, DMA) лише пакують події в кільцеву чергу. Головний цикл послідовно витягує події, передає їх автомату, а за відсутності подій переводить мікроконтролер у режим сну через __WFI().*

#### Реалізація потокобезпечної черги подій без блокувань

Для взаємодії одного джерела (або багатьох ISR) з одним споживачем (головним циклом) застосовується кільцевий буфер фіксованого розміру, де довжина буфера є ступенем двійки (це замінює повільну операцію взяття залишку `%` на швидку бітову маску `& (SIZE - 1)`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_SIZE 16
#define EVENT_QUEUE_MASK (EVENT_QUEUE_SIZE - 1)

typedef uint16_t EventId;

typedef struct {
    EventId id;
    uintptr_t payload;
} Event;

typedef struct {
    Event buffer[EVENT_QUEUE_SIZE];
    volatile uint8_t head; // індекс запису (виробник / ISR)
    volatile uint8_t tail; // індекс читання (споживач / main)
} EventQueue;

void event_queue_init(EventQueue *q) {
    q->head = 0;
    q->tail = 0;
}

// Виклик виключно з ISR або з критичної секції
bool event_queue_push(EventQueue *q, EventId id, uintptr_t payload) {
    uint8_t next_head = (q->head + 1) & EVENT_QUEUE_MASK;
    if (next_head == q->tail) {
        // Переповнення черги! Подію втрачено (Backpressure)
        return false;
    }
    q->buffer[q->head].id = id;
    q->buffer[q->head].payload = payload;
    q->head = next_head;
    return true;
}

// Виклик виключно з головного циклу
bool event_queue_pop(EventQueue *q, Event *out_event) {
    if (q->head == q->tail) {
        return false; // Черга порожня
    }
    *out_event = q->buffer[q->tail];
    q->tail = (q->tail + 1) & EVENT_QUEUE_MASK;
    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>
#include <atomic>

template <typename EventType, size_t Capacity = 16>
class EventQueue {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of 2");

public:
    constexpr EventQueue() : head_(0), tail_(0) {}

    // Виклик з ISR
    bool push(const EventType& event) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);
        const size_t next_head = (current_head + 1) & (Capacity - 1);

        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Черга переповнена
        }

        buffer_[current_head] = event;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    // Виклик з головного циклу
    std::optional<EventType> pop() noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);

        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Черга порожня
        }

        EventType event = buffer_[current_tail];
        tail_.store((current_tail + 1) & (Capacity - 1), std::memory_order_release);
        return event;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

private:
    std::array<EventType, Capacity> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
};
```
:::

#### Диспетчер та енергозбереження

Головний цикл перетворюється на елегантну конструкцію з трьох рядків:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

// Макрос засинання для ARM Cortex-M
#ifndef __WFI
#define __WFI() __asm volatile("wfi")
#endif

extern EventQueue g_queue;
extern EvseController g_evse;

int main(void) {
    // Ініціалізація апаратних периферійних вузлів
    // hardware_init();
    // evse_fsm_init(&g_evse);
    event_queue_init(&g_queue);

    while (1) {
        Event evt;
        if (event_queue_pop(&g_queue, &evt)) {
            // Диспетчеризація події у відповідний автомат
            // evse_fsm_dispatch(&g_evse, (FsmEvent)evt.id);
        } else {
            // Черга порожня: засинаємо до наступного апаратного переривання
            __WFI();
        }
    }
}
```
```cpp
#include <cstdint>

#ifndef __WFI
#define __WFI() __asm volatile("wfi")
#endif

extern EventQueue<Event, 16> g_event_queue;
extern EvseController g_evse_controller;

int main() {
    // hardware_init();

    while (true) {
        if (auto evt = g_event_queue.pop()) {
            g_evse_controller.dispatch(static_cast<FsmEvent>(evt->id));
        } else {
            // Сон до спрацьовування будь-якого переривання
            __WFI();
        }
    }
}
```
:::

Коли подій немає, процесор не крутить мільйони порожніх ітерацій, а засинає за інструкцією `__WFI()`. Струм споживання кристала падає з 25 мА до лічених мікроампер. Перше ж переривання (таймер або кнопка) будить ядро, обробник кладе подію в чергу, і головний цикл негайно виконує диспетчеризацію.

---

### Ієрархічні автомати станів (HSM / Statecharts)

У міру розвитку функціоналу прошивки плоский автомат неминуче стикається з проблемою **дублювання переходів**. Якщо система має робочі підстани `Init`, `Authenticating`, `Precharge`, `FastCharging` та `Balancing`, і в **кожному** з них при натисканні аварійної кнопки слід переходити у стан `FAULT`, у плоскому автоматі доводиться малювати п'ять ідентичних стрілок.

Девід Гарель у 1984 році запропонував розширення автоматів під назвою **Statecharts** (докладніше про [історію винаходу Statecharts для авіоніки](root:embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/hist-statecharts.md)), де стани можуть бути вкладені один в один.

![Скорочення кількості переходів у HSM завдяки суперстанам](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/img/hierarchical-states-reduction.svg)
*Ліворуч — плоский автомат із комбінаторним дублюванням переходів на кожну аварійну подію. Праворуч — ієрархічний автомат, де суперстан Operational перехоплює подію аварії один-єдиний раз для всіх внутрішніх підстанів.*

Принцип роботи HSM базується на **поведінковому наслідуванні**:
1. Подія надходить до найбільш глибокого активного підстану (Leaf State);
2. Якщо підстан знає, як обробити подію, він обробляє її і повертає `HANDLED`;
3. Якщо підстан не містить обробника для цієї події, вона **автоматично піднімається** до суперстану (Parent State);
4. Процес повторюється вгору до кореня ієрархії (`Top`).

Це дозволяє локалізувати специфічні реакції у підстанах, а всі загальні правила поведінки (таймаути бездіяльності, помилки живлення, аварії) описати один раз у суперстані. Повну інженерну реалізацію та алгоритм обчислення LCA дивіться у вставці [готовий рушій ієрархічного автомата станів](root:embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/proj-hierarchical-fsm.md).

---

### Наскрізний інженерний приклад: Контролер зарядної станції EVSE

Розглянемо реальну систему керування зарядною станцією електромобілів змінного струму за міжнародним стандартом **IEC 61851-1 / SAE J1772**.

#### Фізика процесу та лінія Control Pilot (CP)
Станція спілкується з автомобілем через одну аналогову лінію зв'язку CP:
- **Стан A (Очікування):** Станція видає постійну напругу +12 В. Кабель не підключений.
- **Стан B (Підключено):** Автомобіль підключив штекер. Вхідний резистор автомата просаджує напругу до +9 В. Станція вмикає ШІМ 1 кГц (шпаруватість задає максимальний допустимий струм).
- **Стан C (Заряджання):** Автомобіль замикає внутрішній ключ, просаджуючи напругу пілота до +6 В (запит енергії). Станція замикає силове трифазне реле 400 В.
- **Стан D (Аварія):** Корозія, пробій ізоляції або обрив пілота (напруга ≤ 0 В або відхилення частоти). Реле аварійно розмикається.

![Діаграма станів контролера зарядної станції EVSE](/root/course/embedded/avtomat-staniv-i-cherha-podii-u-proshyvtsi/img/evse-state-machine.svg)
*Повний граф станів зарядної станції EVSE: штатні переходи A-B-C та аварійні переходи у Fault із примусовим відключенням силового контактора.*

Нижче наведено повний робочий каркас прошивки на базі скінченного автомата та диспетчера подій.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Сигнали системи */
typedef enum {
    EV_CP_VOLTAGE_12V, // Автомобіль відключено
    EV_CP_VOLTAGE_9V,  // Автомобіль підключено
    EV_CP_VOLTAGE_6V,  // Запит заряджання
    EV_RFID_AUTH_OK,   // Авторизація успішна
    EV_OVERCURRENT,    // Перевищення струму (аварія)
    EV_RESET_BTN       // Ручне скидання
} EvseSignal;

typedef enum {
    ST_STANDBY,
    ST_CONNECTED,
    ST_CHARGING,
    ST_FAULT
} EvseStateId;

typedef struct EvseEvse Evse;
typedef void (*EvseStateHandler)(Evse *me, EvseSignal sig);

struct EvseEvse {
    EvseStateHandler state;
    bool is_authorized;
    uint16_t current_limit_a;
};

/* Апаратні функції абстракції (HAL) */
static void HAL_SetPilotPWM(uint8_t duty_percent) { (void)duty_percent; }
static void HAL_SetRelay(bool closed) { (void)closed; }
static void HAL_SetRedLed(bool on) { (void)on; }

/* Прототипи станів */
static void state_standby(Evse *me, EvseSignal sig);
static void state_connected(Evse *me, EvseSignal sig);
static void state_charging(Evse *me, EvseSignal sig);
static void state_fault(Evse *me, EvseSignal sig);

static void evse_transition(Evse *me, EvseStateHandler next) {
    me->state = next;
    // Одразу виконуємо ініціалізацію для нового стану
}

static void state_standby(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_CP_VOLTAGE_9V:
            // Кабель підключено -> переходимо в очікування авторизації
            HAL_SetPilotPWM(50); // 32A доступно
            evse_transition(me, state_connected);
            break;

        default:
            break;
    }
}

static void state_connected(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_RFID_AUTH_OK:
            me->is_authorized = true;
            break;

        case EV_CP_VOLTAGE_6V:
            if (me->is_authorized) {
                // Автомобіль готовий і авторизований -> заряджаємо
                HAL_SetRelay(true);
                evse_transition(me, state_charging);
            }
            break;

        case EV_CP_VOLTAGE_12V:
            // Штекер витягли
            me->is_authorized = false;
            HAL_SetPilotPWM(100); // 12V DC
            evse_transition(me, state_standby);
            break;

        case EV_OVERCURRENT:
            HAL_SetRedLed(true);
            evse_transition(me, state_fault);
            break;

        default:
            break;
    }
}

static void state_charging(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_CP_VOLTAGE_9V:
            // Автомобіль призупинив заряджання (акумулятор повний)
            HAL_SetRelay(false);
            evse_transition(me, state_connected);
            break;

        case EV_CP_VOLTAGE_12V:
            // Аварійне висмикування під навантаженням
            HAL_SetRelay(false);
            me->is_authorized = false;
            HAL_SetPilotPWM(100);
            evse_transition(me, state_standby);
            break;

        case EV_OVERCURRENT:
            // Аварія струму: миттєве розмикання
            HAL_SetRelay(false);
            HAL_SetPilotPWM(0);
            HAL_SetRedLed(true);
            evse_transition(me, state_fault);
            break;

        default:
            break;
    }
}

static void state_fault(Evse *me, EvseSignal sig) {
    switch (sig) {
        case EV_RESET_BTN:
            HAL_SetRedLed(false);
            HAL_SetPilotPWM(100);
            me->is_authorized = false;
            evse_transition(me, state_standby);
            break;

        default:
            break;
    }
}

void evse_init(Evse *me) {
    me->is_authorized = false;
    me->current_limit_a = 32;
    HAL_SetRelay(false);
    HAL_SetPilotPWM(100);
    HAL_SetRedLed(false);
    me->state = state_standby;
}
```
```cpp
#include <cstdint>

enum class EvseSignal : uint8_t {
    CpVoltage12V,
    CpVoltage9V,
    CpVoltage6V,
    RfidAuthOk,
    Overcurrent,
    ResetBtn
};

enum class EvseStateId : uint8_t {
    Standby,
    Connected,
    Charging,
    Fault
};

class EvseController {
public:
    using StateHandler = void (EvseController::*)(EvseSignal);

    EvseController() noexcept {
        initHardware();
        state_ = &EvseController::stateStandby;
    }

    void dispatch(EvseSignal sig) noexcept {
        if (state_) {
            (this->*state_)(sig);
        }
    }

private:
    void initHardware() noexcept {
        setRelay(false);
        setPilotPwm(100);
        setRedLed(false);
    }

    void setPilotPwm(uint8_t duty) noexcept { (void)duty; }
    void setRelay(bool closed) noexcept { (void)closed; }
    void setRedLed(bool on) noexcept { (void)on; }

    void stateStandby(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::CpVoltage9V:
                setPilotPwm(50);
                state_ = &EvseController::stateConnected;
                break;
            default:
                break;
        }
    }

    void stateConnected(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::RfidAuthOk:
                is_authorized_ = true;
                break;

            case EvseSignal::CpVoltage6V:
                if (is_authorized_) {
                    setRelay(true);
                    state_ = &EvseController::stateCharging;
                }
                break;

            case EvseSignal::CpVoltage12V:
                is_authorized_ = false;
                setPilotPwm(100);
                state_ = &EvseController::stateStandby;
                break;

            case EvseSignal::Overcurrent:
                setRedLed(true);
                state_ = &EvseController::stateFault;
                break;

            default:
                break;
        }
    }

    void stateCharging(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::CpVoltage9V:
                setRelay(false);
                state_ = &EvseController::stateConnected;
                break;

            case EvseSignal::CpVoltage12V:
                setRelay(false);
                is_authorized_ = false;
                setPilotPwm(100);
                state_ = &EvseController::stateStandby;
                break;

            case EvseSignal::Overcurrent:
                setRelay(false);
                setPilotPwm(0);
                setRedLed(true);
                state_ = &EvseController::stateFault;
                break;

            default:
                break;
        }
    }

    void stateFault(EvseSignal sig) noexcept {
        switch (sig) {
            case EvseSignal::ResetBtn:
                setRedLed(false);
                setPilotPwm(100);
                is_authorized_ = false;
                state_ = &EvseController::stateStandby;
                break;
            default:
                break;
        }
    }

    StateHandler state_{nullptr};
    bool is_authorized_{false};
    uint16_t current_limit_a_{32};
};
```
:::

---

### Підсумки: чекліст побудови надійної подійної архітектури

Щоб вбудована система ніколи не зависала і мала гарантований час відгуку, керуйтеся чотирма залізними правилами:

1. **Жодних delay() у коді виконання:** Тривалість будь-якого кроку обробки події в автоматі має вимірюватися мікросекундами. Тривалі затримки реалізуються виключно через таймерні події `EVT_TIMEOUT`.
2. **Нуль важкої логіки в ISR:** Переривання лише фіксують апаратну зміну, заповнюють поля структури `Event` і штовхають її в кільцеву чергу.
3. **Атомарний життєвий цикл через Entry/Exit:** Ресурси безпеки (вимикання нагрівачів, знеструмлення високовольтних реле) прив'язуються до `Exit Action` стану, а не розпорошуються по окремих гілках `if`.
4. **Сон у порожній черзі:** Якщо черга подій порожня, процесор викликає інструкцію енергозбереження `__WFI()`, знижуючи споживання енергії на 99%.

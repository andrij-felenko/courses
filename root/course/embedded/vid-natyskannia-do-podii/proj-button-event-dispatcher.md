# ⚙️ Диспетчер подій кнопок та енкодерів: від тиків до черги

Пряме опитування виводів GPIO у головному циклі програми через блокувальні виклики із затримками швидко руйнує модульність прошивки. Якщо мікроконтролер одночасно керує силовими ключами ШІМ, оновлює графіку на дисплеї та підтримує сесію обміну даними по бездротовому чи послідовному інтерфейсу, жодна підсистема не має права монополізувати процесорний час. Обробка органів введення повинна бути повністю **неблокувальною** (*non-blocking*), **подієво-орієнтованою** (*event-driven*) та **детермінованою за часом**.

Цей проект демонструє виробничу архітектуру введення, яка розділяє низькорівневу дискретизацію фізичних контактів і високорівневу семантику інтерфейсу користувача.

```
Архітектура обробки від заліза до бізнес-логіки:

 [ Кнопка / Енкодер ]
         │ (сирий контакт, брязкіт)
         ▼
 [ Системний таймер (5 мс) ] ───► [ Дебаунс: інтегруючий лічильник / зсувний регістр ]
                                              │ (стабільний рівень 0/1)
                                              ▼
                                 [ Скінченний автомат FSM (таймаути) ]
                                              │ (події: CLICK, DBL_CLICK, LONG)
                                              ▼
                                 [ Кільцева черга подій Ring Buffer FIFO ]
                                              │ (event_pop)
                                              ▼
                                 [ Головний цикл застосунку / RTOS Task ]
```

## Трирівнева архітектура обробки

Система побудована на чіткому розмежуванні обов'язків між трьома ізольованими рівнями:

1. **Рівень періодичної дискретизації (Sampling & Debounce Layer):**
   Виконується у контексті регулярного переривання системного таймера (SysTick або апаратного таймера) з періодом 5–10 мс. Цей рівень не аналізує тривалість кліків і не викликає зворотних викликів. Його єдина задача — прочитати сирий логічний стан піна GPIO і оновити маску історії зсувного регістра або лічильник з насиченням. Лише коли маска фіксує безперервну серію однакових значень (наприклад, вісім нулів `0x00` для активного низького рівня), стан вважається верифікованим.

2. **Рівень розпізнавання жестів (Gesture FSM Layer):**
   Скінченний автомат відстежує часові інтервали між змінами стабільного стану. Він вимірює тривалість утримання контакту, детектує момент відпускання та запускає таймер очікування повторного натискання. Завдяки цьому проста тактова кнопка генерує багату палітру подій: одинарний клік (*Short Click*), подвійний клік (*Double Click*), початок утримання (*Long Press Start*), утримання (*Long Press Hold*) та періодичний автоповтор (*Auto-Repeat*).

3. **Рівень асинхронної черги подій (Event Queue Layer):**
   Події, сформовані автоматом, упаковуються у компактні структури та розміщуються у безблокувальній кільцевій черзі FIFO (*First-In, First-Out*). Головний цикл програми або фонова задача операційної системи реального часу (FreeRTOS, Zephyr) забирає події з черги у міру готовності, повністю ізолюючи інтерфейс користувача від жорсткого таймінгу переривань.

## Математика квадратурного декодування енкодера

Для обробки поворотних квадратурних енкодерів застосовується табличний метод переходу станів у коді Грея. Енкодер формує дві фази — `A` (CLK) та `B` (DT), зсунуті на 90 електричних градусів. Поточний стан описується 2-бітним числом `[A B]`.

Об'єднуючи попередній стан `prev` і поточний стан `curr`, ми отримуємо 4-бітний індекс переходу `index = (prev << 2) | curr`, який набуває значень від 0 до 15.

```
Таблиця переходів квадратурного коду Грея:

 Попередній [A_old B_old]  Поточний [A_new B_new]  Індекс (hex)  Напрямок / Крок
 ────────────────────────────────────────────────────────────────────────────────
 00                        01                      0x1           +1 (CW)
 01                        11                      0x7           +1 (CW)
 11                        10                      0xE           +1 (CW)
 10                        00                      0x8           +1 (CW)
 ────────────────────────────────────────────────────────────────────────────────
 00                        10                      0x2           -1 (CCW)
 10                        11                      0xB           -1 (CCW)
 11                        01                      0xD           -1 (CCW)
 01                        00                      0x4           -1 (CCW)
 ────────────────────────────────────────────────────────────────────────────────
 00                        11                      0x3           0 (Заборонено / Брязкіт)
 01                        10                      0x6           0 (Заборонено / Брязкіт)
 10                        01                      0x9           0 (Заборонено / Брязкіт)
 11                        00                      0xC           0 (Заборонено / Брязкіт)
 Будь-який стан           Той самий               0, 5, 10, 15  0 (Немає руху)
```

Заборонені переходи (одночасна зміна обох бітів `00 ↔ 11` або `01 ↔ 10`) виникають виключно внаслідок сильного брязкоту або надвисокої швидкості обертання. Таблиця автоматично присвоює їм нульове значення, запобігаючи накопиченню хибних кроків.

## Повна реалізація диспетчера мовами C та C++

Нижче наведено виробничі реалізації бібліотеки. Версія мовою C розрахована на використання в класичних вбудованих середовищах із чистим C99, а версія на C++ надає строго типізований об'єктний інтерфейс з нульовими накладними витратами (*zero-cost abstractions*) на C++17/C++20.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_SIZE 16

typedef enum {
    EVENT_NONE = 0,
    EVENT_BUTTON_PRESS,
    EVENT_BUTTON_RELEASE,
    EVENT_BUTTON_SHORT_CLICK,
    EVENT_BUTTON_DOUBLE_CLICK,
    EVENT_BUTTON_LONG_PRESS_START,
    EVENT_BUTTON_LONG_PRESS_HOLD,
    EVENT_BUTTON_REPEAT,
    EVENT_ENCODER_CW,
    EVENT_ENCODER_CCW
} event_type_t;

typedef struct {
    uint8_t id;
    event_type_t type;
    uint16_t duration_ms;
} input_event_t;

/* --- Кільцева черга подій FIFO --- */
typedef struct {
    input_event_t buffer[EVENT_QUEUE_SIZE];
    uint8_t head;
    uint8_t tail;
    uint8_t count;
} event_queue_t;

void queue_init(event_queue_t *q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

bool queue_push(event_queue_t *q, input_event_t evt) {
    if (q->count >= EVENT_QUEUE_SIZE) {
        return false; /* Переповнення буфера: нова подія відкидається */
    }
    q->buffer[q->head] = evt;
    q->head = (uint8_t)((q->head + 1) % EVENT_QUEUE_SIZE);
    q->count++;
    return true;
}

bool queue_pop(event_queue_t *q, input_event_t *evt) {
    if (q->count == 0) {
        return false;
    }
    *evt = q->buffer[q->tail];
    q->tail = (uint8_t)((q->tail + 1) % EVENT_QUEUE_SIZE);
    q->count--;
    return true;
}

/* --- Скінченний автомат кнопки --- */
typedef enum {
    BTN_STATE_IDLE,
    BTN_STATE_DEBOUNCING_PRESS,
    BTN_STATE_PRESSED,
    BTN_STATE_DEBOUNCING_RELEASE,
    BTN_STATE_WAIT_DOUBLE_CLICK,
    BTN_STATE_LONG_PRESS,
    BTN_STATE_REPEAT
} btn_fsm_state_t;

typedef struct {
    uint8_t id;
    uint8_t (*read_pin)(void);  /* Повертає 0 (натиснуто, active-low) або 1 (відпущено) */
    btn_fsm_state_t state;
    uint16_t timer_ms;
    uint16_t press_duration_ms;
    uint8_t debounce_history;
} button_t;

void button_init(button_t *btn, uint8_t id, uint8_t (*read_pin_fn)(void)) {
    btn->id = id;
    btn->read_pin = read_pin_fn;
    btn->state = BTN_STATE_IDLE;
    btn->timer_ms = 0;
    btn->press_duration_ms = 0;
    btn->debounce_history = 0xFF;
}

void button_process_tick(button_t *btn, uint16_t tick_ms, event_queue_t *q) {
    uint8_t raw = btn->read_pin() ? 1 : 0;
    btn->debounce_history = (uint8_t)((btn->debounce_history << 1) | raw);
    bool is_pressed = (btn->debounce_history == 0x00);
    bool is_released = (btn->debounce_history == 0xFF);

    switch (btn->state) {
    case BTN_STATE_IDLE:
        if (raw == 0) {
            btn->state = BTN_STATE_DEBOUNCING_PRESS;
            btn->timer_ms = 0;
        }
        break;

    case BTN_STATE_DEBOUNCING_PRESS:
        btn->timer_ms += tick_ms;
        if (is_pressed) {
            btn->state = BTN_STATE_PRESSED;
            btn->press_duration_ms = 0;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_PRESS, 0});
        } else if (btn->timer_ms > 30) {
            btn->state = BTN_STATE_IDLE;
        }
        break;

    case BTN_STATE_PRESSED:
        btn->press_duration_ms += tick_ms;
        if (raw == 1) {
            btn->state = BTN_STATE_DEBOUNCING_RELEASE;
            btn->timer_ms = 0;
        } else if (btn->press_duration_ms >= 800) {
            btn->state = BTN_STATE_LONG_PRESS;
            btn->timer_ms = 0;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_LONG_PRESS_START, btn->press_duration_ms});
        }
        break;

    case BTN_STATE_DEBOUNCING_RELEASE:
        btn->timer_ms += tick_ms;
        if (is_released) {
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms});
            btn->state = BTN_STATE_WAIT_DOUBLE_CLICK;
            btn->timer_ms = 0;
        } else if (btn->timer_ms > 30) {
            btn->state = BTN_STATE_PRESSED;
        }
        break;

    case BTN_STATE_WAIT_DOUBLE_CLICK:
        btn->timer_ms += tick_ms;
        if (raw == 0) {
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_DOUBLE_CLICK, btn->timer_ms});
            btn->state = BTN_STATE_DEBOUNCING_PRESS;
            btn->timer_ms = 0;
        } else if (btn->timer_ms >= 250) {
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_SHORT_CLICK, btn->press_duration_ms});
            btn->state = BTN_STATE_IDLE;
        }
        break;

    case BTN_STATE_LONG_PRESS:
        btn->press_duration_ms += tick_ms;
        btn->timer_ms += tick_ms;
        if (raw == 1) {
            btn->state = BTN_STATE_IDLE;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms});
        } else if (btn->timer_ms >= 100) {
            btn->timer_ms = 0;
            btn->state = BTN_STATE_REPEAT;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_LONG_PRESS_HOLD, btn->press_duration_ms});
        }
        break;

    case BTN_STATE_REPEAT:
        btn->press_duration_ms += tick_ms;
        btn->timer_ms += tick_ms;
        if (raw == 1) {
            btn->state = BTN_STATE_IDLE;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_RELEASE, btn->press_duration_ms});
        } else if (btn->timer_ms >= 80) {
            btn->timer_ms = 0;
            queue_push(q, (input_event_t){btn->id, EVENT_BUTTON_REPEAT, btn->press_duration_ms});
        }
        break;
    }
}

/* --- Декодер квадратурного енкодера --- */
typedef struct {
    uint8_t id;
    uint8_t (*read_phase_a)(void);
    uint8_t (*read_phase_b)(void);
    uint8_t prev_state;
    int8_t sub_step_acc;
} encoder_t;

static const int8_t encoder_lut[16] = {
     0, -1,  1,  0,
     1,  0,  0, -1,
    -1,  0,  0,  1,
     0,  1, -1,  0
};

void encoder_init(encoder_t *enc, uint8_t id, uint8_t (*read_a)(void), uint8_t (*read_b)(void)) {
    enc->id = id;
    enc->read_phase_a = read_a;
    enc->read_phase_b = read_b;
    uint8_t a = enc->read_phase_a() ? 1 : 0;
    uint8_t b = enc->read_phase_b() ? 1 : 0;
    enc->prev_state = (uint8_t)((a << 1) | b);
    enc->sub_step_acc = 0;
}

void encoder_process_tick(encoder_t *enc, event_queue_t *q) {
    uint8_t a = enc->read_phase_a() ? 1 : 0;
    uint8_t b = enc->read_phase_b() ? 1 : 0;
    uint8_t curr = (uint8_t)((a << 1) | b);

    if (curr == enc->prev_state) {
        return;
    }

    uint8_t code = (uint8_t)((enc->prev_state << 2) | curr);
    int8_t step = encoder_lut[code];
    enc->prev_state = curr;

    if (step != 0) {
        enc->sub_step_acc += step;
        if (enc->sub_step_acc >= 4) {
            enc->sub_step_acc = 0;
            queue_push(q, (input_event_t){enc->id, EVENT_ENCODER_CW, 1});
        } else if (enc->sub_step_acc <= -4) {
            enc->sub_step_acc = 0;
            queue_push(q, (input_event_t){enc->id, EVENT_ENCODER_CCW, 1});
        }
    }
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>
#include <functional>

enum class EventType : uint8_t {
    None = 0,
    ButtonPress,
    ButtonRelease,
    ButtonShortClick,
    ButtonDoubleClick,
    ButtonLongPressStart,
    ButtonLongPressHold,
    ButtonRepeat,
    EncoderCW,
    EncoderCCW
};

struct InputEvent {
    uint8_t id{0};
    EventType type{EventType::None};
    uint16_t durationMs{0};
};

/* --- Безпечна шаблонна кільцева черга FIFO --- */
template <typename T, size_t Capacity>
class EventQueue {
public:
    constexpr EventQueue() = default;

    bool push(const T& item) noexcept {
        if (count_ >= Capacity) {
            return false;
        }
        buffer_[head_] = item;
        head_ = (head_ + 1) % Capacity;
        ++count_;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (count_ == 0) {
            return std::nullopt;
        }
        T item = buffer_[tail_];
        tail_ = (tail_ + 1) % Capacity;
        --count_;
        return item;
    }

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }

private:
    std::array<T, Capacity> buffer_{};
    size_t head_{0};
    size_t tail_{0};
    size_t count_{0};
};

/* --- Об'єктно-орієнтований контролер кнопки з FSM --- */
class Button {
public:
    using PinReader = std::function<bool()>;

    enum class State : uint8_t {
        Idle,
        DebouncingPress,
        Pressed,
        DebouncingRelease,
        WaitDoubleClick,
        LongPress,
        Repeat
    };

    Button(uint8_t id, PinReader reader) noexcept
        : id_{id}, readPin_{std::move(reader)} {}

    template <size_t N>
    void tick(uint16_t tickMs, EventQueue<InputEvent, N>& queue) noexcept {
        const bool rawActive = !readPin_(); /* Active-low: 0 В означає активний стан */
        history_ = static_cast<uint8_t>((history_ << 1) | (rawActive ? 1 : 0));

        const bool isStableActive = (history_ == 0xFF);
        const bool isStableInactive = (history_ == 0x00);

        switch (state_) {
        case State::Idle:
            if (rawActive) {
                state_ = State::DebouncingPress;
                timerMs_ = 0;
            }
            break;

        case State::DebouncingPress:
            timerMs_ += tickMs;
            if (isStableActive) {
                state_ = State::Pressed;
                pressDurationMs_ = 0;
                queue.push({id_, EventType::ButtonPress, 0});
            } else if (timerMs_ > 30) {
                state_ = State::Idle;
            }
            break;

        case State::Pressed:
            pressDurationMs_ += tickMs;
            if (!rawActive) {
                state_ = State::DebouncingRelease;
                timerMs_ = 0;
            } else if (pressDurationMs_ >= LongPressThresholdMs) {
                state_ = State::LongPress;
                timerMs_ = 0;
                queue.push({id_, EventType::ButtonLongPressStart, pressDurationMs_});
            }
            break;

        case State::DebouncingRelease:
            timerMs_ += tickMs;
            if (isStableInactive) {
                queue.push({id_, EventType::ButtonRelease, pressDurationMs_});
                state_ = State::WaitDoubleClick;
                timerMs_ = 0;
            } else if (timerMs_ > 30) {
                state_ = State::Pressed;
            }
            break;

        case State::WaitDoubleClick:
            timerMs_ += tickMs;
            if (rawActive) {
                queue.push({id_, EventType::ButtonDoubleClick, timerMs_});
                state_ = State::DebouncingPress;
                timerMs_ = 0;
            } else if (timerMs_ >= DoubleClickTimeoutMs) {
                queue.push({id_, EventType::ButtonShortClick, pressDurationMs_});
                state_ = State::Idle;
            }
            break;

        case State::LongPress:
            pressDurationMs_ += tickMs;
            timerMs_ += tickMs;
            if (!rawActive) {
                state_ = State::Idle;
                queue.push({id_, EventType::ButtonRelease, pressDurationMs_});
            } else if (timerMs_ >= 100) {
                timerMs_ = 0;
                state_ = State::Repeat;
                queue.push({id_, EventType::ButtonLongPressHold, pressDurationMs_});
            }
            break;

        case State::Repeat:
            pressDurationMs_ += tickMs;
            timerMs_ += tickMs;
            if (!rawActive) {
                state_ = State::Idle;
                queue.push({id_, EventType::ButtonRelease, pressDurationMs_});
            } else if (timerMs_ >= RepeatRateMs) {
                timerMs_ = 0;
                queue.push({id_, EventType::ButtonRepeat, pressDurationMs_});
            }
            break;
        }
    }

private:
    static constexpr uint16_t LongPressThresholdMs = 800;
    static constexpr uint16_t DoubleClickTimeoutMs = 250;
    static constexpr uint16_t RepeatRateMs = 80;

    uint8_t id_{0};
    PinReader readPin_{};
    State state_{State::Idle};
    uint16_t timerMs_{0};
    uint16_t pressDurationMs_{0};
    uint8_t history_{0x00};
};

/* --- Декодер квадратурного енкодера на C++ --- */
class RotaryEncoder {
public:
    using PinReader = std::function<bool()>;

    RotaryEncoder(uint8_t id, PinReader readA, PinReader readB) noexcept
        : id_{id}, readA_{std::move(readA)}, readB_{std::move(readB)} {
        const uint8_t a = readA_() ? 1 : 0;
        const uint8_t b = readB_() ? 1 : 0;
        prevState_ = static_cast<uint8_t>((a << 1) | b);
    }

    template <size_t N>
    void tick(EventQueue<InputEvent, N>& queue) noexcept {
        const uint8_t a = readA_() ? 1 : 0;
        const uint8_t b = readB_() ? 1 : 0;
        const uint8_t currState = static_cast<uint8_t>((a << 1) | b);

        if (currState == prevState_) {
            return;
        }

        const uint8_t code = static_cast<uint8_t>((prevState_ << 2) | currState);
        const int8_t step = StateTable[code];
        prevState_ = currState;

        if (step != 0) {
            subSteps_ += step;
            if (subSteps_ >= 4) {
                subSteps_ = 0;
                queue.push({id_, EventType::EncoderCW, 1});
            } else if (subSteps_ <= -4) {
                subSteps_ = 0;
                queue.push({id_, EventType::EncoderCCW, 1});
            }
        }
    }

private:
    static constexpr std::array<int8_t, 16> StateTable = {
         0, -1,  1,  0,
         1,  0,  0, -1,
        -1,  0,  0,  1,
         0,  1, -1,  0
    };

    uint8_t id_{0};
    PinReader readA_{};
    PinReader readB_{};
    uint8_t prevState_{0};
    int8_t subSteps_{0};
};
```
:::

## Інженерні пастки та правила інтеграції

1. **Розділення контекстів переривання та головного циклу:**
   Метод `button_process_tick()` викликається виключно в контексті системного таймера з фіксованим періодом 5–10 мс. Він виконує лише елементарні бітові операції та додає подію в чергу. Будь-яка ресурсомістка бізнес-логіка (перемальовування дисплея, запис у flash-пам'ять або передача пакетів по радіоканалу) виконується виключно у фоновому циклі застосунку під час споживання подій із черги функцією `queue_pop()`.

2. **Безпека багатопотокового доступу до кільцевого буфера:**
   Якщо запис у чергу відбувається в обробнику апаратного переривання (ISR), а зчитування — у головному циклі `main()`, змінні `head`, `tail` та лічильник `count` повинні змінюватися атомарно. У найпростішому випадку на мікроконтролерах Cortex-M доступ до буфера огортають критичними секціями (`__disable_irq()` / `__enable_irq()`), або реалізують класичний безблокувальний буфер *Single-Producer Single-Consumer (SPSC)*, де модифікація індексів виконується атомарно без зміни спільного лічильника.

3. **Джитер таймаутів дискретизації:**
   Якщо виклик функції `tick` зазнає часового тремтіння (*jitter*) через триваліше виконання пріоритетніших переривань, передача точного параметра `tick_ms` (наприклад, дельти системного лічильника) дозволяє автомату зберігати калібровану тривалість розпізнавання жестів незалежно від навантаження на систему.

4. **Адаптивний автоповтор (Auto-Repeat Acceleration):**
   При тривалому утриманні кнопки часто необхідно плавно прискорювати темп генерації подій (наприклад, під час швидкого перемотування значень меню від 0 до 1000). У структурі `button_t` інтервал `timer_ms` у стані `BTN_STATE_REPEAT` можна динамічно зменшувати від 100 мс до 20 мс залежно від накопиченого значення `press_duration_ms`.

5. **Очищення черги при зміні екранів:**
   Під час перемикання режимів меню або зміни екранів графічного інтерфейсу черга подій повинна бути очищена викликом `queue_init()`, щоб залишковий клік від попереднього вікна випадково не активував небажану кнопку у новому контексті.

6. **Статичний розподіл пам'яті без динамічної купи:**
   Усі структури даних — буфер черги `buffer`, дескриптори кнопок `button_t` та енкодерів `encoder_t` — виділяються статично на етапі компіляції. Це унеможливлює фрагментацію оперативної пам'яті (*heap fragmentation*) та забезпечує миттєвий передбачуваний час ініціалізації на будь-якому мікроконтролері з обмеженою оперативною пам'яттю (SRAM від 2 КБ).

# ⚙️ Драйвер неінвазивних інтерфейсів: геркон, ємнісна кнопка та світловод

У герметичному корпусі зі ступенем захисту IP67/IP68 фізичні кнопки з рухомими штоками, відкриті контакти налагодження та наскрізні отвори під світлодіоди ліквідовано. Будь-який механічний отвір у пластику стає каналом проникнення вологи при добових перепадах температур, а рухомі еластомірні ущільнення неминуче деградують від тертя, сонячного ультрафіолету та пилу. Уся взаємодія з автономним приладом переноситься на неінвазивні сенсори: магнітний замикач (геркон або мікропотужний давач Холла), ємнісний чутливий майданчик під діелектричною стінкою та жорсткі оптичні світловоди для виведення індикації.

Програмний шар, що обслуговує ці канали, стикається з фізичними артефактами матеріалів корпусу та жорсткими обмеженнями енергетичного бюджету:
1. **Магнітне брязкання та паразитні поля:** при піднесенні зовнішнього постійного магніту пружні феромагнітні пелюстки геркона змикаються не миттєво, а зазнають механічних коливань із серією мікророзривів контакту тривалістю 2–5 мс. Крім того, прилад може транспортуватися поруч із металевими конструкціями, електромагнітними замками чи електродвигунами. Драйвер зобов'язаний надійно розрізняти короткочасний магнітний імпульс (користувацький тап) та фіксоване утримання магніту понад 5 секунд для сервісних операцій (скидання до заводських налаштувань, аварійне пробудження).
2. **Ємнісний дрейф і температурна нестабільність:** діелектрична проникність корпусних полімерів (ABS-пластик `ε_r ≈ 2.8…3.2`, полікарбонат `ε_r ≈ 2.9…3.4`) та склотекстоліту плати плаває від температури й вологості. Якщо зафіксувати поріг спрацьовування статичним числом, кнопка або «залипне» в постійно активному стані при утворенні внутрішнього конденсату, або втратить чутливість до пальця на морозі. Драйвер зобов'язаний реалізувати динамічне відстеження опорної лінії (baseline tracking) з механізмом заморожування адаптації під час активного натискання.
3. **Керування яскравістю та оптична безінерційність світловода:** полікарбонатний або акриловий світловод транспортує світло без власної люмінесцентної інерції. Плавна анімація («дихання», пульсація) вимагає стабільного ШІМ із частотою не менше 1 кГц, щоб уникнути стробоскопічного розриву світлового сліду в русі та акустичного писку керамічних конденсаторів плати.
4. **Мікроамперний бюджет споживання:** при живленні від літієвого дискового елемента CR2032 або батареї Li-SOCl₂ вимірювальна схема не може працювати безперервно. Драйвер підтримує чергування низькоспоживаючого сну та коротких вимірювальних вікон (duty cycling).

Нижче розібрано фізичні механізми кожного каналу, алгоритми фільтрації та робочу реалізацію драйвера мовами C та C++.

## Фізика каналів та архітектура драйвера

Драйвер спроєктовано як неблокуючий кінцевий автомат, що викликається з фіксованим періодом квантування (10 мс через апаратний таймер) або інтегрується в подієвий цикл операційної системи реального часу (RTOS).

```
[Геркон / Холл] ──(EXTI переривання)──► [Пробудження MCU] ──► [Фільтр брязкоту 30 мс] ──► Події TAP / HOLD
                                                                                               │
[Ємнісний сенсор] ──(Duty Cycle 50 мс)──► [IIR-фільтр бази] ──► [Детектор дельти ΔC] ──► Події PRESS / RELEASE
                                                                                               │
[Оптичний світловод] ◄──(ШІМ 1 кГц)────── [Генератор фази] ◄── [Керування режимом LED] ◄───────┘
```

### Магнітний канал: обробка переривань від геркона та фільтрація брязкоту

Геркон забезпечує нульовий струм споживання в розімкненому стані, що робить його ідеальним кандидатом для вузла пробудження автономного приладу. Проте пряме підключення виводу геркона до входу зовнішніх переривань (EXTI) мікроконтролера таїть небезпеку: під час замикання пружні контакти генерують шторм із десятків асинхронних імпульсів за кілька мілісекунд. Обробка кожного імпульсу окремим перериванням перевантажує стек ядра й блокує виконання прикладного коду.

Для надійної роботи застосовують дворівневу схему обробки:
- **Асинхронний рівень пробудження (Wakeup ISR):** у черговому режимі глибокого сну (Deep Sleep / Stop) лінія геркона налаштована як джерело пробудження за спадним фронтом. При першому механічному дотику пелюсток мікроконтролер миттєво прокидається, після чого в обробнику переривання лінія EXTI тимчасово маскується, а керування передається періодичному системному таймеру.
- **Синхронний рівень антидеренчання:** функція `update_magnetic` опитує сирий стан піна `pin_level`. При зміні значення оновлюється мітка часу останнього перепаду `last_edge_time_ms`. Лише тоді, коли новий логічний рівень утримується неперервно протягом захисного часового вікна `DEBOUNCE_TIME_MS` (30 мс), стан визнається валідним (`debounced_state`).

Захист від випадкових магнітних полів (наприклад, під час транспортування виробу в сумці поруч із ноутбуком чи інструментом) реалізується через часовий поріг:
1. Якщо стабільний контакт триває менше 5 секунд і розмикається, формується подія короткого натискання `EVT_REED_SHORT_TAP` (користувацьке перемикання режиму чи відображення заряду);
2. Якщо магніт утримується біля корпусу безперервно протягом 5000 мс (`LONG_HOLD_TIME_MS`), спрацьовує прапорець `long_hold_triggered`, генеруючи подію `EVT_REED_LONG_HOLD` (запуск процедури скидання конфігурації або переходу в сервісний бутлоадер). Повторні події блокуються до повного відведення магніту.

### Ємнісний канал: калібрування, IIR-фільтрація та заморожування бази

Ємнісний контролер вимірює тривалість перезаряджання чутливого майданчика або використовує метод зарядового переносу (Charge Transfer). Вихідний цифровий код `raw_counts` пропорційний сумарній ємності електрода:

```
C_total = C_trace + C_touch
```

Діелектрична проникність пластикової стінки корпусу змінюється залежно від температури навколишнього середовища (до 0.2%/°C) та відносної вологості повітря. Щоб усунути хибні спрацьовування, драйвер реалізує низькочастотний цифровий IIR-фільтр (Infinite Impulse Response) для постійного супроводу базової лінії. 

Для максимальної швидкодії на мікроконтролерах Cortex-M0+/M3 без апаратного блоку FPU фільтр реалізовано в арифметиці з фіксованою точкою Q16.16:

```
baseline_fixed = baseline_fixed + ((raw_counts << 16) - baseline_fixed) / 64
```

Коефіцієнт згладжування `α = 1/64` (задається зсувом `BASELINE_ALPHA_SHIFT = 6`) забезпечує повільне, плавне підлаштування під кліматичний дрейф із постійною часу в кілька секунд.

**Критичний механізм заморожування базової лінії (Baseline Freeze):**
Якщо людина утримує палець на сенсорі протягом 10–20 секунд, підвищена ємність пальця є корисним сигналом, а не зміною клімату. Якби IIR-фільтр продовжував оновлюватися під час утримання, він поступово інтегрував би ємність пальця в нове значення опорної бази. У момент, коли користувач відпустить кнопку, сигнал `raw_counts` миттєво впаде до реальної ємності плати, що створить глибокий від'ємний зсув `ΔC < 0`. Кнопка буде «паралізована» й не реагуватиме на жодні дотики, доки фільтр повільно не повернеться назад. Драйвер запобігає цьому стану простим правилом: оновлення `baseline_fixed` дозволено виключно тоді, коли сенсор перебуває у відпущеному стані (`!is_touched`).

Пороговий детектор з гістерезисом `TOUCH_HYSTERESIS` у поєднанні з часовою фільтрацією `DEBOUNCE_TIME_MS` повністю відсікає короткочасні імпульсні завади від радіомодулів (Wi-Fi, BLE, LoRa).

### Низькоспоживаючий режим і диспетчеризація живлення (Duty Cycling)

Постійно увімкнений ємнісний сенсорний контролер споживає від 150 до 500 мкА, що вичерпує заряд дискової батареї CR2032 (номінальна ємність 220 мА·год) менш ніж за два місяці. 

Для забезпечення 5–10 років автономної роботи драйвер інтегрується в цикл періодичного стробування (Duty Cycling):
1. Мікроконтролер перебуває в режимі сну Stop/Standby зі споживанням 1.5–3 мкА;
2. Апаратний таймер низького енергоспоживання (LPTIM або RTC) генерує подію пробудження з періодом 50–100 мс;
3. Контролер прокидається на 100–150 мкс, запускає один цикл вимірювання ємності, передає відлік у `sealed_interface_tick` і знову засинає;
4. Якщо виявлено початок дотику або піднесення магніту, період опитування динамічно перемикається на 10 мс для забезпечення плавної анімації світловода та швидкого відгуку інтерфейсу. Після відпускання та завершення світлової індикації драйвер автоматично повертається до рідкісного стробування 100 мс.

## Робочий код драйвера

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Події неінвазивного інтерфейсу */
typedef enum {
    EVT_NONE = 0,
    EVT_REED_SHORT_TAP,
    EVT_REED_LONG_HOLD,
    EVT_TOUCH_PRESS,
    EVT_TOUCH_RELEASE
} InterfaceEvent;

/* Режими анімації світловода */
typedef enum {
    LED_MODE_OFF = 0,
    LED_MODE_STATIC,
    LED_MODE_HEARTBEAT,
    LED_MODE_BLINK_FAST
} LedMode;

/* Конфігурація часових параметрів (у мілісекундах) */
#define DEBOUNCE_TIME_MS      30
#define LONG_HOLD_TIME_MS     5000
#define TOUCH_HYSTERESIS      120
#define BASELINE_ALPHA_SHIFT  6     /* Фільтр IIR: коефіцієнт 1/64 для повільного дрейфу */

/* Структура стану магнітного сенсора (геркон / Холл) */
typedef struct {
    bool raw_state;
    bool debounced_state;
    uint32_t last_edge_time_ms;
    uint32_t press_start_time_ms;
    bool long_hold_triggered;
} MagneticSensor;

/* Структура ємнісного сенсора дотику */
typedef struct {
    uint32_t baseline_fixed;  /* Опорне значення у форматі з фіксованою точкою Q16.16 */
    bool is_touched;
    uint32_t touch_debounce_time_ms;
} TouchSensor;

/* Структура індикатора світловода */
typedef struct {
    LedMode mode;
    uint8_t current_brightness;
    uint8_t target_brightness;
    uint16_t phase_counter;
} LightPipeIndicator;

/* Головний контекст контролера */
typedef struct {
    MagneticSensor reed;
    TouchSensor touch;
    LightPipeIndicator led;
    void (*event_callback)(InterfaceEvent event);
} SealedInterfaceController;

/* Ініціалізація підсистеми */
void sealed_interface_init(SealedInterfaceController *ctrl, void (*cb)(InterfaceEvent)) {
    if (!ctrl) return;
    ctrl->event_callback = cb;

    ctrl->reed.raw_state = false;
    ctrl->reed.debounced_state = false;
    ctrl->reed.last_edge_time_ms = 0;
    ctrl->reed.press_start_time_ms = 0;
    ctrl->reed.long_hold_triggered = false;

    ctrl->touch.baseline_fixed = 0;
    ctrl->touch.is_touched = false;
    ctrl->touch.touch_debounce_time_ms = 0;

    ctrl->led.mode = LED_MODE_OFF;
    ctrl->led.current_brightness = 0;
    ctrl->led.target_brightness = 0;
    ctrl->led.phase_counter = 0;
}

/* Оновлення стану магнітного сенсора (викликається в циклі або по таймеру) */
static void update_magnetic(SealedInterfaceController *ctrl, bool pin_level, uint32_t now_ms) {
    MagneticSensor *m = &ctrl->reed;

    /* Виявлення перепаду */
    if (pin_level != m->raw_state) {
        m->raw_state = pin_level;
        m->last_edge_time_ms = now_ms;
    }

    /* Антидеренчання за часовим вікном */
    if ((now_ms - m->last_edge_time_ms) >= DEBOUNCE_TIME_MS) {
        if (m->raw_state != m->debounced_state) {
            m->debounced_state = m->raw_state;

            if (m->debounced_state) {
                /* Замикання контакту під дією магніту */
                m->press_start_time_ms = now_ms;
                m->long_hold_triggered = false;
            } else {
                /* Розмикання контакту */
                if (!m->long_hold_triggered && (now_ms - m->press_start_time_ms) >= DEBOUNCE_TIME_MS) {
                    if (ctrl->event_callback) {
                        ctrl->event_callback(EVT_REED_SHORT_TAP);
                    }
                }
            }
        }
    }

    /* Перевірка тривалого сервісного утримання (5 секунд) */
    if (m->debounced_state && !m->long_hold_triggered) {
        if ((now_ms - m->press_start_time_ms) >= LONG_HOLD_TIME_MS) {
            m->long_hold_triggered = true;
            if (ctrl->event_callback) {
                ctrl->event_callback(EVT_REED_LONG_HOLD);
            }
        }
    }
}

/* Оновлення ємнісного сенсора з адаптивним фільтром базової лінії */
static void update_capacitive(SealedInterfaceController *ctrl, uint16_t raw_counts, uint32_t now_ms) {
    TouchSensor *t = &ctrl->touch;

    /* Початкова ініціалізація базової лінії */
    if (t->baseline_fixed == 0) {
        t->baseline_fixed = (uint32_t)raw_counts << 16;
        return;
    }

    uint16_t baseline_val = (uint16_t)(t->baseline_fixed >> 16);
    int32_t delta = (int32_t)raw_counts - (int32_t)baseline_val;

    /* Якщо сигнал вищий за поріг — маємо дотик */
    bool touched_raw = (delta > TOUCH_HYSTERESIS);

    if (touched_raw != t->is_touched) {
        if (t->touch_debounce_time_ms == 0) {
            t->touch_debounce_time_ms = now_ms;
        } else if ((now_ms - t->touch_debounce_time_ms) >= DEBOUNCE_TIME_MS) {
            t->is_touched = touched_raw;
            t->touch_debounce_time_ms = 0;
            if (ctrl->event_callback) {
                ctrl->event_callback(t->is_touched ? EVT_TOUCH_PRESS : EVT_TOUCH_RELEASE);
            }
        }
    } else {
        t->touch_debounce_time_ms = 0;
    }

    /* Оновлюємо базову лінію ТІЛЬКИ коли кнопка відпущена, щоб уникнути захоплення дотику в базу */
    if (!t->is_touched) {
        /* IIR-фільтр низьких частот: baseline += (raw - baseline) / 64 */
        int32_t error = ((int32_t)raw_counts << 16) - (int32_t)t->baseline_fixed;
        t->baseline_fixed += (error >> BASELINE_ALPHA_SHIFT);
    }
}

/* Оновлення генератора анімації світловода */
static void update_indicator(SealedInterfaceController *ctrl) {
    LightPipeIndicator *ind = &ctrl->led;
    ind->phase_counter++;

    switch (ind->mode) {
        case LED_MODE_OFF:
            ind->current_brightness = 0;
            break;

        case LED_MODE_STATIC:
            ind->current_brightness = ind->target_brightness;
            break;

        case LED_MODE_HEARTBEAT: {
            /* Формування плавного дихання через трикутну фазу */
            uint16_t step = ind->phase_counter % 256;
            if (step < 128) {
                ind->current_brightness = (uint8_t)(step * 2);
            } else {
                ind->current_brightness = (uint8_t)((255 - step) * 2);
            }
            break;
        }

        case LED_MODE_BLINK_FAST:
            ind->current_brightness = ((ind->phase_counter % 32) < 16) ? 255 : 0;
            break;
    }
}

/* Головний такт обробки інтерфейсу (виклик кожні 10 мс) */
void sealed_interface_tick(SealedInterfaceController *ctrl, bool reed_raw_pin, uint16_t touch_raw_counts, uint32_t now_ms) {
    if (!ctrl) return;
    update_magnetic(ctrl, reed_raw_pin, now_ms);
    update_capacitive(ctrl, touch_raw_counts, now_ms);
    update_indicator(ctrl);
}

/* Отримання поточного значення ШІМ для виводу на таймер світлодіода */
uint8_t sealed_interface_get_led_pwm(const SealedInterfaceController *ctrl) {
    return ctrl ? ctrl->led.current_brightness : 0;
}

void sealed_interface_set_led_mode(SealedInterfaceController *ctrl, LedMode mode, uint8_t max_brightness) {
    if (!ctrl) return;
    ctrl->led.mode = mode;
    ctrl->led.target_brightness = max_brightness;
}
```
```cpp
#include <cstdint>
#include <concepts>
#include <functional>
#include <algorithm>

enum class InterfaceEvent : uint8_t {
    None = 0,
    ReedShortTap,
    ReedLongHold,
    TouchPress,
    TouchRelease
};

enum class LedMode : uint8_t {
    Off = 0,
    Static,
    Heartbeat,
    BlinkFast
};

class SealedInterfaceController {
public:
    struct Config {
        uint32_t debounce_time_ms{30};
        uint32_t long_hold_time_ms{5000};
        int32_t  touch_hysteresis{120};
        uint8_t  baseline_alpha_shift{6};
    };

    using EventCallback = std::function<void(InterfaceEvent)>;

    explicit SealedInterfaceController(EventCallback cb, Config cfg = {})
        : callback_(std::move(cb)), cfg_(cfg) {}

    void tick(bool reed_pin, uint16_t touch_raw, uint32_t now_ms) noexcept {
        update_magnetic(reed_pin, now_ms);
        update_capacitive(touch_raw, now_ms);
        update_indicator();
    }

    void set_led_mode(LedMode mode, uint8_t target_brightness = 255) noexcept {
        led_mode_ = mode;
        target_brightness_ = target_brightness;
    }

    [[nodiscard]] uint8_t get_led_pwm() const noexcept {
        return current_brightness_;
    }

private:
    void update_magnetic(bool pin_level, uint32_t now_ms) noexcept {
        if (pin_level != reed_raw_state_) {
            reed_raw_state_ = pin_level;
            last_reed_edge_ms_ = now_ms;
        }

        if ((now_ms - last_reed_edge_ms_) >= cfg_.debounce_time_ms) {
            if (reed_raw_state_ != reed_debounced_state_) {
                reed_debounced_state_ = reed_raw_state_;

                if (reed_debounced_state_) {
                    press_start_ms_ = now_ms;
                    long_hold_triggered_ = false;
                } else {
                    if (!long_hold_triggered_ && (now_ms - press_start_ms_) >= cfg_.debounce_time_ms) {
                        dispatch(InterfaceEvent::ReedShortTap);
                    }
                }
            }
        }

        if (reed_debounced_state_ && !long_hold_triggered_) {
            if ((now_ms - press_start_ms_) >= cfg_.long_hold_time_ms) {
                long_hold_triggered_ = true;
                dispatch(InterfaceEvent::ReedLongHold);
            }
        }
    }

    void update_capacitive(uint16_t raw_counts, uint32_t now_ms) noexcept {
        if (baseline_fixed_ == 0) {
            baseline_fixed_ = static_cast<uint32_t>(raw_counts) << 16;
            return;
        }

        const auto baseline_val = static_cast<int32_t>(baseline_fixed_ >> 16);
        const int32_t delta = static_cast<int32_t>(raw_counts) - baseline_val;
        const bool touched_raw = (delta > cfg_.touch_hysteresis);

        if (touched_raw != is_touched_) {
            if (touch_debounce_ms_ == 0) {
                touch_debounce_ms_ = now_ms;
            } else if ((now_ms - touch_debounce_ms_) >= cfg_.debounce_time_ms) {
                is_touched_ = touched_raw;
                touch_debounce_ms_ = 0;
                dispatch(is_touched_ ? InterfaceEvent::TouchPress : InterfaceEvent::TouchRelease);
            }
        } else {
            touch_debounce_ms_ = 0;
        }

        if (!is_touched_) {
            const int32_t error = (static_cast<int32_t>(raw_counts) << 16) - static_cast<int32_t>(baseline_fixed_);
            baseline_fixed_ += (error >> cfg_.baseline_alpha_shift);
        }
    }

    void update_indicator() noexcept {
        ++phase_counter_;
        switch (led_mode_) {
            case LedMode::Off:
                current_brightness_ = 0;
                break;
            case LedMode::Static:
                current_brightness_ = target_brightness_;
                break;
            case LedMode::Heartbeat: {
                const uint16_t step = phase_counter_ % 256;
                current_brightness_ = static_cast<uint8_t>(step < 128 ? step * 2 : (255 - step) * 2);
                break;
            }
            case LedMode::BlinkFast:
                current_brightness_ = ((phase_counter_ % 32) < 16) ? 255 : 0;
                break;
        }
    }

    void dispatch(InterfaceEvent ev) const noexcept {
        if (callback_) {
            callback_(ev);
        }
    }

    EventCallback callback_;
    Config cfg_;

    // Magnetic state
    bool reed_raw_state_{false};
    bool reed_debounced_state_{false};
    bool long_hold_triggered_{false};
    uint32_t last_reed_edge_ms_{0};
    uint32_t press_start_ms_{0};

    // Capacitive state
    uint32_t baseline_fixed_{0};
    bool is_touched_{false};
    uint32_t touch_debounce_ms_{0};

    // LED state
    LedMode led_mode_{LedMode::Off};
    uint8_t current_brightness_{0};
    uint8_t target_brightness_{255};
    uint16_t phase_counter_{0};
};
```
:::

## Інженерні пастки реалізації

1. **Захоплення дотику в базову лінію (Baseline Freeze):** Якщо оновлювати IIR-фільтр опорної ємності під час тривалого утримання пальця, фільтр сприйме збільшену ємність пальця за нову нормаль навколишнього середовища. Коли користувач забере руку, розрахована дельта стане глибоко від'ємною, і кнопка заблокується на кілька секунд до повторної адаптації. У коді вище базову лінію заморожено на весь час активного дотику (`if (!t->is_touched)`).
2. **Конденсація на внутрішній стінці та захисні кільця (Guard Ring):** При різкому перепаді температур на внутрішній грані пластику випадає мікроплівка води. Вона створює паразитний витік струму між ємнісним п'ятаком і земляним полігоном плати, викликаючи спонтанні спрацьовування. Лікування — розведення навколо сенсора захисного кільця (Driven Guard Ring), що живиться буферизованим сигналом тієї ж амплітуди й фази, ліквідуючи різницю потенціалів для плівки вологи, а також механічне притискання провідної губки безпосередньо до пластику без повітряних проміжків.
3. **Стробоскопічний ефект у світловоді:** Оптичний пластик (полікарбонат) не має інерції люмінофора. Якщо ШІМ-керування виконувати на частотах нижче 200 Гц, рух приладу в полі зору викликає розрив світлового сліду на ланцюжок окремих точок. Використовуйте апаратні таймери мікроконтролера з частотою не менше 1 кГц.
4. **Механічний прогин плати при натисканні:** Якщо ємнісний майданчик з'єднується з корпусом через стиснену пружину або тактова сервісна кнопка розміщена посередині плати без локальної опорної стійки, натискання викликає мікропрогин текстоліту FR-4. Це призводить до розтріскування прилеглих керамічних конденсаторів (MLCC) у типорозмірах 0805/1206 та виникнення п'єзоелектричних шумів у чутливих аналогових колах. Локальні різьбові стійки або ребра жорсткості корпусу розміщують безпосередньо під точками прикладання зусиль.

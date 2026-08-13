# ⚙️ Синтез 38 кГц несучої та декодування NEC-протоколу

Побудова пристроїв інфрачервоного зв'язку на мікроконтролерах вимагає вирішення двох автономних задач реального часу:
1. **Генерація модульованої несучої 38 кГц (Передача):** Формування точного високочастотного меандру заданої тривалості за допомогою апаратного ШІМ-модуля таймера без витрати процесорного часу в затримках `delay()`.
2. **Декодування часових інтервалів (Прийом):** Точне вимірювання тривалостей імпульсів від інтегрованого ІЧ-приймача за допомогою модуля захоплення (Input Capture) або переривань по зміні логічного рівня GPIO.

### Порівняння програмного (Bit-Banging) та апаратного підходів

У найпростіших аматорських конструкціях передачу 38 кГц часто виконують програмними цикличестими затримками (програмний Bit-Banging через `delayMicroseconds()`). Проте цей підхід має фатальні вади:
- Процесор повністю блокується на час передачі всієї кодової послідовності (до 70–100 мілісекунд).
- Будь-яке високопріоритетне переривання (наприклад, від UART, USB або системного кванту часу SysTick) збиває частоту несучої, що спричиняє відхилення від 38 кГц і втрату зв'язку.

Тому у професійній розробці генерацію несучої та вимірювання інтервалів прийому завжди покладають на апаратні таймери мікроконтролера.

### Апаратний розрахунок параметрів ШІМ 38 кГц для різних тактових частот

Частота несучої 38 кГц має період `T = 26.315 мкс`. Для забезпечення максимальної імпульсної оптичної потужності та запобігання перегріву світлодіода застосовують шпаруватість 33% (1/3 періоду вихід у HIGH, 2/3 періоду вихід у LOW).

Розглянемо математичну формулу обчислення регістрів таймера. Кількість тактів таймера `N_ticks` на один період несучої визначається як відношення частоти тактування `F_CLK` до частоти несучої `F_carrier = 38000 Гц`:

```
N_ticks = F_CLK / F_carrier

Регістр автоперезавантаження (Auto-Reload Register / Top):
ARR = N_ticks - 1

Регістр порівняння (Compare Register / Duty Cycle 33%):
CCR = N_ticks / 3
```

Наведемо порівняльну таблицю розрахунку регістрів для найпоширеніших мікроконтролерних платформ:

| Частота ядра `F_CLK` | Дільник Prescaler `PSC` | Тактова частота таймера | Період `ARR` | Порівняння `CCR` (33%) | Похибка частоти |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **8 МГц** (AVR / Internal RC) | 0 | 8 МГц | 209 | 70 | -0.19% |
| **16 МГц** (Arduino Uno / AVR) | 0 | 16 МГц | 420 | 140 | +0.01% |
| **48 МГц** (STM32F0 / Cortex-M0) | 0 | 48 МГц | 1262 | 421 | +0.01% |
| **72 МГц** (STM32F103 BluePill) | 0 | 72 МГц | 1894 | 631 | -0.02% |
| **80 МГц** (ESP8266 / ESP32 APB) | 0 | 80 МГц | 2104 | 701 | -0.01% |

Для випромінювання пачки 38 кГц мікроконтролер вмикає вихід ШІМ таймера (наприклад, переключаючи режим виводу з GPIO Input на PWM Output або дозволяючи генерацію через регістр `BDTR/CCER`), а для формування паузи — призупиняє вихідну генерацію, залишаючи таймер увімкненим для збереження фази.

### Налаштування апаратного цифрового фільтра на вході захоплення

Сучасні таймери мікроконтролерів (наприклад, серія TIM у STM32 або Timer1 в AVR) мають вбудований апаратний цифровий фільтр у модулі захоплення (Input Capture). Цей фільтр дозволяє повністю придушити короткочасні імпульсні завади та наводки на лінії від фотодіода без залучення процесора.

Конфігурація цифрового фільтра працює за принципом послідовного вибіркового контролю: логічний рівень на вході вважається зміненим лише тоді, коли `N` послідовних відліків внутрішньої частоти таймера підтверджують новий стан. Наприклад, біти `IC1F[3:0]` у регістрі `TIMx_CCMR1` дозволяють встановити фільтрацію на 4, 8 або 16 тактів, що повністю відсікає короткі високочастотні голки тривалістю менше 200 наносекунд.

### Програмна реалізація драйвера передавача та декодера

Нижче наведено повну реалізацію драйвера ІЧ-зв'язку. Версія на мові C розроблена для вбудованих систем з обмеженими ресурсами (без динамічного виділення пам'яті), а версія на C++17 надає безпечну об'єктно-орієнтовану інкапсуляцію зі строгим контролем типів через `std::optional`.

:::tabs
```c
/* c — Повний C-драйвер декодера NEC-протоколу з кінцевим автоматом */
#include <stdint.h>
#include <stdbool.h>

/* Структура декодованого кадру NEC */
typedef struct {
    uint32_t raw_code;     /* Повний 32-бітний код кадру */
    uint8_t  address;      /* 8-бітний адрес пристрою */
    uint8_t  address_inv;  /* Інверсний адрес для перевірки паритету */
    uint8_t  command;      /* 8-бітна команда */
    uint8_t  command_inv;  /* Інверсна команда */
    bool     is_repeat;    /* Прапорець кадру повтору */
    bool     valid;        /* Прапорець успішної перевірки КС */
} nec_frame_t;

/* Стани кінцевого автомата декодера */
typedef enum {
    NEC_STATE_IDLE,
    NEC_STATE_HEADER_SPACE,
    NEC_STATE_BIT_PULSE,
    NEC_STATE_BIT_SPACE
} nec_rx_state_t;

static nec_rx_state_t g_rx_state = NEC_STATE_IDLE;
static uint32_t g_rx_shift_reg = 0;
static uint8_t  g_rx_bit_count = 0;
static nec_frame_t g_last_frame = {0};

/*
 * Обробник переривання по зміні рівня виводу (Input Capture ISR).
 * delta_us — тривалість попереднього стану у мікросекундах.
 * pin_state_low — true, якщо поточний рівень на вході LOW (пачка 38 кГц).
 */
void nec_rx_process_edge(uint32_t delta_us, bool pin_state_low) {
    switch (g_rx_state) {
        case NEC_STATE_IDLE:
            /* Очікуємо спад сигналу: пачка преамбули тривалістю ~9000 мкс */
            if (pin_state_low && delta_us >= 8000 && delta_us <= 10000) {
                g_rx_state = NEC_STATE_HEADER_SPACE;
            }
            break;

        case NEC_STATE_HEADER_SPACE:
            /* Очікуємо паузу преамбули: 4500 мкс (звичайний кадр) або 2250 мкс (повтор) */
            if (!pin_state_low) {
                if (delta_us >= 4000 && delta_us <= 5000) {
                    g_rx_shift_reg = 0;
                    g_rx_bit_count = 0;
                    g_rx_state = NEC_STATE_BIT_PULSE;
                } else if (delta_us >= 2000 && delta_us <= 2600) {
                    /* Зафіксовано повтор натискання кнопки */
                    g_last_frame.is_repeat = true;
                    g_last_frame.valid = true;
                    g_rx_state = NEC_STATE_IDLE;
                } else {
                    g_rx_state = NEC_STATE_IDLE;
                }
            }
            break;

        case NEC_STATE_BIT_PULSE:
            /* Пачка перед кожним бітом: ~562 мкс */
            if (pin_state_low && delta_us >= 400 && delta_us <= 750) {
                g_rx_state = NEC_STATE_BIT_SPACE;
            } else {
                g_rx_state = NEC_STATE_IDLE;
            }
            break;

        case NEC_STATE_BIT_SPACE:
            /* Пауза визначає біт: ~562 мкс -> '0', ~1687 мкс -> '1' */
            if (!pin_state_low) {
                g_rx_shift_reg >>= 1;
                if (delta_us >= 1400 && delta_us <= 1950) {
                    g_rx_shift_reg |= 0x80000000UL; /* Біт '1' */
                } else if (delta_us < 400 || delta_us > 850) {
                    g_rx_state = NEC_STATE_IDLE;    /* Помилка таймингу */
                    break;
                }

                g_rx_bit_count++;
                if (g_rx_bit_count >= 32) {
                    /* Прийнято всі 32 біти: перевіряємо контрольні байти */
                    uint8_t addr  = (g_rx_shift_reg >> 0)  & 0xFF;
                    uint8_t naddr = (g_rx_shift_reg >> 8)  & 0xFF;
                    uint8_t cmd   = (g_rx_shift_reg >> 16) & 0xFF;
                    uint8_t ncmd  = (g_rx_shift_reg >> 24) & 0xFF;

                    if ((addr ^ naddr) == 0xFF && (cmd ^ ncmd) == 0xFF) {
                        g_last_frame.raw_code    = g_rx_shift_reg;
                        g_last_frame.address     = addr;
                        g_last_frame.address_inv = naddr;
                        g_last_frame.command     = cmd;
                        g_last_frame.command_inv = ncmd;
                        g_last_frame.is_repeat   = false;
                        g_last_frame.valid       = true;
                    }
                    g_rx_state = NEC_STATE_IDLE;
                } else {
                    g_rx_state = NEC_STATE_BIT_PULSE;
                }
            }
            break;
    }
}

bool nec_get_frame(nec_frame_t *out_frame) {
    if (g_last_frame.valid) {
        *out_frame = g_last_frame;
        g_last_frame.valid = false;
        return true;
    }
    return false;
}
```
```cpp
// cpp — C++17 об'єктна інкапсуляція декодера з std::optional та noexcept
#include <cstdint>
#include <optional>

struct NecCommand {
    uint8_t  address{0};
    uint8_t  command{0};
    uint32_t raw_code{0};
    bool     is_repeat{false};
};

class NecDecoder {
public:
    enum class State : uint8_t {
        Idle,
        HeaderSpace,
        BitPulse,
        BitSpace
    };

    void process_edge(uint32_t delta_us, bool pin_state_low) noexcept {
        switch (state_) {
            case State::Idle:
                if (pin_state_low && is_in_range(delta_us, 8000, 10000)) {
                    state_ = State::HeaderSpace;
                }
                break;

            case State::HeaderSpace:
                if (!pin_state_low) {
                    if (is_in_range(delta_us, 4000, 5000)) {
                        shift_reg_ = 0;
                        bit_count_ = 0;
                        state_ = State::BitPulse;
                    } else if (is_in_range(delta_us, 2000, 2600) && last_valid_command_) {
                        last_valid_command_->is_repeat = true;
                        pending_command_ = last_valid_command_;
                        state_ = State::Idle;
                    } else {
                        state_ = State::Idle;
                    }
                }
                break;

            case State::BitPulse:
                if (pin_state_low && is_in_range(delta_us, 400, 750)) {
                    state_ = State::BitSpace;
                } else {
                    state_ = State::Idle;
                }
                break;

            case State::BitSpace:
                if (!pin_state_low) {
                    shift_reg_ >>= 1;
                    if (is_in_range(delta_us, 1400, 1950)) {
                        shift_reg_ |= 0x80000000U; // Логічна '1'
                    } else if (!is_in_range(delta_us, 400, 850)) {
                        state_ = State::Idle;     // Збій таймингу
                        break;
                    }

                    if (++bit_count_ >= 32) {
                        auto parsed = parse_frame(shift_reg_);
                        if (parsed) {
                            last_valid_command_ = parsed;
                            pending_command_    = parsed;
                        }
                        state_ = State::Idle;
                    } else {
                        state_ = State::BitPulse;
                    }
                }
                break;
        }
    }

    [[nodiscard]] std::optional<NecCommand> poll_command() noexcept {
        auto cmd = pending_command_;
        pending_command_.reset();
        return cmd;
    }

private:
    State state_{State::Idle};
    uint32_t shift_reg_{0};
    uint8_t  bit_count_{0};
    std::optional<NecCommand> pending_command_{std::nullopt};
    std::optional<NecCommand> last_valid_command_{std::nullopt};

    static constexpr bool is_in_range(uint32_t val, uint32_t min_v, uint32_t max_v) noexcept {
        return val >= min_v && val <= max_v;
    }

    static std::optional<NecCommand> parse_frame(uint32_t raw) noexcept {
        const uint8_t addr  = (raw >> 0)  & 0xFF;
        const uint8_t naddr = (raw >> 8)  & 0xFF;
        const uint8_t cmd   = (raw >> 16) & 0xFF;
        const uint8_t ncmd  = (raw >> 24) & 0xFF;

        if ((addr ^ naddr) == 0xFF && (cmd ^ ncmd) == 0xFF) {
            return NecCommand{addr, cmd, raw, false};
        }
        return std::nullopt;
    }
};
```
:::

### Помилки реалізації, інверсії та захист від джитера

Під час розробки та налагодження систем інфрачервоного зв'язку виникають чотири типові категорії апаратних і програмних проблем:

1. **Інверсія сигналу виходу:** Інтегровані приймачі TSOP мають вихід з відкритим колектором (**Active LOW**). Це означає, що спад сигналу (Falling Edge) відповідає початку пачки 38 кГц, а наростання (Rising Edge) — початку паузи. Невірна трактовка полярності переривань призведе до декодування паузи замість пачки.
2. **Дрейф внутрішнього генератора:** Недорогі ІЧ-пульти живляться від батарейок та використовують дешеві керамічні резонатори або внутрішні RC-генератори з точністю ±5%. З урахуванням змін температури довкілля та розряду батареї допуск таймингів у кінцевому автоматі декодера повинен становити не менше **±20%** від номінальних значень.
3. **Захист від джитера переривань (ISR Latency):** Якщо мікроконтролер виконує інші критичні переривання з високим пріоритетом, затримка обробки переривання таймера може спотворити виміряне значення `delta_us` на 20–50 мікросекунд. Для усунення цієї проблеми рекомендовано використовувати апаратний блок Input Capture, який зберігає точний час спаду/наростання в апаратному регістрі незалежно від затримки входу в процедуру ISR.
4. **Обробка кадру повтору (Repeat Code):** Якщо користувач утримує кнопку пульта натиснутою, передавач надсилає повний кадр лише один раз, після чого кожні 110 мс випромінює короткі кадри повтору (Leader pulse 9 мс + space 2.25 мс + burst 562 мкс). Програма повинна правильно відрізняти повтор від нового натискання кнопки.

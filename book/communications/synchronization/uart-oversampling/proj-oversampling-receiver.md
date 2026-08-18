# ⚙️ Програмна модель апаратного блоку передискретизації UART

Вбудовані апаратні периферійні блоки UART у мікроконтролерах реалізують синхронізацію та демодуляцію асинхронного потоку за допомогою цифрових автоматів станів (FSM, *Finite State Machine*), що тактуються від внутрішнього генератора швидкості з частотою у 16 або 8 разів вищою за швидкість передачі даних. Розуміння логіки роботи такого апаратного автомата, алгоритмів фільтрації імпульсних завад на спадному фронті та мажоритарного голосування вибірок необхідне для глибокої діагностики помилок зв'язку, написання програмних емуляторів (Software UART / Bit-banging) та проєктування власних IP-ядер для FPGA.

Нижче наведено закінчену програмну модель приймача з передискретизацією, що відтворює поведінку апаратного макрокоміркового блоку мікроконтролерів STM32, NXP та Microchip з підтримкою динамічного перемикання режимів 16× та 8×.

### Архітектура цифрового приймача

Апаратний блок приймача з передискретизацією складається з п'яти взаємопов'язаних функціональних вузлів:

1. **Вхідний синхронізатор**: ланцюжок із двох послідовних D-тригерів для усунення метастабільності асинхронного вхідного сигналу RX відносно внутрішньої тактової сітки. Час напрацювання на відмову (MTBF, *Mean Time Between Failures*) такого синхронізатора перевищує сотні років за типових тактових частот периферії:

```
MTBF = exp(t_resolve / τ) / (T_0 · f_clk · f_data)
```

де `t_resolve` — доступний час виходу тригера зі стану невизначеності, `τ` — постійна часу регенерації комірки, `f_clk` — тактова частота передискретизації, а `f_data` — частота фронтів вхідного сигналу.

2. **Детектор спадного фронту (*Falling Edge Detector*)**: комбінаційна логічна схема, що порівнює поточний та попередній збережений стан синхронізованого сигналу. Вона фіксує перехід вхідної лінії з високого рівня (стан очікування *Mark*, логічна '1') у низький рівень (*Space*, логічний '0').
3. **Субтактовий лічильник-акумулятор фази**: модуль, що лічить субтакти від 0 до `N - 1` (де `N = 16` або `N = 8`). Скидається в 0 у момент виявлення спаду.
4. **Фільтр імпульсних завад (*Glitch Filter*)**: логіка перевірки дійсності стартового біта на середині інтервалу. Якщо лінія повернулася в '1' до контрольних тактів, подія визнається хибним спрацьовуванням, і автомат повертається в стан очікування без генерації переривань.
5. **Мажоритарний селектор 3 вибірок з детектором шуму**: схема, що фіксує значення лінії на трьох послідовних субтактах, обчислює результат за правилом більшості двох із трьох та виставляє апаратний прапорець завади `NF` (*Noise Flag*), якщо вибірки не були одностайними.

```
       RX Pin ───►[ 2-Stage Sync ]───►[ Edge Detector ]───► Скидання фази
                         │
                         ▼
             [ Sub-tick Counter ] ◄─── f_sample (16× / 8× baud)
                         │
                         ▼
             [ 3-Sample Voter ] ────► Мажоритарний біт (D0..D7)
                         │
                         ▼
             [ Noise Detector ] ────► Прапорець шуму (NF)
```

### Таблиця переходів цифрового автомата станів

Автомат станів приймача працює за строго детермінованим циклом, переходячи між чотирма основними станами:

| Поточний стан | Вхідна подія / Умова | Наступний стан | Дія апаратури |
|---|---|---|---|
| `RX_STATE_IDLE` | Спадний фронт (`prev=1 ∧ curr=0`) | `START_VERIFY` | Обнулення лічильника субтактів, скидання прапорця шуму |
| `RX_STATE_IDLE` | Немає спаду (`curr=1`) | `RX_STATE_IDLE` | Очікування нового спаду на лінії RX |
| `START_VERIFY` | Субтакти 7, 8, 9 (16×) або 3, 4, 5 (8×) | `START_VERIFY` | Збереження значень лінії в тригерний буфер вибірок |
| `START_VERIFY` | Такт голосування: мажоритарне значення = 0 | `DATA_BITS` (після такту `N-1`) | Старт підтверджено; перехід до прийому даних |
| `START_VERIFY` | Такт голосування: мажоритарне значення = 1 | `RX_STATE_IDLE` | Відсікання завади (Glitch); аварійне скидання в IDLE |
| `DATA_BITS` | Субтакти 7, 8, 9; біти з 0 до 7 | `DATA_BITS` | Голосування, зсув біта в `shift_register`, фіксація `NF` |
| `DATA_BITS` | Завершення 8-го біта даних (D7) | `STOP_VERIFY` | Підготовка до контролю стопового біта |
| `STOP_VERIFY` | Субтакти 7, 8, 9; мажоритарне значення = 1 | `RX_STATE_IDLE` | Кадр валідний; виставлення прапорця готовності даних |
| `STOP_VERIFY` | Субтакти 7, 8, 9; мажоритарне значення = 0 | `RX_STATE_IDLE` | Помилка кадрування (Framing Error `FE`); фіксація збою |

### Покроковий субтактовий аналіз прийому кадру

Щоб зрозуміти внутрішню динаміку цифрового блоку, простежимо поведінку субтактового лічильника та зсувного регістра під час прийому контрольного байта `0xA5` (двійковий запис `10100101b`, де біти передаються молодшим уперед: D0=1, D1=0, D2=1, D3=0, D4=0, D5=1, D6=0, D7=1) у стандартному режимі 16×:

1. **Фаза спокою (IDLE)**: лінія RX перебуває на рівні 1. Субтактовий лічильник не активний. На виході детектора спаду формується логічний нуль.
2. **Стартовий біт (такти 0..15)**:
   - *Такт 0*: лінія RX падає в 0. Детектор спаду генерує одиночний тактовий імпульс скидання. Лічильник субтактів встановлюється в 0, FSM переходить у стан `START_VERIFY`.
   - *Такти 1..6*: лічильник інкрементується. Лінія RX утримується на рівні 0.
   - *Такти 7, 8, 9*: схема вибірки фіксує значення лінії в буфер: `S7=0`, `S8=0`, `S9=0`.
   - *Такт 9*: мажоритарний селектор обчислює `(0 ∧ 0) ∨ (0 ∧ 0) ∨ (0 ∧ 0) = 0`. Оскільки результат дорівнює нулю, стартовий біт визнається дійсним, а прапорець шуму залишається 0.
   - *Такти 10..15*: завершення бітового інтервалу стартового біта.
3. **Прийом біта D0 = 1 (такти 16..31)**:
   - *Такт 15 → 0*: лічильник переповнюється, обнуляється, `bit_index` встановлюється в 0, FSM переходить у `DATA_BITS`.
   - *Такти 7, 8, 9*: вибірки дають `S7=1`, `S8=1`, `S9=1`.
   - *Такт 9*: мажоритарне значення = 1. Зсувний регістр записує біт у нульову позицію: `shift_register = 0x01`.
4. **Прийом бітів D1..D7 (такти 32..143)**:
   - На кожному бітовому інтервалі процес повторюється: лічильник відраховує 16 субтактів, на 9-му такті результат записується у відповідний розряд зсувного регістра.
   - Після завершення 8-го біта даних (D7) зсувний регістр містить значення `0xA5`, а FSM переходить у стан `STOP_VERIFY`.
5. **Стоповий біт (такти 144..159)**:
   - *Такти 7, 8, 9*: вибірки на лінії дають `S7=1`, `S8=1`, `S9=1`.
   - *Такт 9*: мажоритарний результат = 1 (стоп-біт підтверджено). Вміст зсувного регістра паралельно записується у вихідний регістр даних `RDR`, виставляється прапорець готовності `RXNE`, генерується переривання або запит DMA.
   - *Такт 15*: FSM повертається у стан `IDLE`, очікуючи наступного спадного фронту.

### Програмна реалізація мовами C та C++

Програмна модель надає функцію тактування `uart_rx_engine_tick()`, яка викликається на кожному такті частоти передискретизації `f_sample = N · f_baud`. На вхід подається поточний двійковий стан фізичного виводу RX.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

typedef enum {
    UART_OVERSAMPLING_16X = 16,
    UART_OVERSAMPLING_8X  = 8
} uart_os_mode_t;

typedef enum {
    RX_STATE_IDLE = 0,
    RX_STATE_START_VERIFY,
    RX_STATE_DATA_BITS,
    RX_STATE_STOP_VERIFY
} uart_rx_state_t;

typedef struct {
    uint8_t data_byte;
    bool    noise_flag;      /* Ознака шуму на лінії (вибірки 2:1) */
    bool    framing_error;   /* Помилка стоп-біта (стоп прочитано як 0) */
    bool    glitch_detected; /* Виявлено хибний старт */
} uart_rx_frame_t;

typedef struct {
    uart_os_mode_t   os_mode;
    uart_rx_state_t  state;
    uint8_t          subtick_counter;
    uint8_t          bit_index;
    uint8_t          shift_register;
    uint8_t          sample_buffer[3];
    uint8_t          prev_rx_pin;
    bool             frame_noise_accumulated;
    uart_rx_frame_t  last_frame;
    bool             has_new_frame;
} uart_rx_engine_t;

void uart_rx_init(uart_rx_engine_t *rx, uart_os_mode_t mode) {
    rx->os_mode = mode;
    rx->state = RX_STATE_IDLE;
    rx->subtick_counter = 0;
    rx->bit_index = 0;
    rx->shift_register = 0;
    rx->sample_buffer[0] = 1;
    rx->sample_buffer[1] = 1;
    rx->sample_buffer[2] = 1;
    rx->prev_rx_pin = 1;
    rx->frame_noise_accumulated = false;
    rx->has_new_frame = false;
    rx->last_frame.glitch_detected = false;
    rx->last_frame.framing_error = false;
    rx->last_frame.noise_flag = false;
    rx->last_frame.data_byte = 0;
}

/* Мажоритарне голосування 2 з 3 та детектор розбіжності */
static inline uint8_t majority_vote_3(const uint8_t s[3], bool *out_noise) {
    uint8_t sum = s[0] + s[1] + s[2];
    /* Якщо сума 1 або 2 — була розбіжність (шум на лінії) */
    *out_noise = (sum == 1 || sum == 2);
    return (sum >= 2) ? 1 : 0;
}

/* Обчислення позицій 3 центральних вибірок для обраного режиму */
static inline bool is_sample_subtick(uart_os_mode_t mode, uint8_t tick, uint8_t *sample_idx) {
    if (mode == UART_OVERSAMPLING_16X) {
        if (tick == 7)  { *sample_idx = 0; return true; }
        if (tick == 8)  { *sample_idx = 1; return true; }
        if (tick == 9)  { *sample_idx = 2; return true; }
    } else { /* 8X */
        if (tick == 3)  { *sample_idx = 0; return true; }
        if (tick == 4)  { *sample_idx = 1; return true; }
        if (tick == 5)  { *sample_idx = 2; return true; }
    }
    return false;
}

/* Такт апаратного автомата передискретизації */
void uart_rx_tick(uart_rx_engine_t *rx, uint8_t rx_pin) {
    uint8_t sample_idx = 0;
    const uint8_t last_tick = (uint8_t)rx->os_mode - 1;
    const uint8_t voting_tick = (rx->os_mode == UART_OVERSAMPLING_16X) ? 9 : 5;

    switch (rx->state) {
    case RX_STATE_IDLE:
        /* Детекція спадного фронту: лінія була 1 і стала 0 */
        if (rx->prev_rx_pin == 1 && rx_pin == 0) {
            rx->state = RX_STATE_START_VERIFY;
            rx->subtick_counter = 0;
            rx->frame_noise_accumulated = false;
        }
        break;

    case RX_STATE_START_VERIFY:
        /* Фіксація вибірок середини стартового біта */
        if (is_sample_subtick(rx->os_mode, rx->subtick_counter, &sample_idx)) {
            rx->sample_buffer[sample_idx] = rx_pin;
        }

        /* У момент останньої вибірки перевіряємо дійсність старту */
        if (rx->subtick_counter == voting_tick) {
            bool start_noise = false;
            uint8_t start_val = majority_vote_3(rx->sample_buffer, &start_noise);
            if (start_val != 0) {
                /* Хибний старт (завада / Glitch): лінія повернулася в 1 */
                rx->last_frame.glitch_detected = true;
                rx->state = RX_STATE_IDLE;
                break;
            }
            if (start_noise) {
                rx->frame_noise_accumulated = true;
            }
        }

        /* Завершення бітового інтервалу стартового біта */
        if (rx->subtick_counter >= last_tick) {
            rx->subtick_counter = 0;
            rx->bit_index = 0;
            rx->shift_register = 0;
            rx->state = RX_STATE_DATA_BITS;
        } else {
            rx->subtick_counter++;
        }
        break;

    case RX_STATE_DATA_BITS:
        if (is_sample_subtick(rx->os_mode, rx->subtick_counter, &sample_idx)) {
            rx->sample_buffer[sample_idx] = rx_pin;
        }

        /* Голосування наприкінці центрального вікна */
        if (rx->subtick_counter == voting_tick) {
            bool bit_noise = false;
            uint8_t bit_val = majority_vote_3(rx->sample_buffer, &bit_noise);
            if (bit_noise) {
                rx->frame_noise_accumulated = true;
            }
            /* Зсув даних молодшим бітом уперед (LSB First) */
            rx->shift_register |= (bit_val << rx->bit_index);
        }

        if (rx->subtick_counter >= last_tick) {
            rx->subtick_counter = 0;
            rx->bit_index++;
            if (rx->bit_index >= 8) {
                rx->state = RX_STATE_STOP_VERIFY;
            }
        } else {
            rx->subtick_counter++;
        }
        break;

    case RX_STATE_STOP_VERIFY:
        if (is_sample_subtick(rx->os_mode, rx->subtick_counter, &sample_idx)) {
            rx->sample_buffer[sample_idx] = rx_pin;
        }

        if (rx->subtick_counter == voting_tick) {
            bool stop_noise = false;
            uint8_t stop_val = majority_vote_3(rx->sample_buffer, &stop_noise);
            if (stop_noise) {
                rx->frame_noise_accumulated = true;
            }

            /* Формування вихідного кадру */
            rx->last_frame.data_byte = rx->shift_register;
            rx->last_frame.noise_flag = rx->frame_noise_accumulated;
            rx->last_frame.framing_error = (stop_val == 0); /* Стоп має бути 1 */
            rx->last_frame.glitch_detected = false;
            rx->has_new_frame = true;
        }

        if (rx->subtick_counter >= last_tick) {
            rx->subtick_counter = 0;
            rx->state = RX_STATE_IDLE;
        } else {
            rx->subtick_counter++;
        }
        break;
    }

    rx->prev_rx_pin = rx_pin;
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>
#include <span>
#include <iostream>
#include <iomanip>

enum class OversamplingMode : uint8_t {
    Ratio16x = 16,
    Ratio8x  = 8
};

enum class ReceiverState : uint8_t {
    Idle = 0,
    StartBitVerification,
    DataBitsReception,
    StopBitVerification
};

struct RxFrameResult {
    uint8_t data{0};
    bool    noise_flag{false};
    bool    framing_error{false};
};

template <OversamplingMode Mode = OversamplingMode::Ratio16x>
class UartOversamplingReceiver {
public:
    constexpr UartOversamplingReceiver() noexcept { reset(); }

    void reset() noexcept {
        state_ = ReceiverState::Idle;
        subtick_counter_ = 0;
        bit_index_ = 0;
        shift_reg_ = 0;
        samples_.fill(1);
        prev_rx_pin_ = 1;
        frame_noise_detected_ = false;
        glitch_flag_ = false;
    }

    // Повертає декодований кадр у разі завершення прийому стоп-біта
    std::optional<RxFrameResult> tick(uint8_t rx_pin) noexcept {
        std::optional<RxFrameResult> output_frame = std::nullopt;
        const uint8_t last_tick = static_cast<uint8_t>(Mode) - 1;
        constexpr uint8_t voting_tick = (Mode == OversamplingMode::Ratio16x) ? 9 : 5;

        switch (state_) {
        case ReceiverState::Idle:
            if (prev_rx_pin_ == 1 && rx_pin == 0) { // Спадний фронт
                state_ = ReceiverState::StartBitVerification;
                subtick_counter_ = 0;
                frame_noise_detected_ = false;
                glitch_flag_ = false;
            }
            break;

        case ReceiverState::StartBitVerification:
            recordSample(subtick_counter_, rx_pin);

            if (subtick_counter_ == voting_tick) {
                const auto [start_val, noise] = evaluateMajority();
                if (start_val != 0) { // Хибний старт: завада відфільтрована
                    glitch_flag_ = true;
                    state_ = ReceiverState::Idle;
                    break;
                }
                if (noise) frame_noise_detected_ = true;
            }

            if (subtick_counter_ >= last_tick) {
                subtick_counter_ = 0;
                bit_index_ = 0;
                shift_reg_ = 0;
                state_ = ReceiverState::DataBitsReception;
            } else {
                ++subtick_counter_;
            }
            break;

        case ReceiverState::DataBitsReception:
            recordSample(subtick_counter_, rx_pin);

            if (subtick_counter_ == voting_tick) {
                const auto [bit_val, noise] = evaluateMajority();
                if (noise) frame_noise_detected_ = true;
                shift_reg_ |= static_cast<uint8_t>(bit_val << bit_index_);
            }

            if (subtick_counter_ >= last_tick) {
                subtick_counter_ = 0;
                if (++bit_index_ >= 8) {
                    state_ = ReceiverState::StopBitVerification;
                }
            } else {
                ++subtick_counter_;
            }
            break;

        case ReceiverState::StopBitVerification:
            recordSample(subtick_counter_, rx_pin);

            if (subtick_counter_ == voting_tick) {
                const auto [stop_val, noise] = evaluateMajority();
                if (noise) frame_noise_detected_ = true;

                output_frame = RxFrameResult{
                    .data = shift_reg_,
                    .noise_flag = frame_noise_detected_,
                    .framing_error = (stop_val == 0)
                };
            }

            if (subtick_counter_ >= last_tick) {
                subtick_counter_ = 0;
                state_ = ReceiverState::Idle;
            } else {
                ++subtick_counter_;
            }
            break;
        }

        prev_rx_pin_ = rx_pin;
        return output_frame;
    }

    [[nodiscard]] bool wasGlitchRejected() const noexcept { return glitch_flag_; }

private:
    void recordSample(uint8_t tick, uint8_t pin_level) noexcept {
        if constexpr (Mode == OversamplingMode::Ratio16x) {
            if (tick == 7) samples_[0] = pin_level;
            else if (tick == 8) samples_[1] = pin_level;
            else if (tick == 9) samples_[2] = pin_level;
        } else {
            if (tick == 3) samples_[0] = pin_level;
            else if (tick == 4) samples_[1] = pin_level;
            else if (tick == 5) samples_[2] = pin_level;
        }
    }

    struct MajorityResult {
        uint8_t value;
        bool    noise;
    };

    [[nodiscard]] MajorityResult evaluateMajority() const noexcept {
        const uint8_t sum = samples_[0] + samples_[1] + samples_[2];
        const bool noise = (sum == 1 || sum == 2);
        const uint8_t val = (sum >= 2) ? 1 : 0;
        return {val, noise};
    }

    ReceiverState          state_{ReceiverState::Idle};
    uint8_t                subtick_counter_{0};
    uint8_t                bit_index_{0};
    uint8_t                shift_reg_{0};
    std::array<uint8_t, 3> samples_{1, 1, 1};
    uint8_t                prev_rx_pin_{1};
    bool                   frame_noise_detected_{false};
    bool                   glitch_flag_{false};
};
```
:::

### Покроковий розбір критичних сценаріїв функціонування

Розглянемо, як представлена програмна модель обробляє нестандартні та крайові стани лінії зв'язку:

#### 1. Класифікація імпульсних завад за тривалістю

Поведінка цифрового автомата суттєво залежить від тривалості імпульсу завади `t_pulse`:
- **Надвузький сплеск (`t_pulse < 1 / f_sample`)**: завада тривалістю менше періоду тактування фільтра (наприклад, 5–10 нс) повністю пригнічується вхідним двокаскадним тригером синхронізації та навіть не викликає спрацьовування детектора спаду.
- **Короткий глітч (`1 ≤ t_pulse < 4` субтакти)**: спад фіксується, лічильник субтактів починає рахувати, але на такті перевірки (такт 9 у режимі 16×) лінія вже повертається у високий рівень '1'. Мажоритарний селектор обчислює `Result = 1`, FSM ідентифікує подію як хибний старт і скидається в `IDLE` без запису сміття в регістри даних.
- **Середня завада (`4 ≤ t_pulse < 12` субтактів)**: якщо завада утримує лінію низькою під час перевірки стартового біта, але закінчується на середині першого біта даних D0, стартовий біт буде хибно підтверджено. Проте на наступних бітах виникне невідповідність мажоритарних вибірок, і в кінці кадру буде згенеровано апаратну помилку кадрування `FE` (*Framing Error*), оскільки стоповий біт виявиться на неочікуваній позиції.

#### 2. Обробка стану розриву лінії (Break Detection)

Якщо фізичний провідник RX обривається або замкнений на землю, лінія залишається в стані логічного нуля '0' невизначено довго.
1. Приймач фіксує спадний фронт та валідує старт-біт.
2. Далі зчитуються 8 нульових бітів даних `0x00`.
3. На етапі стопового біта мажоритарний селектор фіксує '0' замість обов'язкової одиниці '1' і виставляє прапорець помилки кадрування `FE`.
4. Якщо лінія утримується на рівні '0' протягом повного кадрового інтервалу (10–11 бітів), сучасні контролери (як-от STM32 та Microchip) виставляють спеціальний прапорець виявлення розриву лінії `LBDF` (*Line Break Detection Flag*).

#### 3. Подвійна буферизація та переповнення (Overrun Error)

Апаратні периферійні блоки UART використовують дворівневу буферизацію:
1. **Зсувний регістр прийому (RSR, *Receive Shift Register*)**: внутрішній регістр, у який апаратний автомат побітово зсуває біти даних D0..D7 безпосередньо з виходу мажоритарного селектора.
2. **Регістр даних прийому (RDR, *Receive Data Register*)**: доступний програмісту регістр (або вхідний FIFO-буфер глибиною 4–16 слів).

У момент валідації стопового біта вміст зсувного регістра паралельно копіюється в `RDR`, виставляється прапорець готовності `RXNE` (*Read Data Register Not Empty*), і генерується переривання. Якщо центральний процесор або контролер DMA не встигли вичитати попередній байт із `RDR` до моменту прибуття нового стопового біта, попередні дані затираються, і апаратура фіксує критичну помилку переповнення `ORE` (*Overrun Error*).

#### 4. Взаємодія з прямим доступом до пам'яті (DMA) та перериваннями

В реальних прошивках кожен прийнятий байт супроводжується статусними прапорцями помилок (`PE` — паритет, `FE` — кадр, `NF` — шум, `ORE` — переповнення FIFO). 
- За використання DMA статус помилки шуму `NF` не генерує окремого запиту на передачу даних, але встановлює біт переривання в контролері USART.
- Якщо обробник переривання фіксує часті спрацьовування `NF` при успішній доставці байтів через DMA, це свідчить про наближення лінії до граничної межі затухання або підвищений джиттер передавача.

#### 5. Реалізація контролю парності (Parity Bit Verification)

У конфігураціях з контролем парності (7E1, 8E1, 8O1) між старшим бітом даних D7 та стоповим бітом передається додатковий біт парності `P`.
Апаратний блок передискретизації виділяє для біта парності окремий повноцінний інтервал у 16 субтактів (або 8 субтактів при 8×):
1. На субтактах 7, 8 та 9 знімаються три вибірки та обчислюється мажоритарне значення біта `P_rx`.
2. Внутрішній апаратний лічильник парності паралельно підраховує кількість одиниць у зсувному регістрі: `Parity_calc = D0 ⊕ D1 ⊕ ... ⊕ D7`.
3. Для парного контролю (Even Parity) значення `P_rx` має дорівнювати `Parity_calc`. Для непарного (Odd Parity) — інверсії `¬Parity_calc`.
4. У разі невідповідності апаратура виставляє прапорець помилки парності `PE` (*Parity Error*), який зберігається в регістрі статусу разом із прийнятим байтом.

#### 6. Проєктування IP-ядер для FPGA (RTL Verilog / VHDL)

При синтезі блоку передискретизації на базі FPGA застосовують синхронний дизайн із єдиним доменом тактової частоти `clk`:
- Лічильник субтактів будується як синхронний дільник із лічильником дозволу тактування (*Clock Enable Generator*), що виключає появу небезпечних стробів та глітчів на тактових лініях (*gated clocks*).
- Стан FSM кодується за методом *One-Hot* (для мінімізації кількості логічних рівнів LUT і досягнення максимальної тактової частоти понад 200 МГц) або *Gray* (для зниження динамічного енергоспоживання).
- Регістри мажоритарних вибірок `sample_buffer[2:0]` тактуються стробом `enable_sample`, який формується комбінаційно за рівністю лічильника субтактів значенням 7, 8 та 9.
- Для FPGA з низькою щільністю логіки (наприклад, Lattice iCE40) повний приймач UART 16× з фільтром завад займає менше 60 логічних елементів (LUT4) та 45 тригерів (DFF).

#### 7. Автоматичне визначення швидкості (Auto-Baud Rate Detection)

Сучасні апаратні блоки UART (зокрема в контролерах STM32 та Microchip) підтримують режим автопідстроювання швидкості `ABR` (*Auto-Baud Rate*). 
- Робота базується на вимірюванні тривалості стартового біта або спеціального тестового символу (наприклад, `0x7F` або `0x55` з частими переходами 0-1) за допомогою лічильника тактової частоти шини.
- Отримане значення автоматично завантажується в регістр `USART_BRR`, після чого блок передискретизації починає штатний прийом даних без участі центрального процесора.

#### 8. Відновлення після помилок та скидання FSM (Error Recovery)

Після виникнення помилок кадрування `FE` або шуму `NF` програмний драйвер повинен коректно очистити стан периферійного блоку:
- У сучасних мікроконтролерах прапорці скидаються записом одиниці у відповідний розряд регістра очищення переривань `USART_ICR` (наприклад, біти `FECF`, `NCF`, `ORECF`).
- Якщо лінія зазнала тривалого шумового шторму, вичитування сміттєвого байта з `RDR` та програмне скидання модуля повертають FSM у стан `IDLE`, готуючи до синхронізації за чистим стартовим фронтом.
- У разі виявлення розриву лінії драйвер може перевести модуль у режим очікування сигналу пробудження (*Wakeup on Idle Line*).

#### 9. Особливості тестування та генерація тестових векторів

Для верифікації RTL-моделей в середовищах моделювання (ModelSim, Questa, Verilator) створюють тестові стенди (*Testbenches*), які імітують фізичні спотворення реального каналу зв'язку:
- **Генератор випадкового джиттеру**: додає випадкову часову затримку від 0 до `0.1 · T_bit` до кожного перепаду напруги.
- **Інжектор імпульсних перешкод**: вставляє випадкові викиди тривалістю від 1 до 5 тактових імпульсів на різних фазах бітового інтервалу.
- **Емулятор дрейфу частоти**: змінює період передавача на величину від −5% до +5%, перевіряючи граничні точки виникнення помилок кадрування `FE`.
- **Автоматизоване порівняння з еталоном (Golden Model)**: результати роботи синтезованого блоку в RTL автоматично зіставляються з виходом наведеної вище програмної C++ моделі, а будь-яка розбіжність вибірок фіксується директивою `$fatal` у середовищі симуляції.

### Тестовий стенд: верифікація завад та мажоритарного голосування

Для перевірки стійкості автомата проведемо симуляцію трьох типових аварійних ситуацій на фізичній лінії:
1. **Короткочасний викид шуму (Glitch 20 нс)**: на 2 субтакти лінія падає в 0 у стані спокою. Фільтр завад повинен скинути FSM в IDLE на такті 9 без формування кадру.
2. **Імпульсна завада посеред біта даних**: на 8-му субтакті біта D0 вибірки дають `1, 0, 1`. Мажоритарний селектор повинен відновити дійсне значення 1 і виставити прапорець `noise_flag`.
3. **Прийом байта 0xA5 у режимах 16× та 8×**.

:::tabs
```c
int main(void) {
    uart_rx_engine_t rx16;
    uart_rx_init(&rx16, UART_OVERSAMPLING_16X);

    printf("=== ТЕСТ 1: Фільтрація імпульсної завади (Glitch Filter) ===\n");
    /* Лінія в IDLE */
    uart_rx_tick(&rx16, 1);
    /* Короткий спад на 2 такти */
    uart_rx_tick(&rx16, 0); // Такт 0: спад (Start verify почався)
    uart_rx_tick(&rx16, 0); // Такт 1
    /* Лінія відновилася в 1 */
    for (int t = 2; t < 16; ++t) {
        uart_rx_tick(&rx16, 1);
    }
    if (rx16.last_frame.glitch_detected && rx16.state == RX_STATE_IDLE) {
        printf("✓ Успіх: заваду відфільтровано, FSM повернувся в IDLE\n\n");
    }

    printf("=== ТЕСТ 2: Мажоритарне відновлення зашумленого біта ===\n");
    /* Передача байта 0x01 (D0=1, D1..D7=0) із завадою на D0: вибірки 1, 0, 1 */
    uart_rx_init(&rx16, UART_OVERSAMPLING_16X);
    /* Старт-біт (16 нулів) */
    for (int t = 0; t < 16; ++t) uart_rx_tick(&rx16, 0);
    /* D0 (має бути 1, але на такті 8 шум = 0) */
    for (int t = 0; t < 16; ++t) {
        uint8_t pin = (t == 8) ? 0 : 1; // Вибірки: S7=1, S8=0, S9=1
        uart_rx_tick(&rx16, pin);
    }
    /* D1..D7 (чисті нулі) */
    for (int b = 1; b < 8; ++b) {
        for (int t = 0; t < 16; ++t) uart_rx_tick(&rx16, 0);
    }
    /* Стоп-біт (одиниці) */
    for (int t = 0; t < 16; ++t) uart_rx_tick(&rx16, 1);

    if (rx16.has_new_frame) {
        printf("✓ Отримано байт: 0x%02X (очікувалось 0x01)\n", rx16.last_frame.data_byte);
        printf("✓ Прапорець шуму NF: %s (очікувалось TRUE)\n", rx16.last_frame.noise_flag ? "TRUE" : "FALSE");
        printf("✓ Помилка кадру FE: %s\n", rx16.last_frame.framing_error ? "TRUE" : "FALSE");
    }

    return 0;
}
```
```cpp
int main() {
    UartOversamplingReceiver<OversamplingMode::Ratio16x> rx;

    std::cout << "=== ТЕСТ 1: Фільтрація імпульсної завади (Glitch Filter) ===\n";
    rx.tick(1);
    rx.tick(0); // Спад
    rx.tick(0);
    for (int t = 2; t < 16; ++t) {
        rx.tick(1); // Відновлення лінії в 1
    }
    if (rx.wasGlitchRejected()) {
        std::cout << "✓ Успіх: заваду відфільтровано, FSM повернувся в Idle\n\n";
    }

    std::cout << "=== ТЕСТ 2: Мажоритарне відновлення зашумленого біта ===\n";
    rx.reset();
    // Старт-біт (16 нулів)
    for (int t = 0; t < 16; ++t) rx.tick(0);
    // D0 (рівень 1, на такті 8 сплеск 0)
    for (int t = 0; t < 16; ++t) {
        uint8_t pin = (t == 8) ? 0 : 1;
        rx.tick(pin);
    }
    // D1..D7 (чисті нулі)
    for (int b = 1; b < 8; ++b) {
        for (int t = 0; t < 16; ++t) rx.tick(0);
    }
    // Стоп-біт (одиниці)
    std::optional<RxFrameResult> frame;
    for (int t = 0; t < 16; ++t) {
        auto res = rx.tick(1);
        if (res) frame = res;
    }

    if (frame.has_value()) {
        std::cout << "✓ Отримано байт: 0x" << std::hex << std::uppercase << std::setw(2)
                  << std::setfill('0') << static_cast<int>(frame->data) << "\n";
        std::cout << "✓ Прапорець шуму NF: " << std::boolalpha << frame->noise_flag << "\n";
        std::cout << "✓ Помилка кадру FE: " << frame->framing_error << "\n";
    }

    return 0;
}
```
:::

### Інженерні висновки та поради щодо програмної реалізації (Bit-Banging)

1. **Фільтр стартового біта рятує від каскадних збоїв**: якби приймач починав формувати байт за кожним спадним фронтом без перевірки середини, 20-наносекундна завада блокувала б інтерфейс на цілий кадровий інтервал (при 9600 бод це понад 1 мілісекунду), через що наступний дійсний пакет було б гарантовано втрачено.
2. **Мажоритарне голосування діє як цифровий інтегратор**: одиночні викиди тривалістю до `1 / N` біта відновлюються без спотворення значення байта, а статусний прапорець `NF` сигналізує драйверу про деградацію фізичного каналу ще до виникнення фатальних помилок паритету чи контрольної суми CRC.
3. **Особливості програмної реалізації на таймерах**: у разі створення програмного UART на мікроконтролерах без вільного апаратного блоку (Bit-Banging UART) рекомендується налаштовувати апаратний таймер на переривання з частотою `3 · f_baud` або `4 · f_baud` для реалізації спрощеної передискретизації замість одноразового опитування посередині біта. Це дозволяє вбудувати базовий фільтр завад та зменшити чутливість до затримок обробки переривань іншими драйверами операційної системи реального часу (RTOS).
4. **Уникнення інверсії пріоритетів в RTOS**: якщо прийом реалізовано програмним опитуванням, обробник переривання таймера повинен мати найвищий апаратний пріоритет (вище системного тику RTOS), оскільки джиттер виклику ISR понад `0.5 · t_sub` миттєво руйнує узгодженість мажоритарного вікна.

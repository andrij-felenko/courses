# Демодуляція та декодер пакетів стандарту Qi

Бездротова передача енергії за стандартом WPC Qi передає як потужність, так і цифрові дані керування крізь єдиний магнітний зв'язок без додаткових радіомодулів на кшталт Bluetooth чи Wi-Fi. Приймач модулює власний опір, що створює флуктуації амплітуди струму в первинній котушці передавача (зворотне розсіяння, *backscatter load modulation*). Цей практичний проєкт реалізує повний стек прийому даних на боці передавача: від апаратної фільтрації та декодування коду без повернення до нуля з фазовою маніпуляцією (Biphase Mark Code, BMC) до автомата станів розбору пакетів Qi та замкненого ПІД-регулятора потужності.

## Фізичний рівень та модуляція BMC

Зв'язок від приймача до передавача здійснюється на швидкості `2000 біт/с` (тривалість одного бітового інтервалу `T_bit = 500 мкс`). Сигнал кодується методом Biphase Mark Code (BMC, диференційне манчестерське кодування):
1. На початку **кожного** бітового інтервалу обов'язково відбувається фронт (перепад сигналу `0 → 1` або `1 → 0`).
2. Для передачі логічної **«1»** у середині бітового інтервалу (через `250 мкс`) додається **ще один** додатковий перепад.
3. Для передачі логічного **«0»** посередині бітового інтервалу перепад **відсутній** (сигнал тримає незмінний рівень протягом усіх `500 мкс`).

Таке кодування є самосинхронізовним: передавач може підлаштовувати свій таймер за кожним початковим фронтом, компенсуючи температурне плавання тактової частоти генератора приймача (допустиме відхилення за стандартом Qi становить `±4%`).

Для надійного захоплення імпульсів таймер захоплення входів (Input Capture) вимірює тривалість інтервалу `Δt` між сусідніми фронтами:
- Інтервал напівперіоду (Half-bit cell): номінально `250 мкс`. З урахуванням джитеру, перехідних процесів та фазового шуму інвертора вікно розпізнавання встановлюють у межах `180–320 мкс`.
- Інтервал повного біта (Full-bit cell): номінально `500 мкс`. Вікно розпізнавання встановлюють у межах `420–580 мкс`.
- Будь-який імпульс коротший за `180 мкс` відкидається як комутаційна завада (глитч), а довший за `580 мкс` фіксує втрату синхронізації та скидає декодер у стан пошуку преамбули.

## Аналоговий вхідний тракт (AFE)

Перш ніж потрапити на цифровий вхід таймера мікроконтролера, високочастотний струм первинної котушки (110–205 кГц) амплітудою до 5 А повинен пройти аналогове перетворення:

1. **Датчик струму або напруги**: напруга знімається або з точного низькоомного шунта (наприклад, 20 мОм у нижньому плечі моста), або за допомогою вимірювального трансформатора струму, або через резистивний дільник безпосередньо з резонансного конденсатора `C_tx`.
2. **Детектор обвідної (Envelope Detector)**: діод Шотткі та швидкий піковий детектор на операційному підсилювачі виділяють амплітудну обвідну високої частоти, відсікаючи тримальну синусоїду 125 кГц.
3. **Фільтр високих частот (HPF)**: пасивний RC-ланцюг (`C = 10 нФ, R = 10 кОм`, частота зрізу `~1.6 кГц`) усуває постійну складову струму котушки та повільні дрейфи живлення, пропускаючи лише швидкі модуляційні перепади 2 кГц.
4. **Активний смуговий фільтр (BPF)**: активний фільтр другого порядку Саллена-Кея з центральною частотою 2 кГц пригнічує низькочастотні пульсації випрямляча мережі 100 Гц та залишки тримальної частоти 125 кГц.
5. **Гістерезисний компаратор**: тригер Шмітта з динамічним порогом перетворює аналоговий двополярний сигнал у прямокутні логічні рівні `0 / 3.3 В`.

## Формат пакета даних Qi

Кожен інформаційний пакет складається з чотирьох послідовних полів:
1. **Преамбула (Preamble)**: послідовність від 11 до 25 логічних одиниць (`0x7F...`), яка дозволяє демодулятору передавача налаштувати фазове автопідлаштування та зафіксувати рівень порогу.
2. **Заголовок (Header, 1 байт)**: визначає тип пакета та кількість інформаційних байтів корисного навантаження (від 1 до 27 байтів).
3. **Корисне навантаження (Payload, 1–27 байтів)**: дані вимірювань, ідентифікації чи конфігурації.
4. **Контрольна сума (Checksum, 1 байт)**: побайтове виключне АБО (XOR) байта заголовка та всіх байтів корисного навантаження:
   ```
   Checksum = Header ⊕ Byte[0] ⊕ Byte[1] ⊕ ... ⊕ Byte[N-1]
   ```

### Основні типи пакетів стандарту Qi

| Байт заголовка | Назва пакета | Довжина даних | Призначення |
| :--- | :--- | :--- | :--- |
| `0x01` | **Signal Strength** | 1 байт | Рівень сигналу на стадії Ping (0–255), слугує для виявлення центрів котушок |
| `0x02` | **End Power Transfer (EPT)** | 1 байт | Код причини завершення зарядки (0x01: батарея повна, 0x02: перегрів, 0x03: перенапруга, 0x08: перезапуск) |
| `0x03` | **Control Error Packet (CEP)** | 1 байт | Знаковий відхил потужності (`−128...+127`) для покрокового замкненого регулювання |
| `0x04` | **Received Power (8-bit)** | 1 байт | Значення отриманої приймачем потужності для контролю сторонніх предметів (FOD) |
| `0x31` | **Received Power (24-bit)** | 3 байти | Розширений пакет виміряної потужності (EPP, точність до міліват) |
| `0x51` | **Configuration** | 5 байтів | Клас потужності, максимальна потужність, прапорці вікна регулювання |
| `0x71` | **Identification** | 7 байтів | Код виробника, версія стандарту Qi (1.2 / 1.3), серійний номер чіпа |

## Замкнена петля регулювання (Control Error Packet)

У фазі передачі енергії приймач кожні `32–250 мс` надсилає пакет помилки керування `CEP` (Header `0x03`). Байт даних є знаковим цілим числом `int8_t`:
- `CEP = 0`: напруга на виході випрямляча `V_rect` точно відповідає цільовому значенню (наприклад, 7.0 В для стабілізатора 5 В). Зміна частоти не потрібна.
- `CEP > 0`: вихідна напруга просіла нижче норми (наприклад, телефон увімкнув екран або збільшив струм заряду). Передавач повинен **збільшити** вихідну потужність. Для топології SS це означає **зниження** робочої частоти ближче до резонансу (зростання передавального коефіцієнта) або збільшення напруги живлення H-моста.
- `CEP < 0`: вихідна напруга завищена (наприклад, акумулятор майже зарядився, і струм спав). Передавач повинен **зменшити** потужність, **підвищуючи** частоту інвертора далі від резонансу.

Якщо передавач не отримує черговий пакет CEP протягом таймауту `1.5 с`, протокол Qi вимагає негайно знеструмити котушку передавача (аварійний захист від розриву зворотного зв'язку).

## Реалізація декодера та регулятора

Нижче наведено модульний код приймача та парсера Qi-пакетів:
- Програмний декодер часових інтервалів BMC за перериваннями таймера (Input Capture).
- Побайтовий автомат станів розбору пакетів Qi з перевіркою контрольної суми XOR.
- Обробник пакета помилки регулювання `CEP` з ПІД-корекцією робочої частоти інвертора.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define QI_BIT_HALF_MIN_US    180
#define QI_BIT_HALF_MAX_US    320
#define QI_BIT_FULL_MIN_US    420
#define QI_BIT_FULL_MAX_US    580

#define QI_MAX_PAYLOAD_LEN    32
#define QI_PREAMBLE_MIN_BITS  11

/* Заголовки стандартних пакетів WPC Qi */
#define QI_HDR_SIGNAL_STRENGTH  0x01
#define QI_HDR_END_TRANSFER     0x02
#define QI_HDR_CONTROL_ERROR    0x03
#define QI_HDR_RECEIVED_POWER   0x04
#define QI_HDR_CONFIG           0x51
#define QI_HDR_IDENTIFICATION   0x71

typedef enum {
    BMC_WAIT_SYNC,
    BMC_FIRST_HALF,
    BMC_FULL_CELL
} BmcState;

typedef enum {
    QI_STATE_PREAMBLE,
    QI_STATE_HEADER,
    QI_STATE_PAYLOAD,
    QI_STATE_CHECKSUM
} QiParserState;

typedef struct {
    uint8_t header;
    uint8_t payload[QI_MAX_PAYLOAD_LEN];
    uint8_t payload_len;
    uint8_t checksum;
    bool valid;
} QiPacket;

typedef struct {
    /* Стан BMC */
    BmcState bmc_state;
    uint32_t last_edge_time_us;
    uint8_t preamble_count;

    /* Побайтовий бітовий буфер */
    uint8_t rx_byte;
    uint8_t bit_index;

    /* Стан парсера пакетів */
    QiParserState parser_state;
    QiPacket current_packet;
    uint8_t payload_idx;
    uint8_t calc_checksum;

    /* Колбек успішного прийому */
    void (*on_packet_received)(const QiPacket *pkt);
} QiReceiver;

/* Ініціалізація структури приймача */
void qi_receiver_init(QiReceiver *rx, void (*callback)(const QiPacket *pkt)) {
    rx->bmc_state = BMC_WAIT_SYNC;
    rx->last_edge_time_us = 0;
    rx->preamble_count = 0;
    rx->rx_byte = 0;
    rx->bit_index = 0;
    rx->parser_state = QI_STATE_PREAMBLE;
    rx->payload_idx = 0;
    rx->calc_checksum = 0;
    rx->on_packet_received = callback;
    rx->current_packet.valid = false;
}

/* Отримання довжини корисного навантаження за кодом заголовка */
static uint8_t qi_get_payload_length(uint8_t header) {
    switch (header) {
        case QI_HDR_SIGNAL_STRENGTH: return 1;
        case QI_HDR_END_TRANSFER:    return 1;
        case QI_HDR_CONTROL_ERROR:   return 1;
        case QI_HDR_RECEIVED_POWER:  return 1;
        case QI_HDR_CONFIG:          return 5;
        case QI_HDR_IDENTIFICATION:  return 7;
        default:
            /* Для нестандартних/пропрієтарних пакетів Qi: біти 5..7 задають довжину */
            return (header >> 5) + 1;
    }
}

/* Обробка одного завершеного прийнятого байта */
static void qi_parser_push_byte(QiReceiver *rx, uint8_t byte) {
    switch (rx->parser_state) {
        case QI_STATE_PREAMBLE:
            /* Перший не-0xFF байт після преамбули є заголовком */
            rx->current_packet.header = byte;
            rx->current_packet.payload_len = qi_get_payload_length(byte);
            rx->calc_checksum = byte;
            rx->payload_idx = 0;
            rx->parser_state = (rx->current_packet.payload_len > 0) ? QI_STATE_PAYLOAD : QI_STATE_CHECKSUM;
            break;

        case QI_STATE_PAYLOAD:
            rx->current_packet.payload[rx->payload_idx++] = byte;
            rx->calc_checksum ^= byte;
            if (rx->payload_idx >= rx->current_packet.payload_len) {
                rx->parser_state = QI_STATE_CHECKSUM;
            }
            break;

        case QI_STATE_CHECKSUM:
            rx->current_packet.checksum = byte;
            rx->current_packet.valid = (rx->calc_checksum == byte);
            if (rx->current_packet.valid && rx->on_packet_received) {
                rx->on_packet_received(&rx->current_packet);
            }
            /* Повертаємося до пошуку наступної преамбули */
            rx->parser_state = QI_STATE_PREAMBLE;
            rx->preamble_count = 0;
            break;
    }
}

/* Обробка одного прийнятого біта */
static void qi_push_bit(QiReceiver *rx, uint8_t bit) {
    if (rx->parser_state == QI_STATE_PREAMBLE) {
        if (bit == 1) {
            rx->preamble_count++;
        } else {
            /* Якщо накопичили достатньо одиниць преамбули, перший 0 позначає Start Bit */
            if (rx->preamble_count >= QI_PREAMBLE_MIN_BITS) {
                rx->bit_index = 0;
                rx->rx_byte = 0;
                rx->parser_state = QI_STATE_HEADER;
            }
            rx->preamble_count = 0;
        }
        return;
    }

    /* Збір байта: у стандарті Qi біти передаються MSB-first у межах байта */
    rx->rx_byte = (rx->rx_byte << 1) | (bit & 0x01);
    rx->bit_index++;

    if (rx->bit_index >= 8) {
        qi_parser_push_byte(rx, rx->rx_byte);
        rx->bit_index = 0;
        rx->rx_byte = 0;
    }
}

/* Переривання захоплення фронтів таймера (Edge Capture ISR) */
void qi_receiver_on_edge(QiReceiver *rx, uint32_t current_time_us) {
    if (rx->last_edge_time_us == 0) {
        rx->last_edge_time_us = current_time_us;
        return;
    }

    uint32_t dt = current_time_us - rx->last_edge_time_us;
    rx->last_edge_time_us = current_time_us;

    /* Фільтрація брязкоту та викидів */
    if (dt < QI_BIT_HALF_MIN_US) {
        return;
    }

    switch (rx->bmc_state) {
        case BMC_WAIT_SYNC:
            if (dt >= QI_BIT_HALF_MIN_US && dt <= QI_BIT_HALF_MAX_US) {
                rx->bmc_state = BMC_FIRST_HALF;
            } else if (dt >= QI_BIT_FULL_MIN_US && dt <= QI_BIT_FULL_MAX_US) {
                qi_push_bit(rx, 0);
            }
            break;

        case BMC_FIRST_HALF:
            /* Очікуємо другу половину біта для логічної «1» */
            if (dt >= QI_BIT_HALF_MIN_US && dt <= QI_BIT_HALF_MAX_US) {
                qi_push_bit(rx, 1);
                rx->bmc_state = BMC_WAIT_SYNC;
            } else {
                /* Помилка синхронізації — скидання стану */
                rx->bmc_state = BMC_WAIT_SYNC;
                rx->preamble_count = 0;
            }
            break;

        default:
            rx->bmc_state = BMC_WAIT_SYNC;
            break;
    }
}

/* ========================================================================= */
/* Замкнений ПІД-регулятор потужності інвертора за пакетами CEP               */
/* ========================================================================= */

#define FREQ_MIN_KHZ  110.0f
#define FREQ_MAX_KHZ  205.0f
#define KP_GAIN       0.25f
#define KI_GAIN       0.05f

typedef struct {
    float current_freq_khz;
    float integral_err;
} QiPowerController;

void qi_controller_init(QiPowerController *ctrl) {
    ctrl->current_freq_khz = 145.0f; /* Стартова безпечна частота вище резонансу */
    ctrl->integral_err = 0.0f;
}

/* Обробка пакета Control Error Packet (CEP) */
void qi_controller_process_cep(QiPowerController *ctrl, int8_t cep_value) {
    /* cep_value > 0: приймачу бракує напруги -> ЗНИЖУЄМО частоту (ближче до резонансу)
       cep_value < 0: напруга завищена -> ПІДВИЩУЄМО частоту (далі від резонансу) */
    float error = (float)cep_value;
    ctrl->integral_err += error;

    /* Анти-вінд-ап захист інтегратора */
    if (ctrl->integral_err > 50.0f)  ctrl->integral_err = 50.0f;
    if (ctrl->integral_err < -50.0f) ctrl->integral_err = -50.0f;

    float delta_f = -(KP_GAIN * error + KI_GAIN * ctrl->integral_err);
    ctrl->current_freq_khz += delta_f;

    /* Захисне насичення робочого діапазону частот */
    if (ctrl->current_freq_khz < FREQ_MIN_KHZ) ctrl->current_freq_khz = FREQ_MIN_KHZ;
    if (ctrl->current_freq_khz > FREQ_MAX_KHZ) ctrl->current_freq_khz = FREQ_MAX_KHZ;
}
```
```cpp
#include <cstdint>
#include <functional>
#include <span>
#include <array>
#include <algorithm>

namespace qi {

constexpr uint32_t kBitHalfMinUs = 180;
constexpr uint32_t kBitHalfMaxUs = 320;
constexpr uint32_t kBitFullMinUs = 420;
constexpr uint32_t kBitFullMaxUs = 580;

constexpr size_t   kMaxPayloadLen   = 32;
constexpr uint8_t  kPreambleMinBits = 11;

enum class Header : uint8_t {
    SignalStrength = 0x01,
    EndTransfer    = 0x02,
    ControlError   = 0x03,
    ReceivedPower  = 0x04,
    Configuration  = 0x51,
    Identification = 0x71
};

struct Packet {
    Header header{Header::SignalStrength};
    std::array<uint8_t, kMaxPayloadLen> payload{};
    uint8_t payload_len{0};
    uint8_t checksum{0};
    bool valid{false};

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return std::span<const uint8_t>(payload.data(), payload_len);
    }
};

class Receiver {
public:
    using PacketCallback = std::function<void(const Packet&)>;

    explicit Receiver(PacketCallback callback = nullptr)
        : callback_(std::move(callback)) {}

    void on_edge(uint32_t current_time_us) {
        if (last_edge_time_us_ == 0) {
            last_edge_time_us_ = current_time_us;
            return;
        }

        const uint32_t dt = current_time_us - last_edge_time_us_;
        last_edge_time_us_ = current_time_us;

        if (dt < kBitHalfMinUs) {
            return;
        }

        switch (bmc_state_) {
            case BmcState::WaitSync:
                if (dt >= kBitHalfMinUs && dt <= kBitHalfMaxUs) {
                    bmc_state_ = BmcState::FirstHalf;
                } else if (dt >= kBitFullMinUs && dt <= kBitFullMaxUs) {
                    push_bit(0);
                }
                break;

            case BmcState::FirstHalf:
                if (dt >= kBitHalfMinUs && dt <= kBitHalfMaxUs) {
                    push_bit(1);
                    bmc_state_ = BmcState::WaitSync;
                } else {
                    bmc_state_ = BmcState::WaitSync;
                    preamble_count_ = 0;
                }
                break;
        }
    }

private:
    enum class BmcState { WaitSync, FirstHalf };
    enum class ParserState { Preamble, Header, Payload, Checksum };

    void push_bit(uint8_t bit) {
        if (parser_state_ == ParserState::Preamble) {
            if (bit == 1) {
                preamble_count_++;
            } else {
                if (preamble_count_ >= kPreambleMinBits) {
                    bit_index_ = 0;
                    rx_byte_ = 0;
                    parser_state_ = ParserState::Header;
                }
                preamble_count_ = 0;
            }
            return;
        }

        rx_byte_ = static_cast<uint8_t>((rx_byte_ << 1) | (bit & 0x01));
        bit_index_++;

        if (bit_index_ >= 8) {
            push_byte(rx_byte_);
            bit_index_ = 0;
            rx_byte_ = 0;
        }
    }

    void push_byte(uint8_t byte) {
        switch (parser_state_) {
            case ParserState::Preamble:
                break;

            case ParserState::Header:
                current_pkt_.header = static_cast<Header>(byte);
                current_pkt_.payload_len = get_payload_len(byte);
                calc_checksum_ = byte;
                payload_idx_ = 0;
                parser_state_ = (current_pkt_.payload_len > 0) ? ParserState::Payload : ParserState::Checksum;
                break;

            case ParserState::Payload:
                current_pkt_.payload[payload_idx_++] = byte;
                calc_checksum_ ^= byte;
                if (payload_idx_ >= current_pkt_.payload_len) {
                    parser_state_ = ParserState::Checksum;
                }
                break;

            case ParserState::Checksum:
                current_pkt_.checksum = byte;
                current_pkt_.valid = (calc_checksum_ == byte);
                if (current_pkt_.valid && callback_) {
                    callback_(current_pkt_);
                }
                parser_state_ = ParserState::Preamble;
                preamble_count_ = 0;
                break;
        }
    }

    static uint8_t get_payload_len(uint8_t hdr_raw) {
        switch (static_cast<Header>(hdr_raw)) {
            case Header::SignalStrength: return 1;
            case Header::EndTransfer:    return 1;
            case Header::ControlError:   return 1;
            case Header::ReceivedPower:  return 1;
            case Header::Configuration:  return 5;
            case Header::Identification: return 7;
            default: return static_cast<uint8_t>((hdr_raw >> 5) + 1);
        }
    }

    BmcState bmc_state_{BmcState::WaitSync};
    uint32_t last_edge_time_us_{0};
    uint8_t  preamble_count_{0};

    uint8_t  rx_byte_{0};
    uint8_t  bit_index_{0};

    ParserState parser_state_{ParserState::Preamble};
    Packet      current_pkt_{};
    uint8_t     payload_idx_{0};
    uint8_t     calc_checksum_{0};
    PacketCallback callback_;
};

class PowerController {
public:
    static constexpr float kFreqMinKhz = 110.0f;
    static constexpr float kFreqMaxKhz = 205.0f;
    static constexpr float kKp         = 0.25f;
    static constexpr float kKi         = 0.05f;

    explicit PowerController(float start_freq_khz = 145.0f)
        : current_freq_khz_(start_freq_khz) {}

    void process_cep(int8_t cep_value) {
        const float error = static_cast<float>(cep_value);
        integral_err_ += error;
        integral_err_ = std::clamp(integral_err_, -50.0f, 50.0f);

        const float delta_f = -(kKp * error + kKi * integral_err_);
        current_freq_khz_ = std::clamp(current_freq_khz_ + delta_f, kFreqMinKhz, kFreqMaxKhz);
    }

    [[nodiscard]] float frequency_khz() const noexcept {
        return current_freq_khz_;
    }

private:
    float current_freq_khz_{145.0f};
    float integral_err_{0.0f};
};

} // namespace qi
```
:::

## Типові підводні камені при розробці

1. **Комутаційні шуми синхронного випрямляча**: у моменти перемикання MOSFET випрямляча RX у котушці виникають високочастотні дзвони. Без низькочастотної RC-фільтрації (зріз на `~8–10 кГц`) аналоговий компаратор генеруватиме фальшиві переривання, які зриватимуть роботу BMC-декодера.
2. **Фазовий стрибок при зміні частоти інвертора**: коли регулятор TX різко змінює частоту ШІМ для стабілізації напруги, на котушці виникає перехідний процес амплітуди, який демодулятор може сприйняти за біт преамбули. Регулювання частоти слід виконувати плавно між пакетами даних, а не всередині них.
3. **Втрата зв'язку через вихід за поріг компаратора**: при сильному зміщенні котушок коефіцієнт `k` падає, а разом із ним зменшується амплітуда модуляції зворотного розсіяння (з `500 мВ` до менш ніж `20 мВ`). У професійних TX-контролерах поріг компаратора роблять адаптивним (на базі ЦАП), підлаштовуючи його під поточну амплітуду несучої.
4. **Зависання на помилках контрольної суми при переході навантаження**: під час різкого стрибка струму навантаження (наприклад, старт процесора телефону) амплітуда коливань на котушці зазнає стрибка, який спотворює поточний біт пакета. Прошивка повинна скидати парсер у стан `QI_STATE_PREAMBLE` без блокування черги обробки наступних пакетів.

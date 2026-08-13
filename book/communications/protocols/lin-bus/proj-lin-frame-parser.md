# ⚙️ Реалізація парсера кадру LIN та обчислення контрольної суми

Ця практична вставка детально розбирає апаратні та програмні прийоми обробки шини LIN у мікроконтролерах, проектування скінченних автоматів (Finite State Machine, FSM) для прийому кадрів через UART, а також надає повністю готові, ідіоматичні реалізації парсера та алгоритмів контролю цілісності мовами C та C++.

---

## Апаратні особливості прийому кадру LIN через UART

У більшості автомобільних електронних блоків керування (ECU) передача та прийом кадрів LIN здійснюється за допомогою стандартних периферійних модулів UART / USART або спеціалізованих LIN-контролерів. Головна складність обробки сигналу LIN полягає у правильному розпізнаванні сигналу Break (сигналу перерви), який є тривалим домінантним імпульсом `LOW`.

### Механізми виявлення сигналу Break

Оскільки сигнал Break є тривалим домінантним імпульсом `LOW` тривалістю від 13 до 26 бітових інтервалів, звичайне апаратне забезпечення UART сприймає його як помилковий стан кадрування, оскільки на місці очікуваного рецесивного стопового біта знаходиться домінантний рівень `0`. У мікроконтролерах застосовують два основні підходи до обробки Break:

1. **Використання апаратного прапорця Framing Error (FE):**
   UART-периферія налаштовується на стандартну швидкість шини (наприклад, 19.2 кбіт/с). Коли Master генерує Break, приймач UART фіксує відсутність стопового біта після 8-го біта `LOW` і виставляє прапорець помилки `Framing Error`. Програма обробки переривання UART аналізує цей прапорець і переводить скінченний автомат у стан очікування байта синхронізації `0x55`.

2. **Апаратний детектор LIN Break (STM32, NXP S32K, Microchip AVR):**
   Сучасні автомобільні мікроконтролери містять спеціалізований режим LIN у периферії USART. Приймач автоматично підраховує кількість послідовних бітів `LOW`. Якщо тривалість імпульсу перевищує 10 або 11 бітових інтервалів, модуль виставляє окремий переривальний прапорець `LIN Break Detected` (`LBD`), повністю звільняючи процесор від ручного аналізу помилок кадрування.

---

## Архітектура скінченного автомата (FSM)

Обробка потоку байтів, що надходять з шини LIN, здійснюється послідовно у міру виклику функції обробки байта. Парсер реалізує скінченний автомат із п'ятьма чітко розмежованими станами.

```
                  [Сигнал Break / FE]
                           │
                           ▼
                  ┌─────────────────┐
                  │ LIN_WAIT_BREAK  │
                  └────────┬────────┘
                           │ Break виявлено
                           ▼
                  ┌─────────────────┐
                  │  LIN_WAIT_SYNC  │ ── (Байт != 0x55) ──┐
                  └────────┬────────┘                     │
                           │ Байт == 0x55                 │
                           ▼                              │
                  ┌─────────────────┐                     │
                  │  LIN_WAIT_PID   │ ── (PID спотворено)─┤
                  └────────┬────────┘                     │
                           │ PID валідний                 │
                           ▼                              │
                  ┌─────────────────┐                     │
                  │  LIN_WAIT_DATA  │                     │
                  └────────┬────────┘                     │
                           │ Прийнято N байтів            │
                           ▼                              │
                  ┌─────────────────┐                     │
                  │LIN_WAIT_CHECKSUM│                     │
                  └────────┬────────┘                     │
                           │                              │
                           ├─ (Сума валідна)  ──> [Кадр готовий]
                           │                              │
                           └─ (Помилка суми) ─────────────┴──> [Reset у WAIT_BREAK]
```

### Деталізація переходів та обробка крайових випадків

1. **`LIN_WAIT_BREAK`:** Початковий стан простою. Усі звичайні байти даних ігноруються, поки периферійний модуль не зафіксує апаратний сигнал Break (або Framing Error). Це гарантує, що при підключенні вузла до шини посередині передачі парсер не почне приймати байти даних як заголовок.
2. **`LIN_WAIT_SYNC`:** Парсер перевіряє прийнятий байт на точне значення `0x55`. Якщо значення збігається, автомат переходить до прийому PID. Якщо прийнято будь-яке інше значення, вважається, що сталася збійна синхронізація, і автомат негайно скидається в `LIN_WAIT_BREAK`.
3. **`LIN_WAIT_PID`:** Приймається байт Protected Identifier. Парсер верифікує біти паритету `P0` та `P1`. Якщо паритет коректний, визначається довжина корисного навантаження, і автомат переходить до накопичення даних. При помилці паритету кадр скасовується.
4. **`LIN_WAIT_DATA`:** Накопичення від 1 до 8 байтів корисного навантаження у внутрішній буфер. Приймач контролює кількість прийнятих байтів згідно з довжиною, прив'язаною до отриманого ідентифікатора.
5. **`LIN_WAIT_CHECKSUM`:** Отримання байта контрольної суми. Парсер обчислює інвертовану суму за відповідним алгоритмом (Classic для діагностичних кадрів `0x3C`/`0x3D`, Enhanced для звичайних сигнальних кадрів у режимі LIN 2.x) і порівнює її з байтом у шині. При збігу прапорець `valid` встановлюється в `true`, і кадр передається верхньому рівню додатка.

---

## Обробка міжбайтових тайм-аутів та захист від зациклень

Реальні автомобільні мережі піддаються впливу сплесків завад та тимчасових розривів лінії. Якщо під час прийому байтів даних лінія обривається, парсер не повинен залишатися у стані `LIN_WAIT_DATA` назавжди.

Для забезпечення стійкості застосовується апаратний або програмний таймер міжбайтового інтервалу (Inter-Byte Timeout):
- **Максимальний зазор між байтами (`T_Header_Max` / `T_Response_Max`):** Специфікація ISO 17987 обмежує максимальну паузу між сусідніми байтами значенням `1.4 × T_bit_nominal × 10`.
- **Дія при тайм-ауті:** Якщо після прийому чергового байта наступний байт не надходить протягом розрахованого тайм-ауту, системний таймер генерує переривання, яке примусово скидає автомат LIN у початковий стан `LIN_WAIT_BREAK`.

---

## Реалізація парсера мовами C та C++

Усі реалізації розроблені з урахуванням суворих вимог до автомобільного програмного забезпечення (MISRA C / AUTOSAR): вони не використовують динамічне виділення пам'яті (`malloc` / `new`), не генерують винятків та працюють за константний час `O(1)`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LIN_MAX_DATA_BYTES 8

typedef enum {
    LIN_CHECKSUM_CLASSIC,
    LIN_CHECKSUM_ENHANCED
} lin_checksum_type_t;

typedef enum {
    LIN_STATE_WAIT_BREAK,
    LIN_STATE_WAIT_SYNC,
    LIN_STATE_WAIT_PID,
    LIN_STATE_WAIT_DATA,
    LIN_STATE_WAIT_CHECKSUM
} lin_parser_state_t;

typedef struct {
    uint8_t id;
    uint8_t pid;
    uint8_t data[LIN_MAX_DATA_BYTES];
    uint8_t data_len;
    uint8_t checksum;
    bool valid;
} lin_frame_t;

typedef struct {
    lin_parser_state_t state;
    lin_frame_t current_frame;
    uint8_t data_index;
    lin_checksum_type_t checksum_type;
} lin_parser_t;

// Обчислення бітів паритету P0 та P1 для ID (0x00..0x3F)
static inline uint8_t lin_calc_pid(uint8_t id) {
    uint8_t id_clean = id & 0x3F;
    uint8_t p0 = ((id_clean >> 0) ^ (id_clean >> 1) ^ (id_clean >> 2) ^ (id_clean >> 4)) & 0x01;
    uint8_t p1 = ~((id_clean >> 1) ^ (id_clean >> 3) ^ (id_clean >> 4) ^ (id_clean >> 5)) & 0x01;
    return id_clean | (p0 << 6) | (p1 << 7);
}

// Перевірка коректності байта PID
static inline bool lin_verify_pid(uint8_t pid) {
    uint8_t id = pid & 0x3F;
    return lin_calc_pid(id) == pid;
}

// Обчислення контрольної суми LIN (Classic або Enhanced)
static uint8_t lin_calc_checksum(uint8_t pid, const uint8_t *data, uint8_t len, lin_checksum_type_t type) {
    uint16_t sum = 0;
    
    if (type == LIN_CHECKSUM_ENHANCED) {
        sum += pid;
    }
    
    for (uint8_t i = 0; i < len; ++i) {
        sum += data[i];
        if (sum > 0xFF) {
            sum = (sum & 0xFF) + 1;
        }
    }
    
    return (uint8_t)(~sum & 0xFF);
}

// Ініціалізація парсера
void lin_parser_init(lin_parser_t *parser, lin_checksum_type_t type) {
    if (!parser) return;
    parser->state = LIN_STATE_WAIT_BREAK;
    parser->checksum_type = type;
    parser->data_index = 0;
    parser->current_frame.valid = false;
}

// Повідомлення парсера про фіксацію сигналу Break
void lin_parser_on_break(lin_parser_t *parser) {
    if (!parser) return;
    parser->state = LIN_STATE_WAIT_SYNC;
    parser->data_index = 0;
    parser->current_frame.valid = false;
}

// Обробка одного байта, отриманого з UART
bool lin_parser_process_byte(lin_parser_t *parser, uint8_t byte, uint8_t expected_data_len) {
    if (!parser) return false;

    switch (parser->state) {
        case LIN_STATE_WAIT_BREAK:
            // Очікування Break триває; звичайні байти ігноруються
            break;

        case LIN_STATE_WAIT_SYNC:
            if (byte == 0x55) {
                parser->state = LIN_STATE_WAIT_PID;
            } else {
                parser->state = LIN_STATE_WAIT_BREAK;
            }
            break;

        case LIN_STATE_WAIT_PID:
            if (lin_verify_pid(byte)) {
                parser->current_frame.pid = byte;
                parser->current_frame.id = byte & 0x3F;
                parser->current_frame.data_len = (expected_data_len > LIN_MAX_DATA_BYTES) ? 
                                                  LIN_MAX_DATA_BYTES : expected_data_len;
                parser->data_index = 0;
                parser->state = LIN_STATE_WAIT_DATA;
            } else {
                parser->state = LIN_STATE_WAIT_BREAK;
            }
            break;

        case LIN_STATE_WAIT_DATA:
            parser->current_frame.data[parser->data_index++] = byte;
            if (parser->data_index >= parser->current_frame.data_len) {
                parser->state = LIN_STATE_WAIT_CHECKSUM;
            }
            break;

        case LIN_STATE_WAIT_CHECKSUM:
            parser->current_frame.checksum = byte;
            // Для діагностичних кадрів 0x3C та 0x3D завжди Classic Checksum
            lin_checksum_type_t active_type = parser->checksum_type;
            if (parser->current_frame.id == 0x3C || parser->current_frame.id == 0x3D) {
                active_type = LIN_CHECKSUM_CLASSIC;
            }

            uint8_t calculated = lin_calc_checksum(parser->current_frame.pid,
                                                   parser->current_frame.data,
                                                   parser->current_frame.data_len,
                                                   active_type);
            
            parser->current_frame.valid = (calculated == byte);
            parser->state = LIN_STATE_WAIT_BREAK;
            return parser->current_frame.valid;
    }

    return false;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

enum class LinChecksumType {
    Classic,
    Enhanced
};

enum class LinState {
    WaitBreak,
    WaitSync,
    WaitPid,
    WaitData,
    WaitChecksum
};

struct LinFrame {
    uint8_t id{0};
    uint8_t pid{0};
    std::array<uint8_t, 8> data{};
    uint8_t data_len{0};
    uint8_t checksum{0};
    bool valid{false};

    [[nodiscard]] constexpr std::span<const uint8_t> payload() const noexcept {
        return std::span<const uint8_t>{data.data(), data_len};
    }
};

class LinFrameParser {
public:
    explicit constexpr LinFrameParser(LinChecksumType default_checksum = LinChecksumType::Enhanced) noexcept
        : default_checksum_{default_checksum} {}

    static constexpr uint8_t calculate_pid(uint8_t id) noexcept {
        const uint8_t id_clean = id & 0x3F;
        const uint8_t p0 = ((id_clean >> 0) ^ (id_clean >> 1) ^ (id_clean >> 2) ^ (id_clean >> 4)) & 0x01;
        const uint8_t p1 = ~((id_clean >> 1) ^ (id_clean >> 3) ^ (id_clean >> 4) ^ (id_clean >> 5)) & 0x01;
        return id_clean | static_cast<uint8_t>(p0 << 6) | static_cast<uint8_t>(p1 << 7);
    }

    static constexpr bool verify_pid(uint8_t pid) noexcept {
        return calculate_pid(pid & 0x3F) == pid;
    }

    static constexpr uint8_t calculate_checksum(uint8_t pid, std::span<const uint8_t> data, LinChecksumType type) noexcept {
        uint16_t sum = 0;
        if (type == LinChecksumType::Enhanced) {
            sum += pid;
        }
        for (const uint8_t b : data) {
            sum += b;
            if (sum > 0xFF) {
                sum = (sum & 0xFF) + 1;
            }
        }
        return static_cast<uint8_t>(~sum & 0xFF);
    }

    constexpr void reset() noexcept {
        state_ = LinState::WaitBreak;
        data_index_ = 0;
        current_frame_ = LinFrame{};
    }

    constexpr void on_break_detected() noexcept {
        state_ = LinState::WaitSync;
        data_index_ = 0;
        current_frame_ = LinFrame{};
    }

    constexpr std::optional<LinFrame> process_byte(uint8_t byte, uint8_t expected_len) noexcept {
        switch (state_) {
            case LinState::WaitBreak:
                break;

            case LinState::WaitSync:
                if (byte == 0x55) {
                    state_ = LinState::WaitPid;
                } else {
                    reset();
                }
                break;

            case LinState::WaitPid:
                if (verify_pid(byte)) {
                    current_frame_.pid = byte;
                    current_frame_.id = byte & 0x3F;
                    current_frame_.data_len = (expected_len > 8) ? 8 : expected_len;
                    data_index_ = 0;
                    state_ = LinState::WaitData;
                } else {
                    reset();
                }
                break;

            case LinState::WaitData:
                current_frame_.data[data_index_++] = byte;
                if (data_index_ >= current_frame_.data_len) {
                    state_ = LinState::WaitChecksum;
                }
                break;

            case LinState::WaitChecksum: {
                current_frame_.checksum = byte;
                LinChecksumType active_type = default_checksum_;
                if (current_frame_.id == 0x3C || current_frame_.id == 0x3D) {
                    active_type = LinChecksumType::Classic;
                }

                const uint8_t calculated = calculate_checksum(
                    current_frame_.pid,
                    current_frame_.payload(),
                    active_type
                );

                current_frame_.valid = (calculated == byte);
                LinFrame result = current_frame_;
                reset();
                
                if (result.valid) {
                    return result;
                }
                break;
            }
        }
        return std::nullopt;
    }

private:
    LinChecksumType default_checksum_;
    LinState state_{LinState::WaitBreak};
    uint8_t data_index_{0};
    LinFrame current_frame_{};
};
```
:::

---

## Розбір особливостей та переваг реалізації C++

Версія C++ розроблена з використанням сучасних паттернів проектування високопродуктивного вбудованого коду:
- **`std::span<const uint8_t>`:** Забезпечує безпечний перегляд буфера корисного навантаження без виділення додаткової пам'яті та без передачі сирих вказівників із розмірами `(ptr, len)`.
- **`std::optional<LinFrame>`:** Надає чітку та виразну семантику виклику функції. Повернення значення `std::nullopt` однозначно інформує викликаючий код про те, що кадр ще перебуває в процесі формування або був скасований через помилку цілісності.
- **Оголошення `constexpr`:** Усі функції обчислення та перевірки PID і контрольних сум позначено як `constexpr`. Якщо ідентифікатор каду відомий під час компіляції (наприклад, константний PID опитування у розкладі Master), компілятор обчислює очікувані байти ще на етапі збирання проєкту, повністю звільняючи процесор від арифметичних обчислень у реальному часі.
- **Строга типізація `enum class`:** Виключає невизначену поведінку та випадкові неявні приведення типів між станами автомата, типами контрольних сум та звичайними цілими числами.

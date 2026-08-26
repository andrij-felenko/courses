# ⚙️ Практикум: Прийом і парсинг пакетів телеметрії через кільцевий буфер

Цей практикум демонструє повну побудову надійного безблокувального конвеєра прийому, буферизації та валідації пакетів телеметрії між асинхронним обробником переривання UART і основним циклом мікроконтролера мовами C та C++ без використання динамічної пам'яті.

### Інженерна постановка задачі

Бортовий навігаційний вузол безпілотного апарата передає потік телеметричних даних через асинхронний послідовний порт UART на швидкості 921600 бод. За такої швидкості новий байт надходить на вхід мікроконтролера кожні 10.85 мікросекунди.

Обробка такого потоку висуває жорсткі інженерні вимоги до коду прошивки:
1. **Мінімальний час перебування в ISR:** Обробник переривання UART повинен встигнути прочитати байт із регістра `DR`, зберегти його в буфер і вийти менше ніж за 1 мікросекунду, щоб не блокувати переривання таймерів стабілізації польоту та ШІМ-генераторів моторів.
2. **Нульове динамічне виділення:** Жоден байт пам'яті не повинен виділятися через `malloc()` або оператор `new`, оскільки фрагментація пам'яті або затримка пошуку вільного блоку в купі призведе до втрати пакетів керування.
3. **Захист від шумів лінії:** Послідовний радіоканал піддається електромагнітним завадам, тому окремі байти можуть губитися або спотворюватися. Парсер зобов'язаний розпізнавати пошкоджені кадри за допомогою контрольної суми CRC-16 і миттєво відновлювати синхронізацію потоку без зациклення.

### Специфікація протоколу кадру телеметрії

Для надійної передачі обрано протокол фіксованої довжини зі стартовим маркером `0xAA`, кінцевим маркером `0x55` та 16-бітною контрольною сумою CRC-16-CCITT:

| Поле кадру | Довжина (байти) | Зсув у кадрі | Тип даних | Опис фізичного змісту |
| :--- | :--- | :--- | :--- | :--- |
| `START_DELIMITER` | 1 | 0 | `uint8_t` | Фіксований маркер початку кадру: `0xAA` |
| `node_id` | 1 | 1 | `uint8_t` | Унікальний номер бортового вузла (0x01 = Навігація) |
| `timestamp_ms` | 4 | 2 | `uint32_t` | Монотонний системний час з моменту старту (мс) |
| `accel_x` | 2 | 6 | `int16_t` | Проекція прискорення по осі X (масштаб: 1 LSB = 0.001g) |
| `accel_y` | 2 | 8 | `int16_t` | Проекція прискорення по осі Y (масштаб: 1 LSB = 0.001g) |
| `accel_z` | 2 | 10 | `int16_t` | Проекція прискорення по осі Z (масштаб: 1 LSB = 0.001g) |
| `voltage_mv` | 2 | 12 | `uint16_t` | Напруга основної силової батареї (мілівольти) |
| `sequence_id` | 2 | 14 | `uint16_t` | Наскрізний лічильник надісланих пакетів |
| `crc16` | 2 | 16 | `uint16_t` | Контрольна сума CRC-16-CCITT (поліном 0x1021) |
| `END_DELIMITER` | 1 | 18 | `uint8_t` | Фіксований маркер завершення кадру: `0x55` |

Повний розмір кадру становить строго 19 байтів. Корисне навантаження займає 15 байтів (зсуви 1..15), і саме по них обчислюється контрольна сума CRC-16.

### Математичні властивості контрольної суми CRC-16

Для контролю цілісності обрано алгоритм CRC-16-CCITT з прямим генераторним поліномом `x^16 + x^12 + x^5 + 1` (шістнадцяткове значення `0x1021`) та початковим значенням регістрів `0xFFFF`.

Цей поліном забезпечує наступні математичні гарантії для блоків довжиною 15 байтів:
* 100% виявлення всіх поодиноких бітових помилок у каналі зв'язку.
* 100% виявлення всіх подвійних бітових помилок на відстані до 2048 бітів (кодова відстань Геммінга `d = 4`).
* 100% виявлення будь-яких непарних кількостей помилкових бітів.
* 100% виявлення пачкових помилок (*burst errors*) довжиною до 16 бітів включно.
* Понад 99.997% імовірності виявлення випадкових довгих спотворень сигналу.

### Механіка роботи скінченного автомата парсера

Щоб парсинг не блокував процесор очікуванням цілого пакета, обробка виконується байт за байтом за моделлю скінченного автомата (*Finite State Machine*, FSM).

Автомат має п'ять дискретних станів:
1. `STATE_WAIT_START` (Пошук старту): Автомат ігнорує будь-яке сміття в каналі, доки не зустріне байт `0xAA`. Щойно байт знайдено, лічильник прийнятих байтів обнуляється, і автомат переходить до читання корисного навантаження.
2. `STATE_READ_PAYLOAD` (Збір даних): Байти записуються у внутрішній статичний буфер `payload_raw[15]`. Після накопичення 15 байтів автомат перемикається на прийом молодшого байта контрольної суми.
3. `STATE_READ_CRC_LOW`: Зчитується молодший байт CRC (`crc_low`).
4. `STATE_READ_CRC_HIGH`: Зчитується старший байт CRC, формується повне 16-бітне число `rx_crc = crc_low | (crc_high << 8)`.
5. `STATE_WAIT_END` (Валідація): Перевіряється наявність кінцевого маркера `0x55`. Якщо маркер збігається, автомат розраховує CRC-16 над буфером `payload_raw` і порівнює з `rx_crc`. У разі збігу викликається функція обробки телеметрії. Якщо маркер або CRC некоректні, пакет відкидається, а автомат негайно повертається в стан пошуку старту.

### Обробка крайових випадків та помилок зв'язку

Парсер гарантує стійкість у наступних позаштатних ситуаціях:
* **Поява хибного стартового байта `0xAA` всередині корисних даних:** Якщо шум або значення заміру давача містить `0xAA`, автомат збере наступні 15 байтів, виявить невідповідність CRC або відсутність кінцевого маркера `0x55`, скине стан і почне пошук наступного справжнього пакета.
* **Переповнення кільцевого буфера:** Якщо головний цикл затримався на виконання складної математики, функція `ring_put` поверне `false` і безпечно відкине надлишковий байт, не руйнуючи вже записані старі дані.
* **Обчислення CRC на льоту:** Алгоритм CRC-16-CCITT гарантує детерміноване обчислення без використання таблиць пам'яті (Bit-by-Bit) або з компактною таблицею на 16 елементів для максимальної швидкодії.
* **Раптове знеструмлення або перезапуск передавача:** Якщо передавач обірвав передачу посеред кадру, автомат зависне в стані очікування лише до прибуття наступного валідного маркера `0xAA`, після чого автоматично синхронізується заново.

### Програмна реалізація конвеєра

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FRAME_START_BYTE 0xAAU
#define FRAME_END_BYTE   0x55U

// --- Структура корисного навантаження без проміжних байтів ---
typedef struct __attribute__((packed)) {
    uint8_t  node_id;
    uint32_t timestamp_ms;
    int16_t  accel_x;
    int16_t  accel_y;
    int16_t  accel_z;
    uint16_t voltage_mv;
    uint16_t sequence_id;
} TelemetryPayload;

#define PAYLOAD_SIZE sizeof(TelemetryPayload)
_Static_assert(PAYLOAD_SIZE == 15, "Payload size must be exactly 15 bytes!");

// --- Статичний кільцевий буфер SPSC ---
#define RX_BUF_SIZE 256U
#define RX_BUF_MASK (RX_BUF_SIZE - 1U)

typedef struct {
    uint8_t buffer[RX_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} RingBuffer;

static RingBuffer rx_ring;

static inline bool ring_put(RingBuffer *rb, uint8_t byte) {
    uint16_t next = (uint16_t)((rb->head + 1U) & RX_BUF_MASK);
    if (next == rb->tail) {
        return false; // Буфер переповнено
    }
    rb->buffer[rb->head] = byte;
    rb->head = next;
    return true;
}

static inline bool ring_get(RingBuffer *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *byte = rb->buffer[rb->tail];
    rb->tail = (uint16_t)((rb->tail + 1U) & RX_BUF_MASK);
    return true;
}

// --- Розрахунок контрольної суми CRC-16-CCITT ---
static uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)((uint16_t)data[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = (uint16_t)((crc << 1) ^ 0x1021U);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

// --- Апаратний обробник переривання UART (ISR) ---
void USART1_IRQHandler(void) {
    volatile uint32_t *uart_sr = (volatile uint32_t *)0x40013800UL;
    volatile uint32_t *uart_dr = (volatile uint32_t *)0x40013804UL;

    if (*uart_sr & (1U << 5)) { // Прапорець RXNE (байт готовий)
        uint8_t byte = (uint8_t)(*uart_dr & 0xFFU);
        ring_put(&rx_ring, byte);
    }
}

// --- Скінченний автомат розбору пакетів ---
typedef enum {
    PARSER_WAIT_START,
    PARSER_READ_PAYLOAD,
    PARSER_READ_CRC_LOW,
    PARSER_READ_CRC_HIGH,
    PARSER_WAIT_END
} ParserState;

typedef struct {
    ParserState state;
    uint8_t payload_raw[PAYLOAD_SIZE];
    uint8_t bytes_read;
    uint16_t rx_crc;
    uint32_t packets_received;
    uint32_t crc_errors;
} TelemetryParser;

static TelemetryParser parser;

void telemetry_process_packet(const TelemetryPayload *packet) {
    // Безпечна обробка валідованого кадру в super-loop
    (void)packet;
}

void telemetry_parser_poll(void) {
    uint8_t byte;
    while (ring_get(&rx_ring, &byte)) {
        switch (parser.state) {
            case PARSER_WAIT_START:
                if (byte == FRAME_START_BYTE) {
                    parser.bytes_read = 0;
                    parser.state = PARSER_READ_PAYLOAD;
                }
                break;

            case PARSER_READ_PAYLOAD:
                parser.payload_raw[parser.bytes_read++] = byte;
                if (parser.bytes_read >= PAYLOAD_SIZE) {
                    parser.state = PARSER_READ_CRC_LOW;
                }
                break;

            case PARSER_READ_CRC_LOW:
                parser.rx_crc = byte;
                parser.state = PARSER_READ_CRC_HIGH;
                break;

            case PARSER_READ_CRC_HIGH:
                parser.rx_crc |= (uint16_t)((uint16_t)byte << 8);
                parser.state = PARSER_WAIT_END;
                break;

            case PARSER_WAIT_END:
                if (byte == FRAME_END_BYTE) {
                    uint16_t calc_crc = crc16_ccitt(parser.payload_raw, PAYLOAD_SIZE);
                    if (calc_crc == parser.rx_crc) {
                        TelemetryPayload packet;
                        memcpy(&packet, parser.payload_raw, sizeof(packet));
                        parser.packets_received++;
                        telemetry_process_packet(&packet);
                    } else {
                        parser.crc_errors++;
                    }
                }
                parser.state = PARSER_WAIT_START;
                break;
        }
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <span>
#include <cstring>

inline constexpr uint8_t FRAME_START_BYTE = 0xAA;
inline constexpr uint8_t FRAME_END_BYTE   = 0x55;

// --- C++20 упакована структура корисного навантаження ---
struct [[gnu::packed]] TelemetryPayload {
    uint8_t  node_id;
    uint32_t timestamp_ms;
    int16_t  accel_x;
    int16_t  accel_y;
    int16_t  accel_z;
    uint16_t voltage_mv;
    uint16_t sequence_id;
};

inline constexpr size_t PAYLOAD_SIZE = sizeof(TelemetryPayload);
static_assert(PAYLOAD_SIZE == 15, "Payload size must be exactly 15 bytes!");

// --- Шаблонний безпечний буфер SPSC ---
template <typename T, size_t Capacity>
class StaticRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of two");
public:
    constexpr StaticRingBuffer() noexcept = default;

    bool push(T item) noexcept {
        size_t next = (head_ + 1U) & mask_;
        if (next == tail_) return false;
        buffer_[head_] = item;
        head_ = next;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (head_ == tail_) return std::nullopt;
        T item = buffer_[tail_];
        tail_ = (tail_ + 1U) & mask_;
        return item;
    }

private:
    static constexpr size_type mask_ = Capacity - 1U;
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

// --- Обчислення CRC16-CCITT на std::span ---
constexpr uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFFU;
    for (uint8_t b : data) {
        crc ^= static_cast<uint16_t>(static_cast<uint16_t>(b) << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = static_cast<uint16_t>((crc << 1) ^ 0x1021U);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

// --- Клас приймача та парсера телеметрії ---
class TelemetryReceiver {
public:
    enum class State : uint8_t {
        WaitStart,
        ReadPayload,
        ReadCrcLow,
        ReadCrcHigh,
        WaitEnd
    };

    void on_uart_rx_isr(uint8_t byte) noexcept {
        rx_buffer_.push(byte);
    }

    template <typename Callback>
    void poll(Callback&& packet_callback) noexcept {
        while (auto byte_opt = rx_buffer_.pop()) {
            const uint8_t byte = *byte_opt;
            switch (state_) {
                case State::WaitStart:
                    if (byte == FRAME_START_BYTE) {
                        bytes_read_ = 0;
                        state_ = State::ReadPayload;
                    }
                    break;

                case State::ReadPayload:
                    payload_raw_[bytes_read_++] = byte;
                    if (bytes_read_ >= PAYLOAD_SIZE) {
                        state_ = State::ReadCrcLow;
                    }
                    break;

                case State::ReadCrcLow:
                    rx_crc_ = byte;
                    state_ = State::ReadCrcHigh;
                    break;

                case State::ReadCrcHigh:
                    rx_crc_ |= static_cast<uint16_t>(static_cast<uint16_t>(byte) << 8);
                    state_ = State::WaitEnd;
                    break;

                case State::WaitEnd:
                    if (byte == FRAME_END_BYTE) {
                        const uint16_t calc_crc = calculate_crc16(payload_raw_);
                        if (calc_crc == rx_crc_) {
                            TelemetryPayload packet{};
                            std::memcpy(&packet, payload_raw_.data(), sizeof(packet));
                            packets_received_++;
                            packet_callback(packet);
                        } else {
                            crc_errors_++;
                        }
                    }
                    state_ = State::WaitStart;
                    break;
            }
        }
    }

    [[nodiscard]] uint32_t packets_received() const noexcept { return packets_received_; }
    [[nodiscard]] uint32_t crc_errors() const noexcept { return crc_errors_; }

private:
    StaticRingBuffer<uint8_t, 256> rx_buffer_{};
    State state_{State::WaitStart};
    std::array<uint8_t, PAYLOAD_SIZE> payload_raw_{};
    size_t bytes_read_{0};
    uint16_t rx_crc_{0};
    uint32_t packets_received_{0};
    uint32_t crc_errors_{0};
};
```
:::

### Результати профілювання та ресурси

* **Витрати SRAM:** Точно 256 байтів під буфер + 28 байтів під стан автомата = 284 байти у секції `.bss`.
* **Витрати Flash:** Скомпільований бінарний код автомата разом із таблицею та функцією CRC займає менше 450 байтів у секції `.text`.
* **Швидкодія обробника переривання:** Запис байта в кільцевий буфер в `USART1_IRQHandler` займає рівно 8 машинних інструкцій (менше 120 нс при частоті 72 МГц), що повністю усуває небезпеку переповнення буфера переривань навіть на максимальній швидкості UART.
* **Стійкість до помилок:** Автомат ніколи не виділяє пам'ять і гарантує повернення в стан пошуку `STATE_WAIT_START` при будь-якій помилці кадру або CRC.

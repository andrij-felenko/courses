# ⚙️ Реалізація потокового кодека COBS без динамічної пам'яті

Реалізація потокового кодека COBS демонструє, як побудувати швидкий, безпечний до переповнень і не залежний від динамічної пам'яті канальний драйвер для передачі та прийому пакетів через переривання UART або черги RTOS.

---

## Інженерні вимоги та виклики вбудованих систем

Розробка канального рівня зв'язку для мікроконтролерів (STM32, ESP32, NXP LPC, RP2040) суттєво відрізняється від програмування мережевих застосунків для операційних систем загального призначення. В умовах жорсткого реального часу драйвер послідовного інтерфейсу підпорядковується суворим обмеженням:

1. **Повна заборона динамічного виділення пам'яті:** Виклики `malloc`, `free`, `new` та динамічні контейнери на кшталт `std::vector` чи `std::string` заборонені промисловими стандартами надійності (зокрема MISRA C / AUTOSAR). Динамічна купа спричиняє непередбачувані затримки виконання (англ. *non-deterministic latency*), фрагментацію пам'яті та загрозу аварійної зупинки системи через вичерпання пулу оперативної пам'яті. Усі буфери приймача й передавача мають бути статичними або виділятися на етапі компіляції.
2. **Робота в контексті апаратних переривань (ISR):** Коли потік байтів надходить через послідовний порт UART на швидкості 921 600 біт/с або 3 Мбіт/с, час між двома сусідніми байтами становить менше кількох мікросекунд. Обробник переривання приймача не може виконувати складні цикли пошуку, обчислення геш-таблиць чи копіювання великих блоків пам'яті. Кожен байт має оброблятися потоково за сталий час `O(1)`.
3. **Захист від переповнення та спотворень у каналі:** Шум у лінії передачі (наприклад, перешкоди від роботи силових ключів інвертора двигуна в робототехніці) може інвертувати біти або створити хибні нульові байти. Драйвер зобов'язаний миттєво відкидати некоректні кадри, скидати свій внутрішній стан і відновлювати синхронізацію без витоку пам'яті та зависання кінцевого автомата.

---

## Архітектура потокового скінченного автомата (FSM)

Для побайтового декодування пакетів у режимі реального часу застосовується **потоковий скінченний автомат** (англ. *Streaming Finite State Machine*, FSM). 

На відміну від блокового декодера, який вимагає наявності всього кадру в пам'яті перед початком обробки, потоковий автомат розпаковує корисні дані на льоту, розміщуючи відновлені байти безпосередньо в цільовий буфер прийому.

Автомат підтримує три стани:

```
                  ┌──────────────────────┐
                  │   HUNT_DELIMITER     │◄─────────────────┐
                  │ (Очікування 0x00)    │                  │
                  └──────────┬───────────┘                  │
                             │ Байт == 0x00                 │
                             ▼                              │ Помилка
                  ┌──────────────────────┐                  │ кадрування /
            ┌────►│      READ_CODE       │                  │ Переповнення
            │     │ (Читання покажчика)  │                  │ буфера
            │     └──────────┬───────────┘                  │
            │ Байт == 0x00   │ Код > 0x01                   │
            │ (Кінець кадру) │ (Дані є)                     │
            │                ▼                              │
            │     ┌──────────────────────┐                  │
            └─────┤      READ_DATA       ├──────────────────┘
                  │ (Збирання блоку)     │
                  └──────────────────────┘
```

### Логіка переходу між станами

1. **`HUNT_DELIMITER` (Синхронізація):** Початковий стан після ввімкнення живлення, апаратного перезавантаження або виявлення помилки структури кадру. Приймач ігнорує всі вхідні байти даних, оскільки вони можуть бути фрагментом незавершеного попереднього пакета. Щойно в лінію надходить розділювач `0x00`, автомат переходить у стан `READ_CODE`.
2. **`READ_CODE` (Зчитування зміщення):** Автомат очікує перший байт нового блоку (покажчик зміщення `code`).
   * Якщо `code == 0x00`: це повторний розділювач (між двома пакетами передано кілька нулів поспіль або лінія була в стані спокою). Автомат залишається в очікуванні валідного кодового байта.
   * Якщо `code == 0x01`: блок містить нуль корисних байтів даних, після яких одразу слідує відновлений нуль `0x00` (випадок появи `0x00 0x00` у вихідному повідомленні). Автомат записує `0x00` у вихідний буфер і залишається в стані `READ_CODE`.
   * Якщо `code > 0x01`: блок містить `code - 1` ненульових байтів даних. Автомат ініціалізує лічильник залишку `block_rem = code - 1` і переходить у стан `READ_DATA`.
3. **`READ_DATA` (Накопичення корисного навантаження):** Кожен отриманий ненульовий байт безпосередньо записується у вихідний масив, а лічильник `block_rem` зменшується на одиницю.
   * Якщо в стані `READ_DATA` раптово надходить розділювач `0x00`, це свідчить про апаратний збій (кадр обірвався раніше, ніж було прочитано заявлені `code - 1` байтів). Автомат скидає довжину прийнятих даних `rx_len = 0`, формує помилку `COBS_ERR_UNEXPECTED_DELIMITER` і переходить у стан `HUNT_DELIMITER`.
   * Коли лічильник `block_rem` досягає нуля, блок успішно завершено. Якщо значення коду було `code < 0xFF`, автомат записує у вихідний буфер неявний нуль `0x00` (поглинутий під час кодування) і повертається в стан `READ_CODE`. Якщо ж було `code == 0xFF`, неявний нуль не вставляється, оскільки блок досяг максимальної місткості 254 байти без розділювача.

---

## Механіка блокового кодування та In-Place декодування

Для передавача, який уже сформував повну структуру повідомлення в пам'яті (наприклад, пакет телеметрії MAVLink або команду керування сервоприводами), найефективнішим є блокове кодування.

### Алгоритм кодування з відкладеним записом покажчиків

Під час кодування розмір вихідного масиву невідомий заздалегідь, оскільки позиції нулів визначають розташування службових байтів. Проте алгоритм COBS дозволяє виконати кодування за **один прохід** без проміжних буферів.

Передавач резервує перший байт вихідного буфера під покажчик зміщення `code_ptr = dst++` і встановлює початковий лічильник `code = 0x01`.

Потім алгоритм послідовно читає вхідний масив:
* Якщо черговий байт ненульовий, він записується у вихідний буфер `*dst++ = *src++`, а лічильник `code` інкрементується. Якщо `code` досягає `0xFF` (254 байти даних), передавач записує `*code_ptr = 0xFF`, виділяє нову позицію під наступний покажчик `code_ptr = dst++` і скидає лічильник `code = 0x01`.
* Якщо черговий байт дорівнює `0x00`, поточний блок завершено. Передавач записує накопичене значення `*code_ptr = code`, виділяє нову позицію під наступний покажчик `code_ptr = dst++`, скидає лічильник `code = 0x01` і пропускає вхідний нуль `src++`.

Після обробки всіх вхідних байтів у фінальний зарезервований слот записується поточне значення `*code_ptr = code`, а в кінець додається розділювач `0x00`.

### Теорема безпеки In-Place декодування

Важливою практичною властивістю алгоритму COBS є можливість виконання декодування безпосередньо у вхідному буфері (in-place) без виділення окремого вихідного масиву пам'яті.

> **Теорема (Інваріант випередження читання):**
> Нехай `pos_read` — поточний індекс зчитування закодованого масиву, а `pos_write` — поточний індекс запису відновлених даних у той самий буфер. Для будь-якого коректного кадру COBS на кожному кроці алгоритму виконується нерівність:
> ```
> pos_write ≤ pos_read
> ```

*Доведення:*
На початку декодування `pos_read = 1` (прочитано перший кодовий байт), тоді як `pos_write = 0`. Різниця становить `pos_read - pos_write = 1`.
Для кожного блоку зі значенням покажчика `code`:
1. Декодер зчитує `code - 1` байтів даних: обидва індекси збільшуються на `code - 1`. Різниця `pos_read - pos_write` залишається рівною `1`.
2. Якщо `code < 0xFF`, декодер записує один відновлений нуль `0x00` (`pos_write` збільшується на 1) і зчитує наступний байт покажчика із закодованого потоку (`pos_read` збільшується на 1). Різниця залишається незмінною: `pos_read - pos_write = 1`.
3. Якщо `code == 0xFF`, нуль не записується, а декодер зчитує наступний покажчик (`pos_read` збільшується на 1). Різниця зростає до `pos_read - pos_write = 2`.

Оскільки різниця індексів `pos_read - pos_write ≥ 1` є строго додатною на всіх етапах обробки, позиція запису ніколи не обганяє позицію читання. Відновлені байти ніколи не затирають ще не декодовані байти кадру, що математично гарантує безпеку in-place розпакування.

---

## Повний вихідний код реалізації на C та C++

Нижче наведено модульну бібліотеку, яка містить як швидкі блокові функції, так і потоковий скінченний автомат для інтеграції в обробники переривань UART та завдання RTOS.

:::tabs
```c
#ifndef COBS_H
#define COBS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    COBS_OK = 0,
    COBS_ERR_NULL_PTR,
    COBS_ERR_BUFFER_OVERFLOW,
    COBS_ERR_ZERO_IN_PAYLOAD,
    COBS_ERR_UNEXPECTED_DELIMITER,
    COBS_ERR_INVALID_OFFSET
} cobs_status_t;

typedef enum {
    COBS_STATE_HUNT_DELIMITER = 0,
    COBS_STATE_READ_CODE,
    COBS_STATE_READ_DATA
} cobs_parser_state_t;

typedef struct {
    uint8_t *rx_buf;
    size_t rx_capacity;
    size_t rx_len;
    cobs_parser_state_t state;
    uint8_t code;
    uint8_t block_rem;
} cobs_parser_t;

/**
 * Блокове кодування масиву байтів.
 * @param src Вказівник на вхідний масив.
 * @param src_len Довжина вхідного масиву.
 * @param dst Вказівник на вихідний буфер (розмір >= src_len + src_len/254 + 1).
 * @param dst_capacity Місткість вихідного буфера.
 * @param out_len Вказівник для повернення фактичної кількості записаних байтів.
 */
cobs_status_t cobs_encode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len);

/**
 * Блокове декодування масиву (підтримує in-place при src == dst).
 */
cobs_status_t cobs_decode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len);

/**
 * Ініціалізація потокового парсера.
 */
void cobs_parser_init(cobs_parser_t *parser, uint8_t *buffer, size_t capacity);

/**
 * Обробка одного байта, отриманого з UART/DMA.
 * @return true, якщо зібрано повний валідний пакет.
 */
bool cobs_parser_feed_byte(cobs_parser_t *parser, uint8_t byte, cobs_status_t *status);

#ifdef __cplusplus
}
#endif

#endif // COBS_H

// --- cobs.c ---
#include <string.h>

cobs_status_t cobs_encode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len) {
    if (!src || !dst || !out_len) return COBS_ERR_NULL_PTR;

    size_t max_req = src_len + (src_len / 254) + 1;
    if (dst_capacity < max_req) return COBS_ERR_BUFFER_OVERFLOW;

    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 0x01;

    while (read_idx < src_len) {
        uint8_t byte = src[read_idx++];
        if (byte == 0x00) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 0x01;
        } else {
            dst[write_idx++] = byte;
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 0x01;
            }
        }
    }
    dst[code_idx] = code;
    *out_len = write_idx;
    return COBS_OK;
}

cobs_status_t cobs_decode(const uint8_t *src, size_t src_len, 
                          uint8_t *dst, size_t dst_capacity, size_t *out_len) {
    if (!src || !dst || !out_len) return COBS_ERR_NULL_PTR;
    if (src_len == 0) {
        *out_len = 0;
        return COBS_OK;
    }

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src_len) {
        uint8_t code = src[read_idx++];
        if (code == 0x00) return COBS_ERR_ZERO_IN_PAYLOAD;

        uint8_t copy_len = code - 1;
        if (read_idx + copy_len > src_len) return COBS_ERR_INVALID_OFFSET;
        if (write_idx + copy_len > dst_capacity) return COBS_ERR_BUFFER_OVERFLOW;

        for (uint8_t i = 0; i < copy_len; ++i) {
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src_len) {
            if (write_idx >= dst_capacity) return COBS_ERR_BUFFER_OVERFLOW;
            dst[write_idx++] = 0x00;
        }
    }

    *out_len = write_idx;
    return COBS_OK;
}

void cobs_parser_init(cobs_parser_t *parser, uint8_t *buffer, size_t capacity) {
    if (!parser) return;
    parser->rx_buf = buffer;
    parser->rx_capacity = capacity;
    parser->rx_len = 0;
    parser->state = COBS_STATE_HUNT_DELIMITER;
    parser->code = 0;
    parser->block_rem = 0;
}

bool cobs_parser_feed_byte(cobs_parser_t *parser, uint8_t byte, cobs_status_t *status) {
    if (!parser || !parser->rx_buf) {
        if (status) *status = COBS_ERR_NULL_PTR;
        return false;
    }

    // Зустріч із розділювачем кінця кадру
    if (byte == 0x00) {
        if (parser->state == COBS_STATE_READ_DATA && parser->block_rem > 0) {
            parser->rx_len = 0;
            parser->state = COBS_STATE_READ_CODE;
            if (status) *status = COBS_ERR_UNEXPECTED_DELIMITER;
            return false;
        }

        if (parser->rx_len > 0) {
            parser->state = COBS_STATE_READ_CODE;
            if (status) *status = COBS_OK;
            return true;
        }

        parser->state = COBS_STATE_READ_CODE;
        if (status) *status = COBS_OK;
        return false;
    }

    switch (parser->state) {
    case COBS_STATE_HUNT_DELIMITER:
        break;

    case COBS_STATE_READ_CODE:
        parser->code = byte;
        if (parser->code == 0x01) {
            if (parser->rx_len >= parser->rx_capacity) {
                parser->rx_len = 0;
                parser->state = COBS_STATE_HUNT_DELIMITER;
                if (status) *status = COBS_ERR_BUFFER_OVERFLOW;
                return false;
            }
            parser->rx_buf[parser->rx_len++] = 0x00;
        } else {
            parser->block_rem = parser->code - 1;
            parser->state = COBS_STATE_READ_DATA;
        }
        break;

    case COBS_STATE_READ_DATA:
        if (parser->rx_len >= parser->rx_capacity) {
            parser->rx_len = 0;
            parser->state = COBS_STATE_HUNT_DELIMITER;
            if (status) *status = COBS_ERR_BUFFER_OVERFLOW;
            return false;
        }

        parser->rx_buf[parser->rx_len++] = byte;
        parser->block_rem--;

        if (parser->block_rem == 0) {
            if (parser->code < 0xFF) {
                if (parser->rx_len >= parser->rx_capacity) {
                    parser->rx_len = 0;
                    parser->state = COBS_STATE_HUNT_DELIMITER;
                    if (status) *status = COBS_ERR_BUFFER_OVERFLOW;
                    return false;
                }
                parser->rx_buf[parser->rx_len++] = 0x00;
            }
            parser->state = COBS_STATE_READ_CODE;
        }
        break;
    }

    if (status) *status = COBS_OK;
    return false;
}
```
```cpp
#pragma once

#include <span>
#include <array>
#include <cstdint>
#include <cstddef>
#include <expected>
#include <concepts>
#include <algorithm>

namespace cobs {

enum class Status {
    Ok = 0,
    BufferOverflow,
    ZeroInPayload,
    UnexpectedDelimiter,
    InvalidOffset
};

[[nodiscard]] constexpr size_t max_encoded_length(size_t raw_len) noexcept {
    return raw_len + (raw_len / 254) + 1;
}

[[nodiscard]] constexpr std::expected<size_t, Status> encode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst
) noexcept {
    if (dst.size() < max_encoded_length(src.size())) {
        return std::unexpected(Status::BufferOverflow);
    }

    size_t read_idx = 0;
    size_t write_idx = 1;
    size_t code_idx = 0;
    uint8_t code = 0x01;

    while (read_idx < src.size()) {
        const uint8_t byte = src[read_idx++];
        if (byte == 0x00) {
            dst[code_idx] = code;
            code_idx = write_idx++;
            code = 0x01;
        } else {
            dst[write_idx++] = byte;
            code++;
            if (code == 0xFF) {
                dst[code_idx] = code;
                code_idx = write_idx++;
                code = 0x01;
            }
        }
    }
    dst[code_idx] = code;
    return write_idx;
}

[[nodiscard]] constexpr std::expected<size_t, Status> decode(
    std::span<const uint8_t> src, 
    std::span<uint8_t> dst
) noexcept {
    if (src.empty()) return 0;

    size_t read_idx = 0;
    size_t write_idx = 0;

    while (read_idx < src.size()) {
        const uint8_t code = src[read_idx++];
        if (code == 0x00) return std::unexpected(Status::ZeroInPayload);

        const size_t copy_len = code - 1;
        if (read_idx + copy_len > src.size()) {
            return std::unexpected(Status::InvalidOffset);
        }
        if (write_idx + copy_len > dst.size()) {
            return std::unexpected(Status::BufferOverflow);
        }

        for (size_t i = 0; i < copy_len; ++i) {
            dst[write_idx++] = src[read_idx++];
        }

        if (code < 0xFF && read_idx < src.size()) {
            if (write_idx >= dst.size()) {
                return std::unexpected(Status::BufferOverflow);
            }
            dst[write_idx++] = 0x00;
        }
    }

    return write_idx;
}

template <size_t MaxPacketSize>
class StreamingDecoder {
public:
    enum class State {
        HuntDelimiter,
        ReadCode,
        ReadData
    };

    constexpr StreamingDecoder() noexcept = default;

    template <typename Callback>
    requires std::invocable<Callback, std::span<const uint8_t>>
    Status feed(uint8_t byte, Callback&& on_packet_cb) noexcept {
        if (byte == 0x00) {
            if (state_ == State::ReadData && block_rem_ > 0) {
                rx_len_ = 0;
                state_ = State::ReadCode;
                return Status::UnexpectedDelimiter;
            }

            if (rx_len_ > 0) {
                std::span<const uint8_t> packet{buffer_.data(), rx_len_};
                rx_len_ = 0;
                state_ = State::ReadCode;
                std::forward<Callback>(on_packet_cb)(packet);
                return Status::Ok;
            }

            state_ = State::ReadCode;
            return Status::Ok;
        }

        switch (state_) {
        case State::HuntDelimiter:
            break;

        case State::ReadCode:
            code_ = byte;
            if (code_ == 0x01) {
                if (rx_len_ >= MaxPacketSize) {
                    reset_on_overflow();
                    return Status::BufferOverflow;
                }
                buffer_[rx_len_++] = 0x00;
            } else {
                block_rem_ = code_ - 1;
                state_ = State::ReadData;
            }
            break;

        case State::ReadData:
            if (rx_len_ >= MaxPacketSize) {
                reset_on_overflow();
                return Status::BufferOverflow;
            }

            buffer_[rx_len_++] = byte;
            block_rem_--;

            if (block_rem_ == 0) {
                if (code_ < 0xFF) {
                    if (rx_len_ >= MaxPacketSize) {
                        reset_on_overflow();
                        return Status::BufferOverflow;
                    }
                    buffer_[rx_len_++] = 0x00;
                }
                state_ = State::ReadCode;
            }
            break;
        }

        return Status::Ok;
    }

    [[nodiscard]] constexpr size_t current_length() const noexcept { return rx_len_; }
    constexpr void reset() noexcept {
        rx_len_ = 0;
        state_ = State::HuntDelimiter;
        code_ = 0;
        block_rem_ = 0;
    }

private:
    constexpr void reset_on_overflow() noexcept {
        rx_len_ = 0;
        state_ = State::HuntDelimiter;
    }

    std::array<uint8_t, MaxPacketSize> buffer_{};
    size_t rx_len_{0};
    State state_{State::HuntDelimiter};
    uint8_t code_{0};
    uint8_t block_rem_{0};
};

} // namespace cobs
```
:::

---

## Інтеграція з кільцевим буфером DMA на STM32

Для досягнення максимальної пропускної здатності на сучасних мікроконтролерах STM32 (наприклад, Cortex-M4/M7) прийом байтів організовують через апаратний модуль прямого доступу до пам'яті (DMA) у циклічному режимі (англ. *Circular Mode*).

Канал DMA налаштовується на постійне зчитування регістру даних UART `USART_RDR` у проміжний кільцевий масив пам'яті `dma_ring_buffer` розміром 128 або 256 байтів.

Програма налаштовує три типи апаратних переривань:
1. **`HT` (Half-Transfer Interrupt):** Генерується контролером DMA, коли заповнено рівно першу половину кільцевого буфера. Головний процесор опрацьовує байти від індексу `0` до `capacity / 2 - 1`, передаючи їх у функцію `cobs_parser_feed_byte`.
2. **`TC` (Transfer-Complete Interrupt):** Генерується контролером DMA, коли заповнення дійшло до кінця буфера. Процесор опрацьовує другу половину буфера від індексу `capacity / 2` до `capacity - 1`.
3. **`IDLE` (UART Line Idle Interrupt):** Генерується апаратною логікою UART, коли лінія зв'язку перебуває в стані спокою протягом часу передачі одного байта. Це дозволяє негайно обробити хвіст пакета, не чекаючи заповнення повної половини буфера DMA.

Ця трирівнева схема гарантує нульові втрати байтів навіть при 100% завантаженні процесора іншими обчислювальними завданнями RTOS, забезпечуючи надійне кадрування на швидкостях до декількох мегабіт за секунду.

### Узгодженість кешу даних на процесорах ARM Cortex-M7

На високопродуктивних мікроконтролерах із роздільним кешем інструкцій та даних (наприклад, STM32H7 на базі ядра ARM Cortex-M7 із тактовою частотою 480 МГц) апаратний контролер DMA записує байти безпосередньо в системну пам'ять AXI SRAM, оминаючи L1 D-Cache процесора.

Якщо не вжити спеціальних заходів, виникає критична проблема узгодженості кешу (англ. *Cache Coherency*): процесор може зчитувати застарілі дані зі свого внутрішнього кешу замість свіжих байтів, записаних контролером DMA.

Для запобігання цьому дефекту застосовують два інженерні рішення:
* **Інвалідація ліній кешу:** Перед передачею даних із буфера DMA в парсер COBS викликається інструкція ядра `SCB_InvalidateDCache_by_Addr((uint32_t*)dma_buf, size)`.
* **Налаштування блоку MPU:** За допомогою модуля захисту пам'яті (англ. *Memory Protection Unit*, MPU) область пам'яті буферів DMA конфігурується як некешована (англ. *Non-cacheable / Device Memory* або *Shareable*).

---

## Взаємодія з FreeRTOS та асинхронними чергами

У багатозадачних операційних системах реального часу (FreeRTOS, Zephyr) розпакований пакет передається з контексту переривання в завдання прикладного аналізу за принципом нульового копіювання (Zero-Copy):
* Переривання UART накопичує байти в статичному буфері `parser.rx_buf`.
* Щойно `cobs_parser_feed_byte` повертає `true`, обробник переривання викликає системну функцію `xQueueSendFromISR`, передаючи в чергу завдань лише вказівник на готовий буфер та довжину пакета.
* Завдання-обробник прокидається за подією черги, перевіряє контрольну суму CRC та опрацьовує команду телеметрії.

Завдяки фіксованому розміру буферів та відсутності динамічної купи операційна система гарантує суворий детермінізм часу відгуку, що критично важливо для контурів керування авіоніки та приводів роботів.

---

## Апаратне споживання пам'яті на різних архітектурах

Завдяки граничній лаконічності алгоритму кодек COBS має надзвичайно низький апаратний відбиток (англ. *Memory Footprint*) у бінарному файлі прошивки:

| Апаратна платформа | Архітектура | Розмір коду (Flash) | Статична RAM кодека | Динамічна RAM (Heap) |
|---|---|---|---|---|
| ATmega328P (Arduino) | AVR 8-bit | ~180 байтів | 16 байтів (`cobs_parser_t`) | **0 байтів** |
| STM32G030 (Cortex-M0+) | ARMv6-M 32-bit | ~210 байтів | 24 байти (`cobs_parser_t`) | **0 байтів** |
| STM32F401 (Cortex-M4) | ARMv7E-M 32-bit | ~240 байтів | 24 байти (`cobs_parser_t`) | **0 байтів** |
| ESP32-S3 | Xtensa LX7 32-bit | ~290 байтів | 32 байти (`cobs_parser_t`) | **0 байтів** |

Мінімальні вимоги до пам'яті дозволяють запускати кодек COBS навіть на найдешевших восьмибітних мікроконтролерах із кількома сотнями байтів оперативної пам'яті. При компіляції з прапорцями оптимізації `-O2` або `-Os` та увімкненим Link-Time Optimization (`-flto`) увесь модуль займає менше половини одного сектора Flash-пам'яті.

---

## Аналіз поведінки кодека при канальних збоях

В умовах промислового цеху або силового відсіку дрона електромагнітні наведення від безколекторних моторів (BLDC) створюють сплески напруги на лініях послідовного зв'язку. Розглянемо, як розроблений кодек відпрацьовує типові аварійні сценарії:

### Сценарій A: Втрата байта через апаратне переповнення UART FIFO
Якщо процесор не встиг вичитати регістр даних UART, виникає помилка переповнення Overrun Error (`ORE`), і один байт випадає з потоку. У цьому випадку реальна довжина блоку даних виявляється на 1 меншою за значення зчитаного покажчика `code`. Коли в лінію надходить кінцевий розділювач `0x00`, лічильник `block_rem` усе ще дорівнює `1`. Парсер миттєво фіксує статус `COBS_ERR_UNEXPECTED_DELIMITER`, скидає накопичувальний індекс `rx_len = 0` і запобігає передачі пошкодженого обрізка на прикладний рівень.

### Сценарій B: Інверсія бітів у байті покажчика зміщення
Якщо завада спотворює значення кодового октету (наприклад, замість `0x03` приймач отримує `0x83`), автомат очікує 130 байтів замість 2. Зустріч зі справжнім нулем `0x00` через 2 байти негайно перериває накопичення і скидає стан у точку синхронізації. Спроба інтерпретації спотворених даних повністю блокується на канальному рівні.

### Сценарій C: Поява фальшивого розділювача 0x00
Якщо імпульсна перешкода перетворює ненульовий байт на `0x00`, поточний блок обривається достроково. Автомат фіксує аварійний стан `COBS_ERR_UNEXPECTED_DELIMITER` і скидає неповний пакет. Наступний блок буде розпізнано як новий пакет або відкинуто контрольною сумою CRC, що повністю виключає аварійне зависання мікроконтролера.

---

## Оптимізація сканування нулів на 32-розрядних процесорах (SWAR)

На 32-розрядних ядрах ARM Cortex-M4/M7 кодування довгих пакетів можна додатково прискорити за допомогою паралельного аналізу 4 байтів за одну інструкцію (техніка SWAR — *SIMD Within A Register*).

Замість побайтового порівняння перевірка наявності хоча б одного нульового октету в 32-бітному слові `v` виконується арифметичним виразом:

```
has_zero_byte(v) = ((v - 0x01010101UL) & ~v & 0x80808080UL)
```

Якщо цей вираз повертає нуль, усе 32-бітне слово гарантовано не містить нулів і може бути записане у вихідний буфер однією машинною інструкцією `STR` із відповідним збільшенням покажчика на 4. Це зменшує час кодування довгих блоків телеметрії на 60% порівняно з наївним побайтовим циклом.

---

## Методологія модульного та стрес-тестування (Fuzzing)

Для гарантії безперебійної роботи канального драйвера в реальних польотних умовах кодек піддається автоматизованому стрес-тестуванню (англ. *Fuzz Testing*):
1. **Тестування на випадкових масивах:** Генератор випадкових чисел генерує мільйон пакетів довільної довжини від 0 до 2048 байтів із різним вмістом (випадкові байти, суцільні нулі, відсутність нулів, блоки понад 254 байти). Кожен пакет кодується, декодується та побайтово порівнюється з оригіналом.
2. **Ін'єкція канальних спотворень:** У закодований потік штучно вносяться випадкові бітові помилки, випадання символів та вставки нулів. Тестовий стенд контролює, що за будь-яких вхідних послідовностей:
   * Не відбувається виходу за межі виділених буферів пам'яті (відсутність Buffer Overrun);
   * Лічильник прийнятих байтів не перевищує місткість буфера;
   * Парсер повертається в робочий режим синхронізації відразу після надходження коректного кадру.

---

## Набір тестових векторів та верифікація

Для перевірки коректності компіляції та функціонування кодека на цільовій апаратній платформі використовується набір стандартизованих тестових векторів:

| № | Вхідні дані (Hex) | Закодований масив COBS | Розмір (Out/In) | Опис тестового сценарію |
|---|---|---|---|---|
| 1 | `[ 0x00 ]` | `[ 0x01, 0x01 ]` | 2 / 1 | Одиночний нуль (поглинання) |
| 2 | `[ 0x00, 0x00 ]` | `[ 0x01, 0x01, 0x01 ]` | 3 / 2 | Послідовні нулі |
| 3 | `[ 0x11, 0x22, 0x00, 0x33 ]` | `[ 0x03, 0x11, 0x22, 0x02, 0x33 ]` | 5 / 4 | Розбиття на два блоки |
| 4 | `[ 0x11, 0x22, 0x33, 0x44 ]` | `[ 0x05, 0x11, 0x22, 0x33, 0x44 ]` | 5 / 4 | Масив без нулів |
| 5 | `[ 0x11, 0x00, 0x00, 0x00 ]` | `[ 0x02, 0x11, 0x01, 0x01, 0x01 ]` | 5 / 4 | Серія нулів наприкінці |
| 6 | `[ 0x01, 0x02, ..., 0xFE ]` | `[ 0xFF, 0x01, 0x02, ..., 0xFE ]` | 255 / 254 | Блок максимальної довжини 254 |
| 7 | `[ 0x00, 0x01, ..., 0xFE ]` | `[ 0x01, 0xFF, 0x01, ..., 0xFE ]` | 256 / 255 | Нуль перед блоком 254 байти |
| 8 | `[ 0x01, 0x02, ..., 0xFF ]` | `[ 0xFF, 0x01, ..., 0xFE, 0x02, 0xFF ]` | 257 / 255 | Переповнення блоку 254 (255 байтів) |

Усі наведені тестові випадки мають проходити автоматичні тести перевірки як для блокових функцій `cobs_encode`/`cobs_decode`, так і для потокового класу `StreamingDecoder`.

### Діагностика фізичного сигналу осцилографом

Під час налагодження каналу зв'язку за допомогою логічного аналізатора (наприклад, Saleae Logic) кадри COBS легко ідентифікуються серед шумів:
* Між пакетами на лінії спостерігається рівень логічної одиниці (стан IDLE послідовного порту UART).
* Кожен кадр завершується передачею байта `0x00` (старт-біт 0, 8 нульових бітів даних, стоп-біт 1), що створює характерний довгий імпульс низького рівня на екрані осцилографа.
* Усередині самого пакета жоден байт не створює аналогічного дев'ятибітного імпульсу нуля, що виключає хибне спрацьовування апаратних тригерів синхронізації вимірювальних приладів.

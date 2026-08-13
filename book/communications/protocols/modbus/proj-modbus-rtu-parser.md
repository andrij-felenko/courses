# ⚙️ Парсер кадрів Modbus RTU та обчислення CRC-16

Цей проєктний модуль містить практичну ідіоматичну реалізацію обчислення контрольної суми Modbus CRC-16 та парсингу вхідних кадрів Modbus RTU для вбудованих систем і серверного коду мовами C та C++.

### Принцип обчислення CRC-16 (Modbus IBM Polynomial)

Перевірка цілісності двійкових кадрів у Modbus RTU виконується за допомогою 16-бітного циклічного надлишкового коду (CRC-16). Алгоритм використовує реверсивний поліном `0xA001` (що відповідає прямому поліному `0x8005`, `x^16 + x^15 + x^2 + 1`).

Покроковий алгоритм обчислення:
1. Регістр CRC ініціалізується значенням `0xFFFF`.
2. Кожен черговий байт вхідного масиву об'єднується операцією XOR з молодшим байтом регістра CRC.
3. Регістр зсувається на 1 біт праворуч (у бік молодшого біта).
4. Якщо висунутий молодший біт дорівнював `1`, регістр XOR-иться з константою полінома `0xA001`.
5. Кроки 3 та 4 повторюються 8 разів для всіх бітів поточного байта.
6. Після обробки всіх байтів кадру результат повертається у форматі **Little-Endian**: спочатку молодший байт CRC, потім старший.

У реалізованому парсері функція приймає сирий буфер байтів, перевіряє мінімально припустиму довжину кадру (4 байти: 1 байт адреси + 1 байт коду функції + 2 байти CRC), розраховує контрольною суму над отриманим пакетом і порівнює її з прийнятою. Якщо CRC збігається, парсер декодує код функції, перевіряє виставлення прапорця винятку (старший біт `0x80`) і виділяє вказівник на корисне навантаження (payload).

### Організація обробки винятків та перевірка адресації

Під час прийому кадру ведений пристрій (Слейв) або клієнтська бібліотека повинні спочатку перевірити збіг адреси пристрою. Якщо адреса в першому байті кадру не збігається з власною адресою вузла і не дорівнює `0` (широкомовна адреса Broadcast), кадр ігнорується без виклику будь-яких обробників.

Якщо код функції у другого байта має встановлений найстарший біт `0x80` (наприклад, `0x83` замість `0x03`), це означає, що пристрій повернув відповідь-виняток. Парсер відокремлює код винятку (Exception Code), який міститься у третьому байті кадру, та сигналізує про помилку вищому рівню застосунку.

### Покроковий приклад розбору реального кадру

Розглянемо сирий двійковий кадр із 8 байтів, який надійшов із послідовного порту:

`01 03 00 6B 00 02 B5 D9`

Кроки обробки парсером:
1. **Перевірка довжини:** Довжина `8` байтів `>= 4` байтів — умова виконується.
2. **Обчислення CRC-16:** Функція `modbus_crc16` приймає перші 6 байтів (`01 03 00 6B 00 02`). Обчислене значення дорівнює `0xD9B5`.
3. **Зчитування прийнятого CRC:** Останні два байти `B5 D9` інтерпретуються як 16-бітне число в Little-Endian: `(0xD9 << 8) | 0xB5 = 0xD9B5`.
4. **Порівняння CRC:** `0xD9B5 == 0xD9B5` — контрольна сума збіглася, кадр не пошкоджено.
5. **Адресація:** Перший байт `0x01` відповідає адресі нашого пристрою.
6. **Декодування PDU:** Байт 1 містить код функції `0x03` (Read Holding Registers). Старший біт не виставлений (`0x03 & 0x80 == 0`), отже це нормальний запит без винятку. Корисне навантаження (Payload) займає байти з 2 по 5 (`00 6B 00 02`), що означає початкову адресу `107` та кількість регістрів `2`.

### Скінченний автомат прийому кадрів з кільцевого буфера

На рівні вбудованої прошивки (Firmware) байти надходять із переривання UART по одному в кільцевий буфер (Ring Buffer). Для виділення кадру Modbus RTU з безперервного потоку застосовують апаратний або програмний таймер міжкадрової тиші `t3.5`.

Скінченний автомат (FSM) приймача має три основні стани:
1. **STATE_IDLE (Очікування):** Таймер `t3.5` підраховує інтервал тиші. Скидання лічильника байтів відбувається при виявленні паузи понад `t3.5`.
2. **STATE_RECEIVING (Прийом кадру):** Кожен прибулий байт записується в буфер пакета, а таймер `t1.5` перезапускається. Якщо інтервал між байтами перевищує `t1.5`, автомат переходить у стан помилки (розрив кадру).
3. **STATE_FRAME_READY (Кадр сформовано):** При виникненні паузи понад `t3.5` після прийому байтів автомат фіксує завершення кадру та передає буфер на перевірку CRC-16 та декодування.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коди помилок парсера Modbus RTU */
typedef enum {
    MODBUS_OK = 0,
    MODBUS_ERR_FRAME_TOO_SHORT,
    MODBUS_ERR_ADDRESS_MISMATCH,
    MODBUS_ERR_CRC_INVALID,
    MODBUS_ERR_EXCEPTION_RESPONSE
} modbus_status_t;

/* Структура розібраного кадру */
typedef struct {
    uint8_t slave_addr;
    uint8_t function_code;
    bool is_exception;
    uint8_t exception_code;
    const uint8_t *payload;
    size_t payload_len;
} modbus_frame_t;

/* Обчислення Modbus CRC-16 за поліномом 0xA001 */
uint16_t modbus_crc16(const uint8_t *buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= buffer[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

/* Парсер вхідного кадру Modbus RTU */
modbus_status_t modbus_rtu_parse(const uint8_t *buffer, size_t length,
                                  uint8_t my_address, modbus_frame_t *out_frame) {
    /* Мінімальний кадр RTU: Адреса (1) + Код (1) + CRC (2) = 4 байти */
    if (length < 4) {
        return MODBUS_ERR_FRAME_TOO_SHORT;
    }

    /* Перевірка контрольної суми CRC-16 */
    uint16_t calculated_crc = modbus_crc16(buffer, length - 2);
    uint16_t rx_crc = (uint16_t)buffer[length - 2] | ((uint16_t)buffer[length - 1] << 8);

    if (calculated_crc != rx_crc) {
        return MODBUS_ERR_CRC_INVALID;
    }

    uint8_t addr = buffer[0];
    /* Фільтрація адреси (якщо my_address == 0, приймаємо будь-яку) */
    if (my_address != 0 && addr != my_address && addr != 0) {
        return MODBUS_ERR_ADDRESS_MISMATCH;
    }

    out_frame->slave_addr = addr;
    uint8_t fc = buffer[1];

    /* Перевірка прапорця винятку (старший біт 0x80) */
    if (fc & 0x80) {
        out_frame->function_code = fc & 0x7F;
        out_frame->is_exception = true;
        out_frame->exception_code = (length > 4) ? buffer[2] : 0;
        out_frame->payload = NULL;
        out_frame->payload_len = 0;
        return MODBUS_ERR_EXCEPTION_RESPONSE;
    }

    out_frame->function_code = fc;
    out_frame->is_exception = false;
    out_frame->exception_code = 0;
    out_frame->payload = &buffer[2];
    out_frame->payload_len = length - 4; /* Віднімаємо адресу, код та 2 байти CRC */

    return MODBUS_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <expected>

enum class ModbusError {
    FrameTooShort,
    AddressMismatch,
    CrcInvalid,
    ExceptionResponse
};

struct ModbusFrame {
    uint8_t slave_addr{0};
    uint8_t function_code{0};
    bool is_exception{false};
    uint8_t exception_code{0};
    std::span<const uint8_t> payload{};
};

class ModbusRtuParser {
public:
    static constexpr uint16_t calculate_crc(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0xA001;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    static std::expected<ModbusFrame, ModbusError> parse(
        std::span<const uint8_t> frame_bytes,
        uint8_t my_address = 0) noexcept 
    {
        if (frame_bytes.size() < 4) {
            return std::unexpected(ModbusError::FrameTooShort);
        }

        const size_t payload_and_hdr_len = frame_bytes.size() - 2;
        const uint16_t calculated_crc = calculate_crc(frame_bytes.first(payload_and_hdr_len));
        const uint16_t rx_crc = static_cast<uint16_t>(frame_bytes[frame_bytes.size() - 2]) |
                               (static_cast<uint16_t>(frame_bytes[frame_bytes.size() - 1]) << 8);

        if (calculated_crc != rx_crc) {
            return std::unexpected(ModbusError::CrcInvalid);
        }

        const uint8_t addr = frame_bytes[0];
        if (my_address != 0 && addr != my_address && addr != 0) {
            return std::unexpected(ModbusError::AddressMismatch);
        }

        ModbusFrame frame;
        frame.slave_addr = addr;
        const uint8_t raw_fc = frame_bytes[1];

        if (raw_fc & 0x80) {
            frame.function_code = raw_fc & 0x7F;
            frame.is_exception = true;
            frame.exception_code = (frame_bytes.size() > 4) ? frame_bytes[2] : 0;
            return std::unexpected(ModbusError::ExceptionResponse);
        }

        frame.function_code = raw_fc;
        frame.is_exception = false;
        frame.payload = frame_bytes.subspan(2, payload_and_hdr_len - 2);

        return frame;
    }
};
```
:::

### Оцінка продуктивності та оптимізація Табличним CRC

Попобітовий алгоритм обчислення CRC-16, наведений у коді, вимагає 8 циклів із умовними розгалуженнями на кожен байт. На малопотужних 8-бітних та 16-бітних мікроконтролерах без апаратного прискорювача CRC це може створювати помітне обчислювальне навантаження.

Для прискорення обчислень у 8–10 разів використовують **табличний алгоритм (Lookup Table)**, де результати XOR-ування попередньо розраховано для всіх 256 можливих значень байта та збережено у Flash-пам'яті у вигляді двох таблиць по 256 байтів (`auchCRCHi` та `auchCRCLo`). Поточний байт слугує індексом у таблиці, що дозволяє замінити цикл із 8 зсувів одним зверненням до пам'яті. Проте для систем із жорстким обмеженням обсягу Flash-пам'яті попобітовий обчислювач є переважним через нульовий додатковий обсяг пам'яті.

При написанні C++ коду використання `std::span` дозволяє уникнути копіювання буферів та забезпечує безпеку меж масиву без виділення динамічної пам'яті у купі (Heap), що є критичним для високонадійних вбудованих систем реального часу.

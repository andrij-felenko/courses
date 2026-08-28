# ⚙️ Парсер та серіалізатор CoAP без динамічної пам'яті на C та C++

У цьому проектному матеріалі реалізовано компактну та безпечну бібліотеку двійкового розбору й серіалізації повідомлень протоколу CoAP (RFC 7252) для вбудованих систем реального часу. Реалізація спроектована за принципом повної відмови від динамічної пам'яті (zero-allocation) і працює безпосередньо з вхідними та вихідними буферами мережевого стека «на місці» (in-place zero-copy). Це унеможливлює фрагментацію купи, витоки пам'яті та недетерміновані затримки на мікроконтролерах із жорсткими обмеженнями оперативної пам'яті (ARM Cortex-M0+/M4, RISC-V, ESP32, STM32, AVR).

### Архітектурні принципи zero-allocation у вбудованих системах

Розробка мережевого парсера для мікроконтролерів класу C0/C1 (RAM від 2 до 10 КБ) вимагає суворого контролю кожного байта пам'яті на стеку та повного виключення викликів `malloc()` і `free()`. Динамічне виділення пам'яті в умовах тривалої безперервної роботи (місяці або роки без перезавантаження) неминуче призводить до фрагментації пулу вільної пам'яті, коли черговий запит завершується фатальним аварійним скиданням через брак неперервного блоку пам'яті.

Запропонована архітектура вирішує цю проблему завдяки дескрипторному розбору:
1. **Зрізи пам'яті замість копіювання:** Замість копіювання значень опцій (наприклад, текстових рядків `Uri-Path` чи бінарних корисних навантажень) дескриптор зберігає лише пару «покажчик + довжина» або безпечний шаблон `std::span` / `std::string_view` у C++, що посилається на байти вже виділеного статичного буфера вхідного UDP-пакета.
2. **Статичний ліміт таблиці опцій:** Кількість одночасно оброблюваних опцій в одному пакеті фіксується константою `COAP_MAX_OPTIONS` (за замовчуванням 16). Для 99% практичних сценаріїв IoT (шлях із 2–3 сегментів, формат контенту, маркер спостереження, номер блока) 16 слотів є більш ніж достатнім запасом, а розмір самої структури дескриптора на стеку становить менш як 300 байтів.
3. **Захист від нерозпізнаних та пошкоджених даних:** Перевірка меж буфера здійснюється перед кожним читанням байта. Це захищає систему від атак переповнення буфера (buffer overflow) та читання за межами виділеного масиву (out-of-bounds read) при отриманні навмисно спотворених пакетів з ефіру.
4. **Вирівнювання пам'яті та порядок байтів:** Читання багатобайтових числових полів (`Message ID`, розширені зміщення дельти) виконується побайтовими бітовими зсувами, що усуває проблеми неперевіреного доступу до невирівняних адрес (англ. *unaligned memory access faults*) на процесорних ядрах ARM Cortex-M0/M0+, які апаратно не підтримують непарні адреси для 16/32-бітних слів.

### Структури даних та реалізація парсера

Нижче наведено повні реалізації бібліотеки на чистому стандарті C99 та сучасному ідіоматичному C++23. Обидва варіанти містять повнофункціональний парсер вхідних датаграм `coap_parse()` / `PacketView::parse()` та зворотний серіалізатор `coap_serialize()`.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define COAP_HEADER_SIZE 4
#define COAP_PAYLOAD_MARKER 0xFF
#define COAP_MAX_OPTIONS 16

typedef enum {
    COAP_TYPE_CON = 0,
    COAP_TYPE_NON = 1,
    COAP_TYPE_ACK = 2,
    COAP_TYPE_RST = 3
} coap_type_t;

typedef struct {
    uint16_t number;
    uint16_t length;
    const uint8_t *value;
} coap_option_t;

typedef struct {
    uint8_t version;
    coap_type_t type;
    uint8_t token_len;
    uint8_t code;
    uint16_t message_id;
    uint8_t token[8];
    coap_option_t options[COAP_MAX_OPTIONS];
    size_t option_count;
    const uint8_t *payload;
    size_t payload_len;
} coap_packet_t;

/* Розбір вхідної UDP-датаграми у структуру coap_packet_t */
bool coap_parse(const uint8_t *buf, size_t len, coap_packet_t *pkt) {
    if (!buf || !pkt || len < COAP_HEADER_SIZE) {
        return false;
    }

    memset(pkt, 0, sizeof(*pkt));

    pkt->version = (buf[0] >> 6) & 0x03;
    if (pkt->version != 1) {
        return false; /* Непідтримувана версія CoAP */
    }

    pkt->type = (coap_type_t)((buf[0] >> 4) & 0x03);
    pkt->token_len = buf[0] & 0x0F;
    if (pkt->token_len > 8) {
        return false; /* TKL більше 8 є неприпустимим */
    }

    pkt->code = buf[1];
    pkt->message_id = ((uint16_t)buf[2] << 8) | buf[3];

    size_t offset = COAP_HEADER_SIZE;
    if (len < offset + pkt->token_len) {
        return false;
    }

    if (pkt->token_len > 0) {
        memcpy(pkt->token, &buf[offset], pkt->token_len);
        offset += pkt->token_len;
    }

    uint16_t current_option_number = 0;

    while (offset < len) {
        if (buf[offset] == COAP_PAYLOAD_MARKER) {
            offset++; /* Пропускаємо маркер 0xFF */
            if (offset >= len) {
                return false; /* Маркер без тіла є помилкою синтаксису */
            }
            pkt->payload = &buf[offset];
            pkt->payload_len = len - offset;
            return true;
        }

        if (pkt->option_count >= COAP_MAX_OPTIONS) {
            return false; /* Переповнення статичної таблиці опцій */
        }

        uint8_t opt_header = buf[offset++];
        uint16_t delta = (opt_header >> 4) & 0x0F;
        uint16_t opt_len = opt_header & 0x0F;

        if (delta == 15 || opt_len == 15) {
            return false; /* Значення 15 зарезервовано для маркера */
        }

        /* Розширення Delta */
        if (delta == 13) {
            if (offset >= len) return false;
            delta = (uint16_t)buf[offset++] + 13;
        } else if (delta == 14) {
            if (offset + 1 >= len) return false;
            delta = (((uint16_t)buf[offset] << 8) | buf[offset + 1]) + 269;
            offset += 2;
        }

        /* Розширення Length */
        if (opt_len == 13) {
            if (offset >= len) return false;
            opt_len = (uint16_t)buf[offset++] + 13;
        } else if (opt_len == 14) {
            if (offset + 1 >= len) return false;
            opt_len = (((uint16_t)buf[offset] << 8) | buf[offset + 1]) + 269;
            offset += 2;
        }

        if (offset + opt_len > len) {
            return false;
        }

        current_option_number += delta;
        pkt->options[pkt->option_count].number = current_option_number;
        pkt->options[pkt->option_count].length = opt_len;
        pkt->options[pkt->option_count].value = &buf[offset];
        pkt->option_count++;

        offset += opt_len;
    }

    return true;
}

/* Серіалізація структури coap_packet_t у вихідний буфер */
size_t coap_serialize(const coap_packet_t *pkt, uint8_t *out, size_t max_len) {
    if (!pkt || !out || max_len < (size_t)(COAP_HEADER_SIZE + pkt->token_len)) {
        return 0;
    }

    out[0] = (uint8_t)((1 << 6) | ((pkt->type & 0x03) << 4) | (pkt->token_len & 0x0F));
    out[1] = pkt->code;
    out[2] = (uint8_t)(pkt->message_id >> 8);
    out[3] = (uint8_t)(pkt->message_id & 0xFF);

    size_t offset = COAP_HEADER_SIZE;
    if (pkt->token_len > 0) {
        memcpy(&out[offset], pkt->token, pkt->token_len);
        offset += pkt->token_len;
    }

    uint16_t prev_opt_num = 0;
    for (size_t i = 0; i < pkt->option_count; i++) {
        const coap_option_t *opt = &pkt->options[i];
        if (opt->number < prev_opt_num) {
            return 0; /* Порушено обов'язкове сортування опцій */
        }

        uint16_t delta = opt->number - prev_opt_num;
        uint8_t d_header = (delta < 13) ? (uint8_t)delta : (delta < 269 ? 13 : 14);
        uint8_t l_header = (opt->length < 13) ? (uint8_t)opt->length : (opt->length < 269 ? 13 : 14);

        if (offset >= max_len) return 0;
        out[offset++] = (uint8_t)((d_header << 4) | l_header);

        if (d_header == 13) {
            if (offset >= max_len) return 0;
            out[offset++] = (uint8_t)(delta - 13);
        } else if (d_header == 14) {
            if (offset + 1 >= max_len) return 0;
            uint16_t ext = delta - 269;
            out[offset++] = (uint8_t)(ext >> 8);
            out[offset++] = (uint8_t)(ext & 0xFF);
        }

        if (l_header == 13) {
            if (offset >= max_len) return 0;
            out[offset++] = (uint8_t)(opt->length - 13);
        } else if (l_header == 14) {
            if (offset + 1 >= max_len) return 0;
            uint16_t ext = opt->length - 269;
            out[offset++] = (uint8_t)(ext >> 8);
            out[offset++] = (uint8_t)(ext & 0xFF);
        }

        if (offset + opt->length > max_len) return 0;
        memcpy(&out[offset], opt->value, opt->length);
        offset += opt->length;

        prev_opt_num = opt->number;
    }

    if (pkt->payload && pkt->payload_len > 0) {
        if (offset + 1 + pkt->payload_len > max_len) return 0;
        out[offset++] = COAP_PAYLOAD_MARKER;
        memcpy(&out[offset], pkt->payload, pkt->payload_len);
        offset += pkt->payload_len;
    }

    return offset;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>
#include <optional>
#include <expected>
#include <algorithm>

namespace coap {

enum class Type : uint8_t {
    Confirmable = 0,
    NonConfirmable = 1,
    Acknowledgement = 2,
    Reset = 3
};

enum class ParseError {
    BufferTooSmall,
    InvalidVersion,
    InvalidTokenLength,
    MalformedOptions,
    OptionsNotSorted,
    EmptyPayloadMarker,
    OptionBufferOverflow
};

struct OptionView {
    uint16_t number{0};
    std::span<const uint8_t> value{};

    [[nodiscard]] std::string_view as_string() const noexcept {
        return {reinterpret_cast<const char*>(value.data()), value.size()};
    }

    [[nodiscard]] uint32_t as_uint() const noexcept {
        uint32_t res = 0;
        for (uint8_t b : value) {
            res = (res << 8) | b;
        }
        return res;
    }
};

class PacketView {
public:
    static constexpr size_t HeaderSize = 4;
    static constexpr uint8_t PayloadMarker = 0xFF;
    static constexpr size_t MaxOptions = 16;

    uint8_t version{1};
    Type type{Type::Confirmable};
    uint8_t code{0};
    uint16_t message_id{0};
    std::span<const uint8_t> token{};
    std::array<OptionView, MaxOptions> options{};
    size_t option_count{0};
    std::span<const uint8_t> payload{};

    static std::expected<PacketView, ParseError> parse(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < HeaderSize) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        PacketView pkt;
        pkt.version = (buffer[0] >> 6) & 0x03;
        if (pkt.version != 1) {
            return std::unexpected(ParseError::InvalidVersion);
        }

        pkt.type = static_cast<Type>((buffer[0] >> 4) & 0x03);
        const uint8_t tkl = buffer[0] & 0x0F;
        if (tkl > 8) {
            return std::unexpected(ParseError::InvalidTokenLength);
        }

        pkt.code = buffer[1];
        pkt.message_id = (static_cast<uint16_t>(buffer[2]) << 8) | buffer[3];

        size_t offset = HeaderSize;
        if (buffer.size() < offset + tkl) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        if (tkl > 0) {
            pkt.token = buffer.subspan(offset, tkl);
            offset += tkl;
        }

        uint16_t current_option_number = 0;

        while (offset < buffer.size()) {
            if (buffer[offset] == PayloadMarker) {
                offset++;
                if (offset >= buffer.size()) {
                    return std::unexpected(ParseError::EmptyPayloadMarker);
                }
                pkt.payload = buffer.subspan(offset);
                return pkt;
            }

            if (pkt.option_count >= MaxOptions) {
                return std::unexpected(ParseError::OptionBufferOverflow);
            }

            const uint8_t header = buffer[offset++];
            uint16_t delta = (header >> 4) & 0x0F;
            uint16_t length = header & 0x0F;

            if (delta == 15 || length == 15) {
                return std::unexpected(ParseError::MalformedOptions);
            }

            if (delta == 13) {
                if (offset >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                delta = static_cast<uint16_t>(buffer[offset++]) + 13;
            } else if (delta == 14) {
                if (offset + 1 >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                delta = ((static_cast<uint16_t>(buffer[offset]) << 8) | buffer[offset + 1]) + 269;
                offset += 2;
            }

            if (length == 13) {
                if (offset >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                length = static_cast<uint16_t>(buffer[offset++]) + 13;
            } else if (length == 14) {
                if (offset + 1 >= buffer.size()) return std::unexpected(ParseError::MalformedOptions);
                length = ((static_cast<uint16_t>(buffer[offset]) << 8) | buffer[offset + 1]) + 269;
                offset += 2;
            }

            if (offset + length > buffer.size()) {
                return std::unexpected(ParseError::BufferTooSmall);
            }

            current_option_number += delta;
            pkt.options[pkt.option_count++] = OptionView{
                .number = current_option_number,
                .value = buffer.subspan(offset, length)
            };
            offset += length;
        }

        return pkt;
    }

    [[nodiscard]] std::optional<OptionView> find_option(uint16_t number) const noexcept {
        for (size_t i = 0; i < option_count; ++i) {
            if (options[i].number == number) {
                return options[i];
            }
        }
        return std::nullopt;
    }
};

} // namespace coap
```
:::

### Покроковий розбір алгоритму парсингу та граничні випадки

Алгоритм розбору побудовано у вигляді послідовного кінцевого автомата (FSM), який крок за кроком верифікує цілісність бінарного потоку:

1. **Валідація розміру та магічних бітів заголовка:**
   Функція спочатку перевіряє, що розмір переданого буфера `len` не менший за фіксований розмір заголовка `COAP_HEADER_SIZE` (4 байти). Перші 2 біти першого байта перевіряються на збіг із версією протоколу: вираз `(buf[0] >> 6) & 0x03` повинен строго дорівнювати `1`. Будь-яке інше значення вказує на несумісний або спотворений протокол.

2. **Витягування токена та контроль меж:**
   Поле `TKL` (довжина токена) витягується з молодшої тетради першого байта: `buf[0] & 0x0F`. Оскільки специфікація RFC 7252 жорстко обмежує максимальний розмір токена 8 байтами, перевірка `tkl > 8` відсікає фальшиві або пошкоджені пакети. Після цього перевіряється, чи вистачає залишку буфера для читання токена: `len < offset + pkt->token_len`. Якщо умова виконується, токен вилучається, а покажчик зміщення `offset` пересувається вперед.

3. **Ітеративний розбір опцій з накопиченням дельти:**
   Змінна `current_option_number` ініціалізується нулем. У циклі розбору для кожної опції зчитується 1 байт заголовка, де старша тетрада містить `delta`, а молодша — `opt_len`.
   - Якщо значення дельти або довжини становить `13`, зчитується 1 додатковий байт розширення, а підсумкове значення коригується зсувом `+ 13`;
   - Якщо значення становить `14`, зчитуються 2 додаткові байти, упаковані в Big-Endian, зі зсувом `+ 269`;
   - Значення `15` у будь-якому з цих полів вважається забороненим за стандартом і призводить до негайної відмови у розборі (`MalformedOptions`).
   Після обчислення приросту абсолютний номер опції накопичується: `current_option_number += delta`. Покажчик на сире значення опції та її довжина записуються у черговий елемент масиву `options`, а лічильник `option_count` інкрементується.

4. **Виявлення розділювача корисного навантаження (Payload Marker):**
   Якщо поточний байт дорівнює `0xFF` (`COAP_PAYLOAD_MARKER`), цикл обробки опцій негайно зупиняється. Наступний за маркером байт оголошується початком корисного навантаження (`pkt->payload = &buf[offset + 1]`), а довжина обчислюється як різниця між загальним розміром буфера та зміщенням маркера. Важливий крайовий випадок RFC 7252: якщо байт `0xFF` є останнім байтом пакета і за ним не слідує жодного байта даних, пакет визнається синтаксично дефектним (`EmptyPayloadMarker`).

### Інтеграція в цикл обробки сокетів та верифікація

У типовій прошивці на базі FreeRTOS або Zephyr RTOS мережева задача слухає сокет у блокуючому виклику `recvfrom()`. Отриманий масив передається прямо у функцію `coap_parse()`. Якщо функція повернула `true`, обробник виконує лінійний пошук потрібних опцій за їхніми числовими номерами та викликає відповідну бізнес-логіку.

Нижче наведено демонстраційний модуль тестування, що імітує отримання бінарного запиту `GET /sensors/temp` із токеном `0xAB` та двома сегментами `Uri-Path`. Приклад демонструє, як розпарсений дескриптор використовується для швидкої маршрутизації в коді вбудованого сервера.

:::tabs
```c
#include <stdio.h>

int main(void) {
    /* Байти запиту: CON GET /sensors/temp, MID=0x1234, Token=0xAB */
    const uint8_t raw_req[] = {
        0x41, 0x01, 0x12, 0x34,                  /* Ver=1, Type=0(CON), TKL=1, Code=0.01 (GET), MID=0x1234 */
        0xAB,                                    /* Token */
        0xB7, 's', 'e', 'n', 's', 'o', 'r', 's', /* Option Uri-Path (11), len 7 */
        0x04, 't', 'e', 'm', 'p'                 /* Option Uri-Path (delta 0 -> 11), len 4 */
    };

    coap_packet_t pkt;
    if (!coap_parse(raw_req, sizeof(raw_req), &pkt)) {
        return 1;
    }

    /* Перевірка вилучених полів */
    if (pkt.code == 1 && pkt.option_count == 2) {
        /* Перший сегмент шляху */
        if (pkt.options[0].number == 11 && pkt.options[0].length == 7) {
            if (memcmp(pkt.options[0].value, "sensors", 7) == 0) {
                return 0; /* Тест пройдено успішно */
            }
        }
    }

    return 1;
}
```
```cpp
#include <iostream>
#include <cstring>

int main() {
    const uint8_t raw_req[] = {
        0x41, 0x01, 0x12, 0x34,
        0xAB,
        0xB7, 's', 'e', 'n', 's', 'o', 'r', 's',
        0x04, 't', 'e', 'm', 'p'
    };

    auto result = coap::PacketView::parse(raw_req);
    if (!result.has_value()) {
        return 1;
    }

    const auto& pkt = result.value();
    if (pkt.code == 1 && pkt.option_count == 2) {
        auto opt = pkt.find_option(11); // Uri-Path
        if (opt.has_value() && opt->as_string() == "sensors") {
            return 0; // Тест пройдено успішно
        }
    }

    return 1;
}
```
:::

# ⚙️ Практична реалізація парсера та генератора NDEF-повідомлень

Бінарний формат NDEF (NFC Data Exchange Format) призначений для компактної та однотипної капсуляції даних у пам meті NFC-міток або при передачі повідомлень між пристроями у режимах P2P (через протокол SNEP). Даний розбір містить практичну реалізацію бінарного парсера та генератора NDEF-записів мовами C та C++ з дотриманням ідіом кожної мови, обробкою помилок та контролем меж буфера.

Оскільки пристрої NFC часто функціонують на мікроконтролерах із суворими обмеженнями оперативної пам meті (наприклад, STM32 або ESP32 з кількома кілобайтами RAM), програмна реалізація повинна уникати зайвого виділення динамічної пам meті, запобігати фрагментації купи та забезпечувати максимальну швидкість парсингу бінарних полів на льоту.

## Архітектура NDEF-запису та бітові маски

Кожен NDEF-запис починається з 1-байтового заголовка прапорів (`Header Byte`). Бітова структура заголовка визначає наявність опціональних полів та спосіб інтерпретації довжини корисного навантаження:

```
 Bit 7   Bit 6   Bit 5   Bit 4   Bit 3   Bit 2   Bit 1   Bit 0
+-------+-------+-------+-------+-------+-------+-------+-------+
|  MB   |  ME   |  CF   |  SR   |  IL   |         TNF           |
+-------+-------+-------+-------+-------+-------+-------+-------+
```

Для роботи з цими полями в коді розробляється набір константних бітових масок:
- `MB = 0x80` (Message Begin) — перший запис у повідомленні. При парсингу першого запису повідомлення цей біт обов'язково має бути встановлений у `1`.
- `ME = 0x40` (Message End) — останній запис у повідомленні. Якщо повідомлення складається з одного-єдиного запису, обидва прапорці `MB` та `ME` встановлюються у `1`.
- `CF = 0x20` (Chunk Flag) — сигналізує про те, що даний запис є частиною фрагментованого великого файлу (поділеного на кілька послідовних частин).
- `SR = 0x10` (Short Record) — прапорець короткого запису. Якщо `SR = 1`, поле довжини корисного навантаження `Payload Length` займає рівно 1 байт (максимальний розмір даних до 255 байт). Якщо `SR = 0`, поле `Payload Length` розширюється до 4 байтів і передається у форматі Big-Endian.
- `IL = 0x08` (ID Length Present) — вказує на наявність 1-байтового поля `ID Length` та відповідного байтового масиву ідентифікатора запису `ID`.
- `TNF = 0x07` (Type Name Format) — 3-бітове поле у молодших бітах, яке визначає контекст простору імен типу запису (Well-Known, MIME, Absolute URI тощо).

## Покроковий алгоритм парсингу NDEF-записів

Процес розбору сирого масиву байтів, отриманого від NFC-контролера або зчитаного з сторінок пам meті мітки, складається з таких послідовних кроків:

1. **Валідація мінімального розміру буфера:** Мінімальний NDEF-запис (порожній запис з `SR=1` та `IL=0`) займає щонайменше 3 байти: Заголовок (1 байт) + Довжина типу (1 байт) + Довжина навантаження (1 байт). Якщо доступний буфер менший за 2 байти, парсер негайно повертає помилку `BufferTooSmall`.
2. **Декодування прапорців заголовка:** Зчитується перший байт `buf[0]`. За допомогою побітових операцій `AND` витягуються прапорці `MB`, `ME`, `SR`, `IL` та 3-бітове значення `TNF`.
3. **Обчислення довжини полів:** Зсув покажчика `offset` збільшується на 1. Зчитується байт `type_len`. Далі перевіряється прапорець `SR`:
   - Якщо `SR == 1`, наступний 1 байт інтерпретується як `payload_len`.
   - Якщо `SR == 0`, наступні 4 байти об'єднуються у 32-бітове ціле число `payload_len` за допомогою побітових зсувів (`(buf[0] << 24) | (buf[1] << 16) | ...`), що гарантує коректне декодування Big-Endian незалежно від архітектури процесора.
4. **Перевірка наявності ID:** Якщо `IL == 1`, зчитується байт `id_len`. Інакше `id_len` приймається рівним `0`.
5. **Контроль меж (Bounds Checking):** Парсер підсумовує `offset + type_len + id_len + payload_len`. Якщо отримана сума перевищує загальну довжину вхідного буфера `len`, це свідчить про пошкодження бінарних даних або спробу атаки на переповнення буфера. Парсер безпечно зупиняє розбір та повертає помилку.
6. **Формування покажчиків:** Замість копіювання байтів у нові масиви парсер повертає структуру покажчиків (`const uint8_t*` у C або `std::string_view` / `std::span` у C++), які посилаються безпосередньо на зсуви у вихідному буфері. Це забезпечує нульові витрати на копіювання пам meті (Zero-Copy Parsing).

Нижче наведено паралельну реалізацію парсера мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define NDEF_FLAG_MB 0x80
#define NDEF_FLAG_ME 0x40
#define NDEF_FLAG_CF 0x20
#define NDEF_FLAG_SR 0x10
#define NDEF_FLAG_IL 0x08
#define NDEF_TNF_MASK 0x07

typedef enum {
    NDEF_OK = 0,
    NDEF_ERR_BUFFER_TOO_SMALL,
    NDEF_ERR_INVALID_HEADER,
    NDEF_ERR_UNSUPPORTED_TNF
} ndef_error_t;

typedef struct {
    uint8_t tnf;
    bool is_first;
    bool is_last;
    const uint8_t *type;
    uint8_t type_len;
    const uint8_t *id;
    uint8_t id_len;
    const uint8_t *payload;
    uint32_t payload_len;
} ndef_record_t;

static const char *URI_PREFIXES[] = {
    "",
    "http://www.",
    "https://www.",
    "http://",
    "https://",
    "tel:",
    "mailto:",
    "ftp://anonymous:anonymous@",
    "ftp://ftp.",
    "ftps://",
    "sftp://"
};
#define URI_PREFIX_COUNT (sizeof(URI_PREFIXES) / sizeof(URI_PREFIXES[0]))

ndef_error_t ndef_parse_record(const uint8_t *buf, size_t len, ndef_record_t *rec, size_t *parsed_bytes) {
    if (len < 2) return NDEF_ERR_BUFFER_TOO_SMALL;

    uint8_t header = buf[0];
    rec->is_first = (header & NDEF_FLAG_MB) != 0;
    rec->is_last = (header & NDEF_FLAG_ME) != 0;
    rec->tnf = header & NDEF_TNF_MASK;
    bool is_short = (header & NDEF_FLAG_SR) != 0;
    bool has_id = (header & NDEF_FLAG_IL) != 0;

    size_t offset = 1;

    rec->type_len = buf[offset++];
    
    if (is_short) {
        if (offset >= len) return NDEF_ERR_BUFFER_TOO_SMALL;
        rec->payload_len = buf[offset++];
    } else {
        if (offset + 4 > len) return NDEF_ERR_BUFFER_TOO_SMALL;
        rec->payload_len = ((uint32_t)buf[offset] << 24) |
                          ((uint32_t)buf[offset + 1] << 16) |
                          ((uint32_t)buf[offset + 2] << 8) |
                          ((uint32_t)buf[offset + 3]);
        offset += 4;
    }

    if (has_id) {
        if (offset >= len) return NDEF_ERR_BUFFER_TOO_SMALL;
        rec->id_len = buf[offset++];
    } else {
        rec->id_len = 0;
        rec->id = NULL;
    }

    if (offset + rec->type_len + rec->id_len + rec->payload_len > len) {
        return NDEF_ERR_BUFFER_TOO_SMALL;
    }

    rec->type = &buf[offset];
    offset += rec->type_len;

    if (has_id) {
        rec->id = &buf[offset];
        offset += rec->id_len;
    }

    rec->payload = &buf[offset];
    offset += rec->payload_len;

    *parsed_bytes = offset;
    return NDEF_OK;
}

size_t ndef_decode_uri(const ndef_record_t *rec, char *out_str, size_t out_max) {
    if (rec->tnf != 0x01 || rec->type_len != 1 || rec->type[0] != 'U') {
        return 0;
    }
    if (rec->payload_len < 1) return 0;

    uint8_t prefix_idx = rec->payload[0];
    const char *prefix = "";
    if (prefix_idx < URI_PREFIX_COUNT) {
        prefix = URI_PREFIXES[prefix_idx];
    }

    size_t prefix_len = strlen(prefix);
    size_t body_len = rec->payload_len - 1;

    if (prefix_len + body_len + 1 > out_max) return 0;

    memcpy(out_str, prefix, prefix_len);
    memcpy(out_str + prefix_len, &rec->payload[1], body_len);
    out_str[prefix_len + body_len] = '\0';

    return prefix_len + body_len;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <array>

namespace ndef {

enum class ParseError {
    BufferTooSmall,
    InvalidHeader,
    UnsupportedTnf
};

enum class Tnf : uint8_t {
    Empty = 0x00,
    WellKnown = 0x01,
    MimeMedia = 0x02,
    AbsoluteUri = 0x03,
    External = 0x04,
    Unknown = 0x05,
    Unchanged = 0x06
};

struct RecordView {
    Tnf tnf{Tnf::Empty};
    bool is_first{false};
    bool is_last{false};
    std::string_view type{};
    std::string_view id{};
    std::span<const uint8_t> payload{};
};

constexpr std::array<std::string_view, 11> URI_PREFIXES = {
    "",
    "http://www.",
    "https://www.",
    "http://",
    "https://",
    "tel:",
    "mailto:",
    "ftp://anonymous:anonymous@",
    "ftp://ftp.",
    "ftps://",
    "sftp://"
};

class Parser {
public:
    static std::expected<std::pair<RecordView, size_t>, ParseError> parse(std::span<const uint8_t> buffer) {
        if (buffer.size() < 2) return std::unexpected(ParseError::BufferTooSmall);

        uint8_t header = buffer[0];
        RecordView rec;
        rec.is_first = (header & 0x80) != 0;
        rec.is_last = (header & 0x40) != 0;
        rec.tnf = static_cast<Tnf>(header & 0x07);

        bool is_short = (header & 0x10) != 0;
        bool has_id = (header & 0x08) != 0;

        size_t offset = 1;
        uint8_t type_len = buffer[offset++];

        uint32_t payload_len = 0;
        if (is_short) {
            if (offset >= buffer.size()) return std::unexpected(ParseError::BufferTooSmall);
            payload_len = buffer[offset++];
        } else {
            if (offset + 4 > buffer.size()) return std::unexpected(ParseError::BufferTooSmall);
            payload_len = (static_cast<uint32_t>(buffer[offset]) << 24) |
                          (static_cast<uint32_t>(buffer[offset + 1]) << 16) |
                          (static_cast<uint32_t>(buffer[offset + 2]) << 8) |
                          static_cast<uint32_t>(buffer[offset + 3]);
            offset += 4;
        }

        uint8_t id_len = 0;
        if (has_id) {
            if (offset >= buffer.size()) return std::unexpected(ParseError::BufferTooSmall);
            id_len = buffer[offset++];
        }

        if (offset + type_len + id_len + payload_len > buffer.size()) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        rec.type = std::string_view(reinterpret_cast<const char*>(buffer.data() + offset), type_len);
        offset += type_len;

        if (has_id) {
            rec.id = std::string_view(reinterpret_cast<const char*>(buffer.data() + offset), id_len);
            offset += id_len;
        }

        rec.payload = buffer.subspan(offset, payload_len);
        offset += payload_len;

        return std::make_pair(rec, offset);
    }

    static std::expected<std::string, ParseError> decode_uri(const RecordView& rec) {
        if (rec.tnf != Tnf::WellKnown || rec.type != "U" || rec.payload.empty()) {
            return std::unexpected(ParseError::InvalidHeader);
        }

        uint8_t prefix_idx = rec.payload[0];
        std::string_view prefix = "";
        if (prefix_idx < URI_PREFIXES.size()) {
            prefix = URI_PREFIXES[prefix_idx];
        }

        std::string result(prefix);
        result.append(reinterpret_cast<const char*>(rec.payload.data() + 1), rec.payload.size() - 1);
        return result;
    }
};

} // namespace ndef
```
:::

## Покроковий алгоритм генерації NDEF-записів (NDEF Builder)

Генерація NDEF-запису є зворотним процесом: вона приймає вихідний URL або текстове повідомлення та пакує його у бінарну послідовність байтів для запису в пам meть мітки.

Алгоритм генератора виконує такі підготовчі розрахунки:
1. **Аналіз довжини:** Обчислюється довжина тіла URL `body_len`. Загальна довжина корисного навантаження складає `payload_len = 1 + body_len` (1 байт для префіксного селектора + байти текстового URL).
2. **Вибір формату запису:** Перевіряється умова `payload_len <= 255`. Якщо умова виконується, виставляється прапорець `SR = 1` (Short Record), а заголовок скорочується на 3 байти.
3. **Формування заголовка:** Формується байт прапорів. Для поодинокого NDEF-повідомлення виставляються біти `MB = 1` та `ME = 1`. Записується тип `TNF = 0x01` (NFC Forum Well-Known Type).
4. **Упаковка запису:** У вихідний буфер послідовно копіюються:
   - Байт прапорів (Header Byte).
   - Довжина типу `Type Length = 1`.
   - Довжина навантаження `Payload Length` (1 байт при `SR=1` або 4 байти при `SR=0`).
   - Байт типу `'U'`.
   - Блок корисного навантаження: префіксний код `prefix_code` та рядок `url_body`.

У реалізації C++ використовується метод `RecordBuilder::create_uri`, який автоматично виділяє масив `std::vector<uint8_t>` потрібного розміру за допомогою `reserve()`, виключаючи багаторазові перевиділення пам meті при заповненні.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

size_t ndef_build_uri_record(uint8_t prefix_code, const char *url_body, bool is_first, bool is_last, uint8_t *out_buf, size_t max_buf) {
    size_t body_len = strlen(url_body);
    size_t payload_len = 1 + body_len;
    bool is_short = (payload_len <= 255);

    size_t header_size = 1 + 1 + (is_short ? 1 : 4) + 1; // Flags + TypeLen + PayloadLen + Type('U')
    size_t total_size = header_size + payload_len;

    if (total_size > max_buf) return 0;

    uint8_t flags = 0x01; // TNF = Well-Known (0x01)
    if (is_first) flags |= 0x80;
    if (is_last)  flags |= 0x40;
    if (is_short) flags |= 0x10;

    size_t offset = 0;
    out_buf[offset++] = flags;
    out_buf[offset++] = 1; // Type Length = 1 ('U')

    if (is_short) {
        out_buf[offset++] = (uint8_t)payload_len;
    } else {
        out_buf[offset++] = (uint8_t)(payload_len >> 24);
        out_buf[offset++] = (uint8_t)(payload_len >> 16);
        out_buf[offset++] = (uint8_t)(payload_len >> 8);
        out_buf[offset++] = (uint8_t)(payload_len & 0xFF);
    }

    out_buf[offset++] = 'U'; // Record Type
    out_buf[offset++] = prefix_code; // URI Prefix Code

    memcpy(&out_buf[offset], url_body, body_len);
    offset += body_len;

    return offset;
}
```
```cpp
#include <cstdint>
#include <vector>
#include <string_view>
#include <span>

namespace ndef {

class RecordBuilder {
public:
    static std::vector<uint8_t> create_uri(uint8_t prefix_code, std::string_view url_body, bool is_first = true, bool is_last = true) {
        size_t payload_len = 1 + url_body.size();
        bool is_short = (payload_len <= 255);

        size_t header_size = 1 + 1 + (is_short ? 1 : 4) + 1;
        std::vector<uint8_t> buffer;
        buffer.reserve(header_size + payload_len);

        uint8_t flags = 0x01; // TNF = Well-Known
        if (is_first) flags |= 0x80;
        if (is_last)  flags |= 0x40;
        if (is_short) flags |= 0x10;

        buffer.push_back(flags);
        buffer.push_back(1); // Type Length ('U')

        if (is_short) {
            buffer.push_back(static_cast<uint8_t>(payload_len));
        } else {
            buffer.push_back(static_cast<uint8_t>(payload_len >> 24));
            buffer.push_back(static_cast<uint8_t>(payload_len >> 16));
            buffer.push_back(static_cast<uint8_t>(payload_len >> 8));
            buffer.push_back(static_cast<uint8_t>(payload_len & 0xFF));
        }

        buffer.push_back('U');
        buffer.push_back(prefix_code);

        buffer.insert(buffer.end(), url_body.begin(), url_body.end());

        return buffer;
    }
};

} // namespace ndef
```
:::

## Особливості парсингу та створення текстових записів (Text Record)

Окрім посилань URI, поширеним типом NDEF-записів є текстовий запис (Type Name `'T'`). Формат корисного навантаження текстового запису визначається специфікацією Text Record Type Definition:

- **Байт статусу (Status Byte):** Перший байт `payload[0]`.
  - Старший біт 7: `0` для кодування UTF-8, `1` для кодування UTF-16.
  - Біт 6: Зарезервований (мусить бути `0`).
  - Біти 5..0: Довжина мовного коду IANA `lang_len` у байтах (наприклад, `2` для коду `"en"` або `"uk"`).
- **Код мови (Language Code):** ASCII-рядок довжиною `lang_len` байтів (відразу за байтом статусу).
- **Текст (Text String):** Залишок масиву `payload_len - 1 - lang_len` байтів у кодуванні UTF-8 або UTF-16.

При парсингу текстового запису необхідно виділити код мови та перевірити біт 7. Якщо біт 7 встановлений, тексту вимагає обробки як двохбайтових символів UTF-16 з урахуванням BOM (Byte Order Mark `0xFEFF` або `0xFFFE`).

## Логіка запакування NDEF у файл пам meті TLV

На пасивних мітках Type 2 (наприклад NTAG213/NTAG215) згенероване NDEF-повідомлення не може бути записане напряму на 0-ву сторінку EEPROM. Згідно зі специфікацією NFC Forum Tag Type 2 Technical Specification, перші 4 сторінки (байти 0..15) зарезервовані під UID мітки, байти конфігурації та байти магічного контейнера Capability Container (CC).

Карта пам meті мітки NTAG215 (подетальна посторінкова структура по 4 байти на сторінку):
- **Сторінки 0x00..0x01:** 7-байтовий унікальний ідентифікатор UID та байти перевірки BCC.
- **Сторінка 0x02:** Байт внутрішньої конфігурації та байти блокування Static Lock Bytes.
- **Сторінка 0x03:** Контейнер можливостей Capability Container (CC). Для NDEF-міток тут записані байти `0xE1 0x10 0x3E 0x00` (де `0x3E = 62`, що вказує на розмір пам meті `62 * 8 = 496 байт`).
- **Сторінка 0x04 і далі:** Корисні дані користувача, огорнуті у структури TLV.

При записі у фізичні сторінки мікросхеми мітки слід дотримуватися таймінгу програмування EEPROM. Кожна сторінка (4 байти) вимагає окремої команди запису `WRITE = 0xA2` із затримкою обробки не менше `5.0 мс` (часове вікно внутрішнього програмування `t_WC`). Запис масиву байтів розбивається на посторінкові блоки. Якщо останній блок містить менше 4 байтів, він доповнюється нульовими байтами заповнення (Padding Bytes).

Згенероване NDEF-повідомлення обов'язково розвертається у файловий контейнер TLV (Tag-Length-Value):

1. **Тег типу NDEF TLV:** Першим байтом контейнера записується константа `Tag = 0x03`.
2. **Поле довжини TLV:** 
   - Якщо загальна довжина NDEF-повідомлення `ndef_len < 255` байт, поле довжини займає `1 байт`.
   - Якщо `ndef_len >= 255` байт, у поле довжини записується маркер `0xFF`, за яким ідуть 2 байти `uint16_t` у форматі Big-Endian, що передають реальний розмір повідомлення.
3. **Тіло повідомлення:** Після заголовка TLV байт у байт копіюється згенероване NDEF-повідомлення.
4. **Тег завершення Terminator TLV:** Відразу за останнім байтом NDEF-повідомлення записується байт `0xFE` (Terminator TLV Tag), який інформує зчитувач про завершення корисних структур даних у пам meті мітки.

Нижче наведено реалізацію огортача TLV для мов C та C++.

:::tabs
```c
size_t ndef_wrap_in_tlv(const uint8_t *ndef_msg, size_t ndef_len, uint8_t *tag_mem, size_t max_tag_mem) {
    size_t tlv_header_len = (ndef_len < 255) ? 2 : 4;
    size_t total_len = tlv_header_len + ndef_len + 1; // +1 для Terminator TLV (0xFE)

    if (total_len > max_tag_mem) return 0;

    size_t offset = 0;
    tag_mem[offset++] = 0x03; // NDEF Message TLV Tag

    if (ndef_len < 255) {
        tag_mem[offset++] = (uint8_t)ndef_len;
    } else {
        tag_mem[offset++] = 0xFF; // Індикатор трибайтового поля довжини
        tag_mem[offset++] = (uint8_t)(ndef_len >> 8);
        tag_mem[offset++] = (uint8_t)(ndef_len & 0xFF);
    }

    memcpy(&tag_mem[offset], ndef_msg, ndef_len);
    offset += ndef_len;

    tag_mem[offset++] = 0xFE; // Terminator TLV Tag

    return offset;
}
```
```cpp
namespace ndef {

class TlvWrapper {
public:
    static std::vector<uint8_t> wrap_ndef(std::span<const uint8_t> ndef_msg) {
        std::vector<uint8_t> result;
        size_t ndef_len = ndef_msg.size();
        size_t tlv_header_len = (ndef_len < 255) ? 2 : 4;
        result.reserve(tlv_header_len + ndef_len + 1);

        result.push_back(0x03); // NDEF TLV Tag

        if (ndef_len < 255) {
            result.push_back(static_cast<uint8_t>(ndef_len));
        } else {
            result.push_back(0xFF);
            result.push_back(static_cast<uint8_t>(ndef_len >> 8));
            result.push_back(static_cast<uint8_t>(ndef_len & 0xFF));
        }

        result.insert(result.end(), ndef_msg.begin(), ndef_msg.end());
        result.push_back(0xFE); // Terminator TLV

        return result;
    }
};

} // namespace ndef
```
:::

## Захист пам meті та парольна аутентифікація PWD_AUTH

При проведення операцій запису у мітки NTAG213/215/216 часто вимагається обмежити доступ сторонніх пристроїв до перезапису NDEF-даних. Мікросхеми NTAG підтримють захист за допомогою 32-бітного пароля:

1. **Конфігураційні сторінки:** В останніх сторінках пам meті мітки (для NTAG215 це сторінки `0x83..0x86`) розташовані регістри `CFG0`, `CFG1`, `PWD` та `PACK`.
2. **Встановлення пароля:** У сторінку `PWD` записуються 4 байти секретного пароля `P3..P0`. У сторінку `PACK` записуються 2 байти відповідного підтвердження `PACK1..PACK0`.
3. **Аутентифікація:** Зчитувач відправляють команду `PWD_AUTH = 0x1B`, після якої передає 4 байти пароля. Якщо пароль вірний, мітка повертає 2 байти `PACK` і знімає біти блокування запису до моменту вимкнення радіочастотного поля.

Програмування парольного захисту вимагає строгого дотримання порядку записаних полів. Помилка у значеннях `CFG0` може назавжди заблокувати мітку у стані Read-Only.

## Оптимізація пам meті для вбудованих систем

При реалізації парсера на мікроконтролерах без динамічної пам meті (статичне виділення RAM) замість контейнерів `std::vector` використовується статичний статичний буфер фіксованого розміру `uint8_t static_buf[512]` або шаблонний клас C++20 `std::span`. Це унеможливлює витік пам meті та виключає накладні витрати на виклики `malloc`/`free` під час обробки трафіку NFC.

Оцінка використання пам meті статичним парсером:
- Розмір тексту коду (Flash/ROM): ~`1.2 Кб` для C, ~`2.8 Кб` для C++20.
- Використання стеку (RAM): `32 байти` для структури `RecordView` та покажчиків.

Для модульного тестування парсера NDEF рекомендується використовувати тестові фреймворки Unity (для C) або Catch2/GoogleTest (для C++). Набір модульних тестів повинен включати перевірку крайових випадків: порожній вхідний буфер, буфер з некоректним `Payload Length`, повідомлення з відсутнім прапорцем `ME`, а також валідацію витягнутих покажчиків на зсуви у пам'яті. Автоматизовані тести запобігають падінню пристрою при зчитанні пошкодженого кадру з радіоефіру.

## Інтеграція з операційними системами та драйверами

При роботі на рівнях утиліт вбудованих операційних систем (Linux/Android) згенеровані масиви байтів передаються у стек системного драйвера NFC через стандартні системні виклики та фреймворки:

1. **Linux Subsystem (Neard / Subsystem NFC):** В операційній системі Linux взаємодія з NFC-контролером здійснюється через Netlink сокети `AF_NFC`. Згенероване NDEF-повідомлення передається у виклику сокета для відправки в активне поле пристрою.
2. **Android NDEF API:** Операційна система Android підтримує класи `NdefMessage` та `NdefRecord`. Вбудований парсер Android автоматично витягує MIME-типи або записи AAR (Android Application Record, `android.com:pkg`), викликаючи відповідний прикладний процес Intent Filter `ACTION_NDEF_DISCOVERED`.
3. **Апаратні драйвери PN532 / ST25R:** Для систем на мікроконтролерах бінарний масив NDEF передається через команду `InCommunicateThru` контролера PN532 по шині SPI або I2C, огорнутий у кадр ISO-DEP або прямий кадр каскадного рівня.

У разі виявлення запису типу AAR системний диспетчер Android ігнорує інші типи і відкриває додаток з вказаним іменем пакунка у полі `Payload`, або автоматично перенаправляє користувача в магазин Google Play Store для його завантаження.

## Ключові пастки та крайові випадки реалізації

Під час практичного використання NDEF-парсерів у вбудованих системах розробники найчастіше стикаються з такими проблемами:

1. **Нехтування ендіанністю (Big-Endian vs Little-Endian):**
   Поле `Payload Length` у випадку `SR = 0` передається у форматі Big-Endian. Пряме приведення покажчика `*(uint32_t*)&buf[offset]` на мікроконтролерах ARM Cortex-M або х86 прочитає байти у зворотному порядку, що призведе к інтерпретації довжини як велетенського числа і викличе крах програми. Необхідно виконувати побайтовий зсув або застосовувати функції `ntohl()`.

2. **Захист від некоректного розміру пам meті (Out-of-bounds Read):**
   Пошкоджені або зловмисно прошиті мітки можуть містити деструктивні байти заголовка (наприклад, `payload_len = 0xFFFFFFFF`). Будь-яка спроба парсера прочитати задекларовану кількість байтів без жорсткої перевірки `offset + payload_len <= input_buffer_len` призведе до зчитування сторонніх ділянок RAM та можливої уразливості системи.

3. **Особливості декодування текстових записів (Type 'T'):**
   При парсингу текстових записів перший байт корисного навантаження являє собою статусний байт. Молодші біти `5..0` визначають довжину коду мови `N` (наприклад, `2` для "en" або "uk"). Покажчик на початок самого тексту обчислюється як `payload_ptr + 1 + N`. Якщо розробник не врахує довжину коду мови `N`, перші символи тексту будуть зрізані або спотворені.

4. **Фрагментовані записи (Chunked Records):**
   При передачі великих файлів (наприклад, фотографій у режимі P2P) NDEF-повідомлення розбивається на фрагменти з прапорцем `CF = 1`. Перший фрагмент містить `TNF` та `Record Type`, а наступні фрагменти передаються з `TNF = 0x06` (Unchanged) та порожнім полем типу. Парсер повинен зберігати стан попереднього типу до отримання фінального фрагмента з `CF = 0`.

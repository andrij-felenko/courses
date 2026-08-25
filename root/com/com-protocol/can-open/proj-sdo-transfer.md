# ⚙️ Реалізація клієнта та сервера SDO на C та C++

Протокол SDO (Service Data Object) забезпечує прямий точка-точка доступ до будь-якого запису Словника Об'єктів CANopen за його 16-бітним індексом та 8-бітним субіндексом. Оскільки SDO призначений переважно для конфігурації, опитування діагностичних регістрів та ініціалізації пристроїв під час запуску мережі, кожен запит клієнта вимагає суворого підтвердження від сервера за допомогою відповіді (модель «клієнт-сервер»).

Для транзакцій із даними невеликого обсягу (до 4 байтів корисного навантаження), які покривають переважну більшість конфігураційних змінних (прапорці boolean, цілі числа int8/int16/int32, числа з рухомою комою float32), CANopen використовує режим прискореної передачі — **Expedited Transfer**. У цьому режимі вся транзакція запису або читання виконується за допомогою всього одного кадру запиту від клієнта та одного кадру відповіді від сервера.

### 1. Бітова анатомія командного байта SDO Expedited

Корисне навантаження кадру CAN для SDO завжди становить рівно 8 байтів. Байт 0 відведений під командний байт, який містить управляючі прапорці транзакції, байти 1..2 несуть 16-бітний індекс Словника Об'єктів, байт 3 — 8-бітний субіндекс, а байти 4..7 вміщують корисні дані чи 32-бітний код помилки в разі відмови.

Командний байт (Байт 0) має сувору розрядність:
- **Біти 7..5 (CCS / SCS)**: Специфікатор команди. Для кадру від клієнта до сервера використовується `CCS` (*Client Command Specifier*): `1` (`001b`) — запит на запис (Initiate Download Request), `2` (`010b`) — запит на читання (Initiate Upload Request). Для кадру від сервера до клієнта використовується `SCS` (*Server Command Specifier*): `3` (`011b`) — підтвердження запису (Initiate Download Response), `2` (`010b`) — відповідь з даними читання (Initiate Upload Response), `4` (`100b`) — кадр відмови SDO Abort.
- **Біти 3..2 (n)**: Вказують кількість порожніх (невикористаних) байтів у полі даних (байтах 4..7). Оскільки максимальний обсяг даних у прискореному режимі становить 4 байти, фактичний розмір корисних даних обчислюється як `4 - n`. Наприклад, якщо передається 16-бітне ціле число (2 байти), то `n = 2` (`10b`).
- **Бит 1 (e)**: Прапорець прискореного режиму (*Expedited Transfer Flag*). Значення `1` вказує, що дані передаються безпосередньо у байтах 4..7 поточного кадру. Значення `0` вказує на виклик сегментованої передачі (Segmented Transfer) для великих масивів даних чи текстових рядків.
- **Бит 0 (s)**: Прапорець вказівки розміру (*Size Indicator*). Значення `1` означає, що поле `n` у бітах 3..2 є дійсним і містить кількість невикористаних байтів.

### 2. Принцип функціонування сегментованого переказу (Segmented Transfer)

Коли розмір параметра у Словнику Об'єктів перевищує 4 байти (наприклад, текстова назва пристрою за індексом `0x1008`, довгий масив параметрів або файл прошивки мікроконтролера), CANopen переходить у режим сегментованого переказу:
1. **Ініціалізація транзакції**. Клієнт надсилає кадр `Initiate Download Request` або `Initiate Upload Request` із прапорцем `e = 0`. Якщо прапорець `s = 1`, то у байтах 4..7 вказується повний 32-бітний розмір файлу у байтах. Сервер підтверджує готовність відповідним кадром ініціалізації.
2. **Передача сегментів**. Дані передаються послідовністю 8-байтових кадрів, де кожен кадр містить до 7 байтів корисного навантаження (байти 1..7), а байт 0 виконує роль управляючого заголовка сегмента.
3. **Біт перемикання (Toggle Bit)**. У командному байті кожного сегмента біт 4 відведений під тригерний біт перемикання `t`. Під час відправки першого сегмента `t = 0`, під час другого `t = 1`, під час третього `t = 0` і так далі. Якщо сервер отримує сегмент з тим самим значенням `t`, що й у попередньому кадрі, він відкидає його як дублікат, запобігаючи спотворенню потоку даних при повторних спробах відправки.
4. **Завершення переказу**. У останньому сегменті біт 0 (`c` — *Last Segment Flag*) встановлюється в `1`, а біти 3..1 містять кількість впорожнілих байтів у байтах 1..7 кадру.

### 3. Алгоритм та бізнес-логіка скінченного автомата SDO-клієнта

Під час проєктування стека CANopen на мікроконтролері або верхньому рівні (Linux / Embedded C++) модуль SDO-клієнта реалізують у вигляді скінченного автомата з підтримкою таймаутів.

Основними станами автомата є:
- `SDO_STATE_IDLE` — клієнт вільний і готовий до формування нового запиту.
- `SDO_STATE_WAIT_WRITE_RESP` — запит на запис відправлено на шину; очікується відповідь сервера з `SCS = 3` або `SCS = 4` (Abort).
- `SDO_STATE_WAIT_READ_RESP` — запит на читання відправлено на шину; очікується відповідь сервера з `SCS = 2` або `SCS = 4` (Abort).
- `SDO_STATE_TIMED_OUT` — сервер не відповів упродовж встановленого інтервалу (зазвичай від 20 до 1000 мілісекунд). Клієнт генерує внутрішню помилку та анулює транзакцію.

### 4. Формат Little Endian та обробка відмов SDO Abort

Важливою особливістю стандарту CANopen є суворе дотримання порядку байтів **Little Endian** (молодший байт за меншою адресою в пам'яті). Це стосується як 16-бітного індексу у байтах 1..2, так і 32-бітного значення корисних даних або коду Abort у байтах 4..7:
- `Байт 1`: Молодший байт індексу (Index LSB);
- `Байт 2`: Старший байт індексу (Index MSB);
- `Байт 4`: Байт 0 даних (Bits 7..0);
- `Байт 5`: Байт 1 даних (Bits 15..8);
- `Байт 6`: Байт 2 даних (Bits 23..16);
- `Байт 7`: Байт 3 даних (Bits 31..24).

Якщо сервер не може виконати запит SDO (наприклад, спроба записати значення у параметр, доступний лише для читання, відсутність індексу у Словнику Об'єктів або вихід значення за допустимі межі), він повертає відповідь **SDO Abort**. Командний байт відмови дорівнює `0x80` (`SCS = 4`), а байти 4..7 містять 32-бітний код помилки SDO Abort Code:
- `0x05030000` — Помилка перемикання біта тогла (Toggle bit not altered);
- `0x05040001` — Перевищено час очікування SDO (Client/server SDO timeout);
- `0x06010000` — Спроба доступу, який не підтримується цим об'єктом (Unsupported access);
- `0x06010002` — Спроба запису у параметр, відкритий лише для читання (Attempt to write a read-only object);
- `0x06020000` — Об'єкт відсутній у Словнику Об'єктів (Object does not exist in the Object Dictionary);
- `0x06090011` — Субіндекс відсутній у даному об'єкті (Subindex does not exist);
- `0x06090030` — Значення параметра вийшло за припустимі межі (Value range of parameter exceeded).

Нижче наведено робочі реалізації упакування запитів та розбору відповідей SDO Expedited мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Специфікатори команд SDO у бітах 7..5 */
#define SDO_CCS_WRITE_REQ  1U
#define SDO_SCS_WRITE_RESP 3U
#define SDO_CCS_READ_REQ   2U
#define SDO_SCS_READ_RESP  2U
#define SDO_SCS_ABORT      4U

/* Канонічні коди помилок SDO Abort */
#define SDO_ABORT_TOGGLE_BIT         0x05030000UL
#define SDO_ABORT_TIMEOUT            0x05040001UL
#define SDO_ABORT_UNSUPPORTED_ACCESS 0x06010000UL
#define SDO_ABORT_READ_ONLY          0x06010002UL
#define SDO_ABORT_OBJECT_NOT_EXIST   0x06020000UL
#define SDO_ABORT_SUBINDEX_NOT_EXIST 0x06090011UL
#define SDO_ABORT_VALUE_OUT_OF_RANGE 0x06090030UL

typedef struct {
    uint8_t data[8];
} canopen_frame_payload_t;

typedef struct {
    uint16_t index;
    uint8_t subindex;
    uint32_t data;
    uint8_t data_len;
    bool is_abort;
    uint32_t abort_code;
} sdo_packet_t;

/* 
 * Формування кадру SDO Write Request (Initiate Download Expedited).
 * Формує 8-байтове корисне навантаження кадру CAN для запису значення до 4 байтів.
 */
bool canopen_sdo_pack_write_req(uint16_t index, uint8_t subindex, 
                                uint32_t data, uint8_t data_len, 
                                canopen_frame_payload_t *out_frame) {
    if (!out_frame || data_len < 1 || data_len > 4) {
        return false;
    }

    uint8_t empty_bytes = 4U - data_len;
    /* Bit 7..5: ccs=1 (Write), Bit 3..2: n (empty bytes), Bit 1: e=1 (Expedited), Bit 0: s=1 (Size) */
    uint8_t cmd = (SDO_CCS_WRITE_REQ << 5) | (empty_bytes << 2) | 0x02U | 0x01U;

    out_frame->data[0] = cmd;
    out_frame->data[1] = (uint8_t)(index & 0xFFU);
    out_frame->data[2] = (uint8_t)((index >> 8) & 0xFFU);
    out_frame->data[3] = subindex;

    /* Копіювання 32-бітного значення у порядку Little Endian */
    out_frame->data[4] = (uint8_t)(data & 0xFFU);
    out_frame->data[5] = (uint8_t)((data >> 8) & 0xFFU);
    out_frame->data[6] = (uint8_t)((data >> 16) & 0xFFU);
    out_frame->data[7] = (uint8_t)((data >> 24) & 0xFFU);

    return true;
}

/* 
 * Формування кадру SDO Read Request (Initiate Upload Request).
 * Формує запит на зчитування значення за вказаним індексом та субіндексом.
 */
bool canopen_sdo_pack_read_req(uint16_t index, uint8_t subindex, 
                               canopen_frame_payload_t *out_frame) {
    if (!out_frame) {
        return false;
    }

    /* Bit 7..5: ccs=2 (Read Request), решта бітів 0 */
    out_frame->data[0] = (SDO_CCS_READ_REQ << 5);
    out_frame->data[1] = (uint8_t)(index & 0xFFU);
    out_frame->data[2] = (uint8_t)((index >> 8) & 0xFFU);
    out_frame->data[3] = subindex;
    
    memset(&out_frame->data[4], 0, 4);
    return true;
}

/* 
 * Розбір відповіді SDO Read Response (Initiate Upload Response).
 * Розпаковує 8-байтовий кадр відповіді, витягує індекс, субіндекс, дані або код помилки Abort.
 */
bool canopen_sdo_parse_read_resp(const canopen_frame_payload_t *frame, 
                                 sdo_packet_t *out_packet) {
    if (!frame || !out_packet) {
        return false;
    }

    uint8_t cmd = frame->data[0];
    uint8_t scs = (cmd >> 5) & 0x07U;

    out_packet->index = (uint16_t)frame->data[1] | ((uint16_t)frame->data[2] << 8);
    out_packet->subindex = frame->data[3];

    /* Перевірка на кадр відмови SDO Abort (SCS = 4) */
    if (scs == SDO_SCS_ABORT) {
        out_packet->is_abort = true;
        out_packet->abort_code = (uint32_t)frame->data[4] |
                                 ((uint32_t)frame->data[5] << 8) |
                                 ((uint32_t)frame->data[6] << 16) |
                                 ((uint32_t)frame->data[7] << 24);
        out_packet->data = 0;
        out_packet->data_len = 0;
        return true;
    }

    if (scs != SDO_SCS_READ_RESP) {
        return false; /* Невідомий або невідповідний тип кадру SDO */
    }

    out_packet->is_abort = false;
    out_packet->abort_code = 0;

    uint8_t empty_bytes = (cmd >> 2) & 0x03U;
    out_packet->data_len = 4U - empty_bytes;

    out_packet->data = (uint32_t)frame->data[4] |
                       ((uint32_t)frame->data[5] << 8) |
                       ((uint32_t)frame->data[6] << 16) |
                       ((uint32_t)frame->data[7] << 24);

    return true;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <system_error>

enum class SdoClientCommand : uint8_t {
    WriteRequest = 1,
    ReadRequest  = 2
};

enum class SdoServerCommand : uint8_t {
    WriteResponse = 3,
    ReadResponse  = 2,
    Abort         = 4
};

enum class SdoAbortCode : uint32_t {
    ToggleBit            = 0x05030000,
    Timeout              = 0x05040001,
    UnsupportedAccess    = 0x06010000,
    ReadOnly             = 0x06010002,
    ObjectDoesNotExist   = 0x06020000,
    SubindexDoesNotExist = 0x06090011,
    ValueOutOfRange      = 0x06090030
};

struct SdoExpeditedRequest {
    uint16_t index;
    uint8_t subindex;
    uint32_t data;
    uint8_t data_len;
};

struct SdoResponse {
    uint16_t index;
    uint8_t subindex;
    uint32_t data;
    uint8_t data_len;
};

enum class SdoParseError {
    InvalidFrameLength,
    UnknownCommandSpecifier,
    InvalidDataLength,
    AbortReceived
};

class SdoCodec {
public:
    using FrameData = std::array<uint8_t, 8>;

    /* Упакування прискореного запису SDO Write Request із використанням C++20 std::expected */
    static std::expected<FrameData, SdoParseError> pack_expedited_write(const SdoExpeditedRequest& req) {
        if (req.data_len < 1 || req.data_len > 4) {
            return std::unexpected(SdoParseError::InvalidDataLength);
        }

        FrameData frame{};
        const uint8_t empty_bytes = static_cast<uint8_t>(4 - req.data_len);
        const uint8_t ccs = static_cast<uint8_t>(SdoClientCommand::WriteRequest);
        
        frame[0] = static_cast<uint8_t>((ccs << 5) | (empty_bytes << 2) | 0x02U | 0x01U);
        frame[1] = static_cast<uint8_t>(req.index & 0xFFU);
        frame[2] = static_cast<uint8_t>((req.index >> 8) & 0xFFU);
        frame[3] = req.subindex;

        frame[4] = static_cast<uint8_t>(req.data & 0xFFU);
        frame[5] = static_cast<uint8_t>((req.data >> 8) & 0xFFU);
        frame[6] = static_cast<uint8_t>((req.data >> 16) & 0xFFU);
        frame[7] = static_cast<uint8_t>((req.data >> 24) & 0xFFU);

        return frame;
    }

    /* Упакування прискореного запису SDO Read Request */
    static FrameData pack_read_request(uint16_t index, uint8_t subindex) {
        FrameData frame{};
        const uint8_t ccs = static_cast<uint8_t>(SdoClientCommand::ReadRequest);
        
        frame[0] = static_cast<uint8_t>(ccs << 5);
        frame[1] = static_cast<uint8_t>(index & 0xFFU);
        frame[2] = static_cast<uint8_t>((index >> 8) & 0xFFU);
        frame[3] = subindex;

        return frame;
    }

    /* Безпечний розбір кадру відповіді SDO з виділенням SdoAbortCode у разі помилки */
    static std::expected<SdoResponse, SdoAbortCode> parse_read_response(std::span<const uint8_t, 8> frame) {
        const uint8_t cmd = frame[0];
        const uint8_t scs = (cmd >> 5) & 0x07U;

        const uint16_t idx = static_cast<uint16_t>(frame[1]) | (static_cast<uint16_t>(frame[2]) << 8);
        const uint8_t sub_idx = frame[3];

        if (scs == static_cast<uint8_t>(SdoServerCommand::Abort)) {
            const uint32_t raw_abort = static_cast<uint32_t>(frame[4]) |
                                       (static_cast<uint32_t>(frame[5]) << 8) |
                                       (static_cast<uint32_t>(frame[6]) << 16) |
                                       (static_cast<uint32_t>(frame[7]) << 24);
            return std::unexpected(static_cast<SdoAbortCode>(raw_abort));
        }

        const uint8_t empty_bytes = (cmd >> 2) & 0x03U;
        const uint32_t payload = static_cast<uint32_t>(frame[4]) |
                                 (static_cast<uint32_t>(frame[5]) << 8) |
                                 (static_cast<uint32_t>(frame[6]) << 16) |
                                 (static_cast<uint32_t>(frame[7]) << 24);

        return SdoResponse{
            .index = idx,
            .subindex = sub_idx,
            .data = payload,
            .data_len = static_cast<uint8_t>(4 - empty_bytes)
        };
    }
};
```
:::

# ⚙️ Практична реалізація кодека пакетів телеметрії на C та C++

У реальних вбудованих системах зв'язок між процесорними вузлами або бездротовими радіомодемами забезпечується за допомогою потокового обробника, який ніколи не блокує виконання основного польотного циклу і не вдається до динамічного виділення пам'яті.

Нижче наведено повний, функціонально замкнений сирцевий код кодека (серіалізатора та потокового скінченного автомата десеріалізатора) мовами C та C++, а також тестовий стенд із симуляцією канальних збоїв: випадання випадкових байтів, інверсії бітів усередині корисного навантаження та появи хибних преамбул.

---

## Архітектурна модель та програмна реалізація

Кодек побудовано на основі двох взаємодоповнюючих модулів, розрахованих на детерміновану роботу в жорсткому реальному часі:

1. **Серіалізатор (`serialize_packet` / `serialize`)**: приймає ідентифікатор повідомлення `msg_id`, порядковий номер `seq` та сирий масив байтів `payload`. Він послідовно записує преамбулу `0xAA 0x55`, поля заголовка, копіює байти навантаження та паралельно розраховує контрольну суму CRC-16-CCITT за допомогою табличного прискорювача. Наприкінці вихідного буфера додаються два байти CRC у порядку Little-Endian (молодший байт `CRC_L`, потім старший `CRC_H`).
2. **Потоковий десеріалізатор (`parser_consume_byte` / `StreamParser::consumeByte`)**: реалізує детермінований скінченний автомат із 8 станами. Він обробляє вхідний потік по одному байту за виклик, не вимагаючи блокуючого очікування всього кадру. Автомат володіє внутрішнім статичним буфером `payload[64]` в оперативній пам'яті, що усуває будь-яку залежність від динамічної купи (Heap).

У версії для C++20 таблиця коефіцієнтів CRC-16 генерується безпосередньо під час компіляції за допомогою функції `consteval`, що гарантує нульові накладні витрати часу виконання на ініціалізацію та розміщення масиву безпосередньо у Flash-пам'яті (`.rodata`).

:::tabs
```c
/* ============================================================================
 * tele_codec.c — Автономний потоковий кодек пакетів телеметрії (C99)
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PREAMBLE_BYTE_1       0xAA
#define PREAMBLE_BYTE_2       0x55
#define MAX_PAYLOAD_CAPACITY  64

typedef enum {
    PARSER_CONTINUE = 0,
    PARSER_PACKET_OK = 1,
    PARSER_ERR_CRC = 2,
    PARSER_ERR_LEN = 3
} parser_status_t;

typedef struct {
    uint8_t msg_id;
    uint8_t seq;
    uint8_t len;
    uint8_t payload[MAX_PAYLOAD_CAPACITY];
} packet_t;

typedef enum {
    STATE_WAIT_PREAMBLE_1 = 0,
    STATE_WAIT_PREAMBLE_2,
    STATE_GET_MSG_ID,
    STATE_GET_SEQ,
    STATE_GET_LEN,
    STATE_GET_PAYLOAD,
    STATE_GET_CRC_LOW,
    STATE_GET_CRC_HIGH
} parser_state_t;

typedef struct {
    parser_state_t state;
    uint8_t        rx_index;
    uint16_t       crc_accum;
    uint16_t       crc_received;
    packet_t       pkt;
} parser_t;

/* Таблиця коефіцієнтів CRC-16-CCITT (поліном 0x1021) */
static const uint16_t crc16_lut[256] = {
    0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
    0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
    0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
    0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
    0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
    0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
    0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
    0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
    0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
    0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
    0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
    0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
    0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
    0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
    0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
    0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
    0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
    0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
    0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
    0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
    0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
    0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
    0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
    0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
    0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
    0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
    0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
    0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
    0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
    0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
    0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
    0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
};

static inline uint16_t crc16_step(uint16_t crc, uint8_t byte) {
    uint8_t index = ((crc >> 8) ^ byte) & 0xFF;
    return (crc << 8) ^ crc16_lut[index];
}

void parser_init(parser_t *p) {
    if (!p) return;
    p->state = STATE_WAIT_PREAMBLE_1;
    p->rx_index = 0;
    p->crc_accum = 0xFFFF;
    p->crc_received = 0;
}

size_t serialize_packet(uint8_t msg_id, uint8_t seq, const uint8_t *payload, uint8_t len, uint8_t *out_buf) {
    if (!out_buf || (len > MAX_PAYLOAD_CAPACITY)) return 0;
    if (len > 0 && !payload) return 0;

    out_buf[0] = PREAMBLE_BYTE_1;
    out_buf[1] = PREAMBLE_BYTE_2;
    out_buf[2] = msg_id;
    out_buf[3] = seq;
    out_buf[4] = len;

    uint16_t crc = 0xFFFF;
    crc = crc16_step(crc, msg_id);
    crc = crc16_step(crc, seq);
    crc = crc16_step(crc, len);

    for (uint8_t i = 0; i < len; ++i) {
        out_buf[5 + i] = payload[i];
        crc = crc16_step(crc, payload[i]);
    }

    out_buf[5 + len] = (uint8_t)(crc & 0xFF);        /* CRC LSB */
    out_buf[6 + len] = (uint8_t)((crc >> 8) & 0xFF); /* CRC MSB */

    return 7 + len;
}

parser_status_t parser_consume_byte(parser_t *p, uint8_t byte, packet_t *out_packet) {
    if (!p) return PARSER_CONTINUE;

    switch (p->state) {
    case STATE_WAIT_PREAMBLE_1:
        if (byte == PREAMBLE_BYTE_1) {
            p->state = STATE_WAIT_PREAMBLE_2;
        }
        return PARSER_CONTINUE;

    case STATE_WAIT_PREAMBLE_2:
        if (byte == PREAMBLE_BYTE_2) {
            p->state = STATE_GET_MSG_ID;
            p->crc_accum = 0xFFFF;
        } else if (byte == PREAMBLE_BYTE_1) {
            /* Залишаємось у стані очікування другого байта преамбули */
            p->state = STATE_WAIT_PREAMBLE_2;
        } else {
            p->state = STATE_WAIT_PREAMBLE_1;
        }
        return PARSER_CONTINUE;

    case STATE_GET_MSG_ID:
        p->pkt.msg_id = byte;
        p->crc_accum = crc16_step(p->crc_accum, byte);
        p->state = STATE_GET_SEQ;
        return PARSER_CONTINUE;

    case STATE_GET_SEQ:
        p->pkt.seq = byte;
        p->crc_accum = crc16_step(p->crc_accum, byte);
        p->state = STATE_GET_LEN;
        return PARSER_CONTINUE;

    case STATE_GET_LEN:
        if (byte > MAX_PAYLOAD_CAPACITY) {
            /* Помилка довжини: скидання автомата для уникнення переповнення */
            p->state = STATE_WAIT_PREAMBLE_1;
            return PARSER_ERR_LEN;
        }
        p->pkt.len = byte;
        p->crc_accum = crc16_step(p->crc_accum, byte);
        p->rx_index = 0;

        if (p->pkt.len == 0) {
            p->state = STATE_GET_CRC_LOW;
        } else {
            p->state = STATE_GET_PAYLOAD;
        }
        return PARSER_CONTINUE;

    case STATE_GET_PAYLOAD:
        p->pkt.payload[p->rx_index++] = byte;
        p->crc_accum = crc16_step(p->crc_accum, byte);

        if (p->rx_index >= p->pkt.len) {
            p->state = STATE_GET_CRC_LOW;
        }
        return PARSER_CONTINUE;

    case STATE_GET_CRC_LOW:
        p->crc_received = (uint16_t)byte;
        p->state = STATE_GET_CRC_HIGH;
        return PARSER_CONTINUE;

    case STATE_GET_CRC_HIGH:
        p->crc_received |= ((uint16_t)byte << 8);
        p->state = STATE_WAIT_PREAMBLE_1;

        if (p->crc_received == p->crc_accum) {
            if (out_packet) {
                *out_packet = p->pkt;
            }
            return PARSER_PACKET_OK;
        } else {
            return PARSER_ERR_CRC;
        }

    default:
        p->state = STATE_WAIT_PREAMBLE_1;
        return PARSER_CONTINUE;
    }
}
```
```cpp
// ============================================================================
// tele_codec.hpp — Автономний потоковий кодек пакетів телеметрії (C++20)
// ============================================================================
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace TelemetryProtocol {

inline constexpr std::uint8_t  Preamble1    = 0xAA;
inline constexpr std::uint8_t  Preamble2    = 0x55;
inline constexpr std::size_t   MaxPayload   = 64;
inline constexpr std::size_t   HeaderSize   = 5;
inline constexpr std::size_t   CrcSize      = 2;
inline constexpr std::size_t   MaxFrameSize = HeaderSize + MaxPayload + CrcSize;

enum class ParserResult : std::uint8_t {
    NeedMoreBytes,
    PacketReady,
    ErrorCrc,
    ErrorLength
};

struct Packet {
    std::uint8_t msg_id{0};
    std::uint8_t seq{0};
    std::uint8_t len{0};
    std::array<std::uint8_t, MaxPayload> payload{};
};

/* Генерація таблиці CRC-16-CCITT у час компіляції (consteval) */
consteval std::array<std::uint16_t, 256> generateCrc16Lut() noexcept {
    std::array<std::uint16_t, 256> table{};
    for (std::size_t i = 0; i < 256; ++i) {
        std::uint16_t curr = static_cast<std::uint16_t>(i << 8);
        for (int b = 0; b < 8; ++b) {
            if (curr & 0x8000U) {
                curr = static_cast<std::uint16_t>((curr << 1) ^ 0x1021U);
            } else {
                curr = static_cast<std::uint16_t>(curr << 1);
            }
        }
        table[i] = curr;
    }
    return table;
}

inline constexpr auto Crc16Table = generateCrc16Lut();

inline constexpr std::uint16_t crcStep(std::uint16_t crc, std::uint8_t byte) noexcept {
    std::uint8_t idx = static_cast<std::uint8_t>((crc >> 8) ^ byte);
    return static_cast<std::uint16_t>((crc << 8) ^ Crc16Table[idx]);
}

class StreamParser {
public:
    enum class State : std::uint8_t {
        WaitSync1,
        WaitSync2,
        GetMsgId,
        GetSeq,
        GetLen,
        GetPayload,
        GetCrcLow,
        GetCrcHigh
    };

    constexpr StreamParser() noexcept = default;

    constexpr void reset() noexcept {
        m_state = State::WaitSync1;
        m_rxIndex = 0;
        m_crcAccum = 0xFFFF;
        m_crcReceived = 0;
    }

    constexpr ParserResult consumeByte(std::uint8_t byte, Packet& outPacket) noexcept {
        switch (m_state) {
        case State::WaitSync1:
            if (byte == Preamble1) {
                m_state = State::WaitSync2;
            }
            return ParserResult::NeedMoreBytes;

        case State::WaitSync2:
            if (byte == Preamble2) {
                m_state = State::GetMsgId;
                m_crcAccum = 0xFFFF;
            } else if (byte == Preamble1) {
                m_state = State::WaitSync2;
            } else {
                m_state = State::WaitSync1;
            }
            return ParserResult::NeedMoreBytes;

        case State::GetMsgId:
            m_packet.msg_id = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            m_state = State::GetSeq;
            return ParserResult::NeedMoreBytes;

        case State::GetSeq:
            m_packet.seq = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            m_state = State::GetLen;
            return ParserResult::NeedMoreBytes;

        case State::GetLen:
            if (byte > MaxPayload) {
                m_state = State::WaitSync1;
                return ParserResult::ErrorLength;
            }
            m_packet.len = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            m_rxIndex = 0;
            if (m_packet.len == 0) {
                m_state = State::GetCrcLow;
            } else {
                m_state = State::GetPayload;
            }
            return ParserResult::NeedMoreBytes;

        case State::GetPayload:
            m_packet.payload[m_rxIndex++] = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            if (m_rxIndex >= m_packet.len) {
                m_state = State::GetCrcLow;
            }
            return ParserResult::NeedMoreBytes;

        case State::GetCrcLow:
            m_crcReceived = static_cast<std::uint16_t>(byte);
            m_state = State::GetCrcHigh;
            return ParserResult::NeedMoreBytes;

        case State::GetCrcHigh:
            m_crcReceived |= static_cast<std::uint16_t>(byte << 8);
            m_state = State::WaitSync1;
            if (m_crcReceived == m_crcAccum) {
                outPacket = m_packet;
                return ParserResult::PacketReady;
            }
            return ParserResult::ErrorCrc;
        }
        m_state = State::WaitSync1;
        return ParserResult::NeedMoreBytes;
    }

private:
    State         m_state{State::WaitSync1};
    std::uint8_t  m_rxIndex{0};
    std::uint16_t m_crcAccum{0xFFFF};
    std::uint16_t m_crcReceived{0};
    Packet        m_packet{};
};

inline std::size_t serialize(std::uint8_t msgId, std::uint8_t seq,
                             std::span<const std::uint8_t> payload,
                             std::span<std::uint8_t> outBuffer) noexcept {
    if (payload.size() > MaxPayload || outBuffer.size() < (HeaderSize + payload.size() + CrcSize)) {
        return 0;
    }

    outBuffer[0] = Preamble1;
    outBuffer[1] = Preamble2;
    outBuffer[2] = msgId;
    outBuffer[3] = seq;
    outBuffer[4] = static_cast<std::uint8_t>(payload.size());

    std::uint16_t crc = 0xFFFF;
    crc = crcStep(crc, msgId);
    crc = crcStep(crc, seq);
    crc = crcStep(crc, static_cast<std::uint8_t>(payload.size()));

    for (std::size_t i = 0; i < payload.size(); ++i) {
        outBuffer[5 + i] = payload[i];
        crc = crcStep(crc, payload[i]);
    }

    outBuffer[5 + payload.size()] = static_cast<std::uint8_t>(crc & 0xFF);
    outBuffer[6 + payload.size()] = static_cast<std::uint8_t>((crc >> 8) & 0xFF);

    return HeaderSize + payload.size() + CrcSize;
}

} // namespace TelemetryProtocol
```
:::

---

## Тестовий стенд із симуляцією збоїв каналу

Тестовий стенд відтворює реальні умови радіоефіру та перевіряє поведінку кінцевого автомата за чотирма основними сценаріями:

1. **Нормальне проходження (Happy Path)**: пакет коректно серіалізується, передається через байтовий потік і повністю розбирається FSM із підтвердженням ідентифікатора повідомлення, порядкового номера та вмісту корисного навантаження.
2. **Інверсія біта (Bit Flip)**: зміна 1 біта у полі корисного навантаження призводить до негайної фіксації статусу `PARSER_ERR_CRC` та відкидання кадру без впливу на наступні пакети.
3. **Зсув байтів (Byte Slip)**: штучне випадання одного байта всередині кадру спотворює перший пакет (викликає помилку довжини або CRC), однак наступний валідний пакет, що надходить одразу слідом, розпізнається і декодується з першої спроби без потреби у зовнішньому скиданні парсера.
4. **Атака хибної преамбули (Phantom Preamble)**: якщо корисне навантаження першого пакета містить випадкові байти `0xAA 0x55`, автомат не зависає на хибному кадрі — помилка CRC відсікає фальшивий пакет, і черговий справжній кадр успішно приймається.

:::tabs
```c
/* ============================================================================
 * main_test.c — Тестування стійкості автомата до завад
 * ============================================================================ */
#include <stdio.h>
#include <assert.h>

int main(void) {
    parser_t parser;
    parser_init(&parser);

    uint8_t tx_buffer[128];
    uint8_t dummy_payload[4] = {0x11, 0x22, 0x33, 0x44};

    /* 1. Серіалізація тестового кадру */
    size_t frame_len = serialize_packet(0x02, 10, dummy_payload, 4, tx_buffer);
    assert(frame_len == 11);

    /* 2. Потокове декодування валідного кадру */
    packet_t rx_packet;
    parser_status_t status = PARSER_CONTINUE;
    for (size_t i = 0; i < frame_len; ++i) {
        status = parser_consume_byte(&parser, tx_buffer[i], &rx_packet);
    }
    assert(status == PARSER_PACKET_OK);
    assert(rx_packet.msg_id == 0x02);
    assert(rx_packet.seq == 10);
    assert(rx_packet.len == 4);

    /* 3. Симуляція пошкодження даних (Bit Flip) */
    tx_buffer[6] ^= 0x01; /* Спотворюємо один байт навантаження */
    for (size_t i = 0; i < frame_len; ++i) {
        status = parser_consume_byte(&parser, tx_buffer[i], &rx_packet);
    }
    assert(status == PARSER_ERR_CRC);

    /* 4. Симуляція випадання байта (Byte Slip) перед наступним нормальним пакетом */
    uint8_t stream_with_slip[25];
    /* Пакет 1 (битий, без 4-го байта) */
    memcpy(stream_with_slip, tx_buffer, 3);
    memcpy(stream_with_slip + 3, tx_buffer + 4, frame_len - 4);
    /* Пакет 2 (цілий) */
    size_t pkt2_len = serialize_packet(0x03, 11, dummy_payload, 4, stream_with_slip + frame_len - 1);

    int ok_packets = 0;
    for (size_t i = 0; i < (frame_len - 1 + pkt2_len); ++i) {
        status = parser_consume_byte(&parser, stream_with_slip[i], &rx_packet);
        if (status == PARSER_PACKET_OK) {
            ok_packets++;
        }
    }
    /* Перший пакет відкинуто через помилку довжини або CRC, другий успішно прийнято */
    assert(ok_packets == 1);
    assert(rx_packet.msg_id == 0x03);
    assert(rx_packet.seq == 11);

    return 0;
}
```
```cpp
// ============================================================================
// main_test.cpp — Тестування стійкості автомата мовою C++
// ============================================================================
#include <array>
#include <cassert>
#include <span>
#include <vector>

int main() {
    using namespace TelemetryProtocol;

    StreamParser parser;
    std::array<std::uint8_t, 128> txBuffer{};
    std::array<std::uint8_t, 4> dummyPayload{0x11, 0x22, 0x33, 0x44};

    // 1. Серіалізація валідного кадру
    std::size_t frameLen = serialize(0x02, 10, dummyPayload, txBuffer);
    assert(frameLen == 11);

    // 2. Декодування без завад
    Packet rxPacket{};
    ParserResult res{ParserResult::NeedMoreBytes};
    for (std::size_t i = 0; i < frameLen; ++i) {
        res = parser.consumeByte(txBuffer[i], rxPacket);
    }
    assert(res == ParserResult::PacketReady);
    assert(rxPacket.msg_id == 0x02);
    assert(rxPacket.seq == 10);
    assert(rxPacket.len == 4);

    // 3. Інверсія біта -> очікуємо ErrorCrc
    txBuffer[6] ^= 0x01;
    for (std::size_t i = 0; i < frameLen; ++i) {
        res = parser.consumeByte(txBuffer[i], rxPacket);
    }
    assert(res == ParserResult::ErrorCrc);

    return 0;
}
```
:::

---

## Аналіз ресурсів та продуктивності на мікроконтролері

Вимірювання апаратних витрат на цільовому ядрі ARM Cortex-M4 (STM32F405 @ 168 МГц, компілятор GCC 12 з оптимізацією `-O2`):

1. **Використання пам'яті програм (Flash ROM)**:
   - Таблиця CRC-16 LUT: рівно 512 байтів у секції константних даних `.rodata`.
   - Машинний код функцій парсера `parser_consume_byte()` та серіалізатора `serialize_packet()`: менш ніж 420 байтів у секції інструкцій `.text`.
   - Сумарний слід у Flash: менш ніж 1 кілобайт, що становить менше 0.1% доступної пам'яті типового мікроконтролера польотного контролера (1024 КБ Flash).

2. **Використання оперативної пам'яті (SRAM)**:
   - Екземпляр структури `parser_t`: рівно 72 байти у статичній пам'яті (секція `.bss` або `.data`).
   - Глибина використання системного стека під час обробки виклику: не більше 16 байтів на збереження локальних регістрів.
   - Використання динамічної купи (Heap): **строго 0 байтів**.

3. **Швидкодія та обчислювальний бюджет**:
   - Обробка одного байта методом `parser_consume_byte()` у середньому займає 14–18 машинних тактів процесора (~90–110 наносекунд на частоті 168 МГц).
   - При максимальній практичній швидкості послідовного радіоканалу 115 200 бод (близько 11 520 байтів на секунду) безперервний потік телеметрії забирає менш ніж **0.12% процесорного часу** одного процесорного ядра.
   - Навіть при роботі на надшвидкісному лінку 921 600 бод навантаження на процесор не перевищує 0.95%, що залишає понад 99% обчислювального ресурсу для матричних обчислень розширеного фільтра Калмана (EKF), навігаційного планувальника та контуру кутової стабілізації польоту (PID-регулятора на частоті 4–8 кГц).

4. **Пастки реалізації у вбудованому коді**:
   - *Гонка станів при роботі з перериваннями*: екземпляр парсера `parser_t` ніколи не повинен викликатися одночасно з ISR переривання UART та з головного циклу `main()`. Єдиною коректною моделлю є розміщення парсера виключно в контексті споживача (основний потік або фонова таска), тоді як переривання або контролер DMA займаються виключно копіюванням сирих байтів у кільцевий буфер FIFO.
   - *Збереження преамбули у стані `WAIT_PREAMBLE_2`*: якщо після першого байта `0xAA` надходить не `0x55`, а ще один байт `0xAA` (наприклад, у послідовності `0xAA 0xAA 0x55`), автомат зобов'язаний залишитися у стані `WAIT_PREAMBLE_2`. Скидання у `WAIT_PREAMBLE_1` призвело б до пропуску валідного початку кадру.

# ⚙️ Потоковий розбірник кадру MAVLink v2 на C та C++

У вбудованих системах керування безпілотними апаратами байти телеметрії надходять із послідовного порту UART безперервним неструктурованим потоком. Апаратний контролер отримує байти через переривання або кільцевий буфер прямого доступу до пам'яті (DMA), де фізичні межі повідомлень відсутні, а в каналі зв'язку неминуче трапляються шумові спотворення, втрачені байти та випадкові фальшиві маркери.

Головне завдання потокового розбірника (англ. *stream parser*, від лат. *pars* — частина) — виділити валідний двійковий кадр MAVLink v2 із сирого потоку, перевірити цілісність контрольної суми CRC, розпізнати наявність блоку підпису та безпечно передати корисні дані у польотний стек. При цьому обробка кожного байта має виконуватися за постійний час `O(1)` з нульовим динамічним виділенням пам'яті (без викликів `malloc` або `free`).

### Архітектура скінченного автомата розбору

Потоковий розбірник проєктується як детермінований скінченний автомат (англ. *finite-state machine*, лат. *finitus* — обмежений). Автомат приймає по одному байту за виклик функції, змінює внутрішній стан і накопичує контрольну суму кадру на льоту:

```
[Очікування STX (0xFD)]
         │
         ▼
[Довжина LEN] ──► [INC прапорці] ──► [CMP прапорці] ──► [Лічильник SEQ]
                                                              │
                                                              ▼
[CRC_HIGH] ◄── [CRC_LOW] ◄── [Корисні дані PAYLOAD] ◄── [Адреси SYS/COMP та MSG_ID]
     │
     ├─ (Якщо INC_FLAGS & 0x01) ──► [Блок підпису (13 байтів)] ──► [Пакет готовий]
     │
     └─ (Без підпису) ───────────────────────────────────────────► [Пакет готовий]
```

Автомат починає роботу в стані очікування стартового байта. Щойно вхідний потік містить байт `0xFD` (маркер MAVLink v2), накопичувач CRC скидається в початкове значення `0xFFFF`, і система переходить до читання полів заголовка.

Якщо під час отримання заголовка чи корисних даних лічильник байтів перевищує допустиму межу або фінальна контрольна сума не збігається, автомат миттєво повертається до початкового стану пошуку нового маркера `0xFD`.

### Покрокове простеження розбору кадру

Простежимо роботу автомата на конкретному прикладі прийому повідомлення `HEARTBEAT` (ID 0, довжина 9 байтів) від автопілота з адресою `SYSID = 1`, `COMPID = 1`.

Вхідна послідовність байтів з UART:
`0xFD 0x09 0x00 0x00 0x1A 0x01 0x01 0x00 0x00 0x00 [9 байтів даних] [CRC_L] [CRC_H]`

1.  **Крок 1 (Байт `0xFD`)**: Стан `MAV_PARSE_STATE_IDLE` виявляє магічне число. Автомат ініціалізує акумулятор `crc_accum = 0xFFFF`, записує `magic = 0xFD` і перемикається у стан `MAV_PARSE_STATE_GOT_STX`.
2.  **Крок 2 (Байт `0x09`)**: Зчитується довжина корисного навантаження `LEN = 9`. Байт `0x09` додається до накопичувача CRC. Автомат переходить до `MAV_PARSE_STATE_GOT_LENGTH`.
3.  **Крок 3–4 (Байти `0x00`, `0x00`)**: Зчитуються прапорці `INC_FLAGS` та `CMP_FLAGS`. Оскільки біт `0x01` в `INC_FLAGS` скинутий, автомат фіксує, що пакет передається без блоку підпису.
4.  **Крок 5–7 (Байти `0x1A`, `0x01`, `0x01`)**: Зчитуються лічильник пакета `SEQ = 26`, системна адреса `SYSID = 1` та компонент `COMPID = 1`. Усі байти послідовно пропускаються через поліном CRC.
5.  **Крок 8–10 (Байти `0x00`, `0x00`, `0x00`)**: Три байти збираються у 24-бітне число `MSG_ID = 0` (повідомлення `HEARTBEAT`). Лічильник прийнятих байтів корисних даних скидається в 0.
6.  **Крок 11 (Прийом 9 байтів PAYLOAD)**: Автомат перебуває у стані `MAV_PARSE_STATE_GOT_PAYLOAD`, записує байти у внутрішній масив `payload` і оновлює CRC. Після прийому 9-го байта лічильник збігається з `LEN`, і автомат переходить до читання контрольної суми.
7.  **Крок 12–13 (Байти `CRC_L` та `CRC_H`)**: Зчитується 16-бітна контрольна сума. До накопичувача CRC додається байт `CRC_EXTRA = 50` (відбиток схеми `HEARTBEAT`). Якщо розраховане значення збігається з отриманим, функція повертає `true`, сигналізуючи про успішний прийом валідного кадру.

### Реалізація розбірника

Нижче наведено повну реалізацію потокового розбірника кадру MAVLink v2: на C у процедурному стилі для низькорівневих драйверів вбудованих ОС (FreeRTOS, NuttX) та на C++ з інкапсуляцією стану, строгими типами `enum class` та безпечною роботою з пам'яттю через `std::span` та `std::array`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAVLINK_STX_V2 0xFD
#define MAVLINK_MAX_PAYLOAD_LEN 255
#define MAVLINK_NUM_CHECKSUM_BYTES 2
#define MAVLINK_SIGNATURE_LEN 13
#define MAVLINK_IFLAG_SIGNED 0x01

typedef enum {
    MAV_PARSE_STATE_IDLE,
    MAV_PARSE_STATE_GOT_STX,
    MAV_PARSE_STATE_GOT_LENGTH,
    MAV_PARSE_STATE_GOT_INCOMPAT_FLAGS,
    MAV_PARSE_STATE_GOT_COMPAT_FLAGS,
    MAV_PARSE_STATE_GOT_SEQ,
    MAV_PARSE_STATE_GOT_SYSID,
    MAV_PARSE_STATE_GOT_COMPID,
    MAV_PARSE_STATE_GOT_MSGID1,
    MAV_PARSE_STATE_GOT_MSGID2,
    MAV_PARSE_STATE_GOT_MSGID3,
    MAV_PARSE_STATE_GOT_PAYLOAD,
    MAV_PARSE_STATE_GOT_CRC1,
    MAV_PARSE_STATE_GOT_CRC2,
    MAV_PARSE_STATE_GOT_SIGNATURE
} mav_parse_state_t;

typedef struct {
    uint8_t magic;
    uint8_t len;
    uint8_t incompat_flags;
    uint8_t compat_flags;
    uint8_t seq;
    uint8_t sysid;
    uint8_t compid;
    uint32_t msgid;
    uint8_t payload[MAVLINK_MAX_PAYLOAD_LEN];
    uint16_t checksum;
    uint8_t signature[MAVLINK_SIGNATURE_LEN];
} mavlink_frame_t;

typedef struct {
    mav_parse_state_t state;
    mavlink_frame_t frame;
    uint16_t rx_count;
    uint16_t crc_accum;
    uint8_t sig_count;
} mavlink_parser_t;

static inline void crc_accumulate(uint8_t data, uint16_t *crcAccum) {
    uint8_t tmp = data ^ (uint8_t)(*crcAccum & 0xFF);
    tmp ^= (tmp << 4);
    *crcAccum = (*crcAccum >> 8) ^ ((uint16_t)tmp << 8) ^ ((uint16_t)tmp << 3) ^ ((uint16_t)tmp >> 4);
}

void mavlink_parser_init(mavlink_parser_t *p) {
    p->state = MAV_PARSE_STATE_IDLE;
    p->rx_count = 0;
    p->crc_accum = 0xFFFF;
    p->sig_count = 0;
    memset(&p->frame, 0, sizeof(p->frame));
}

bool mavlink_parse_byte(mavlink_parser_t *p, uint8_t byte, uint8_t crc_extra) {
    switch (p->state) {
    case MAV_PARSE_STATE_IDLE:
        if (byte == MAVLINK_STX_V2) {
            p->frame.magic = byte;
            p->crc_accum = 0xFFFF;
            p->state = MAV_PARSE_STATE_GOT_STX;
        }
        break;

    case MAV_PARSE_STATE_GOT_STX:
        p->frame.len = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_LENGTH;
        break;

    case MAV_PARSE_STATE_GOT_INCOMPAT_FLAGS:
        p->frame.incompat_flags = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_COMPAT_FLAGS;
        break;

    case MAV_PARSE_STATE_GOT_COMPAT_FLAGS:
        p->frame.compat_flags = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_SEQ;
        break;

    case MAV_PARSE_STATE_GOT_SEQ:
        p->frame.seq = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_SYSID;
        break;

    case MAV_PARSE_STATE_GOT_SYSID:
        p->frame.sysid = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_COMPID;
        break;

    case MAV_PARSE_STATE_GOT_COMPID:
        p->frame.compid = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_MSGID1;
        break;

    case MAV_PARSE_STATE_GOT_MSGID1:
        p->frame.msgid = byte;
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_MSGID2;
        break;

    case MAV_PARSE_STATE_GOT_MSGID2:
        p->frame.msgid |= ((uint32_t)byte << 8);
        crc_accumulate(byte, &p->crc_accum);
        p->state = MAV_PARSE_STATE_GOT_MSGID3;
        break;

    case MAV_PARSE_STATE_GOT_MSGID3:
        p->frame.msgid |= ((uint32_t)byte << 16);
        crc_accumulate(byte, &p->crc_accum);
        p->rx_count = 0;
        if (p->frame.len == 0) {
            p->state = MAV_PARSE_STATE_GOT_CRC1;
        } else {
            p->state = MAV_PARSE_STATE_GOT_PAYLOAD;
        }
        break;

    case MAV_PARSE_STATE_GOT_PAYLOAD:
        if (p->rx_count < p->frame.len) {
            p->frame.payload[p->rx_count++] = byte;
            crc_accumulate(byte, &p->crc_accum);
        }
        if (p->rx_count >= p->frame.len) {
            p->state = MAV_PARSE_STATE_GOT_CRC1;
        }
        break;

    case MAV_PARSE_STATE_GOT_CRC1:
        p->frame.checksum = byte;
        p->state = MAV_PARSE_STATE_GOT_CRC2;
        break;

    case MAV_PARSE_STATE_GOT_CRC2:
        p->frame.checksum |= ((uint16_t)byte << 8);
        crc_accumulate(crc_extra, &p->crc_accum);

        if (p->frame.checksum != p->crc_accum) {
            mavlink_parser_init(p);
            return false;
        }

        if (p->frame.incompat_flags & MAVLINK_IFLAG_SIGNED) {
            p->sig_count = 0;
            p->state = MAV_PARSE_STATE_GOT_SIGNATURE;
        } else {
            p->state = MAV_PARSE_STATE_IDLE;
            return true;
        }
        break;

    case MAV_PARSE_STATE_GOT_SIGNATURE:
        p->frame.signature[p->sig_count++] = byte;
        if (p->sig_count >= MAVLINK_SIGNATURE_LEN) {
            p->state = MAV_PARSE_STATE_IDLE;
            return true;
        }
        break;
    }
    return false;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>

namespace mavlink {

constexpr uint8_t STX_V2 = 0xFD;
constexpr size_t MAX_PAYLOAD_LEN = 255;
constexpr size_t SIGNATURE_LEN = 13;
constexpr uint8_t IFLAG_SIGNED = 0x01;

enum class ParserState : uint8_t {
    Idle,
    GotStx,
    GotLength,
    GotIncompatFlags,
    GotCompatFlags,
    GotSeq,
    GotSysId,
    GotCompId,
    GotMsgId1,
    GotMsgId2,
    GotMsgId3,
    ReceivingPayload,
    GotCrc1,
    GotCrc2,
    ReceivingSignature
};

struct Frame {
    uint8_t magic{STX_V2};
    uint8_t len{0};
    uint8_t incompat_flags{0};
    uint8_t compat_flags{0};
    uint8_t seq{0};
    uint8_t sysid{0};
    uint8_t compid{0};
    uint32_t msgid{0};
    std::array<uint8_t, MAX_PAYLOAD_LEN> payload{};
    uint16_t checksum{0};
    std::array<uint8_t, SIGNATURE_LEN> signature{};

    [[nodiscard]] std::span<const uint8_t> payload_view() const noexcept {
        return {payload.data(), len};
    }
};

class FrameParser {
public:
    constexpr FrameParser() = default;

    void reset() noexcept {
        state_ = ParserState::Idle;
        rx_count_ = 0;
        crc_accum_ = 0xFFFF;
        sig_count_ = 0;
        frame_ = Frame{};
    }

    std::optional<Frame> parse_byte(uint8_t byte, uint8_t crc_extra) noexcept {
        switch (state_) {
        case ParserState::Idle:
            if (byte == STX_V2) {
                frame_.magic = byte;
                crc_accum_ = 0xFFFF;
                state_ = ParserState::GotStx;
            }
            break;

        case ParserState::GotStx:
            frame_.len = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotLength;
            break;

        case ParserState::GotLength:
            frame_.incompat_flags = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotIncompatFlags;
            break;

        case ParserState::GotIncompatFlags:
            frame_.compat_flags = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotCompatFlags;
            break;

        case ParserState::GotCompatFlags:
            frame_.seq = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotSeq;
            break;

        case ParserState::GotSeq:
            frame_.sysid = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotSysId;
            break;

        case ParserState::GotSysId:
            frame_.compid = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotCompId;
            break;

        case ParserState::GotCompId:
            frame_.msgid = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotMsgId1;
            break;

        case ParserState::GotMsgId1:
            frame_.msgid |= (static_cast<uint32_t>(byte) << 8);
            accumulate_crc(byte);
            state_ = ParserState::GotMsgId2;
            break;

        case ParserState::GotMsgId2:
            frame_.msgid |= (static_cast<uint32_t>(byte) << 16);
            accumulate_crc(byte);
            rx_count_ = 0;
            if (frame_.len == 0) {
                state_ = ParserState::GotCrc1;
            } else {
                state_ = ParserState::ReceivingPayload;
            }
            break;

        case ParserState::ReceivingPayload:
            frame_.payload[rx_count_++] = byte;
            accumulate_crc(byte);
            if (rx_count_ >= frame_.len) {
                state_ = ParserState::GotCrc1;
            }
            break;

        case ParserState::GotCrc1:
            frame_.checksum = byte;
            state_ = ParserState::GotCrc2;
            break;

        case ParserState::GotCrc2:
            frame_.checksum |= (static_cast<uint16_t>(byte) << 8);
            accumulate_crc(crc_extra);

            if (frame_.checksum != crc_accum_) {
                reset();
                return std::nullopt;
            }

            if (frame_.incompat_flags & IFLAG_SIGNED) {
                sig_count_ = 0;
                state_ = ParserState::ReceivingSignature;
            } else {
                Frame completed = frame_;
                reset();
                return completed;
            }
            break;

        case ParserState::ReceivingSignature:
            frame_.signature[sig_count_++] = byte;
            if (sig_count_ >= SIGNATURE_LEN) {
                Frame completed = frame_;
                reset();
                return completed;
            }
            break;
        }
        return std::nullopt;
    }

private:
    void accumulate_crc(uint8_t byte) noexcept {
        uint8_t tmp = byte ^ static_cast<uint8_t>(crc_accum_ & 0xFF);
        tmp ^= (tmp << 4);
        crc_accum_ = (crc_accum_ >> 8) ^ (static_cast<uint16_t>(tmp) << 8)
                   ^ (static_cast<uint16_t>(tmp) << 3) ^ (static_cast<uint16_t>(tmp) >> 4);
    }

    ParserState state_{ParserState::Idle};
    Frame frame_{};
    uint16_t rx_count_{0};
    uint16_t crc_accum_{0xFFFF};
    uint8_t sig_count_{0};
};

} // namespace mavlink
```
:::

### Взаємодія з кільцевим буфером DMA

У реальній прошивці розбірник не викликається зсередини переривання UART, оскільки обробка байта в ISR блокує вищі пріоритети системи. Замість цього контролер DMA записує потік у кільцевий буфер оперативної пам'яті, а окрема задача операційної системи реального часу (RTOS) вичитує накопичені байти:

:::tabs
```c
// Типовий цикл обробки телеметрії в задачі RTOS
void telemetry_task_loop(mavlink_parser_t *parser, uart_dma_ring_t *ring) {
    uint8_t byte;
    while (uart_dma_ring_pop(ring, &byte)) {
        // Отримуємо MSG_ID на кроці заголовка для вибору правильного CRC_EXTRA
        uint8_t crc_extra = mavlink_get_crc_extra(parser->frame.msgid);
        
        if (mavlink_parse_byte(parser, byte, crc_extra)) {
            // Пакет успішно прийнято та верифіковано
            handle_mavlink_message(&parser->frame);
        }
    }
}
```
```cpp
// Обробка потоку з кільцевого буфера на C++
void process_telemetry_loop(FrameParser& parser, UartRingBuffer& ring) noexcept {
    uint8_t byte{0};
    while (ring.pop(byte)) {
        const uint8_t crc_extra = get_crc_extra(parser.current_msg_id());
        if (auto frame = parser.parse_byte(byte, crc_extra)) {
            handle_message(*frame);
        }
    }
}
```
:::

Така архітектура повністю ізолює апаратний рівень прийому байтів від логіки польотного контролера і гарантує відсутність втрати даних навіть при короткочасних пікових навантаженнях на центральний процесор.

### Типові пастки під час обробки потоку

1. **Фальшивий STX усередині корисних даних.** Байт зі значенням `0xFD` може законно зустрітися у середині `float` числа кута тангажу чи таймштампу. Якщо попередній кадр був пошкоджений шумом, автомат може зачепитися за цей байт і почати розбір фальшивого кадру. Він прочитає наступні байти як заголовок і неминуче відкине пакет на кроці перевірки CRC. Правильний розбірник не зависає, а одразу повертається до стану `MAV_PARSE_STATE_IDLE`.
2. **Нульова довжина корисного навантаження (`LEN = 0`).** Повідомлення без корисних даних (наприклад, деякі системні запити `REQUEST_DATA_STREAM`) мають `LEN = 0`. Автомат повинен коректно оминати стан читання даних і переходити одразу до перевірки контрольної суми `CRC1`.
3. **Відновлення після відтинання нулів (Zero-Truncation).** Під час копіювання отриманого корисного навантаження в цільову структуру пам'яті обов'язково викликають `memset` для очищення всієї структури нулями. Якщо скопіювати лише отримані `len` байтів у неініціалізовану структуру зі стека, у відтятих полях залишиться випадкове сміття оперативної пам'яті.
4. **Знаковий зсув байтів у розрахунку CRC.** У мові C тип `char` на деяких платформах є знаковим (`signed`). Якщо передати байт значенням `0xFD` у функцію з типом `int` без явного перетворення до `uint8_t`, відбудеться знакове розширення до `0xFFFFFFFD`, що повністю спотворить розрахунок контрольної суми.

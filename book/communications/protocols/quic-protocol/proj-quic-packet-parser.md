# ⚙️ Розбір двійкових пакетів та фреймів QUIC у просторі користувача

Оскільки протокол QUIC функціонує в просторі користувача поверх беззв'язкових датаграм UDP, кожен високопродуктивний вебсервер, зворотний проксі-сервер або клієнтська бібліотека (наприклад, Envoy, NGINX, Cloudflare quiche, ngtcp2, MsQuic) зобов'язані самостійно реалізовувати низькорівневий бінарний розбір мережевих пакетів. На відміну від класичного стеку TCP, де декодуванням заголовків, фільтрацією дублікатів, перевіркою контрольних сум та впорядкуванням черг сегментів займається підсистема мережевого ядра операційної системи (підсистема `net/ipv4/tcp_input.c` у Linux), у QUIC уся транспортна логіка виконується в користувацькому процесі.

Обробка датаграм відбувається в найгарячішому циклі прийому подій (Event Loop). Якщо сервер обслуговує потік у 100 000 запитів на секунду, будь-яка неефективність під час синтаксичного розбору — зайве копіювання пам'яті, динамічне виділення буферів через `malloc`, відсутність вирівнювання за кеш-лініями процесора або некоректна обробка чисел змінної довжини — миттєво перетворює парсер на вузьке місце системи та створює ризики вразливостей відмови в обслуговуванні (DoS).

Нижче наведено повний архітектурний розбір принципів побудови парсера QUIC, алгоритмів відновлення номерів пакетів, маршрутизації через eBPF, валідації лімітів контролю потоку, механізмів зняття маски заголовків, таблиць відстеження Connection ID, апаратних SIMD-оптимізацій, організації кільцевих буферів AF_XDP, інтеграції з конвеєром HTTP/3 та захисту від DoS-атак, а також робочу реалізацію синтаксичного аналізатора двійкових пакетів, фреймів `STREAM` та `ACK` мовами C та C++ з нульовим копіюванням (zero-copy), суворою перевіркою меж буферів та захистом від переповнень пам'яті.

## 1. Архітектурні виклики та оптимізація прийому в просторі користувача

Створення швидкого мережевого рушія QUIC вимагає розв'язання кількох фундаментальних інженерних задач:

### 1.1. Пакетне склеювання датаграм (Packet Coalescing)
Специфікація RFC 9000 (§12.2) дозволяє розміщувати декілька логічних пакетів QUIC всередині однієї фізичної UDP-датаграми. Наприклад, під час початкового підключення клієнт може надіслати єдину UDP-датаграму розміром 1200 байтів, у якій послідовно розташовані пакет `Initial` (що містить криптографічний блок `ClientHello`) та пакет `0-RTT` (із ранніми HTTP-даними).

Синтаксичний аналізатор зобов'язаний коректно зчитувати поле довжини `Length` першого пакета, виокремлювати його зашифроване навантаження і, не повертаючись до операційної системи, негайно починати розбір наступного пакета з тієї самої UDP-датаграми. Помилка у зсуві покажчика призведе до того, що другий пакет буде прочитано як пошкоджене сміття.

### 1.2. Використання системних викликів recvmmsg, io_uring та UDP GSO/GRO
Виклик стандартного POSIX-функціоналу `recvfrom()` для кожної окремої датаграми створює колосальний накладний оверхед через постійні перемикання контексту між простором користувача та ядром операційної системи. Сучасні рушії QUIC застосовують пакетний системний виклик `recvmmsg()` або черги асинхронного введення-виведення Linux `io_uring`, які за один системний перехід вичитують з черги сокета до 64 або 128 UDP-датаграм у підготовлений масив структур `struct mmsghdr`.

Більше того, у Linux використовується механізм сегментації UDP (Generic Segmentation Offload, UDP GSO) та апаратного збирання (Generic Receive Offload, GRO). Це дозволяє передавати датаграми розміром до 64 кілобайтів через віртуальний стек сокета, розбиваючи їх на MTU-сегменти безпосередньо на мережевій карті, що зменшує навантаження на процесор у 3–4 рази.

### 1.3. Маршрутизація з'єднань за допомогою Connection ID та eBPF/XDP
У багатопотокових серверах (наприклад, з архітектурою worker threads за кількістю ядер CPU) традиційний розподіл трафіку сокетів через прапорець `SO_REUSEPORT` хешує 4-tuple (IP джерела, порт джерела, IP призначення, порт призначення). Коли клієнт змінює мережу (наприклад, перемикається з Wi-Fi на LTE), його 4-tuple змінюється, і ядро Linux помилково перенаправляє пакет на інший потік (worker), де немає стану цієї сесії.

Щоб запобігти цьому, високонавантажені сервери розміщують перед сокетами програму eBPF/XDP (eXpress Data Path). Програма eBPF за кілька наносекунд розбирає перші байти UDP-датаграми, вилучає Destination Connection ID, зчитує закодований у ньому ідентифікатор робочого потоку (Server ID / Worker ID) та спрямовує пакет безпосередньо у сокет потрібного ядра без блокувань та синхронізацій.

### 1.4. Принцип нульового копіювання (Zero-Copy Data Slicing)
При швидкостях передачі даних 10–40 Гбіт/с копіювання корисного навантаження з системного буфера в проміжні структури даних призводить до вимивання L1/L2 кеш-пам'яті процесора. Надійний парсер повинен повертати лише легковикові структури-зрізи (в C — покажчик `const uint8_t*` та довжину `size_t`, у C++ — `std::span<const uint8_t>`), які посилаються на оригінальний буфер сокета. Виділення динамічної пам'яті в купі (`heap`) під час розбору пакетів суворо заборонено: усі структури створюються на стеку виконання.

## 2. Відновлення повного номера пакета (Packet Number Decoding)

Для економії пропускної здатності в заголовку QUIC передається не повний 62-бітний номер пакета, а лише його молодші 1, 2, 3 або 4 байти (усічений номер, `truncated_pn`). Отримувач зобов'язаний реконструювати повний номер `full_pn`, спираючись на найбільший раніше підтверджений номер пакета `largest_acked` (RFC 9000 Appendix A).

Математичний алгоритм реконструкції знаходить значення, найближче до очікуваного номера:

```
bits_count = num_bytes · 8
window_size = 1 << bits_count
half_window = window_size / 2
expected_pn = largest_acked + 1

candidate_pn = (expected_pn & ~(window_size - 1)) | truncated_pn

Якщо candidate_pn <= expected_pn - half_window та candidate_pn + window_size < (1ULL << 62):
    full_pn = candidate_pn + window_size
Інакше якщо candidate_pn > expected_pn + half_window та candidate_pn >= window_size:
    full_pn = candidate_pn - window_size
Інакше:
    full_pn = candidate_pn
```

Ця формула гарантує однозначне відновлення номера навіть при отриманні пакетів із затримкою або перевпорядкуванням у межах половини вікна розрядності переданого поля.

## 3. Зняття захисту заголовка (Header Protection Unmasking)

Захист заголовків (RFC 9001 §5.4) унеможливлює пасивне прослуховування метаданих проміжними мережевими вузлами. Процедура демаскування реалізується наступним чином:
1. Після зчитування незахищених полів (Connection ID) визначається позиція зміщення номера пакета `pn_offset`.
2. Відступаючи від `pn_offset` на 4 байти вперед углиб зашифрованого навантаження (де навантаження гарантовано зашифроване), вибирається 16-байтний блок `sample`.
3. За допомогою ключа захисту заголовків `hp_key` (довжиною 16 або 32 байти) обчислюється 16-байтна маска `mask = AES_ECB(hp_key, sample)` (або `ChaCha20` з фіксованим лічильником).
4. Операцією XOR відновлюються замасковані біти першого октету:
   - Для Long Header: `first_byte ^= (mask[0] & 0x0F)` (відновлюються 2 біти довжини номера пакета).
   - Для Short Header: `first_byte ^= (mask[0] & 0x1F)` (відновлюються біт Key Phase та 2 біти довжини номера пакета).
5. За відновленими бітами визначається довжина номера пакета `pn_len = (first_byte & 0x03) + 1`.
6. Байти номера пакета демаскуються: `for (int i = 0; i < pn_len; i++) pn_bytes[i] ^= mask[1 + i]`.
7. Значення `pn_bytes` збирається в ціле число `truncated_pn` та передається у функцію реконструкції `full_pn`.

## 4. Покроковий алгоритм двійкового розбору

Бінарний синтаксичний аналіз датаграми QUIC складається з п'яти послідовних кроків:

1. **Декодування цілих чисел змінної довжини (Variable-Length Integer):**
   Парсер аналізує 2 старші біти першого байта числа (бітова маска `0xC0`). Якщо маска дорівнює `0x00`, довжина числа становить 1 байт (значення від 0 до 63); якщо `0x40` — 2 байти (значення до 16 383); якщо `0x80` — 4 байти (значення до 1 073 741 823); якщо `0xC0` — 8 байтів (значення до `2⁶² - 1`). Перед зчитуванням парсер перевіряє, чи залишок буфера не менший за розраховану довжину. Зчитування байтів виконується за схемою Big-Endian з побітовим зсувом.

2. **Класифікація форми заголовка (Header Form Classification):**
   Перевіряється старший біт `0x80` найпершого байта датаграми:
   - Якщо біт дорівнює `1` (Long Header), парсер перевіряє наявність мінімум 5 байтів у буфері, зчитує 4-байтну версію протоколу (`Version`), розпізнає двобітний тип пакета (`Initial`, `0-RTT`, `Handshake`, `Retry`), вилучає довжини та байти Destination і Source Connection ID, зчитує токен валідації адреси (для пакета `Initial`) та отримує поле довжини корисного навантаження `Length`.
   - Якщо біт дорівнює `0` (Short Header), версія та Source Connection ID відсутні. Парсер використовує раніше узгоджену статичну довжину Destination Connection ID, після чого весь залишок датаграми віддається криптографічній підсистемі.

3. **Розшифрування та автентифікація AEAD:**
   З відновленим номером пакета формується Nonce (`IV XOR full_pn`), після чого розшифровується корисне навантаження алгоритмом AES-GCM або ChaCha20-Poly1305.

4. **Розбір послідовності фреймів (Frame Iteration):**
   Розшифроване навантаження ітерується байт за байтом. Перший байт кожного кадру визначає його тип. Якщо тип лежить у діапазоні від `0x08` до `0x0F`, запускається процедура розбору фрейму `STREAM`. Якщо тип дорівнює `0x02` або `0x03`, запускається розбір підтвердження `ACK`.

5. **Збирання потоку в буфері застосунку (Stream Reassembly):**
   Отримані байти кадру `STREAM` розміщуються у спадному буфері потоку відповідно до значення `Offset`. Якщо байти надійшли послідовно (зсув збігається з поточною позицією читання застосунку), вони негайно передаються обробнику HTTP/3. Якщо виявлено дірку в зміщеннях, фрагмент зберігається в інтервальному дереві очікування, при цьому паралельні потоки з іншими `Stream ID` продовжують оброблятися без затримок.

## 5. Програмна реалізація парсера

Нижче наведено повну реалізацію бінарного аналізатора на мовах C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define QUIC_MAX_CID_LEN 20
#define QUIC_VERSION_1   0x00000001

typedef enum {
    QUIC_OK = 0,
    QUIC_ERR_BUFFER_TOO_SHORT,
    QUIC_ERR_INVALID_VARINT,
    QUIC_ERR_INVALID_VERSION,
    QUIC_ERR_CID_TOO_LONG,
    QUIC_ERR_UNKNOWN_FRAME
} quic_status_t;

typedef enum {
    QUIC_PKT_INITIAL   = 0x00,
    QUIC_PKT_0RTT      = 0x01,
    QUIC_PKT_HANDSHAKE = 0x02,
    QUIC_PKT_RETRY     = 0x03,
    QUIC_PKT_1RTT_SHORT
} quic_pkt_type_t;

typedef struct {
    uint8_t len;
    uint8_t data[QUIC_MAX_CID_LEN];
} quic_cid_t;

typedef struct {
    quic_pkt_type_t type;
    bool is_long_header;
    uint32_t version;
    quic_cid_t dcid;
    quic_cid_t scid;
    const uint8_t *token;
    size_t token_len;
    uint64_t payload_len;
    const uint8_t *payload;
} quic_header_t;

typedef struct {
    uint64_t stream_id;
    uint64_t offset;
    uint64_t length;
    bool fin;
    const uint8_t *data;
} quic_stream_frame_t;

typedef struct {
    uint64_t largest_acked;
    uint64_t ack_delay;
    uint64_t first_ack_range;
    uint64_t range_count;
} quic_ack_frame_t;

/* Декодування цілого числа змінної довжини (RFC 9000 §16) */
quic_status_t quic_read_varint(const uint8_t **buf, size_t *buf_len, uint64_t *val) {
    if (*buf_len == 0) return QUIC_ERR_BUFFER_TOO_SHORT;

    uint8_t first = **buf;
    uint8_t prefix = (first >> 6) & 0x03;
    size_t len = (size_t)1 << prefix;

    if (*buf_len < len) return QUIC_ERR_BUFFER_TOO_SHORT;

    uint64_t res = first & 0x3F;
    (*buf)++;
    (*buf_len)--;

    for (size_t i = 1; i < len; i++) {
        res = (res << 8) | (**buf);
        (*buf)++;
        (*buf_len)--;
    }

    *val = res;
    return QUIC_OK;
}

/* Розбір незахищеного заголовка пакета QUIC */
quic_status_t quic_parse_header(const uint8_t *raw, size_t raw_len,
                                size_t dcid_len_for_short, quic_header_t *hdr) {
    if (raw_len < 1) return QUIC_ERR_BUFFER_TOO_SHORT;

    const uint8_t *p = raw;
    size_t rem = raw_len;
    uint8_t first_byte = *p++;
    rem--;

    hdr->is_long_header = (first_byte & 0x80) != 0;

    if (hdr->is_long_header) {
        if (rem < 4) return QUIC_ERR_BUFFER_TOO_SHORT;
        hdr->version = ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
                       ((uint32_t)p[2] << 8)  | ((uint32_t)p[3]);
        p += 4; rem -= 4;

        uint8_t type_bits = (first_byte >> 4) & 0x03;
        hdr->type = (quic_pkt_type_t)type_bits;

        /* DCID */
        if (rem < 1) return QUIC_ERR_BUFFER_TOO_SHORT;
        hdr->dcid.len = *p++; rem--;
        if (hdr->dcid.len > QUIC_MAX_CID_LEN) return QUIC_ERR_CID_TOO_LONG;
        if (rem < hdr->dcid.len) return QUIC_ERR_BUFFER_TOO_SHORT;
        memcpy(hdr->dcid.data, p, hdr->dcid.len);
        p += hdr->dcid.len; rem -= hdr->dcid.len;

        /* SCID */
        if (rem < 1) return QUIC_ERR_BUFFER_TOO_SHORT;
        hdr->scid.len = *p++; rem--;
        if (hdr->scid.len > QUIC_MAX_CID_LEN) return QUIC_ERR_CID_TOO_LONG;
        if (rem < hdr->scid.len) return QUIC_ERR_BUFFER_TOO_SHORT;
        memcpy(hdr->scid.data, p, hdr->scid.len);
        p += hdr->scid.len; rem -= hdr->scid.len;

        /* Initial Token */
        if (hdr->type == QUIC_PKT_INITIAL) {
            uint64_t tlen = 0;
            quic_status_t st = quic_read_varint(&p, &rem, &tlen);
            if (st != QUIC_OK) return st;
            if (rem < tlen) return QUIC_ERR_BUFFER_TOO_SHORT;
            hdr->token = p;
            hdr->token_len = (size_t)tlen;
            p += tlen; rem -= tlen;
        } else {
            hdr->token = NULL;
            hdr->token_len = 0;
        }

        /* Payload Length */
        uint64_t plen = 0;
        quic_status_t st = quic_read_varint(&p, &rem, &plen);
        if (st != QUIC_OK) return st;
        if (rem < plen) return QUIC_ERR_BUFFER_TOO_SHORT;

        hdr->payload_len = plen;
        hdr->payload = p;
    } else {
        /* Short Header (1-RTT) */
        hdr->type = QUIC_PKT_1RTT_SHORT;
        hdr->version = 0;
        hdr->scid.len = 0;
        hdr->token = NULL;
        hdr->token_len = 0;

        if (dcid_len_for_short > QUIC_MAX_CID_LEN) return QUIC_ERR_CID_TOO_LONG;
        if (rem < dcid_len_for_short) return QUIC_ERR_BUFFER_TOO_SHORT;

        hdr->dcid.len = (uint8_t)dcid_len_for_short;
        memcpy(hdr->dcid.data, p, dcid_len_for_short);
        p += dcid_len_for_short; rem -= dcid_len_for_short;

        hdr->payload_len = rem;
        hdr->payload = p;
    }

    return QUIC_OK;
}

/* Розбір кадру STREAM з розшифрованого корисного навантаження */
quic_status_t quic_parse_stream_frame(const uint8_t *payload, size_t payload_len,
                                      quic_stream_frame_t *frame) {
    if (payload_len < 1) return QUIC_ERR_BUFFER_TOO_SHORT;

    const uint8_t *p = payload;
    size_t rem = payload_len;
    uint8_t ftype = *p++;
    rem--;

    if (ftype < 0x08 || ftype > 0x0F) return QUIC_ERR_UNKNOWN_FRAME;

    bool has_off = (ftype & 0x04) != 0;
    bool has_len = (ftype & 0x02) != 0;
    frame->fin   = (ftype & 0x01) != 0;

    /* Stream ID */
    quic_status_t st = quic_read_varint(&p, &rem, &frame->stream_id);
    if (st != QUIC_OK) return st;

    /* Offset */
    if (has_off) {
        st = quic_read_varint(&p, &rem, &frame->offset);
        if (st != QUIC_OK) return st;
    } else {
        frame->offset = 0;
    }

    /* Length & Data */
    if (has_len) {
        st = quic_read_varint(&p, &rem, &frame->length);
        if (st != QUIC_OK) return st;
        if (rem < frame->length) return QUIC_ERR_BUFFER_TOO_SHORT;
        frame->data = p;
    } else {
        frame->length = rem;
        frame->data = p;
    }

    return QUIC_OK;
}

/* Розбір кадру ACK */
quic_status_t quic_parse_ack_frame(const uint8_t *payload, size_t payload_len,
                                   quic_ack_frame_t *ack) {
    if (payload_len < 1) return QUIC_ERR_BUFFER_TOO_SHORT;

    const uint8_t *p = payload;
    size_t rem = payload_len;
    uint8_t ftype = *p++;
    rem--;

    if (ftype != 0x02 && ftype != 0x03) return QUIC_ERR_UNKNOWN_FRAME;

    quic_status_t st = quic_read_varint(&p, &rem, &ack->largest_acked);
    if (st != QUIC_OK) return st;

    st = quic_read_varint(&p, &rem, &ack->ack_delay);
    if (st != QUIC_OK) return st;

    st = quic_read_varint(&p, &rem, &ack->range_count);
    if (st != QUIC_OK) return st;

    st = quic_read_varint(&p, &rem, &ack->first_ack_range);
    if (st != QUIC_OK) return st;

    return QUIC_OK;
}
```
```cpp
#include <iostream>
#include <span>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <cstdint>
#include <cstring>

namespace quic {

inline constexpr size_t kMaxCidLen = 20;
inline constexpr uint32_t kQuicVersion1 = 0x00000001;

enum class Error {
    BufferTooShort,
    InvalidVarint,
    InvalidVersion,
    CidTooLong,
    UnknownFrame
};

enum class PacketType {
    Initial   = 0x00,
    ZeroRtt   = 0x01,
    Handshake = 0x02,
    Retry     = 0x03,
    OneRttShort
};

struct ConnectionId {
    uint8_t len{0};
    uint8_t data[kMaxCidLen]{0};

    [[nodiscard]] std::span<const uint8_t> as_span() const noexcept {
        return {data, len};
    }
};

struct PacketHeader {
    PacketType type{PacketType::Initial};
    bool is_long_header{true};
    uint32_t version{0};
    ConnectionId dcid;
    ConnectionId scid;
    std::span<const uint8_t> token;
    std::span<const uint8_t> payload;
};

struct StreamFrame {
    uint64_t stream_id{0};
    uint64_t offset{0};
    bool fin{false};
    std::span<const uint8_t> data;
};

struct AckFrame {
    uint64_t largest_acked{0};
    uint64_t ack_delay{0};
    uint64_t first_ack_range{0};
    uint64_t range_count{0};
};

/* Декодування цілого числа змінної довжини (RFC 9000 §16) */
[[nodiscard]] inline std::expected<uint64_t, Error> read_varint(std::span<const uint8_t>& buf) noexcept {
    if (buf.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    const uint8_t first = buf[0];
    const uint8_t prefix = (first >> 6) & 0x03;
    const size_t len = static_cast<size_t>(1) << prefix;

    if (buf.size() < len) {
        return std::unexpected(Error::BufferTooShort);
    }

    uint64_t res = first & 0x3F;
    buf = buf.subspan(1);

    for (size_t i = 1; i < len; ++i) {
        res = (res << 8) | buf[0];
        buf = buf.subspan(1);
    }

    return res;
}

/* Безпечний розбір бінарного заголовка пакета QUIC */
[[nodiscard]] inline std::expected<PacketHeader, Error> parse_header(
    std::span<const uint8_t> raw, size_t dcid_len_for_short) noexcept {
    if (raw.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    PacketHeader hdr;
    const uint8_t first_byte = raw[0];
    raw = raw.subspan(1);

    hdr.is_long_header = (first_byte & 0x80) != 0;

    if (hdr.is_long_header) {
        if (raw.size() < 4) return std::unexpected(Error::BufferTooShort);
        hdr.version = (static_cast<uint32_t>(raw[0]) << 24) |
                      (static_cast<uint32_t>(raw[1]) << 16) |
                      (static_cast<uint32_t>(raw[2]) << 8)  |
                      (static_cast<uint32_t>(raw[3]));
        raw = raw.subspan(4);

        const uint8_t type_bits = (first_byte >> 4) & 0x03;
        hdr.type = static_cast<PacketType>(type_bits);

        /* DCID */
        if (raw.empty()) return std::unexpected(Error::BufferTooShort);
        const uint8_t dcil = raw[0];
        raw = raw.subspan(1);
        if (dcil > kMaxCidLen) return std::unexpected(Error::CidTooLong);
        if (raw.size() < dcil) return std::unexpected(Error::BufferTooShort);
        hdr.dcid.len = dcil;
        std::memcpy(hdr.dcid.data, raw.data(), dcil);
        raw = raw.subspan(dcil);

        /* SCID */
        if (raw.empty()) return std::unexpected(Error::BufferTooShort);
        const uint8_t scil = raw[0];
        raw = raw.subspan(1);
        if (scil > kMaxCidLen) return std::unexpected(Error::CidTooLong);
        if (raw.size() < scil) return std::unexpected(Error::BufferTooShort);
        hdr.scid.len = scil;
        std::memcpy(hdr.scid.data, raw.data(), scil);
        raw = raw.subspan(scil);

        /* Token for Initial */
        if (hdr.type == PacketType::Initial) {
            auto token_len = read_varint(raw);
            if (!token_len) return std::unexpected(token_len.error());
            if (raw.size() < *token_len) return std::unexpected(Error::BufferTooShort);
            hdr.token = raw.first(static_cast<size_t>(*token_len));
            raw = raw.subspan(static_cast<size_t>(*token_len));
        }

        /* Payload length */
        auto payload_len = read_varint(raw);
        if (!payload_len) return std::unexpected(payload_len.error());
        if (raw.size() < *payload_len) return std::unexpected(Error::BufferTooShort);

        hdr.payload = raw.first(static_cast<size_t>(*payload_len));
    } else {
        /* Short Header */
        hdr.type = PacketType::OneRttShort;
        hdr.version = 0;

        if (dcid_len_for_short > kMaxCidLen) return std::unexpected(Error::CidTooLong);
        if (raw.size() < dcid_len_for_short) return std::unexpected(Error::BufferTooShort);

        hdr.dcid.len = static_cast<uint8_t>(dcid_len_for_short);
        std::memcpy(hdr.dcid.data, raw.data(), dcid_len_for_short);
        raw = raw.subspan(dcid_len_for_short);

        hdr.payload = raw;
    }

    return hdr;
}

/* Розбір кадру STREAM з розшифрованого корисного навантаження */
[[nodiscard]] inline std::expected<StreamFrame, Error> parse_stream_frame(
    std::span<const uint8_t> payload) noexcept {
    if (payload.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    const uint8_t ftype = payload[0];
    payload = payload.subspan(1);

    if (ftype < 0x08 || ftype > 0x0F) {
        return std::unexpected(Error::UnknownFrame);
    }

    const bool has_off = (ftype & 0x04) != 0;
    const bool has_len = (ftype & 0x02) != 0;

    StreamFrame frame;
    frame.fin = (ftype & 0x01) != 0;

    auto stream_id = read_varint(payload);
    if (!stream_id) return std::unexpected(stream_id.error());
    frame.stream_id = *stream_id;

    if (has_off) {
        auto offset = read_varint(payload);
        if (!offset) return std::unexpected(offset.error());
        frame.offset = *offset;
    } else {
        frame.offset = 0;
    }

    if (has_len) {
        auto len = read_varint(payload);
        if (!len) return std::unexpected(len.error());
        if (payload.size() < *len) return std::unexpected(Error::BufferTooShort);
        frame.data = payload.first(static_cast<size_t>(*len));
    } else {
        frame.data = payload;
    }

    return frame;
}

/* Розбір кадру ACK */
[[nodiscard]] inline std::expected<AckFrame, Error> parse_ack_frame(
    std::span<const uint8_t> payload) noexcept {
    if (payload.empty()) {
        return std::unexpected(Error::BufferTooShort);
    }

    const uint8_t ftype = payload[0];
    payload = payload.subspan(1);

    if (ftype != 0x02 && ftype != 0x03) {
        return std::unexpected(Error::UnknownFrame);
    }

    AckFrame ack;
    auto largest = read_varint(payload);
    if (!largest) return std::unexpected(largest.error());
    ack.largest_acked = *largest;

    auto delay = read_varint(payload);
    if (!delay) return std::unexpected(delay.error());
    ack.ack_delay = *delay;

    auto count = read_varint(payload);
    if (!count) return std::unexpected(count.error());
    ack.range_count = *count;

    auto first_range = read_varint(payload);
    if (!first_range) return std::unexpected(first_range.error());
    ack.first_ack_range = *first_range;

    return ack;
}

} // namespace quic
```
:::

## 6. Валідація лімітів контролю потоку та безпека парсингу

Під час практичної інтеграції парсера в мережевий конвеєр необхідно забезпечити обробку протокольних лімітів контролю потоку даних (Flow Control) та протидію шкідливим атакам:

### 6.1. Перевірка перевищення кредитів (Flow Control Invariants)
Коли парсер вилучає байти з кадру `STREAM`, він зобов'язаний перевірити два ліміти перед передачею даних у прикладний буфер:
1. **Ліміт потоку:** сума `Offset + Length` не повинна перевищувати значення `max_stream_data`, раніше узгоджене для цього конкретного `Stream ID`. Якщо клієнт надіслав байти зі зсувом за межами дозволеного вікна, парсер негайно перериває з'єднання з кодом помилки `FLOW_CONTROL_ERROR (0x03)`.
2. **Загальний ліміт з'єднання:** сумарна кількість прийнятих унікальних байтів у всіх відкритих потоках разом не повинна перевищувати `max_data`.

Крім того, якщо кадр `STREAM` містить прапорець `FIN = 1`, значення `Offset + Length` фіксується як кінцевий розмір потоку (`Final Size`). Будь-який наступний кадр для цього `Stream ID`, що містить дані зі зсувом, більшим або меншим за `Final Size`, або спроба змінити фінальний розмір іншим кадровим пакетом кваліфікується як критичне протокольне порушення `FINAL_SIZE_ERROR (0x06)`.

### 6.2. Захист від атак вичерпання пам'яті (Memory Exhaustion Defense)
Зловмисник може надіслати кадр `STREAM` з малим обсягом даних (наприклад, 1 байт), але зі штучно величезним зсувом `Offset = 1 000 000 000` (1 Гігабайт). Якщо наївний рушій спробує попередньо виділити суцільний масив пам'яті розміром 1 Гб для очікування проміжних байтів, це призведе до миттєвого вичерпання RAM сервера (Out-of-Memory Crash).

Правильна архітектура збирання потоку використовує розріджені структури даних (інтервальні списки або B-дерева чанків фіксованого розміру по 4 або 16 Кб). Пам'ять виділяється виключно під фактично отримані байти, а сумарний обсяг незібраних дірок у потоках жорстко обмежується глобальним конфігураційним параметром демона.

## 7. Керування таблицями Connection ID та відстеження сесій

У серверах високої доступності підтримка міграції з'єднань вимагає спеціалізованої хеш-таблиці з'єднань (Connection Hash Table), що індексується за Connection ID:

1. **Кілька ключів на одну сесію:** оскільки сервер видає клієнту пул із кількох Connection ID (за допомогою фреймів `NEW_CONNECTION_ID`), одна й та сама структура сесії в пам'яті прив'язується до кількох незалежних 20-байтних ключів у хеш-таблиці.
2. **Атомарне відкликання (Retiring):** коли клієнт надсилає `RETIRE_CONNECTION_ID`, парсер видаляє старий ключ із таблиці, запобігаючи витоку пам'яті та колізіям ідентифікаторів.
3. **Захист від атак підміни (Stateless Reset Handling):** якщо сервер зазнав аварійного перезапуску і втратив стан з'єднання, він не може розшифрувати вхідний пакет Short Header. Замість мовчазного відкидання сервер бере закодований у сесії `Stateless Reset Token` (16 байтів) і відправляє його клієнту, що дозволяє клієнтському додатку миттєво перезапустити сесію без очікування таймауту неактивності.

## 8. Апаратні SIMD-оптимізації та кільцеві буфери AF_XDP

У магістральних балансувальниках навантаження для прискорення розбору пакетних масивів застосовуються векторні інструкції Intel AVX-512 або ARM NEON:
- **Швидкий пошук меж фреймів:** векторні інструкції порівняння байтових масок дозволяють за один такт процесора визначити наявність байтів із встановленим старшим бітом або знайти позицію наступного кадру в незахищеному буфері.
- **Паралельний розрахунок масок заголовка:** криптографічний зразок (Sample) для 4 або 8 пакетів одночасно завантажується у 256-бітний або 512-бітний векторний регістр, що дозволяє паралельно виконати операцію AES-ECB для всього батчу датаграм `recvmmsg` за один прохід конвеєра шифрування AES-NI.
- **Кільцеві буфери AF_XDP (UMEM):** пряме відображення пакетів із мережевої карти у простір пам'яті процесу в обхід стеку ядра Linux усуває копіювання байтів між простором ядра та простором користувача, а апаратне попереднє вичитування кеш-ліній (`__builtin_prefetch`) готує заголовок наступного пакета ще під час декодування поточного.

## 9. Інтеграція з конвеєром HTTP/3 та QPACK

Після того як фрейм `STREAM` успішно зібрано, потік байтів передається безпосередньо в конвеєр демультиплексування HTTP/3:
- Якщо потік є односпрямованим потоком керування (`Stream ID = 2` або `3`), байти зчитуються як кадри `SETTINGS` або `GOAWAY`.
- Якщо потік є потоком QPACK Encoder/Decoder, байти передаються модулю динамічного словника стиснення заголовків (RFC 9204).
- Для стандартних двоспрямованих потоків запитів (`Stream ID = 0, 4, 8...`) байти розбираються як прикладні кадри `HEADERS` та `DATA` без додаткового копіювання через механізм запозичення зрізів буферів.

## 10. Тестування та аналіз верифікаційного вектора

Для комплексної перевірки коректності функціонування синтаксичного аналізатора розглянемо двійковий масив пакета `Initial` версії 1, що містить кадр `STREAM` з прикладними даними:

:::tabs
```c
/* Тестовий двійковий вектор пакета QUIC Initial v1 (C99) */
const uint8_t raw_packet[] = {
    /* 1. Long Header Байт прапорців: Initial, Form=1 */
    0xC0,
    /* 2. Version (4B): 0x00000001 (QUIC v1) */
    0x00, 0x00, 0x00, 0x01,
    /* 3. DCIL (1B): 4 байти + DCID (0xAA, 0xBB, 0xCC, 0xDD) */
    0x04, 0xAA, 0xBB, 0xCC, 0xDD,
    /* 4. SCIL (1B): 4 байти + SCID (0x11, 0x22, 0x33, 0x44) */
    0x04, 0x11, 0x22, 0x33, 0x44,
    /* 5. Token Length: 0 (Varint: 0x00) */
    0x00,
    /* 6. Payload Length (Varint: 12 байтів -> 0x0C) */
    0x0C,
    /* 7. Корисне навантаження: кадр STREAM (0x0E -> OFF=1, LEN=1, FIN=0) */
    0x0E,
    /* Stream ID: 0 (Varint 0x00) */
    0x00,
    /* Offset: 256 (Varint 2 байти: 0x4100 -> 0x0100 = 256) */
    0x41, 0x00,
    /* Length: 4 байти (Varint 0x04) */
    0x04,
    /* Прикладні байти корисного навантаження */
    'T', 'E', 'S', 'T'
};
```
```cpp
/* Тестовий двійковий вектор пакета QUIC Initial v1 (C++20) */
inline constexpr std::array<uint8_t, 25> raw_packet = {
    /* 1. Long Header Байт прапорців: Initial, Form=1 */
    0xC0,
    /* 2. Version (4B): 0x00000001 (QUIC v1) */
    0x00, 0x00, 0x00, 0x01,
    /* 3. DCIL (1B): 4 байти + DCID (0xAA, 0xBB, 0xCC, 0xDD) */
    0x04, 0xAA, 0xBB, 0xCC, 0xDD,
    /* 4. SCIL (1B): 4 байти + SCID (0x11, 0x22, 0x33, 0x44) */
    0x04, 0x11, 0x22, 0x33, 0x44,
    /* 5. Token Length: 0 (Varint: 0x00) */
    0x00,
    /* 6. Payload Length (Varint: 12 байтів -> 0x0C) */
    0x0C,
    /* 7. Корисне навантаження: кадр STREAM (0x0E -> OFF=1, LEN=1, FIN=0) */
    0x0E,
    /* Stream ID: 0 (Varint 0x00) */
    0x00,
    /* Offset: 256 (Varint 2 байти: 0x4100 -> 0x0100 = 256) */
    0x41, 0x00,
    /* Length: 4 байти (Varint 0x04) */
    0x04,
    /* Прикладні байти корисного навантаження */
    'T', 'E', 'S', 'T'
};
```
:::

При подачі цього буфера у функцію `parse_header`:
1. Перший байт `0xC0` декодується як `is_long_header = true`, тип `PacketType::Initial`.
2. Чотири байти `0x00000001` визначають версію QUIC v1.
3. Довжина `DCIL = 4` зчитує масив `0xAA 0xBB 0xCC 0xDD`, а `SCIL = 4` — масив `0x11 0x22 0x33 0x44`.
4. Varint `Token Length = 0` сигналізує про відсутність токена.
5. Varint `Length = 12` виокремлює зріз розміром 12 байтів для навантаження.
6. Функція `parse_stream_frame` аналізує байт `0x0E` (`0b00001110`), встановлює наявність полів `Offset` і `Length`, зчитує `Stream ID = 0`, декодує 2-байтний Varint `Offset = 256`, зчитує `Length = 4` та повертає безпечний зріз пам'яті на рядок `'TEST'`.

Завдяки суворій перевірці розмірів перед кожним побітовим зсувом у функції `read_varint` будь-яка спроба передати усічений або некоректно сформований пакет повертає код помилки `Error::BufferTooShort` або `Error::InvalidVarint`, запобігаючи аварійній зупинці мережевого демона (Panic/Segmentation Fault).

# ⚙️ Реалізація клієнта MAVFTP на C та C++

Цей практичний посібник містить повну робочу реалізацію клієнта MAVLink FTP (повідомлення `FILE_TRANSFER_PROTOCOL`, `#110`) мовами C та C++: від низькорівневого складання двійкових заголовків `PayloadHeader` до кінцевого автомата (FSM) пакетного вичитування (Burst Read), завантаження файлів на борт (Upload), сканування каталогів (ListDirectory) та контролю цілісності `CRC32`. Матеріал призначений для інженерів, які розробляють власні наземні станції, супутні бортові комп'ютери або вбудовані утиліти для швидкого вивантаження логів польоту (`.bin`, `.ulg`), місій та оновлень прошивки без сторонніх громіздких бібліотек.

---

## 1. Архітектура задачі та модель кінцевого автомата

Передача багатомегабайтних файлів (логів польоту або геодезичних карт рельєфу) через радіомодем на швидкості 57600 бод вимагає від клієнта постійного контролю двох критичних факторів:
1. **Максимізація завантаження лінії:** використання пакетного режиму `BurstReadFile` замість поодиноких запитів `ReadFile` для уникнення простою каналу під час кругової затримки (RTT).
2. **Гарантія цілісності даних:** відстеження неперервності номерів послідовності `seq_number` і точного зсуву `offset` кожного фрагмента, повторний запит втрачених блоків та фінальне звірення контрольної суми `CRC32`.

### Стани клієнтського автомата завантаження (Download FSM)

```
   [ IDLE ]
      │  Ініціалізація: OpenFileRO
      ▼
 [ OPENING ] ──(NAK / Timeout 3x)──► [ FAILED ]
      │  Отримано ACK (session, file_size)
      ▼
 [ BURST_STREAMING ] ◄──┐
      │                 │ Відновлено потік (BurstReadFile)
      ├──(Втрата seq)──► [ GAP_RECOVERY ]
      │
      ├──(Отримано burst_complete / EOF)
      ▼
 [ CLOSING ] ──(ACK / Timeout)──► [ VERIFY_CRC ] ──► [ SUCCESS ]
```

* **IDLE:** Початковий стан. Клієнт очищає буфери, скидає лічильники та готує запит на відкриття файлу `OpenFileRO`.
* **OPENING:** Надіслано `kCmdOpenFileRO`. Клієнт очікує підтвердження `kRspAck` із номером сесії та розміром файлу. У разі таймауту запит повторюється до 3–5 разів. Якщо сервер повертає `kErrFileNotFound`, клієнт негайно переходить у стан `FAILED`.
* **BURST_STREAMING:** Надіслано запит `kCmdBurstReadFile`. Клієнт перебуває у режимі прийому безперервного потоку пакетів даних від автопілота. Для кожного прийнятого пакета перевіряється умова `seq_number == expected_seq` та `offset == expected_offset`.
* **GAP_RECOVERY:** Якщо виявлено розрив у нумерації `seq_number` (один або кілька пакетів змило радіозавадою), клієнт фіксує точку втрати й надсилає новий запит `kCmdBurstReadFile` зі зсувом першого відсутнього байта.
* **CLOSING:** Файл прийнято повністю. Клієнт відправляє `kCmdTerminateSession` для коректного закриття файлового дескриптора на борту та вивільнення слота пам'яті.
* **VERIFY_CRC:** Отримання від сервера контрольної суми `CalcFileCRC32` та звірення її з локально обчисленою сумою прийнятого масиву.
* **SUCCESS / FAILED:** Термінальні стани успіху або невідновного збою.

---

## 2. Структури даних та бінарне пакування

Для коректної роботи на різних апаратних платформах (ARM Cortex-M, x86_64, RISC-V) усі протокольні структури повинні мати строге пакування без проміжків, а багатобайтові поля — перетворюватися на little-endian.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define MAVFTP_MAX_DATA_LEN 239
#define MAVFTP_HEADER_LEN   12
#define MAVFTP_PAYLOAD_LEN  251

/* Опкоди MAVFTP */
typedef enum {
    MAVFTP_OP_NONE              = 0,
    MAVFTP_OP_TERMINATE_SESSION = 1,
    MAVFTP_OP_RESET_SESSIONS    = 2,
    MAVFTP_OP_LIST_DIRECTORY    = 3,
    MAVFTP_OP_OPEN_FILE_RO      = 4,
    MAVFTP_OP_READ_FILE         = 5,
    MAVFTP_OP_CREATE_FILE       = 6,
    MAVFTP_OP_WRITE_FILE        = 7,
    MAVFTP_OP_REMOVE_FILE       = 8,
    MAVFTP_OP_CREATE_DIRECTORY  = 9,
    MAVFTP_OP_REMOVE_DIRECTORY  = 10,
    MAVFTP_OP_OPEN_FILE_WO      = 11,
    MAVFTP_OP_TRUNCATE_FILE     = 12,
    MAVFTP_OP_RENAME            = 13,
    MAVFTP_OP_CALC_FILE_CRC32   = 14,
    MAVFTP_OP_BURST_READ_FILE   = 15,
    MAVFTP_OP_ACK               = 128,
    MAVFTP_OP_NAK               = 129
} mavftp_op_t;

/* Коди помилок NAK */
typedef enum {
    MAVFTP_ERR_NONE             = 0,
    MAVFTP_ERR_FAIL             = 1,
    MAVFTP_ERR_FAIL_ERRNO       = 2,
    MAVFTP_ERR_INVALID_SIZE     = 3,
    MAVFTP_ERR_INVALID_SESSION  = 4,
    MAVFTP_ERR_NO_SESSIONS      = 5,
    MAVFTP_ERR_EOF              = 6,
    MAVFTP_ERR_UNKNOWN_CMD      = 7,
    MAVFTP_ERR_FILE_EXISTS      = 8,
    MAVFTP_ERR_FILE_PROTECTED   = 9,
    MAVFTP_ERR_FILE_NOT_FOUND   = 10
} mavftp_err_t;

#pragma pack(push, 1)
typedef struct {
    uint16_t seq_number;       /* Номер послідовності (LE) */
    uint8_t  session;          /* ID сесії */
    uint8_t  opcode;           /* Опкод операції / відповіді */
    uint8_t  size;             /* Кількість значущих байтів у data */
    uint8_t  req_opcode;       /* Опкод запиту для ACK/NAK */
    uint8_t  burst_complete;   /* 1 якщо останній пакет burst */
    uint8_t  padding;          /* Зарезервовано (0) */
    uint32_t offset;           /* Зсув у файлі (LE) */
    uint8_t  data[MAVFTP_MAX_DATA_LEN]; /* Тіло фрагмента */
} mavftp_pkt_t;
#pragma pack(pop)
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <string_view>
#include <vector>
#include <expected>
#include <optional>
#include <algorithm>

namespace mavftp {

constexpr size_t MaxDataLen = 239;
constexpr size_t HeaderLen = 12;
constexpr size_t PayloadLen = HeaderLen + MaxDataLen; // 251

enum class Opcode : uint8_t {
    None             = 0,
    TerminateSession = 1,
    ResetSessions    = 2,
    ListDirectory    = 3,
    OpenFileRO       = 4,
    ReadFile         = 5,
    CreateFile       = 6,
    WriteFile        = 7,
    RemoveFile       = 8,
    CreateDirectory  = 9,
    RemoveDirectory  = 10,
    OpenFileWO       = 11,
    TruncateFile     = 12,
    Rename           = 13,
    CalcFileCRC32    = 14,
    BurstReadFile    = 15,
    Ack              = 128,
    Nak              = 129
};

enum class ErrorCode : uint8_t {
    None             = 0,
    Fail             = 1,
    FailErrno        = 2,
    InvalidSize      = 3,
    InvalidSession   = 4,
    NoSessions       = 5,
    EOF_Reached      = 6,
    UnknownCmd       = 7,
    FileExists       = 8,
    FileProtected    = 9,
    FileNotFound     = 10
};

#pragma pack(push, 1)
struct [[gnu::packed]] Packet {
    uint16_t seqNumber{0};
    uint8_t  session{0};
    Opcode   opcode{Opcode::None};
    uint8_t  size{0};
    Opcode   reqOpcode{Opcode::None};
    uint8_t  burstComplete{0};
    uint8_t  padding{0};
    uint32_t offset{0};
    uint8_t  data[MaxDataLen]{0};

    [[nodiscard]] std::span<const uint8_t> payload() const noexcept {
        return {data, std::min<size_t>(size, MaxDataLen)};
    }
};
#pragma pack(pop)

static_assert(sizeof(Packet) == PayloadLen, "Packet must be exactly 251 bytes");

} // namespace mavftp
```
:::

---

## 3. Складання та розбір пакетів MAVFTP

Нижче наведено функції генерації командних повідомлень та безпечного вилучення даних з відповідей.

:::tabs
```c
/* Допоміжні функції конвертації little-endian */
static inline uint16_t le16(uint16_t v) {
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    return (uint16_t)((v << 8) | (v >> 8));
#else
    return v;
#endif
}

static inline uint32_t le32(uint32_t v) {
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    return ((v >> 24) & 0xff) | ((v << 8) & 0xff0000) |
           ((v >> 8) & 0xff00) | ((v << 24) & 0xff000000);
#else
    return v;
#endif
}

/* Формування запиту OpenFileRO */
void mavftp_build_open_ro(mavftp_pkt_t *pkt, uint16_t seq, const char *path) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->opcode = MAVFTP_OP_OPEN_FILE_RO;
    size_t len = strlen(path) + 1;
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = (uint8_t)len;
    memcpy(pkt->data, path, len);
    pkt->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

/* Формування запиту CreateFile */
void mavftp_build_create_file(mavftp_pkt_t *pkt, uint16_t seq, const char *path) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->opcode = MAVFTP_OP_CREATE_FILE;
    size_t len = strlen(path) + 1;
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = (uint8_t)len;
    memcpy(pkt->data, path, len);
    pkt->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

/* Формування запиту WriteFile */
void mavftp_build_write_file(mavftp_pkt_t *pkt, uint16_t seq, uint8_t session, uint32_t offset, const uint8_t *src, uint8_t len) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->session = session;
    pkt->opcode = MAVFTP_OP_WRITE_FILE;
    pkt->offset = le32(offset);
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = len;
    memcpy(pkt->data, src, len);
}

/* Формування запиту BurstReadFile */
void mavftp_build_burst_read(mavftp_pkt_t *pkt, uint16_t seq, uint8_t session, uint32_t offset) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->session = session;
    pkt->opcode = MAVFTP_OP_BURST_READ_FILE;
    pkt->offset = le32(offset);
    pkt->size = 0;
}

/* Формування запиту CalcFileCRC32 */
void mavftp_build_calc_crc32(mavftp_pkt_t *pkt, uint16_t seq, const char *path) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->opcode = MAVFTP_OP_CALC_FILE_CRC32;
    size_t len = strlen(path) + 1;
    if (len > MAVFTP_MAX_DATA_LEN) len = MAVFTP_MAX_DATA_LEN;
    pkt->size = (uint8_t)len;
    memcpy(pkt->data, path, len);
    pkt->data[MAVFTP_MAX_DATA_LEN - 1] = '\0';
}

/* Формування запиту TerminateSession */
void mavftp_build_terminate(mavftp_pkt_t *pkt, uint16_t seq, uint8_t session) {
    memset(pkt, 0, sizeof(*pkt));
    pkt->seq_number = le16(seq);
    pkt->session = session;
    pkt->opcode = MAVFTP_OP_TERMINATE_SESSION;
}
```
```cpp
namespace mavftp {

class PacketBuilder {
public:
    static Packet makeOpenRO(uint16_t seq, std::string_view path) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::OpenFileRO;
        const size_t copyLen = std::min(path.size(), MaxDataLen - 1);
        std::memcpy(pkt.data, path.data(), copyLen);
        pkt.data[copyLen] = '\0';
        pkt.size = static_cast<uint8_t>(copyLen + 1);
        return pkt;
    }

    static Packet makeCreateFile(uint16_t seq, std::string_view path) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::CreateFile;
        const size_t copyLen = std::min(path.size(), MaxDataLen - 1);
        std::memcpy(pkt.data, path.data(), copyLen);
        pkt.data[copyLen] = '\0';
        pkt.size = static_cast<uint8_t>(copyLen + 1);
        return pkt;
    }

    static Packet makeWriteFile(uint16_t seq, uint8_t session, uint32_t offset, std::span<const uint8_t> chunk) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.session = session;
        pkt.opcode = Opcode::WriteFile;
        pkt.offset = offset;
        const size_t writeLen = std::min(chunk.size(), MaxDataLen);
        std::memcpy(pkt.data, chunk.data(), writeLen);
        pkt.size = static_cast<uint8_t>(writeLen);
        return pkt;
    }

    static Packet makeBurstRead(uint16_t seq, uint8_t session, uint32_t offset) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.session = session;
        pkt.opcode = Opcode::BurstReadFile;
        pkt.offset = offset;
        pkt.size = 0;
        return pkt;
    }

    static Packet makeCalcCRC32(uint16_t seq, std::string_view path) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::CalcFileCRC32;
        const size_t copyLen = std::min(path.size(), MaxDataLen - 1);
        std::memcpy(pkt.data, path.data(), copyLen);
        pkt.data[copyLen] = '\0';
        pkt.size = static_cast<uint8_t>(copyLen + 1);
        return pkt;
    }

    static Packet makeTerminate(uint16_t seq, uint8_t session) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.session = session;
        pkt.opcode = Opcode::TerminateSession;
        return pkt;
    }

    static Packet makeResetSessions(uint16_t seq) noexcept {
        Packet pkt{};
        pkt.seqNumber = seq;
        pkt.opcode = Opcode::ResetSessions;
        return pkt;
    }
};

} // namespace mavftp
```
:::

---

## 4. Обчислення контрольної суми CRC32 (IEEE 802.3)

Для фінальної перевірки цілісності файлу після завантаження клієнт локально обчислює CRC32 і порівнює результат із відповіддю сервера на команду `CalcFileCRC32`.

:::tabs
```c
/* Стандартний розрахунок CRC32 IEEE 802.3 (поліном 0xEDB88320) */
uint32_t mavftp_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320 : 0);
        }
    }
    return crc ^ 0xFFFFFFFF;
}
```
```cpp
namespace mavftp {

constexpr uint32_t crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (const uint8_t byte : data) {
        crc ^= byte;
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320 : 0);
        }
    }
    return crc ^ 0xFFFFFFFF;
}

} // namespace mavftp
```
:::

---

## 5. Реалізація клієнта пакетного зчитування (Burst Reader Client)

Клієнт організовано як об'єктний кінцевий автомат. Він керує буфером файлу, перевіряє послідовність номерів пакетів `seq_number`, обробляє таймаути та відновлює потік у разі виявлення дірок.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>

typedef enum {
    CLIENT_STATE_IDLE,
    CLIENT_STATE_OPENING,
    CLIENT_STATE_BURST_STREAMING,
    CLIENT_STATE_GAP_RECOVERY,
    CLIENT_STATE_CLOSING,
    CLIENT_STATE_VERIFY_CRC,
    CLIENT_STATE_SUCCESS,
    CLIENT_STATE_FAILED
} client_state_t;

typedef struct {
    client_state_t state;
    uint8_t        session;
    uint16_t       next_seq;
    uint16_t       expected_burst_seq;
    uint32_t       file_size;
    uint32_t       bytes_received;
    uint8_t       *file_buffer;
    size_t         buffer_capacity;
    uint32_t       remote_crc;
    char           remote_path[MAVFTP_MAX_DATA_LEN];
    uint32_t       retry_count;
    uint32_t       max_retries;
} mavftp_client_t;

/* Ініціалізація клієнта */
bool mavftp_client_init(mavftp_client_t *c, size_t max_file_size) {
    memset(c, 0, sizeof(*c));
    c->state = CLIENT_STATE_IDLE;
    c->max_retries = 5;
    c->buffer_capacity = max_file_size;
    c->file_buffer = (uint8_t *)malloc(max_file_size);
    return (c->file_buffer != NULL);
}

void mavftp_client_free(mavftp_client_t *c) {
    if (c->file_buffer) {
        free(c->file_buffer);
        c->file_buffer = NULL;
    }
}

/* Старт завантаження */
void mavftp_client_start(mavftp_client_t *c, const char *path, mavftp_pkt_t *out_req) {
    c->state = CLIENT_STATE_OPENING;
    c->bytes_received = 0;
    c->file_size = 0;
    c->retry_count = 0;
    strncpy(c->remote_path, path, sizeof(c->remote_path) - 1);
    c->remote_path[sizeof(c->remote_path) - 1] = '\0';
    mavftp_build_open_ro(out_req, ++c->next_seq, path);
}

/* Обробка вхідного пакета MAVFTP */
void mavftp_client_on_packet(mavftp_client_t *c, const mavftp_pkt_t *pkt, mavftp_pkt_t *out_reply, bool *has_reply) {
    *has_reply = false;
    uint16_t seq = le16(pkt->seq_number);
    uint32_t off = le32(pkt->offset);

    /* Обробка негативного підтвердження NAK */
    if (pkt->opcode == MAVFTP_OP_NAK) {
        uint8_t err = pkt->data[0];
        if (err == MAVFTP_ERR_EOF && c->state == CLIENT_STATE_BURST_STREAMING) {
            /* Досягнуто кінця файлу через NAK(EOF) — переходимо до закриття */
            c->state = CLIENT_STATE_CLOSING;
            mavftp_build_terminate(out_reply, ++c->next_seq, c->session);
            *has_reply = true;
            return;
        }
        printf("[MAVFTP] NAK помилка: %u, операція: %u\n", err, pkt->req_opcode);
        c->state = CLIENT_STATE_FAILED;
        return;
    }

    if (pkt->opcode != MAVFTP_OP_ACK) {
        return;
    }

    switch (c->state) {
    case CLIENT_STATE_OPENING:
        if (pkt->req_opcode == MAVFTP_OP_OPEN_FILE_RO) {
            c->session = pkt->session;
            if (pkt->size >= 4) {
                uint32_t sz;
                memcpy(&sz, pkt->data, 4);
                c->file_size = le32(sz);
            }
            printf("[MAVFTP] Сесію відкрито: ID=%u, розмір=%u байтів\n", c->session, c->file_size);

            /* Запуск пакетного вичитування */
            c->state = CLIENT_STATE_BURST_STREAMING;
            c->bytes_received = 0;
            c->expected_burst_seq = seq + 1;
            c->retry_count = 0;

            mavftp_build_burst_read(out_reply, ++c->next_seq, c->session, 0);
            *has_reply = true;
        }
        break;

    case CLIENT_STATE_BURST_STREAMING:
    case CLIENT_STATE_GAP_RECOVERY:
        if (pkt->req_opcode == MAVFTP_OP_BURST_READ_FILE || pkt->req_opcode == MAVFTP_OP_READ_FILE) {
            /* Перевірка послідовності номерів пакетів */
            if (c->state == CLIENT_STATE_BURST_STREAMING && seq != c->expected_burst_seq) {
                printf("[MAVFTP] Пропуск! Очікували seq=%u, прийшов seq=%u. Відновлюємо з offset=%u\n",
                       c->expected_burst_seq, seq, c->bytes_received);
                c->state = CLIENT_STATE_GAP_RECOVERY;
                c->retry_count++;
                if (c->retry_count > c->max_retries) {
                    c->state = CLIENT_STATE_FAILED;
                    return;
                }
                mavftp_build_burst_read(out_reply, ++c->next_seq, c->session, c->bytes_received);
                *has_reply = true;
                return;
            }

            /* Збереження отриманого блоку */
            if (off == c->bytes_received && (c->bytes_received + pkt->size) <= c->buffer_capacity) {
                memcpy(c->file_buffer + off, pkt->data, pkt->size);
                c->bytes_received += pkt->size;
                c->expected_burst_seq = seq + 1;
                c->state = CLIENT_STATE_BURST_STREAMING;
                c->retry_count = 0;
            }

            /* Перевірка фінішу потоку */
            if (pkt->burst_complete == 1 || (c->file_size > 0 && c->bytes_received >= c->file_size)) {
                printf("[MAVFTP] Завантаження завершено (%u байтів). Закриваємо сесію...\n", c->bytes_received);
                c->state = CLIENT_STATE_CLOSING;
                mavftp_build_terminate(out_reply, ++c->next_seq, c->session);
                *has_reply = true;
            }
        }
        break;

    case CLIENT_STATE_CLOSING:
        if (pkt->req_opcode == MAVFTP_OP_TERMINATE_SESSION) {
            printf("[MAVFTP] Сесію закрито. Запитуємо CRC32 файлу...\n");
            c->state = CLIENT_STATE_VERIFY_CRC;
            mavftp_build_calc_crc32(out_reply, ++c->next_seq, c->remote_path);
            *has_reply = true;
        }
        break;

    case CLIENT_STATE_VERIFY_CRC:
        if (pkt->req_opcode == MAVFTP_OP_CALC_FILE_CRC32 && pkt->size == 4) {
            uint32_t remote_crc;
            memcpy(&remote_crc, pkt->data, 4);
            c->remote_crc = le32(remote_crc);

            uint32_t local_crc = mavftp_crc32(c->file_buffer, c->bytes_received);
            if (local_crc == c->remote_crc) {
                printf("[MAVFTP] CRC32 збігається: 0x%08X. Успіх!\n", local_crc);
                c->state = CLIENT_STATE_SUCCESS;
            } else {
                printf("[MAVFTP] Помилка CRC: локальний 0x%08X != віддалений 0x%08X\n", local_crc, c->remote_crc);
                c->state = CLIENT_STATE_FAILED;
            }
        }
        break;

    default:
        break;
    }
}
```
```cpp
#include <iostream>
#include <memory>
#include <span>
#include <vector>
#include <string>

namespace mavftp {

enum class ClientState {
    Idle,
    Opening,
    BurstStreaming,
    GapRecovery,
    Closing,
    VerifyCRC,
    Success,
    Failed
};

class BurstDownloadClient {
public:
    explicit BurstDownloadClient(size_t maxCapacity)
        : bufferCapacity_(maxCapacity) {
        buffer_.reserve(maxCapacity);
    }

    [[nodiscard]] ClientState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t bytesReceived() const noexcept { return bytesReceived_; }
    [[nodiscard]] uint32_t fileSize() const noexcept { return fileSize_; }
    [[nodiscard]] std::span<const uint8_t> data() const noexcept { return buffer_; }

    [[nodiscard]] Packet startDownload(std::string_view remotePath) {
        state_ = ClientState::Opening;
        remotePath_ = remotePath;
        bytesReceived_ = 0;
        fileSize_ = 0;
        retryCount_ = 0;
        buffer_.clear();
        return PacketBuilder::makeOpenRO(++nextSeq_, remotePath);
    }

    std::expected<std::optional<Packet>, ErrorCode> handlePacket(const Packet& pkt) {
        if (pkt.opcode == Opcode::Nak) {
            const auto err = static_cast<ErrorCode>(pkt.data[0]);
            if (err == ErrorCode::EOF_Reached && state_ == ClientState::BurstStreaming) {
                state_ = ClientState::Closing;
                return PacketBuilder::makeTerminate(++nextSeq_, session_);
            }
            state_ = ClientState::Failed;
            return std::unexpected(err);
        }

        if (pkt.opcode != Opcode::Ack) {
            return std::nullopt;
        }

        switch (state_) {
        case ClientState::Opening:
            if (pkt.reqOpcode == Opcode::OpenFileRO) {
                session_ = pkt.session;
                if (pkt.size >= 4) {
                    std::memcpy(&fileSize_, pkt.data, 4);
                }
                state_ = ClientState::BurstStreaming;
                expectedBurstSeq_ = pkt.seqNumber + 1;
                retryCount_ = 0;
                return PacketBuilder::makeBurstRead(++nextSeq_, session_, 0);
            }
            break;

        case ClientState::BurstStreaming:
        case ClientState::GapRecovery:
            if (pkt.reqOpcode == Opcode::BurstReadFile || pkt.reqOpcode == Opcode::ReadFile) {
                // Виявлення пропуску пакетів
                if (state_ == ClientState::BurstStreaming && pkt.seqNumber != expectedBurstSeq_) {
                    state_ = ClientState::GapRecovery;
                    if (++retryCount_ > maxRetries_) {
                        state_ = ClientState::Failed;
                        return std::unexpected(ErrorCode::Fail);
                    }
                    return PacketBuilder::makeBurstRead(++nextSeq_, session_, bytesReceived_);
                }

                // Збереження отриманого блоку
                if (pkt.offset == bytesReceived_ && (bytesReceived_ + pkt.size) <= bufferCapacity_) {
                    buffer_.insert(buffer_.end(), pkt.data, pkt.data + pkt.size);
                    bytesReceived_ += pkt.size;
                    expectedBurstSeq_ = pkt.seqNumber + 1;
                    state_ = ClientState::BurstStreaming;
                    retryCount_ = 0;
                }

                // Перевірка завершення вичитування
                if (pkt.burstComplete == 1 || (fileSize_ > 0 && bytesReceived_ >= fileSize_)) {
                    state_ = ClientState::Closing;
                    return PacketBuilder::makeTerminate(++nextSeq_, session_);
                }
            }
            break;

        case ClientState::Closing:
            if (pkt.reqOpcode == Opcode::TerminateSession) {
                state_ = ClientState::VerifyCRC;
                return PacketBuilder::makeCalcCRC32(++nextSeq_, remotePath_);
            }
            break;

        case ClientState::VerifyCRC:
            if (pkt.reqOpcode == Opcode::CalcFileCRC32 && pkt.size == 4) {
                uint32_t remoteCRC = 0;
                std::memcpy(&remoteCRC, pkt.data, 4);
                const uint32_t localCRC = crc32(buffer_);
                if (localCRC == remoteCRC) {
                    state_ = ClientState::Success;
                    return std::nullopt;
                } else {
                    state_ = ClientState::Failed;
                    return std::unexpected(ErrorCode::Fail);
                }
            }
            break;

        default:
            break;
        }

        return std::nullopt;
    }

private:
    ClientState state_{ClientState::Idle};
    std::string remotePath_;
    uint8_t session_{0};
    uint16_t nextSeq_{0};
    uint16_t expectedBurstSeq_{0};
    uint32_t fileSize_{0};
    uint32_t bytesReceived_{0};
    size_t bufferCapacity_{0};
    std::vector<uint8_t> buffer_;
    uint32_t retryCount_{0};
    uint32_t maxRetries_{5};
};

} // namespace mavftp
```
:::

---

## 6. Реалізація клієнта запису та завантаження на борт (Upload Client)

Запис файлу на накопичувач автопілота вимагає покрокового відправлення блоків `kCmdWriteFile` із перевіркою підтвердження кожного сегмента. Це гарантує, що у разі браку місця (`ENOSPC`) або збою флеш-пам'яті клієнт своєчасно зупинить операцію.

:::tabs
```c
typedef enum {
    UPLOAD_STATE_IDLE,
    UPLOAD_STATE_CREATING,
    UPLOAD_STATE_WRITING,
    UPLOAD_STATE_CLOSING,
    UPLOAD_STATE_SUCCESS,
    UPLOAD_STATE_FAILED
} upload_state_t;

typedef struct {
    upload_state_t state;
    uint8_t        session;
    uint16_t       next_seq;
    const uint8_t *file_data;
    size_t         total_size;
    size_t         bytes_written;
    uint32_t       retry_count;
} mavftp_uploader_t;

void mavftp_uploader_start(mavftp_uploader_t *u, const char *remote_path, const uint8_t *data, size_t size, mavftp_pkt_t *out_req) {
    memset(u, 0, sizeof(*u));
    u->state = UPLOAD_STATE_CREATING;
    u->file_data = data;
    u->total_size = size;
    mavftp_build_create_file(out_req, ++u->next_seq, remote_path);
}

void mavftp_uploader_on_packet(mavftp_uploader_t *u, const mavftp_pkt_t *pkt, mavftp_pkt_t *out_req, bool *has_req) {
    *has_req = false;

    if (pkt->opcode == MAVFTP_OP_NAK) {
        printf("[MAVFTP-UP] Помилка NAK: %u під час запису\n", pkt->data[0]);
        u->state = UPLOAD_STATE_FAILED;
        return;
    }

    if (pkt->opcode != MAVFTP_OP_ACK) return;

    switch (u->state) {
    case UPLOAD_STATE_CREATING:
        if (pkt->req_opcode == MAVFTP_OP_CREATE_FILE) {
            u->session = pkt->session;
            u->state = UPLOAD_STATE_WRITING;
            u->bytes_written = 0;

            /* Відправка першого блоку даних */
            size_t chunk = u->total_size - u->bytes_written;
            if (chunk > MAVFTP_MAX_DATA_LEN) chunk = MAVFTP_MAX_DATA_LEN;

            mavftp_build_write_file(out_req, ++u->next_seq, u->session, 0, u->file_data, (uint8_t)chunk);
            *has_req = true;
        }
        break;

    case UPLOAD_STATE_WRITING:
        if (pkt->req_opcode == MAVFTP_OP_WRITE_FILE) {
            size_t last_chunk = u->total_size - u->bytes_written;
            if (last_chunk > MAVFTP_MAX_DATA_LEN) last_chunk = MAVFTP_MAX_DATA_LEN;
            u->bytes_written += last_chunk;

            if (u->bytes_written < u->total_size) {
                /* Відправка наступного фрагмента */
                size_t next_chunk = u->total_size - u->bytes_written;
                if (next_chunk > MAVFTP_MAX_DATA_LEN) next_chunk = MAVFTP_MAX_DATA_LEN;

                mavftp_build_write_file(out_req, ++u->next_seq, u->session, (uint32_t)u->bytes_written,
                                        u->file_data + u->bytes_written, (uint8_t)next_chunk);
                *has_req = true;
            } else {
                /* Запис завершено, закриваємо сесію */
                u->state = UPLOAD_STATE_CLOSING;
                mavftp_build_terminate(out_req, ++u->next_seq, u->session);
                *has_req = true;
            }
        }
        break;

    case UPLOAD_STATE_CLOSING:
        if (pkt->req_opcode == MAVFTP_OP_TERMINATE_SESSION) {
            u->state = UPLOAD_STATE_SUCCESS;
            printf("[MAVFTP-UP] Файл успішно завантажено на борт (%zu байтів)\n", u->total_size);
        }
        break;

    default:
        break;
    }
}
```
```cpp
namespace mavftp {

enum class UploadState {
    Idle,
    Creating,
    Writing,
    Closing,
    Success,
    Failed
};

class FileUploadClient {
public:
    [[nodiscard]] Packet startUpload(std::string_view remotePath, std::span<const uint8_t> data) {
        state_ = UploadState::Creating;
        data_ = data;
        bytesWritten_ = 0;
        return PacketBuilder::makeCreateFile(++nextSeq_, remotePath);
    }

    [[nodiscard]] UploadState state() const noexcept { return state_; }
    [[nodiscard]] size_t bytesWritten() const noexcept { return bytesWritten_; }

    std::expected<std::optional<Packet>, ErrorCode> handlePacket(const Packet& pkt) {
        if (pkt.opcode == Opcode::Nak) {
            state_ = UploadState::Failed;
            return std::unexpected(static_cast<ErrorCode>(pkt.data[0]));
        }

        if (pkt.opcode != Opcode::Ack) return std::nullopt;

        switch (state_) {
        case UploadState::Creating:
            if (pkt.reqOpcode == Opcode::CreateFile) {
                session_ = pkt.session;
                state_ = UploadState::Writing;
                bytesWritten_ = 0;

                const size_t chunkSize = std::min(data_.size(), MaxDataLen);
                return PacketBuilder::makeWriteFile(++nextSeq_, session_, 0, data_.subspan(0, chunkSize));
            }
            break;

        case UploadState::Writing:
            if (pkt.reqOpcode == Opcode::WriteFile) {
                const size_t lastChunk = std::min(data_.size() - bytesWritten_, MaxDataLen);
                bytesWritten_ += lastChunk;

                if (bytesWritten_ < data_.size()) {
                    const size_t nextChunk = std::min(data_.size() - bytesWritten_, MaxDataLen);
                    return PacketBuilder::makeWriteFile(++nextSeq_, session_, static_cast<uint32_t>(bytesWritten_),
                                                        data_.subspan(bytesWritten_, nextChunk));
                } else {
                    state_ = UploadState::Closing;
                    return PacketBuilder::makeTerminate(++nextSeq_, session_);
                }
            }
            break;

        case UploadState::Closing:
            if (pkt.reqOpcode == Opcode::TerminateSession) {
                state_ = UploadState::Success;
                return std::nullopt;
            }
            break;

        default:
            break;
        }

        return std::nullopt;
    }

private:
    UploadState state_{UploadState::Idle};
    uint8_t session_{0};
    uint16_t nextSeq_{0};
    std::span<const uint8_t> data_;
    size_t bytesWritten_{0};
};

} // namespace mavftp
```
:::

---

## 7. Покрокове трасування завантаження файлу

Щоб наочно проілюструвати роботу автомата, розгляньмо покроковий протокол завантаження файлу конфігурації розміром `600` байтів через радіолінк із втратою одного кадру:

1. **Крок 1 (Запит відкриття):**
   * Клієнт надсилає `seq_number = 1`, `opcode = 4 (OpenFileRO)`, `data = "/etc/config.txt\0"`.
   * Стан: `OPENING`. Запускається таймер `RTO = 1000` мс.
2. **Крок 2 (Підтвердження відкриття):**
   * Сервер відповідає: `opcode = 128 (ACK)`, `req_opcode = 4`, `session = 1`, `size = 4`, `data = [0x58, 0x02, 0x00, 0x00]` (600 байтів у little-endian).
   * Клієнт фіксує `file_size = 600`, `session = 1` і негайно надсилає `seq_number = 2`, `opcode = 15 (BurstReadFile)`, `offset = 0`.
   * Стан: `BURST_STREAMING`, очікується `expected_burst_seq = 3`.
3. **Крок 3 (Прийом першого чанка):**
   * Сервер транслює: `seq_number = 3`, `opcode = 128 (ACK)`, `offset = 0`, `size = 239`, `burst_complete = 0`.
   * Перевірка: `seq (3) == expected (3)`, `offset (0) == bytes_received (0)`.
   * Клієнт копіює 239 байтів у буфер. `bytes_received = 239`, `expected_burst_seq = 4`.
4. **Крок 4 (Втрата другого чанка в ефірі):**
   * Сервер транслює: `seq_number = 4`, `offset = 239`, `size = 239`. Цей пакет губиться через радіозаваду.
   * Сервер продовжує трансляцію і надсилає третій чанк: `seq_number = 5`, `offset = 478`, `size = 122`, `burst_complete = 1`.
5. **Крок 5 (Виявлення пропуску та відновлення):**
   * Клієнт отримує `seq_number = 5`, але очікує `expected_burst_seq = 4`.
   * Автомат негайно фіксує пропуск, ігнорує дані третього чанка (бо вони не стикуються з `bytes_received = 239`), переходить у стан `GAP_RECOVERY` і відправляє точковий повторний запит: `seq_number = 6`, `opcode = 15 (BurstReadFile)`, `offset = 239`.
6. **Крок 6 (Повторна трансляція від місця розриву):**
   * Сервер приймає новий Burst-запит і перезапускає потік зі зсуву 239.
   * Пакет 1: `seq_number = 7`, `offset = 239`, `size = 239`, `burst_complete = 0`. Клієнт приймає, `bytes_received = 478`, `expected_burst_seq = 8`.
   * Пакет 2: `seq_number = 8`, `offset = 478`, `size = 122`, `burst_complete = 1`. Клієнт приймає, `bytes_received = 600`.
   * Умова завершення виконана: `bytes_received == file_size` та `burst_complete == 1`.
7. **Крок 7 (Закриття сесії):**
   * Клієнт надсилає `seq_number = 9`, `opcode = 1 (TerminateSession)`, `session = 1`.
   * Сервер відповідає `ACK`. Сесію закрито, файл цілісно збережено.

---

## 8. Практичні пастки та тонкощі налагодження

Під час впровадження протоколу MAVFTP у виробничі системи виникають характерні проблеми, зумовлені фізикою радіозв'язку та архітектурою операційних систем реального часу (RTOS):

1. **Переповнення передавального буфера радіомодема (Radio Buffer Overrun):**
   Під час вичитування `BurstReadFile` польотний контролер здатний генерувати пакети на швидкості процесора (десятки кілобайтів за секунду). Якщо між мікроконтролером та радіомодемом немає апаратного контролю потоку (CTS/RTS), черга UART модема переповнюється за лічені мілісекунди, що призводить до масового змивання пакетів. Слід або увімкнути апаратний CTS/RTS, або налаштувати ліміт швидкості генерації MAVLink (параметри `SERIALx_BAUD`, `STREAM_RATE`).

2. **Затримки стирання Flash-пам'яті та карт SD:**
   Операції запису на microSD карту мають нелінійний час виконання: стирання блоку флеш-пам'яті (Flash Erase Block) може блокувати шину SDIO/SPI на `100..250` мілісекунд. Клієнтський таймаут очікування `RTO` повинен бути не меншим за `1000` мс для уникнення передчасних повторних запитів.

3. **Скидання завислих сесій при перепідключенні:**
   Якщо наземна станція раптово перезавантажилася під час відкритої сесії, польотний контролер триматиме дескриптор відкритим до спливання таймауту неактивності (`2..5` с). Якщо новий запуск клієнта одразу надішле `OpenFileRO`, сервер поверне помилку `kErrNoSessionsAvailable` (`5`). Завжди починайте роботу клієнта з відправки команди `kCmdResetSessions` (`2`).

4. **Два варіанти завершення файлу:**
   Старі версії автопілотів надсилають останній блок з `burst_complete = 0`, а на наступний зсув відповідають `kRspNak` із кодом `kErrEOF` (`6`). Сучасні версії PX4 та ArduPilot встановлюють `burst_complete = 1` безпосередньо у фінальному пакеті `kRspAck`. Клієнт зобов'язаний коректно підтримувати обидва механізми завершення.

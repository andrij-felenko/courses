# Протокол локального сервісного шлюзу для польового обслуговування

Цей документ визначає двійковий інтерфейс взаємодії (API) та протокольний контракт між польовим сервісним інструментом техніка (планшетом, оптичною зчитувальною голівкою або сервісним шлюзом) та ізольованим мікроконтролерним пристроєм для виконання автономного оновлення прошивки, діагностики та зняття аудиторських журналів.

Протокол розроблено для роботи поверх ненадійних або напівдуплексних фізичних інтерфейсів (Bluetooth Low Energy GATT, послідовна оптична шина IEC 62056-21, ізольований інтерфейс RS-485 Modbus або локальна точка доступу Wi-Fi SoftAP). Він забезпечує взаємну криптографічну автентифікацію, стійкість до раптового розриву зв'язку (англ. *resumable upload*) та гарантоване вивантаження звітів стану без ризику пошкодження робочого слота пам'яті.

---

### 1. Фізичні середовища та канальне обрамлення

У польових умовах сервісний шлюз стикається з трьома принципово різними середовищами передачі даних:
- **Послідовний напівдуплексний UART/RS-485:** застосовується під час підключення оптичної зчитувальної голівки або кабелю до клемної колодки. Канал схильний до байтових втрат через оптичні завади або перешкоди інверторів.
- **Bluetooth Low Energy (BLE 5.0):** застосовується для бездротового контакту з герметичними приладами без розбирання шафи. Обмін відбувається через дескриптори характеристик із контролем розміру MTU.
- **Локальна SoftAP точка доступу Wi-Fi:** контролер піднімає тимчасову мережу на кілька хвилин після піднесення магнітного ключа (геркона) або натискання сервісної кнопки.

Для уніфікації обробки на рівні прошивки протокол використовує двійкове обрамлення з байт-стафінгом COBS (Consistent Overhead Byte Stuffing). Це дозволяє чітко розрізняти межі пакетів у потоці байтів за допомогою єдиного роздільника `0x00`, гарантуючи, що всередині корисного навантаження нульовий байт ніколи не з'явиться у відкритому вигляді.

```
+---------------+---------------+----------------+-------------------+----------+---------------+
| SOF (0x00)    | Seq ID (1 Б)  | Opcode (1 Б)   | Payload Len (2 Б) | Payload  | CRC32 (4 Б)   |
+---------------+---------------+----------------+-------------------+----------+---------------+
```

#### Специфікація полів кадру:
- **`SOF` (Start of Frame, 1 байт):** маркер початку або роздільник пакетів (`0x00`).
- **`Seq ID` (Sequence Identifier, 1 байт):** монотонний лічильник кадру (0..255). Дозволяє приймачу миттєво відкидати дублікати пакетів при повторних передачах через таймаут.
- **`Opcode` (Operation Code, 1 байт):** код сервісної операції. Якщо старший біт `0x80` встановлено, кадр є відповіддю (`RESPONSE`), якщо скинуто — запитом (`COMMAND`).
- **`Payload Len` (Payload Length, 2 байти):** фактична кількість байтів корисного навантаження (формат Little-Endian, межа від 0 до 4096 байтів).
- **`Payload` (Змінний розмір):** тіло команди або параметри відповіді.
- **`CRC32` (4 байти):** апаратна або програмна контрольна сума полінома IEEE 802.3 (`0xEDB88320`), обчислена від полів `Seq ID .. Payload`. Забезпечує виявлення багатобітових спотворень на зашумлених польових лініях.

---

### 2. Таблиця кодів операцій (Opcodes)

| Opcode | Назва | Напрямок | Опис корисного навантаження |
| :--- | :--- | :--- | :--- |
| **`0x01`** | `CMD_DISCOVERY` | Шлюз → Вузол | Запит ідентифікації: `[Timestamp (4B), Nonce (16B)]`. |
| **`0x81`** | `RESP_DISCOVERY` | Вузол → Шлюз | Відповідь: `[Device_UID (8B), HW_ID (2B), Active_Ver (4B), Status (1B), Nonce (16B), Sig (64B)]`. |
| **`0x02`** | `CMD_AUTH_CHALLENGE`| Шлюз → Вузол | Сесійний виклик: `[Technician_ID (4B), Ephemeral_PubKey (32B), Token_Sig (64B)]`. |
| **`0x82`** | `RESP_AUTH_STATUS` | Вузол → Шлюз | Результат автентифікації: `[Status_Code (1B), Session_ID (4B), Device_Ephemeral_PubKey (32B)]`. |
| **`0x03`** | `CMD_NEGOTIATE_MANIFEST`| Шлюз → Вузол | Маніфест оновлення: `[Target_Ver (4B), Total_Size (4B), Chunk_Size (2B), Full_SHA256 (32B), Signature (64B)]`. |
| **`0x83`** | `RESP_MANIFEST_ACK` | Вузол → Шлюз | Статус готовності: `[Status_Code (1B), Existing_Bitmask_Offset (2B), Bitmask_Bytes (16B)]`. |
| **`0x04`** | `CMD_PUSH_CHUNK` | Шлюз → Вузол | Дані блоку: `[Chunk_Index (2B), Chunk_CRC16 (2B), Chunk_Data (N байтів)]`. |
| **`0x84`** | `RESP_CHUNK_ACK` | Вузол → Шлюз | Підтвердження блоку: `[Chunk_Index (2B), Status_Code (1B), Next_Missing_Chunk (2B)]`. |
| **`0x05`** | `CMD_COMMIT_AND_TEST`| Шлюз → Вузол | Команда фіналізації: `[Action_Flags (1B), Watchdog_Timeout_Sec (2B)]`. |
| **`0x85`** | `RESP_COMMIT_STATUS`| Вузол → Шлюз | Готовність до перезавантаження: `[Status_Code (1B), Target_Slot (1B)]`. |
| **`0x06`** | `CMD_PULL_AUDIT_LOG`| Шлюз → Вузол | Запит журналу стану: `[Log_Type (1B), Offset (4B), Max_Len (2B)]`. |
| **`0x86`** | `RESP_AUDIT_LOG_DATA`| Вузол → Шлюз | Фрагмент журналу: `[Log_Type (1B), Remaining (4B), Log_Bytes (N)]`. |

---

### 3. Автомат сесії та процедура відновлення обривів (Resumable Transfer)

Сесія між шлюзом та цільовим пристроєм проходить через чітко розмежовані стани, керовані внутрішнім автоматом:

```
[ IDLE ] ──► [ DISCOVERY ] ──► [ AUTHENTICATED ] ──► [ MANIFEST_SYNC ]
                                                              │
                                                              ▼
[ AUDIT_EXTRACT ] ◄── [ COMMIT_PENDING ] ◄── [ CHUNK_STREAMING ]
```

1. **Фаза виявлення та автентифікації:**
   Шлюз відправляє `CMD_DISCOVERY` з псевдовипадковим числом `Nonce_G`. Пристрій відповідає власним ідентифікатором `Device_UID`, апаратною версією, поточним номером прошивки та підписом відповіді. Далі шлюз надсилає сертифікат техніка у виклику `CMD_AUTH_CHALLENGE`. Пристрій звіряє відкритий ключ техніка зі списком довірених сертифікатів. Якщо валідація успішна, сторони обчислюють спільний сесійний ключ шифрування каналу (ECDH).
2. **Фаза узгодження маніфесту та отримання бітової маски:**
   Шлюз передає `CMD_NEGOTIATE_MANIFEST` із параметрами майбутнього образу. Пристрій перевіряє рівень напруги живлення батареї (якщо напруга нижче 3.6 В, сесія відхиляється з кодом `ERR_LOW_BATTERY`). Якщо перевірка успішна, пристрій перевіряє стан неактивного слота Flash B. Якщо в ньому вже збережено частину чанків від попередньої сесії з тим самим хешем образу, пристрій повертає бітову маску наявних блоків. Шлюз відправляє виключно ті чанки, які позначені нулем, що заощаджує час та заряд батареї в польових умовах.
3. **Фаза віконного передавання чанків (Windowed Chunk Transfer):**
   Щоб мінімізувати затримки напівдуплексного каналу, шлюз надсилає групу чанків (наприклад, вікно з 4 або 8 чанків) без очікування миттєвої відповіді на кожен. Пристрій буферизує байти, перевіряє `CRC16` кожного блоку, прошиває сектор Flash і повертає `RESP_CHUNK_ACK` із кумулятивною бітовою маскою або індексом першого пропущеного чанка.
4. **Фаза фіналізації та тестування (Commit & Watchdog Supervision):**
   Після передачі 100% чанків шлюз надсилає `CMD_COMMIT_AND_TEST`. Пристрій виконує підсумкову звірку SHA-256 і готує апаратний таймер Watchdog на 30–60 секунд. Якщо пристрій успішно завантажився у нову прошивку, провів внутрішнє самотестування периферії та підтвердив працездатність, таймер відкату скидається, а новий слот фіксується як постійний.

---

### 4. Профіль Bluetooth Low Energy (BLE GATT)

Якщо оновлення виконується бездротово через інтерфейс BLE, контролер піднімає GATT-сервіс із фіксованим UUID `0000FEF0-0000-1000-8000-00805F9B34FB`.

#### Специфікація характеристик:
- **`Control Point` (UUID: `0000FEF1-...`) [Write, Indicate]:** дескриптор керування. Запис запускає зміну станів автомата; відповіді пристрою приходять через механізм `Indication` з обов'язковим підтвердженням на рівні BLE-стеку.
- **`Chunk Data Stream` (UUID: `0000FEF2-...`) [Write Without Response]:** високошвидкісний потік двійкових чанків прошивки. Використання непідтверджених записів у поєднанні з MTU до 512 байтів забезпечує швидкість до 60–80 КБ/с на BLE 5.0 2M PHY.
- **`Status & Bitmask` (UUID: `0000FEF3-...`) [Read, Notify]:** моніторинг прогресу прошивки в реальному часі, індикація поточної температури кристала та напруги живлення.
- **`Telemetry & Audit Dump` (UUID: `0000FEF4-...`) [Read, Notify]:** канал зворотного вивантаження підписаних логів та діагностичних зліпків стану чорної скриньки на планшет техніка.

---

### 5. Коди помилок та статусів (`Status_Code`)

```
0x00 = STATUS_OK                     Успішне виконання команди
0x01 = ERR_UNAUTHORIZED              Автентифікація не пройдена / недійсний токен
0x02 = ERR_HARDWARE_MISMATCH         Образ призначений для іншої ревізії плати
0x03 = ERR_VERSION_ROLLBACK          Спроба пониження версії нижче порогу eFuse
0x04 = ERR_LOW_BATTERY               Напруга батареї нижче безпечного порогу (3.6 В)
0x05 = ERR_FLASH_CORRUPTED           Апаратна помилка під час запису сектору Flash
0x06 = ERR_SIGNATURE_FAILED          Криптографічний підпис маніфесту не зійшовся
0x07 = ERR_SEQUENCE_OUT_OF_ORDER     Отримано неочікуваний індекс чанка
0x08 = ERR_SLOT_B_NOT_READY          Помилка стирання неактивного слота пам'яті
```

---

### 6. Програмна реалізація обробника кадру мовами C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define GATEWAY_SOF_BYTE 0x00

typedef enum {
    OP_DISCOVERY          = 0x01,
    OP_DISCOVERY_RESP     = 0x81,
    OP_AUTH_CHALLENGE     = 0x02,
    OP_AUTH_RESP          = 0x82,
    OP_MANIFEST_NEGOTIATE = 0x03,
    OP_MANIFEST_ACK       = 0x83,
    OP_PUSH_CHUNK         = 0x04,
    OP_CHUNK_ACK          = 0x84,
    OP_COMMIT_AND_TEST    = 0x05,
    OP_COMMIT_RESP        = 0x85
} gateway_opcode_t;

typedef struct __attribute__((packed)) {
    uint8_t  seq_id;
    uint8_t  opcode;
    uint16_t payload_len;
} gateway_frame_hdr_t;

typedef struct __attribute__((packed)) {
    uint32_t target_version;
    uint32_t total_payload_size;
    uint16_t chunk_size;
    uint8_t  full_sha256[32];
    uint8_t  signature_ed25519[64];
} manifest_payload_t;

typedef struct __attribute__((packed)) {
    uint16_t chunk_index;
    uint16_t chunk_crc16;
    uint8_t  data[256];
} chunk_payload_t;

/* Обробка отриманого розпакованого кадру */
void handle_gateway_packet(const gateway_frame_hdr_t *hdr,
                           const uint8_t *payload,
                           uint32_t calculated_crc,
                           uint32_t expected_crc) {
    if (calculated_crc != expected_crc) {
        /* Кадр пошкоджено — скидаємо лічильник і не відповідаємо */
        return;
    }

    switch (hdr->opcode) {
        case OP_MANIFEST_NEGOTIATE: {
            const manifest_payload_t *manifest = (const manifest_payload_t *)payload;
            /* Перевірка апаратних обмежень та валідація версії */
            (void)manifest;
            break;
        }
        case OP_PUSH_CHUNK: {
            const chunk_payload_t *chunk = (const chunk_payload_t *)payload;
            /* Запис сектору у Flash B */
            (void)chunk;
            break;
        }
        default:
            break;
    }
}
```
```cpp
#include <span>
#include <cstdint>
#include <expected>
#include <array>

namespace gateway_protocol {

enum class Opcode : uint8_t {
    Discovery          = 0x01,
    DiscoveryResp     = 0x81,
    AuthChallenge     = 0x02,
    AuthResp          = 0x82,
    ManifestNegotiate = 0x03,
    ManifestAck       = 0x83,
    PushChunk         = 0x04,
    ChunkAck          = 0x84,
    CommitAndTest     = 0x05,
    CommitResp        = 0x85
};

struct [[gnu::packed]] FrameHeader {
    uint8_t seq_id;
    Opcode opcode;
    uint16_t payload_len;
};

struct [[gnu::packed]] ManifestPayload {
    uint32_t target_version;
    uint32_t total_payload_size;
    uint16_t chunk_size;
    std::array<uint8_t, 32> full_sha256;
    std::array<uint8_t, 64> signature_ed25519;
};

struct [[gnu::packed]] ChunkPayload {
    uint16_t chunk_index;
    uint16_t chunk_crc16;
    std::array<uint8_t, 256> data;
};

class GatewaySession {
public:
    enum class ParseError {
        CrcMismatch,
        PayloadLengthMismatch,
        UnknownOpcode
    };

    std::expected<void, ParseError>
    processFrame(const FrameHeader& hdr,
                 std::span<const uint8_t> payload,
                 uint32_t packet_crc,
                 uint32_t expected_crc) {
        if (packet_crc != expected_crc) {
            return std::unexpected(ParseError::CrcMismatch);
        }
        if (payload.size() != hdr.payload_len) {
            return std::unexpected(ParseError::PayloadLengthMismatch);
        }

        switch (hdr.opcode) {
            case Opcode::ManifestNegotiate:
                return handleManifest(payload);
            case Opcode::PushChunk:
                return handleChunk(payload);
            default:
                return std::unexpected(ParseError::UnknownOpcode);
        }
    }

private:
    std::expected<void, ParseError> handleManifest(std::span<const uint8_t> bytes) {
        if (bytes.size() < sizeof(ManifestPayload)) {
            return std::unexpected(ParseError::PayloadLengthMismatch);
        }
        const auto* manifest = reinterpret_cast<const ManifestPayload*>(bytes.data());
        (void)manifest;
        return {};
    }

    std::expected<void, ParseError> handleChunk(std::span<const uint8_t> bytes) {
        if (bytes.size() < sizeof(ChunkPayload)) {
            return std::unexpected(ParseError::PayloadLengthMismatch);
        }
        const auto* chunk = reinterpret_cast<const ChunkPayload*>(bytes.data());
        (void)chunk;
        return {};
    }
};

} // namespace gateway_protocol
```
:::

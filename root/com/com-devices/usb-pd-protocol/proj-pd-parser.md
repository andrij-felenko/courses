# ⚙️ Парсер та валідатор кадрів протоколу USB PD 3.1

Повний розбір сирого бінарного буфера повідомлення USB Power Delivery (USB PD 3.1) із контролем цілісності за допомогою контрольної суми CRC-32, декодуванням бітових полів 16-бітного заголовка, підтримкою розширених фрагментованих повідомлень та формуванням апаратного кадру відповіді GoodCRC.

---

### Завдання та інженерні обмеження

Контролер порту USB Type-C (або апаратний блок фізичного рівня мікроконтролера) прийняв із лінії конфігураційного каналу CC послідовність байтів, яка слідує безпосередньо за 4-символьним стартовим маркером пакета `SOP`. Необхідно створити детермінований модуль розбору кадру, який задовольняє такі жорсткі вимоги:

1. **Контроль цілісності за CRC-32:** Негайно перевірити цілісність отриманого бінарного блоку за стандартизованим поліномом Ethernet/IEEE 802.3 `0x04C11DB7`. Будь-який пакет зі спотвореною контрольною сумою повинен беззастережно відкидатися без подальшої обробки.
2. **Декодування 16-бітного Message Header:** Витягти всі ключові атрибути транзакції: тип повідомлення (`MessageType`), кількість 32-бітних об'єктів даних (`NumDataObjects`), поточний циклічний номер транзакції (`MessageID`), ревізію специфікації (`SpecRevision`) та ролі порту (`PortPowerRole`, `PortDataRole`).
3. **Обробка розширеного заголовка Extended Message Header:** Якщо встановлено ознаку розширеного повідомлення (`Extended = 1`), виконати розбір 16-бітного поля параметрів фрагментації: визначити режим передачі (`Chunked`), номер поточного фрагмента (`ChunkNumber`), прапор запиту наступного чанка (`RequestChunk`) та загальний розмір усього масиву даних (`DataSize` до 260 байтів).
4. **Керування лічильником MessageID та відкидання дублікатів:** Перевірити порядковий номер отриманого кадру відносно попередньої транзакції. Якщо номер збігається з щойно обробленим (свідоцтво втрати попереднього GoodCRC на лінії), модуль зобов'язаний проігнорувати повторне корисне навантаження, але повторно надіслати підтвердження.
5. **Генерація відповіді GoodCRC у жорстких часових рамках:** Сформувати 6-байтний бінарний образ кадру `GoodCRC` із коректним дзеркальним значенням `MessageID` та валідним CRC-32. Ця операція повинна виконуватися за мінімальний час, аби вкластися у норматив стандарту `tTransmitSOP` (не більше ніж **195 мкс** від моменту завершення прийому вхідного пакета).
6. **Безпека роботи з пам'яттю (Zero-Copy):** Забезпечити нульове копіювання корисного навантаження (робота через вказівники або структури `std::span`), що усуває зайві затримки й виключає ризик переповнення буфера на вбудованих платформах.

---

### Архітектура та математичний механізм розв'язку

Кадр протоколу USB PD передається у фізичний канал молодшим байтом уперед (little-endian). Структура вхідного буфера складається з трьох обов'язкових зон: перші два байти займає базовий заголовок `Message Header`, далі розміщується корисне навантаження (довжина якого залежить від типу кадру), а замикають пакет 4 байти контрольної суми CRC-32.

```
+-------------------+--------------------------+-----------------------+------------------+
|  Message Header   |  [Extended Header (2Б)]  |  Payload (0..260 Б)   |  CRC-32 (4 Байти)|
|     (2 Байти)     |     (якщо Ext = 1)       |  (0..7 об'єктів DO)   |  (IEEE 802.3)    |
+-------------------+--------------------------+-----------------------+------------------+
```

#### Фізичний рівень та інтерфейс із контролером порту (TCPC)

У реальних вбудованих системах мікроконтролер взаємодіє з фізичною лінією CC через спеціалізовану мікросхему TCPC (наприклад, ON Semiconductor FUSB302, Texas Instruments TPS65987D або вбудований апаратний периферійний блок STM32 UCPD). Фізичний контролер виконує аналогове детектування рівнів BMC, виділяє стартовий маркер SOP та заповнює апаратний буфер FIFO прийому.

Щойно приймач фіксує маркер кінця пакета EOP, він генерує переривання для головного процесора. Драйвер вичитує сирі байти з регістра FIFO через інтерфейс I²C або SPI зі швидкістю 400 кГц–1 МГц. Оскільки час передачі 30 байтів по шині I²C на частоті 400 кГц займає близько 60–75 мкс, програмний стек має в запасі не більше ніж 100 мкс для повної перевірки цілісності та підготовки відповіді GoodCRC. Будь-яке нераціональне копіювання пам'яті або неефективні математичні цикли ставлять під загрозу виконання стандарту `tTransmitSOP`.

Розглянемо типову послідовність викликів під час взаємодії драйвера з апаратним чипом TCPC:

1. **Регістр переривань `INTERRUPT`:** Чип встановлює біт `I_RX_FULL` або `I_RX_EOP`. Обробник переривання мікроконтролера негайно скидає прапор у регістрі статусу, щоб дозволити прийом наступного кадру.
2. **Зчитування токена `RX_TOKEN`:** Перший байт у буфері FIFO містить числовий код розпізнаного маркера (`0x00` для SOP, `0x01` для SOP', `0x02` для SOP''). Якщо токен відповідає адресації даного порту, драйвер копіює масив байтів кадру в лінійний робочий буфер процесора.
3. **Виклик модуля розбору `pd_parse_packet`:** Модуль виконує верифікацію CRC-32 та розкладає заголовок на складові структури.

#### Математика та оптимізація розрахунку CRC-32

Специфікація USB PD 3.1 використовує 32-бітний циклічний надлишковий код із твірним поліномом `0x04C11DB7` (стандарт IEEE 802.3). Розрахунок виконується над дзеркально перевернутим представленням бітів у кожному байті (reflected CRC) з початковим значенням регістру `0xFFFFFFFF` та фінальною інверсією результату (операція XOR з `0xFFFFFFFF`).

Класичний побітовий розрахунок CRC-32 вимагає 8 ітерацій зсуву на кожен байт. На типовому мікроконтролері з тактовою частотою 16–48 МГц побітова обробка пакета з 28 байтів корисного навантаження забирає до 80–120 мкс, що залишає замало часу на формування відповіді до вичерпання ліміту `tTransmitSOP` (195 мкс). З іншого боку, повна 256-елементна таблиця CRC-32 займає 1024 байти Flash/SRAM, що занадто дорого для компактних мікроконтролерів керування живленням (наприклад, Cortex-M0+ із 8 КБ пам'яті).

Оптимальним компромісом є **нібловий (4-бітний) табличний розрахунок**. Таблиця містить лише 16 32-бітних констант (загалом 64 байти пам'яті) і обробляє кожен байт за два кроки (по 4 біти):

```
Крок 1:  CRC := (CRC >> 4) ^ Table[(CRC ^ (Byte & 0x0F)) & 0x0F]
Крок 2:  CRC := (CRC >> 4) ^ Table[(CRC ^ (Byte >> 4)) & 0x0F]
```

Такий підхід прискорює обчислення в 3.5 раза порівняно з побітовим алгоритмом, гарантуючи завершення перевірки CRC-32 за 8–15 мкс на будь-якому вбудованому ядрі.

#### Правила перевірки цілісності та розподіл за типами

Парсер спочатку розраховує еталонний CRC-32 над заголовком і корисним навантаженням. Обчислений результат порівнюється з 4-байтним числом, розміщеним наприкінці вхідного буфера. Якщо суми не зійшлися, пакет вважається пошкодженим імпульсною завадою і знищується.

Якщо контрольна сума зійшлася, модуль декодує бітові поля:
1. Якщо `Extended == 0` і `NumDataObjects == 0` — це **керівне повідомлення** (Control Message). Довжина тіла має строго дорівнювати 0 байтів.
2. Якщо `Extended == 0` і `NumDataObjects > 0` — це **стандартне повідомлення даних** (Data Message). Довжина корисного навантаження повинна строго дорівнювати `4 × NumDataObjects` байтів.
3. Якщо `Extended == 1` — це **розширене повідомлення** (Extended Message). Парсер витягує розширений заголовок із байтів 2 та 3, перевіряє відповідність поля `DataSize` та розміщує вказівник на початок корисних даних.

#### Логіка автомата Stop-and-Wait ARQ та обробка дублікатів

Протокол надійної доставки базується на суворому контролі лічильника `MessageID`:

* **TX State Machine (Передавач):** При відправці нового пакета передавач зберігає його копію в буфері повтору, запускає апаратний таймер `CRCReceiveTimer` (0.9–1.1 мс) і блокує передачу наступних повідомлень. Якщо GoodCRC надходить вчасно, передавач звільняє буфер, збільшує лічильник TX MessageID на одиницю (по модулю 8) і розблоковує чергу. Якщо таймер спливає, передавач інкрементує лічильник `nRetryCount` і повторює відправку того самого кадру з незмінним `MessageID`. Після трьох невдалих спроб ініціюється аварійне скидання Soft_Reset.
* **RX State Machine (Приймач):** Приймач зберігає номер останньої успішно обробленої транзакції (RX MessageID). Якщо вхідний пакет має номер, що дорівнює `(RX MessageID + 1) mod 8`, він визнається новим, передається рушію політики, а RX MessageID оновлюється. Якщо ж номер точно збігається з поточним `RX MessageID`, це свідчить про те, що відправник не отримав попередній GoodCRC через заваду на лінії. Приймач негайно формує повторний GoodCRC, але відкидає тіло пакета, захищаючи систему від подвійного виконання команд.

---

### Реалізація: перевірка CRC-32, парсер заголовків та генератор GoodCRC

Нижче наведено повну реалізацію парсера двома мовами: на мові C (для прямої інтеграції в драйвери низькорівневих RTOS та контролерів TCPC) та на сучасній мові C++23 (з використанням `std::span`, `std::expected`, типізованих переліків `enum class` та механізмів `constexpr`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define PD_MAX_PAYLOAD_BYTES  260
#define PD_CRC_RESIDUE        0xC704DD7Bu

// Типи повідомлень USB PD (Control та Data)
typedef enum {
    PD_CTRL_GOOD_CRC       = 0x01,
    PD_CTRL_GOTO_MIN       = 0x02,
    PD_CTRL_ACCEPT         = 0x03,
    PD_CTRL_REJECT         = 0x04,
    PD_CTRL_PING           = 0x05,
    PD_CTRL_PS_RDY         = 0x06,
    PD_CTRL_GET_SRC_CAP    = 0x07,
    PD_CTRL_GET_SNK_CAP    = 0x08,
    PD_CTRL_DR_SWAP        = 0x09,
    PD_CTRL_PR_SWAP        = 0x0A,
    PD_CTRL_VCONN_SWAP     = 0x0B,
    PD_CTRL_WAIT           = 0x0C,
    PD_CTRL_SOFT_RESET     = 0x0D,
    PD_CTRL_NOT_SUPPORTED  = 0x10,

    PD_DATA_SRC_CAP        = 0x01,
    PD_DATA_REQUEST        = 0x02,
    PD_DATA_BIST           = 0x03,
    PD_DATA_SNK_CAP        = 0x04,
    PD_DATA_VDM            = 0x0F
} pd_msg_type_t;

// Структура розпарсеного основного заголовка
typedef struct {
    bool is_extended;
    uint8_t num_data_objects;
    uint8_t message_id;
    uint8_t power_role;       // 0 = Sink, 1 = Source
    uint8_t spec_rev;         // 2 = PD 3.0
    uint8_t data_role;        // 0 = UFP, 1 = DFP
    uint8_t msg_type;
} pd_header_t;

// Структура розширеного заголовка
typedef struct {
    bool chunked;
    uint8_t chunk_number;
    bool request_chunk;
    uint16_t data_size;
} pd_ext_header_t;

// Повний розпарсений пакет
typedef struct {
    pd_header_t header;
    pd_ext_header_t ext_header;
    const uint8_t *payload;
    uint16_t payload_len;
} pd_packet_t;

// Нібловий табличний розрахунок CRC-32 (IEEE 802.3 / USB PD)
static uint32_t pd_crc32_update(uint32_t crc, uint8_t byte) {
    static const uint32_t table[16] = {
        0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
        0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
        0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
        0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
    };
    uint8_t nibble;
    crc ^= byte;
    nibble = crc & 0x0F;
    crc = (crc >> 4) ^ table[nibble];
    nibble = (crc ^ (byte >> 4)) & 0x0F;
    crc = (crc >> 4) ^ table[nibble];
    return crc;
}

uint32_t pd_calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < len; ++i) {
        crc = pd_crc32_update(crc, data[i]);
    }
    return ~crc;
}

// Парсер 16-бітного Message Header
static pd_header_t pd_parse_header(uint16_t raw_hdr) {
    pd_header_t h;
    h.msg_type         = (uint8_t)(raw_hdr & 0x1F);
    h.data_role        = (uint8_t)((raw_hdr >> 5) & 0x01);
    h.spec_rev         = (uint8_t)((raw_hdr >> 6) & 0x03);
    h.power_role       = (uint8_t)((raw_hdr >> 8) & 0x01);
    h.message_id       = (uint8_t)((raw_hdr >> 9) & 0x07);
    h.num_data_objects = (uint8_t)((raw_hdr >> 12) & 0x07);
    h.is_extended      = (bool)((raw_hdr >> 15) & 0x01);
    return h;
}

// Парсер 16-бітного Extended Message Header
static pd_ext_header_t pd_parse_ext_header(uint16_t raw_ext) {
    pd_ext_header_t eh;
    eh.data_size      = raw_ext & 0x01FF;
    eh.request_chunk  = (bool)((raw_ext >> 10) & 0x01);
    eh.chunk_number   = (uint8_t)((raw_ext >> 11) & 0x0F);
    eh.chunked        = (bool)((raw_ext >> 15) & 0x01);
    return eh;
}

// Головна функція валідації та парсингу
bool pd_parse_packet(const uint8_t *raw_buf, size_t total_len, pd_packet_t *out_pkt) {
    if (!raw_buf || total_len < 6 || !out_pkt) return false;

    // 1. Перевірка цілісності CRC-32
    size_t payload_and_hdr_len = total_len - 4;
    uint32_t calc_crc = pd_calculate_crc32(raw_buf, payload_and_hdr_len);
    uint32_t pkt_crc = (uint32_t)raw_buf[total_len - 4] |
                       ((uint32_t)raw_buf[total_len - 3] << 8) |
                       ((uint32_t)raw_buf[total_len - 2] << 16) |
                       ((uint32_t)raw_buf[total_len - 1] << 24);

    if (calc_crc != pkt_crc) {
        return false; // Збій контрольної суми
    }

    // 2. Декодування Message Header
    uint16_t raw_hdr = (uint16_t)raw_buf[0] | ((uint16_t)raw_buf[1] << 8);
    out_pkt->header = pd_parse_header(raw_hdr);

    // 3. Перевірка довжини корисного навантаження
    if (!out_pkt->header.is_extended) {
        size_t expected_len = (size_t)out_pkt->header.num_data_objects * 4;
        if (payload_and_hdr_len != 2 + expected_len) {
            return false; // Довжина не відповідає кількості об'єктів
        }
        out_pkt->payload = (expected_len > 0) ? &raw_buf[2] : NULL;
        out_pkt->payload_len = (uint16_t)expected_len;
        memset(&out_pkt->ext_header, 0, sizeof(out_pkt->ext_header));
    } else {
        if (payload_and_hdr_len < 4) return false;
        uint16_t raw_ext = (uint16_t)raw_buf[2] | ((uint16_t)raw_buf[3] << 8);
        out_pkt->ext_header = pd_parse_ext_header(raw_ext);
        out_pkt->payload = &raw_buf[4];
        out_pkt->payload_len = (uint16_t)(payload_and_hdr_len - 4);
    }

    return true;
}

// Генерація кадру GoodCRC у відповідь
size_t pd_build_goodcrc(uint8_t msg_id, uint8_t power_role, uint8_t data_role,
                        uint8_t spec_rev, uint8_t *out_buf, size_t max_buf_len) {
    if (!out_buf || max_buf_len < 6) return 0;

    // Керівне повідомлення GoodCRC: NumDataObjects = 0, MsgType = 0x01
    uint16_t hdr = (uint16_t)PD_CTRL_GOOD_CRC;
    hdr |= (uint16_t)(data_role & 0x01) << 5;
    hdr |= (uint16_t)(spec_rev & 0x03) << 6;
    hdr |= (uint16_t)(power_role & 0x01) << 8;
    hdr |= (uint16_t)(msg_id & 0x07) << 9;

    out_buf[0] = (uint8_t)(hdr & 0xFF);
    out_buf[1] = (uint8_t)((hdr >> 8) & 0xFF);

    uint32_t crc = pd_calculate_crc32(out_buf, 2);
    out_buf[2] = (uint8_t)(crc & 0xFF);
    out_buf[3] = (uint8_t)((crc >> 8) & 0xFF);
    out_buf[4] = (uint8_t)((crc >> 16) & 0xFF);
    out_buf[5] = (uint8_t)((crc >> 24) & 0xFF);

    return 6; // Фіксований розмір: 2 байти заголовка + 4 байти CRC
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>

namespace usb_pd {

enum class MessageType : uint8_t {
    GoodCRC       = 0x01,
    GotoMin       = 0x02,
    Accept        = 0x03,
    Reject        = 0x04,
    Ping          = 0x05,
    PsRdy         = 0x06,
    GetSourceCap  = 0x07,
    GetSinkCap    = 0x08,
    DrSwap        = 0x09,
    PrSwap        = 0x0A,
    VconnSwap     = 0x0B,
    Wait          = 0x0C,
    SoftReset     = 0x0D,
    NotSupported  = 0x10,

    SourceCap     = 0x01,
    Request       = 0x02,
    Bist          = 0x03,
    SinkCap       = 0x04,
    Vdm           = 0x0F
};

enum class PowerRole : uint8_t { Sink = 0, Source = 1 };
enum class DataRole  : uint8_t { Ufp = 0, Dfp = 1 };
enum class SpecRev   : uint8_t { Rev1_0 = 0, Rev2_0 = 1, Rev3_0 = 2 };

enum class ParseError {
    BufferTooShort,
    CrcMismatch,
    InvalidPayloadLength,
    InvalidExtendedHeader
};

struct Header {
    bool is_extended;
    uint8_t num_data_objects;
    uint8_t message_id;
    PowerRole power_role;
    SpecRev spec_rev;
    DataRole data_role;
    MessageType msg_type;

    static constexpr Header from_raw(uint16_t raw) noexcept {
        return Header{
            .is_extended = static_cast<bool>((raw >> 15) & 0x01),
            .num_data_objects = static_cast<uint8_t>((raw >> 12) & 0x07),
            .message_id = static_cast<uint8_t>((raw >> 9) & 0x07),
            .power_role = static_cast<PowerRole>((raw >> 8) & 0x01),
            .spec_rev = static_cast<SpecRev>((raw >> 6) & 0x03),
            .data_role = static_cast<DataRole>((raw >> 5) & 0x01),
            .msg_type = static_cast<MessageType>(raw & 0x1F)
        };
    }

    constexpr uint16_t to_raw() const noexcept {
        uint16_t raw = static_cast<uint8_t>(msg_type) & 0x1F;
        raw |= (static_cast<uint16_t>(data_role) & 0x01) << 5;
        raw |= (static_cast<uint16_t>(spec_rev) & 0x03) << 6;
        raw |= (static_cast<uint16_t>(power_role) & 0x01) << 8;
        raw |= (static_cast<uint16_t>(message_id) & 0x07) << 9;
        raw |= (static_cast<uint16_t>(num_data_objects) & 0x07) << 12;
        raw |= (static_cast<uint16_t>(is_extended) & 0x01) << 15;
        return raw;
    }
};

struct ExtendedHeader {
    bool chunked;
    uint8_t chunk_number;
    bool request_chunk;
    uint16_t data_size;

    static constexpr ExtendedHeader from_raw(uint16_t raw) noexcept {
        return ExtendedHeader{
            .chunked = static_cast<bool>((raw >> 15) & 0x01),
            .chunk_number = static_cast<uint8_t>((raw >> 11) & 0x0F),
            .request_chunk = static_cast<bool>((raw >> 10) & 0x01),
            .data_size = static_cast<uint16_t>(raw & 0x01FF)
        };
    }
};

struct Packet {
    Header header;
    std::optional<ExtendedHeader> ext_header;
    std::span<const uint8_t> payload;
};

// Розрахунок CRC-32 (нібловий метод)
constexpr uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
    constexpr std::array<uint32_t, 16> table = {
        0x00000000, 0x1DB71064, 0x3B6E20C8, 0x26D930AC,
        0x76DC4190, 0x6B6B51F4, 0x4DB26158, 0x5005713C,
        0xEDB88320, 0xF00F9344, 0xD6D6A3E8, 0xCB61B38C,
        0x9B64C2B0, 0x86D3D2D4, 0xA00AE278, 0xBDBDF21C
    };
    uint32_t crc = 0xFFFFFFFFu;
    for (uint8_t b : data) {
        crc ^= b;
        crc = (crc >> 4) ^ table[crc & 0x0F];
        crc = (crc >> 4) ^ table[(crc ^ (b >> 4)) & 0x0F];
    }
    return ~crc;
}

// Парсер кадру пакета
std::expected<Packet, ParseError> parse_packet(std::span<const uint8_t> raw_frame) noexcept {
    if (raw_frame.size() < 6) {
        return std::unexpected(ParseError::BufferTooShort);
    }

    const size_t content_len = raw_frame.size() - 4;
    const uint32_t expected_crc = calculate_crc32(raw_frame.subspan(0, content_len));

    const uint32_t packet_crc = static_cast<uint32_t>(raw_frame[content_len]) |
                                (static_cast<uint32_t>(raw_frame[content_len + 1]) << 8) |
                                (static_cast<uint32_t>(raw_frame[content_len + 2]) << 16) |
                                (static_cast<uint32_t>(raw_frame[content_len + 3]) << 24);

    if (expected_crc != packet_crc) {
        return std::unexpected(ParseError::CrcMismatch);
    }

    const uint16_t raw_hdr = static_cast<uint16_t>(raw_frame[0]) |
                             (static_cast<uint16_t>(raw_frame[1]) << 8);
    const Header hdr = Header::from_raw(raw_hdr);

    if (!hdr.is_extended) {
        const size_t expected_payload_bytes = static_cast<size_t>(hdr.num_data_objects) * 4;
        if (content_len != 2 + expected_payload_bytes) {
            return std::unexpected(ParseError::InvalidPayloadLength);
        }
        return Packet{
            .header = hdr,
            .ext_header = std::nullopt,
            .payload = raw_frame.subspan(2, expected_payload_bytes)
        };
    } else {
        if (content_len < 4) {
            return std::unexpected(ParseError::InvalidExtendedHeader);
        }
        const uint16_t raw_ext = static_cast<uint16_t>(raw_frame[2]) |
                                 (static_cast<uint16_t>(raw_frame[3]) << 8);
        return Packet{
            .header = hdr,
            .ext_header = ExtendedHeader::from_raw(raw_ext),
            .payload = raw_frame.subspan(4, content_len - 4)
        };
    }
}

// Генерація кадру GoodCRC (повертає фіксований масив із 6 байтів)
constexpr std::array<uint8_t, 6> make_goodcrc(uint8_t msg_id, PowerRole role,
                                              DataRole data_role, SpecRev rev) noexcept {
    const Header hdr{
        .is_extended = false,
        .num_data_objects = 0,
        .message_id = msg_id,
        .power_role = role,
        .spec_rev = rev,
        .data_role = data_role,
        .msg_type = MessageType::GoodCRC
    };
    const uint16_t raw_hdr = hdr.to_raw();
    std::array<uint8_t, 6> buf = {
        static_cast<uint8_t>(raw_hdr & 0xFF),
        static_cast<uint8_t>((raw_hdr >> 8) & 0xFF),
        0, 0, 0, 0
    };
    const uint32_t crc = calculate_crc32(std::span<const uint8_t>(buf.data(), 2));
    buf[2] = static_cast<uint8_t>(crc & 0xFF);
    buf[3] = static_cast<uint8_t>((crc >> 8) & 0xFF);
    buf[4] = static_cast<uint8_t>((crc >> 16) & 0xFF);
    buf[5] = static_cast<uint8_t>((crc >> 24) & 0xFF);
    return buf;
}

} // namespace usb_pd
```
:::

---

### Покроковий розбір алгоритму обробки транзакції

Простежимо життєвий цикл вхідного кадру крізь реалізований модуль у типовому сценарії прийому меню профілів живлення `Source_Capabilities`:

1. **Прийом сирого буфера від контролера PHY:** Контролер порту (наприклад, FUSB302 або вбудований UCPD периферійний блок STM32G4) приймає пакети з лінії CC, відкидає преамбулу та маркер SOP і переносить байти кадру в системну пам'ять через прямий доступ DMA. Функція `pd_parse_packet` отримує вказівник на початок буфера та загальну довжину `total_len`.
2. **Перевірка мінімального розміру кадру:** Якщо довжина менша за 6 байтів (2 байти заголовка + 4 байти CRC), функція негайно повертає помилку `BufferTooShort`. Це захищає стек від звернення за межі пам'яті.
3. **Верифікація контрольної суми:** Функція `pd_calculate_crc32` обчислює суму над першими `total_len - 4` байтами. Отриманий результат звіряється з 4 байтами, збереженими у кінці кадру. У разі неспівпадіння повертається `CrcMismatch`, що свідчить про наявність шуму на лінії.
4. **Розбір бітових полів `Message Header`:** Заголовок збирається з нульового та першого байтів за схемою `byte0 | (byte1 << 8)`. Бітові маски розкладають 16-бітне число на структуру `pd_header_t`.
5. **Валідація розміру тіла даних:** Для стандартних повідомлень розмір тіла повинен точно відповідати добутку `4 × NumDataObjects`. Якщо розмір буфера відрізняється, функція фіксує порушення форматування кадру (`InvalidPayloadLength`).
6. **Генерація відповіді `GoodCRC`:** Якщо пакет пройшов перевірку, модуль викликає `pd_build_goodcrc`. Він формує 16-бітний заголовок із кодом `0x01` (`GoodCRC`), дублює отриманий `MessageID`, вказує власні ролі порту та розраховує CRC-32 від 2 байтів заголовка. Отриманий 6-байтний масив негайно передається в апаратний буфер TX контролера порту для відправки в лінію CC.

У C++ версії модуля парсер повертає типізований об'єкт `std::expected<Packet, ParseError>`. Це унеможливлює випадкове використання розпарсених даних при виникненні помилок контрольної суми чи некоректної довжини. Використання `std::span` замість сирих масивів забезпечує безпечний доступ до пам'яті без динамічного виділення пам'яті на купі (`heap allocation`), що є абсолютно неприпустимим у високошвидкісних драйверах реального часу.

#### Приклад практичного розбору байтів живого логу

Розглянемо числовий приклад розбору реального пакета `Request` на 20 вольтів / 3 ампери, отриманого снифером лінії CC:

```
Байтовий потік: [0x82, 0x12, 0x2C, 0xB1, 0x04, 0x20, 0x7B, 0xDD, 0x04, 0xC7]
```

* **Байти 0..1 (`0x82, 0x12`):** Заголовок `Message Header` = `0x1282`. Розкладаємо за бітами:
  * Біти 4:0 = `00010b` (`0x02` — тип `Request`).
  * Біт 5 = `0` (UFP).
  * Біти 7:6 = `10b` (PD 3.0).
  * Біт 8 = `0` (Sink).
  * Біти 11:9 = `001b` (`MessageID = 1`).
  * Біти 14:12 = `001b` (`NumDataObjects = 1`, тобто рівно 4 байти тіла даних).
  * Біт 15 = `0` (Standard Message).
* **Байти 2..5 (`0x2C, 0xB1, 0x04, 0x20`):** 32-бітний об'єкт `RDO` = `0x2004B12C`:
  * Біти 30:28 = `010b` (обрано профіль PDO #2 — 20 В).
  * Біти 19:10 = `0x12C` = 300 (робочий струм 3.00 А).
  * Біти 9:0 = `0x12C` = 300 (максимальний струм 3.00 А).
* **Байти 6..9 (`0x7B, 0xDD, 0x04, 0xC7`):** Контрольна сума CRC-32. Обчислення за першими 6 байтами дає значення `0xC704DD7B`, що збігається з вмістом буфера. Пакет валідний.

#### Методика модульного тестування парсера

Для верифікації надійності парсера в процесі розробки створюють набір тестових векторів (Unit Tests), які симулюють різні аварійні ситуації на фізичному каналі:
* **Тест штучного пошкодження біта:** Інвертується один довільний біт у полі заголовка або тіла даних. Парсер зобов'язаний повернути помилку `CrcMismatch` та заблокувати генерацію `GoodCRC`.
* **Тест спотвореної довжини:** Полю `NumDataObjects` присвоюється значення 3 (очікується 12 байтів тіла), а фізичний буфер подає лише 8 байтів. Парсер зобов'язаний повернути `InvalidPayloadLength`.
* **Тест перевірки нульової довжини:** Подається 5-байтний буфер. Парсер зобов'язаний повернути `BufferTooShort` без спроби читання відсутнього байта CRC.
* **Тест повторення транзакції:** Подається валідний кадр із тим самим `MessageID`, що й у попередній ітерації. Парсер розпізнає дублікат, сигналізує рушію політики про пропуск виконання, але успішно генерує повторний кадр `GoodCRC`.

---

### Пастки реалізації, крайові випадки та апаратна інтеграція

1. **Критичність часового бюджету обчислень (`tTransmitSOP`):** Стандарт USB PD 3.1 вимагає, щоб передача першого біта преамбули GoodCRC почалася не пізніше ніж через **195 мкс** після завершення прийому вхідного повідомлення. Якщо мікроконтролер виконує розбір у низькопріоритетному потоці RTOS або заблокований тривалим обробником переривань, GoodCRC запізниться. Передавач вважатиме пакет втраченим і здійснить повторну передачу (Retry).
2. **Заборона рекурсивного квитування GoodCRC:** Якщо модуль прийняв пакет `GoodCRC` від партнера, він зобов'язаний зупинити власний таймер `CRCReceiveTimer` та оновити внутрішній лічильник `MessageID`. **Категорично заборонено генерувати GoodCRC у відповідь на отриманий GoodCRC!** Порушення цього правила спричиняє нескінченний шторм повідомлень у лінії CC.
3. **Обробка розбіжності лічильників під час `Soft_Reset`:** При отриманні керівного повідомлення `Soft_Reset` внутрішні лічильники `MessageID` на приймачі та передавачі примусово скидаються в `0`. Наступне повідомлення-підтвердження `Accept` повинно обов'язково надсилатися зі значенням `MessageID = 0`.
4. **Вирівнювання пам'яті (Memory Alignment Faults):** На 32-бітних процесорах ARM Cortex-M0/M0+ пряме приведення вказівника на непарну адресу `(uint32_t*)&raw_buf[2]` до 32-бітного типу викликає апаратне виключення `HardFault` (Unaligned Access). Функція розбору обов'язково повинна збирати 32-бітні слова через побайтові зсуви або копіювання за допомогою `memcpy`.
5. **Колізії при одночасній передачі на лінії CC:** Якщо обидва пристрої починають передачу одночасно, пакети накладаються і контрольна сума спотворюється на обох кінцях. Стандарт вимагає, щоб у разі колізії споживач (Sink) поступався лінії й витримував захисну паузу перед повторною спробою, дозволяючи джерелу (Source) завершити свою транзакцію.
6. **Обрізані пакети під час висмикування штекера:** Гаряче відключення кабелю під час передачі кадру призводить до раптового обриву сигналу на середині байта. Парсер повинен коректно обробляти ситуацію, коли довжина вхідного буфера виявляється меншою за декларовану в заголовку `NumDataObjects`, не допускаючи читання за межами виділеного буфера.
7. **Координація черг при швидкій зміні ролей (FRS):** Під час виконання процедури Fast Role Swap контролер порту може отримати апаратний сигнал перемикання VBUS саме в момент, коли в буфері передачі очікує звичайний пакет. Драйвер зобов'язаний негайно очистити чергу передачі TX FIFO, скинути стан таймерів повторів та перевести протокольний автомат у режим нового джерела, усуваючи конфлікт пріоритетів.

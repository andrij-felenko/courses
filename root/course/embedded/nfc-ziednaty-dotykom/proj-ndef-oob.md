# ⚙️ Програмний драйвер генерації NDEF-повідомлень та спаровування BLE OOB

Завдання автономного вбудованого вузла — за лічені мілісекунди після фізичного піднесення смартфона сформувати валідне повідомлення NDEF (NFC Data Exchange Format), запакувати в нього актуальні параметри бездротового зв'язку (MAC-адресу, криптографічний секрет спаровування, локальне ім'я вузла) та записати сформований двійковий образ через шину I2C у двопортову пам'ять динамічного чипа NFC (наприклад, NXP NTAG I2C Plus або STMicroelectronics ST25DV).

Нижче наведено модульну архітектуру генератора NDEF-записів та драйвера мітки з повним контролем меж пам'яті (bounds checking), захистом від зависання шини I2C при тактовому розтягуванні (clock stretching), підтримкою алгоритму спаровування Bluetooth Low Energy Out-of-Band (BLE OOB) та обробкою переривання виявлення поля (Field Detect).

## Архітектура драйвера та структури даних

Серіалізатор будує NDEF-повідомлення послідовно у виділеному статичному буфері оперативної пам'яті мікроконтролера. Кожен запис починається із заголовка, що містить біти конфігурації `MB` (Message Begin), `ME` (Message End), `SR` (Short Record) та код `TNF` (Type Name Format).

Для підтримки спаровування BLE створюється MIME-запис типу `application/vnd.bluetooth.ep.oob`, корисне навантаження якого складається зі стандартизованих структур Advertising Data (AD Data): прапорців, типу та значення MAC-адреси, ролі вузла та 128-бітного тимчасового ключа автентифікації (Temporary Key, TK) або хешу підтвердження LE Secure Connections.

### Покроковий механізм формування пакетів

Побудова двійкового образу складається з чотирьох послідовних кроків:
1. **Ініціалізація структури повідомлення:** Виділяється масив фіксованого розміру (зазвичай 128–256 байтів у статичній RAM), обнуляється зміщення запису та лічильник доданих елементів;
2. **Формування заголовка запису:** Для першого запису виставляється прапорець початку повідомлення `MB = 1`, для коротких пакетів довжиною до 255 байтів активується прапорець `SR = 1`, а поле `TNF` заповнюється відповідним значенням (`0x01` для стандартизованих URI/Text або `0x02` для MIME);
3. **Пакування корисного навантаження (Payload):**
   - Для записів URI додається байт протокольного префікса (наприклад, `0x04` для `https://`), після якого копіюється ASCII-рядок адреси;
   - Для дескрипторів BLE OOB послідовно пакуються структури AD Data: обов'язкові прапорці доступності (Flags, 3 байти), 6-байтна MAC-адреса у форматі Little-Endian разом із байтом типу адреси (LE Bluetooth Device Address, 9 байтів), роль пристрою (LE Role, 3 байти), 16-байтний криптографічний ключ (Security Manager TK, 18 байтів) та опціональний рядок локального імені пристрою;
4. **Огортання в TLV-структуру мітки:** Перед відправкою по шині I2C повідомлення доповнюється маркером `0x03` (NDEF TLV), байтом розрахованої повної довжини та замикаючим термінатором `0xFE` (Terminator TLV).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define NDEF_TNF_WELL_KNOWN   0x01
#define NDEF_TNF_MIME_MEDIA   0x02

#define NDEF_FLAG_MB          0x80
#define NDEF_FLAG_ME          0x40
#define NDEF_FLAG_CF          0x20
#define NDEF_FLAG_SR          0x10
#define NDEF_FLAG_IL          0x08

#define BLE_AD_TYPE_FLAGS     0x01
#define BLE_AD_TYPE_NAME      0x09
#define BLE_AD_TYPE_TK        0x10
#define BLE_AD_TYPE_LE_ADDR   0x1B
#define BLE_AD_TYPE_LE_ROLE   0x1C

typedef enum {
    NDEF_OK = 0,
    NDEF_ERR_BUFFER_OVERFLOW,
    NDEF_ERR_INVALID_PARAM,
    NDEF_ERR_I2C_FAULT
} ndef_status_t;

typedef struct {
    uint8_t *buffer;
    size_t   capacity;
    size_t   length;
    size_t   record_count;
} ndef_msg_t;

void ndef_msg_init(ndef_msg_t *msg, uint8_t *storage, size_t capacity) {
    msg->buffer = storage;
    msg->capacity = capacity;
    msg->length = 0;
    msg->record_count = 0;
}

ndef_status_t ndef_add_uri(ndef_msg_t *msg, uint8_t prefix_code, const char *uri_str, bool is_last) {
    if (!msg || !uri_str) return NDEF_ERR_INVALID_PARAM;
    
    size_t uri_len = strlen(uri_str);
    size_t payload_len = 1 + uri_len; // 1 байт префіксу + рядок URI
    size_t record_overhead = 4;        // Header (1B) + TypeLen (1B) + PayloadLen (1B) + Type (1B: 'U')
    
    if (msg->length + record_overhead + payload_len > msg->capacity) {
        return NDEF_ERR_BUFFER_OVERFLOW;
    }
    
    uint8_t header = NDEF_FLAG_SR | NDEF_TNF_WELL_KNOWN;
    if (msg->record_count == 0) header |= NDEF_FLAG_MB;
    if (is_last) header |= NDEF_FLAG_ME;
    
    uint8_t *ptr = msg->buffer + msg->length;
    *ptr++ = header;
    *ptr++ = 0x01; // Type Length = 1
    *ptr++ = (uint8_t)payload_len;
    *ptr++ = 'U';  // Type = 'U' (URI)
    *ptr++ = prefix_code;
    memcpy(ptr, uri_str, uri_len);
    
    msg->length += (record_overhead + payload_len);
    msg->record_count++;
    return NDEF_OK;
}

ndef_status_t ndef_add_ble_oob(ndef_msg_t *msg, 
                              const uint8_t mac_le[6], 
                              uint8_t addr_type, 
                              const uint8_t tk[16], 
                              const char *device_name, 
                              bool is_last) {
    if (!msg || !mac_le || !tk) return NDEF_ERR_INVALID_PARAM;
    
    const char mime_type[] = "application/vnd.bluetooth.ep.oob";
    size_t mime_len = strlen(mime_type);
    size_t name_len = device_name ? strlen(device_name) : 0;
    
    // Розрахунок довжини корисного навантаження (AD Data)
    // 1. Flags: Len(1) + Type(1) + Val(1) = 3B
    // 2. LE Addr: Len(1) + Type(1) + MAC(6) + Type(1) = 9B
    // 3. LE Role: Len(1) + Type(1) + Val(1) = 3B
    // 4. TK: Len(1) + Type(1) + Key(16) = 18B
    // 5. Name (якщо є): Len(1) + Type(1) + Str(name_len) = 2 + name_len
    size_t payload_len = 3 + 9 + 3 + 18 + (name_len > 0 ? (2 + name_len) : 0);
    size_t record_overhead = 3 + mime_len; // Header (1B) + TypeLen (1B) + PayloadLen (1B) + Type(mime_len)
    
    if (msg->length + record_overhead + payload_len > msg->capacity) {
        return NDEF_ERR_BUFFER_OVERFLOW;
    }
    
    uint8_t header = NDEF_FLAG_SR | NDEF_TNF_MIME_MEDIA;
    if (msg->record_count == 0) header |= NDEF_FLAG_MB;
    if (is_last) header |= NDEF_FLAG_ME;
    
    uint8_t *ptr = msg->buffer + msg->length;
    *ptr++ = header;
    *ptr++ = (uint8_t)mime_len;
    *ptr++ = (uint8_t)payload_len;
    memcpy(ptr, mime_type, mime_len);
    ptr += mime_len;
    
    // AD Structure 1: Flags (LE General Discoverable + BR/EDR Not Supported)
    *ptr++ = 0x02; // Довжина поля (Type + Data)
    *ptr++ = BLE_AD_TYPE_FLAGS;
    *ptr++ = 0x06; // 0x02 (LE General Disc) | 0x04 (No BR/EDR)
    
    // AD Structure 2: LE Bluetooth Device Address (6 байтів MAC + 1 байт тип адреси)
    *ptr++ = 0x08;
    *ptr++ = BLE_AD_TYPE_LE_ADDR;
    memcpy(ptr, mac_le, 6);
    ptr += 6;
    *ptr++ = addr_type; // 0x00 = Public, 0x01 = Random
    
    // AD Structure 3: LE Role (0x00 = Only Peripheral)
    *ptr++ = 0x02;
    *ptr++ = BLE_AD_TYPE_LE_ROLE;
    *ptr++ = 0x00;
    
    // AD Structure 4: Security Manager TK (16 байтів)
    *ptr++ = 0x11; // 17 байтів (1 байт Type + 16 байтів TK)
    *ptr++ = BLE_AD_TYPE_TK;
    memcpy(ptr, tk, 16);
    ptr += 16;
    
    // AD Structure 5: Complete Local Name (опціонально)
    if (name_len > 0) {
        *ptr++ = (uint8_t)(1 + name_len);
        *ptr++ = BLE_AD_TYPE_NAME;
        memcpy(ptr, device_name, name_len);
        ptr += name_len;
    }
    
    msg->length += (record_overhead + payload_len);
    msg->record_count++;
    return NDEF_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <array>
#include <algorithm>

namespace embedded::nfc {

enum class Tnf : uint8_t {
    Empty      = 0x00,
    WellKnown  = 0x01,
    MimeMedia  = 0x02,
    AbsoluteUri= 0x03,
    External   = 0x04
};

enum class Status {
    Ok,
    BufferOverflow,
    InvalidParam
};

namespace flags {
    inline constexpr uint8_t MessageBegin = 0x80;
    inline constexpr uint8_t MessageEnd   = 0x40;
    inline constexpr uint8_t ShortRecord  = 0x10;
}

namespace ble_ad {
    inline constexpr uint8_t Flags       = 0x01;
    inline constexpr uint8_t Name        = 0x09;
    inline constexpr uint8_t SecurityTk  = 0x10;
    inline constexpr uint8_t LeAddress   = 0x1B;
    inline constexpr uint8_t LeRole      = 0x1C;
}

class NdefMessageBuilder {
public:
    explicit constexpr NdefMessageBuilder(std::span<uint8_t> storage) noexcept
        : buffer_(storage), length_(0), record_count_(0) {}

    [[nodiscard]] size_t size() const noexcept { return length_; }
    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return buffer_.subspan(0, length_);
    }

    Status addUri(uint8_t prefixCode, std::string_view uri, bool isLast) noexcept {
        const size_t payloadLen = 1 + uri.size();
        constexpr size_t recordOverhead = 4; // Header, TypeLen, PayloadLen, Type('U')

        if (length_ + recordOverhead + payloadLen > buffer_.size()) {
            return Status::BufferOverflow;
        }

        uint8_t header = flags::ShortRecord | static_cast<uint8_t>(Tnf::WellKnown);
        if (record_count_ == 0) header |= flags::MessageBegin;
        if (isLast) header |= flags::MessageEnd;

        auto* ptr = buffer_.data() + length_;
        *ptr++ = header;
        *ptr++ = 0x01; // Type Length = 1
        *ptr++ = static_cast<uint8_t>(payloadLen);
        *ptr++ = 'U';
        *ptr++ = prefixCode;
        std::copy_n(uri.data(), uri.size(), ptr);

        length_ += (recordOverhead + payloadLen);
        record_count_++;
        return Status::Ok;
    }

    Status addBleOob(std::span<const uint8_t, 6> macLe, 
                     uint8_t addrType, 
                     std::span<const uint8_t, 16> tk, 
                     std::string_view deviceName, 
                     bool isLast) noexcept {
        constexpr std::string_view mimeType = "application/vnd.bluetooth.ep.oob";
        const size_t nameLen = deviceName.size();
        
        // 3B (Flags) + 9B (LE Addr) + 3B (LE Role) + 18B (TK) + (Name)
        const size_t payloadLen = 3 + 9 + 3 + 18 + (nameLen > 0 ? (2 + nameLen) : 0);
        const size_t recordOverhead = 3 + mimeType.size();

        if (length_ + recordOverhead + payloadLen > buffer_.size()) {
            return Status::BufferOverflow;
        }

        uint8_t header = flags::ShortRecord | static_cast<uint8_t>(Tnf::MimeMedia);
        if (record_count_ == 0) header |= flags::MessageBegin;
        if (isLast) header |= flags::MessageEnd;

        auto* ptr = buffer_.data() + length_;
        *ptr++ = header;
        *ptr++ = static_cast<uint8_t>(mimeType.size());
        *ptr++ = static_cast<uint8_t>(payloadLen);
        ptr = std::copy_n(mimeType.data(), mimeType.size(), ptr);

        // 1. Flags
        *ptr++ = 0x02;
        *ptr++ = ble_ad::Flags;
        *ptr++ = 0x06;

        // 2. LE Device Address
        *ptr++ = 0x08;
        *ptr++ = ble_ad::LeAddress;
        ptr = std::copy_n(macLe.data(), 6, ptr);
        *ptr++ = addrType;

        // 3. LE Role
        *ptr++ = 0x02;
        *ptr++ = ble_ad::LeRole;
        *ptr++ = 0x00; // Peripheral only

        // 4. Security Manager TK
        *ptr++ = 0x11;
        *ptr++ = ble_ad::SecurityTk;
        ptr = std::copy_n(tk.data(), 16, ptr);

        // 5. Complete Local Name
        if (nameLen > 0) {
            *ptr++ = static_cast<uint8_t>(1 + nameLen);
            *ptr++ = ble_ad::Name;
            std::copy_n(deviceName.data(), nameLen, ptr);
        }

        length_ += (recordOverhead + payloadLen);
        record_count_++;
        return Status::Ok;
    }

private:
    std::span<uint8_t> buffer_;
    size_t length_;
    size_t record_count_;
};

} // namespace embedded::nfc
```
:::

## Запис NDEF TLV у пам'ять мітки по I2C

Для запису сформованого повідомлення у пам'ять мітки (наприклад, NTAG I2C Plus із розміром сторінки 16 байтів або ST25DV) створюється обгортка TLV:
1. Байт типу TLV: `0x03` (NDEF Message TLV);
2. Байт довжини: якщо довжина `< 255` байтів — 1 байт, якщо `≥ 255` байтів — три байти `0xFF`, `Len_High`, `Len_Low`;
3. Послідовність байтів NDEF-повідомлення;
4. Байт-термінатор: `0xFE` (Terminator TLV).

Оскільки комірки EEPROM вимагають часу внутрішнього запису (`t_WR` ≈ 4.5 мс), драйвер виконує запис блоками по 16 байтів та використовує апаратне опитування готовності (I2C Acknowledge Polling) або чекає завершення циклу перед наступною транзакцією.

:::tabs
```c
// Запис у NTAG I2C Plus починаючи з адреси блоку user memory (0x04)
ndef_status_t nfc_tag_write_ndef(uint8_t i2c_addr_7bit, 
                                 const uint8_t *ndef_raw, 
                                 size_t ndef_len,
                                 bool (*i2c_write_fn)(uint8_t addr, uint8_t mem_addr, const uint8_t *data, size_t len)) {
    if (!ndef_raw || ndef_len == 0 || !i2c_write_fn) return NDEF_ERR_INVALID_PARAM;
    
    // Формуємо образ памяті з TLV структурою
    uint8_t memory_image[256];
    size_t offset = 0;
    
    // Capability Container (CC) для NTAG I2C (блок 0x03) зазвичай уже прошитий.
    // Починаємо формувати NDEF TLV:
    memory_image[offset++] = 0x03; // NDEF TLV Marker
    if (ndef_len < 255) {
        memory_image[offset++] = (uint8_t)ndef_len;
    } else {
        memory_image[offset++] = 0xFF;
        memory_image[offset++] = (uint8_t)(ndef_len >> 8);
        memory_image[offset++] = (uint8_t)(ndef_len & 0xFF);
    }
    
    memcpy(&memory_image[offset], ndef_raw, ndef_len);
    offset += ndef_len;
    memory_image[offset++] = 0xFE; // Terminator TLV
    
    // Запис сторінками по 16 байтів у пам'ять мітки
    uint8_t start_block = 0x04; // Перший блок користувацької EEPROM
    size_t bytes_written = 0;
    
    while (bytes_written < offset) {
        size_t chunk = offset - bytes_written;
        if (chunk > 16) chunk = 16;
        
        uint8_t page_buf[16] = {0};
        memcpy(page_buf, &memory_image[bytes_written], chunk);
        
        if (!i2c_write_fn(i2c_addr_7bit, start_block, page_buf, 16)) {
            return NDEF_ERR_I2C_FAULT;
        }
        
        start_block++;
        bytes_written += chunk;
    }
    
    return NDEF_OK;
}
```
```cpp
namespace embedded::nfc {

template <typename I2cDriver>
class NtagI2cWriter {
public:
    explicit NtagI2cWriter(I2cDriver& i2c, uint8_t i2cAddress = 0x55) noexcept
        : i2c_(i2c), address_(i2cAddress) {}

    Status writeNdef(std::span<const uint8_t> ndefData) noexcept {
        if (ndefData.empty() || ndefData.size() > 240) {
            return Status::InvalidParam;
        }

        std::array<uint8_t, 256> memoryImage{};
        size_t offset = 0;

        // 1. TLV Marker
        memoryImage[offset++] = 0x03;
        if (ndefData.size() < 255) {
            memoryImage[offset++] = static_cast<uint8_t>(ndefData.size());
        } else {
            memoryImage[offset++] = 0xFF;
            memoryImage[offset++] = static_cast<uint8_t>(ndefData.size() >> 8);
            memoryImage[offset++] = static_cast<uint8_t>(ndefData.size() & 0xFF);
        }

        // 2. NDEF Data
        std::copy(ndefData.begin(), ndefData.end(), memoryImage.begin() + offset);
        offset += ndefData.size();

        // 3. Terminator TLV
        memoryImage[offset++] = 0xFE;

        // 4. Посторінковий запис по 16 байтів
        uint8_t startBlock = 0x04;
        size_t bytesWritten = 0;

        while (bytesWritten < offset) {
            const size_t chunk = std::min<size_t>(16, offset - bytesWritten);
            std::array<uint8_t, 16> pageBuf{};
            std::copy_n(memoryImage.begin() + bytesWritten, chunk, pageBuf.begin());

            if (!i2c_.writeMemoryBlock(address_, startBlock, pageBuf)) {
                return Status::InvalidParam;
            }

            startBlock++;
            bytesWritten += chunk;
        }

        return Status::Ok;
    }

private:
    I2cDriver& i2c_;
    uint8_t address_;
};

} // namespace embedded::nfc
```
:::

## Обробка апаратного переривання Field Detect (FD)

Для мінімізації енергоспоживання мікроконтролер переводиться в режим глибокого сну (Standby / Deep Sleep), з якого виводиться сигналом логічного нуля на виводі `FD`. Обробник переривання визначає джерело події та запускає відповідну процедуру:

1. **Вхід у поле (Field Presence Detected):** Мікроконтролер активує внутрішні тактові генератори (PLL/HSI), перевіряє статус заряду батареї та генерує новий псевдовипадковий 128-бітний ключ `TK` або пару `Confirm / Random` за допомогою апаратного криптографічного генератора TRNG;
2. **Оновлення NDEF:** Оновлені ключі спаровування записуються в EEPROM чипа NFC;
3. **Активація радіотракту BLE:** Стек Bluetooth вмикає швидке спрямоване рекламування (Fast Directed Advertising з інтервалом 20 мс) на обмежений час (наприклад, вікно у 30 секунд);
4. **Вихід із поля (Field Lost):** Якщо спаровування не відбулося протягом таймауту, мікроконтролер гасить радіопередавач та знову переходить у глибокий сон.

## Типові підводні камені реалізації

- **Порядок байтів MAC-адреси:** У структурі `AD Type = 0x1B` (LE Device Address) MAC-адреса передається у форматі **Little-Endian** (найменш значущий байт іде першим), тоді як довжина NDEF-запису для довгих повідомлень (`SR = 0`) кодується у форматі **Big-Endian**. Плутанина у порядку байтів призводить до того, що смартфон намагається підключитися до неіснуючої або дзеркальної MAC-адреси.
- **Clock Stretching під час запису в EEPROM:** Якщо мікроконтролер надсилає наступну I2C-транзакцію до завершення внутрішнього циклу програмування комірок (`t_WR`), чип утримує лінію `SCL` у нулі (clock stretching) або відповідає `NACK`. I2C-драйвер мікроконтролера повинен коректно обробляти тактове розтягування без скидання шини за короткочасним таймаутом.
- **Блокування арбітражу при читанні телефоном:** Якщо в момент запису мікроконтролером по I2C смартфон активно вичитує сусідній сектор по RF, чип виставить прапорець зайнятості. Драйвер повинен реалізувати обмежену кількість повторних спроб (retry loop із експоненційною затримкою 1–2 мс) перед поверненням статусу помилки.

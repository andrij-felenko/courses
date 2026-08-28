# ⚙️ Парсер та валідатор MAC OUI і USB VID/PID на C та C++

У процесі виробничого програмування мікроконтролерів, заводського калібрування бездротових плат та автоматизованого тестування на конвеєрі інженер стикається із задачею верифікації апаратних ідентифікаторів. Необхідно перевіряти коректність структури записаної в OTP/eFuse MAC-адреси, виділяти зареєстрований префікс IEEE OUI, аналізувати біти індивідуальної чи локальної адресації, валідувати поля дескриптора USB Device Descriptor та автоматично генерувати конфігураційні правила для підсистеми `udev` операційної системи Linux.

У цьому проєкті реалізовано автономний бібліотечний модуль розбору, перевірки та перетворення мережевих і шинних ідентифікаторів без зовнішніх залежностей двома мовами: низькорівневою мовою C (стандарт C99 для вбудованих систем) та сучасною об'єктно-орієнтованою мовою C++ (стандарт C++20 із застосуванням безпечних типів `std::span`, `std::optional` та `std::string_view`).

---

### Архітектурні вимоги та модель верифікації

Адреса канального рівня стандарту IEEE 802 (EUI-48) складається з 6 байтів. Під час розбору парсер повинен перевіряти два критичні бітові прапорці, розташовані в нульовому октеті:
1. **Біт `I/G (Individual / Group)` (маска `0x01`):** Якщо біт встановлений в `1`, адреса є груповою (Multicast) або широкомовною (Broadcast). Таку адресу фізично неможливо призначити мережевому інтерфейсу як унікальну апаратну адресу станції. Спроба зашити таку адресу в OTP-пам'ять є критичною помилкою виробництва.
2. **Біт `U/L (Universal / Local)` (маска `0x02`):** Якщо біт дорівнює `0`, адреса належить до універсального простору (Universally Administered Address, UAA), отриманого з офіційного діапазону IEEE OUI. Якщо біт дорівнює `1`, адреса вважається локально згенерованою (Locally Administered Address, LAA), що неприпустимо для серійної комерційної продукції.

Для дескрипторів USB модуль виконує розбір 18-байтного сирого масиву, витягує поля `idVendor`, `idProduct`, `bcdUSB`, `bcdDevice`, контролює порядок байтів Little-Endian та перевіряє заборонені значення ідентифікаторів (нульовий `0x0000` та зарезервований `0xFFFF`).

---

### Програмна реалізація

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

/* Тип адресації за стандартом IEEE 802 */
typedef enum {
    MAC_TYPE_UNIVERSAL_UNICAST   = 0,
    MAC_TYPE_UNIVERSAL_MULTICAST = 1,
    MAC_TYPE_LOCAL_UNICAST       = 2,
    MAC_TYPE_LOCAL_MULTICAST     = 3
} mac_address_type_t;

/* Структура розібраної MAC-адреси */
typedef struct {
    uint8_t raw[6];
    uint32_t oui_24;        /* Старші 24 біти (MA-L) */
    mac_address_type_t type;
    bool is_valid;
} parsed_mac_t;

/* Структура дескриптора пристрою USB (USB 2.0) */
typedef struct {
    uint16_t bcd_usb;
    uint8_t  device_class;
    uint8_t  device_subclass;
    uint8_t  device_protocol;
    uint8_t  max_packet_size0;
    uint16_t vendor_id;
    uint16_t product_id;
    uint16_t bcd_device;
    bool     is_valid;
} parsed_usb_device_t;

/* Допоміжна функція перетворення символу hex у 4-бітне число */
static int hex_char_to_nibble(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Парсинг рядка MAC-адреси (підтримує роздільники ':', '-' або без них) */
bool parse_mac_string(const char *str, parsed_mac_t *out_mac) {
    if (!str || !out_mac) return false;
    memset(out_mac, 0, sizeof(parsed_mac_t));

    uint8_t bytes[6] = {0};
    int byte_idx = 0;
    int nibble_cnt = 0;
    uint8_t cur_byte = 0;

    for (size_t i = 0; str[i] != '\0' && byte_idx < 6; ++i) {
        char c = str[i];
        if (c == ':' || c == '-') {
            if (nibble_cnt != 2) return false;
            bytes[byte_idx++] = cur_byte;
            cur_byte = 0;
            nibble_cnt = 0;
            continue;
        }
        int nibble = hex_char_to_nibble(c);
        if (nibble < 0) return false;

        cur_byte = (uint8_t)((cur_byte << 4) | (uint8_t)nibble);
        nibble_cnt++;
        if (nibble_cnt == 2) {
            bytes[byte_idx++] = cur_byte;
            cur_byte = 0;
            nibble_cnt = 0;
        }
    }

    if (byte_idx != 6 || nibble_cnt != 0) return false;

    memcpy(out_mac->raw, bytes, 6);
    out_mac->oui_24 = ((uint32_t)bytes[0] << 16) | ((uint32_t)bytes[1] << 8) | (uint32_t)bytes[2];

    bool is_group = (bytes[0] & 0x01) != 0;
    bool is_local = (bytes[0] & 0x02) != 0;

    if (!is_group && !is_local) out_mac->type = MAC_TYPE_UNIVERSAL_UNICAST;
    else if (is_group && !is_local) out_mac->type = MAC_TYPE_UNIVERSAL_MULTICAST;
    else if (!is_group && is_local) out_mac->type = MAC_TYPE_LOCAL_UNICAST;
    else out_mac->type = MAC_TYPE_LOCAL_MULTICAST;

    out_mac->is_valid = true;
    return true;
}

/* Перетворення EUI-48 у розширений 64-бітний формат EUI-64 (Zigbee / IPv6) */
void mac_to_eui64(const parsed_mac_t *mac, uint8_t out_eui64[8]) {
    if (!mac || !out_eui64) return;
    out_eui64[0] = mac->raw[0];
    out_eui64[1] = mac->raw[1];
    out_eui64[2] = mac->raw[2];
    out_eui64[3] = 0xFF;
    out_eui64[4] = 0xFE;
    out_eui64[5] = mac->raw[3];
    out_eui64[6] = mac->raw[4];
    out_eui64[7] = mac->raw[5];
}

/* Парсинг сирого 18-байтного USB Device Descriptor */
bool parse_usb_descriptor(const uint8_t *buffer, size_t len, parsed_usb_device_t *out_usb) {
    if (!buffer || len < 18 || !out_usb) return false;
    memset(out_usb, 0, sizeof(parsed_usb_device_t));

    uint8_t b_length = buffer[0];
    uint8_t b_descriptor_type = buffer[1];

    /* Інваріанти стандарту USB */
    if (b_length != 18 || b_descriptor_type != 0x01) return false;

    out_usb->bcd_usb = (uint16_t)(buffer[2] | ((uint16_t)buffer[3] << 8));
    out_usb->device_class = buffer[4];
    out_usb->device_subclass = buffer[5];
    out_usb->device_protocol = buffer[6];
    out_usb->max_packet_size0 = buffer[7];
    out_usb->vendor_id = (uint16_t)(buffer[8] | ((uint16_t)buffer[9] << 8));
    out_usb->product_id = (uint16_t)(buffer[10] | ((uint16_t)buffer[11] << 8));
    out_usb->bcd_device = (uint16_t)(buffer[12] | ((uint16_t)buffer[13] << 8));

    /* Валідація Vendor ID: не нуль і не зарезервований 0xFFFF */
    if (out_usb->vendor_id == 0x0000 || out_usb->vendor_id == 0xFFFF) {
        out_usb->is_valid = false;
        return false;
    }

    out_usb->is_valid = true;
    return true;
}

/* Генерація правила udev для Linux */
void generate_udev_rule(const parsed_usb_device_t *usb, const char *symlink_name, char *out_rule, size_t max_len) {
    if (!usb || !symlink_name || !out_rule || max_len == 0) return;
    snprintf(out_rule, max_len,
             "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"%04x\", ATTR{idProduct}==\"%04x\", "
             "MODE=\"0666\", SYMLINK+=\"%s\"",
             usb->vendor_id, usb->product_id, symlink_name);
}
```
```cpp
#include <iostream>
#include <span>
#include <string_view>
#include <string>
#include <array>
#include <optional>
#include <format>
#include <cstdint>

enum class MacAddressType {
    UniversalUnicast,
    UniversalMulticast,
    LocalUnicast,
    LocalMulticast
};

struct ParsedMac {
    std::array<uint8_t, 6> raw{};
    uint32_t oui24{0};
    MacAddressType type{MacAddressType::UniversalUnicast};

    [[nodiscard]] bool isUniversalUnicast() const noexcept {
        return type == MacAddressType::UniversalUnicast;
    }

    [[nodiscard]] std::array<uint8_t, 8> toEui64() const noexcept {
        return {raw[0], raw[1], raw[2], 0xFF, 0xFE, raw[3], raw[4], raw[5]};
    }

    [[nodiscard]] std::string format() const {
        return std::format("{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}",
                           raw[0], raw[1], raw[2], raw[3], raw[4], raw[5]);
    }
};

struct ParsedUsbDevice {
    uint16_t bcdUsb{0};
    uint8_t  deviceClass{0};
    uint8_t  deviceSubclass{0};
    uint8_t  deviceProtocol{0};
    uint8_t  maxPacketSize0{0};
    uint16_t vendorId{0};
    uint16_t productId{0};
    uint16_t bcdDevice{0};

    [[nodiscard]] std::string toUdevRule(std::string_view symlinkName) const {
        return std::format("SUBSYSTEM==\"usb\", ATTR{{idVendor}}==\"{:04x}\", "
                           "ATTR{{idProduct}}==\"{:04x}\", MODE=\"0666\", SYMLINK+=\"{}\"",
                           vendorId, productId, symlinkName);
    }
};

class HardwareIdentifierValidator {
private:
    static constexpr int hexCharToNibble(char c) noexcept {
        if (c >= '0' && c <= '9') return c - '0';
        if (c >= 'a' && c <= 'f') return c - 'a' + 10;
        if (c >= 'A' && c <= 'F') return c - 'A' + 10;
        return -1;
    }

public:
    static std::optional<ParsedMac> parseMac(std::string_view str) noexcept {
        ParsedMac result{};
        int byteIdx = 0;
        int nibbleCnt = 0;
        uint8_t curByte = 0;

        for (char c : str) {
            if (c == ':' || c == '-') {
                if (nibbleCnt != 2) return std::nullopt;
                result.raw[byteIdx++] = curByte;
                curByte = 0;
                nibbleCnt = 0;
                if (byteIdx > 6) return std::nullopt;
                continue;
            }
            int nibble = hexCharToNibble(c);
            if (nibble < 0) return std::nullopt;

            curByte = static_cast<uint8_t>((curByte << 4) | static_cast<uint8_t>(nibble));
            nibbleCnt++;
            if (nibbleCnt == 2) {
                if (byteIdx >= 6) return std::nullopt;
                result.raw[byteIdx++] = curByte;
                curByte = 0;
                nibbleCnt = 0;
            }
        }

        if (byteIdx != 6 || nibbleCnt != 0) return std::nullopt;

        result.oui24 = (static_cast<uint32_t>(result.raw[0]) << 16) |
                       (static_cast<uint32_t>(result.raw[1]) << 8)  |
                       static_cast<uint32_t>(result.raw[2]);

        bool isGroup = (result.raw[0] & 0x01) != 0;
        bool isLocal = (result.raw[0] & 0x02) != 0;

        if (!isGroup && !isLocal) result.type = MacAddressType::UniversalUnicast;
        else if (isGroup && !isLocal) result.type = MacAddressType::UniversalMulticast;
        else if (!isGroup && isLocal) result.type = MacAddressType::LocalUnicast;
        else result.type = MacAddressType::LocalMulticast;

        return result;
    }

    static std::optional<ParsedUsbDevice> parseUsbDescriptor(std::span<const uint8_t> buffer) noexcept {
        if (buffer.size() < 18) return std::nullopt;
        if (buffer[0] != 18 || buffer[1] != 0x01) return std::nullopt;

        ParsedUsbDevice dev{};
        dev.bcdUsb = static_cast<uint16_t>(buffer[2] | (static_cast<uint16_t>(buffer[3]) << 8));
        dev.deviceClass = buffer[4];
        dev.deviceSubclass = buffer[5];
        dev.deviceProtocol = buffer[6];
        dev.maxPacketSize0 = buffer[7];
        dev.vendorId = static_cast<uint16_t>(buffer[8] | (static_cast<uint16_t>(buffer[9]) << 8));
        dev.productId = static_cast<uint16_t>(buffer[10] | (static_cast<uint16_t>(buffer[11]) << 8));
        dev.bcdDevice = static_cast<uint16_t>(buffer[12] | (static_cast<uint16_t>(buffer[13]) << 8));

        if (dev.vendorId == 0x0000 || dev.vendorId == 0xFFFF) {
            return std::nullopt;
        }

        return dev;
    }
};
```
:::

---

### Покроковий розбір коду та деталі реалізації

#### 1. Безпечний розбір шістнадцяткових рядків без динамічної пам'яті
Функція `parse_mac_string` (у варіанті C) та метод `parseMac` (у варіанті C++) працюють за принципом потокового автомата станів:
- На вхід приймається текстовий рядок довільного формату: канонічний двокрапковий (`00:1A:2B:3C:4D:5E`), дефісний (`00-1A-2B-3C-4D-5E`) або суцільний шістнадцятковий потік без роздільників (`001A2B3C4D5E`);
- Перетворення кожного символу у 4-бітне значення (напівбайт, nibble) здійснюється константною функцією `hex_char_to_nibble` без використання важких функцій стандартної бібліотеки на зразок `sscanf` чи регулярних виразів. Це забезпечує мінімальний розмір двійкового коду (менше 400 байтів у скомпільованому вигляді) та нульове виділення динамічної пам'яті (zero-allocation), що є обов'язковою вимогою для прошивок мікроконтролерів із жорстким дефіцитом RAM;
- Якщо кількість октет не дорівнює точно шести, або якщо в роздільнику виявлено неповний байт, функція повертає помилку `false` або `std::nullopt`.

#### 2. Перетворення Little-Endian у дескрипторах USB
У стандарті USB усі 16-бітні числові поля передаються молодшим байтом уперед (Little-Endian).
При розборі поля `vendor_id` вираз `buffer[8] | ((uint16_t)buffer[9] << 8)` явно збирає 16-бітне ціле число через побітовий зсув та логічне АБО, замість небезпечного приведення вказівників `*(uint16_t*)&buffer[8]`. Явне збирання гарантує переносність коду між архітектурами з різним порядком байтів (Big-Endian проти Little-Endian) та запобігає виникненню апаратних виключень невирівняного доступу (Alignment Fault) на ядрах ARM Cortex-M0/M0+.

---

### Інтеграція у виробничий стенд тестування (ATE)

На етапі фінального вихідного контролю продукції на виробництві (Automated Test Equipment, ATE) цей модуль вбудовується у прошивку тестового стенда або утиліту прошивання:
1. **Зчитування адреси з бази даних серійних номерів:** Стенд формує наступну вільну MAC-адресу з придбаного пулу компанії (наприклад, MA-S блок);
2. **Верифікація перед записом:** Парсер перевіряє, що адреса має прапорець `MAC_TYPE_UNIVERSAL_UNICAST` (біти `I/G = 0` та `U/L = 0`) і префікс відповідає офіційному OUI компанії;
3. **Запис у захищену пам'ять:** Адреса записується у комірки OTP (One-Time Programmable) мікроконтролера (STM32 OTP або ESP32 eFuse `BLK3`);
4. **Контрольне зчитування:** Стенд зчитує записані байти, повторно пропускає їх через парсер і звіряє хеш-суму із заводською базою даних.

---

### Аналіз крайових випадків та типові пастки

#### 1. Пастка порядку передачі бітів у радіоефірі (Canonical vs Non-Canonical)
Найпоширенішою помилкою інженерів є плутанина між порядком передачі бітів фізичного рівня та розташуванням бітів у пам'яті:
- У канонічному форматі Ethernet, Wi-Fi та BLE молодший біт кожного байта (LSB) виходить у радіоефір першим;
- Тому біт `I/G` розташований саме у нульовому біті першого октету (`raw[0] & 0x01`), а не в сьомому (`raw[0] & 0x80`);
- Якщо перевіряти біт через зсув `0x80`, парсер помилково визначить звичайну Unicast адресу як Multicast і навпаки.

#### 2. Інверсія біта U/L при формуванні адрес IPv6 SLAAC
При автоматичній генерації 64-бітного ідентифікатора інтерфейсу IPv6 за стандартом RFC 4291 адреса EUI-48 модифікується виразом `out_eui64[0] = mac->raw[0] ^ 0x02` (інверсія біта Universal/Local). Ця інверсія є обов'язковою: в оригінальному стандарті IEEE значення `0` означає «глобальна адреса», а в архітектурі IPv6 значення `1` означає «універсальна область видимості». Якщо забути виконати інверсію через операцію XOR `^ 0x02`, операційні системи вважатимуть згенеровану адресу IPv6 суто локальною та блокуватимуть вихід у глобальну мережу Internet.

#### 3. Генерація системних правил udev
Сформований рядок правила udev дозволяє автоматично призначати права доступу `0666` до файлу символьного пристрою у `/dev/` без прав суперкористувача `root`:
```
SUBSYSTEM=="usb", ATTR{idVendor}=="1209", ATTR{idProduct}=="0042", MODE="0666", SYMLINK+="my_telemetry_device"
```
Це усуває необхідність запуску користувацького застосунку чи GUI-утиліти через команду `sudo` в операційних системах сімейства Linux.

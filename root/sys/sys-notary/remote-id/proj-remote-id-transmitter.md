# ⚙️ Генератор і передавач повідомлень Open Drone ID на мікроконтролері

Розробка автономного модуля прямої цифрової ідентифікації (Direct Remote ID Add-on Module) або інтеграція відповідного стека у прошивку польотного контролера вимагає побудови надійного вбудованого конвеєра обробки даних реального часу. Система повинна безперервно приймати навігаційні пакети від супутникового приймача (GNSS NMEA/UBX), витягувати телеметрію стану апарата від автопілота, квантувати числові величини у двійковий формат ASTM F3411 та формувати сирі радіопакети для передачі через контролери Bluetooth Low Energy (BLE) і Wi-Fi.

Головна інженерна вимога до такого передавача — детермінованість та автономність: передача не повинна перериватися навіть за умов тимчасової втрати радіозв'язку з наземним пультом керування або збоїв основного процесора автопілота.

---

### Архітектура вбудованого конвеєра передавача

Конвеєр обробки даних на мікроконтролері під керуванням операційної системи реального часу (FreeRTOS або Zephyr RTOS) розділяється на три ізольовані задачі з пріоритетним плануванням:

1. **Задача прийому телеметрії (Telemetry Ingestion Task, пріоритет High):**
   - Фоновий потік або апаратне переривання UART із прямим доступом до пам'яті (DMA) приймає бінарні пакети протоколу `UBX-NAV-PVT` від модуля GNSS із частотою 5–10 Гц.
   - Одночасно через додатковий порт UART зчитуються стандартні повідомлення MAVLink: `OPEN_DRONE_ID_LOCATION` (Message ID 12901), `OPEN_DRONE_ID_BASIC_ID` (Message ID 12900) та `OPEN_DRONE_ID_SYSTEM` (Message ID 12904) від прошивок ArduPilot або PX4.
   - Дані верифікуються за контрольними сумами та складаються у потокобезпечний кільцевий буфер (Ring Buffer).

2. **Задача квантування та серіалізації (Quantization & Framing Task, пріоритет Medium):**
   - Виконується кожні 100–200 мс. Географічні координати (широта та довгота) переводяться з чисел з рухомою комою подвійної точності (`double`) у 32-бітні знакові цілі числа шляхом множення на `10 000 000`.
   - Висоти над еліпсоїдом WGS84 та барометричні дані зміщуються на базис +1000 метрів і квантуються з кроком 0.5 метра у 16-бітні значення `uint16_t`.
   - Обчислюється часова мітка поточної години UTC з роздільною здатністю 100 мс (0.1 секунди).
   - Формуються двійкові структури ASTM F3411 для кожного типу повідомлень.

3. **Задача радіомовлення (RF Emission Task, пріоритет Real-Time):**
   - Для застарілого каналу Bluetooth 4.2 Legacy таймер формує 250-мілісекундні кванти передачі, почергово завантажуючи в апаратний буфер радіотракту повідомлення Basic ID (0x0), Location (0x1), System Data (0x4) та повторно Location (0x1).
   - Для каналів Bluetooth 5 Coded PHY та Wi-Fi Beacon формується єдиний контейнер `Message Pack` (тип 0xF), який транслюється з фіксованою частотою 1.0 Гц.
   - Драйвер Wi-Fi формує сирий кадр управління IEEE 802.11 Beacon Frame з інформаційним елементом `Vendor Specific IE (0xDD)` і відправляє його в радіоефір на фіксованому каналі 6 у режимі прямої ін'єкції пакетів (Promiscuous / Raw Frame Injection).

---

### Структура кадру Wi-Fi Beacon для Open Drone ID

Для передачі ідентифікації через Wi-Fi мікроконтролер генерує сирий двійковий кадр управління (Management Frame, підтип `0x0080` — Beacon):
```
[ 802.11 MAC Header (24 байти) ]
  - Frame Control: 0x0080 (Type: Management, Subtype: Beacon)
  - Duration: 0x0000
  - Destination Address: FF:FF:FF:FF:FF:FF (Broadcast)
  - Source Address: MAC-адреса передавача
  - BSSID: MAC-адреса передавача
  - Sequence Control: Інкрементний лічильник фрагментів

[ Beacon Fixed Parameters (12 байтів) ]
  - Timestamp: 8 байтів апаратного таймера TSF (Timer Synchronization Function)
  - Beacon Interval: 0x0064 (100 TU = 102.4 мс)
  - Capability Info: 0x0021 (ESS, Short Preamble)

[ Tagged Parameters (Information Elements) ]
  - SSID IE: Tag 0, Length 0 (Прихована мережа) або «RID-xxxx»
  - Supported Rates IE: Tag 1, Length 8 (1, 2, 5.5, 11, 6, 9, 12, 24 Мбіт/с)
  - DS Parameter Set IE: Tag 3, Length 1 (Channel 6)
  - Vendor Specific IE: Tag 221 (0xDD), Length 82 байти
      * OUI: 0xFA-0B-BC (Wi-Fi Alliance Remote ID)
      * OUI Type: 0x0D (Open Drone ID Application)
      * Payload: Message Pack 0xF (78 байтів: Basic ID + Location + System Data)
```

---

### Програмна реалізація генератора на C та C++

Нижче наведено самодостатній та переносний модуль кодування повідомлень ASTM F3411 двома мовами: чистим C99 для апаратних драйверів та ідіоматичним C++20 із нульовими накладними витратами пам'яті (англ. *zero-cost abstractions*), суворою типізацією та представленням масивів через `std::span`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#pragma pack(push, 1)

#define ODID_MSG_SIZE 25
#define ODID_PROTOCOL_VERSION 0x01

typedef enum {
    ODID_MSG_TYPE_BASIC_ID   = 0x0,
    ODID_MSG_TYPE_LOCATION   = 0x1,
    ODID_MSG_TYPE_AUTH       = 0x2,
    ODID_MSG_TYPE_SELF_ID    = 0x3,
    ODID_MSG_TYPE_SYSTEM     = 0x4,
    ODID_MSG_TYPE_OPERATOR   = 0x5,
    ODID_MSG_TYPE_PACK       = 0xF
} odid_msg_type_t;

typedef enum {
    ODID_ID_TYPE_SERIAL_NUMBER = 1,
    ODID_ID_TYPE_CAA           = 2,
    ODID_ID_TYPE_SESSION_ID    = 4
} odid_id_type_t;

typedef enum {
    ODID_UA_TYPE_AEROPLANE   = 1,
    ODID_UA_TYPE_HELICOPTER  = 2,
    ODID_UA_TYPE_MULTIROTOR  = 15
} odid_ua_type_t;

typedef enum {
    ODID_STATUS_UNDECLARED = 0,
    ODID_STATUS_GROUND     = 1,
    ODID_STATUS_AIRBORNE   = 2,
    ODID_STATUS_EMERGENCY  = 3
} odid_status_t;

/* Структура 0x0: Basic ID (25 байтів) */
typedef struct {
    uint8_t header;             /* Старші 4 біти: 0x0, молодші: Protocol Version */
    uint8_t id_ua_type;         /* Старші 4 біти: id_type, молодші: ua_type */
    uint8_t uas_id[20];         /* ASCII рядок серійного номера ANSI/CTA-2063-A */
    uint8_t reserved[3];
} odid_basic_id_t;

/* Структура 0x1: Location/Vector (25 байтів) */
typedef struct {
    uint8_t header;             /* Старші 4 біти: 0x1, молодші: Protocol Version */
    uint8_t status_flags;       /* Старші 4 біти: Status (0..3) */
    uint8_t direction;          /* Напрямок руху 0..359 град (крок 1 град) */
    uint8_t speed_horizontal;   /* Швидкість horiz (крок 0.25 м/с) */
    int8_t  speed_vertical;     /* Швидкість vert (крок 0.5 м/с, зі знаком) */
    int32_t latitude;           /* Широта: grad * 1e7 */
    int32_t longitude;          /* Довгота: grad * 1e7 */
    uint16_t altitude_geodetic; /* Висота WGS84: (alt_m + 1000.0) / 0.5 */
    uint16_t altitude_pressure; /* Висота барометрична */
    uint16_t height_agl;        /* Висота над землею (AGL) */
    uint8_t horiz_vert_acc;     /* Старші 4 біти: HAcc (0..13), молодші: VAcc */
    uint8_t baro_speed_acc;     /* Старші 4 біти: BaroAcc, молодші: SpeedAcc */
    uint16_t timestamp;         /* Десяті частки секунди поточної години (0..35999) */
    uint8_t time_adv_acc;       /* Точність часу та інтервал */
    uint8_t reserved;
} odid_location_t;

/* Структура 0x4: System Data (25 байтів) */
typedef struct {
    uint8_t header;             /* Старші 4 біти: 0x4, молодші: Protocol Version */
    uint8_t operator_loc_type;  /* 0 = Takeoff, 1 = Live GNSS, 2 = Fixed */
    int32_t operator_latitude;  /* Широта оператора: grad * 1e7 */
    int32_t operator_longitude; /* Довгота оператора: grad * 1e7 */
    uint16_t area_count;        /* Кількість БПЛА в групі */
    uint8_t area_radius;        /* Радіус зони: крок 10 м */
    uint16_t area_ceiling;      /* Верхня стеля зони */
    uint16_t area_floor;        /* Нижня підлога зони */
    uint8_t classification;     /* Категорія EASA Open/Specific */
    uint16_t operator_altitude; /* Геодезична висота оператора WGS84 */
    uint32_t system_timestamp;  /* UTC секунди Unix */
    uint8_t reserved;
} odid_system_t;

/* Структура 0xF: Message Pack (Об'єднання повідомлень) */
typedef struct {
    uint8_t header;             /* 0xF1 */
    uint8_t msg_pack_size;      /* Розмір одного елемента = 25 байтів */
    uint8_t msg_count;          /* Кількість вкладених повідомлень */
    uint8_t messages[3 * ODID_MSG_SIZE]; /* Basic ID + Location + System */
} odid_msg_pack_t;

#pragma pack(pop)

/* Кодування повідомлення Basic ID */
void odid_encode_basic_id(odid_basic_id_t *out, odid_id_type_t id_type, 
                          odid_ua_type_t ua_type, const char *serial_str) {
    memset(out, 0, sizeof(odid_basic_id_t));
    out->header = (ODID_MSG_TYPE_BASIC_ID << 4) | (ODID_PROTOCOL_VERSION & 0x0F);
    out->id_ua_type = ((id_type & 0x0F) << 4) | (ua_type & 0x0F);
    size_t len = strlen(serial_str);
    if (len > 20) len = 20;
    memcpy(out->uas_id, serial_str, len);
}

/* Кодування повідомлення Location */
void odid_encode_location(odid_location_t *out, odid_status_t status,
                          double lat_deg, double lon_deg, double alt_wgs84_m,
                          double speed_h_mps, double speed_v_mps, double heading_deg,
                          uint32_t sec_in_hour, uint32_t ms_fraction) {
    memset(out, 0, sizeof(odid_location_t));
    out->header = (ODID_MSG_TYPE_LOCATION << 4) | (ODID_PROTOCOL_VERSION & 0x0F);
    out->status_flags = (status & 0x0F) << 4;

    int hdg = (int)round(heading_deg);
    if (hdg < 0) hdg = (hdg % 360) + 360;
    out->direction = (uint8_t)(hdg % 360);

    out->speed_horizontal = (uint8_t)(fmin(speed_h_mps / 0.25, 254.0));
    out->speed_vertical = (int8_t)(fmax(-127.0, fmin(speed_v_mps / 0.5, 127.0)));

    out->latitude = (int32_t)round(lat_deg * 10000000.0);
    out->longitude = (int32_t)round(lon_deg * 10000000.0);

    double alt_enc = (alt_wgs84_m + 1000.0) / 0.5;
    if (alt_enc < 0.0) alt_enc = 0.0;
    if (alt_enc > 65535.0) alt_enc = 65535.0;
    out->altitude_geodetic = (uint16_t)round(alt_enc);
    out->altitude_pressure = out->altitude_geodetic;

    out->horiz_vert_acc = (11 << 4) | (10 & 0x0F);
    out->baro_speed_acc = (10 << 4) | (10 & 0x0F);

    uint32_t tenths = (sec_in_hour % 3600) * 10 + (ms_fraction / 100);
    out->timestamp = (uint16_t)(tenths % 36000);
    out->time_adv_acc = 0x10;
}

/* Формування пакету Bluetooth 4.2 Legacy Advertising (32 байти PDU) */
uint8_t odid_build_ble4_packet(uint8_t *out_pdu, const void *odid_msg) {
    out_pdu[0] = 0x02; /* Довжина секції Flags */
    out_pdu[1] = 0x01; /* AD Type = Flags */
    out_pdu[2] = 0x06; /* LE General Discoverable Mode */

    out_pdu[3] = 0x1B; /* Довжина секції Service Data: 1 + 2 + 25 = 28 байтів (0x1B) */
    out_pdu[4] = 0x16; /* AD Type = Service Data - 16-bit UUID */
    out_pdu[5] = 0xFA; /* OpenDroneID UUID: 0xFFFA (Little-endian) */
    out_pdu[6] = 0xFF;

    memcpy(&out_pdu[7], odid_msg, ODID_MSG_SIZE);
    return 32;
}
```
```cpp
#include <array>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <span>
#include <algorithm>
#include <string_view>

namespace remote_id {

inline constexpr std::size_t MsgSize = 25;
inline constexpr uint8_t ProtocolVersion = 0x01;
inline constexpr uint16_t OpenDroneIdUuid = 0xFFFA;

enum class MsgType : uint8_t {
    BasicId   = 0x0,
    Location  = 0x1,
    Auth      = 0x2,
    SelfId    = 0x3,
    System    = 0x4,
    Operator  = 0x5,
    Pack      = 0xF
};

enum class IdType : uint8_t {
    SerialNumber = 1,
    Caa          = 2,
    SessionId    = 4
};

enum class UaType : uint8_t {
    Aeroplane   = 1,
    Helicopter  = 2,
    Multirotor  = 15
};

enum class FlightStatus : uint8_t {
    Undeclared = 0,
    Ground     = 1,
    Airborne   = 2,
    Emergency  = 3
};

#pragma pack(push, 1)

struct alignas(1) BasicIdMessage {
    uint8_t header{static_cast<uint8_t>((static_cast<uint8_t>(MsgType::BasicId) << 4) | (ProtocolVersion & 0x0F))};
    uint8_t id_ua_type{0};
    std::array<uint8_t, 20> uas_id{};
    std::array<uint8_t, 3> reserved{};

    constexpr BasicIdMessage(IdType id_type, UaType ua_type, std::string_view serial) noexcept {
        id_ua_type = static_cast<uint8_t>((static_cast<uint8_t>(id_type) << 4) | (static_cast<uint8_t>(ua_type) & 0x0F));
        const auto copy_len = std::min(serial.size(), uas_id.size());
        for (std::size_t i = 0; i < copy_len; ++i) {
            uas_id[i] = static_cast<uint8_t>(serial[i]);
        }
    }
};

struct alignas(1) LocationMessage {
    uint8_t header{static_cast<uint8_t>((static_cast<uint8_t>(MsgType::Location) << 4) | (ProtocolVersion & 0x0F))};
    uint8_t status_flags{0};
    uint8_t direction{0};
    uint8_t speed_horizontal{0};
    int8_t  speed_vertical{0};
    int32_t latitude{0};
    int32_t longitude{0};
    uint16_t altitude_geodetic{0};
    uint16_t altitude_pressure{0};
    uint16_t height_agl{0};
    uint8_t horiz_vert_acc{0xBA}; /* HAcc=11, VAcc=10 */
    uint8_t baro_speed_acc{0xAA}; /* BaroAcc=10, SpeedAcc=10 */
    uint16_t timestamp{0};
    uint8_t time_adv_acc{0x10};
    uint8_t reserved{0};

    LocationMessage(FlightStatus status, double lat_deg, double lon_deg, double alt_m,
                    double speed_h, double speed_v, double heading_deg,
                    uint32_t sec_in_hour, uint32_t ms_part) noexcept {
        status_flags = static_cast<uint8_t>(static_cast<uint8_t>(status) << 4);

        int hdg = static_cast<int>(std::round(heading_deg));
        if (hdg < 0) hdg = (hdg % 360) + 360;
        direction = static_cast<uint8_t>(hdg % 360);

        speed_horizontal = static_cast<uint8_t>(std::clamp(speed_h / 0.25, 0.0, 254.0));
        speed_vertical = static_cast<int8_t>(std::clamp(speed_v / 0.5, -127.0, 127.0));

        latitude = static_cast<int32_t>(std::round(lat_deg * 1e7));
        longitude = static_cast<int32_t>(std::round(lon_deg * 1e7));

        double alt_enc = std::clamp((alt_m + 1000.0) / 0.5, 0.0, 65535.0);
        altitude_geodetic = static_cast<uint16_t>(std::round(alt_enc));
        altitude_pressure = altitude_geodetic;

        uint32_t tenths = (sec_in_hour % 3600) * 10 + (ms_part / 100);
        timestamp = static_cast<uint16_t>(tenths % 36000);
    }
};

struct alignas(1) Ble4Packet {
    uint8_t flags_len{0x02};
    uint8_t flags_type{0x01};
    uint8_t flags_val{0x06};

    uint8_t service_len{0x1B};
    uint8_t service_type{0x16};
    uint8_t uuid_lo{static_cast<uint8_t>(OpenDroneIdUuid & 0xFF)};
    uint8_t uuid_hi{static_cast<uint8_t>((OpenDroneIdUuid >> 8) & 0xFF)};
    std::array<uint8_t, MsgSize> payload{};

    template <typename TMsg>
    explicit Ble4Packet(const TMsg& msg) noexcept {
        static_assert(sizeof(TMsg) == MsgSize, "Повідомлення Open Drone ID повинно мати рівно 25 байтів");
        std::memcpy(payload.data(), &msg, MsgSize);
    }

    [[nodiscard]] std::span<const uint8_t> as_bytes() const noexcept {
        return {reinterpret_cast<const uint8_t*>(this), sizeof(Ble4Packet)};
    }
};

#pragma pack(pop)

} // namespace remote_id
```
:::

---

### Критичні пастки інтеграції та налагодження

1. **Спотворення порядку байтів (Endianness Issues):** Стандарти ASTM F3411 та Bluetooth LE вимагають суворого порядку байтів `little-endian` для всіх багатобайтних числових полів (`int32_t latitude`, `uint16_t altitude`, `UUID 0xFFFA`). При розробці на мікроконтролерах із прямою адресацією пам'яті (ARM Cortex-M, Xtensa, RISC-V) порядок збігається з нативним, проте при роботі з мережевими протоколами (де стандартом є big-endian) потрібна явна перевірка байтового порядку.
2. **Псевдовипадковий джиттер інтервалу мовлення (Advertising Jitter):** Якщо кілька дронів одночасно вмикають передавачі з фіксованим таймером 1000 мс, їхні радіопакети почнуть системно накладатися в ефірі, взаємно знищуючи прийом на наземних станціях. Специфікація Bluetooth вимагає апаратного або програмного додавання випадкового зсуву від 0 до 10 мс до кожного періоду реклами (Advertising Event).
3. **Хвилястість геоїда WGS84 проти висоти над рівнем моря (MSL):** Багато недорогих супутникових модулів повертають висоту `MSL` (Mean Sea Level), розраховану за спрощеною гравітаційною моделлю Землі EGM96. Стандарт Remote ID прямо вимагає передачі еліпсоїдальної геодезичної висоти `Height Above Ellipsoid (HAE)`. Розробник зобов'язаний налаштувати GNSS-модуль на видачу HAE (наприклад, через прапорець `UBX-CFG-NAV5` або парсинг висоти геоїда в реченні NMEA `$GPGGA`).
4. **Валідація приймачами OpenDroneID:** Для верифікації роботи передавача рекомендується використовувати еталонні додатки з відкритим вихідним кодом: *OpenDroneID OSM* (Android) або *Drone Scanner* (iOS/Android). Якщо додаток фіксує пакет, але не відображає маркер на карті, найчастішою причиною є некоректне заповнення бітів точності `NACp/GVA` (значення `0` сприймається програмою як невалідний сигнал і відкидається).
5. **Лабораторний аналіз спектральним сканером:** Для перевірки відповідності спектральної маски та структури пакетів використовують SDR-приймачі або апаратні аналізатори протоколів Bluetooth (наприклад, Nordic nRF Sniffer на базі nRF52840 Dongle із плагіном Wireshark для OpenDroneID). Захоплення на каналах 37, 38, 39 дозволяє перевірити точність часових інтервалів (1000 мс ± 10 мс), відсутність втрат пакетів та коректність UUID `0xFFFA`.

# ⚙️ Парсер та емулятор пакетів BLE-маячків мовами C та C++

Для обробки широкомовних радіопакетів маячків на шлюзах Інтернету речей (IoT), вбудованих контролерах або серверах позиціонування потрібен швидкий синтаксичний аналізатор з нульовим копіюванням пам'яті (zero-copy), що розпізнає формати iBeacon, Eddystone та AltBeacon, декодує специфічні поля (токени URL, фіксовану кому температури) та розраховує дистанцію з фільтрацією шуму.

Нижче наведено детальний опис архітектури, структур даних та повну закінчену програмну реалізацію парсера рекламних пакетів та одновимірного фільтра Калмана двома мовами програмування: процедурному C з явним пакуванням структур та ідіоматичному сучасному C++20 із застосуванням `std::span`, `std::string_view` та типізованих об'єднань.

---

### 1. Архітектурні вимоги та модель обробки без копіювання (Zero-Copy)

При проектуванні вбудованих систем збору телеметрії та шлюзів позиціонування обчислювальний модуль щосекунди отримує від контролера Bluetooth через інтерфейс HCI сотні рекламних пакетів. Застосування динамічного виділення пам'яті (`malloc` / `new`) у циклі обробки таких повідомлень неприпустиме: виділення дрібних блоків спричиняє фрагментацію купи мікроконтролера, призводить до недетермінованих затримок і може спричинити вичерпання пам'яті (OOM).

З цієї причини парсер будується за моделлю **нульового копіювання пам'яті (Zero-Copy)**. Вхідний буфер сирих байтів рекламного кадру (довжиною до 31 байта) передається за вказівником або безпечним представленням `std::span`. Функція аналізатора послідовно ітерується за заголовками внутрішніх структур `AD Structure`, перевіряє межі буфера та інтерпретує корисні поля шляхом приведення типів до двійково упакованих структур або копіювання компактних скалярних значень безпосередньо в результуючий стек.

```
                  Вхідний сирий буфер Advertising Data (31 байт)
  ┌──────────┬──────────┬──────────┬───────────────────────────────────────────┐
  │ Len (1B) │ Type(1B) │ Flags(1B)│ Len (1B) │ Type(1B) │ Дані формату (26B)  │
  └──────────┴──────────┴──────────┴──────────┴──────────┴─────────────────────┘
        │          │                     │          │               │
        ▼          ▼                     ▼          ▼               ▼
   Зсув 0x00   Зсув 0x01             Зсув 0x03  Зсув 0x04       Зсув 0x05
   [Валідація прапорців]             [Вибір парсера: 0xFF чи 0x16]  [iBeacon / Eddystone]
```

#### Захист від пошкоджених пакетів та перевірка меж буфера
Кожна ітерація розбору перевіряє умову `offset + 1 + ad_len <= buf_len`. Якщо передавач надіслав пакет із пошкодженим полем довжини (наприклад, значення `0xFF` у буфері розміром 10 байтів), парсер негайно перериває обробку без виходу за межі виділеної пам'яті (Buffer Overflow). Аналогічно обробляється нульова довжина `ad_len == 0`, яка сигналізує про завершення корисних даних і наявність нульового заповнення (padding) до кінця 31-байтного буфера.

---

### 2. Керування вирівнюванням пам'яті та порядок байтів (Endianness)

У радіопротоколі Bluetooth Low Energy порядок розташування байтів має змішаний характер, зумовлений історичною еволюцією специфікації:

1. **Little Endian (прямий порядок байтів за стандартом BLE):**
   * Ідентифікатор компанії-виробника `Company ID` (наприклад, `0x004C` для Apple Inc. або `0x0118` для Radius Networks) передається молодшим байтом уперед: `0x4C, 0x00`.
   * 16-бітний ідентифікатор сервісу `Service UUID` (наприклад, `0xFEAA` для Google Eddystone) передається як `0xAA, 0xFE`.

2. **Big Endian (мережевий порядок байтів):**
   * Поля прикладного рівня, такі як `Major ID` та `Minor ID` в iBeacon, лічильники пакетів `ADV Count`, час роботи `Uptime` та напруга живлення `Battery Voltage` в Eddystone-TLM, передаються старшим байтом уперед.

Щоб уникнути помилок доступу до невідвирівняних адрес пам'яті (що призводить до апаратного винятку `HardFault` на ядрах ARM Cortex-M0/M0+), синтаксичний аналізатор не виконує пряме розіменування вказівників типу `uint16_t*` на довільні адреси буфера. Натомість використовуються безпечні побайтові функції зчитування `read_be16()` та `read_be32()`, які гарантують коректну роботу на процесорах із будь-якою апаратною архітектурою.

Для компактного представлення заголовків у мові C використовується директива компілятора `#pragma pack(push, 1)`, яка відключає автоматичне вирівнювання полів структури по 4-байтних межах і забезпечує взаємне розташування байтів один в один із форматом радіоканалу.

---

### 3. Декодування стиснених URL-адрес та чисел із фіксованою комою

#### Алгоритм розгортання Eddystone-URL
Оскільки корисне поле кадру Eddystone-URL обмежене 17 байтами, стандарт замінює типові текстові послідовності однобайтними токенами. Алгоритм розпакування працює в два етапи:
1. **Префікс протоколу:** перший байт даних після типу кадру розпізнається через таблицю підстановки: `0x00` перетворюється на `http://www.`, `0x01` — на `https://www.`, `0x02` — на `http://`, `0x03` — на `https://`.
2. **Тіло адреси та суфікси:** наступні байти аналізуються по черзі. Якщо значення байта потрапляє в діапазон `0x00..0x0D`, з таблиці розширень підставляється відповідне закінчення (`.com/`, `.org/`, `.net/` тощо). Якщо байт є друкованим символом ASCII (код `32..126`), він додається до вихідного рядка як звичайний символ.

#### Арифметика фіксованої коми 8.8 (Fixed-Point Temperature)
У кадрі Eddystone-TLM температура вимірювального кристала кодується як 16-бітне знакове число у форматі з фіксованою комою 8.8:
* Старший байт (`raw[0]`, біти 15..8) є знаковим цілим числом градусів Цельсія (`int8_t`);
* Молодший байт (`raw[1]`, біти 7..0) є дрібною частиною з дискретністю `1 / 256 ≈ 0.00390625 °C`.

Перетворення у значення з плаваючою комою виконується без втрати точності:

:::tabs
```c
float temp_c = (float)((int16_t)((raw[0] << 8) | raw[1])) / 256.0f;
```
```cpp
float temp_c = static_cast<float>(static_cast<int16_t>((raw[0] << 8) | raw[1])) / 256.0f;
```
:::

---

### 4. Одновимірний фільтр Калмана для стабілізації оцінки відстані

Радіосигнал маячка в закритому приміщенні зазнає значних випадкових флуктуацій через багатопроменеве поширення радіохвиль та завади від мереж Wi-Fi. Прямий розрахунок фізичної відстані за сирим рівнем RSSI викликає неприпустимі стрибки розрахункових координат (до 5–10 метрів при зміні сигналу лише на кілька децибелів).

Для придушення високочастотного шуму радіотракту в парсер інтегровано одновимірний фільтр Калмана, що динамічно згладжує вхідний потік вимірювань:

1. **Етап прогнозу (Time Update):**
   * Апріорна оцінка сигналу дорівнює значенню на попередньому кроці: `x̂⁻[k] = x̂[k-1]`.
   * Апріорна дисперсія помилки збільшується на величину шуму динаміки процесу: `P⁻[k] = P[k-1] + Q`.

2. **Етап корекції (Measurement Update):**
   * Обчислюється оптимальний коефіцієнт підсилення Калмана: `K[k] = P⁻[k] / (P⁻[k] + R)`.
   * Апостеріорна оцінка оновлюється з урахуванням нев'язки між вимірюванням `z[k]` та прогнозом: `x̂[k] = x̂⁻[k] + K[k] · (z[k] - x̂⁻[k])`.
   * Апостеріорна дисперсія зменшується: `P[k] = (1 - K[k]) · P⁻[k]`.

Параметр `Q` (коваріація шуму процесу, рекомендоване значення `0.01..0.1`) визначає швидкість адаптації фільтра до реального переміщення маячка в просторі. Параметр `R` (коваріація шуму вимірювача, рекомендоване значення `2.0..6.0`) задає ступінь згладжування випадкових стрибків сигналу.

---

### 5. Повна програмна реалізація мовами C та C++

Нижче наведено завершений синтаксичний аналізатор маячків, систему оцінки відстані за моделлю Log-Distance Path Loss та одновимірний фільтр Калмана у двох взаємозамінних варіантах.

:::tabs
```c
/* beacon_parser.h / beacon_parser.c — Стандарт C99/C11 */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#pragma pack(push, 1)

/* Структура AD-блоку загального призначення */
typedef struct {
    uint8_t length;
    uint8_t type;
    uint8_t data[29];
} ble_ad_element_t;

/* Двійковий кадр iBeacon (Apple) */
typedef struct {
    uint8_t  len;              /* 0x1A */
    uint8_t  type;             /* 0xFF */
    uint16_t company_id;       /* 0x004C (Little Endian) */
    uint8_t  beacon_type;      /* 0x02 */
    uint8_t  subtype_len;      /* 0x15 */
    uint8_t  uuid[16];         /* Proximity UUID (Big Endian) */
    uint16_t major;            /* Major (Big Endian) */
    uint16_t minor;            /* Minor (Big Endian) */
    int8_t   measured_power;   /* TxPower @ 1m */
} ibeacon_frame_t;

/* Двійковий кадр Eddystone-UID */
typedef struct {
    uint8_t  frame_type;       /* 0x00 */
    int8_t   tx_power_0m;      /* TxPower @ 0m */
    uint8_t  namespace_id[10];
    uint8_t  instance_id[6];
    uint16_t reserved;         /* 0x0000 */
} eddystone_uid_t;

/* Двійковий кадр Eddystone-TLM (незашифрований) */
typedef struct {
    uint8_t  frame_type;       /* 0x20 */
    uint8_t  version;          /* 0x00 */
    uint16_t vbatt_mv;         /* Напруга батареї (Big Endian) */
    int16_t  temp_fixed;       /* 8.8 fixed-point (Big Endian) */
    uint32_t adv_cnt;          /* Кількість пакетів (Big Endian) */
    uint32_t uptime_ticks;     /* Тики по 0.1 с (Big Endian) */
} eddystone_tlm_t;

/* Двійковий кадр AltBeacon */
typedef struct {
    uint8_t  len;              /* 0x1B */
    uint8_t  type;             /* 0xFF */
    uint16_t manufacturer_id;  /* Little Endian */
    uint16_t beacon_code;      /* 0xBEAC (Big Endian) */
    uint8_t  beacon_id[20];
    int8_t   ref_rssi;         /* Ref RSSI @ 1m */
    uint8_t  mfg_reserved;
} altbeacon_frame_t;

#pragma pack(pop)

/* Типи розпізнаних маячків */
typedef enum {
    BEACON_TYPE_UNKNOWN = 0,
    BEACON_TYPE_IBEACON,
    BEACON_TYPE_EDDYSTONE_UID,
    BEACON_TYPE_EDDYSTONE_URL,
    BEACON_TYPE_EDDYSTONE_TLM,
    BEACON_TYPE_ALTBEACON
} beacon_type_t;

/* Розпарсені дані маячка */
typedef struct {
    beacon_type_t type;
    int8_t   calibrated_power_1m; /* Зведений рівень до 1 метра */
    union {
        struct {
            uint8_t  uuid[16];
            uint16_t major;
            uint16_t minor;
        } ibeacon;
        struct {
            uint8_t namespace_id[10];
            uint8_t instance_id[6];
        } eddystone_uid;
        struct {
            char url[128];
        } eddystone_url;
        struct {
            uint16_t battery_mv;
            float    temperature_c;
            uint32_t adv_count;
            uint32_t uptime_sec;
        } eddystone_tlm;
        struct {
            uint16_t manufacturer_id;
            uint8_t  beacon_id[20];
        } altbeacon;
    } data;
} parsed_beacon_t;

/* 1D Фільтр Калмана */
typedef struct {
    float x; /* Оцінка стану RSSI */
    float p; /* Дисперсія оцінки */
    float q; /* Коваріація шуму процесу */
    float r; /* Коваріація шуму вимірювача */
    bool  initialized;
} kalman_filter_t;

void kalman_init(kalman_filter_t *kf, float q, float r) {
    kf->x = 0.0f;
    kf->p = 5.0f;
    kf->q = q;
    kf->r = r;
    kf->initialized = false;
}

float kalman_update(kalman_filter_t *kf, float measurement) {
    if (!kf->initialized) {
        kf->x = measurement;
        kf->p = 5.0f;
        kf->initialized = true;
        return kf->x;
    }
    /* Прогноз */
    float p_pred = kf->p + kf->q;
    /* Оновлення */
    float k = p_pred / (p_pred + kf->r);
    kf->x = kf->x + k * (measurement - kf->x);
    kf->p = (1.0f - k) * p_pred;
    return kf->x;
}

/* Розрахунок відстані за моделлю Log-Distance Path Loss */
float calculate_distance(int8_t tx_power_1m, float rssi, float path_loss_exponent) {
    if (path_loss_exponent <= 0.0f) path_loss_exponent = 2.0f;
    float exponent = ((float)tx_power_1m - rssi) / (10.0f * path_loss_exponent);
    return powf(10.0f, exponent);
}

/* Безпечне зчитування Big-Endian 16-bit */
static inline uint16_t read_be16(const uint8_t *p) {
    return (uint16_t)((p[0] << 8) | p[1]);
}

/* Безпечне зчитування Big-Endian 32-bit */
static inline uint32_t read_be32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  | (uint32_t)p[3];
}

/* Декодування Eddystone-URL токенів */
static void decode_eddystone_url(const uint8_t *payload, uint8_t len, char *out, size_t out_max) {
    if (len < 1) return;
    out[0] = '\0';

    static const char *prefixes[] = {
        "http://www.", "https://www.", "http://", "https://"
    };
    uint8_t scheme = payload[0];
    if (scheme < 4) {
        snprintf(out, out_max, "%s", prefixes[scheme]);
    }

    static const char *suffixes[] = {
        ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
        ".com",  ".org",  ".edu",  ".net",  ".info",  ".biz",  ".gov"
    };

    size_t cur_len = strlen(out);
    for (uint8_t i = 1; i < len; ++i) {
        uint8_t b = payload[i];
        if (b <= 0x0D) {
            strncat(out, suffixes[b], out_max - cur_len - 1);
            cur_len = strlen(out);
        } else if (b >= 32 && b <= 126) {
            if (cur_len + 1 < out_max) {
                out[cur_len++] = (char)b;
                out[cur_len] = '\0';
            }
        }
    }
}

/* Парсер буфера рекламних даних (31 байт) */
bool parse_ble_advertisement(const uint8_t *buf, size_t buf_len, parsed_beacon_t *out) {
    if (!buf || buf_len == 0 || !out) return false;
    memset(out, 0, sizeof(*out));

    size_t offset = 0;
    while (offset < buf_len) {
        uint8_t ad_len = buf[offset];
        if (ad_len == 0 || offset + 1 + ad_len > buf_len) break;

        uint8_t ad_type = buf[offset + 1];
        const uint8_t *ad_data = &buf[offset + 2];
        uint8_t data_len = ad_len - 1;

        /* Перевірка на Manufacturer Specific Data (0xFF) */
        if (ad_type == 0xFF && data_len >= 25) {
            uint16_t company = (uint16_t)(ad_data[0] | (ad_data[1] << 8));
            
            /* Apple iBeacon: Company ID = 0x004C, Type = 0x02, Subtype Len = 0x15 */
            if (company == 0x004C && ad_data[2] == 0x02 && ad_data[3] == 0x15) {
                const ibeacon_frame_t *ib = (const ibeacon_frame_t *)&buf[offset];
                out->type = BEACON_TYPE_IBEACON;
                memcpy(out->data.ibeacon.uuid, ib->uuid, 16);
                out->data.ibeacon.major = read_be16((const uint8_t *)&ib->major);
                out->data.ibeacon.minor = read_be16((const uint8_t *)&ib->minor);
                out->calibrated_power_1m = ib->measured_power;
                return true;
            }

            /* AltBeacon: Beacon Code = 0xBEAC */
            if (data_len >= 26 && ad_data[2] == 0xBE && ad_data[3] == 0xAC) {
                const altbeacon_frame_t *ab = (const altbeacon_frame_t *)&buf[offset];
                out->type = BEACON_TYPE_ALTBEACON;
                out->data.altbeacon.manufacturer_id = company;
                memcpy(out->data.altbeacon.beacon_id, ab->beacon_id, 20);
                out->calibrated_power_1m = ab->ref_rssi;
                return true;
            }
        }

        /* Перевірка на Service Data (0x16) для Google Eddystone (0xFEAA) */
        if (ad_type == 0x16 && data_len >= 3) {
            uint16_t service_uuid = (uint16_t)(ad_data[0] | (ad_data[1] << 8));
            if (service_uuid == 0xFEAA) {
                uint8_t frame_type = ad_data[2];
                if (frame_type == 0x00 && data_len >= 18) { /* UID */
                    const eddystone_uid_t *uid = (const eddystone_uid_t *)&ad_data[2];
                    out->type = BEACON_TYPE_EDDYSTONE_UID;
                    out->calibrated_power_1m = (int8_t)(uid->tx_power_0m - 41);
                    memcpy(out->data.eddystone_uid.namespace_id, uid->namespace_id, 10);
                    memcpy(out->data.eddystone_uid.instance_id, uid->instance_id, 6);
                    return true;
                } else if (frame_type == 0x10 && data_len >= 4) { /* URL */
                    out->type = BEACON_TYPE_EDDYSTONE_URL;
                    out->calibrated_power_1m = (int8_t)((int8_t)ad_data[3] - 41);
                    decode_eddystone_url(&ad_data[4], data_len - 4, out->data.eddystone_url.url, sizeof(out->data.eddystone_url.url));
                    return true;
                } else if (frame_type == 0x20 && data_len >= 14) { /* TLM */
                    const eddystone_tlm_t *tlm = (const eddystone_tlm_t *)&ad_data[2];
                    out->type = BEACON_TYPE_EDDYSTONE_TLM;
                    out->calibrated_power_1m = -59;
                    out->data.eddystone_tlm.battery_mv = read_be16((const uint8_t *)&tlm->vbatt_mv);
                    out->data.eddystone_tlm.temperature_c = (float)((int16_t)read_be16((const uint8_t *)&tlm->temp_fixed)) / 256.0f;
                    out->data.eddystone_tlm.adv_count = read_be32((const uint8_t *)&tlm->adv_cnt);
                    out->data.eddystone_tlm.uptime_sec = read_be32((const uint8_t *)&tlm->uptime_ticks) / 10;
                    return true;
                }
            }
        }

        offset += 1 + ad_len;
    }

    return false;
}

int main(void) {
    /* Тестовий пакет Apple iBeacon у сирому форматі BLE Advertising */
    const uint8_t raw_ibeacon[] = {
        0x02, 0x01, 0x06,                               /* Flags */
        0x1A, 0xFF, 0x4C, 0x00, 0x02, 0x15,             /* Header: Apple (0x004C), iBeacon */
        0xE2, 0xC5, 0x6D, 0xB5, 0xDF, 0xFB, 0x48, 0xD2, /* Proximity UUID (16B) */
        0xB0, 0x60, 0xD0, 0xF5, 0xA7, 0x10, 0x96, 0xE0,
        0x00, 0x0A,                                     /* Major = 10 */
        0x00, 0x02,                                     /* Minor = 2 */
        0xC5                                            /* TxPower @ 1m = -59 dBm */
    };

    parsed_beacon_t beacon;
    if (parse_ble_advertisement(raw_ibeacon, sizeof(raw_ibeacon), &beacon)) {
        printf("Знайдено iBeacon!\n");
        printf("Major: %u, Minor: %u, Calibrated TxPower@1m: %d dBm\n",
               beacon.data.ibeacon.major, beacon.data.ibeacon.minor, beacon.calibrated_power_1m);
    }

    /* Симуляція потоку зашумлених вимірювань RSSI та робота фільтра Калмана */
    kalman_filter_t kf;
    kalman_init(&kf, 0.05f, 4.0f);

    float raw_rssi_series[] = {-68.0f, -72.0f, -69.0f, -85.0f, -70.0f, -71.0f};
    printf("\nФільтрація шумів RSSI та оцінка відстані (n = 2.0):\n");
    for (size_t i = 0; i < sizeof(raw_rssi_series)/sizeof(raw_rssi_series[0]); ++i) {
        float raw = raw_rssi_series[i];
        float filtered = kalman_update(&kf, raw);
        float dist_raw = calculate_distance(beacon.calibrated_power_1m, raw, 2.0f);
        float dist_filtered = calculate_distance(beacon.calibrated_power_1m, filtered, 2.0f);
        printf("[%zu] Сирий: %5.1f dBm (d=%5.2f м) -> Калман: %5.1f dBm (d=%5.2f м)\n",
               i + 1, raw, dist_raw, filtered, dist_filtered);
    }

    return 0;
}
```
```cpp
// beacon_parser.hpp / main.cpp — Стандарт C++20
#include <iostream>
#include <iomanip>
#include <vector>
#include <span>
#include <string_view>
#include <string>
#include <array>
#include <variant>
#include <optional>
#include <cmath>
#include <cstdint>
#include <bit>

namespace ble {

struct IBeaconData {
    std::array<uint8_t, 16> uuid;
    uint16_t major;
    uint16_t minor;
};

struct EddystoneUidData {
    std::array<uint8_t, 10> namespace_id;
    std::array<uint8_t, 6>  instance_id;
};

struct EddystoneUrlData {
    std::string url;
};

struct EddystoneTlmData {
    uint16_t battery_mv;
    float    temperature_c;
    uint32_t adv_count;
    uint32_t uptime_sec;
};

struct AltBeaconData {
    uint16_t manufacturer_id;
    std::array<uint8_t, 20> beacon_id;
};

using BeaconPayload = std::variant<
    std::monostate,
    IBeaconData,
    EddystoneUidData,
    EddystoneUrlData,
    EddystoneTlmData,
    AltBeaconData
>;

struct BeaconFrame {
    int8_t calibrated_power_1m{ -59 };
    BeaconPayload payload{};

    [[nodiscard]] bool isValid() const noexcept {
        return !std::holds_alternative<std::monostate>(payload);
    }
};

class KalmanRssiFilter {
public:
    constexpr explicit KalmanRssiFilter(float process_noise = 0.05f, float measurement_noise = 4.0f) noexcept
        : q_{ process_noise }, r_{ measurement_noise } {}

    [[nodiscard]] float update(float measurement) noexcept {
        if (!initialized_) {
            x_ = measurement;
            p_ = 5.0f;
            initialized_ = true;
            return x_;
        }
        // Прогноз
        const float p_pred = p_ + q_;
        // Оновлення
        const float k = p_pred / (p_pred + r_);
        x_ += k * (measurement - x_);
        p_ = (1.0f - k) * p_pred;
        return x_;
    }

    [[nodiscard]] float state() const noexcept { return x_; }
    [[nodiscard]] bool isInitialized() const noexcept { return initialized_; }

private:
    float x_{ 0.0f };
    float p_{ 5.0f };
    float q_{ 0.05f };
    float r_{ 4.0f };
    bool  initialized_{ false };
};

[[nodiscard]] inline float calculateDistance(int8_t tx_power_1m, float rssi, float n = 2.0f) noexcept {
    if (n <= 0.0f) n = 2.0f;
    return std::pow(10.0f, (static_cast<float>(tx_power_1m) - rssi) / (10.0f * n));
}

namespace detail {
    [[nodiscard]] inline uint16_t readBe16(std::span<const uint8_t, 2> s) noexcept {
        return static_cast<uint16_t>((s[0] << 8) | s[1]);
    }

    [[nodiscard]] inline uint32_t readBe32(std::span<const uint8_t, 4> s) noexcept {
        return (static_cast<uint32_t>(s[0]) << 24) |
               (static_cast<uint32_t>(s[1]) << 16) |
               (static_cast<uint32_t>(s[2]) << 8)  |
                static_cast<uint32_t>(s[3]);
    }

    inline std::string decodeEddystoneUrl(std::span<const uint8_t> payload) {
        if (payload.empty()) return {};

        static constexpr std::string_view prefixes[] = {
            "http://www.", "https://www.", "http://", "https://"
        };
        static constexpr std::string_view suffixes[] = {
            ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",
            ".com",  ".org",  ".edu",  ".net",  ".info",  ".biz",  ".gov"
        };

        std::string result;
        const uint8_t scheme = payload[0];
        if (scheme < std::size(prefixes)) {
            result += prefixes[scheme];
        }

        for (size_t i = 1; i < payload.size(); ++i) {
            const uint8_t b = payload[i];
            if (b < std::size(suffixes)) {
                result += suffixes[b];
            } else if (b >= 32 && b <= 126) {
                result.push_back(static_cast<char>(b));
            }
        }
        return result;
    }
} // namespace detail

class BeaconParser {
public:
    [[nodiscard]] static std::optional<BeaconFrame> parse(std::span<const uint8_t> packet) {
        size_t offset = 0;
        while (offset < packet.size()) {
            const uint8_t ad_len = packet[offset];
            if (ad_len == 0 || offset + 1 + ad_len > packet.size()) break;

            const uint8_t ad_type = packet[offset + 1];
            const auto ad_data = packet.subspan(offset + 2, ad_len - 1);

            // Manufacturer Specific Data (0xFF)
            if (ad_type == 0xFF && ad_data.size() >= 25) {
                const uint16_t company = static_cast<uint16_t>(ad_data[0] | (ad_data[1] << 8));

                // Apple iBeacon (Company = 0x004C, Type = 0x02, Subtype Len = 0x15)
                if (company == 0x004C && ad_data[2] == 0x02 && ad_data[3] == 0x15 && ad_data.size() >= 25) {
                    BeaconFrame frame{};
                    IBeaconData ib{};
                    std::copy_n(ad_data.subspan(4, 16).begin(), 16, ib.uuid.begin());
                    ib.major = detail::readBe16(ad_data.subspan<20, 2>());
                    ib.minor = detail::readBe16(ad_data.subspan<22, 2>());
                    frame.calibrated_power_1m = static_cast<int8_t>(ad_data[24]);
                    frame.payload = ib;
                    return frame;
                }

                // AltBeacon (Beacon Code = 0xBEAC)
                if (ad_data.size() >= 26 && ad_data[2] == 0xBE && ad_data[3] == 0xAC) {
                    BeaconFrame frame{};
                    AltBeaconData ab{};
                    ab.manufacturer_id = company;
                    std::copy_n(ad_data.subspan(4, 20).begin(), 20, ab.beacon_id.begin());
                    frame.calibrated_power_1m = static_cast<int8_t>(ad_data[24]);
                    frame.payload = ab;
                    return frame;
                }
            }

            // Service Data (0x16) для Google Eddystone (0xFEAA)
            if (ad_type == 0x16 && ad_data.size() >= 3) {
                const uint16_t uuid = static_cast<uint16_t>(ad_data[0] | (ad_data[1] << 8));
                if (uuid == 0xFEAA) {
                    const uint8_t frame_type = ad_data[2];
                    if (frame_type == 0x00 && ad_data.size() >= 18) { // UID
                        BeaconFrame frame{};
                        EddystoneUidData uid{};
                        frame.calibrated_power_1m = static_cast<int8_t>(static_cast<int8_t>(ad_data[3]) - 41);
                        std::copy_n(ad_data.subspan(4, 10).begin(), 10, uid.namespace_id.begin());
                        std::copy_n(ad_data.subspan(14, 6).begin(), 6, uid.instance_id.begin());
                        frame.payload = uid;
                        return frame;
                    }
                    if (frame_type == 0x10 && ad_data.size() >= 4) { // URL
                        BeaconFrame frame{};
                        frame.calibrated_power_1m = static_cast<int8_t>(static_cast<int8_t>(ad_data[3]) - 41);
                        frame.payload = EddystoneUrlData{ detail::decodeEddystoneUrl(ad_data.subspan(4)) };
                        return frame;
                    }
                    if (frame_type == 0x20 && ad_data.size() >= 14) { // TLM
                        BeaconFrame frame{};
                        frame.calibrated_power_1m = -59;
                        const auto raw_temp = static_cast<int16_t>(detail::readBe16(ad_data.subspan<5, 2>()));
                        frame.payload = EddystoneTlmData{
                            .battery_mv = detail::readBe16(ad_data.subspan<3, 2>()),
                            .temperature_c = static_cast<float>(raw_temp) / 256.0f,
                            .adv_count = detail::readBe32(ad_data.subspan<7, 4>()),
                            .uptime_sec = detail::readBe32(ad_data.subspan<11, 4>()) / 10
                        };
                        return frame;
                    }
                }
            }

            offset += 1 + ad_len;
        }

        return std::nullopt;
    }
};

} // namespace ble

int main() {
    // Тестовий пакет Google Eddystone-URL
    const std::vector<uint8_t> raw_eddystone_url = {
        0x02, 0x01, 0x06,                         // Flags
        0x03, 0x03, 0xAA, 0xFE,                   // Complete 16-bit Service UUID
        0x0E, 0x16, 0xAA, 0xFE,                   // Service Data Header
        0x10, 0xEE,                               // Frame: URL, TxPower@0m = -18 dBm
        0x01,                                     // Scheme: https://www.
        'e', 'x', 'a', 'm', 'p', 'l', 'e', 0x00   // "example" + ".com/"
    };

    if (auto frame = ble::BeaconParser::parse(raw_eddystone_url)) {
        if (const auto* url_data = std::get_if<ble::EddystoneUrlData>(&frame->payload)) {
            std::cout << "Розпізнано Eddystone-URL!\n";
            std::cout << "Адреса: " << url_data->url << "\n";
            std::cout << "Опорна потужність @1m: " << static_cast<int>(frame->calibrated_power_1m) << " дБм\n";
        }
    }

    ble::KalmanRssiFilter filter(0.05f, 4.0f);
    const std::vector<float> measurements = { -68.0f, -72.0f, -69.0f, -85.0f, -70.0f, -71.0f };

    std::cout << "\nФільтрація сигналу Калманом у C++20:\n";
    for (size_t i = 0; i < measurements.size(); ++i) {
        const float raw = measurements[i];
        const float smoothed = filter.update(raw);
        const float dist_raw = ble::calculateDistance(-59, raw, 2.0f);
        const float dist_smooth = ble::calculateDistance(-59, smoothed, 2.0f);

        std::cout << "[" << i + 1 << "] Raw: " << std::setw(5) << raw << " dBm ("
                  << dist_raw << " м) -> Kalman: " << std::setw(5) << smoothed
                  << " dBm (" << dist_smooth << " м)\n";
    }

    return 0;
}
```
:::

---

### 6. Інтеграція зі стеком BlueZ через сокети Linux HCI Raw

Для практичного перехоплення пакетів маячків на одноплатних комп'ютерах (Raspberry Pi, Orange Pi) або серверах Linux парсер підключається до сокета протоколу `AF_BLUETOOTH` у режимі прямого доступу до контролера:

:::tabs
```c
int fd = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI);
struct sockaddr_hci addr = {
    .hci_family = AF_BLUETOOTH,
    .hci_dev = 0, /* hci0 */
    .hci_channel = HCI_CHANNEL_RAW
};
bind(fd, (struct sockaddr *)&addr, sizeof(addr));

/* Встановлення фільтра подій HCI_EV_LE_META */
struct hci_filter flt;
hci_filter_clear(&flt);
hci_filter_set_ptype(HCI_EVENT_PKT, &flt);
hci_filter_set_event(EVT_LE_META_EVENT, &flt);
setsockopt(fd, SOL_HCI, HCI_FILTER, &flt, sizeof(flt));
```
```cpp
int fd = ::socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI);
sockaddr_hci addr{
    .hci_family = AF_BLUETOOTH,
    .hci_dev = 0, // hci0
    .hci_channel = HCI_CHANNEL_RAW
};
::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));

// Встановлення фільтра подій HCI_EV_LE_META
hci_filter flt{};
hci_filter_clear(&flt);
hci_filter_set_ptype(HCI_EVENT_PKT, &flt);
hci_filter_set_event(EVT_LE_META_EVENT, &flt);
::setsockopt(fd, SOL_HCI, HCI_FILTER, &flt, sizeof(flt));
```
:::

Коли контролер повертає подію `EVT_LE_ADVERTISING_REPORT`, покажчик на поле `data` передається функції `parse_ble_advertisement()`, що забезпечує пряму обробку радіоефіру з мінімальними накладними витратами процесора.

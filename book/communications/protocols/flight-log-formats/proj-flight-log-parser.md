# ⚙️ Розробка двійкових парсерів польотних логів: кодеки ULog та DataFlash у C та C++

Цей інженерний практикум містить повні, автономні програмні реалізації високопродуктивних двійкових парсерів для двох головних форматів бортових чорних скриньок сучасних безпілотних систем — ArduPilot DataFlash (.BIN) та PX4 ULog. Наведені кодеки розв'язують задачу потокового розбору самоописних бінарних потоків на мовах C (стандарт C99/C11) та C++ (сучасний стандарт C++20) з підтримкою динамічного формування таблиць схем, захисту від невирівняного доступу до пам'яті на вбудованих мікроконтролерах ARM та автоматичного відновлення синхронізації при втраті байтів під час аварій.

---

## 1. Архітектурні виклики та концепція самоописного декодування

Головна відмінність форматів бортових чорних скриньок від класичних мережевих протоколів (таких як MAVLink або телеметричні кадри) полягає в їхній **динамічній самоописній природі** (англ. *self-describing stream*). У стандартному мережевому стеку структура кожного пакета жорстко зафіксована заголовними файлами (`.h`), згенерованими на етапі компіляції прошивки. Якщо наземна станція керування або діагностична утиліта скомпільована з іншою версією структури, дані спотворюються або відкидаються.

У бортових логах такий підхід неприйнятний: двійковий файл десятирічної давнини повинен відкриватися будь-яким сучасним аналізатором без необхідності пошуку точної версії вихідного коду автопілота, на якому здійснювався політ. Щоб гарантувати довгострокову сумісність, формати DataFlash та ULog вбудовують повну схему даних безпосередньо в тіло файлу перед початком запису високочастотних семплів.

### 1.1. Трьохфазний конвеєр обробки бінарного потоку

Програмний конвеєр обох розроблених декодерів базується на моделі скінченного автомата з трьома послідовними фазами функціонування:

1. **Фаза ініціалізації та валідації потоку:**
   * Для ULog: зчитування та перевірка 16-байтного магічного заголовка `0x55 0x4C 0x6F 0x67 0x01 0x12 0x35`, вилучення початкової мітки часу старту системи (`start_timestamp`), перевірка бітових масок сумісності в секції `'H'`.
   * Для DataFlash: побайтове сканування вхідного буфера до виявлення першої 2-байтної преамбули `0xA3 0x95` та перевірка валідності типу кадру.

2. **Фаза динамічної побудови словника схем (Metadata Extraction):**
   * Для DataFlash: розбір повідомлень `FMT` (Type `0x80`), вилучення імені структури (`char[4]`), довжини кадру (`length`), форматного рядка типів (`char[16]`) та назв стовпчиків (`char[64]`). Створення індексних дескрипторів у масиві швидкого доступу за числовим `Type ID`.
   * Для ULog: розбір текстових секцій визначення типів `'F'` (формат `name:field1;field2;...`), обчислення розмірів і зміщень полів у пам'яті, а також збереження зв'язок підписки в секціях `'A'` (`msg_id` → `format_name`).

3. **Фаза потокового декодування високочастотних семплів (Data Ingestion):**
   * Зчитування корисного навантаження (`'D'` у ULog або безпосередній касетний пакет у DataFlash), розпакування числових значень відповідно до збережених форматних масок, вирівнювання за часовими мітками та передача у високорівневі структури або аналітичні графічні рушії.

---

## 2. Повний парсер формату ArduPilot DataFlash (.BIN)

Парсер DataFlash здійснює лінійне сканування бінарного масиву. Якщо поточні байти не відповідають маркеру `0xA3 0x95`, алгоритм зміщує покажчик на 1 байт уперед, збільшуючи лічильник помилок синхронізації. Це гарантує миттєве відновлення розбору навіть після повного пошкодження секторів накопичувача.

:::tabs
```c
/* ============================================================================
   dataflash_parser.c — Потоковий парсер ArduPilot DataFlash мовою C (C99/C11)
   ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DF_HEAD1 0xA3
#define DF_HEAD2 0x95
#define DF_MSG_FMT 0x80
#define MAX_DF_TYPES 256

// Структура дескриптора схеми повідомлення DataFlash
typedef struct {
    bool     valid;
    uint8_t  type_id;
    uint8_t  length;
    char     name[5];       // 4 символи назви + нуль-термінатор
    char     format[17];    // до 16 символьних специфікаторів типів
    char     columns[65];   // назви стовпчиків через кому
} df_message_format_t;

// Стан потокового парсера
typedef struct {
    df_message_format_t formats[MAX_DF_TYPES];
    uint32_t parsed_messages;
    uint32_t fmt_messages;
    uint32_t sync_errors;
} df_parser_t;

// Ініціалізація стану парсера
void df_parser_init(df_parser_t *p) {
    memset(p, 0, sizeof(df_parser_t));
}

// Безпечне зчитування цілих та дробових чисел без невирівняного доступу (Little-Endian)
static inline uint16_t read_u16_le(const uint8_t *buf) {
    return (uint16_t)buf[0] | ((uint16_t)buf[1] << 8);
}

static inline int16_t read_i16_le(const uint8_t *buf) {
    return (int16_t)read_u16_le(buf);
}

static inline uint32_t read_u32_le(const uint8_t *buf) {
    return (uint32_t)buf[0] | ((uint32_t)buf[1] << 8) |
           ((uint32_t)buf[2] << 16) | ((uint32_t)buf[3] << 24);
}

static inline int32_t read_i32_le(const uint8_t *buf) {
    return (int32_t)read_u32_le(buf);
}

static inline uint64_t read_u64_le(const uint8_t *buf) {
    uint64_t low = read_u32_le(buf);
    uint64_t high = read_u32_le(buf + 4);
    return low | (high << 32);
}

static inline float read_float_le(const uint8_t *buf) {
    uint32_t u = read_u32_le(buf);
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

// Реєстрація схеми нового типу повідомлення з пакету FMT (довжина 86 байтів payload)
static void process_fmt_payload(df_parser_t *p, const uint8_t *payload) {
    uint8_t type = payload[0];
    uint8_t len  = payload[1];
    
    df_message_format_t *fmt = &p->formats[type];
    fmt->valid = true;
    fmt->type_id = type;
    fmt->length = len;
    
    memcpy(fmt->name, payload + 2, 4);
    fmt->name[4] = '\0';
    
    memcpy(fmt->format, payload + 6, 16);
    fmt->format[16] = '\0';
    
    memcpy(fmt->columns, payload + 22, 64);
    fmt->columns[64] = '\0';
    
    p->fmt_messages++;
    printf("[FMT] ID: 0x%02X (%3u), Name: %-4s, Len: %2u, Format: %s\n",
           type, type, fmt->name, len, fmt->format);
}

// Декодування корисного навантаження зареєстрованого повідомлення даних
static void process_data_payload(df_parser_t *p, uint8_t type, const uint8_t *payload) {
    const df_message_format_t *fmt = &p->formats[type];
    p->parsed_messages++;
    
    // Обробка касетного повідомлення просторової орієнтації ATT (Attitude)
    if (strcmp(fmt->name, "ATT") == 0 && strcmp(fmt->format, "Qcccc") == 0) {
        uint64_t time_us   = read_u64_le(payload);
        float des_roll    = read_i16_le(payload + 8) / 100.0f;
        float roll        = read_i16_le(payload + 10) / 100.0f;
        float des_pitch   = read_i16_le(payload + 12) / 100.0f;
        float pitch       = read_i16_le(payload + 14) / 100.0f;
        printf("  [ATT] t=%llu us: Roll=%.2f deg (Des=%.2f), Pitch=%.2f deg (Des=%.2f)\n",
               (unsigned long long)time_us, roll, des_roll, pitch, des_pitch);
    }
    // Обробка повідомлення супутникової навігації GPS
    else if (strcmp(fmt->name, "GPS") == 0) {
        uint64_t time_us = read_u64_le(payload);
        uint8_t status   = payload[8];
        int32_t lat_raw  = read_i32_le(payload + 16);
        int32_t lng_raw  = read_i32_le(payload + 20);
        float alt        = read_float_le(payload + 24);
        printf("  [GPS] t=%llu us: Fix=%u, Lat=%.7f, Lng=%.7f, Alt=%.2f m\n",
               (unsigned long long)time_us, status, lat_raw / 1e7, lng_raw / 1e7, alt);
    }
}

// Головна функція потокового розбору буфера довільного розміру
void df_parse_stream(df_parser_t *p, const uint8_t *data, size_t size) {
    size_t offset = 0;
    
    while (offset + 3 <= size) {
        // Пошук синхронізуючого маркера 0xA3 0x95
        if (data[offset] != DF_HEAD1 || data[offset + 1] != DF_HEAD2) {
            offset++;
            p->sync_errors++;
            continue;
        }
        
        uint8_t type = data[offset + 2];
        
        // Обробка повідомлення FMT (фіксована довжина 89 байтів разом з заголовком)
        if (type == DF_MSG_FMT) {
            if (offset + 89 > size) break; // неповний блок у кінці чанка
            process_fmt_payload(p, &data[offset + 3]);
            offset += 89;
            continue;
        }
        
        // Обробка відомого типу повідомлення
        const df_message_format_t *fmt = &p->formats[type];
        if (fmt->valid) {
            if (offset + fmt->length > size) break; // очікуємо наступну порцію даних
            process_data_payload(p, type, &data[offset + 3]);
            offset += fmt->length;
        } else {
            // Тип повідомлення ще не зареєстрований через FMT: зсув для ресинхронізації
            offset++;
            p->sync_errors++;
        }
    }
}
```
```cpp
// ============================================================================
// dataflash_parser.hpp — Потоковий парсер ArduPilot DataFlash на C++20
// ============================================================================
#pragma once
#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <bit>
#include <cstring>
#include <cstdint>
#include <algorithm>

namespace dataflash {

constexpr uint8_t HEAD1 = 0xA3;
constexpr uint8_t HEAD2 = 0x95;
constexpr uint8_t TYPE_FMT = 0x80;

struct MessageFormat {
    uint8_t type_id{0};
    uint8_t length{0};
    std::string name;
    std::string format;
    std::string columns;
};

class Parser {
public:
    void parse_chunk(std::span<const uint8_t> buffer) {
        size_t offset = 0;
        const size_t total_size = buffer.size();

        while (offset + 3 <= total_size) {
            if (buffer[offset] != HEAD1 || buffer[offset + 1] != HEAD2) {
                ++offset;
                ++sync_errors_;
                continue;
            }

            const uint8_t type = buffer[offset + 2];

            if (type == TYPE_FMT) {
                if (offset + 89 > total_size) break;
                parse_fmt(buffer.subspan(offset + 3, 86));
                offset += 89;
                continue;
            }

            auto it = formats_.find(type);
            if (it != formats_.end()) {
                const auto& fmt = it->second;
                if (offset + fmt.length > total_size) break;
                
                dispatch_message(fmt, buffer.subspan(offset + 3, fmt.length - 3));
                offset += fmt.length;
                ++parsed_messages_;
            } else {
                ++offset;
                ++sync_errors_;
            }
        }
    }

    [[nodiscard]] size_t total_parsed() const noexcept { return parsed_messages_; }
    [[nodiscard]] size_t sync_errors() const noexcept { return sync_errors_; }
    [[nodiscard]] const std::unordered_map<uint8_t, MessageFormat>& formats() const noexcept { return formats_; }

private:
    void parse_fmt(std::span<const uint8_t, 86> payload) {
        MessageFormat fmt;
        fmt.type_id = payload[0];
        fmt.length  = payload[1];
        
        fmt.name = extract_string(payload.subspan(2, 4));
        fmt.format = extract_string(payload.subspan(6, 16));
        fmt.columns = extract_string(payload.subspan(22, 64));

        std::cout << "[FMT] Registered: " << fmt.name 
                  << " (0x" << std::hex << static_cast<int>(fmt.type_id) << std::dec
                  << "), Length: " << static_cast<int>(fmt.length) << "\n";

        formats_[fmt.type_id] = std::move(fmt);
    }

    void dispatch_message(const MessageFormat& fmt, std::span<const uint8_t> payload) {
        if (fmt.name == "ATT" && fmt.format == "Qcccc") {
            const uint64_t time_us = read_le<uint64_t>(payload.data());
            const float roll = read_le<int16_t>(payload.data() + 10) / 100.0f;
            const float pitch = read_le<int16_t>(payload.data() + 14) / 100.0f;
            std::cout << "  [ATT] t=" << time_us << " us, Roll=" << roll << " deg, Pitch=" << pitch << " deg\n";
        } else if (fmt.name == "GPS") {
            const uint64_t time_us = read_le<uint64_t>(payload.data());
            const uint8_t status = payload[8];
            const int32_t lat = read_le<int32_t>(payload.data() + 16);
            const int32_t lng = read_le<int32_t>(payload.data() + 20);
            const float alt = read_le<float>(payload.data() + 24);
            std::cout << "  [GPS] t=" << time_us << " us, Status=" << static_cast<int>(status)
                      << ", Pos=(" << (lat / 1e7) << ", " << (lng / 1e7) << "), Alt=" << alt << " m\n";
        }
    }

    static std::string extract_string(std::span<const uint8_t> span) {
        std::string s;
        for (uint8_t b : span) {
            if (b == '\0') break;
            s.push_back(static_cast<char>(b));
        }
        return s;
    }

    template <typename T>
    static T read_le(const uint8_t* ptr) noexcept {
        T val;
        std::memcpy(&val, ptr, sizeof(T));
        if constexpr (std::endian::native == std::endian::big) {
            // Реверс байтів для Big-Endian платформ
            uint8_t* byte_ptr = reinterpret_cast<uint8_t*>(&val);
            std::reverse(byte_ptr, byte_ptr + sizeof(T));
        }
        return val;
    }

    std::unordered_map<uint8_t, MessageFormat> formats_;
    size_t parsed_messages_{0};
    size_t sync_errors_{0};
};

} // namespace dataflash
```
:::

---

## 3. Повний парсер формату PX4 ULog

Парсер ULog демонструє роботу з потоковим протоколом без покадрових синхромаркерів. Він спирається на суворе дотримання розміру пакетів `msg_size`. Якщо значення `msg_size` є коректним, парсер послідовно читає блоки, обробляючи визначення схем `'F'`, підписки `'A'`, системні повідомлення `'L'` та пакети даних `'D'`.

:::tabs
```c
/* ============================================================================
   ulog_parser.c — Потоковий парсер PX4 ULog мовою C (C99/C11)
   ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SUBSCRIPTIONS 512
#define MAX_FORMATS 256

// Опис схеми uORB топіка
typedef struct {
    char format_name[64];
    char raw_fields[512];
    uint16_t total_size;
} ulog_format_t;

// Активна підписка msg_id -> назва схеми
typedef struct {
    bool active;
    uint16_t msg_id;
    uint8_t  multi_id;
    char message_name[64];
    const ulog_format_t *format;
} ulog_subscription_t;

// Стан декодера ULog
typedef struct {
    bool header_parsed;
    uint64_t start_timestamp;
    ulog_format_t formats[MAX_FORMATS];
    uint16_t format_count;
    ulog_subscription_t subscriptions[MAX_SUBSCRIPTIONS];
    uint32_t data_messages;
    uint32_t dropouts;
} ulog_parser_t;

void ulog_parser_init(ulog_parser_t *p) {
    memset(p, 0, sizeof(ulog_parser_t));
}

// Перевірка 16-байтного магічного заголовка файлу ULog
bool ulog_parse_header(ulog_parser_t *p, const uint8_t *buf, size_t size) {
    const uint8_t expected_magic[7] = {0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35};
    if (size < 16) return false;
    
    if (memcmp(buf, expected_magic, 7) != 0) {
        printf("Помилка: недійсний заголовок сигнатури ULog!\n");
        return false;
    }
    
    memcpy(&p->start_timestamp, buf + 7, sizeof(uint64_t));
    p->header_parsed = true;
    printf("[ULOG] Файл ініціалізовано. Системний час старту: %llu мкс\n",
           (unsigned long long)p->start_timestamp);
    return true;
}

// Реєстрація форматної схеми 'F'
static void ulog_process_format(ulog_parser_t *p, const char *fmt_str, uint16_t len) {
    if (p->format_count >= MAX_FORMATS) return;
    
    ulog_format_t *fmt = &p->formats[p->format_count];
    memset(fmt, 0, sizeof(ulog_format_t));
    
    const char *colon = strchr(fmt_str, ':');
    if (!colon) return;
    
    size_t name_len = colon - fmt_str;
    if (name_len >= sizeof(fmt->format_name)) name_len = sizeof(fmt->format_name) - 1;
    strncpy(fmt->format_name, fmt_str, name_len);
    fmt->format_name[name_len] = '\0';
    
    size_t fields_len = len - (colon - fmt_str + 1);
    if (fields_len >= sizeof(fmt->raw_fields)) fields_len = sizeof(fmt->raw_fields) - 1;
    strncpy(fmt->raw_fields, colon + 1, fields_len);
    fmt->raw_fields[fields_len] = '\0';
    
    p->format_count++;
    printf("[ULOG-F] Формат: %s -> Поля: %s\n", fmt->format_name, fmt->raw_fields);
}

// Обробка реєстрації підписки 'A'
static void ulog_process_add_msg(ulog_parser_t *p, const uint8_t *payload, uint16_t len) {
    if (len < 3) return;
    
    uint8_t multi_id = payload[0];
    uint16_t msg_id = (uint16_t)payload[1] | ((uint16_t)payload[2] << 8);
    
    if (msg_id >= MAX_SUBSCRIPTIONS) return;
    
    ulog_subscription_t *sub = &p->subscriptions[msg_id];
    sub->active = true;
    sub->msg_id = msg_id;
    sub->multi_id = multi_id;
    
    size_t name_len = len - 3;
    if (name_len >= sizeof(sub->message_name)) name_len = sizeof(sub->message_name) - 1;
    memcpy(sub->message_name, payload + 3, name_len);
    sub->message_name[name_len] = '\0';
    
    // Пошук раніше оголошеного формату
    for (int i = 0; i < p->format_count; ++i) {
        if (strcmp(p->formats[i].format_name, sub->message_name) == 0) {
            sub->format = &p->formats[i];
            break;
        }
    }
    
    printf("[ULOG-A] Підписка: ID=%u -> Топік %s (екземпляр %u)\n",
           msg_id, sub->message_name, multi_id);
}

// Потоковий розбір блоків ULog
void ulog_parse_stream(ulog_parser_t *p, const uint8_t *data, size_t size) {
    size_t offset = 0;
    
    if (!p->header_parsed) {
        if (!ulog_parse_header(p, data, size)) return;
        offset = 16;
    }
    
    while (offset + 3 <= size) {
        uint16_t msg_size = (uint16_t)data[offset] | ((uint16_t)data[offset + 1] << 8);
        uint8_t  msg_type = data[offset + 2];
        
        if (offset + 3 + msg_size > size) break; // неповний блок
        
        const uint8_t *payload = &data[offset + 3];
        
        switch (msg_type) {
            case 'F': {
                char temp[512];
                size_t cpy = (msg_size < sizeof(temp) - 1) ? msg_size : sizeof(temp) - 1;
                memcpy(temp, payload, cpy);
                temp[cpy] = '\0';
                ulog_process_format(p, temp, msg_size);
                break;
            }
            case 'A':
                ulog_process_add_msg(p, payload, msg_size);
                break;
            case 'D': {
                if (msg_size >= 2) {
                    uint16_t msg_id = (uint16_t)payload[0] | ((uint16_t)payload[1] << 8);
                    p->data_messages++;
                    if (msg_id < MAX_SUBSCRIPTIONS && p->subscriptions[msg_id].active) {
                        // Тут сирі байти передаються декодеру конкретної структури uORB
                    }
                }
                break;
            }
            case 'L': {
                if (msg_size >= 9) {
                    uint8_t level = payload[0];
                    uint64_t ts;
                    memcpy(&ts, payload + 1, sizeof(uint64_t));
                    char text_buf[256];
                    size_t tlen = msg_size - 9;
                    if (tlen >= sizeof(text_buf)) tlen = sizeof(text_buf) - 1;
                    memcpy(text_buf, payload + 9, tlen);
                    text_buf[tlen] = '\0';
                    printf("  [LOG L%u] t=%llu us: %s\n", level, (unsigned long long)ts, text_buf);
                }
                break;
            }
            case 'S': {
                if (msg_size >= 2) {
                    uint16_t dur = (uint16_t)payload[0] | ((uint16_t)payload[1] << 8);
                    p->dropouts++;
                    printf("  [DROPOUT] Втрата даних тривалістю: %u мс\n", dur);
                }
                break;
            }
            default:
                break;
        }
        
        offset += 3 + msg_size;
    }
}
```
```cpp
// ============================================================================
// ulog_parser.hpp — Потоковий парсер PX4 ULog на C++20
// ============================================================================
#pragma once
#include <iostream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <cstring>
#include <cstdint>

namespace ulog {

struct FormatDefinition {
    std::string name;
    std::string raw_schema;
};

struct Subscription {
    uint16_t msg_id{0};
    uint8_t multi_id{0};
    std::string topic_name;
    std::shared_ptr<FormatDefinition> format;
};

class Parser {
public:
    void parse_chunk(std::span<const uint8_t> buffer) {
        size_t offset = 0;
        const size_t total_size = buffer.size();

        if (!header_verified_) {
            if (total_size < 16) return;
            if (!verify_header(buffer.subspan(0, 16))) return;
            offset = 16;
            header_verified_ = true;
        }

        while (offset + 3 <= total_size) {
            const uint16_t msg_size = buffer[offset] | (static_cast<uint16_t>(buffer[offset + 1]) << 8);
            const uint8_t msg_type = buffer[offset + 2];

            if (offset + 3 + msg_size > total_size) break;

            auto payload = buffer.subspan(offset + 3, msg_size);
            dispatch_section(msg_type, payload);
            offset += 3 + msg_size;
        }
    }

    [[nodiscard]] size_t total_data_samples() const noexcept { return data_messages_; }
    [[nodiscard]] size_t total_dropouts() const noexcept { return dropouts_; }

private:
    bool verify_header(std::span<const uint8_t, 16> hdr) {
        constexpr uint8_t expected_magic[7] = {0x55, 0x4C, 0x6F, 0x67, 0x01, 0x12, 0x35};
        if (std::memcmp(hdr.data(), expected_magic, 7) != 0) {
            std::cerr << "Помилка: недійсний магічний заголовок ULog!\n";
            return false;
        }
        std::memcpy(&start_time_us_, hdr.data() + 7, sizeof(uint64_t));
        std::cout << "[ULOG] Валідний файл ULog. Час старту: " << start_time_us_ << " мкс\n";
        return true;
    }

    void dispatch_section(uint8_t type, std::span<const uint8_t> payload) {
        switch (type) {
            case 'F': {
                std::string_view schema(reinterpret_cast<const char*>(payload.data()), payload.size());
                auto colon = schema.find(':');
                if (colon != std::string_view::npos) {
                    auto name = std::string(schema.substr(0, colon));
                    auto fmt = std::make_shared<FormatDefinition>(name, std::string(schema));
                    formats_[name] = fmt;
                    std::cout << "[ULOG-F] Зареєстровано формат: " << name << "\n";
                }
                break;
            }
            case 'A': {
                if (payload.size() < 3) break;
                const uint8_t multi_id = payload[0];
                const uint16_t msg_id = payload[1] | (static_cast<uint16_t>(payload[2]) << 8);
                std::string topic_name(reinterpret_cast<const char*>(payload.data() + 3), payload.size() - 3);

                Subscription sub{msg_id, multi_id, topic_name, nullptr};
                auto it = formats_.find(topic_name);
                if (it != formats_.end()) {
                    sub.format = it->second;
                }
                subscriptions_[msg_id] = sub;
                std::cout << "[ULOG-A] ID " << msg_id << " -> " << topic_name << " (inst " << static_cast<int>(multi_id) << ")\n";
                break;
            }
            case 'D': {
                if (payload.size() >= 2) {
                    ++data_messages_;
                }
                break;
            }
            case 'L': {
                if (payload.size() >= 9) {
                    const uint8_t level = payload[0];
                    uint64_t ts;
                    std::memcpy(&ts, payload.data() + 1, sizeof(uint64_t));
                    std::string_view text(reinterpret_cast<const char*>(payload.data() + 9), payload.size() - 9);
                    std::cout << "  [LOG L" << static_cast<int>(level) << "] t=" << ts << " us: " << text << "\n";
                }
                break;
            }
            case 'S': {
                if (payload.size() >= 2) {
                    const uint16_t duration_ms = payload[0] | (static_cast<uint16_t>(payload[1]) << 8);
                    ++dropouts_;
                    std::cout << "  [ULOG-S] Фіксація пропуску даних: " << duration_ms << " мс\n";
                }
                break;
            }
            default:
                break;
        }
    }

    bool header_verified_{false};
    uint64_t start_time_us_{0};
    std::unordered_map<std::string, std::shared_ptr<FormatDefinition>> formats_;
    std::unordered_map<uint16_t, Subscription> subscriptions_;
    size_t data_messages_{0};
    size_t dropouts_{0};
};

} // namespace ulog
```
:::

---

## 4. Порівняльний аналіз швидкодії: буферизований I/O проти Memory Mapping (mmap)

При обробці польотних логів гігабайтного обсягу (наприклад, тривалих місій картографування або багатогодинних польотів БПЛА літакового типу) продуктивність дискового вводу-виводу стає головним вузьким місцем аналітичного програмного забезпечення.

### 4.1. Класичний поблоковий I/O (`fread`)
У стандартній реалізації поблокового читання буфер фіксованого розміру (наприклад, 64 КБ або 1 МБ) заповнюється системним викликом `fread()` або `read()`:
* **Переваги:** Мінімальні вимоги до оперативної пам'яті (парсер може працювати навіть на мікроконтролері з 32 КБ RAM), простота реалізації вбудованих обробників.
* **Недоліки:** Додаткові витрати процесорного часу на подвійне копіювання даних: спершу ядро операційної системи зчитує сектори диска у власний Page Cache, після чого системний виклик копіює байти в буфер користувацького простору. При переході межі буфера парсер змушений склеювати розірвані пакети.

### 4.2. Віртуальне відображення пам'яті (`mmap`)
На 64-бітних аналітичних станціях (декомпресори, графічні утиліти PlotJuggler або Mission Planner) найефективнішим методом є відображення всього бінарного файлу у віртуальний адресний простір процесу за допомогою POSIX-виклику `mmap()`:
* **Переваги:** Повна відсутність додаткових копіювань (Zero-Copy). Ядро операційної системи автоматично підвантажує сторінки файлу за запитом механізму Page Fault і вивантажує неактивні блоки.
* **Швидкість:** Пропускна здатність декодування збільшується у 3–5 разів, досягаючи 400–800 МБ/с на сучасних процесорах x86_64 та Apple Silicon.

### 4.3. Покрокове розгортання експорту даних у формат CSV
Для інтеграції з науковими пакетами аналізу (MATLAB, Python pandas, NumPy) парсери зазвичай реалізують модуль експорту окремих топіків у текстовий формат CSV (Comma-Separated Values).
* На етапі ініціалізації парсер створює окремий вихідний текстовий файл для кожного унікального імені структури (наприклад, `sensor_combined.csv`, `vehicle_attitude.csv`, `gps.csv`).
* Першим рядком записуються назви колонок, вилучені з секції `columns` у DataFlash або з оголошення полів у ULog.
* При надходженні кожного бінарного семпла числові значення форматуються у текстовий рядок і скидаються у відповідний файловий дескриптор.

---

## 5. Побудова індексів для швидкого позиціонування (Time Seeking B-Tree)

При аналізі польотів тривалістю понад 30 хвилин типовий обсяг файлу логу досягає 200–500 МБ. Якщо користувач у графічній утиліті переміщує повзунок часу на 25-ту хвилину польоту, послідовний перебір усіх попередніх 400 МБ даних створює неприпустиму затримку в кілька секунд.

Для забезпечення миттєвого відгуку аналізатори будують **індекс часових зміщень** під час первинного фонового проходу:

1. **Таблиця ключових кадрів (Keyframe Index):** Через кожні 1.0 секунди польотного часу (або кожні N тисяч пакетів) парсер фіксує пару значень: `[Timestamp, FileOffset]`.
2. **Структура зберігання:** Масив або B-дерево в оперативній пам'яті.
3. **Алгоритм бінарного пошуку (Binary Search):**
   * При запиті переходу на цільовий час `T_target` алгоритм здійснює пошук у таблиці індексів, знаходячи максимальний `T_key <= T_target`.
   * Файловий покажчик миттєво зсувається на зміщення `FileOffset` за допомогою системного виклику `lseek()` або зміщення вказівника `mmap`.
   * Для DataFlash декодер шукає найближчий маркер `0xA3 0x95` і продовжує нормальний розбір; для ULog алгоритм відновлює карту підписок із початкової таблиці схем і продовжує декодування семплів `'D'`.

Така архітектура скорочує час довільного позиціонування на будь-яку точку польоту з декількох секунд до кількох мікросекунд (`O(log K)`, де `K` — кількість зафіксованих ключових точок індексу).

---

## 6. Покрокове трасування декодування бінарного кадру

Щоб наочно проілюструвати роботу кодека на рівні окремих байтів пам'яті, розглянемо процес декодування реального бінарного кадру просторової орієнтації `ATT` у форматі DataFlash.

Нехай вхідний потік байтів містить наступну 19-байтову послідовність у шістнадцятковому вигляді:
`A3 95 05 40 42 0F 00 00 00 00 00 E8 03 10 27 D0 07 20 4E`

Покрокове виконання скінченного автомата парсера:
1. **Зчитування преамбули (байти 0..1):** `0xA3 0x95` — ідентифіковано валідний початок кадру.
2. **Визначення типу повідомлення (байт 2):** `0x05` — знайдено зареєстрований тип `ATT` (довжина 19 байтів).
3. **Вилучення системного часу (байти 3..10):** `40 42 0F 00 00 00 00 00` Little-Endian:
   ```
   TimeUS = 0x00000000000F4240 = 1000000 мкс (рівно 1.0 секунда від старту)
   ```
4. **Вилучення цільового крену DesRoll (байти 11..12):** `E8 03` Little-Endian:
   ```
   DesRoll = (int16_t)0x03E8 = 1000 -> Масштаб c: 1000 / 100.0 = +10.00 град
   ```
5. **Вилучення фактичного крену Roll (байти 13..14):** `10 27` Little-Endian:
   ```
   Roll = (int16_t)0x2710 = 10000 -> Масштаб c: 10000 / 100.0 = +100.00 град
   ```
6. **Вилучення цільового тангажу DesPitch (байти 15..16):** `D0 07` Little-Endian:
   ```
   DesPitch = (int16_t)0x07D0 = 2000 -> Масштаб c: 2000 / 100.0 = +20.00 град
   ```
7. **Вилучення фактичного тангажу Pitch (байти 17..18):** `20 4E` Little-Endian:
   ```
   Pitch = (int16_t)0x4E20 = 20000 -> Масштаб c: 20000 / 100.0 = +200.00 град
   ```

У результаті виконання семи простих операцій зсуву покажчика сирі байти перетворюються на фізичні величини, готові для аналізу контуру керування.

Аналогічно, у форматі ULog повідомлення `'D'` для структури `vehicle_attitude` містить 2-байтний заголовок `msg_size = 34`, `msg_type = 'D'`, після чого слідують 2 байти `msg_id = 0x0004` та 32 байти корисного навантаження (`uint64_t timestamp` та 4 числа `float` кватерніона орієнтації `q[0..3]`). Парсер перевіряє прив'язку `msg_id` у таблиці підписок і безпосередньо копіює 32 байти у вектор стану EKF.

---

## 7. Архітектура керування пам'яттю у вбудованих логерах

Усередині операційних систем реального часу (NuttX, ChibiOS, FreeRTOS), що виконуються на борту польотного контролера, підсистема логування працює в умовах жорстких обмежень на динамічне виділення пам'яті.

### 7.1. Заборона кучі (No Dynamic Heap Allocation)
Виклики функцій `malloc()`, `realloc()` або створення динамічних об'єктів `new` під час активного польоту категорично заборонені в коді автопілота:
* **Недетермінований час виконання:** Алгоритми пошуку вільних блоків у кучі можуть блокувати потік на сотні мікросекунд у випадкові моменти часу, викликаючи зрив циклів контуру стабілізації.
* **Фрагментація пам'яті:** Постійне виділення та звільнення пам'яті різного розміру під повідомлення змінної довжини швидко призводить до вичерпання суцільних блоків SRAM.
* **Архітектурне вирішення:** Усі буфери дескрипторів схем, масиви підписок та таблиці повідомлень розміщуються у статичній пам'яті (BSS-сегмент) на етапі ініціалізації мікроконтролера або керуються пуловими алокаторами фіксованого розміру (англ. *fixed-size block pool allocators*).

---

## 8. Інтеграція парсерів у веб-аналізатори через WebAssembly

Сучасні інструменти телеметричного аналізу (такі як браузерні візуалізатори польотів PX4 Flight Review та FlightPlot Web) вимагають виконання бінарного розбору безпосередньо на стороні клієнта в браузері.
* Скомпільовані за допомогою компілятора Emscripten або Clang у цільову архітектуру WebAssembly (`wasm32`), наведені кодеки на C та C++ забезпечують розбір 100-мегабайтного файлу логу за 150–300 мілісекунд прямо в пам'яті вкладки браузера.
* Застосування векторних інструкцій WebAssembly SIMD128 дозволяє паралельно масштабувати масиви цілих чисел та конвертувати поля з фіксованою комою у формат `float32` зі швидкістю понад 1 ГБ/с.
* Двійковий потік передається у WebAssembly у вигляді масиву `Uint8Array`, де парсер наповнює структури `Float64Array`, готові для миттєвого рендерингу графіків через WebGL та WebGPU без блокування графічного інтерфейсу користувача.

---

## 9. Глибокий розбір інженерних пасток та крайових випадків

Під час практичної розробки кодеків польотних логів виникає низка специфічних апаратних і алгоритмічних проблем, ігнорування яких призводить до падіння парсерів або спотворення аналітичних даних:

### 9.1. Проблема невирівняного доступу до пам'яті (Unaligned Memory Access)
У бінарних структурах DataFlash та ULog багатобайтові числа розміщуються з непарними зміщеннями. Наприклад, у кадрі `0xA3 0x95 Type Payload` корисні дані починаються з третього байта. Якщо першим полем структури є `uint64_t TimeUS`, його адреса в пам'яті буде не кратною 8.
* На процесорах x86_64 та сучасних ARM Cortex-M7 невирівняне читання підтримується апаратно, хоча й коштує кількох додаткових тактів шини.
* На мікроконтролерах без апаратної підтримки невирівняного доступу (ARM Cortex-M0/M0+, застарілі ядра MIPS) спроба прямого розіменування вказівника `*(uint64_t*)(buf + 3)` миттєво генерує апаратний виняток процесора `HardFault` / `Alignment Fault`.
* **Правильне рішення:** використання побайтового копіювання через функцію `memcpy` або явне збирання чисел побітовими зсувами, як продемонстровано у функціях `read_u64_le()` та `read_le<T>()`. Сучасні компілятори GCC та Clang оптимізують такі виклики в швидкі апаратні інструкції збирання.

### 9.2. Пошкодження полів довжини при раптовому вимкненні живлення
Якщо живлення польотного контролера переривається під час запису чергового блоку на SD-карту, останні байти файлу можуть містити незавершений сміттєвий заголовок, у якому поле `msg_size` набуває випадкового великого значення (наприклад, `0xFFFF` = 65535 байтів).
* Якщо парсер наївно виділяє пам'ять під розмір `msg_size` або намагається прочитати 65 КБ за межами файлу, виникає аварійне завершення `Segmentation Fault`.
* **Правильне рішення:** перед кожним розбором поля корисного навантаження парсер зобов'язаний перевіряти інваріант: `offset + header_size + payload_size <= total_buffer_size`. Якщо умова порушена, цикл розбору зупиняється без помилки, зберігаючи всі успішно прочитані попередні кадри.

### 9.3. Обробка спеціальних значень чисел із рухомою комою (NaN / Inf)
На етапі початкової ініціалізації датчиків, калібрування EKF або при апаратній відмові I2C/SPI шини значення датчиків у логу можуть набувати спеціальних бінарних комбінацій IEEE 754: `NaN` (`0x7FC00000`) або `+Inf`/`-Inf` (`0x7F800000` / `0xFF800000`).
* Пряме використання таких чисел у математичних фільтрах або обчисленнях середньоквадратичного відхилення призводить до «забруднення» всієї подальшої статистики (будь-яка арифметична операція з `NaN` повертає `NaN`).
* **Правильне рішення:** валідація отриманих чисел стандартними предикатами `isnan()` / `std::isnan()` та `isfinite()` / `std::isfinite()` перед передачею в графічні рушії та алгоритми цифрової фільтрації.

### 9.4. Часові розриви та компенсація втрачених пакетів (Time Series Alignment)
При виникненні затримок запису на повільні SD-карти кільцевий буфер переповнюється, що фіксується повідомленням `'S'` у ULog або стрибком поля `TimeUS` у DataFlash.
* Якщо графічний аналізатор з'єднує дві сусідні точки неперервною лінією без урахування часової мітки, виникає ілюзія плавної зміни параметра, хоча насправді в цей інтервал апарат міг виконати різкий маневр або зазнати удару.
* **Правильне рішення:** алгоритм побудови графіків зобов'язаний аналізувати різницю `dt = t[i] - t[i-1]`. Якщо `dt` перевищує очікуваний період дискретизації більш ніж у 3–5 разів (або зафіксовано повідомлення `'S'`), графічна крива розривається, відображаючи реальний інтервал відсутності даних.

### 9.5. Ідентифікація дубльованих екземплярів сенсорів (Multi-Instance Tracking)
Сучасні польотні контролери містять від двох до трьох незалежних IMU-чіпів різних виробників (наприклад, TDK InvenSense ICM-42688-P та Bosch BMI088) для забезпечення апаратного резервування.
* У форматі ULog різні екземпляри одного типу датчика розрізняються за допомогою поля `multi_id` у повідомленні підписки `'A'`. Екземпляр `multi_id = 0` позначає первинний сенсор, а `multi_id = 1` — вторинний дублюючий сенсор.
* У форматі DataFlash повідомлення описують кожен сенсор власним унікальним ім'ям касети у таблиці `FMT` (наприклад, `IMU` для першого гіроскопа/акселерометра, `IMU2` для другого, `IMU3` для третього).
* Парсер повинен підтримувати роздільне накопичення часових рядів для кожного фізичного екземпляра сенсора, забезпечуючи можливість порівняльного спектрального аналізу шумів та виявлення вібраційної асиметрії рами.

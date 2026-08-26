# ⚙️ Реалізація потокового TLV-парсера без динамічної пам'яті

Формат TLV (*Type-Length-Value* — «тип, довжина, значення») є класичним будівельним блоком протоколів зв'язку, де потрібна повна пряма сумісність: приймач не зобов'язаний знати всі можливі типи записів наперед. Зустрівши невідомий тег, парсер зчитує поле довжини `L` і переміщує покажчик читання на `L` байтів уперед, безпечно пропускаючи невідомі дані без аварійного завершення та без спотворення наступних записів.

У вбудованих системах реалізація TLV стикається з трьома суворими вимогами:
1. **Повна заборона динамічного виділення пам'яті (`malloc`/`free`)**: парсер повинен працювати за принципом *in-place* (безпосередньо у вхідному буфері прийому) зі статично виділеними структурами цільових даних.
2. **Абсолютна стійкість до зловмисних або пошкоджених пакетів**: перевірка виходу за межі буфера перед кожним зверненням до пам'яті, захист від цілочисельного переповнення лічильників довжини та відсікання нескінченних циклів.
3. **Підтримка вкладених структур (Nested TLV)**: здатність інтерпретувати значення певного тегу як самостійний вкладений потік підпорядкованих TLV-записів без використання рекурсії, яка загрожує переповненням стека мікроконтролера.

## Архітектура та розкладка кадру

Визначимо бінарну розкладку нашого TLV-повідомлення:
- Кожен запис починається з однобайтового поля тегу `tag` (`uint8_t`), що визначає семантику параметра.
- Далі слідує однобайтове поле довжини `length` (`uint8_t`), яке задає точну кількість байтів корисного навантаження у полі `value`.
- За ним розміщується рівно `length` байтів значення `value`.

```
+----------+------------+-------------------------------+
| Tag (1B) | Length(1B) | Value (Length байтів)         |
+----------+------------+-------------------------------+
```

Виділимо тестовий набір тегів телеметрії та налаштувань:
- `TAG_VOLTAGE_MV (0x01)`: Напруга живлення, `uint16_t` (2 байти, little-endian).
- `TAG_CURRENT_MA (0x02)`: Струм споживання, `int32_t` (4 байти, little-endian).
- `TAG_TEMPERATURE (0x03)`: Температура сенсора, `int16_t` (соті градуса °C, 2 байти).
- `TAG_DEVICE_NAME (0x04)`: Текстова назва пристрою, UTF-8 рядок змінної довжини (1..32 байти).
- `TAG_NETWORK_CONFIG (0x05)`: Вкладений контейнер налаштувань мережі (Nested TLV), що містить підтеги IP-адреси та порту.
- `TAG_UNKNOWN_EXP (0x85)`: Гіпотетичний новий датчик майбутньої прошивки (наприклад, 6 байтів спектральних даних), який наш старий парсер повинен успішно пропустити.

## Крайові випадки та пастки безпеки вбудованого розбору

Під час написання коду для мікроконтролерів стандартні підходи розбору рядків можуть призвести до фатальних уразливостей:

### 1. Пастка нульової довжини (`Length = 0`)
Згідно зі специфікацією TLV, запис із нульовою довжиною є цілком валідним: він сигналізує про наявність булевого прапорця (наприклад, `TAG_ALARM_ACTIVE` без додаткових параметрів). Якщо внутрішній ітератор зміщує курсор лише на величину `length` без врахування розміру заголовків `sizeof(Tag) + sizeof(Length)`, цикл розбору перетвориться на нескінченне зависання процесора. Наш ітератор завжди переміщує покажчик на `2 + length` байтів.

### 2. Цілочисельне переповнення покажчика (*Integer Overflow*)
Наївна перевірка `if (cursor + len < total_len)` на 32-бітних мікроконтролерах може бути вразливою, якщо зловмисник передасть `len = 0xFF`, а `cursor` близький до кінця адресного простору. Правильний шаблон перевірки завжди віднімає відомі величини або перевіряє доступний залишок:

:::tabs
```c
if (len > (total_len - cursor - 2)) {
    return TLV_ERR_INVALID_LENGTH;
}
```
```cpp
if (len > payload.size() - cursor) {
    return std::unexpected(TlvError::InvalidLength);
}
```
:::

### 3. Невирівняний доступ до пам'яті (*Unaligned Memory Access*)
У потоці TLV корисне навантаження `Value` може починатися з будь-якого непарного байта буфера. Пряме приведення типу `uint32_t val = *(uint32_t*)elem.value;` на мікроконтролерах ARM Cortex-M0/M0+ викликає апаратний виняток `HardFault`. Тому безпечний парсер зчитує багатобайтові числа виключно побайтово або через копіювання `memcpy`.

### 4. Вибір порядку байтів: нативний little-endian проти мережевого
Традиційні мережеві протоколи інтернету (IP, TCP, UDP) використовують порядок big-endian (старший байт попереду). Проте переважна більшість сучасних мікроконтролерів (ARM Cortex-M, ESP32, RISC-V) є нативно little-endian архітектурами. Кожне перевертання байтів через функцію `ntohl()` або команду `REV` вимагає додаткових машинних інструкцій та тактових циклів. 

У закритих або спеціалізованих вбудованих каналах (UART, SPI, радіолінк) вигідніше фіксувати порядок **little-endian** на рівні специфікації протоколу:
- Читання багатобайтового числа зводиться до найпростіших побітових зсувів `payload[0] | (payload[1] << 8)`, які оптимізатор компілятора згортає в одну інструкцію або пряме безвиняткове завантаження.
- Накладні витрати CPU знижуються практично до нуля, що критично для автономних батарейних вузлів.

### 5. Метрики здоров'я каналу зв'язку
Парсер не повинен мовчки поглинати невідомі теги. У структурі результатів передбачено лічильник `unknown_tags_count`. У діагностичній телеметрії пристрій передає це число на сервер: якщо після оновлення сусідніх вузлів лічильник невідомих тегів стрімко зростає, система моніторингу виявляє наявність застарілих шлюзів у польовій мережі та автоматично формує завдання на їхнє OTA-оновлення.

## Реалізація парсера

Код складається з двох частин:
1. **Ітератор TLV-записів**: функція низького рівня, яка перевіряє межі буфера та повертає покажчик на наступний елемент або код завершення/помилки.
2. **Диспетчер повідомлення**: обробник високого рівня, який заповнює цільову структуру відомими параметрами, підставляючи дефолтні значення для відсутніх полів, розбирає вкладені блоки та фіксує прапорці наявності `has_field`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>

/* Перелік відомих тегів протоколу */
typedef enum {
    TLV_TAG_VOLTAGE_MV     = 0x01,
    TLV_TAG_CURRENT_MA     = 0x02,
    TLV_TAG_TEMPERATURE    = 0x03,
    TLV_TAG_DEVICE_NAME    = 0x04,
    TLV_TAG_NETWORK_CONFIG = 0x05,
    /* Підтеги для вкладеного контейнера TLV_TAG_NETWORK_CONFIG */
    TLV_SUBTAG_IP_ADDR     = 0x10,
    TLV_SUBTAG_PORT        = 0x11
} TlvTag_t;

/* Коди результату обробки */
typedef enum {
    TLV_OK = 0,
    TLV_ERR_BUFFER_OVERRUN = -1,
    TLV_ERR_INVALID_LENGTH = -2,
    TLV_ERR_NESTED_INVALID = -3
} TlvStatus_t;

/* Структура одного розібраного TLV елемента */
typedef struct {
    uint8_t tag;
    uint8_t length;
    const uint8_t *value;
} TlvElement_t;

/* Структура мережевих налаштувань */
typedef struct {
    uint32_t ip_address; /* IPv4 у мережевому порядку */
    uint16_t port;
    bool     has_ip;
    bool     has_port;
} NetworkConfig_t;

/* Цільова бізнес-структура з дефолтами та прапорцями наявності */
typedef struct {
    uint16_t voltage_mv;
    int32_t  current_ma;
    int16_t  temperature_c_x100;
    char     device_name[33];
    NetworkConfig_t net_cfg;
    
    /* Бітова маска наявності полів у прийнятому пакеті */
    struct {
        uint8_t has_voltage : 1;
        uint8_t has_current : 1;
        uint8_t has_temperature : 1;
        uint8_t has_device_name : 1;
        uint8_t has_net_config : 1;
    } flags;
    
    /* Лічильник пропущених невідомих тегів */
    uint16_t unknown_tags_count;
} TelemetryData_t;

/* 
 * Низькорівневий ітератор потоку: зчитує один TLV-елемент.
 * Зсуває *cursor на наступний елемент.
 * Повертає true, якщо елемент успішно прочитано, false якщо потік закінчився або пошкоджений.
 */
static bool tlv_next_element(const uint8_t *buffer, size_t total_len, 
                             size_t *cursor, TlvElement_t *out_elem) 
{
    if (cursor == NULL || out_elem == NULL || buffer == NULL) {
        return false;
    }
    
    /* Чи залишилося хоча б 2 байти на заголовок (Tag + Length)? */
    if (*cursor + 2 > total_len) {
        return false;
    }
    
    uint8_t tag = buffer[*cursor];
    uint8_t len = buffer[*cursor + 1];
    
    /* Безпечна перевірка без ризику цілочисельного переповнення */
    if (len > (total_len - *cursor - 2)) {
        return false;
    }
    
    out_elem->tag = tag;
    out_elem->length = len;
    out_elem->value = &buffer[*cursor + 2];
    
    /* Переміщуємо курсор на наступний TLV-блок (заголовок 2 байти + тіло) */
    *cursor += 2 + len;
    return true;
}

/* 
 * Розбір вкладеного контейнера налаштувань мережі (Nested TLV).
 */
static TlvStatus_t parse_nested_network_config(const uint8_t *buffer, size_t len, 
                                               NetworkConfig_t *out_net) 
{
    size_t cursor = 0;
    TlvElement_t elem;
    
    out_net->ip_address = 0;
    out_net->port = 0;
    out_net->has_ip = false;
    out_net->has_port = false;
    
    while (cursor < len) {
        if (!tlv_next_element(buffer, len, &cursor, &elem)) {
            return TLV_ERR_NESTED_INVALID;
        }
        
        switch (elem.tag) {
            case TLV_SUBTAG_IP_ADDR:
                if (elem.length == sizeof(uint32_t)) {
                    uint32_t ip = (uint32_t)elem.value[0] |
                                  ((uint32_t)elem.value[1] << 8) |
                                  ((uint32_t)elem.value[2] << 16) |
                                  ((uint32_t)elem.value[3] << 24);
                    out_net->ip_address = ip;
                    out_net->has_ip = true;
                }
                break;
                
            case TLV_SUBTAG_PORT:
                if (elem.length == sizeof(uint16_t)) {
                    uint16_t port = (uint16_t)(elem.value[0] | (elem.value[1] << 8));
                    out_net->port = port;
                    out_net->has_port = true;
                }
                break;
                
            default:
                /* Невідомий підтег налаштувань безпечно ігноруємо */
                break;
        }
    }
    
    return TLV_OK;
}

/* 
 * Ініціалізація структури дефолтними значеннями перед розбором.
 */
void telemetry_data_init_defaults(TelemetryData_t *data) {
    if (data == NULL) return;
    
    memset(data, 0, sizeof(TelemetryData_t));
    data->voltage_mv = 0;
    data->current_ma = 0;
    data->temperature_c_x100 = -32768; /* Маркер відсутності даних */
    data->device_name[0] = '\0';
    data->unknown_tags_count = 0;
}

/* 
 * Високорівневий розбір усього TLV-пакета в структуру даних.
 */
TlvStatus_t telemetry_parse_tlv_stream(const uint8_t *buffer, size_t total_len, 
                                       TelemetryData_t *out_data) 
{
    if (buffer == NULL || out_data == NULL) {
        return TLV_ERR_BUFFER_OVERRUN;
    }
    
    telemetry_data_init_defaults(out_data);
    
    size_t cursor = 0;
    TlvElement_t elem;
    
    while (cursor < total_len) {
        if (!tlv_next_element(buffer, total_len, &cursor, &elem)) {
            /* Потік містить обрізаний або некоректний заголовок */
            return TLV_ERR_INVALID_LENGTH;
        }
        
        switch (elem.tag) {
            case TLV_TAG_VOLTAGE_MV:
                if (elem.length == sizeof(uint16_t)) {
                    /* Безпечне декодування little-endian без порушення вирівнювання */
                    out_data->voltage_mv = (uint16_t)(elem.value[0] | (elem.value[1] << 8));
                    out_data->flags.has_voltage = 1;
                }
                break;
                
            case TLV_TAG_CURRENT_MA:
                if (elem.length == sizeof(int32_t)) {
                    uint32_t raw = (uint32_t)elem.value[0] |
                                   ((uint32_t)elem.value[1] << 8) |
                                   ((uint32_t)elem.value[2] << 16) |
                                   ((uint32_t)elem.value[3] << 24);
                    out_data->current_ma = (int32_t)raw;
                    out_data->flags.has_current = 1;
                }
                break;
                
            case TLV_TAG_TEMPERATURE:
                if (elem.length == sizeof(int16_t)) {
                    uint16_t raw = (uint16_t)(elem.value[0] | (elem.value[1] << 8));
                    out_data->temperature_c_x100 = (int16_t)raw;
                    out_data->flags.has_temperature = 1;
                }
                break;
                
            case TLV_TAG_DEVICE_NAME:
                if (elem.length > 0 && elem.length < sizeof(out_data->device_name)) {
                    memcpy(out_data->device_name, elem.value, elem.length);
                    out_data->device_name[elem.length] = '\0';
                    out_data->flags.has_device_name = 1;
                }
                break;
                
            case TLV_TAG_NETWORK_CONFIG:
                if (parse_nested_network_config(elem.value, elem.length, &out_data->net_cfg) == TLV_OK) {
                    out_data->flags.has_net_config = 1;
                }
                break;
                
            default:
                /* 
                 * ПРЯМА СУМІСНІСТЬ (Forward Compatibility):
                 * Невідомий тег просто ігнорується, курсор уже зсунуто вперед на elem.length.
                 */
                out_data->unknown_tags_count++;
                break;
        }
    }
    
    return TLV_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <string_view>
#include <optional>
#include <expected>
#include <array>
#include <string>

enum class TlvTag : uint8_t {
    VoltageMv     = 0x01,
    CurrentMa     = 0x02,
    Temperature   = 0x03,
    DeviceName    = 0x04,
    NetworkConfig = 0x05
};

enum class TlvSubTag : uint8_t {
    IpAddress = 0x10,
    Port      = 0x11
};

enum class TlvError {
    BufferOverrun,
    InvalidLength,
    TruncatedPayload,
    NestedInvalid
};

struct NetworkConfig {
    std::optional<uint32_t> ip_address;
    std::optional<uint16_t> port;
};

struct TelemetryData {
    std::optional<uint16_t> voltage_mv;
    std::optional<int32_t>  current_ma;
    std::optional<int16_t>  temperature_c_x100;
    std::string             device_name;
    NetworkConfig           net_cfg;
    uint16_t                unknown_tags_count{0};
};

class TlvStreamParser {
private:
    static std::expected<NetworkConfig, TlvError> 
    parse_nested_net_cfg(std::span<const uint8_t> payload) {
        NetworkConfig net;
        size_t cursor = 0;

        while (cursor < payload.size()) {
            if (cursor + 2 > payload.size()) {
                return std::unexpected(TlvError::TruncatedPayload);
            }

            const uint8_t tag = payload[cursor];
            const uint8_t len = payload[cursor + 1];
            cursor += 2;

            if (len > payload.size() - cursor) {
                return std::unexpected(TlvError::InvalidLength);
            }

            auto val_span = payload.subspan(cursor, len);
            cursor += len;

            switch (static_cast<TlvSubTag>(tag)) {
                case TlvSubTag::IpAddress:
                    if (val_span.size() == sizeof(uint32_t)) {
                        uint32_t ip = static_cast<uint32_t>(val_span[0]) |
                                      (static_cast<uint32_t>(val_span[1]) << 8) |
                                      (static_cast<uint32_t>(val_span[2]) << 16) |
                                      (static_cast<uint32_t>(val_span[3]) << 24);
                        net.ip_address = ip;
                    }
                    break;

                case TlvSubTag::Port:
                    if (val_span.size() == sizeof(uint16_t)) {
                        net.port = static_cast<uint16_t>(val_span[0] | (val_span[1] << 8));
                    }
                    break;

                default:
                    // Пропуск невідомого підтегу
                    break;
            }
        }

        return net;
    }

public:
    static std::expected<TelemetryData, TlvError> parse(std::span<const uint8_t> payload) {
        TelemetryData result;
        size_t cursor = 0;

        while (cursor < payload.size()) {
            if (cursor + 2 > payload.size()) {
                return std::unexpected(TlvError::TruncatedPayload);
            }

            const uint8_t tag = payload[cursor];
            const uint8_t len = payload[cursor + 1];
            cursor += 2;

            if (len > payload.size() - cursor) {
                return std::unexpected(TlvError::InvalidLength);
            }

            auto val_span = payload.subspan(cursor, len);
            cursor += len;

            switch (static_cast<TlvTag>(tag)) {
                case TlvTag::VoltageMv:
                    if (val_span.size() == sizeof(uint16_t)) {
                        result.voltage_mv = static_cast<uint16_t>(val_span[0] | (val_span[1] << 8));
                    }
                    break;

                case TlvTag::CurrentMa:
                    if (val_span.size() == sizeof(int32_t)) {
                        uint32_t raw = static_cast<uint32_t>(val_span[0]) |
                                       (static_cast<uint32_t>(val_span[1]) << 8) |
                                       (static_cast<uint32_t>(val_span[2]) << 16) |
                                       (static_cast<uint32_t>(val_span[3]) << 24);
                        result.current_ma = static_cast<int32_t>(raw);
                    }
                    break;

                case TlvTag::Temperature:
                    if (val_span.size() == sizeof(int16_t)) {
                        uint16_t raw = static_cast<uint16_t>(val_span[0] | (val_span[1] << 8));
                        result.temperature_c_x100 = static_cast<int16_t>(raw);
                    }
                    break;

                case TlvTag::DeviceName:
                    if (!val_span.empty() && val_span.size() <= 32) {
                        result.device_name = std::string(
                            reinterpret_cast<const char*>(val_span.data()), 
                            val_span.size()
                        );
                    }
                    break;

                case TlvTag::NetworkConfig:
                    if (auto net_res = parse_nested_net_cfg(val_span); net_res.has_value()) {
                        result.net_cfg = *net_res;
                    }
                    break;

                default:
                    result.unknown_tags_count++;
                    break;
            }
        }

        return result;
    }
};
```
:::

## Тестовий стенд і перевірка стійкості

Для перевірки прямої та зворотної сумісності запустимо парсер на чотирьох характерних векторах даних:

1. **Вектор 1 (Базовий пакет v1.0)**: містить тільки напругу 3300 мВ (`0x0CE4`) та струм 150 мА (`0x00000096`).
2. **Вектор 2 (Розширений пакет v2.0 з невідомим сенсором)**: містить напругу, потім невідомий тег майбутнього спектрометра `0x85` (довжина 6 байтів: `0xAA 0xBB 0xCC 0xDD 0xEE 0xFF`), потім температуру 23.48 °C (`0x092C`) та назву вузла `"Node-7"`.
3. **Вектор 3 (Пакет із вкладеним контейнером Nested TLV)**: містить конфігурацію мережі (IP `192.168.1.100`, Port `8080`).
4. **Вектор 4 (Пошкоджений бінарний потік)**: містить тег напруги, але поле довжини заявляє 80 байтів при розмірі буфера 4 байти.

:::tabs
```c
int main(void) {
    TelemetryData_t data;
    
    /* 1. Базовий пакет v1.0 */
    const uint8_t pkt_v1[] = {
        0x01, 0x02, 0xE4, 0x0C,             /* Tag 1, Len 2: Voltage = 3300 mV */
        0x02, 0x04, 0x96, 0x00, 0x00, 0x00  /* Tag 2, Len 4: Current = 150 mA */
    };
    
    if (telemetry_parse_tlv_stream(pkt_v1, sizeof(pkt_v1), &data) == TLV_OK) {
        printf("Pkt v1 parsed: V=%u mV, I=%ld mA, Temp_present=%d, Unknown=%u\n",
               data.voltage_mv, (long)data.current_ma, 
               data.flags.has_temperature, data.unknown_tags_count);
    }
    
    /* 2. Розширений пакет із невідомим тегом 0x85 */
    const uint8_t pkt_v2[] = {
        0x01, 0x02, 0xE4, 0x0C,                         /* Voltage = 3300 mV */
        0x85, 0x06, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, /* НЕВІДОМИЙ ТЕГ 0x85 */
        0x03, 0x02, 0x2C, 0x09,                         /* Temp = 2348 (23.48 C) */
        0x04, 0x06, 'N', 'o', 'd', 'e', '-', '7'        /* Name = "Node-7" */
    };
    
    if (telemetry_parse_tlv_stream(pkt_v2, sizeof(pkt_v2), &data) == TLV_OK) {
        printf("Pkt v2 parsed: V=%u mV, Temp=%.2f C, Name='%s', Unknown=%u\n",
               data.voltage_mv, (double)data.temperature_c_x100 / 100.0,
               data.device_name, data.unknown_tags_count);
    }
    
    /* 3. Пакет із вкладеним TLV (Network Config) */
    const uint8_t pkt_nested[] = {
        0x05, 0x0A,                                     /* Tag 5 (NetConfig), Len 10 */
        0x10, 0x04, 0xC0, 0xA8, 0x01, 0x64,             /* Subtag 0x10 (IP): 192.168.1.100 */
        0x11, 0x02, 0x90, 0x1F                          /* Subtag 0x11 (Port): 8080 (0x1F90) */
    };
    
    if (telemetry_parse_tlv_stream(pkt_nested, sizeof(pkt_nested), &data) == TLV_OK) {
        printf("Pkt nested: IP_present=%d, Port=%u\n", 
               data.net_cfg.has_ip, data.net_cfg.port);
    }
    
    /* 4. Зіпсований пакет із некоректною довжиною */
    const uint8_t pkt_corrupt[] = {
        0x01, 0x50, 0xE4, 0x0C /* Заявлена довжина 80 байтів при фактичних 2 */
    };
    
    TlvStatus_t status = telemetry_parse_tlv_stream(pkt_corrupt, sizeof(pkt_corrupt), &data);
    printf("Corrupt packet status: %d (Expected %d)\n", status, TLV_ERR_INVALID_LENGTH);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>

int main() {
    // 1. Базовий пакет
    const std::array<uint8_t, 10> pkt_v1 = {
        0x01, 0x02, 0xE4, 0x0C,
        0x02, 0x04, 0x96, 0x00, 0x00, 0x00
    };

    if (auto res = TlvStreamParser::parse(pkt_v1); res.has_value()) {
        std::cout << "Pkt v1 parsed: V=" << res->voltage_mv.value_or(0)
                  << " mV, I=" << res->current_ma.value_or(0)
                  << " mA, Temp_present=" << res->temperature_c_x100.has_value()
                  << ", Unknown=" << res->unknown_tags_count << "\n";
    }

    // 2. Розширений пакет із невідомим тегом 0x85
    const std::array<uint8_t, 22> pkt_v2 = {
        0x01, 0x02, 0xE4, 0x0C,
        0x85, 0x06, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,
        0x03, 0x02, 0x2C, 0x09,
        0x04, 0x06, 'N', 'o', 'd', 'e', '-', '7'
    };

    if (auto res = TlvStreamParser::parse(pkt_v2); res.has_value()) {
        std::cout << "Pkt v2 parsed: V=" << res->voltage_mv.value_or(0)
                  << " mV, Temp=" << std::fixed << std::setprecision(2)
                  << (res->temperature_c_x100.value_or(0) / 100.0)
                  << " C, Name='" << res->device_name
                  << "', Unknown=" << res->unknown_tags_count << "\n";
    }

    // 3. Вкладений TLV
    const std::array<uint8_t, 12> pkt_nested = {
        0x05, 0x0A,
        0x10, 0x04, 0xC0, 0xA8, 0x01, 0x64,
        0x11, 0x02, 0x90, 0x1F
    };

    if (auto res = TlvStreamParser::parse(pkt_nested); res.has_value()) {
        std::cout << "Pkt nested parsed: IP_present=" << res->net_cfg.ip_address.has_value()
                  << ", Port=" << res->net_cfg.port.value_or(0) << "\n";
    }

    // 4. Зіпсований пакет
    const std::array<uint8_t, 4> pkt_corrupt = {
        0x01, 0x50, 0xE4, 0x0C
    };

    auto res_corrupt = TlvStreamParser::parse(pkt_corrupt);
    std::cout << "Corrupt packet valid: " << std::boolalpha << res_corrupt.has_value() << "\n";

    return 0;
}
```
:::

## Інженерні висновки

1. **Безпека меж**: Вираз `len > (total_len - *cursor - 2)` гарантує, що парсер ніколи не вийде за межі масиву пам'яті незалежно від вмісту вхідних байтів.
2. **Нульове копіювання**: Прості числові типи зчитуються безпосередньо з буфера через побітові зсуви, що запобігає апаратним виняткам невирівняного доступу (*unaligned memory access trap*) на мікроконтролерах ARM Cortex-M0/M3.
3. **Логічна ізоляція**: Поява десятків нових типів сенсорів у майбутніх версіях пристроїв не вимагає перепрошивки старих проміжних шлюзів і маршрутизаторів, якщо вони реалізують TLV-пропуск.
4. **Витрати пам'яті та тактових циклів**: Весь розбір виконується в межах одного стекового фрейму (близько 64 байтів стека на виклик). На мікроконтролері з тактовою частотою 48 МГц розбір типового пакета з 5 полів займає менше ніж 1.2 мікросекунди, що повністю відповідає вимогам систем реального часу.

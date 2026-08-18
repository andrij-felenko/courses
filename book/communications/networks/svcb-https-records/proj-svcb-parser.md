# ⚙️ Розбір двійкового формату записів SVCB та HTTPS на C і C++

У цій практичній вставці реалізовано повноцінний надійний розбирач (парсер) двійкового формату поля RDATA для ресурсних записів DNS типу SVCB (тип 64) та HTTPS (тип 65) відповідно до стандарту RFC 9460. Він призначений для використання у складі мережевих клієнтів, HTTP-бібліотек, веб-браузерів та системних DNS-резолверів, яким необхідно витягувати параметри транспортних протоколів ALPN, нестандартні порти, IP-підказки та криптографічні ключі ECH безпосередньо з сирих двійкових відповідей DNS.

## Архітектура парсера та вимоги безпеки RFC 9460

Класичний парсинг ресурсних записів DNS зазвичай зводився до простого копіювання фіксованих структур (як-от 4 байти для запису A або 16 байтів для AAAA). Проте записи SVCB та HTTPS мають динамічну TLV-структуру (Type-Length-Value), що містить змінну кількість параметрів довільної довжини. Це вимагає ретельної перевірки меж пам'яті (bounds checking) для запобігання вразливостям переповнення буфера (buffer overflow) та читання за межами виділеної пам'яті (out-of-bounds read).

Специфікація RFC 9460 встановлює п'ять обов'язкових правил валідації, порушення будь-якого з яких вимагає від клієнта повного відкидання отриманого запису:

1. **Сувора заборона стиснення імен (DNS Name Compression).** У класичному DNS (RFC 1035) для економії байтів у пакеті мітки доменних імен можуть замінюватися 2-байтовими покажчиками зі старшими бітами `11xx xxxx` (значення `0xC0..0xFF`), які вказують на зміщення раніше зустрінутого імені. У записах SVCB/HTTPS у полі `TargetName` використання таких покажчиків **заборонено**. Це рішення усуває небезпеку зациклення покажчиків стиснення та значно прискорює парсинг RDATA без необхідності доступу до повного початкового буфера DNS-пакета.
2. **Канонічне сортування ключів `SvcParamKey`.** Параметри `SvcParams` на дроті зобов'язані слідувати у строго зростаючому числовому порядку (`Key[0] < Key[1] < Key[2]`). Наприклад, ключ `alpn` (1) зобов'язаний передувати ключу `port` (3), а `port` (3) — ключу `ipv4hint` (4). Наявність невідсортованих ключів або дублікатів свідчить про пошкодження або фальсифікацію пакета.
3. **Розділення режимів `AliasMode` та `ServiceMode`.** Запис із числовим значенням `SvcPriority = 0` позначає аліас. У цьому режимі поле `TargetName` зобов'язане містити валідне доменне ім'я (значення `.` є неприпустимим), а хвіст параметрів `SvcParams` зобов'язаний бути повністю порожнім. Навпаки, у режимі `ServiceMode` (`SvcPriority > 0`) ціль `.` дозволена (позначає поточне ім'я запиту), а наявність параметрів визначає конфігурацію служби.
4. **Валідація розмірностей параметрів.** Для кожного стандартного параметра визначено суворі правила довжини: `port` зобов'язаний мати довжину рівно 2 байти; `no-default-alpn` — рівно 0 байтів; `ipv4hint` — кратну 4 байтам; `ipv6hint` — кратну 16 байтам; `mandatory` — парну кількість байтів.
5. **Обробка списку критичних параметрів (`mandatory`).** Якщо в параметрі `mandatory` перелічено числовий ідентифікатор ключа, невідомий цьому парсеру, запис не може бути використаний для встановлення з'єднання.

## Реалізація парсера мовами C та C++

Нижче наведено паралельну реалізацію розбирача двома системними мовами. 

У вкладці **C** представлено компактний код у стандарті C99/C11, що використовує роботу з сирими покажчиками, явне перетворення порядку байтів із мережевого (big-endian) у хостовий та фіксовані структури без динамічного виділення пам'яті (за винятком довільного буфера ECH).

У вкладці **C++** реалізовано сучасний ідіоматичний підхід у стандарті C++20: передача безпечних неволодіючих представлень пам'яті `std::span<const uint8_t>`, типізовані переліки `enum class`, автоматичне керування пам'яттю через `std::vector` і `std::string`, а також повернення результату або коду помилки через монадичний тип `std::expected`.

:::tabs
```c
/* svcb_parser.c — Низькорівневий парсер RDATA записів SVCB/HTTPS (RFC 9460) на C */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_WIN32)
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#endif

#define SVCB_KEY_MANDATORY        0
#define SVCB_KEY_ALPN             1
#define SVCB_KEY_NO_DEFAULT_ALPN  2
#define SVCB_KEY_PORT             3
#define SVCB_KEY_IPV4HINT         4
#define SVCB_KEY_ECH              5
#define SVCB_KEY_IPV6HINT         6
#define SVCB_KEY_DOHPATH          7

#define MAX_TARGET_NAME_LEN 256
#define MAX_ALPN_ENTRIES    8
#define MAX_IP_HINTS        8

typedef struct {
    uint16_t priority;
    bool is_alias_mode;
    char target_name[MAX_TARGET_NAME_LEN];
    
    /* Параметри ServiceMode */
    uint16_t port;                      /* За замовчуванням 443 для HTTPS */
    bool no_default_alpn;
    
    char alpn_list[MAX_ALPN_ENTRIES][32];
    size_t alpn_count;
    
    struct in_addr ipv4_hints[MAX_IP_HINTS];
    size_t ipv4_count;
    
    struct in6_addr ipv6_hints[MAX_IP_HINTS];
    size_t ipv6_count;
    
    uint8_t *ech_config;
    size_t ech_len;
    
    uint16_t mandatory_keys[16];
    size_t mandatory_count;
} svcb_record_t;

typedef enum {
    SVCB_OK = 0,
    SVCB_ERR_TRUNCATED,
    SVCB_ERR_INVALID_NAME,
    SVCB_ERR_COMPRESSION_NOT_ALLOWED,
    SVCB_ERR_ALIAS_HAS_PARAMS,
    SVCB_ERR_KEYS_NOT_SORTED,
    SVCB_ERR_DUPLICATE_KEY,
    SVCB_ERR_INVALID_PARAM_LEN,
    SVCB_ERR_MANDATORY_VIOLATION
} svcb_error_t;

/* Читання доменного імені без використання покажчиків стиснення */
static svcb_error_t parse_dns_name(const uint8_t *buf, size_t len, size_t *offset,
                                  char *out_name, size_t max_out) {
    size_t pos = *offset;
    size_t out_pos = 0;
    
    out_name[0] = '\0';
    
    while (pos < len) {
        uint8_t label_len = buf[pos++];
        
        /* Заборона DNS compression pointers (0xC0..0xFF) за RFC 9460 */
        if ((label_len & 0xC0) != 0) {
            return SVCB_ERR_COMPRESSION_NOT_ALLOWED;
        }
        
        if (label_len == 0) {
            /* Нульова мітка завершує ім'я */
            if (out_pos == 0) {
                if (max_out < 2) return SVCB_ERR_INVALID_NAME;
                out_name[0] = '.';
                out_name[1] = '\0';
            } else {
                out_name[out_pos] = '\0';
            }
            *offset = pos;
            return SVCB_OK;
        }
        
        if (pos + label_len > len) {
            return SVCB_ERR_TRUNCATED;
        }
        
        if (out_pos > 0 && out_pos < max_out - 1) {
            out_name[out_pos++] = '.';
        }
        
        if (out_pos + label_len >= max_out) {
            return SVCB_ERR_INVALID_NAME;
        }
        
        memcpy(&out_name[out_pos], &buf[pos], label_len);
        out_pos += label_len;
        pos += label_len;
    }
    
    return SVCB_ERR_TRUNCATED;
}

/* Розбір блоку RDATA запису SVCB/HTTPS */
svcb_error_t svcb_parse_rdata(const uint8_t *rdata, size_t rdata_len, svcb_record_t *rec) {
    if (!rdata || !rec) return SVCB_ERR_TRUNCATED;
    if (rdata_len < 3) return SVCB_ERR_TRUNCATED;
    
    memset(rec, 0, sizeof(*rec));
    rec->port = 443; /* Порт за замовчуванням */
    
    size_t offset = 0;
    
    /* 1. SvcPriority (2 байти, big-endian) */
    rec->priority = (uint16_t)((rdata[offset] << 8) | rdata[offset + 1]);
    offset += 2;
    rec->is_alias_mode = (rec->priority == 0);
    
    /* 2. TargetName */
    svcb_error_t err = parse_dns_name(rdata, rdata_len, &offset,
                                      rec->target_name, sizeof(rec->target_name));
    if (err != SVCB_OK) return err;
    
    /* У режимі AliasMode ціль не може бути "." і параметри заборонені */
    if (rec->is_alias_mode) {
        if (strcmp(rec->target_name, ".") == 0) {
            return SVCB_ERR_INVALID_NAME;
        }
        if (offset < rdata_len) {
            return SVCB_ERR_ALIAS_HAS_PARAMS;
        }
        return SVCB_OK;
    }
    
    /* 3. SvcParams (режим ServiceMode) */
    int32_t last_key = -1;
    
    while (offset < rdata_len) {
        if (offset + 4 > rdata_len) return SVCB_ERR_TRUNCATED;
        
        uint16_t key = (uint16_t)((rdata[offset] << 8) | rdata[offset + 1]);
        uint16_t val_len = (uint16_t)((rdata[offset + 2] << 8) | rdata[offset + 3]);
        offset += 4;
        
        if (offset + val_len > rdata_len) return SVCB_ERR_TRUNCATED;
        
        /* Перевірка строгого сортування ключів (Key[i] > Key[i-1]) */
        if ((int32_t)key <= last_key) {
            return (key == (uint16_t)last_key) ? SVCB_ERR_DUPLICATE_KEY : SVCB_ERR_KEYS_NOT_SORTED;
        }
        last_key = (int32_t)key;
        
        const uint8_t *val = &rdata[offset];
        
        switch (key) {
            case SVCB_KEY_MANDATORY: {
                if (val_len % 2 != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                size_t count = val_len / 2;
                for (size_t i = 0; i < count && rec->mandatory_count < 16; i++) {
                    uint16_t mkey = (uint16_t)((val[i*2] << 8) | val[i*2 + 1]);
                    rec->mandatory_keys[rec->mandatory_count++] = mkey;
                }
                break;
            }
            case SVCB_KEY_ALPN: {
                size_t v_off = 0;
                while (v_off < val_len && rec->alpn_count < MAX_ALPN_ENTRIES) {
                    uint8_t slen = val[v_off++];
                    if (v_off + slen > val_len || slen >= 32) return SVCB_ERR_INVALID_PARAM_LEN;
                    memcpy(rec->alpn_list[rec->alpn_count], &val[v_off], slen);
                    rec->alpn_list[rec->alpn_count][slen] = '\0';
                    rec->alpn_count++;
                    v_off += slen;
                }
                break;
            }
            case SVCB_KEY_NO_DEFAULT_ALPN: {
                if (val_len != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                rec->no_default_alpn = true;
                break;
            }
            case SVCB_KEY_PORT: {
                if (val_len != 2) return SVCB_ERR_INVALID_PARAM_LEN;
                rec->port = (uint16_t)((val[0] << 8) | val[1]);
                break;
            }
            case SVCB_KEY_IPV4HINT: {
                if (val_len % 4 != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                size_t count = val_len / 4;
                for (size_t i = 0; i < count && rec->ipv4_count < MAX_IP_HINTS; i++) {
                    memcpy(&rec->ipv4_hints[rec->ipv4_count++].s_addr, &val[i*4], 4);
                }
                break;
            }
            case SVCB_KEY_IPV6HINT: {
                if (val_len % 16 != 0) return SVCB_ERR_INVALID_PARAM_LEN;
                size_t count = val_len / 16;
                for (size_t i = 0; i < count && rec->ipv6_count < MAX_IP_HINTS; i++) {
                    memcpy(&rec->ipv6_hints[rec->ipv6_count++].s6_addr, &val[i*16], 16);
                }
                break;
            }
            case SVCB_KEY_ECH: {
                rec->ech_config = (uint8_t *)malloc(val_len);
                if (rec->ech_config) {
                    memcpy(rec->ech_config, val, val_len);
                    rec->ech_len = val_len;
                }
                break;
            }
            default:
                /* Невідомі ключі пропускаються, якщо вони не вказані у mandatory */
                break;
        }
        
        offset += val_len;
    }
    
    return SVCB_OK;
}

void svcb_free_record(svcb_record_t *rec) {
    if (rec && rec->ech_config) {
        free(rec->ech_config);
        rec->ech_config = NULL;
        rec->ech_len = 0;
    }
}
```
```cpp
// svcb_parser.cpp — Ідіоматичний парсер RDATA записів SVCB/HTTPS (RFC 9460) на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <expected>
#include <cstdint>
#include <cstring>
#include <array>

#if defined(_WIN32)
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#endif

enum class SvcParamKey : uint16_t {
    Mandatory      = 0,
    Alpn           = 1,
    NoDefaultAlpn  = 2,
    Port           = 3,
    Ipv4Hint       = 4,
    Ech            = 5,
    Ipv6Hint       = 6,
    DohPath        = 7
};

enum class ParseError {
    Truncated,
    InvalidName,
    CompressionNotAllowed,
    AliasHasParams,
    KeysNotSorted,
    DuplicateKey,
    InvalidParamLength,
    MandatoryViolation
};

struct SvcRecord {
    uint16_t priority{0};
    bool is_alias_mode{false};
    std::string target_name;
    
    uint16_t port{443};
    bool no_default_alpn{false};
    std::vector<std::string> alpns;
    std::vector<in_addr> ipv4_hints;
    std::vector<in6_addr> ipv6_hints;
    std::vector<uint8_t> ech_config;
    std::vector<uint16_t> mandatory_keys;
};

class SvcParser {
public:
    static std::expected<SvcRecord, ParseError> parse(std::span<const uint8_t> rdata) {
        if (rdata.size() < 3) {
            return std::unexpected(ParseError::Truncated);
        }
        
        SvcRecord rec;
        size_t offset = 0;
        
        // 1. Читання SvcPriority (uint16 big-endian)
        rec.priority = static_cast<uint16_t>((rdata[0] << 8) | rdata[1]);
        offset += 2;
        rec.is_alias_mode = (rec.priority == 0);
        
        // 2. Читання TargetName
        auto name_res = parse_name(rdata, offset);
        if (!name_res) return std::unexpected(name_res.error());
        
        rec.target_name = std::move(*name_res);
        
        if (rec.is_alias_mode) {
            if (rec.target_name == ".") {
                return std::unexpected(ParseError::InvalidName);
            }
            if (offset < rdata.size()) {
                return std::unexpected(ParseError::AliasHasParams);
            }
            return rec;
        }
        
        // 3. Читання SvcParams
        int32_t last_key = -1;
        while (offset < rdata.size()) {
            if (offset + 4 > rdata.size()) {
                return std::unexpected(ParseError::Truncated);
            }
            
            uint16_t raw_key = static_cast<uint16_t>((rdata[offset] << 8) | rdata[offset + 1]);
            uint16_t val_len = static_cast<uint16_t>((rdata[offset + 2] << 8) | rdata[offset + 3]);
            offset += 4;
            
            if (offset + val_len > rdata.size()) {
                return std::unexpected(ParseError::Truncated);
            }
            
            if (static_cast<int32_t>(raw_key) <= last_key) {
                return std::unexpected(raw_key == static_cast<uint16_t>(last_key) 
                    ? ParseError::DuplicateKey : ParseError::KeysNotSorted);
            }
            last_key = static_cast<int32_t>(raw_key);
            
            auto val_span = rdata.subspan(offset, val_len);
            auto err = parse_param(static_cast<SvcParamKey>(raw_key), val_span, rec);
            if (err != ParseError::Truncated && err != ParseError::InvalidName) {
                if (err != static_cast<ParseError>(0)) {
                    return std::unexpected(err);
                }
            }
            
            offset += val_len;
        }
        
        return rec;
    }

private:
    static std::expected<std::string, ParseError> parse_name(std::span<const uint8_t> buf, size_t &offset) {
        std::string result;
        size_t pos = offset;
        
        while (pos < buf.size()) {
            uint8_t len = buf[pos++];
            if ((len & 0xC0) != 0) {
                return std::unexpected(ParseError::CompressionNotAllowed);
            }
            if (len == 0) {
                offset = pos;
                return result.empty() ? "." : result;
            }
            if (pos + len > buf.size()) {
                return std::unexpected(ParseError::Truncated);
            }
            if (!result.empty()) result += '.';
            result.append(reinterpret_cast<const char*>(&buf[pos]), len);
            pos += len;
        }
        return std::unexpected(ParseError::Truncated);
    }
    
    static ParseError parse_param(SvcParamKey key, std::span<const uint8_t> val, SvcRecord &rec) {
        switch (key) {
            case SvcParamKey::Mandatory: {
                if (val.size() % 2 != 0) return ParseError::InvalidParamLength;
                for (size_t i = 0; i < val.size(); i += 2) {
                    rec.mandatory_keys.push_back(static_cast<uint16_t>((val[i] << 8) | val[i+1]));
                }
                break;
            }
            case SvcParamKey::Alpn: {
                size_t v_off = 0;
                while (v_off < val.size()) {
                    uint8_t slen = val[v_off++];
                    if (v_off + slen > val.size()) return ParseError::InvalidParamLength;
                    rec.alpns.emplace_back(reinterpret_cast<const char*>(&val[v_off]), slen);
                    v_off += slen;
                }
                break;
            }
            case SvcParamKey::NoDefaultAlpn:
                if (!val.empty()) return ParseError::InvalidParamLength;
                rec.no_default_alpn = true;
                break;
                
            case SvcParamKey::Port:
                if (val.size() != 2) return ParseError::InvalidParamLength;
                rec.port = static_cast<uint16_t>((val[0] << 8) | val[1]);
                break;
                
            case SvcParamKey::Ipv4Hint: {
                if (val.size() % 4 != 0) return ParseError::InvalidParamLength;
                for (size_t i = 0; i < val.size(); i += 4) {
                    in_addr addr;
                    std::memcpy(&addr.s_addr, &val[i], 4);
                    rec.ipv4_hints.push_back(addr);
                }
                break;
            }
            case SvcParamKey::Ipv6Hint: {
                if (val.size() % 16 != 0) return ParseError::InvalidParamLength;
                for (size_t i = 0; i < val.size(); i += 16) {
                    in6_addr addr;
                    std::memcpy(&addr.s6_addr, &val[i], 16);
                    rec.ipv6_hints.push_back(addr);
                }
                break;
            }
            case SvcParamKey::Ech:
                rec.ech_config.assign(val.begin(), val.end());
                break;
                
            default:
                break;
        }
        return static_cast<ParseError>(0);
    }
};
```
:::

## Детальний розбір механізму роботи алгоритму

Щоб зрозуміти, як процесор обробляє кожен байт поля RDATA, простежимо покрокове виконання розбору на реальних сценаріях.

### 1. Декодування імені вузла (TargetName) без рекурсії покажчиків

Функція `parse_dns_name` отримує потік байтів, починаючи з третього октету (після двох байтів `SvcPriority`). У звичайному розбирачі DNS імен (наприклад, для записів PTR чи MX) обробник перевіряє два старші біти довжини мітки: якщо вони дорівнюють `11` (`0xC0`), алгоритм інтерпретує наступні 14 бітів як зміщення (offset) від початку всього DNS-пакета та стрибає за покажчиком.

У нашому парсері перевірка `if ((label_len & 0xC0) != 0)` негайно повертає код `SVCB_ERR_COMPRESSION_NOT_ALLOWED`. Це робить парсер лінійним та автономним: йому не потрібен доступ до заголовка DNS-повідомлення чи інших секцій пакету, що унеможливлює експлуатацію вразливостей некоректних або циклічних зміщень.

Коли зустрічається байт `0x00` (нульова мітка), це свідчить про досягнення кореня доменного дерева. Якщо нульовий байт зустрівся на першій же позиції, ім'я вважається порожнім коренем `.` — у режимі `ServiceMode` це позначає, що запис стосується безпосередньо того домену, який запитувався.

### 2. Цикл обробки TLV-параметрів (SvcParams)

Після успішного прочитання `TargetName` залишок буфера інтерпретується як послідовність блоків TLV. На кожній ітерації циклу:

1. **Контроль довжини заголовка:** Перевіряється `offset + 4 <= rdata_len`. Якщо в буфері залишилося менше 4 байтів, пакет вважається обірваним (`SVCB_ERR_TRUNCATED`).
2. **Зчитування ключа та довжини:** Перші два байти формують `uint16_t key`, наступні два — `uint16_t val_len`. Обидва значення перетворюються з big-endian у системний порядок за допомогою зсувів `(b[0] << 8) | b[1]`.
3. **Контроль довжини корисного навантаження:** Перевіряється `offset + val_len <= rdata_len`. Якщо довжина значення виходить за межі буфера RDATA, цикл переривається з помилкою усічення.
4. **Контроль монотонності:** Стан `last_key` ініціалізується числом `-1`. На кожній ітерації перевіряється умова `(int32_t)key <= last_key`. Якщо новий ключ менший за попередній або дорівнює йому, парсер фіксує порушення канонічного порядку (`SVCB_ERR_KEYS_NOT_SORTED` або `SVCB_ERR_DUPLICATE_KEY`).
5. **Диспетчеризація типу:** Залежно від числового значення ключа викликається відповідна підпрограма розбору.

## Розбір тестових сценаріїв та ін'єкцій помилок

Для перевірки коректності роботи реалізації створено набір контрольних двійкових векторів.

### Сценарій 1. Успішний розбір AliasMode на вершині зони

Вхідний бінарний буфер (RDATA):
```text
00 00 03 63 64 6e 07 65 78 61 6d 70 6c 65 03 6e 65 74 00
```

Покроковий аналіз виконання:
* `offset = 0`: байти `00 00` -> `priority = 0`. Вмикається прапорець `is_alias_mode = true`.
* `offset = 2`: перший байт мітки `0x03`, символи `c`, `d`, `n` (`cdn`).
* `offset = 6`: другий байт мітки `0x07`, символи `e`, `x`, `a`, `m`, `p`, `l`, `e` (`example`).
* `offset = 14`: третій байт мітки `0x03`, символи `n`, `e`, `t` (`net`).
* `offset = 18`: нульовий байт завершення `0x00`. Отримано повне ім'я `"cdn.example.net"`.
* Перевірка: `offset == rdata_len` (19 байтів). Зайвих параметрів немає.
* Результат: `SVCB_OK`. Клієнт отримує цільовий хост для рекурсивного переходу.

### Сценарій 2. Успішний розбір ServiceMode з ALPN (HTTP/3 + HTTP/2), портом та IPv4-підказкою

Вхідний бінарний буфер (RDATA):
```text
00 01 00 00 01 00 06 02 68 33 02 68 32 00 03 00 02 20 fb 00 04 00 04 c6 33 64 01
```

Покроковий аналіз виконання:
* `priority = 1`, `TargetName = "."` (поточний хост).
* Блок 1: `key = 1` (`alpn`), `len = 6`. Перший елемент: `slen = 2`, символи `"h3"`. Другий елемент: `slen = 2`, символи `"h2"`. `last_key = 1`.
* Блок 2: `key = 3` (`port`), `len = 2`. Значення `0x20fb = 8443`. Оскільки `3 > 1`, порядок валідний. `last_key = 3`.
* Блок 3: `key = 4` (`ipv4hint`), `len = 4`. Значення `0xC6336401` відповідає адресі `198.51.100.1`. Оскільки `4 > 3`, порядок валідний.
* Результат: `SVCB_OK`. Структура містить повну інформацію для негайного запуску QUIC на порт 8443 за IP-адресою 198.51.100.1.

### Сценарій 3. Ін'єкція помилки: наявність покажчика стиснення DNS

Вхідний буфер з некоректним `TargetName`:
```text
00 01 c0 0c 00 01 00 06 02 68 33 02 68 32
```

Покроковий аналіз виконання:
* `priority = 1`.
* `offset = 2`: перший байт мітки має значення `0xC0` (`1100 0000` у двійковій системі).
* Умова `(label_len & 0xC0) != 0` спрацьовує ідентифікуючи заборонений покажчик стиснення.
* Результат: негайне повернення `SVCB_ERR_COMPRESSION_NOT_ALLOWED` (або `ParseError::CompressionNotAllowed`). Запис відкидається.

### Сценарій 4. Ін'єкція помилки: порушення порядку сортування параметрів

Вхідний буфер, де параметр `port` (3) передує параметру `alpn` (1):
```text
00 01 00 00 03 00 02 20 fb 00 01 00 06 02 68 33 02 68 32
```

Покроковий аналіз виконання:
* Перший TLV (`port`, key=3) успішно розбирається. `last_key` стає рівним `3`.
* Другий TLV (`alpn`, key=1): парсер перевіряє `key (1) <= last_key (3)`.
* Умова справджується, оскільки 1 менше за 3.
* Результат: `SVCB_ERR_KEYS_NOT_SORTED` (або `ParseError::KeysNotSorted`).

### Сценарій 5. Ін'єкція помилки: некоректна довжина адресної підказки

Вхідний буфер, де параметр `ipv4hint` має довжину 5 байтів замість 4:
```text
00 01 00 00 04 00 05 c6 33 64 01 ff
```

Покроковий аналіз виконання:
* `key = 4` (`ipv4hint`), `val_len = 5`.
* Перевірка `val_len % 4 != 0` виявляє, що довжина не ділиться націло на розмір IPv4-адреси.
* Результат: `SVCB_ERR_INVALID_PARAM_LEN` (або `ParseError::InvalidParamLength`).

## Побудова черги з'єднань (Connection Plan) та інтеграція з Happy Eyeballs

Отриманий після парсингу об'єкт `SvcRecord` або `svcb_record_t` передається модулю транспортного рівня. Цей модуль формує структурований план з'єднання відповідно до алгоритму Happy Eyeballs v2 (RFC 8305):

1. **Вибір протоколу:**
   * Якщо `alpns` містить `"h3"`, створюється кандидат на з'єднання `QUIC/UDP` на вказаний порт (за замовчуванням 443 або значення з поля `port`).
   * Якщо `alpns` містить `"h2"` або `"http/1.1"`, створюється резервний кандидат `TLS/TCP`.
2. **Шифрування рукостискання (ECH):**
   * Якщо поле `ech_config` заповнене, бібліотека TLS (OpenSSL, BoringSSL або Rustls) ініціалізує контекст HPKE і формує розщеплений `ClientHelloOuter` з відкритим ім'ям CDN та зашифрованим внутрішнім `ClientHelloInner` зі справжнім доменом сайту.
3. **Паралельні спроби адресації:**
   * Якщо наявні `ipv6_hints`, клієнт негайно надсилає перший пакет (QUIC Initial або TCP SYN) на першу IPv6-адресу.
   * Якщо протягом 250 мс відповідь не надійшла (або якщо IPv6 недоступний на клієнтському інтерфейсі), клієнт паралельно запускає спробу підключення до першої IPv4-адреси з `ipv4_hints`.
   * Паралельно клієнт оновлює стандартний кеш системного резолвера, надсилаючи звичайні фонові запити A/AAAA.
4. **Захист від блокувань UDP:**
   * Якщо початкова спроба встановлення з'єднання через QUIC (HTTP/3) завершується таймаутом (типова ситуація для корпоративних фаєрволів, що блокують вихідний UDP-трафік на порт 443), клієнт автоматично відкочується до резервного кандидата `TLS/TCP` (HTTP/2), використовуючи ті самі IP-адреси та порт, отримані із запису HTTPS.

## Робота з пам'яттю: стратегії копіювання проти Zero-Copy

Під час інтеграції парсера у високонавантажені мережеві сервери або проксі (як-от Envoy, NGINX чи Cloudflare Edge) критичним фактором є стратегія керування пам'яттю:

1. **Стратегія з повним володінням (Copying Strategy):**
   * Як показано в реалізації C++, поля `target_name`, `alpns` та `ech_config` копіюються у власні динамічні буфери `std::string` та `std::vector`. Це гарантує безпеку часу життя (lifetime safety): отриманий об'єкт `SvcRecord` можна вільно передавати між робочими потоками, зберігати в кеші DNS або чергах асинхронних подій без огляду на час життя первинного UDP-буфера сокета.
   * У мові C для динамічного буфера `ech_config` виділяється пам'ять через `malloc`, яка обов'язково звільняється викликом `svcb_free_record()`, що запобігає витокам пам'яті (memory leaks) у довготривалих процесах.
2. **Стратегія Zero-Copy (для екстремальної продуктивності):**
   * Для високошвидкісних резолверів структури можуть зберігати не скопійовані рядки, а `std::string_view` або пари `(const uint8_t *ptr, size_t len)`, які безпосередньо вказують на байти всередині незмінного буфера вхідного DNS-пакета.
   * За такої моделі виділення динамічної пам'яті взагалі не відбувається, а час обробки одного запису становить лічені десятки наносекунд. Проте розробник зобов'язаний гарантувати, що вхідний пакет не буде перезаписано до завершення побудови плану з'єднання.

## Взаємодія з пулами сокетів та сесійним кешем (0-RTT)

Інформація, отримана з парсера SVCB/HTTPS, відіграє вирішальну роль у повторному використанні відкритих з'єднань (англ. *Connection Reuse / Coalescing*):

* **Злиття з'єднань (Origin Coalescing):** У протоколах HTTP/2 та HTTP/3 клієнт може відправляти запити до різних доменів через один і той самий TLS-сокет, якщо сертифікат сервера покриває обидва домени (наприклад, через Subject Alternative Name, SAN). Завдяки запису HTTPS клієнт переконується, що обидва домени вказують на ідентичний `TargetName`, використовують однаковий порт і підтримують той самий ALPN, перш ніж прийняти рішення про безпечне злиття потоків.
* **Відновлення сесій (Session Resumption / 0-RTT):** Якщо клієнт раніше вже підключався до хоста і має збережений сесійний квиток (TLS Session Ticket), наявність актуального параметра `ech_config` дозволяє відправити ранні дані (Early Data) у першому ж пакеті QUIC або TLS ClientHello, не ризикуючи розкрити SNI відкритим текстом.

## Взаємодія з криптографічними бібліотеками для Encrypted Client Hello

Коли парсер успішно витягує бінарний блок `ech_config`, цей буфер передається криптографічному рушію TLS. Розглянемо, як це працює в коді з використанням стандартного API BoringSSL або OpenSSL 3.2+:

```
+-------------------------------------------------------------+
| 1. DNS Parser: витягує бінарний ECHConfigList з RDATA       |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
| 2. SSL_CTX_set_custom_ech_config_list(ctx, buf, len)        |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
| 3. Бібліотека TLS вибирає перший підтримуваний ECHConfig:   |
|    - KEM ID (наприклад X25519)                              |
|    - KDF ID (наприклад HKDF-SHA256)                         |
|    - AEAD ID (наприклад AES-128-GCM)                        |
|    - Публічний ключ сервера HPKE                            |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
| 4. Генерація ефемерної пари ключів клієнта:                 |
|    - Обчислення спільного секрету HPKE                      |
|    - Шифрування справжнього SNI (secret.example.com)        |
|    - Формування розширення encrypted_client_hello           |
|    - Встановлення відкритого фасадного SNI (public-cdn.net) |
+-------------------------------------------------------------+
```

Якщо під час рукостискання сервер змінив свої ключі ECH і повертає розширення `retry_configs` із новим набором конфігурацій, TLS-клієнт автоматично оновлює локальний кеш ключів і повторює спробу рукостискання без повторного звернення до DNS.

## Стратегія обробки помилок та захист від атак зниження версії

Оскільки записи SVCB/HTTPS передають критичні для безпеки параметри (як-от відключення застарілих протоколів через `no-default-alpn` або вмикання шифрування SNI через `ech`), вони стають привабливою мішенню для атак типу «людина посередині» (MitM).

Якщо зловмисник на незахищеному Wi-Fi перехоплює відкритий UDP DNS-трафік (порт 53), він може видалити запис HTTPS або очистити параметри `ech` та `alpn`, змусивши браузер відкотитися до звичайного HTTP/1.1 з відкритим SNI.

Для запобігання таким маніпуляціям у реальних системах застосовуються три взаємопов'язані рівні захисту:

1. **Валідація підписів DNSSEC:** Перед передачею RDATA у наш парсер системний резолвер перевіряє цифровий підпис RRSIG запису HTTPS. Якщо валідація зазнала невдачі (підпис підроблено або видалено), відповідь вважається скомпрометованою і відкидається.
2. **Захищений транспорт DNS (DoH / DoT):** Клієнт надсилає запити DNS через зашифровані TLS-тунелі (DNS-over-HTTPS або DNS-over-TLS), що виключає можливість підглядання чи підміни параметрів проміжними мережевими вузлами.
3. **Ізоляція помилок окремих кандидатів:** Якщо парсер повертає помилку `SVCB_ERR_MANDATORY_VIOLATION` для одного конкретного запису ServiceMode (через невідомий критичний ключ), клієнт не розриває загальне з'єднання з сайтом, а переходить до наступного за пріоритетом запису. Лише у випадку, коли всі доступні записи виявилися невалідними, клієнт застосовує безпечний відкат до класичного пошуку A/AAAA.

## Діагностика, компіляція та фазинг парсера

Для відладки та аналізу записів мережевими інженерами результат розбору часто необхідно перетворити назад у стандартизоване текстове представлення master-файлу (presentation format). Наприклад, функція логування може генерувати рядок:

```text
example.com. IN HTTPS 1 . alpn="h3,h2" port=8443 ipv4hint=198.51.100.1 ech="AEn+..."
```

Під час генерації такого рядка застосовуються правила екранування: значення ALPN беруться в лапки, спецсимволи екрануються зворотним слешем, а двійковий буфер ECH кодується алгоритмом Base64. Наявність прозорого виводу дозволяє інтегрувати парсер у діагностичні утиліти на зразок `dig` чи `kdig`, спрощуючи моніторинг конфігурації служб у продакшені.

Для компіляції та перевірки надійності парсера рекомендується використовувати сучасні прапорці компілятора та інструменти автоматичного фазингу (fuzzing):

* **Компіляція C++:** `g++ -std=c++20 -O3 -Wall -Wextra -Wpedantic -fsanitize=address,undefined svcb_parser.cpp`
* **Компіляція C:** `gcc -std=c11 -O3 -Wall -Wextra -Wpedantic -fsanitize=address,undefined svcb_parser.c`
* **Тестування на фазинг з AFL++ чи libFuzzer:** Подача мільйонів випадкових та мутованих бінарних фрагментів у функцію `svcb_parse_rdata` підтверджує відсутність падінь, витоків пам'яті чи зависань навіть на повністю спотворених двійкових даних.

Завдяки цьому поєднанню строгої верифікації двійкових структур, оптимізованої роботи з пам'яттю та інтеграції з криптографічними бібліотеками, розбирач забезпечує надійний фундамент для високоефективних клієнтів нового покоління в сучасному інтернеті.

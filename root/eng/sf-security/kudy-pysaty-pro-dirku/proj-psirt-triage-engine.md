# ⚙️ Парсер та валідатор security.txt: перевірка строків і видобування контактів

Автоматизовані сканери вразливостей, системи інвентаризації активів (Attack Surface Management, ASM), інструменти аудиту ланцюга постачання та шлюзи прийому репортів PSIRT потребують надійного програмного компонента для синтаксичного аналізу файлу `security.txt` (RFC 9116). Головне інженерне завдання такого парсера — безпечно розібрати вхідний текст, виділити обов'язкові й опційні директиви, перевірити валідність цифрового підпису та переконатися, що термін придатності інформації `Expires` не минув за системним годинником.

Нижче розглянуто архітектуру парсера, правила захисного синтаксичного аналізу (Defensive Parsing), реалізації мовами C та C++, а також типові пастки розбору часових міток і захисту від атак на парсер.

---

## 1. Архітектура та етапи синтаксичного аналізу

Синтаксичний аналізатор проектується як детермінований лінійний автомат, стійкий до некоректно сформованих та зловмисних вхідних потоків даних.

```text
[ Вхідний буфер UTF-8 ]
          │
          ▼
┌─────────────────────────────────┐
│ 1. Лімітування розміру буфера   │ ──> Помилка: Розмір перевищує ліміт (DoS-захист)
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│ 2. Порядковий поділ (CRLF / LF) │
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│ 3. Фільтрація коментарів (#)    │ ──> Пропуск порожніх рядків та коментарів
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│ 4. Токенізація (Field : Value)  │ ──> Відокремлення імені директиви та значення
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│ 5. Семантична валідація         │
│    • Contact >= 1               │ ──> Перевірка обов'язкових полів
│    • Expires == 1               │ ──> Перевірка формату ISO 8601 (RFC 3339)
└─────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────┐
│ 6. Порівняння з годинником UTC  │ ──> Помилка: Строк дії файлу закінчився
└─────────────────────────────────┘
          │
          ▼
[ Структура SecurityTxt ]
```

### 1.1. Захисне синтаксичне розбиття (Defensive Parsing)

Оскільки файл `security.txt` завантажується із зовнішнього, потенційно скомпрометованого веб-сервера, парсер не має права довіряти структурі вхідних даних:
- **Обмеження пам'яті**: розмір вхідного буфера жорстко обмежується (наприклад, не більше 64 КБ). Це унеможливлює вичерпання оперативної пам'яті у разі передачі гігабайтного сміттєвого потоку.
- **Обмеження довжини рядка**: окремий рядок не повинен перевищувати 1024 символів. Якщо рядок довший, він або усікається, або генерує помилку синтаксису.
- **Нормалізація пробілів**: пробіли на початку та в кінці значень директив видаляються (Trim), однак внутрішні пробіли (наприклад, у списку мов `Preferred-Languages: uk, en`) зберігаються.

### 1.2. Контроль часової шкали та нормалізація UTC

Найбільш критичною операцією є перевірка директиви `Expires`. Специфікація RFC 9116 вимагає формату ISO 8601 / RFC 3339 у нульовому часовому поясі: `YYYY-MM-DDTHH:MM:SSZ` або з дробовими частками секунди `.000Z`.

Парсер конвертує календарну дату в абсолютний Unix-час (`time_t`) за шкалою UTC. Використання стандартної функції `mktime()` є помилкою, оскільки вона інтерпретує структуру `struct tm` у локальному часовому поясі операційної системи. Тому в стандарті POSIX застосовується функція `timegm()`, а у середовищі Windows — `_mkgmtime()`. Отримане значення порівнюється з результатом `time(NULL)`.

---

## 2. Реалізація парсера: C11 та сучасний C++20

:::tabs
@tab C (C11 / POSIX)
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <stdbool.h>

#define MAX_CONTACTS 16
#define MAX_LINE_LEN 1024

typedef struct {
    char contacts[MAX_CONTACTS][MAX_LINE_LEN];
    size_t contact_count;
    char encryption[MAX_LINE_LEN];
    char policy[MAX_LINE_LEN];
    char canonical[MAX_LINE_LEN];
    time_t expires_timestamp;
    bool has_expires;
} security_txt_t;

typedef enum {
    SEC_OK = 0,
    SEC_ERR_NO_CONTACT,
    SEC_ERR_NO_EXPIRES,
    SEC_ERR_EXPIRED,
    SEC_ERR_INVALID_DATE,
    SEC_ERR_MALFORMED
} sec_status_t;

/* Обрізання пробілів з обох боків рядка */
static char *trim_whitespace(char *str) {
    while (isspace((unsigned char)*str)) str++;
    if (*str == 0) return str;
    char *end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    end[1] = '\0';
    return str;
}

/* Парсинг ISO 8601 дати: YYYY-MM-DDTHH:MM:SS */
static bool parse_iso8601_utc(const char *date_str, time_t *out_time) {
    struct tm tm_val;
    memset(&tm_val, 0, sizeof(struct tm));

    int year, month, day, hour, min, sec;
    if (sscanf(date_str, "%4d-%2d-%2dT%2d:%2d:%2d",
               &year, &month, &day, &hour, &min, &sec) < 6) {
        return false;
    }

    tm_val.tm_year = year - 1900;
    tm_val.tm_mon  = month - 1;
    tm_val.tm_mday = day;
    tm_val.tm_hour = hour;
    tm_val.tm_min  = min;
    tm_val.tm_sec  = sec;

    /* Обчислення time_t для UTC */
#if defined(_WIN32)
    *out_time = _mkgmtime(&tm_val);
#else
    *out_time = timegm(&tm_val);
#endif
    return (*out_time != (time_t)-1);
}

/* Основна функція парсингу вмісту security.txt */
sec_status_t parse_security_txt(const char *content, security_txt_t *out_sec) {
    if (!content || !out_sec) return SEC_ERR_MALFORMED;
    memset(out_sec, 0, sizeof(security_txt_t));

    char line_buf[MAX_LINE_LEN];
    const char *ptr = content;

    while (*ptr) {
        /* Зчитування одного рядка */
        size_t len = 0;
        while (*ptr && *ptr != '\n' && *ptr != '\r' && len < MAX_LINE_LEN - 1) {
            line_buf[len++] = *ptr++;
        }
        line_buf[len] = '\0';

        /* Пропуск переведення рядків */
        while (*ptr == '\n' || *ptr == '\r') ptr++;

        char *line = trim_whitespace(line_buf);
        if (*line == '\0' || *line == '#') continue; /* Пропуск коментарів */

        char *colon = strchr(line, ':');
        if (!colon) continue;

        *colon = '\0';
        char *field = trim_whitespace(line);
        char *val   = trim_whitespace(colon + 1);

        if (strcasecmp(field, "Contact") == 0) {
            if (out_sec->contact_count < MAX_CONTACTS) {
                strncpy(out_sec->contacts[out_sec->contact_count++], val, MAX_LINE_LEN - 1);
            }
        } else if (strcasecmp(field, "Expires") == 0) {
            if (parse_iso8601_utc(val, &out_sec->expires_timestamp)) {
                out_sec->has_expires = true;
            } else {
                return SEC_ERR_INVALID_DATE;
            }
        } else if (strcasecmp(field, "Encryption") == 0) {
            strncpy(out_sec->encryption, val, MAX_LINE_LEN - 1);
        } else if (strcasecmp(field, "Policy") == 0) {
            strncpy(out_sec->policy, val, MAX_LINE_LEN - 1);
        } else if (strcasecmp(field, "Canonical") == 0) {
            strncpy(out_sec->canonical, val, MAX_LINE_LEN - 1);
        }
    }

    /* Перевірка обов'язкових полів згідно з RFC 9116 */
    if (out_sec->contact_count == 0) {
        return SEC_ERR_NO_CONTACT;
    }
    if (!out_sec->has_expires) {
        return SEC_ERR_NO_EXPIRES;
    }

    /* Перевірка строку придатності */
    time_t now = time(NULL);
    if (difftime(out_sec->expires_timestamp, now) < 0) {
        return SEC_ERR_EXPIRED;
    }

    return SEC_OK;
}
```

@tab C++ (C++20 / STL)
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <expected>
#include <algorithm>

struct SecurityTxt {
    std::vector<std::string> contacts;
    std::string encryption;
    std::string policy;
    std::string canonical;
    std::chrono::system_clock::time_point expires;
};

enum class ParseError {
    NoContactFound,
    NoExpiresFound,
    FileExpired,
    InvalidDateFormat,
    MalformedContent
};

class SecurityTxtParser {
public:
    static std::expected<SecurityTxt, ParseError> parse(std::string_view content) {
        SecurityTxt result;
        bool has_expires = false;

        std::istringstream stream{std::string(content)};
        std::string line;

        while (std::getline(stream, line)) {
            std::string_view sv = trim(line);
            if (sv.empty() || sv.starts_with('#')) {
                continue;
            }

            auto colon_pos = sv.find(':');
            if (colon_pos == std::string_view::npos) {
                continue;
            }

            auto field = trim(sv.substr(0, colon_pos));
            auto val   = trim(sv.substr(colon_pos + 1));

            if (iequals(field, "Contact")) {
                result.contacts.emplace_back(val);
            } else if (iequals(field, "Expires")) {
                auto tp = parse_rfc3339(val);
                if (!tp) {
                    return std::unexpected(ParseError::InvalidDateFormat);
                }
                result.expires = *tp;
                has_expires = true;
            } else if (iequals(field, "Encryption")) {
                result.encryption = std::string(val);
            } else if (iequals(field, "Policy")) {
                result.policy = std::string(val);
            } else if (iequals(field, "Canonical")) {
                result.canonical = std::string(val);
            }
        }

        if (result.contacts.empty()) {
            return std::unexpected(ParseError::NoContactFound);
        }
        if (!has_expires) {
            return std::unexpected(ParseError::NoExpiresFound);
        }

        const auto now = std::chrono::system_clock::now();
        if (result.expires < now) {
            return std::unexpected(ParseError::FileExpired);
        }

        return result;
    }

private:
    static std::string_view trim(std::string_view s) {
        while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) {
            s.remove_prefix(1);
        }
        while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back()))) {
            s.remove_suffix(1);
        }
        return s;
    }

    static bool iequals(std::string_view a, std::string_view b) {
        return std::ranges::equal(a, b, [](char c1, char c2) {
            return std::tolower(static_cast<unsigned char>(c1)) ==
                   std::tolower(static_cast<unsigned char>(c2));
        });
    }

    static std::optional<std::chrono::system_clock::time_point> parse_rfc3339(std::string_view date_str) {
        std::tm tm_buf{};
        std::istringstream ss{std::string(date_str)};
        ss >> std::get_time(&tm_buf, "%Y-%m-%dT%H:%M:%S");
        if (ss.fail()) {
            return std::nullopt;
        }

#if defined(_WIN32)
        std::time_t tt = _mkgmtime(&tm_buf);
#else
        std::time_t tt = timegm(&tm_buf);
#endif
        if (tt == -1) return std::nullopt;

        return std::chrono::system_clock::from_time_t(tt);
    }
};
```
:::

---

## 3. Інтеграція в автоматизований конвеєр PSIRT

У реальних виробничих середовищах представлений модуль вбудовується у фоновий сервіс обробки вхідних репортів:

1. **Мережевий клієнт (libcurl)**: завантажує `/.well-known/security.txt` через обов'язковий канал TLS з повною перевіркою валідності сертифіката X.509.
2. **Перевірка PGP-підпису**: якщо файл підписано цифровим підписом OpenPGP Cleartext, текст передається до криптографічної бібліотеки (наприклад, `GPGME` або `Botan`), яка верифікує підпис за заздалегідь імпортованим сертифікатом довіри.
3. **Автоматична маршрутизація**: видобуті адреси `Contact:` та посилання на PGP-ключ `Encryption:` зберігаються у базі даних сканера. Якщо система виявляє вразливість у хості організації, звіт автоматично зашифровується на завантажений ключ і надсилається на пріоритетну поштову адресу.

---

## 4. Валідація URL-схем та захист від SSRF

Окремим критичним аспектом безпеки є перевірка витягнутих значень полів `Contact:`, `Encryption:` та `Policy:`. Оскільки вміст `security.txt` контролюється віддаленим сервером, без належної фільтрації автоматизовані інструменти обробки ризикують стати жертвою атак класу Server-Side Request Forgery (SSRF) або ін'єкції небезпечних протоколів:

- **Перевірка дозволених схем URI**:
  - Для `Contact:` допускаються виключно схеми `mailto:`, `https:` та `tel:`. Будь-які небезпечні псевдосхеми на зразок `javascript:`, `file:///etc/passwd` або `data:` мають викликати негайне відхилення запису.
  - Для `Encryption:` та `Policy:` дозволена тільки схема `https:`.
- **Захист від внутрішнього сканування мережі (SSRF Protection)**:
  - Автоматизовані завантажувачі PGP-ключів зобов'язані резолвити доменне ім'я з URL директиви `Encryption:` і перевіряти IP-адресу перед виконанням запиту.
  - Запити до приватних діапазонів адрес IPv4 (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) та службових адрес хмарних метаданих (`169.254.169.254`) суворо блокуються на рівні мережевого сокета.

---

## 5. Аналіз типових пасток реалізації

Під час проектування та налагодження парсера інженери найчастіше стикаються з чотирма категоріями помилок:

1. **Некоректна обробка переведення рядків (CRLF проти LF)**: сервери Windows формують байти `\r\n`, тоді як Linux повертає `\n`. Якщо парсер шукає лише `\n`, байт `\r` залишається наприкінці рядка значення, спотворюючи URL або часову мітку `Expires`.
2. **Ігнорування кількох контактів**: стандарт RFC 9116 прямо дозволяє вказувати кілька адрес `Contact:`. Збереження лише одного рядка позбавляє клієнта резервних каналів зв'язку (наприклад, форми Bug Bounty у разі тимчасової недоступності поштового сервера).
3. **Обробка екранованих дефісів PGP Dash-Escaping**: якщо файл підписано PGP, будь-який рядок вихідного тексту, що починається з дефіса `-`, генератор підпису перетворює на `- - `. Якщо парсер не видаляє цей службовий префікс перед аналізом директив, такі рядки будуть проігноровані або викличуть помилку розбору.
4. **Пастка часових поясів при переході на літній час**: парсери, що використовують наївні функції перетворення часу з урахуванням локального Daylight Saving Time (DST), можуть помилятися на одну годину під час оцінки `Expires`. Лише строга робота за шкалою UTC гарантує точність порівняння.

# ⚙️ Реалізація парсера URL та кодувальника параметрів на C, C++ та Python

Парсинг URL-адрес у високонавантажених проксі-серверах, мережевих шлюзах, бібліотеках HTTP-клієнтів та мікросервісах вимагає максимальної швидкості обробки та повної відсутності динамічних алокацій пам'яті. Якщо веб-сервер обробляє понад 100 000 запитів на секунду, створення навіть одного проміжного об'єкта `std::string` на кожен розібраний компонент призводить до катастрофічної деградації продуктивності через фрагментацію купи (*heap fragmentation*) та постійні блокування в системному алокаторі.

Нижче наведено практичну реалізацію високопродуктивного нуль-алокаційного парсера URL за стандартом RFC 3986 (що оперує легковажними зрізами рядків `std::string_view` у C++ та структурами `url_view_t` у C), а також алгоритми прямого відсоткового кодування і розкодування параметрів запиту з використанням бітових операцій і таблиць швидкого пошуку.

## Архітектурні вимоги та модель пам'яті

Парсер приймає вихідний неперервний буфер пам'яті, що містить сирий рядок URL, і повертає структуру з виділеними компонентами:
1. `scheme` — протокол доступу (`https`, `http`, `git+ssh`).
2. `userinfo` — облікові дані користувача (`user:pass` перед символом `@`), якщо присутні.
3. `host` — доменне ім'я, адреса IPv4 або IPv6 у дужках `[...]`.
4. `port` — цілочисельний номер порту або `0` (якщо не вказано явно).
5. `path` — ієрархічний шлях до ресурсу від кореня (наприклад, `/v1/search`).
6. `query` — сирий рядок параметрів після `?` до `#`.
7. `fragment` — локальний якір клієнта після `#`.

Усі поля структури (крім цілочисельного порту) є безпосередніми вказівниками на байти у вихідному буфері разом із їхньою довжиною. Такий підхід гарантує повну локальність даних у кеші процесора (*L1/L2 cache locality*) та нульові витрати на копіювання пам'яті (*Zero-Copy Parsing*).

## Реалізація парсера URL за RFC 3986

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

/* Зріз рядка без копіювання пам'яті */
typedef struct {
    const char *ptr;
    size_t len;
} url_view_t;

typedef struct {
    url_view_t scheme;
    url_view_t userinfo;
    url_view_t host;
    int port;
    url_view_t path;
    url_view_t query;
    url_view_t fragment;
} parsed_url_t;

/* Друк зрізу рядка у стандартний вивід */
void print_view(const char *label, url_view_t v) {
    printf("%-10s: %.*s\n", label, (int)v.len, v.ptr ? v.ptr : "");
}

/* Розбір URL на компоненти за RFC 3986 */
bool parse_url(const char *raw, size_t len, parsed_url_t *out) {
    if (!raw || !out) return false;
    memset(out, 0, sizeof(*out));

    const char *cur = raw;
    const char *end = raw + len;

    /* 1. Пошук схеми: починається з букви, завершується ':' */
    const char *colon = memchr(cur, ':', end - cur);
    if (colon && colon != cur) {
        /* Перевіряємо, чи немає перед ':' символів '/', '?', '#' */
        const char *p = cur;
        bool valid_scheme = isalpha((unsigned char)*p);
        p++;
        while (p < colon && valid_scheme) {
            char c = *p++;
            if (!isalnum((unsigned char)c) && c != '+' && c != '-' && c != '.') {
                valid_scheme = false;
            }
        }
        if (valid_scheme) {
            out->scheme.ptr = cur;
            out->scheme.len = colon - cur;
            cur = colon + 1;
        }
    }

    /* 2. Пошук Authority: починається з "//" */
    if (cur + 1 < end && cur[0] == '/' && cur[1] == '/') {
        cur += 2;
        const char *auth_start = cur;
        const char *auth_end = cur;
        while (auth_end < end && *auth_end != '/' && *auth_end != '?' && *auth_end != '#') {
            auth_end++;
        }

        /* Пошук userinfo за '@' */
        const char *at = memchr(auth_start, '@', auth_end - auth_start);
        const char *host_start = auth_start;
        if (at) {
            out->userinfo.ptr = auth_start;
            out->userinfo.len = at - auth_start;
            host_start = at + 1;
        }

        /* Пошук host і port (враховуючи IPv6 [::1]) */
        const char *host_end = auth_end;
        if (host_start < auth_end && *host_start == '[') {
            /* IPv6 адреса */
            const char *bracket_close = memchr(host_start, ']', auth_end - host_start);
            if (bracket_close) {
                host_end = bracket_close + 1;
                out->host.ptr = host_start;
                out->host.len = host_end - host_start;
                if (host_end < auth_end && *host_end == ':') {
                    out->port = atoi(host_end + 1);
                }
            } else {
                return false; /* Некоректний IPv6 */
            }
        } else {
            /* Звичайний хост (DNS або IPv4) */
            const char *port_colon = memchr(host_start, ':', auth_end - host_start);
            if (port_colon) {
                out->host.ptr = host_start;
                out->host.len = port_colon - host_start;
                out->port = atoi(port_colon + 1);
            } else {
                out->host.ptr = host_start;
                out->host.len = auth_end - host_start;
            }
        }
        cur = auth_end;
    }

    /* 3. Пошук Path (до '?' або '#') */
    const char *path_start = cur;
    while (cur < end && *cur != '?' && *cur != '#') {
        cur++;
    }
    out->path.ptr = path_start;
    out->path.len = cur - path_start;

    /* 4. Пошук Query (після '?') */
    if (cur < end && *cur == '?') {
        cur++;
        const char *query_start = cur;
        while (cur < end && *cur != '#') {
            cur++;
        }
        out->query.ptr = query_start;
        out->query.len = cur - query_start;
    }

    /* 5. Пошук Fragment (після '#') */
    if (cur < end && *cur == '#') {
        cur++;
        out->fragment.ptr = cur;
        out->fragment.len = end - cur;
    }

    return true;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <optional>
#include <string>
#include <cctype>
#include <charconv>

struct ParsedUrl {
    std::string_view scheme;
    std::string_view userinfo;
    std::string_view host;
    int port{0};
    std::string_view path;
    std::string_view query;
    std::string_view fragment;
};

class UrlParser {
public:
    static std::optional<ParsedUrl> parse(std::string_view raw) noexcept {
        ParsedUrl url;
        std::string_view cur = raw;

        // 1. Схема
        if (auto colon = cur.find(':'); colon != std::string_view::npos) {
            auto candidate = cur.substr(0, colon);
            if (is_valid_scheme(candidate)) {
                url.scheme = candidate;
                cur.remove_prefix(colon + 1);
            }
        }

        // 2. Authority
        if (cur.starts_with("//")) {
            cur.remove_prefix(2);
            auto auth_end = cur.find_first_of("/?#");
            auto auth = (auth_end == std::string_view::npos) ? cur : cur.substr(0, auth_end);

            if (auto at = auth.find('@'); at != std::string_view::npos) {
                url.userinfo = auth.substr(0, at);
                auth.remove_prefix(at + 1);
            }

            // Host і Port
            if (auth.starts_with('[')) {
                // IPv6
                auto close_bracket = auth.find(']');
                if (close_bracket == std::string_view::npos) return std::nullopt;
                url.host = auth.substr(0, close_bracket + 1);
                auto after_host = auth.substr(close_bracket + 1);
                if (after_host.starts_with(':')) {
                    after_host.remove_prefix(1);
                    std::from_chars(after_host.data(), after_host.data() + after_host.size(), url.port);
                }
            } else {
                if (auto port_colon = auth.find(':'); port_colon != std::string_view::npos) {
                    url.host = auth.substr(0, port_colon);
                    auto port_str = auth.substr(port_colon + 1);
                    std::from_chars(port_str.data(), port_str.data() + port_str.size(), url.port);
                } else {
                    url.host = auth;
                }
            }

            cur = (auth_end == std::string_view::npos) ? std::string_view{} : cur.substr(auth_end);
        }

        // 3. Path
        auto path_end = cur.find_first_of("?#");
        url.path = (path_end == std::string_view::npos) ? cur : cur.substr(0, path_end);
        cur = (path_end == std::string_view::npos) ? std::string_view{} : cur.substr(path_end);

        // 4. Query
        if (cur.starts_with('?')) {
            cur.remove_prefix(1);
            auto query_end = cur.find('#');
            url.query = (query_end == std::string_view::npos) ? cur : cur.substr(0, query_end);
            cur = (query_end == std::string_view::npos) ? std::string_view{} : cur.substr(query_end);
        }

        // 5. Fragment
        if (cur.starts_with('#')) {
            url.fragment = cur.substr(1);
        }

        return url;
    }

private:
    static bool is_valid_scheme(std::string_view s) noexcept {
        if (s.empty() || !std::isalpha(static_cast<unsigned char>(s.front()))) return false;
        for (char c : s) {
            if (!std::isalnum(static_cast<unsigned char>(c)) && c != '+' && c != '-' && c != '.') {
                return false;
            }
        }
        return true;
    }
};
```
```py
import urllib.parse
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedUrlPy:
    scheme: str
    userinfo: Optional[str]
    host: str
    port: Optional[int]
    path: str
    query: str
    fragment: str

def parse_url_rfc3986(url_str: str) -> ParsedUrlPy:
    """Розбір URL за допомогою urllib.parse.urlsplit з виділенням компонентів."""
    res = urllib.parse.urlsplit(url_str)
    
    userinfo = None
    if res.username:
        userinfo = res.username
        if res.password:
            userinfo += f":{res.password}"
            
    return ParsedUrlPy(
        scheme=res.scheme,
        userinfo=userinfo,
        host=res.hostname or "",
        port=res.port,
        path=res.path,
        query=res.query,
        fragment=res.fragment
    )
```
:::

## Логіка роботи станів парсера

У наведених реалізаціях розбір адреси здійснюється послідовно через перевірку інваріантів граматики RFC 3986:

1. **Схема (Scheme):** перевіряється наявність першої двокрапки `:`. Якщо перед двокрапкою відсутні заборонені символи (`/`, `?`, `#`), а перший символ є латинською буквою, підрядок до двокрапки фіксується як схема. Перевірка символів виконується циклом без виклику важких регулярних виразів.
2. **Орган повноважень (Authority):** маркується наявністю послідовності `//`. Внутрішній розбір відокремлює облікові дані за символом `@`. Для виділення хоста перевіряється, чи починається підрядок із символу `[`. Якщо так, парсер ізолює блок до парної `]` як адресу IPv6, а наступна двокрапка розглядається як початок номера порту. У C++ для конвертації порту використовується `std::from_chars` — функція, що не залежить від системної локалі, не генерує винятків і працює значно швидше за `atoi` чи `std::stoi`.
3. **Шлях, запит і фрагмент:** виділяються пошуком перших входжень символів-роздільників `?` та `#`. Оскільки зрізи пам'яті лише фіксують зміщення (*offsets*) всередині буфера, час виконання цієї частини лінійно залежить лише від довжини рядка `O(N)`.

## Відсоткове кодування (Percent-Encoding) та розкодування

Під час кодування параметрів запиту критично важливо уникати повільних викликів форматованого виводу типу `sprintf(buf, "%%%02X", byte)`. 

Замість цього застосовуються швидкі бітові операції:
- Старший півбайт (*high nibble*): `c >> 4` як індекс у константній таблиці `"0123456789ABCDEF"`.
- Молодший півбайт (*low nibble*): `c & 0x0F` як індекс у тій самій таблиці.

Це скорочує час кодування одного байта до кількох машинних інструкцій без розгалужень процесорного конвеєра.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

static inline bool is_unreserved(unsigned char c) {
    return (c >= 'A' && c <= 'Z') ||
           (c >= 'a' && c <= 'z') ||
           (c >= '0' && c <= '9') ||
           c == '-' || c == '.' || c == '_' || c == '~';
}

/* Відсоткове кодування рядка за RFC 3986 у вихідний буфер */
size_t url_encode(const char *src, size_t src_len, char *dst, size_t dst_len) {
    static const char hex[] = "0123456789ABCDEF";
    size_t written = 0;

    for (size_t i = 0; i < src_len; i++) {
        unsigned char c = (unsigned char)src[i];
        if (is_unreserved(c)) {
            if (written + 1 >= dst_len) return 0;
            dst[written++] = c;
        } else {
            if (written + 3 >= dst_len) return 0;
            dst[written++] = '%';
            dst[written++] = hex[c >> 4];
            dst[written++] = hex[c & 0x0F];
        }
    }
    if (written < dst_len) dst[written] = '\0';
    return written;
}

static inline int hex_val(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

/* Розкодування відсоткових послідовностей %HH */
size_t url_decode(const char *src, size_t src_len, char *dst, size_t dst_len) {
    size_t written = 0;
    for (size_t i = 0; i < src_len; i++) {
        if (src[i] == '%' && i + 2 < src_len) {
            int h1 = hex_val(src[i + 1]);
            int h2 = hex_val(src[i + 2]);
            if (h1 != -1 && h2 != -1) {
                if (written + 1 >= dst_len) return 0;
                dst[written++] = (char)((h1 << 4) | h2);
                i += 2;
                continue;
            }
        }
        if (written + 1 >= dst_len) return 0;
        dst[written++] = src[i];
    }
    if (written < dst_len) dst[written] = '\0';
    return written;
}
```
```cpp
#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <cctype>

class UrlCodec {
public:
    static bool is_unreserved(unsigned char c) noexcept {
        return (c >= 'A' && c <= 'Z') ||
               (c >= 'a' && c <= 'z') ||
               (c >= '0' && c <= '9') ||
               c == '-' || c == '.' || c == '_' || c == '~';
    }

    static std::string encode(std::string_view src) {
        static constexpr char hex[] = "0123456789ABCDEF";
        std::string dst;
        dst.reserve(src.size() * 3);

        for (unsigned char c : src) {
            if (is_unreserved(c)) {
                dst.push_back(static_cast<char>(c));
            } else {
                dst.push_back('%');
                dst.push_back(hex[c >> 4]);
                dst.push_back(hex[c & 0x0F]);
            }
        }
        return dst;
    }

    static std::string decode(std::string_view src) {
        std::string dst;
        dst.reserve(src.size());

        for (size_t i = 0; i < src.size(); ++i) {
            if (src[i] == '%' && i + 2 < src.size()) {
                auto hex_to_int = [](char h) -> int {
                    if (h >= '0' && h <= '9') return h - '0';
                    if (h >= 'A' && h <= 'F') return h - 'A' + 10;
                    if (h >= 'a' && h <= 'f') return h - 'a' + 10;
                    return -1;
                };

                int h1 = hex_to_int(src[i + 1]);
                int h2 = hex_to_int(src[i + 2]);
                if (h1 != -1 && h2 != -1) {
                    dst.push_back(static_cast<char>((h1 << 4) | h2));
                    i += 2;
                    continue;
                }
            }
            dst.push_back(src[i]);
        }
        return dst;
    }
};
```
```py
import urllib.parse

def encode_query_params(params: dict[str, str], form_mode: bool = False) -> str:
    """
    Кодує словник параметрів у query string.
    form_mode=True: пробіл стає '+', як у application/x-www-form-urlencoded.
    form_mode=False: пробіл стає '%20' за стандартом RFC 3986.
    """
    if form_mode:
        return urllib.parse.urlencode(params)
    return urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

def decode_query_param(val: str, form_mode: bool = False) -> str:
    """Розкодовує значення параметра запиту."""
    if form_mode:
        return urllib.parse.unquote_plus(val)
    return urllib.parse.unquote(val)
```
:::

## Інженерні пастки та захист від атак

Під час практичної експлуатації парсерів та кодувальників URL розробники стикаються з трьома критичними крайовими випадками:

1. **Неповні або пошкоджені шістнадцяткові послідовності:**
   Якщо рядок користувача раптово обривається на символах `%` або `%A` (наприклад, `search=100%`), некоректно написаний декодер на мові C ризикує прочитати пам'ять за межами виділеного буфера (`Buffer Over-read`), що веде до збою процесу (*Segmentation Fault*) або витоку конфіденційної інформації. У наведеній C/C++ реалізації умова `i + 2 < src_len` повністю блокує вихід за межі буфера: якщо після відсотка бракує двох дійсних шістнадцяткових символів, символ `%` безпечно копіюється як звичайний літерал.
2. **Впровадження нульових байтів (`%00`):**
   Якщо декодований рядок містить бінарний нуль, використання класичних функцій C-рядків (`strlen`, `strcpy`) призведе до передчасного усічення рядка, що відкриває можливість обходу фільтрів розширень файлів. Використання довжинних зрізів `url_view_t` та `std::string_view` гарантує збереження повного розміру буфера навіть за наявності вбудованих нулів.
3. **Невалідні послідовності UTF-8:**
   Відсоткове кодування оперує окремими байтами. Якщо вхідний рядок містить розірвані багатобайтові послідовності Юнікоду (наприклад, старший байт `0xD0` без супровідного молодшого байта), декодер поверне некоректний бінарний потік. У високонадійних веб-серверах після етапу `url_decode` обов'язково викликається швидкий валідатор UTF-8 (наприклад, на базі SIMD-інструкцій), що перевіряє цілісність текстових даних перед їх передачею в бізнес-логіку програми.

## Оптимізація розкодування на місці (In-Place Decoding)

Важливою математичною властивістю відсоткового розкодування є те, що вихідний рядок **завжди коротший або рівний** за довжиною вхідному рядку (три символи `%HH` згортаються в один байт, а незакодовані символи зберігають довжину 1:1).

Це дозволяє виконувати розкодування **безпосередньо в тому самому буфері пам'яті** (*In-Place Decoding*) без виділення додаткового вихідного масиву:

```text
Вхідний масив:  ['a', '%', '2', '0', 'b', '\0']
Читач (r):       крокує по вихідному масиву (r = 0..4)
Писач (w):       записує розкодовані байти (w <= r)
Результат:      ['a', ' ', 'b', '\0'] (довжина w = 3)
```

Оскільки показчик запису `w` ніколи не випереджає покажчик читання `r`, алгоритм є абсолютно безпечним і не перезаписує ще не прочитані байти. У мережевих шлюзах такий прийом дозволяє модифікувати заголовки та шляхи безпосередньо у сокетному буфері ядра операційної системи.

## Векторизація SIMD для обробки мільйонів адрес

У сучасних бібліотеках (наприклад, `simdurl` або `ada-url`) розбір URL прискорюють за допомогою векторних інструкцій процесора AVX-2 та ARM NEON. Замість побайтового читання алгоритм завантажує 16 або 32 байти одночасно у векторний регістр і за одну інструкцію порівнює маску символів із таблицею роздільників (`/`, `?`, `#`, `:`). Це дозволяє знаходити межі компонентів на швидкостях до 2–4 гігабайт на секунду на одне процесорне ядро.

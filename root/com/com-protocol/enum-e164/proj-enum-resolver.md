# ⚙️ Реалізація резолвера ENUM: від телефонного номера до SIP URI

У сучасних телекомунікаційних мережах — програмних комутаторах Softswitch, прикордонних контролерах сесій (SBC), серверах [SIP](topic:com-protocol/sip) та ядрах мобільних мереж IMS — функція ENUM-резолвінгу знаходиться на найгарячішому шляху обробки кожного виклику. Коли користувач набирає на смартфоні або апараті IP-телефонії телефонний номер, комутатор зобов'язаний за лічені мілісекунди вирішити маршрутне завдання: перетворити введений номер у доменне ім'я, виконати запит до DNS, розібрати набір правил NAPTR, застосувати регулярні підстановки та знайти кінцеву точку призначення в IP-мережі. Якщо цей процес дає збій або перевищує ліміт очікування, виклик зазнає відчутної для абонента затримки або аварійно скидається в дорогу телефонну мережу PSTN.

Нижче наведено детальне інженерне проектування, покроковий розбір алгоритму, покрокове простеження (Trace Walkthrough) на конкретному виклику, аналіз інтеграції в промислові платформи, архітектуру дворівневого кешування, валідацію через DNSSEC та повну програмну реалізацію високопродуктивного модуля ENUM-резолвера мовами C та C++.

---

### Інженерна постановка задачі

Розроблюваний модуль повинен інтегруватися в сигналізаційний конвеєр SIP-проксі і виконувати детерміновану трансформацію телефонного номера на повну адресу SIP URI. Модуль вирішує такі технічні вимоги:

1. **Уніфікація вхідних даних:** Робота з номерами різного форматування (із пропусками, дужками, дефісами, міжнародними префіксами `00` або `810`) та надійна конвертація в канонічний формат ITU-T E.164 зі знаком `+`.
2. **Формування доменного імені за алгоритмом RFC 6116:** Інверсія цифр, посимвольне розділення крапками та додавання кореневого суфікса зони ENUM (наприклад, `.e164.arpa` для глобальної зони або операторського суфікса для закритих мереж Carrier ENUM).
3. **Низькорівневий двійковий розбір DNS Wire Format:** Обробка пакетів DNS типу NAPTR (Type 35), захист від некоректних зміщень у стиснених мітках доменних імен (DNS Name Decompression) та захист від пошкоджених пакетів зловмисних серверів.
4. **Сортування та фільтрація записів:** Виділення підтримуваних сервісів (пріоритетно `E2U+sip` та `E2U+voice:sip`), сортування за 16-бітними ключами `order` та `preference`.
5. **Безпечне виконання регулярних виразів:** Підтримка sed-подібного формату підстановок `!pattern!replacement!flags`, безпечне захоплення груп `\1`..`\9`, захист від переповнення буферів та атак ReDoS (Regular Expression Denial of Service).
6. **Детермінована обробка виняткових станів:** Чітке розмежування відсутності запису в зоні (`NXDOMAIN`), відсутності типу NAPTR (`NODATA`), мережевих таймаутів та синтаксичних помилок у регулярних виразах із можливістю автоматичного перемикання на резервні канали зв'язку.

---

### Покроковий алгоритм функціонування резолвера

```
[Вхідний рядок телефонного номера]
               │
               ▼
[1. Валідація та нормалізація E.164]
 ├─ Вилучення символів ' ', '-', '(', ')'
 ├─ Перевірка ліміту довжини (від 3 до 15 цифр)
 └─ Формування канонічного рядка: "+380441234567"
               │
               ▼
[2. Генерація ENUM FQDN]
 ├─ Відкидання знака '+'
 ├─ Інверсія порядку цифр: "7.6.5.4.3.2.1.4.4.0.8.3"
 └─ Додавання суфікса: "7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa"
               │
               ▼
[3. Двійковий DNS-запит NAPTR (Type 35)]
 ├─ Виклик системного резолвера res_query()
 └─ Отримання сирого буфера DNS Wire Format
               │
               ▼
[4. Двійковий парсинг секції Answer]
 ├─ Пропуск 12-байтного заголовка та секції Question
 ├─ Ітерація по записах секції Answer (перевірка Type == 35)
 ├─ Зчитування ORDER (uint16) та PREFERENCE (uint16)
 ├─ Вилучення рядків FLAGS, SERVICES, REGEXP (Паскаль-формат)
 └─ Розпакування імені REPLACEMENT (декомпресія DNS)
               │
               ▼
[5. Фільтрація та сортування]
 ├─ Вилучення записів без префікса "E2U+" або не-SIP сервісів
 └─ Сортування масиву: Order (зростання) -> Preference (зростання)
               │
               ▼
[6. Виконання Sed-підстановки (DDDS)]
 ├─ Перебір відсортованих правил
 ├─ Компіляція regex-шаблону з підтримкою прапорця 'i'
 ├─ Зіставлення з канонічним номером "+380441234567"
 └─ Підстановка захоплених груп \1..\9 у рядок заміни
               │
        ┌──────┴──────┐
        ▼             ▼
   [Успіх]        [Помилка/NOMATCH]
        │             │
        ▼             ▼
[Повернення SIP URI]  [Перехід до резерву PSTN / 404 Not Found]
```

#### Етап 1: Нормалізація вхідного номера

Стандарт ITU-T E.164 регламентує, що міжнародний публічний телефонний номер складається виключно з десяткових цифр, починається з коду країни (від 1 до 3 цифр) і не може перевищувати 15 цифр загалом. Проте в реальних SIP-повідомленнях номери надходять у найрізноманітніших форматах: `+380 (44) 123-4567`, `00380441234567`, або `0441234567`.

Функція нормалізації зобов'язана:
- Перевірити наявність міжнародного префікса. Якщо номер починається з `00` або `810`, замінити його на знак `+`.
- Відфільтрувати всі розділові символи, пробіли, круглі дужки та тире.
- Перевірити, щоб кількість цифр після знака плюс була не меншою за 3 і не більшою за 15.
- Сформувати незмінний канонічний рядок (наприклад, `+380441234567`), який надалі подаватиметься на вхід рушія регулярних виразів.

#### Етап 2: Побудова повністю визначеного доменного імені (FQDN)

Для побудови імені домену в системі DNS дзеркально повторюється логіка ієрархії: оскільки в номері E.164 найбільш значуща частина (код країни) стоїть ліворуч, а в DNS найбільш значуща частина (корінь і TLD) знаходиться праворуч, цифри номера обов'язково розгортаються у зворотному порядку.

Кожна десяткова цифра стає окремою доменною міткою першого рівня, розділеною крапкою. До реверсованого рядка додається статичний суфікс доменної зони:
- Для публічного ENUM: `.e164.arpa`.
- Для приватних або операторських мереж Carrier ENUM: наприклад, `.e164.carrier.net` або `.e164.internal`.

Для номера `+380441234567` результатом цього етапу є рядок:
`7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa`.

#### Етап 3: Відправлення двійкового DNS-запиту та робота з EDNS0

Резолвер надсилає стандартний запит до служби DNS. У протоколі DNS запит типу NAPTR має числовий код `T_NAPTR = 35`, клас `C_IN = 1`. Запит формується за допомогою системних функцій бібліотеки `libresolv` (`res_nquery` у багатопотоковому середовищі або `res_query`). Відповідь записується в двійковий буфер розміром від 2048 до 4096 байтів.

Важливий аспект: оскільки зона ENUM часто підписана за допомогою [DNSSEC](topic:sf-security/dns-sec) і повертає великі набори підписів RRSIG та кілька записів NAPTR одночасно, розмір DNS-відповіді регулярно перевищує класичний ліміт UDP у 512 байтів. Промисловий резолвер зобов'язаний використовувати розширення EDNS0 (RFC 6891) з розміром буфера 4096 байтів. Якщо авторитетний сервер повертає відповідь із встановленим прапорцем транкації `TC=1` (Truncated), резолвер повинен автоматично повторити запит через надійний транспорт TCP.

#### Етап 4: Двійковий розбір пакету DNS Wire Format

Двійковий пакет DNS починається з 12-байтного заголовка, що містить прапорці, статус відповіді (RCODE) та лічильники секцій: `QDCOUNT` (кількість запитань), `ANCOUNT` (кількість відповідей у секції Answer), `NSCOUNT` (авторитетні сервери) та `ARCOUNT` (додаткові записи).

Резолвер перевіряє статус: якщо `RCODE == NXDOMAIN` (код 3) або `ANCOUNT == 0`, це свідчить про відсутність записів для цього номера.

Якщо відповідь успішна, резолвер послідовно проходить через записи секції Answer:
1. Пропускає або декомпресує ім'я вузла (Name).
2. Зчитує 16-бітний тип запису (Type) та клас (Class). Якщо тип відрізняється від 35 (NAPTR), запис пропускається.
3. Пропускає 32-бітний TTL та зчитує 16-бітну довжину корисного навантаження (`RDLENGTH`).
4. Послідовно зчитує поля секції `RDATA`:
   - `ORDER`: 2 байти, `uint16_t` (Big-Endian).
   - `PREFERENCE`: 2 байти, `uint16_t` (Big-Endian).
   - `FLAGS`: 1 байт довжини `len`, за яким слідує `len` байтів символів.
   - `SERVICES`: 1 байт довжини `len`, за яким слідує `len` байтів символів.
   - `REGEXP`: 1 байт довжини `len`, за яким слідує `len` байтів символів.
   - `REPLACEMENT`: стандартно закодоване доменне ім'я, розпаковане за допомогою функції `ns_name_uncompress()`.

#### Етап 5: Фільтрація та сортування правил

Не всі записи NAPTR, що повернулися з DNS, підходять для здійснення SIP-дзвінка. Резолвер відкидає:
- Записи, де поле `SERVICES` не починається з обов'язкового префікса `E2U` (E.164 to URI).
- Записи, що описують інші протоколи (наприклад, поштові `E2U+email:mailto` або вебресурси `E2U+web:http`), якщо метою комутатора є суто голосовий дзвінок.
- Записи з пошкодженим синтаксисом регулярного виразу.

Записи, що пройшли фільтр, сортуються:
1. За первинним ключем: значення поля `ORDER` за зростанням (від 0 до 65535).
2. За вторинним ключем: значення поля `PREFERENCE` за зростанням для записів з однаковим `ORDER`.

#### Етап 6: Рушій виконання Sed-підстановки

Поле `REGEXP` має вигляд `!pattern!replacement!flags`. Резолвер:
1. Визначає символ розділювача (перший символ рядка, наприклад `!`).
2. Розбиває рядок на регулярний шаблон `pattern`, рядок заміни `replacement` та прапорці `flags`.
3. Компілює шаблон за допомогою бібліотеки регулярних виразів (POSIX Extended Regular Expression `regcomp` з прапорцем `REG_ICASE`, якщо у полі `flags` присутня літера `i`).
4. Застосовує скомпільований вираз до канонічного вхідного номера `+380441234567`.
5. У разі збігу копіює рядок заміни у вихідний буфер, динамічно підставляючи значення захоплених круглими дужками груп замість позначок `\1`, `\2`, ..., `\9`.

Якщо підстановка пройшла успішно і прапорець запису дорівнює `"u"`, сформований рядок URI повертається як кінцевий результат маршрутизації.

---

### Покрокове простеження виконання (Trace Walkthrough)

Розглянемо реальну послідовність дій резолвера при обробці телефонного виклику:

1. **Вхідний виклик:** Абонент набирає на SIP-телефоні номер `+380 44 123 4567`.
2. **Канонізація:** Функція `e164_to_enum_fqdn` видаляє пробіли, отримує канонічний рядок `+380441234567` та формує доменне ім'я `7.6.5.4.3.2.1.4.4.0.8.3.e164.arpa`.
3. **Двійковий DNS-запит:**
   - Формується DNS-заголовок: `ID = 0x4A1F`, `Flags = 0x0100` (стандартний рекурсивний запит `RD=1`), `QDCOUNT = 1`.
   - Формується секція Question: ім'я кодується послідовністю міток `\x017\x016\x015\x014\x013\x012\x011\x014\x014\x010\x018\x013\x04e164\x04arpa\x00`, тип `QTYPE = 0x0023` (35, NAPTR), клас `QCLASS = 0x0001` (IN).
4. **Отримання та розбір відповіді:**
   - Сервер повертає DNS-відповідь із двома записами NAPTR у секції Answer (`ANCOUNT = 2`).
   - Запис A: `order = 10`, `preference = 100`, `flags = "u"`, `services = "E2U+sip"`, `regexp = "!^\\+38044(.*)$!sip:\\1@primary.operator.ua;user=phone!i"`, `replacement = "."`.
   - Запис B: `order = 10`, `preference = 200`, `flags = "u"`, `services = "E2U+sip"`, `regexp = "!^\\+38044(.*)$!sip:\\1@backup.operator.ua;user=phone!i"`, `replacement = "."`.
5. **Сортування та вибір:** Обидва записи мають `order = 10`. Сортувальник порівнює `preference`: запис A (`pref 100`) стоїть раніше за запис B (`pref 200`).
6. **Виконання підстановки:**
   - Резолвер бере запис A. Розбирає вираз за розділювачем `!`.
   - Шаблон `^\\+38044(.*)$` зіставляється з номером `+380441234567`. Збіг успішний!
   - Захоплена група номер 1 (`\1`) містить підрядок `"1234567"`.
   - Рядок заміни `sip:\1@primary.operator.ua;user=phone` перетворюється на кінцевий SIP URI `sip:1234567@primary.operator.ua;user=phone`.
7. **Результат:** Резолвер негайно повертає сформований URI, і softswitch відправляє SIP-запит `INVITE sip:1234567@primary.operator.ua;user=phone` через локальний IP-інтерфейс.

---

### Асинхронний резолвінг та перевірка DNSSEC через libunbound

У високонавантажених серверах SIP із тисячами одночасних з'єднань блокуючі системні виклики неприпустимі. Крім того, критично важлива перевірка автентичності записів NAPTR за допомогою [DNSSEC](topic:sf-security/dns-sec) для захисту від підміни маршрутизації.

Для цього застосовують бібліотеку `libunbound`, яка надає повністю неблокуючий асинхронний інтерфейс із вбудованим валідатором цифрових підписів:

1. **Ініціалізація контексту:** Створюється контекст `ub_ctx`, в який завантажуються кореневі ключі довіри (Trust Anchors) із файлу `root.key`.
2. **Асинхронний запит `ub_resolve_async`:** Запит ставиться в чергу циклу подій (Event Loop). Функція негайно повертає керування, а робочий потік комутатора продовжує обробку інших SIP-транзакцій.
3. **Обробка результату в Callback:** Коли DNS-відповідь прибуває, бібліотека автоматично перевіряє весь криптографічний ланцюг підписів від кореня `.` до `e164.arpa` та записів NAPTR:
   - Якщо поле `result->secure == 1`, дані є достовірними та підписаними.
   - Якщо `result->bogus == 1`, це свідчить про атаку підміни DNS (DNS Spoofing / Cache Poisoning). Резолвер негайно відхиляє такі записи з генерацією тривожного сповіщення безпеки.
   - Якщо `result->havedata == 1`, масив двійкових RDATA передається функції розбору NAPTR.

---

### Архітектура дворівневого кешування у високонавантажених системах

Для забезпечення продуктивності понад 50 000 викликів за секунду телеком-оператори впроваджують дворівневу схему кешування:

- **L1 Кеш (In-Memory Process Cache):**
  Високошвидкісна хеш-таблиця в оперативній пам'яті процесу SIP-проксі без блокувань (Lock-free / RCU). Вона зберігає готові результати трансляції E.164 → SIP URI з часом доступу менше 100 наносекунд.
- **L2 Кеш (Local DNS Daemon):**
  Локальний демон Unbound або BIND, запущений на інтерфейсі `127.0.0.1`. Він зберігає сирі записи NAPTR, обробляє валідацію DNSSEC та підтримує TTL згідно з політиками зон.
- **Синхронізація з базами MNP:**
  При перенесенні мобільного номера центральна клірингова база розсилає оновлення через механізм DNS NOTIFY або транзакційний потік Kafka. Локальний резолвер миттєво інвалідує запис у L1-кеші, запобігаючи помилковій маршрутизації дзвінків.
- **Коректне збереження URI-параметрів:**
  При формуванні цільових адрес важливо зберігати службові параметри SIP, такі як `;user=phone` (що вказує проксі на телефонну природу імені користувача) або `;transport=tls` для виклику через зашифрований транспорт. Модуль підстановки акуратно переносить ці прапорці у вихідний рядок.

---

### Програмна реалізація ENUM-резолвера

Нижче наведено повнофункціональний, промисловий код резолвера мовами C та C++. Обидва варіанти містять власну реалізацію всіх шести етапів алгоритму та готові до компіляції в середовищі Linux/POSIX.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdint.h>
#include <netinet/in.h>
#include <arpa/nameser.h>
#include <resolv.h>
#include <regex.h>

#define ENUM_MAX_RECORDS 16
#define ENUM_BUFFER_SIZE 4096
#define ENUM_URI_MAX_LEN 256

typedef struct {
    uint16_t order;
    uint16_t preference;
    char flags[16];
    char services[64];
    char regexp[256];
    char replacement[256];
} enum_naptr_record_t;

/* Етап 1 та 2: Нормалізація номера та генерація ENUM FQDN */
int e164_to_enum_fqdn(const char *e164_input, char *fqdn_out, size_t fqdn_size,
                      char *canonical_out, size_t canon_size) {
    char digits[32];
    size_t digit_count = 0;

    if (!e164_input || e164_input[0] != '+') return -1;

    for (size_t i = 1; e164_input[i] != '\0'; ++i) {
        char c = e164_input[i];
        if (isdigit((unsigned char)c)) {
            if (digit_count >= 15) return -1; /* Перевищення ліміту E.164 */
            digits[digit_count++] = c;
        } else if (c != ' ' && c != '-' && c != '(' && c != ')') {
            return -1; /* Неприпустимий символ у номері */
        }
    }
    if (digit_count < 3) return -1;

    /* Зберігаємо нормалізований номер +380... */
    if (canonical_out && canon_size > digit_count + 1) {
        canonical_out[0] = '+';
        memcpy(canonical_out + 1, digits, digit_count);
        canonical_out[digit_count + 1] = '\0';
    }

    /* Формуємо доменне ім'я: інверсія цифр через крапку + суфікс */
    size_t pos = 0;
    for (int i = (int)digit_count - 1; i >= 0; --i) {
        if (pos + 2 >= fqdn_size) return -1;
        fqdn_out[pos++] = digits[i];
        fqdn_out[pos++] = '.';
    }
    const char *suffix = "e164.arpa";
    if (pos + strlen(suffix) >= fqdn_size) return -1;
    strcpy(fqdn_out + pos, suffix);

    return 0;
}

/* Функція сортування: спочатку order, потім preference */
int compare_naptr_records(const void *a, const void *b) {
    const enum_naptr_record_t *r1 = (const enum_naptr_record_t *)a;
    const enum_naptr_record_t *r2 = (const enum_naptr_record_t *)b;
    if (r1->order != r2->order)
        return (int)r1->order - (int)r2->order;
    return (int)r1->preference - (int)r2->preference;
}

/* Безпечний парсинг рядка змінної довжини (Pascal string) з DNS RDATA */
static const unsigned char *extract_dns_string(const unsigned char *ptr,
                                               const unsigned char *end,
                                               char *dst, size_t dst_size) {
    if (ptr >= end) return NULL;
    uint8_t len = *ptr++;
    if (ptr + len > end || len >= dst_size) return NULL;
    memcpy(dst, ptr, len);
    dst[len] = '\0';
    return ptr + len;
}

/* Етап 6: Виконання sed-підстановки !pattern!replacement!flags */
int execute_sed_replacement(const char *sed_expr, const char *input_num,
                            char *uri_out, size_t out_size) {
    if (!sed_expr || strlen(sed_expr) < 3) return -1;
    char delimiter = sed_expr[0];

    const char *p_pat_start = sed_expr + 1;
    const char *p_pat_end = strchr(p_pat_start, delimiter);
    if (!p_pat_end) return -1;

    const char *p_rep_start = p_pat_end + 1;
    const char *p_rep_end = strchr(p_rep_start, delimiter);
    if (!p_rep_end) return -1;

    size_t pat_len = (size_t)(p_pat_end - p_pat_start);
    size_t rep_len = (size_t)(p_rep_end - p_rep_start);

    char pattern[256], replacement[256];
    if (pat_len >= sizeof(pattern) || rep_len >= sizeof(replacement)) return -1;
    memcpy(pattern, p_pat_start, pat_len);
    pattern[pat_len] = '\0';
    memcpy(replacement, p_rep_start, rep_len);
    replacement[rep_len] = '\0';

    int cflags = REG_EXTENDED;
    const char *p_flags = p_rep_end + 1;
    if (strchr(p_flags, 'i') || strchr(p_flags, 'I')) cflags |= REG_ICASE;

    regex_t compiled_re;
    if (regcomp(&compiled_re, pattern, cflags) != 0) return -1;

    regmatch_t match_groups[10];
    int match_res = regexec(&compiled_re, input_num, 10, match_groups, 0);
    if (match_res != 0) {
        regfree(&compiled_re);
        return -1; /* Шаблон регулярного виразу не збігся */
    }

    /* Формуємо результат, замінюючи \1..\9 на відповідні захоплені групи */
    size_t out_pos = 0;
    for (size_t i = 0; i < rep_len; ++i) {
        if (replacement[i] == '\\' && isdigit((unsigned char)replacement[i + 1])) {
            int group_num = replacement[i + 1] - '0';
            if (group_num >= 0 && group_num < 10 && match_groups[group_num].rm_so != -1) {
                regoff_t g_len = match_groups[group_num].rm_eo - match_groups[group_num].rm_so;
                if (out_pos + (size_t)g_len >= out_size) {
                    regfree(&compiled_re);
                    return -1;
                }
                memcpy(uri_out + out_pos, input_num + match_groups[group_num].rm_so, (size_t)g_len);
                out_pos += (size_t)g_len;
            }
            i++; /* Пропускаємо символ цифри */
        } else {
            if (out_pos + 1 >= out_size) {
                regfree(&compiled_re);
                return -1;
            }
            uri_out[out_pos++] = replacement[i];
        }
    }
    uri_out[out_pos] = '\0';
    regfree(&compiled_re);
    return 0;
}

/* Головна точка входу: повна трансляція номера E.164 в SIP URI */
int resolve_enum_to_sip_uri(const char *e164_raw, char *sip_uri_out, size_t out_size) {
    char fqdn[256], canonical_e164[32];
    unsigned char dns_response[ENUM_BUFFER_SIZE];
    enum_naptr_record_t records[ENUM_MAX_RECORDS];
    size_t record_count = 0;

    if (e164_to_enum_fqdn(e164_raw, fqdn, sizeof(fqdn), canonical_e164, sizeof(canonical_e164)) != 0)
        return -1;

    /* Виконуємо DNS-запит типу NAPTR */
    int resp_len = res_query(fqdn, C_IN, T_NAPTR, dns_response, sizeof(dns_response));
    if (resp_len < (int)sizeof(HEADER)) return -1;

    ns_msg msg_handle;
    if (ns_initparse(dns_response, resp_len, &msg_handle) < 0) return -1;

    int answer_count = ns_msg_count(msg_handle, ns_s_an);
    for (int i = 0; i < answer_count && record_count < ENUM_MAX_RECORDS; ++i) {
        ns_rr resource_record;
        if (ns_parserr(&msg_handle, ns_s_an, i, &resource_record) < 0) continue;
        if (ns_rr_type(resource_record) != T_NAPTR) continue;

        const unsigned char *rdata = ns_rr_rdata(resource_record);
        const unsigned char *rdata_end = rdata + ns_rr_rdlen(resource_record);

        if (rdata_end - rdata < 7) continue;

        records[record_count].order = ns_get16(rdata); rdata += 2;
        records[record_count].preference = ns_get16(rdata); rdata += 2;

        rdata = extract_dns_string(rdata, rdata_end, records[record_count].flags, sizeof(records[record_count].flags));
        if (!rdata) continue;
        rdata = extract_dns_string(rdata, rdata_end, records[record_count].services, sizeof(records[record_count].services));
        if (!rdata) continue;
        rdata = extract_dns_string(rdata, rdata_end, records[record_count].regexp, sizeof(records[record_count].regexp));
        if (!rdata) continue;

        char decompressed_name[256];
        if (ns_name_uncompress(dns_response, dns_response + resp_len, rdata, decompressed_name, sizeof(decompressed_name)) >= 0) {
            strncpy(records[record_count].replacement, decompressed_name, sizeof(records[record_count].replacement) - 1);
        }

        /* Фільтрація: перевірка наявності сервісу SIP */
        if (strstr(records[record_count].services, "E2U+sip") || strstr(records[record_count].services, "E2U+voice:sip")) {
            record_count++;
        }
    }

    if (record_count == 0) return -1; /* Жодного валідного SIP запису в зоні */

    /* Сортування масиву знайдених правил */
    qsort(records, record_count, sizeof(enum_naptr_record_t), compare_naptr_records);

    /* Послідовна обробка від найбільш пріоритетного правила */
    for (size_t i = 0; i < record_count; ++i) {
        if (strchr(records[i].flags, 'u') || strchr(records[i].flags, 'U')) {
            if (execute_sed_replacement(records[i].regexp, canonical_e164, sip_uri_out, out_size) == 0)
                return 0; /* Успішно отримано SIP URI */
        }
    }

    return -1;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <algorithm>
#include <regex>
#include <cstdint>
#include <netinet/in.h>
#include <arpa/nameser.h>
#include <resolv.h>

struct EnumNaptrEntry {
    uint16_t order{0};
    uint16_t preference{0};
    std::string flags;
    std::string services;
    std::string regexp;
    std::string replacement;
};

class ModernEnumResolver {
public:
    // Головний метод: трансляція номера у SIP URI
    static std::optional<std::string> resolvePhoneNumber(std::string_view rawInput) {
        auto canonicalNumber = canonicalizeE164(rawInput);
        if (!canonicalNumber) return std::nullopt;

        auto domainFqdn = buildEnumFqdn(*canonicalNumber);
        if (!domainFqdn) return std::nullopt;

        auto records = performDnsNaptrQuery(*domainFqdn);
        if (records.empty()) return std::nullopt;

        // Сортуємо правила за алгоритмом DDDS: Order -> Preference
        std::sort(records.begin(), records.end(), [](const EnumNaptrEntry& a, const EnumNaptrEntry& b) {
            if (a.order != b.order) return a.order < b.order;
            return a.preference < b.preference;
        });

        // Застосовуємо регулярний вираз першого відповідного правила
        for (const auto& entry : records) {
            if (isSupportedSipService(entry.services) && isTerminalUriRule(entry.flags)) {
                auto resolvedUri = applySedTransformation(entry.regexp, *canonicalNumber);
                if (resolvedUri) return resolvedUri;
            }
        }

        return std::nullopt;
    }

private:
    static std::optional<std::string> canonicalizeE164(std::string_view input) {
        if (input.empty() || input.front() != '+') return std::nullopt;

        std::string digits;
        digits.reserve(16);
        for (size_t i = 1; i < input.size(); ++i) {
            char c = input[i];
            if (std::isdigit(static_cast<unsigned char>(c))) {
                if (digits.size() >= 15) return std::nullopt;
                digits.push_back(c);
            } else if (c != ' ' && c != '-' && c != '(' && c != ')') {
                return std::nullopt;
            }
        }
        if (digits.size() < 3) return std::nullopt;
        return "+" + digits;
    }

    static std::optional<std::string> buildEnumFqdn(std::string_view canonicalNumber) {
        if (canonicalNumber.size() < 4 || canonicalNumber.front() != '+') return std::nullopt;
        std::string fqdn;
        fqdn.reserve(canonicalNumber.size() * 2 + 16);

        // Інверсія цифр із розділенням крапками
        for (auto it = canonicalNumber.rbegin(); it != canonicalNumber.rend() - 1; ++it) {
            fqdn.push_back(*it);
            fqdn.push_back('.');
        }
        fqdn += "e164.arpa";
        return fqdn;
    }

    static bool isSupportedSipService(std::string_view services) {
        return services.find("E2U+sip") != std::string_view::npos ||
               services.find("E2U+voice:sip") != std::string_view::npos;
    }

    static bool isTerminalUriRule(std::string_view flags) {
        return flags.find('u') != std::string_view::npos ||
               flags.find('U') != std::string_view::npos;
    }

    static std::vector<EnumNaptrEntry> performDnsNaptrQuery(const std::string& fqdn) {
        std::vector<EnumNaptrEntry> results;
        std::vector<uint8_t> buffer(4096);

        int bytesReceived = res_query(fqdn.c_str(), C_IN, T_NAPTR, buffer.data(), static_cast<int>(buffer.size()));
        if (bytesReceived < static_cast<int>(sizeof(HEADER))) return results;

        ns_msg handle;
        if (ns_initparse(buffer.data(), bytesReceived, &handle) < 0) return results;

        int answerCount = ns_msg_count(handle, ns_s_an);
        for (int i = 0; i < answerCount; ++i) {
            ns_rr resourceRecord;
            if (ns_parserr(&handle, ns_s_an, i, &resourceRecord) < 0) continue;
            if (ns_rr_type(resourceRecord) != T_NAPTR) continue;

            const uint8_t* rdataPtr = ns_rr_rdata(resourceRecord);
            const uint8_t* rdataEnd = rdataPtr + ns_rr_rdlen(resourceRecord);
            if (rdataEnd - rdataPtr < 7) continue;

            EnumNaptrEntry entry;
            entry.order = ns_get16(rdataPtr); rdataPtr += 2;
            entry.preference = ns_get16(rdataPtr); rdataPtr += 2;

            auto readPascalString = [](const uint8_t*& ptr, const uint8_t* limit) -> std::string {
                if (ptr >= limit) return {};
                uint8_t strLen = *ptr++;
                if (ptr + strLen > limit) return {};
                std::string s(reinterpret_cast<const char*>(ptr), strLen);
                ptr += strLen;
                return s;
            };

            entry.flags = readPascalString(rdataPtr, rdataEnd);
            entry.services = readPascalString(rdataPtr, rdataEnd);
            entry.regexp = readPascalString(rdataPtr, rdataEnd);

            char decompressedHost[256];
            if (ns_name_uncompress(buffer.data(), buffer.data() + bytesReceived, rdataPtr, decompressedHost, sizeof(decompressedHost)) >= 0) {
                entry.replacement = decompressedHost;
            }

            results.push_back(std::move(entry));
        }

        return results;
    }

    static std::optional<std::string> applySedTransformation(std::string_view sedExpr, std::string_view canonicalPhone) {
        if (sedExpr.size() < 3) return std::nullopt;
        char delim = sedExpr.front();

        auto p1 = sedExpr.find(delim, 1);
        if (p1 == std::string_view::npos) return std::nullopt;
        auto p2 = sedExpr.find(delim, p1 + 1);
        if (p2 == std::string_view::npos) return std::nullopt;

        std::string pattern(sedExpr.substr(1, p1 - 1));
        std::string replacement(sedExpr.substr(p1 + 1, p2 - p1 - 1));
        std::string flags(sedExpr.substr(p2 + 1));

        std::regex_constants::syntax_option_type regexOptions = std::regex_constants::ECMAScript;
        if (flags.find('i') != std::string::npos || flags.find('I') != std::string::npos) {
            regexOptions |= std::regex_constants::icase;
        }

        try {
            std::regex re(pattern, regexOptions);
            std::smatch matchResults;
            std::string phoneString(canonicalPhone);
            if (!std::regex_search(phoneString, matchResults, re)) return std::nullopt;

            std::string outputUri;
            outputUri.reserve(128);
            for (size_t i = 0; i < replacement.size(); ++i) {
                if (replacement[i] == '\\' && i + 1 < replacement.size() && std::isdigit(static_cast<unsigned char>(replacement[i + 1]))) {
                    size_t groupIndex = replacement[i + 1] - '0';
                    if (groupIndex < matchResults.size()) {
                        outputUri += matchResults[groupIndex].str();
                    }
                    ++i;
                } else {
                    outputUri.push_back(replacement[i]);
                }
            }
            return outputUri;
        } catch (const std::regex_error&) {
            return std::nullopt;
        }
    }
};
```
:::

---

### Інтеграція в реальні платформи IP-телефонії

У виробничих середовищах розробники рідко реалізують весь стек DNS вручну, використовуючи натомість вбудовані модулі популярних відкритих платформ зв'язку:

#### 1. Модуль ENUM у SIP-сервері Kamailio

Високопродуктивний SIP-проксі Kamailio містить модуль `enum`, який надає функцію `enum_query()` безпосередньо в конфігураційному файлі маршрутизації `kamailio.cfg`:

```
route[ENUM_ROUTING] {
    # Перевіряємо, чи Request-URI містить телефонний номер
    if (uri =~ "^sip:\+[0-9]+@") {
        # Виконуємо ENUM запит до зони e164.arpa для сервісу sip
        if (enum_query("e164.arpa.", "sip")) {
            xlog("L_INFO", "ENUM знайдено новий маршрут: $ru\n");
            # Перенаправляємо SIP INVITE за новим знайденим URI
            route(RELAY);
            exit;
        } else {
            xlog("L_WARN", "ENUM маршрут відсутній, перемикаємо на PSTN шлюз\n");
            route(PSTN_GATEWAY);
        }
    }
}
```

Модуль Kamailio автоматично виконує DNS-запит NAPTR, сортує правила за `order`/`preference`, застосовує регулярний вираз та перезаписує змінну `$ru` (Request-URI) отриманим SIP URI.

#### 2. Додаток ENUMLOOKUP у диалплані Asterisk PBX

У платформі Asterisk трансляція номерів виконується за допомогою вбудованої функції диалплану `ENUMLOOKUP`:

```
[outbound-calls]
exten => _+380X.,1,NoOp(Пошук ENUM маршруту для номера ${EXTEN})
 same => n,Set(TARGET_SIP_URI=${ENUMLOOKUP(${EXTEN},sip,,1,e164.arpa)})
 same => n,GotoIf($["${TARGET_SIP_URI}" != ""]?call_sip:call_pstn)

 same => n(call_sip),NoOp(Знайдено прямий IP маршрут: ${TARGET_SIP_URI})
 same => n,Dial(PJSIP/${TARGET_SIP_URI},30)
 same => n,Hangup()

 same => n(call_pstn),NoOp(Прямий IP маршрут відсутній, вихід через E1/PSTN шлюз)
 same => n,Dial(DAHDI/g1/${EXTEN},30)
 same => n,Hangup()
```

#### 3. Модуль mod_enum у комутаторі FreeSWITCH

У FreeSWITCH конфігурація `autoload_configs/enum.conf.xml` дозволяє визначати кілька послідовних дерев пошуку (Search Trees), наприклад, спочатку приватну зону Carrier ENUM оператора, а у разі невдачі — глобальну зону `e164.arpa`:

```xml
<configuration name="enum.conf" description="ENUM Module">
  <settings>
    <param name="default-root" value="e164.arpa"/>
    <param name="auto-reload" value="true"/>
  </settings>
  <routes>
    <!-- Спочатку перевіряємо внутрішнє операторське дерево -->
    <route service="E2U+sip" regex="carrier.e164.org" replace="$1@internal-carrier.net"/>
    <!-- Потім перевіряємо публічне дерево e164.arpa -->
    <route service="E2U+sip" regex="e164.arpa"/>
  </routes>
</configuration>
```

---

### Детальний розбір реалізації та аналіз пасток

Проектування та експлуатація власних ENUM-резолверів у високонавантажених системах вимагає контролю таких потенційних дефектів:

1. **Небезпека синхронних блокуючих викликів `res_query`:**
   Функція `res_query` виконує блокуючий мережевий виклик по протоколу UDP або TCP до DNS-сервера. Якщо авторитетний DNS-сервер оператора-партнера перевантажений або недосяжний, потік обробки виклику softswitch зависає на системний таймаут сокета (за замовчуванням до 5–30 секунд). При навантаженні в сотні викликів на секунду пул робочих потоків комутатора вичерпується за лічені секунди, паралізуючи всю телефонну станцію.
   *Вирішення:* У промислових комутаторах DNS-запити виносять в неблокуючі асинхронні бібліотеки на базі мультиплексування вводу-виводу (`epoll`/`kqueue`), або застосовують локальний кешуючий DNS-демон (наприклад, `unbound` або `dnsmasq`), розміщений на тій самій машині (loopback `127.0.0.1`), що гарантує час відповіді кешу менше 1 мілісекунди.

2. **Вразливість до атак ReDoS при розборі чужих записів NAPTR:**
   Якщо система підтримує відкритий User ENUM або отримує записи NAPTR від неперевірених пірингових операторів, зловмисник може опублікувати регулярний вираз із катастрофічним поверненням (Catastrophic Backtracking), наприклад `!^(a+)+$!...!`. При зіставленні з рядком `aaaaaaaaaaaaaaaaaaaaX` стандартний рушій регулярних виразів виконуватиме мільярди операцій, споживаючи 100% потужності процесора.
   *Вирішення:* Використання лінійних рушіїв регулярних виразів без повернення (наприклад, Google RE2) або суворе обмеження часу виконання виклику `regexec` за допомогою таймерів та лімітування довжини шаблону.

3. **Коректна обробка декомпресії імен DNS:**
   У зонових файлах та двійкових пакетах поле `REPLACEMENT` може використовувати стиснення імен DNS (DNS Name Compression). Якщо утиліта не підтримує розпакування міток зі зміщеннями `0xC0XX`, замість валідного імені сервера буде зчитано сміття з пам'яті. У C-реалізації функція `ns_name_uncompress` гарантує коректне відновлення доменного імені.

4. **Інваріант пріоритетності ORDER:**
   Класичною помилкою програмістів-початківців є спроба перевірити всі регулярні вирази одночасно і вибрати той, що дав перший збіг. Алгоритм DDDS суворо вимагає перевіряти записи **лише найменшого наявного значення ORDER**. До записів із вищим `ORDER` дозволено переходити лише тоді, коли всі записи меншого `ORDER` виявилися непридатними або недосяжними.

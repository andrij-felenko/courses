# ⚙️ Реалізація серверної перевірки квитка, автентифікатора та кешу повторів

Ця вставка містить закінчену практичну реалізацію серверного модуля обробки запиту `KRB_AP_REQ` та формування відповіді взаємної автентифікації `KRB_AP_REP`. У коді розібрано повний ланцюг криптографічної валідації: розшифрування квитка довгостроковим ключем служби, вилучення сесійного ключа, розпакування одноразового автентифікатора, перевірка часового вікна розсинхронізації (Clock Skew) та фільтрація повторних атак через потокобезпечний кеш повторів (Replay Cache).

## Задача та модель загроз

Коли сервер додатку (наприклад, файловий сервер SMB/NFS, вузол розподіленої бази даних або веб-сервер HTTP) отримує від клієнта пакет `AP-REQ`, він функціонує в умовах відсутності прямого онлайн-зв'язку з центром розподілу ключів KDC. Сервер не може в реальному часі надіслати запит до KDC із питанням «чи справді користувач Alice надіслала цей запит?», оскільки це перетворило б KDC на вузьке місце продуктивності (Single Point of Failure) та зруйнувало б масштабованість системи.

Сервер володіє лише власним локальним довгостроковим ключем `K_s` (збереженим у захищеному файлі `keytab`), поточним системним годинником і локальною оперативною пам'яттю.

У цих умовах серверний модуль обробки `AP-REQ` зобов'язаний самостійно вирішити три фундаментальні задачі безпеки:

1. **Автентичність клієнта**: Переконатися, що наданий квиток справді згенерований довіреним KDC, не зазнав змін під час транспортування ненадійною мережею, а клієнт, який ініціював з'єднання, справді володіє симетричним сесійним ключем `K_{c,s}`, вкладеним KDC усередину квитка.
2. **Контроль часових меж сесії**: Відхилити будь-які квитки, чий термін придатності вже вичерпано (`endtime < now`) або чия дія ще не розпочалася (`starttime > now`).
3. **Захист від атак повторного відтворення (Replay Attack)**: Запобігти ситуації, коли мережевий зловмисник перехоплює легітимний пакет `AP-REQ` із каналу зв'язку та відправляє його повторно протягом кількох секунд або хвилин, намагаючись від імені клієнта виконати несанкціоновану дію (наприклад, повторне списання коштів чи виконання віддаленої команди).

## Архітектура конвеєра перевірки

Конвеєр обробки повідомлення `AP-REQ` на стороні сервера складається з шести послідовних кроків, кожен із яких перевіряє строгий криптографічний інваріант:

```
[Вхідний пакет AP-REQ]
        │
        ▼
[1. Розшифрування Ticket ключем K_s (Key Usage = 2)] ── Помилка цілісності ──→ KRB_AP_ERR_BAD_INTEGRITY (31)
        │
        ▼
[2. Перевірка терміну придатності (endtime >= now)] ──── Застарілий квиток ───→ KRB_AP_ERR_TKT_EXPIRED (32)
        │
        ▼
[3. Розшифрування Authenticator сесійним ключем K_{c,s} (Key Usage = 11)] ──→ KRB_AP_ERR_BAD_INTEGRITY (31)
        │
        ▼
[4. Звірка ідентифікаторів: ticket.cname == auth.cname] ── Розбіжність імен ─→ KRB_AP_ERR_BADMATCH (36)
        │
        ▼
[5. Перевірка розсинхронізації годинника (|now - ctime| <= 300 c)] ───────────→ KRB_AP_ERR_SKEW (37)
        │
        ▼
[6. Перевірка та вставка в Replay Cache (cname, ctime, cusec)] ── Дублікат ───→ KRB_AP_ERR_REPEAT (34)
        │
        ▼
[Успішна автентифікація: випуск сесійного ключа або відповіді AP-REP]
```

### Детальний розбір етапів валідації

1. **Розшифрування квитка**: Сервер зчитує поле `sname` і версію ключа `kvno`, вибирає відповідний симетричний ключ `K_s` зі свого `keytab` і розшифровує `EncTicketPart` із номером використання `Key Usage = 2`. Якщо контрольна сума HMAC не збігається, це означає, що квиток підроблено або зашифровано застарілим/чужим ключем. Сервер негайно припиняє обробку з кодом `KRB_AP_ERR_BAD_INTEGRITY`.
2. **Перевірка терміну придатності**: Сервер порівнює поточний системний час `T_{now}` із полем `endtime`. Допускається невелике технологічне послаблення `Δ t` для компенсації розсинхронізації годинників, проте якщо `T_{now} > endtime + Δ t`, квиток беззастережно відхиляється з кодом `KRB_AP_ERR_TKT_EXPIRED`.
3. **Розшифрування автентифікатора**: Сервер вилучає сесійний ключ `K_{c,s}` із розшифрованого `EncTicketPart` і застосовує його для розшифрування структури `Authenticator` із номером використання `Key Usage = 11`. Успішне розшифрування є математичним доказом того, що відправник пакета знає ключ `K_{c,s}`.
4. **Звірка імен принципалів**: Сервер зіставляє поля `cname` (ім'я користувача) та `crealm` (область) з квитка з полями `cname` і `crealm` з автентифікатора. Оскільки вміст квитка підписаний KDC, а автентифікатор сформований клієнтом, повний збіг рядків гарантує, що запит надіслано саме тим клієнтом, кому KDC видав цей квиток.
5. **Контроль розсинхронізації годинників (Clock Skew)**: Сервер обчислює абсолютну різницю `|T_{now} - ctime|`. Якщо похибка перевищує максимальне допустиме вікно `Δ t = 300` секунд (5 хвилин), пакет відхиляється з кодом `KRB_AP_ERR_SKEW`. Це звужує часовий інтервал можливої атаки повтору рівно до величини `Δ t`.
6. **Фільтрація у кеші повторів (Replay Cache)**: Оскільки перехоплений пакет усередині 5-хвилинного вікна залишається криптографічно валідним, сервер веде локальну таблицю всіх нещодавно оброблених автентифікаторів. Ключем запису слугує трійка `(cname, ctime, cusec)`. Якщо такий запис уже існує в таблиці — фіксується атака повторного відтворення і повертається помилка `KRB_AP_ERR_REPEAT`. Якщо запису немає — він додається в кеш із терміном життя (TTL), рівним `2 · Δ t`, після чого запит вважається легітимним.

## Реалізація мовами C та C++

Нижче наведено дві паралельні закінчені реалізації сервера перевірки:
- На чистому C: класичний підхід із плоскими структурами даних, фіксованим масивом записів кешу, явними кодами помилок та функціями очищення застарілих елементів.
- На сучасному C++ (C++20/23): ідіоматичний об'єктно-орієнтований дизайн, використання `std::expected` для безпечної обробки помилок без винятків, `std::unordered_set` із власним гешуванням для амортизованого часу пошуку `O(1)`, семантика володіння RAII, `std::span` та `std::chrono` для строго типізованої роботи з часом.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define KRB5_MAX_SKEW_SEC 300
#define REPLAY_CACHE_CAPACITY 1024

/* Коди результатів обробки Kerberos AP-REQ */
typedef enum {
    KRB5_OK = 0,
    KRB5_ERR_BAD_INTEGRITY = 31,
    KRB5_ERR_TKT_EXPIRED   = 32,
    KRB5_ERR_REPEAT        = 34,
    KRB5_ERR_BADMATCH      = 36,
    KRB5_ERR_SKEW          = 37
} krb5_error_code;

/* Структура симетричного ключа */
typedef struct {
    int32_t keytype;
    uint8_t data[32];
    size_t length;
} krb5_keyblock;

/* Зашифрована частина квитка (EncTicketPart) */
typedef struct {
    char cname[64];
    char crealm[64];
    krb5_keyblock session_key;
    time_t authtime;
    time_t starttime;
    time_t endtime;
} krb5_enc_ticket_part;

/* Автентифікатор клієнта */
typedef struct {
    char cname[64];
    char crealm[64];
    time_t ctime;
    uint32_t cusec;
    uint32_t seq_number;
} krb5_authenticator;

/* Запис у кеші повторів */
typedef struct {
    char cname[64];
    time_t ctime;
    uint32_t cusec;
    time_t expiry;
    bool in_use;
} replay_entry;

/* Сховище кешу повторів сервера */
typedef struct {
    replay_entry entries[REPLAY_CACHE_CAPACITY];
    size_t count;
} replay_cache;

/* Ініціалізація кешу повторів */
void replay_cache_init(replay_cache *rc) {
    if (!rc) return;
    memset(rc->entries, 0, sizeof(rc->entries));
    rc->count = 0;
}

/* Очищення застарілих записів з кешу */
void replay_cache_prune(replay_cache *rc, time_t now) {
    for (size_t i = 0; i < REPLAY_CACHE_CAPACITY; ++i) {
        if (rc->entries[i].in_use && rc->entries[i].expiry <= now) {
            rc->entries[i].in_use = false;
            if (rc->count > 0) rc->count--;
        }
    }
}

/* Перевірка та вставка відбитка автентифікатора в кеш */
bool replay_cache_check_and_add(replay_cache *rc, const char *cname, time_t ctime, uint32_t cusec, time_t now) {
    replay_cache_prune(rc, now);

    /* Пошук дубліката */
    for (size_t i = 0; i < REPLAY_CACHE_CAPACITY; ++i) {
        if (rc->entries[i].in_use) {
            if (rc->entries[i].ctime == ctime &&
                rc->entries[i].cusec == cusec &&
                strcmp(rc->entries[i].cname, cname) == 0) {
                return false; /* Знайдено дублікат (Replay attack) */
            }
        }
    }

    /* Пошук вільного слота */
    for (size_t i = 0; i < REPLAY_CACHE_CAPACITY; ++i) {
        if (!rc->entries[i].in_use) {
            strncpy(rc->entries[i].cname, cname, sizeof(rc->entries[i].cname) - 1);
            rc->entries[i].cname[sizeof(rc->entries[i].cname) - 1] = '\0';
            rc->entries[i].ctime = ctime;
            rc->entries[i].cusec = cusec;
            rc->entries[i].expiry = now + KRB5_MAX_SKEW_SEC;
            rc->entries[i].in_use = true;
            rc->count++;
            return true; /* Успішно зареєстровано новий запит */
        }
    }

    return false; /* Кеш переповнений */
}

/* Імітація криптографічного розшифрування квитка ключем служби */
krb5_error_code decrypt_ticket(const uint8_t *cipher, size_t len, const krb5_keyblock *service_key, krb5_enc_ticket_part *out_ticket) {
    if (!cipher || !service_key || !out_ticket || len == 0) {
        return KRB5_ERR_BAD_INTEGRITY;
    }
    /* У бойовій системі викликається OpenSSL EVP / AES-CTS-HMAC */
    strncpy(out_ticket->cname, "alice@EXAMPLE.ORG", sizeof(out_ticket->cname) - 1);
    strncpy(out_ticket->crealm, "EXAMPLE.ORG", sizeof(out_ticket->crealm) - 1);
    out_ticket->session_key.keytype = 18; /* AES-256 */
    memset(out_ticket->session_key.data, 0x4A, 32);
    out_ticket->session_key.length = 32;
    out_ticket->authtime = time(NULL) - 60;
    out_ticket->starttime = time(NULL) - 60;
    out_ticket->endtime = time(NULL) + 28800; /* Дійсний 8 годин */
    return KRB5_OK;
}

/* Імітація розшифрування автентифікатора сесійним ключем */
krb5_error_code decrypt_authenticator(const uint8_t *cipher, size_t len, const krb5_keyblock *session_key, krb5_authenticator *out_auth) {
    if (!cipher || !session_key || !out_auth || len == 0) {
        return KRB5_ERR_BAD_INTEGRITY;
    }
    strncpy(out_auth->cname, "alice@EXAMPLE.ORG", sizeof(out_auth->cname) - 1);
    strncpy(out_auth->crealm, "EXAMPLE.ORG", sizeof(out_auth->crealm) - 1);
    out_auth->ctime = time(NULL) - 2; /* Згенеровано 2 секунди тому */
    out_auth->cusec = 450123;
    out_auth->seq_number = 1001;
    return KRB5_OK;
}

/* Головний конвеєр перевірки AP-REQ на стороні сервера */
krb5_error_code verify_ap_req(const uint8_t *raw_ticket, size_t ticket_len,
                              const uint8_t *raw_auth, size_t auth_len,
                              const krb5_keyblock *service_key,
                              replay_cache *rc,
                              krb5_keyblock *out_session_key) {
    krb5_enc_ticket_part ticket;
    krb5_authenticator auth;
    time_t now = time(NULL);
    krb5_error_code code;

    /* Крок 1: Розшифрування квитка ключем служби */
    code = decrypt_ticket(raw_ticket, ticket_len, service_key, &ticket);
    if (code != KRB5_OK) return code;

    /* Крок 2: Перевірка терміну придатності квитка */
    if (now > ticket.endtime + KRB5_MAX_SKEW_SEC) {
        return KRB5_ERR_TKT_EXPIRED;
    }

    /* Крок 3: Розшифрування автентифікатора вилученим сесійним ключем */
    code = decrypt_authenticator(raw_auth, auth_len, &ticket.session_key, &auth);
    if (code != KRB5_OK) return code;

    /* Крок 4: Звірка імен клієнта */
    if (strcmp(ticket.cname, auth.cname) != 0 || strcmp(ticket.crealm, auth.crealm) != 0) {
        return KRB5_ERR_BADMATCH;
    }

    /* Крок 5: Перевірка допустимого вікна розсинхронізації часу */
    double diff = difftime(now, auth.ctime);
    if (diff < -KRB5_MAX_SKEW_SEC || diff > KRB5_MAX_SKEW_SEC) {
        return KRB5_ERR_SKEW;
    }

    /* Крок 6: Перевірка в кеші повторів */
    if (!replay_cache_check_and_add(rc, auth.cname, auth.ctime, auth.cusec, now)) {
        return KRB5_ERR_REPEAT;
    }

    /* Успіх: передаємо сесійний ключ викликачу */
    if (out_session_key) {
        *out_session_key = ticket.session_key;
    }
    return KRB5_OK;
}

int main(void) {
    replay_cache rc;
    replay_cache_init(&rc);

    krb5_keyblock srv_key = { .keytype = 18, .length = 32 };
    memset(srv_key.data, 0x5F, 32);

    uint8_t dummy_ticket[128] = {1};
    uint8_t dummy_auth[64] = {2};
    krb5_keyblock negotiated_session_key;

    /* Перша спроба: має завершитися успішно */
    krb5_error_code res1 = verify_ap_req(dummy_ticket, sizeof(dummy_ticket),
                                         dummy_auth, sizeof(dummy_auth),
                                         &srv_key, &rc, &negotiated_session_key);
    printf("Спроба 1: код %d (%s)\n", res1, res1 == KRB5_OK ? "УСПІХ" : "ВІДХИЛЕНО");

    /* Повторна спроба з тим самим автентифікатором: має бути заблокована Replay Cache */
    krb5_error_code res2 = verify_ap_req(dummy_ticket, sizeof(dummy_ticket),
                                         dummy_auth, sizeof(dummy_auth),
                                         &srv_key, &rc, &negotiated_session_key);
    printf("Спроба 2 (Replay): код %d (%s)\n", res2, res2 == KRB5_ERR_REPEAT ? "ЗАБЛОКОВАНО REPLAY" : "ПОМИЛКА ТЕСТУ");

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <chrono>
#include <expected>
#include <optional>
#include <cstdint>
#include <span>

namespace krb5 {

inline constexpr std::chrono::seconds MaxClockSkew{300};

enum class ErrorCode : int32_t {
    BadIntegrity = 31,
    TicketExpired = 32,
    RepeatDetected = 34,
    PrincipalMismatch = 36,
    ClockSkew = 37
};

struct KeyBlock {
    int32_t keyType{18}; // AES-256
    std::vector<uint8_t> data;
};

struct EncTicketPart {
    std::string cname;
    std::string crealm;
    KeyBlock sessionKey;
    std::chrono::system_clock::time_point authTime;
    std::chrono::system_clock::time_point startTime;
    std::chrono::system_clock::time_point endTime;
};

struct Authenticator {
    std::string cname;
    std::string crealm;
    std::chrono::system_clock::time_point ctime;
    uint32_t cusec{0};
    uint32_t seqNumber{0};
    std::optional<KeyBlock> subKey;
};

struct ReplayRecord {
    std::string cname;
    int64_t ctimeSec;
    uint32_t cusec;
    std::chrono::system_clock::time_point expiry;

    bool operator==(const ReplayRecord& other) const noexcept {
        return ctimeSec == other.ctimeSec &&
               cusec == other.cusec &&
               cname == other.cname;
    }
};

struct ReplayRecordHash {
    size_t operator()(const ReplayRecord& r) const noexcept {
        size_t h1 = std::hash<std::string>{}(r.cname);
        size_t h2 = std::hash<int64_t>{}(r.ctimeSec);
        size_t h3 = std::hash<uint32_t>{}(r.cusec);
        return h1 ^ (h2 << 1) ^ (h3 << 2);
    }
};

class ReplayCache {
public:
    [[nodiscard]] bool checkAndAdd(std::string_view cname,
                                   std::chrono::system_clock::time_point ctime,
                                   uint32_t cusec,
                                   std::chrono::system_clock::time_point now) {
        pruneExpired(now);

        const auto sec = std::chrono::duration_cast<std::chrono::seconds>(
            ctime.time_since_epoch()).count();

        ReplayRecord record{
            .cname = std::string(cname),
            .ctimeSec = sec,
            .cusec = cusec,
            .expiry = now + MaxClockSkew
        };

        if (cache_.contains(record)) {
            return false; // Виявлено спробу повтору
        }

        cache_.insert(std::move(record));
        return true;
    }

private:
    void pruneExpired(std::chrono::system_clock::time_point now) {
        std::erase_if(cache_, [now](const ReplayRecord& r) noexcept {
            return r.expiry <= now;
        });
    }

    std::unordered_set<ReplayRecord, ReplayRecordHash> cache_;
};

class ServerValidator {
public:
    explicit ServerValidator(KeyBlock serviceKey)
        : serviceKey_(std::move(serviceKey)) {}

    [[nodiscard]] std::expected<KeyBlock, ErrorCode> verifyApReq(
        std::span<const uint8_t> rawTicket,
        std::span<const uint8_t> rawAuth,
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now()) {

        // Крок 1: Розшифрування квитка ключем служби
        auto ticketRes = decryptTicket(rawTicket, serviceKey_);
        if (!ticketRes) return std::unexpected(ticketRes.error());
        const auto& ticket = *ticketRes;

        // Крок 2: Перевірка терміну придатності квитка
        if (now > ticket.endTime + MaxClockSkew) {
            return std::unexpected(ErrorCode::TicketExpired);
        }

        // Крок 3: Розшифрування автентифікатора вилученим сесійним ключем
        auto authRes = decryptAuthenticator(rawAuth, ticket.sessionKey);
        if (!authRes) return std::unexpected(authRes.error());
        const auto& auth = *authRes;

        // Крок 4: Звірка ідентифікаторів принципала
        if (ticket.cname != auth.cname || ticket.crealm != auth.crealm) {
            return std::unexpected(ErrorCode::PrincipalMismatch);
        }

        // Крок 5: Перевірка вікна розсинхронізації годинників
        const auto diff = std::chrono::abs(std::chrono::duration_cast<std::chrono::seconds>(now - auth.ctime));
        if (diff > MaxClockSkew) {
            return std::unexpected(ErrorCode::ClockSkew);
        }

        // Крок 6: Перевірка та реєстрація в кеші повторів
        if (!replayCache_.checkAndAdd(auth.cname, auth.ctime, auth.cusec, now)) {
            return std::unexpected(ErrorCode::RepeatDetected);
        }

        // Успіх: повертаємо узгоджений сесійний ключ
        return ticket.sessionKey;
    }

private:
    static std::expected<EncTicketPart, ErrorCode> decryptTicket(
        std::span<const uint8_t> cipher, const KeyBlock& key) {
        if (cipher.empty() || key.data.empty()) {
            return std::unexpected(ErrorCode::BadIntegrity);
        }
        const auto now = std::chrono::system_clock::now();
        return EncTicketPart{
            .cname = "alice@EXAMPLE.ORG",
            .crealm = "EXAMPLE.ORG",
            .sessionKey = KeyBlock{ .keyType = 18, .data = std::vector<uint8_t>(32, 0x4A) },
            .authTime = now - std::chrono::minutes(1),
            .startTime = now - std::chrono::minutes(1),
            .endTime = now + std::chrono::hours(8)
        };
    }

    static std::expected<Authenticator, ErrorCode> decryptAuthenticator(
        std::span<const uint8_t> cipher, const KeyBlock& sessionKey) {
        if (cipher.empty() || sessionKey.data.empty()) {
            return std::unexpected(ErrorCode::BadIntegrity);
        }
        const auto now = std::chrono::system_clock::now();
        return Authenticator{
            .cname = "alice@EXAMPLE.ORG",
            .crealm = "EXAMPLE.ORG",
            .ctime = now - std::chrono::seconds(2),
            .cusec = 450123,
            .seqNumber = 1001,
            .subKey = std::nullopt
        };
    }

    KeyBlock serviceKey_;
    ReplayCache replayCache_;
};

} // namespace krb5

int main() {
    using namespace krb5;

    KeyBlock serverKey{ .keyType = 18, .data = std::vector<uint8_t>(32, 0x5F) };
    ServerValidator validator(std::move(serverKey));

    std::vector<uint8_t> dummyTicket(128, 1);
    std::vector<uint8_t> dummyAuth(64, 2);

    auto result1 = validator.verifyApReq(dummyTicket, dummyAuth);
    if (result1) {
        std::cout << "Спроба 1: УСПІШНО автентифіковано. Розмір сесійного ключа: "
                  << result1->data.size() << " байтів\n";
    } else {
        std::cout << "Спроба 1: помилка " << static_cast<int>(result1.error()) << "\n";
    }

    auto result2 = validator.verifyApReq(dummyTicket, dummyAuth);
    if (!result2 && result2.error() == ErrorCode::RepeatDetected) {
        std::cout << "Спроба 2: УСПІШНО заблоковано повтор (Replay Attack Detected, код 34)\n";
    } else {
        std::cout << "Спроба 2: несподіваний результат!\n";
    }

    return 0;
}
```
:::

## Аналіз архітектурних відмінностей C та C++

Порівняння двох наведених реалізацій демонструє фундаментальну різницю між підходами до безпеки пам'яті та керування станом:

1. **Керування пам'яттю та рядками**:
   - У версії на C використовуються масиви фіксованого розміру `char[64]` із захистом через `strncpy` та ручною гарантією нульового термінатора. Якщо ім'я користувача перевищить 63 символи, відбудеться усічення рядка, що в криптографічному протоколі призведе до помилки `KRB_AP_ERR_BADMATCH`.
   - У версії на C++ застосовуються динамічні `std::string` та неволодіючі представлення `std::string_view` і `std::span`, що повністю усуває ризик виходу за межі буфера (Buffer Overflow) та не накладає штучних обмежень на довжину ідентифікаторів у доменних деревах Active Directory.

2. **Структура кешу повторів**:
   - У варіанті на C застосовано статичний циклічний масив `entries[1024]`. Пошук дубліката виконується лінійно за `O(N)`, де `N` — місткість кешу. При високому навантаженні (тисячі запитів на секунду) лінійне сканування починає створювати відчутну затримку CPU.
   - У варіанті на C++ застосовано хеш-таблицю `std::unordered_set` із власною комбінованою хеш-функцією `ReplayRecordHash`. Пошук та вставка виконуються в середньому за `O(1)`, а видалення застарілих елементів реалізовано через стандартний предикатний алгоритм `std::erase_if`.

3. **Модель обробки помилок**:
   - Код мовою C використовує конвенцію повернення числових кодів помилок `krb5_error_code`, а результат (сесійний ключ) передає через вихідний вказівник `krb5_keyblock *out_session_key`. Це вимагає від розробника ретельної перевірки кожної проміжної операції та ручного скидання стану при виході з функції.
   - Модуль мовою C++ повертає монадичний тип `std::expected<KeyBlock, ErrorCode>`, що гарантує: отримати доступ до сесійного ключа неможливо, доки викликач явно не перевірить статус успішності операції, що виключає використання неініціалізованої пам'яті на рівні компіляції.

## Формування та перевірка взаємної автентифікації (AP-REP)

У сценаріях, де клієнт вимагає взаємного підтвердження справжності сервера (прапорець `mutual-required`), після успішної валідації `AP-REQ` сервер формує пакет `KRB_AP_REP`.

Механізм взаємної автентифікації розв'язує критичну проблему довіри: клієнт повинен переконатися, що з'єднався зі справжнім сервером, а не з пасивним посередником (Man-in-the-Middle), який лише зібрав надісланий квиток. Оскільки лише легітимний сервер володіє довгостроковим ключем `K_s`, здатним розкрити `EncTicketPart` і витягти сесійний ключ `K_{c,s}`, доказом справжності сервера слугує повернення точної копії часової мітки клієнта, зашифрованої цим сесійним ключем.

### Алгоритм створення `AP-REP` на сервері:

1. Сервер копіює значення `ctime` та `cusec` із розшифрованого автентифікатора клієнта.
2. Якщо сервер бажає оновити підключ сеансу, він генерує новий випадковий `subkey` і додає його в структуру `EncAPRepPart`.
3. Структура `EncAPRepPart` шифрується сесійним ключем `K_{c,s}` із криптографічним номером використання `Key Usage = 12`.
4. Зашифрований блок пакується у тег `[APPLICATION 15]` (`AP-REP`) і відправляється клієнту у відповідь.

### Алгоритм перевірки `AP-REP` на клієнті:

1. Клієнт розшифровує `enc-part` отриманого `AP-REP` за допомогою збереженого в локальній пам'яті сесійного ключа `K_{c,s}` (використовуючи `Key Usage = 12`).
2. Клієнт звіряє вилучені поля `ctime` та `cusec` зі своїми початковими значеннями, надісланими в `AP-REQ`.
3. Якщо мітки збігаються біт-у-біт — сервер вважається достеменно автентифікованим, і сторони переходять до захищеного прикладного сеансу. Якщо в `AP-REP` було передано `subkey`, усі подальші прикладні пакети шифруються виключно цим підключем.

## Розрахунок параметрів та продуктивності Replay Cache

Розмір та стратегія очищення кешу повторів є компромісом між споживанням оперативної пам'яті та захистом від відмови в обслуговуванні (DoS).

### Математичний розрахунок місткості

Нехай `R` — середня інтенсивність вхідних запитів автентифікації (запитів на секунду), а `Δ t` — часове вікно розсинхронізації (300 секунд). Мінімальна необхідна кількість записів у кеші для уникнення витіснення легітимних елементів становить:

```
N_min = 2 · R · Δt
```

Для високонавантаженого сервера з інтенсивністю `R = 500` запитів/с:

```
N_min = 2 · 500 · 300 = 300 000 записів
```

При розмірі одного запису `ReplayRecord` близько 128 байтів (з урахуванням вирівнювання пам'яті та внутрішніх покажчиків хеш-таблиці `std::unordered_set`), загальний обсяг пам'яті кешу становить:

```
Пам'ять = 300 000 · 128 байтів ≈ 38.4 МБ
```

Для сучасного сервера обсяг у 40 МБ є незначним, проте лінійне сканування такого масиву в однопотоковому режимі призвело б до неприпустимої деградації CPU (`300 000` операцій порівняння на кожен вхідний пакет). Саме тому використання хеш-таблиці з часовою складністю `O(1)` або шардованого кешу є обов'язковою інженерною вимогою для промислових систем.

## Інтеграція з Generic Security Services API (GSS-API / SPNEGO)

У реальних виробничих середовищах прикладні сервери (веб-сервер Nginx/Apache, SMB-демон Samba або база даних PostgreSQL) рідко взаємодіють із сирими ASN.1 структурами Kerberos напряму. Натомість використовується стандартизований інтерфейс GSS-API (RFC 2743) та механізм узгодження SPNEGO (RFC 4178).

Модуль автентифікації викликає стандартні функції:
- `gss_acquire_cred()` — завантаження довгострокового ключа служби `K_s` із файлу `/etc/krb5.keytab`.
- `gss_accept_sec_context()` — виконання повного конвеєра перевірки: десеріалізація SPNEGO токена, розпакування `AP-REQ`, розшифрування квитка та автентифікатора, перевірка replay cache та генерація вихідного токена `AP-REP`.
- `gss_unwrap()` / `gss_wrap()` — шифрування та підпис прикладного трафіку сеансу за допомогою узгодженого сесійного ключа.

Особливістю протоколу Kerberos v5 є підтримка режиму викрадення шифротексту CBC-CTS (англ. *Ciphertext Stealing*, RFC 3962). На відміну від класичного режиму CBC з доповненням PKCS#7, який завжди збільшує розмір блоку до кратного 16 байтам, режим CTS дозволяє шифрувати повідомлення довільної довжини (від 16 байтів) без збільшення розміру корисного навантаження. Останній неповний блок даних ксориться із залишком передостаннього шифрованого блоку. Це критично для зменшення обсягу мережевих пакетів, проте вимагає від серверного коду точного контролю мінімального розміру вхідного буфера (не менше одного повного блоку AES у 16 байтів).

## Практичні підводні камені та вразливості (Security Pitfalls)

1. **Стан гонки в багатопотокових серверах (Replay Cache Race Condition)**:
   Якщо сервер обробляє запити в пулі потоків (наприклад, веб-сервер на базі `epoll` чи worker-процесів), між операцією перевірки наявності запису в кеші та операцією його додавання виникає часовий зазор (Time-of-Check to Time-of-Use, TOCTOU). Зловмисник, що надішле два ідентичні пакети `AP-REQ` одночасно у два паралельні сокети, міг обійти кеш. Захист вимагає атомарної операції `check_and_insert` під захистом `std::mutex` або шардованого м'ютекса за першим байтом хеша імені клієнта.
2. **Ігнорування поля мікросекунд (`cusec`)**:
   Сучасні високопродуктивні клієнти (наприклад, мікросервісні шлюзи gRPC або веб-браузери) відкривають десятки TCP-з'єднань протягом однієї секунди. Якщо кеш повторів зберігає лише секунди `ctime`, усі наступні паралельні запити клієнта з однаковою міткою секунди будуть помилково відхилені як атака повтору. Поле `cusec` є обов'язковим компонентом композитного ключа.
3. **Атаки розсинхронізації часу (Time Drift / NTP Poisoning)**:
   Якщо зловмисник підробить відповіді NTP-сервера і змістить годинник сервера вперед на кілька годин, усі легітимні клієнти отримають помилку `KRB_AP_ERR_SKEW`. Якщо ж змістити годинник назад, зловмисник розширює вікно придатності перехоплених старих квитків. Сервери Kerberos зобов'язані використовувати автентифікований протокол NTP (NTPv4 з симетричним ключем або NTS — Network Time Security).
4. **Атаки на підсесійні ключі (Subkey Downgrade)**:
   Якщо сервер сліпо довіряє підключу `subkey` з автентифікатора без перевірки його криптографічної стійкості, зловмисник із доступом до клієнтського процесу може навмисно підсунути слабкий ключ. Сервер повинен вимагати, щоб тип алгоритму підключа був не слабшим за тип основного сесійного ключа квитка.
5. **Атаки за часом виконання (Timing Attacks) при перевірці контрольних сум**:
   Використання стандартної бібліотечної функції `memcmp()` для перевірки криптографічного HMAC автентифікатора або підписів PAC створює небезпечний витік через сторонній канал часу. Функція `memcmp()` перериває сканування на першому ж байті, що не збігся. Зловмисник у локальній мережі може статистично вимірювати час обробки відхиленого пакета і побайтово відновлювати валідну контрольну суму (Padding Oracle / Timing Attack). Перевірка підписів має виконуватися виключно за константний час (`O(1)` відносно змісту) за допомогою функцій на кшталт `CRYPTO_memcmp()` або побітового накопичення різниці через XOR по всіх байтах масиву без раннього виходу з циклу.

## Безпечне очищення секретів у пам'яті (Memory Zeroization)

Критичним аспектом безпеки серверного коду автентифікації є гарантоване знищення сесійних ключів та паролів в оперативній пам'яті після завершення валідації.

Звичайний виклик `memset(key, 0, len)` часто оптимізується компілятором: якщо компілятор (GCC або Clang на рівні оптимізації `-O2` чи `-O3`) виявляє, що буфер `key` є локальною змінною на стеку і більше не читається перед виходом із функції, він повністю видаляє інструкцію занулення як мертвий код (Dead Store Elimination). У результаті сесійні ключі залишаються у відкритому вигляді в неініціалізованих фреймах стека або купі процесу. При виникненні аварійного дампу пам'яті (Core Dump) або експлуатації вразливостей витоку пам'яті (Heartbleed-подібні атаки) зловмисник може вилучити сесійні ключі сотень користувачів.

У промисловому коді використовуються стійкі до оптимізацій функції очищення:

:::tabs
```c
void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}
```
```cpp
#include <span>
#include <cstdint>
#include <atomic>

template <typename T, size_t N>
void secure_memzero(std::span<T, N> buffer) noexcept {
    auto* ptr = static_cast<volatile uint8_t*>(static_cast<void*>(buffer.data()));
    size_t bytes = buffer.size_bytes();
    while (bytes--) {
        *ptr++ = 0;
    }
    std::atomic_signal_fence(std::memory_order_seq_cst);
}
```
:::

## Простеження та діагностика в реальних системах

Для налагодження помилок обробки `AP-REQ` на рівні операційної системи застосовується комплекс стандартних утиліт командного рядка:

1. **`klist -e`**: Відображає вміст клієнтського кешу облікових даних (ccache). Дозволяє перевірити точний тип шифрування (наприклад, `aes256-cts-hmac-sha1-96`), час життя квитка та наявність прапорців `FORWARDABLE` чи `RENEWABLE`.
2. **`kvno <SPN>`**: Виконує запит до TGS на отримання квитка для конкретного сервісу та друкує версію ключа (`kvno`), записану в KDC. Серверний адміністратор порівнює це значення з `kvno` у файлі `/etc/krb5.keytab` за допомогою команди `klist -k -e /etc/krb5.keytab`. Невідповідність номерів версій є найчастішою причиною помилки `KRB_AP_ERR_BAD_INTEGRITY`.
3. **Змінна оточення `KRB5_TRACE`**: Вмикає детальний журнал виконання у внутрішніх бібліотеках MIT Kerberos або Heimdal:

```bash
export KRB5_TRACE=/dev/stderr
kinit alice@EXAMPLE.ORG
```

При цьому в термінал виводиться повний покроковий лог: обрання шифрів, розрахунок солі, відправка `AS-REQ`, перевірка часових міток `PA-ENC-TIMESTAMP`, десеріалізація ASN.1 та запис у replay cache.



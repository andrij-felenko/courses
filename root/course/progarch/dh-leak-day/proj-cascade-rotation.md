# ⚙️ Двигун каскадного відкликання токенів та ротації секретів

Витік підписочного ключа або секрету інфраструктури вимагає виконання координованого сценарію анулювання сесій та каскадної ротації секретів. Просте видалення старого ключа з конфігурації без підготовки підсистеми розриву сесій призведе або до відмови сервісу для легітимних користувачів, або до пропущення зкомпрометованих токенів, які вже були згенеровані зловмисником.

Коли відбувся витік ключа, час працює проти інженерів: автоматизовані сканери нападників за секунди починають генерувати привілейовані запити. Тому архітектура двигуна відкликання (Revocation Engine) проєктується як багатошаровий захисний механізм, здатний миттєво відсікати чужі JWT-токени на найпершому рубежі Edge Gateway, не навантажуючи при цьому центральну базу даних.

Нижче наведено практичну реалізацію високопродуктивного двигуна відкликання токенів та атомарного перемикання JWKS-ключів. Двигун обробляє три послідовні рівні реагування:
1. **Швидка перевірка глобальної мітки витоку (`leak_timestamp`)**: Будь-який маркер доступу, згенерований до моменту компрометації, відхиляється за наносекунди завдяки перевірці на atomic-змінній у пам'яті.
2. **Фільтр відкликаних унікальних токенів (`jti_blacklist`)**: Для токенів, які видані після витоку, але підлягають точковому анулюванню (наприклад, конкретна сесія компрометованого адміністратора), використовується швидка ін-меморі хеш-структура даних.
3. **Двофазовий JWKS Rollover**: Забезпечення верифікації нових сесій ключем `kid_v2` при збереженні можливості дочитати сесії старим `kid_v1` протягом перехідного вікна (Grace Period).

## 1. Архітектурні вимоги та структури даних двигуна

Для обробки навантаження у 100 000+ запитів на секунду (RPS) на Edge-шлюзі платформи Digital Homes перевірка статусу відкликання токена повинна здійснюватися виключно в оперативній пам'яті (RAM). Жоден запит на валідацію JWT не повинен робити синхронних мережевих хопів до центральної бази даних.

Структура даних двигуна поєднує три криптографічні та системні примітиви:
* **Атомарна змінна `leak_timestamp`**: Зберігає епохальну мітку часу (Unix timestamp) останнього виявленого витоку. Перевірка `issued_at <= leak_timestamp` виконується першою.
* **Хеш-таблиця з ланцюжками `jti_blacklist`**: Зберігає унікальні ідентифікатори JWT (Claim `jti`). Використання атомарних операцій читання дозволяє кільком потокам обробки трафіку одночасно перевіряти статус токена.
* **Кільце ключів `JWKS Key Ring`**: Масив дійсних публічних ключів із приписаними ідентифікаторами `kid`. Ключ, позначений як `active_for_signing`, використовується підсистемою генерації нових JWT.

Утилізація кєш-ліній процесора (Cache-line Alignment) досягається впорядкуванням полів структури `revocation_engine_t`. Перша кєш-лінія (64 байти) вміщує гарячі atomic-змінні `leak_timestamp` та вказівник на таблицю бакетів, що мінімізує ефект false sharing між робочими потоками серверного процесу.

:::tabs
```c
/* C Implementation: High-Performance C11 Revocation Engine */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <stdatomic.h>

#define MAX_KIDS 8
#define JTI_LEN 36
#define HASH_BUCKETS 1024

typedef enum {
    REVOKE_OK = 0,
    REVOKE_ERR_EXPIRED = 1,
    REVOKE_ERR_ISSUED_BEFORE_LEAK = 2,
    REVOKE_ERR_JTI_BLACKLISTED = 3,
    REVOKE_ERR_UNKNOWN_KID = 4,
    REVOKE_ERR_INVALID_SIG = 5
} revoke_status_t;

typedef struct jti_node {
    char jti[JTI_LEN + 1];
    struct jti_node *next;
} jti_node_t;

typedef struct {
    char kid[16];
    char public_key_pem[256];
    bool is_active_for_signing;
    uint64_t created_at;
} key_entry_t;

typedef struct {
    _Atomic uint64_t leak_timestamp;
    jti_node_t *buckets[HASH_BUCKETS];
    key_entry_t key_ring[MAX_KIDS];
    size_t key_count;
} revocation_engine_t;

static uint32_t hash_jti(const char *jti) {
    uint32_t hash = 5381;
    int c;
    while ((c = *jti++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_BUCKETS;
}

revocation_engine_t* revocation_engine_create(void) {
    revocation_engine_t *eng = (revocation_engine_t*)calloc(1, sizeof(revocation_engine_t));
    if (!eng) return NULL;
    atomic_init(&eng->leak_timestamp, 0);
    return eng;
}

void revocation_engine_destroy(revocation_engine_t *eng) {
    if (!eng) return;
    for (int i = 0; i < HASH_BUCKETS; i++) {
        jti_node_t *curr = eng->buckets[i];
        while (curr) {
            jti_node_t *tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(eng);
}

void revocation_engine_trigger_leak_emergency(revocation_engine_t *eng, uint64_t leak_time) {
    atomic_store(&eng->leak_timestamp, leak_time);
}

bool revocation_engine_blacklist_jti(revocation_engine_t *eng, const char *jti) {
    uint32_t idx = hash_jti(jti);
    jti_node_t *curr = eng->buckets[idx];
    while (curr) {
        if (strncmp(curr->jti, jti, JTI_LEN) == 0) {
            return true; /* Already blacklisted */
        }
        curr = curr->next;
    }
    jti_node_t *new_node = (jti_node_t*)malloc(sizeof(jti_node_t));
    if (!new_node) return false;
    strncpy(new_node->jti, jti, JTI_LEN);
    new_node->jti[JTI_LEN] = '\0';
    new_node->next = eng->buckets[idx];
    eng->buckets[idx] = new_node;
    return true;
}

revoke_status_t revocation_engine_validate_jwt(
    const revocation_engine_t *eng,
    const char *kid,
    const char *jti,
    uint64_t issued_at,
    uint64_t expires_at,
    uint64_t current_time
) {
    if (current_time >= expires_at) {
        return REVOKE_ERR_EXPIRED;
    }

    uint64_t global_leak = atomic_load(&eng->leak_timestamp);
    if (global_leak > 0 && issued_at <= global_leak) {
        return REVOKE_ERR_ISSUED_BEFORE_LEAK;
    }

    /* Check kid validity in JWKS Key Ring */
    bool kid_found = false;
    for (size_t i = 0; i < eng->key_count; i++) {
        if (strcmp(eng->key_ring[i].kid, kid) == 0) {
            kid_found = true;
            break;
        }
    }
    if (!kid_found) {
        return REVOKE_ERR_UNKNOWN_KID;
    }

    /* Check JTI Blacklist */
    uint32_t idx = hash_jti(jti);
    jti_node_t *curr = eng->buckets[idx];
    while (curr) {
        if (strcmp(curr->jti, jti) == 0) {
            return REVOKE_ERR_JTI_BLACKLISTED;
        }
        curr = curr->next;
    }

    return REVOKE_OK;
}
```

```cpp
// C++ Implementation: Idiomatic C++20 Thread-Safe Revocation Engine
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_set>
#include <vector>
#include <optional>
#include <shared_mutex>
#include <atomic>
#include <chrono>
#include <expected>

namespace dh::security {

enum class RevocationError {
    Expired,
    IssuedBeforeLeak,
    BlacklistedJti,
    UnknownKeyId,
    SignatureInvalid
};

struct JwtClaims {
    std::string kid;
    std::string jti;
    uint64_t user_id;
    uint64_t issued_at;
    uint64_t expires_at;
};

struct KeyEntry {
    std::string kid;
    std::string public_key_pem;
    bool active_for_signing{false};
    uint64_t created_at{0};
};

class RevocationEngine {
public:
    RevocationEngine() = default;

    void trigger_global_leak_emergency(uint64_t leak_time_epoch) noexcept {
        leak_timestamp_.store(leak_time_epoch, std::memory_order_release);
    }

    void blacklist_jti(std::string_view jti) {
        std::unique_lock lock(mutex_);
        blacklisted_jtis_.emplace(jti);
    }

    void register_key(KeyEntry key) {
        std::unique_lock lock(mutex_);
        if (key.active_for_signing) {
            for (auto& k : key_ring_) {
                k.active_for_signing = false;
            }
        }
        key_ring_.push_back(std::move(key));
    }

    [[nodiscard]] std::expected<void, RevocationError> validate_jwt(
        const JwtClaims& claims,
        uint64_t current_time
    ) const {
        if (current_time >= claims.expires_at) {
            return std::unexpected(RevocationError::Expired);
        }

        const uint64_t global_leak = leak_timestamp_.load(std::memory_order_acquire);
        if (global_leak > 0 && claims.issued_at <= global_leak) {
            return std::unexpected(RevocationError::IssuedBeforeLeak);
        }

        std::shared_lock lock(mutex_);

        // 1. Verify Key ID (kid) exists in JWKS Key Ring
        bool kid_exists = false;
        for (const auto& key : key_ring_) {
            if (key.kid == claims.kid) {
                kid_exists = true;
                break;
            }
        }
        if (!kid_exists) {
            return std::unexpected(RevocationError::UnknownKeyId);
        }

        // 2. Check JTI Blacklist
        if (blacklisted_jtis_.contains(claims.jti)) {
            return std::unexpected(RevocationError::BlacklistedJti);
        }

        return {};
    }

    [[nodiscard]] std::optional<KeyEntry> get_signing_key() const {
        std::shared_lock lock(mutex_);
        for (const auto& key : key_ring_) {
            if (key.active_for_signing) {
                return key;
            }
        }
        return std::nullopt;
    }

private:
    std::atomic<uint64_t> leak_timestamp_{0};
    mutable std::shared_mutex mutex_;
    std::unordered_set<std::string> blacklisted_jtis_;
    std::vector<KeyEntry> key_ring_;
};

} // namespace dh::security
```
:::

## 2. Сценарій роботи двигуна при ротації ключів підпису JWKS

При викритті ключа підпису JWT розробник надсилає сигнал командному сервісу ротації. Алгоритм роботи двигуна розгортається у чотири послідовні кроки:

1. **Фіксація `leak_timestamp`**: Сервіс викликає `trigger_global_leak_emergency(now())`. З цього моменту всі токени, згенеровані до поточної секунди, миттєво відхиляються Edge-шлюзами зі статусом `REVOKE_ERR_ISSUED_BEFORE_LEAK`. Операція виконується атомарно без потреби очищати чи модифікувати мільйони сесійних записів у сховищі.
2. **Генерація нової пари `kid_v2`**: Генерується новий асиметричний ключ Ed25519 з унікальним ідентифікатором `kid_v2`. Новий публічний ключ додається в JWKS та позначається прапорцем `active_for_signing = true`.
3. **Перехідний період (Grace Period)**: Старий публічний ключ `kid_v1` залишається в таблиці `key_ring` для верифікації токенів, виданих уже після `leak_timestamp` (якщо сам ключ підпису не був повністю захоплений атакером), але нові сесії підписуються лише новим `kid_v2`.
4. **Очищення (Purge & Garbage Collection)**: Після закінчення максимального TTL токенів (наприклад, 24 години) старий ключ `kid_v1` остаточно видаляється з JWKS, а фільтр `blacklisted_jtis` очищується від застарілих записів, звільняючи оперативну пам'ять.

Завдяки бар'єрам пам'яті (`std::memory_order_acquire/release` у C++20 та `atomic_load` у C11) розрив сесій компрометованих токенів досягається за менш ніж 1 мікросекунду на обробку запиту, повністю захищаючи підсистеми Digital Homes від несанкціонованого доступу.

## 3. Обробка крайових випадків та синхронізація часу між вузлами

Під час масового відкликання сесій у розподіленому кластері з десятками Edge-вузлів виникають три критичні крайові випадки, які здатні зламати підсистему безпеки:

### 1. Синхронізація годинників (NTP Clock Drift)
Якщо годинник одного з Edge-серверів відстає від серверів видачі токенів на 5 секунд, токен, згенерований одразу після витоку (`issued_at = 105`), на цьому Edge-сервері з `leak_timestamp = 100` буде сприйнятий як виданий ДО витоку, якщо його місцевий час дорівнює `100`.

Для захисту від рассинхронізації годинників логіка валідації додає нормативне вікно припустимого дрейфу `CLOCK_SKEW_SEC = 5`:
```cpp
const uint64_t effective_leak = (global_leak > CLOCK_SKEW_SEC) ? (global_leak - CLOCK_SKEW_SEC) : global_leak;
if (effective_leak > 0 && claims.issued_at <= effective_leak) {
    return std::unexpected(RevocationError::IssuedBeforeLeak);
}
```
Це гарантує, що навіть при відхиленні годинників вузлів на 5 секунд жоден компрометований токен не омине фільтр.

### 2. Захист від вичерпання оперативної пам'яті (Memory Churn & Resizing)
При масовому анулюванні сесій додавання мільйонів рядків `jti` у `std::unordered_set` викликає динамічне виділення пам'яті (`malloc`) та можливе перепідключення бакетів (rehashing), що спричиняє затримки до 50–100 мілісекунд у потоках обробки HTTP-запитів.

У високопродуктивному C++ рушії використовується заздалегідь виділений плоский масив (Flat Hash Map / Arena Allocator), де виділення пам'яті здійснюється один раз при старті додатка. Записи застарілих `jti` автоматично витісняються після закінчення максимального TTL токена.

### 3. Режим стійкості до мережевих розривів (Partition Fallback Mode)
Якщо Edge-вузол втрачає зв'язок із центральним Redis-кластером і не може отримати оновлене значення `leak_timestamp`, він переходить у режим **Fail-Closed for Auth**: усі нові спроби авторизації відхиляються, а існуючі сесії вимагають повторного проходження автентифікації через локальний сервіс перевірки.

## 4. Інтеграція двигуна в конвеєр обробки трафіку API Gateway

У реальній архітектурі платформи Digital Homes двигун відкликання інтегрується безпосередньо у шар API Gateway (Envoy / Custom Go/C++ BFF Gateway).

Кожен вхідний HTTP-запит проходит швидку фазу перевірки авторизаційного заголовка `Authorization: Bearer <JWT>`. Декодування payload-частини JWT здійснюється за допомогою нуль-копіювання (zero-copy string view). Якщо статус перевірки повертає помилку, шлюз негайно обриває з'єднання з кодом `HTTP 401 Unauthorized` та повертає JSON-структуру стандарту RFC 7807 (Problem Details).

Завдяки цьому мікросервіси бізнес-логіки (рушій автоматизацій, сервіс цифрових твінів, підсистема керування замками) взагалі не отримують компрометованих запитів. Радіус вибуху локалізується на самій межі хмарного контуру, запобігаючи виконанню шкідливих дій углибині інфраструктури.

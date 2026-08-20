# ⚙️ Верифікатор підписів API з часовим вікном та кешем одноразових чисел

У прикладних веб-інтерфейсах (REST API, Webhooks, платіжні шлюзи) з'єднання між клієнтом і сервером є короткоживучими і не зберігають постійного транспортного стану. Для захисту від повторного відтворення застосовують схему з підписаною клієнтом часовою міткою, одноразовим псевдовипадковим числом (англ. *nonce*) та оперативним кешем використаних ідентифікаторів.

Нижче наведено промисловий модуль перевірки API-запитів із кільцевим буфером Nonce, контролем розсинхронізації годинників (Clock Skew) та верифікацією підпису в константному часі.

---

### Архітектура та етапи валідації запиту

Кожен вхідний запит передає три обов'язкові криптографічні атрибути:
1. **`Timestamp`** — час створення запиту клієнтом за шкалою UTC.
2. **`Nonce`** — 16-байтний криптографічно стійкий випадковий ідентифікатор (UUIDv4 або 128 біт від CSPRNG).
3. **`Signature`** — HMAC-SHA256 підпис над конкатенацією методу, шляху, тіла запиту, часової мітки та Nonce:
   `Signature = HMAC_SHA256(SecretKey, Method || Path || Timestamp || Nonce || Body)`

Сервер виконує чотири послідовні перевірки:

```
[Вхідний API-запит]
       │
       ▼
1. Чи |Timestamp - T_now| ≤ Tolerance?  ───► [НІ]  ───► Відхилити: AUTH_TIMESTAMP_SKEW (400)
       │
      [ТАК]
       ▼
2. Чи Nonce знайдено в кеші?             ───► [ТАК] ───► Відхилити: AUTH_REPLAY_DETECTED (409)
       │
      [НІ]
       ▼
3. Чи підпис збігається (Constant-Time)? ───► [НІ]  ───► Відхилити: AUTH_INVALID_SIGNATURE (401)
       │
      [ТАК]
       ▼
4. Зберегти Nonce у кеш з TTL = 2·Tolerance
       │
       ▼
[Виконати бізнес-логіку (200 OK)]
```

#### Проблема розсинхронізації системних годинників (Clock Skew)

У розподілених системах абсолютна синхронізація часу є фізично недосяжною. Навіть при використанні протоколу NTP (Network Time Protocol) апаратні таймери серверів дрейфують через коливання температури кристала кварцового генератора та мережеву асиметрію.

Особливо гостро ця проблема постає у віртуалізованих середовищах (AWS EC2, Kubernetes, Docker) та безсерверних функціях (AWS Lambda):
- **Призупинення віртуальних машин (VM Pause/Resume):** Коли гіпервізор призупиняє контейнер для міграції пам'яті на інший фізичний хост, годинник `CLOCK_REALTIME` може раптово стрибнути вперед на десятки секунд.
- **Стрибкоподібна корекція часу (Clock Step):** Якщо системний демон `ntpd` виявляє завелике відставання, він може скоригувати час стрибком, а не плавним уповільненням ходу годинника (slew), що призводить до миттєвого вильоту запитів за межі вікна толерантності.

Параметр `tolerance_sec` (вікно допуску, зазвичай 300 секунд) вирішує одразу три завдання:
1. **Компенсація дрейфу NTP:** Дозволяє серверам працювати без збоїв при допустимому мережевому розходженні годинників до кількох хвилин.
2. **Захист від запізнення в чергах:** Забезпечує успішну обробку запитів, які затрималися на проміжних проксі-серверах або балансувальниках навантаження.
3. **Обмеження часу життя кешу:** Дозволяє автоматично видаляти старі значення Nonce через фіксований час `2 · tolerance_sec`, запобігаючи нескінченному витоку оперативної пам'яті.

#### Канонізація корисного навантаження (Canonicalization)

Критичною вимогою при підписанні API-запитів є попередня нормалізація (канонізація) всіх компонентів:
- **Шлях URI:** Декодування відсоткових послідовностей (Percent-Encoding) та видалення подвійних слешів.
- **Параметри Query:** Лексикографічне сортування ключів за алфавітом.
- **Тіло запиту:** Використання точного байтового масиву (Raw Bytes) без повторної серіалізації JSON, оскільки зміна порядку полів або пробілів у JSON змінює геш і призводить до помилки верифікації.

#### Ентропія клієнтського генератора Nonce

Генерація Nonce на клієнті зобов'язана спиратися на криптографічно стійкі системні виклики: `getrandom()` у Linux, `arc4random_buf()` у BSD/macOS або `BCryptGenRandom()` у Windows. Використання генератора `rand()` стандартної бібліотеки C неприпустиме: передбачувана послідовність дозволяє зловмиснику згенерувати майбутні значення Nonce і здійснити атаку відмови в обслуговуванні (DoS), заздалегідь надіславши їх на сервер для блокування легітимних викликів.

---

### Чому небезпечне звичайне порівняння `memcmp` (Timing Attacks)

Класична функція порівняння пам'яті `memcmp()` або оператор `==` у мовах програмування працюють за принципом раннього виходу (англ. *early exit*):

:::tabs
```c
// ВРАЗЛИВИЙ КОД: витік байтів через різницю в часі
bool insecure_equals(const uint8_t *a, const uint8_t *b, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        if (a[i] != b[i]) return false; // зупинка на першому ж невірному байті!
    }
    return true;
}
```
```cpp
// ВРАЗЛИВИЙ КОД: витік байтів через різницю в часі
bool insecure_equals(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) {
        if (a[i] != b[i]) return false; // зупинка на першому ж невірному байті!
    }
    return true;
}
```
:::

Якщо перший байт підпису не збігається, функція завершується за 1 такт процесора. Якщо збігаються перші 10 байтів, функція виконує 10 ітерацій циклу. Вимірюючи час відповіді сервера з точністю до наносекунд за допомогою статистичного усереднення тисяч запитів, зловмисник може по черзі підібрати всі 32 байти HMAC-підпису без знання таємного ключа.

Функція `crypto_verify_equal()` використовує порозрядне бітове накопичення `result |= (a[i] ^ b[i])` і завжди проходить усі байти масиву до кінця, гарантуючи абсолютно однаковий час виконання незалежно від збігу даних.

---

### Вихідний код реалізації (C та C++)

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
#include <assert.h>

#define NONCE_LEN 16
#define DIGEST_LEN 32
#define NONCE_CACHE_CAPACITY 1024
#define DEFAULT_SKEW_TOLERANCE_SEC 300

typedef enum {
    AUTH_OK = 0,
    AUTH_TIMESTAMP_SKEW = 1,
    AUTH_REPLAY_DETECTED = 2,
    AUTH_INVALID_SIGNATURE = 3
} auth_result_t;

typedef struct {
    uint8_t nonce[NONCE_LEN];
    time_t expires_at;
    bool occupied;
} nonce_entry_t;

typedef struct {
    nonce_entry_t entries[NONCE_CACHE_CAPACITY];
    size_t next_idx;
    uint32_t tolerance_sec;
} replay_guard_t;

// Порівняння байтових масивів у константному часі (захист від Timing Attacks)
static bool crypto_verify_equal(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

// Ініціалізація захисного фільтра
void replay_guard_init(replay_guard_t *g, uint32_t tolerance_sec) {
    memset(g->entries, 0, sizeof(g->entries));
    g->next_idx = 0;
    g->tolerance_sec = (tolerance_sec > 0) ? tolerance_sec : DEFAULT_SKEW_TOLERANCE_SEC;
}

// Повна перевірка запиту та фіксація Nonce у разі успіху
auth_result_t replay_guard_verify(
    replay_guard_t *g,
    const uint8_t nonce[NONCE_LEN],
    time_t req_timestamp,
    time_t now,
    const uint8_t expected_sig[DIGEST_LEN],
    const uint8_t provided_sig[DIGEST_LEN]
) {
    // 1. Перевірка допустимого відхилення часової мітки
    int64_t diff = (int64_t)now - (int64_t)req_timestamp;
    if (diff < -(int64_t)g->tolerance_sec || diff > (int64_t)g->tolerance_sec) {
        return AUTH_TIMESTAMP_SKEW;
    }

    // 2. Перевірка наявності Nonce в кеші
    for (size_t i = 0; i < NONCE_CACHE_CAPACITY; ++i) {
        if (g->entries[i].occupied && g->entries[i].expires_at >= now) {
            if (memcmp(g->entries[i].nonce, nonce, NONCE_LEN) == 0) {
                return AUTH_REPLAY_DETECTED;
            }
        }
    }

    // 3. Константно-часова перевірка цифрового підпису / HMAC
    if (!crypto_verify_equal(expected_sig, provided_sig, DIGEST_LEN)) {
        return AUTH_INVALID_SIGNATURE;
    }

    // 4. Успіх: фіксуємо Nonce у кільцевому буфері кешу
    nonce_entry_t *entry = &g->entries[g->next_idx];
    memcpy(entry->nonce, nonce, NONCE_LEN);
    entry->expires_at = now + (time_t)(2 * g->tolerance_sec);
    entry->occupied = true;

    g->next_idx = (g->next_idx + 1) % NONCE_CACHE_CAPACITY;
    return AUTH_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <chrono>
#include <algorithm>
#include <iostream>
#include <cassert>

enum class AuthResult : uint8_t {
    Ok = 0,
    TimestampSkew = 1,
    ReplayDetected = 2,
    InvalidSignature = 3
};

template <size_t CacheCapacity = 1024, size_t NonceSize = 16, size_t DigestSize = 32>
class ReplayGuard {
public:
    using Nonce = std::array<uint8_t, NonceSize>;
    using Digest = std::array<uint8_t, DigestSize>;

    explicit constexpr ReplayGuard(std::chrono::seconds tolerance = std::chrono::seconds(300)) noexcept
        : tolerance_(tolerance) {}

    [[nodiscard]] AuthResult verify_and_record(
        const Nonce& nonce,
        std::chrono::system_clock::time_point req_time,
        std::chrono::system_clock::time_point now,
        const Digest& expected_sig,
        const Digest& provided_sig
    ) noexcept {
        // 1. Перевірка вікна допустимої часової розсинхронізації
        const auto diff = std::chrono::duration_cast<std::chrono::seconds>(now - req_time);
        if (diff < -tolerance_ || diff > tolerance_) {
            return AuthResult::TimestampSkew;
        }

        // 2. Перевірка кешу одноразових чисел
        for (const auto& entry : entries_) {
            if (entry.occupied && entry.expires_at >= now) {
                if (entry.nonce == nonce) {
                    return AuthResult::ReplayDetected;
                }
            }
        }

        // 3. Порівняння підпису в константному часі
        if (!constant_time_equals(expected_sig, provided_sig)) {
            return AuthResult::InvalidSignature;
        }

        // 4. Запис Nonce у кільцевий буфер
        auto& entry = entries_[next_idx_];
        entry.nonce = nonce;
        entry.expires_at = now + (tolerance_ * 2);
        entry.occupied = true;

        next_idx_ = (next_idx_ + 1) % CacheCapacity;
        return AuthResult::Ok;
    }

private:
    struct CacheEntry {
        Nonce nonce{};
        std::chrono::system_clock::time_point expires_at{};
        bool occupied{false};
    };

    static bool constant_time_equals(const Digest& a, const Digest& b) noexcept {
        uint8_t diff = 0;
        for (size_t i = 0; i < DigestSize; ++i) {
            diff |= (a[i] ^ b[i]);
        }
        return diff == 0;
    }

    std::chrono::seconds tolerance_{300};
    std::array<CacheEntry, CacheCapacity> entries_{};
    size_t next_idx_{0};
};
```
:::

---

### Тестування та перевірка сценаріїв атак

:::tabs
```c
void test_replay_guard(void) {
    replay_guard_t g;
    replay_guard_init(&g, 300); // толерантність 300 секунд

    time_t now = 1755723600;
    uint8_t nonce1[NONCE_LEN] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    uint8_t sig_valid[DIGEST_LEN] = {0xAA};
    uint8_t sig_invalid[DIGEST_LEN] = {0xBB};

    // Сценарій 1: Легітимний запит приймається
    assert(replay_guard_verify(&g, nonce1, now - 10, now, sig_valid, sig_valid) == AUTH_OK);

    // Сценарій 2: Повторний запит із тим самим Nonce відхиляється
    assert(replay_guard_verify(&g, nonce1, now - 5, now, sig_valid, sig_valid) == AUTH_REPLAY_DETECTED);

    // Сценарій 3: Застарілий запит (відхилення 400 секунд > 300 с)
    uint8_t nonce2[NONCE_LEN] = {2};
    assert(replay_guard_verify(&g, nonce2, now - 400, now, sig_valid, sig_valid) == AUTH_TIMESTAMP_SKEW);

    // Сценарій 4: Запит із майбутнього (годинник клієнта поспішає на 500 с)
    assert(replay_guard_verify(&g, nonce2, now + 500, now, sig_valid, sig_valid) == AUTH_TIMESTAMP_SKEW);

    // Сценарій 5: Некоректний підпис відхиляється
    assert(replay_guard_verify(&g, nonce2, now - 10, now, sig_valid, sig_invalid) == AUTH_INVALID_SIGNATURE);
}
```
```cpp
void test_replay_guard_cpp() {
    ReplayGuard<1024> g(std::chrono::seconds(300));

    const auto now = std::chrono::system_clock::from_time_t(1755723600);
    ReplayGuard<1024>::Nonce nonce1{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    ReplayGuard<1024>::Nonce nonce2{2};

    ReplayGuard<1024>::Digest sig_valid{};
    sig_valid.fill(0xAA);
    ReplayGuard<1024>::Digest sig_invalid{};
    sig_invalid.fill(0xBB);

    // Сценарій 1: Легітимний запит приймається
    assert(g.verify_and_record(nonce1, now - std::chrono::seconds(10), now, sig_valid, sig_valid) == AuthResult::Ok);

    // Сценарій 2: Повтор того самого Nonce відхиляється
    assert(g.verify_and_record(nonce1, now - std::chrono::seconds(5), now, sig_valid, sig_valid) == AuthResult::ReplayDetected);

    // Сценарій 3: Застарілий запит
    assert(g.verify_and_record(nonce2, now - std::chrono::seconds(400), now, sig_valid, sig_valid) == AuthResult::TimestampSkew);

    // Сценарій 4: Запит із далекого майбутнього
    assert(g.verify_and_record(nonce2, now + std::chrono::seconds(500), now, sig_valid, sig_valid) == AuthResult::TimestampSkew);

    // Сценарій 5: Невалідний підпис
    assert(g.verify_and_record(nonce2, now - std::chrono::seconds(10), now, sig_valid, sig_invalid) == AuthResult::InvalidSignature);
}
```
:::

---

### Розподілена архітектура та атомарні операції в Redis

У багатосерверних кластерах (Kubernetes / балансувальник навантаження) запити одного клієнта можуть потрапляти на різні вузли. Збереження Nonce у локальній пам'яті процесу створює вразливість «гонки перевірки та використання» (TOCTOU): зловмисник може надіслати копію запиту на два різні сервери одночасно.

Для розподіленого середовища використовують Redis з атомарною командою `SET`:

```bash
SET nonce:c8f1d2e3b4a5 "1" NX EX 600
```

- **Ключ:** `nonce:<значення>`
- **Прапорець `NX` (Set if Not eXists):** Гарантує, що ключ буде встановлено лише тоді, коли його ще немає в базі. Якщо ключ уже існує, Redis повертає `nil` (помилка дубліката), що атомарно блокує паралельні replay-запити без застосування дорогих розподілених блокувань.
- **Прапорець `EX 600` (Expire in Seconds):** Автоматично видаляє ключ із пам'яті через 600 секунд (подвійне вікно толерантності), запобігаючи нескінченному зростанню кешу.

#### Реалізація за допомогою Lua-скрипта в Redis

У високонавантажених системах для об'єднання перевірки та фіксації в єдиний мережевий виклик використовують Lua-скрипти, які виконуються атомарно на стороні сервера Redis:

```lua
-- KEYS[1] = nonce_key, ARGV[1] = ttl_seconds
if redis.call("EXISTS", KEYS[1]) == 1 then
    return 0 -- Nonce знайдено -> Replay Attack
else
    redis.call("SET", KEYS[1], "1", "EX", ARGV[1])
    return 1 -- Успішно зафіксовано новий Nonce
end
```

Така схема дозволяє масштабувати API-шлюзи горизонтально на сотні вузлів із єдиним захищеним станом дедуплікації.

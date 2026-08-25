# ⚙️ Реалізація рушія виклику-відповіді: непередбачувані nonces, HMAC і захист від повтору

У мережевих протоколах автентифікації надійність схеми «виклик-відповідь» визначається не лише стійкістю математичних примітивів, а й інженерною дисципліною під час обробки стану, генерації випадкових чисел, серіалізації даних та перевірки криптографічних доказів. Навіть криптографічно стійкий алгоритм HMAC-SHA256 стає беззахисним, якщо сервер використовує передбачуваний генератор псевдовипадкових чисел `rand()`, порівнює геші вразливою до часових атак функцією `memcmp()`, або не контролює часове вікно свіжості виклику. Нижче наведено детальний розбір та реалізацію промислового модуля симетричної автентифікації на базі безстанового талона виклику (*Stateless Challenge Token*), що гарантує стійкість проти атак повтору (*Replay Attacks*), підміни контексту дії (*Action Confusion*) та витоків через бічні канали вимірювання часу (*Timing Side-Channels*).

## Архітектура перевіряльника: стан проти безстановості

Коли клієнт звертається до сервера з проханням розпочати сесію автентифікації, перевіряльник повинен створити унікальний одноразовий виклик (*nonce*). На цьому етапі постає ключове архітектурне питання: де і як зберігати згенерований виклик до моменту, поки клієнт не поверне відповідь?

### Пастка сховища станів (Stateful Bottleneck)
Найпростіший підхід полягає в тому, щоб згенерувати випадковий масив байтів, записати його в оперативну пам'ять сервера (наприклад, у хеш-таблицю `active_challenges`), встановити таймер життя та відправити значення клієнту. Коли приходить відповідь, сервер шукає збережений запис у таблиці, обчислює очікуваний HMAC і видаляє запис після перевірки.

Ця схема створює дві критичні вразливості:
1. **Вичерпання пам'яті (DoS-атака):** Зловмисник може згенерувати мільйон фіктивних запитів на автентифікацію в секунду з підроблених IP-адрес, змушуючи сервер виділяти пам'ять під нові й нові челенджі. Сервер вичерпає оперативну пам'ять (*RAM exhaustion*) задовго до того, як спливе термін дії першого виклику.
2. **Проблема розподілених кластерів:** Якщо за балансувальником навантаження працюють десять екземплярів сервера, запит клієнта на генерацію виклику потрапить на сервер A, а повторний запит із відповіддю — на сервер B. Серверу B доведеться або звертатися до централізованої спільної бази даних (що створює вузьке місце затримки мережі), або підтримувати липкі сесії (*sticky sessions*).

### Безстановий талон виклику (Stateless Challenge Token)
Елегантним вирішенням цієї проблеми є перенесення зберігання стану на бік самого клієнта за допомогою криптографічного талона. Сервер не зберігає у своїй пам'яті нічого, крім єдиного довготривалого симетричного секрету `K_server`.

Структура безстанового талона об'єднує три складові:
1. **Випадковий nonce (16 байтів):** Забезпечує унікальність та ентропію кожної спроби.
2. **Мітка часу Timestamp (8 байтів):** Фіксує час створення виклику в секундах (Unix Epoch) для обмеження періоду його дійсності.
3. **Підпис сервера HMAC (32 байти):** Автентифікована згортка `HMAC-SHA256(K_server, Nonce || Timestamp || ClientID)`.

```
+-------------------+--------------------+---------------------------------------+
|  Nonce (16 байтів)| Timestamp (8 байт) | HMAC-SHA256 сервера (32 байти)        |
+-------------------+--------------------+---------------------------------------+
|  Ентропія CSPRNG  |  Unix Epoch секунд | HMAC(K_server, Nonce||Time||ClientID) |
+-------------------+--------------------+---------------------------------------+
```

Коли клієнт повертає талон разом зі своєю відповіддю, сервер спочатку повторно обчислює HMAC над полями `Nonce`, `Timestamp` та `ClientID`, використовуючи свій внутрішній ключ `K_server`. Якщо підпис не збігається хоча б в одному біті, це означає, що талон було підроблено або модифіковано, і сервер миттєво відкидає запит без звернення до бази паролів.

## Ентропія та ймовірність колізій випадкового виклику

Надійність захисту від атак повтору та попередньо обчислених словників безпосередньо залежить від розміру простору станів виклику.

Якщо довжина nonce становить `b` бітів, загальна кількість можливих значень дорівнює `N = 2^b`. Відповідно до парадоксу днів народження (*Birthday Paradox*), ймовірність `P` виникнення хоча б однієї колізії після генерації `k` випадкових викликів наближено описується формулою:

```
P(колізії) ≈ 1 - exp( - (k · (k - 1)) / (2 · 2^b) )
```

Для малого 32-бітного nonce (`b = 32`, `2^32 ≈ 4.29 · 10^9`) колізія з імовірністю понад 50% виникне вже після генерації лише `k ≈ 77 000` викликів. У високонавантаженій системі із 10 000 запитів на секунду колізія траплятиметься кожні 8 секунд. Це дозволило б зловмиснику записувати відповіді й успішно перегравати їх при повторенні того самого числа.

При використанні 128-бітного nonce (`b = 128`, `2^128 ≈ 3.4 · 10^38`):
- Для досягнення ймовірності колізії `P = 10^-6` (один шанс на мільйон) системі необхідно згенерувати понад `k ≈ 8.2 · 10^14` викликів.
- Навіть за швидкості 1 мільйон викликів на секунду такий обсяг буде досягнуто лише через 26 000 років безперервної роботи.

Тому 128 бітів (16 байтів) криптографічно стійкої ентропії, отриманої з системного генератора випадкових чисел (CSPRNG — `/dev/urandom` у Linux або `BCryptGenRandom` у Windows), є стандартом безпеки для протоколів виклику-відповіді.

## Повний робочий код клієнта і сервера

Нижче наведено повноцінний промисловий модуль мовами C (стандарт C99) та C++ (стандарт C++20), побудований поверх інтерфейсів OpenSSL EVP API.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <openssl/hmac.h>
#include <openssl/rand.h>

#define NONCE_LEN             16
#define HMAC_LEN              32
#define MAX_CHALLENGE_AGE_SEC 30
#define REPLAY_CACHE_SIZE     256

#pragma pack(push, 1)
typedef struct {
    uint8_t  nonce[NONCE_LEN];
    uint64_t timestamp_sec;
    uint8_t  server_mac[HMAC_LEN];
} challenge_token_t;

typedef struct {
    uint32_t client_id;
    uint8_t  response_mac[HMAC_LEN];
} auth_response_t;
#pragma pack(pop)

/* Циклічний буфер для запам'ятовування використаних nonce */
typedef struct {
    uint8_t nonces[REPLAY_CACHE_SIZE][NONCE_LEN];
    size_t  head;
} replay_cache_t;

/* Порівняння масивів байтів за сталий час (Constant-Time) */
static int constant_time_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *ua = (const uint8_t *)a;
    const uint8_t *ub = (const uint8_t *)b;
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (ua[i] ^ ub[i]);
    }
    return result == 0 ? 0 : -1;
}

/* Генерація безстанового виклику сервером */
int server_create_challenge(const uint8_t *server_key, size_t server_key_len,
                            uint32_t client_id, challenge_token_t *out_token) {
    if (RAND_bytes(out_token->nonce, NONCE_LEN) != 1) {
        return -1;
    }
    out_token->timestamp_sec = (uint64_t)time(NULL);

    /* Обчислення MAC талона: HMAC(K_server, Nonce || Timestamp || ClientID) */
    uint8_t sign_buf[NONCE_LEN + sizeof(uint64_t) + sizeof(uint32_t)];
    memcpy(sign_buf, out_token->nonce, NONCE_LEN);
    memcpy(sign_buf + NONCE_LEN, &out_token->timestamp_sec, sizeof(uint64_t));
    memcpy(sign_buf + NONCE_LEN + sizeof(uint64_t), &client_id, sizeof(uint32_t));

    unsigned int mac_len = 0;
    if (!HMAC(EVP_sha256(), server_key, (int)server_key_len,
              sign_buf, sizeof(sign_buf), out_token->server_mac, &mac_len)) {
        return -1;
    }
    return 0;
}

/* Обчислення відповіді клієнтом: HMAC(K_client, Token || ActionContext) */
int client_compute_response(const uint8_t *client_secret, size_t secret_len,
                            uint32_t client_id,
                            const challenge_token_t *token,
                            const char *action_context,
                            auth_response_t *out_resp) {
    out_resp->client_id = client_id;

    size_t ctx_len = strlen(action_context);
    size_t total_payload = sizeof(challenge_token_t) + ctx_len;
    uint8_t *payload = (uint8_t *)malloc(total_payload);
    if (!payload) return -1;

    memcpy(payload, token, sizeof(challenge_token_t));
    memcpy(payload + sizeof(challenge_token_t), action_context, ctx_len);

    unsigned int mac_len = 0;
    uint8_t *res = HMAC(EVP_sha256(), client_secret, (int)secret_len,
                        payload, total_payload, out_resp->response_mac, &mac_len);
    free(payload);
    return res ? 0 : -1;
}

/* Перевірка відсутності в кеші щойно бачених nonce */
static int check_and_record_nonce(replay_cache_t *cache, const uint8_t *nonce) {
    for (size_t i = 0; i < REPLAY_CACHE_SIZE; ++i) {
        if (constant_time_memcmp(cache->nonces[i], nonce, NONCE_LEN) == 0) {
            return -1; /* Знайдено в кеші: спроба Replay-атаки! */
        }
    }
    memcpy(cache->nonces[cache->head], nonce, NONCE_LEN);
    cache->head = (cache->head + 1) % REPLAY_CACHE_SIZE;
    return 0;
}

/* Верифікація відповіді клієнта сервером */
int server_verify_response(const uint8_t *server_key, size_t server_key_len,
                           const uint8_t *client_secret, size_t client_secret_len,
                           replay_cache_t *cache,
                           const challenge_token_t *token,
                           const auth_response_t *resp,
                           const char *expected_action) {
    /* 1. Перевірка цілісності та автентичності талона сервера */
    uint8_t sign_buf[NONCE_LEN + sizeof(uint64_t) + sizeof(uint32_t)];
    memcpy(sign_buf, token->nonce, NONCE_LEN);
    memcpy(sign_buf + NONCE_LEN, &token->timestamp_sec, sizeof(uint64_t));
    memcpy(sign_buf + NONCE_LEN + sizeof(uint64_t), &resp->client_id, sizeof(uint32_t));

    uint8_t expected_server_mac[HMAC_LEN];
    unsigned int mac_len = 0;
    if (!HMAC(EVP_sha256(), server_key, (int)server_key_len,
              sign_buf, sizeof(sign_buf), expected_server_mac, &mac_len)) {
        return -1;
    }
    if (constant_time_memcmp(token->server_mac, expected_server_mac, HMAC_LEN) != 0) {
        return -2; /* Талон виклику підроблений */
    }

    /* 2. Перевірка свіжості за міткою часу */
    uint64_t now = (uint64_t)time(NULL);
    if (now < token->timestamp_sec || (now - token->timestamp_sec) > MAX_CHALLENGE_AGE_SEC) {
        return -3; /* Термін дії виклику вичерпано або час у майбутньому */
    }

    /* 3. Перевірка кешу повторного використання */
    if (check_and_record_nonce(cache, token->nonce) != 0) {
        return -4; /* Replay Attack: цей nonce уже успішно оброблено */
    }

    /* 4. Перевірка відповіді клієнта на основі його секрету */
    size_t ctx_len = strlen(expected_action);
    size_t total_payload = sizeof(challenge_token_t) + ctx_len;
    uint8_t *payload = (uint8_t *)malloc(total_payload);
    if (!payload) return -1;

    memcpy(payload, token, sizeof(challenge_token_t));
    memcpy(payload + sizeof(challenge_token_t), expected_action, ctx_len);

    uint8_t expected_client_mac[HMAC_LEN];
    HMAC(EVP_sha256(), client_secret, (int)client_secret_len,
         payload, total_payload, expected_client_mac, &mac_len);
    free(payload);

    if (constant_time_memcmp(resp->response_mac, expected_client_mac, HMAC_LEN) != 0) {
        return -5; /* Невірний секрет або контекст операції */
    }

    return 0; /* Успішна автентифікація */
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <string_view>
#include <chrono>
#include <memory>
#include <optional>
#include <algorithm>
#include <openssl/hmac.h>
#include <openssl/rand.h>

namespace crypto_auth {

inline constexpr size_t NonceSize = 16;
inline constexpr size_t HmacSize = 32;
inline constexpr std::chrono::seconds MaxChallengeAge{30};
inline constexpr size_t ReplayCacheCapacity = 256;

#pragma pack(push, 1)
struct ChallengeToken {
    std::array<uint8_t, NonceSize> nonce{};
    uint64_t timestamp_sec{0};
    std::array<uint8_t, HmacSize> server_mac{};
};

struct AuthResponse {
    uint32_t client_id{0};
    std::array<uint8_t, HmacSize> response_mac{};
};
#pragma pack(pop)

enum class VerifyError {
    InternalError,
    InvalidServerMac,
    ExpiredTimestamp,
    ReplayDetected,
    InvalidClientProof
};

/* Порівняння масивів за сталий час для запобігання Timing Attacks */
[[nodiscard]] bool constant_time_equal(std::span<const uint8_t> a,
                                       std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

/* Обчислення HMAC-SHA256 */
[[nodiscard]] std::optional<std::array<uint8_t, HmacSize>>
compute_hmac(std::span<const uint8_t> key, std::span<const uint8_t> data) noexcept {
    std::array<uint8_t, HmacSize> result{};
    unsigned int len = 0;
    if (!HMAC(EVP_sha256(), key.data(), static_cast<int>(key.size()),
              data.data(), data.size(), result.data(), &len)) {
        return std::nullopt;
    }
    return result;
}

class ReplayCache {
public:
    [[nodiscard]] bool test_and_add(const std::array<uint8_t, NonceSize>& nonce) noexcept {
        auto it = std::find_if(cache_.begin(), cache_.end(), [&](const auto& entry) {
            return constant_time_equal(entry, nonce);
        });
        if (it != cache_.end()) {
            return false; /* Знайдено дублікат у вікні свіжості */
        }
        if (cache_.size() >= ReplayCacheCapacity) {
            cache_.erase(cache_.begin());
        }
        cache_.push_back(nonce);
        return true;
    }
private:
    std::vector<std::array<uint8_t, NonceSize>> cache_;
};

class AuthServer {
public:
    explicit AuthServer(std::vector<uint8_t> server_key)
        : server_key_(std::move(server_key)) {}

    [[nodiscard]] std::optional<ChallengeToken>
    create_challenge(uint32_t client_id) const noexcept {
        ChallengeToken token;
        if (RAND_bytes(token.nonce.data(), static_cast<int>(token.nonce.size())) != 1) {
            return std::nullopt;
        }

        const auto now = std::chrono::system_clock::now();
        token.timestamp_sec = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count()
        );

        std::vector<uint8_t> sign_payload;
        sign_payload.reserve(NonceSize + sizeof(uint64_t) + sizeof(uint32_t));
        sign_payload.insert(sign_payload.end(), token.nonce.begin(), token.nonce.end());

        const auto* ts_bytes = reinterpret_cast<const uint8_t*>(&token.timestamp_sec);
        sign_payload.insert(sign_payload.end(), ts_bytes, ts_bytes + sizeof(uint64_t));

        const auto* id_bytes = reinterpret_cast<const uint8_t*>(&client_id);
        sign_payload.insert(sign_payload.end(), id_bytes, id_bytes + sizeof(uint32_t));

        auto mac = compute_hmac(server_key_, sign_payload);
        if (!mac) return std::nullopt;
        token.server_mac = *mac;
        return token;
    }

    [[nodiscard]] std::optional<VerifyError>
    verify_response(const ChallengeToken& token,
                    const AuthResponse& resp,
                    std::span<const uint8_t> client_secret,
                    std::string_view expected_action) noexcept {
        /* 1. Перевірка валідності талона сервера */
        std::vector<uint8_t> sign_payload;
        sign_payload.reserve(NonceSize + sizeof(uint64_t) + sizeof(uint32_t));
        sign_payload.insert(sign_payload.end(), token.nonce.begin(), token.nonce.end());
        const auto* ts_bytes = reinterpret_cast<const uint8_t*>(&token.timestamp_sec);
        sign_payload.insert(sign_payload.end(), ts_bytes, ts_bytes + sizeof(uint64_t));
        const auto* id_bytes = reinterpret_cast<const uint8_t*>(&resp.client_id);
        sign_payload.insert(sign_payload.end(), id_bytes, id_bytes + sizeof(uint32_t));

        auto expected_srv_mac = compute_hmac(server_key_, sign_payload);
        if (!expected_srv_mac || !constant_time_equal(token.server_mac, *expected_srv_mac)) {
            return VerifyError::InvalidServerMac;
        }

        /* 2. Перевірка вікна життя талона */
        const auto now_sec = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );
        if (now_sec < token.timestamp_sec || (now_sec - token.timestamp_sec) > MaxChallengeAge.count()) {
            return VerifyError::ExpiredTimestamp;
        }

        /* 3. Перевірка на повторне використання */
        if (!replay_cache_.test_and_add(token.nonce)) {
            return VerifyError::ReplayDetected;
        }

        /* 4. Перевірка доказу володіння клієнтським секретом */
        std::vector<uint8_t> client_payload;
        const auto* tok_ptr = reinterpret_cast<const uint8_t*>(&token);
        client_payload.insert(client_payload.end(), tok_ptr, tok_ptr + sizeof(ChallengeToken));
        client_payload.insert(client_payload.end(), expected_action.begin(), expected_action.end());

        auto expected_client_mac = compute_hmac(client_secret, client_payload);
        if (!expected_client_mac || !constant_time_equal(resp.response_mac, *expected_client_mac)) {
            return VerifyError::InvalidClientProof;
        }

        return std::nullopt; /* Успішна валідація */
    }

private:
    std::vector<uint8_t> server_key_;
    ReplayCache replay_cache_;
};

class AuthClient {
public:
    [[nodiscard]] static std::optional<AuthResponse>
    compute_response(uint32_t client_id,
                     std::span<const uint8_t> client_secret,
                     const ChallengeToken& token,
                     std::string_view action_context) noexcept {
        std::vector<uint8_t> payload;
        const auto* tok_ptr = reinterpret_cast<const uint8_t*>(&token);
        payload.insert(payload.end(), tok_ptr, tok_ptr + sizeof(ChallengeToken));
        payload.insert(payload.end(), action_context.begin(), action_context.end());

        auto mac = compute_hmac(client_secret, payload);
        if (!mac) return std::nullopt;

        AuthResponse resp;
        resp.client_id = client_id;
        resp.response_mac = *mac;
        return resp;
    }
};

} // namespace crypto_auth
```
:::

## Покроковий розбір конвеєра перевірки

Щоб переконатися у відсутності прихованих вразливостей, простежимо рух байтів на кожному кроці виконання протоколу:

1. **Генерація талона (Server Phase 1):**
   - Сервер викликає функцію `RAND_bytes()` із OpenSSL, яка зчитує 16 байтів із пулу ентропії ядра.
   - Отримує системний час у секундах за допомогою `time(NULL)`.
   - Формує проміжний буфер пам'яті: `[Nonce 16B][Timestamp 8B][ClientID 4B]`.
   - Застосовує `HMAC-SHA256` із довготривалим серверним ключем `K_server`.
   - Упаковує результат у структуру `challenge_token_t` (загальний розмір 56 байтів) і повертає її клієнту.

2. **Обчислення відповіді (Client Phase):**
   - Клієнт отримує структуру `token`.
   - Додає в кінець талона рядок контексту дії, наприклад `"TRANSFER:100:UAH:TO:UA89300001"`.
   - Отримує спільний масив розміром 56 байтів + довжина рядка контексту.
   - Застосовує `HMAC-SHA256` зі своїм персональним секретним ключем `K_client`.
   - Заповнює структуру `auth_response_t` (ідентифікатор клієнта та 32 байти MAC-відповіді) і надсилає назад серверу.

3. **Верифікація на сервері (Server Phase 2):**
   - **Крок 3.1 (Автентичність талона):** Сервер бере `token->nonce`, `token->timestamp_sec` та `resp->client_id` і рахує очікуваний серверний MAC. Порівнює його з `token->server_mac` через функцію `constant_time_memcmp`. Якщо клієнт спробував змінити мітку часу (наприклад, продовжити дію виклику на 1 годину) або підставити чужий `client_id`, перевірка дає збій, і запит відхиляється.
   - **Крок 3.2 (Часове вікно):** Сервер порівнює `now - token->timestamp_sec`. Якщо різниця перевищує 30 секунд, талон визнається застарілим. Це звужує вікно можливостей для перехоплювача.
   - **Крок 3.3 (Антиповтор):** Сервер шукає `token->nonce` у кільцевому буфері останніх 256 оброблених викликів. Якщо nonce знайдено — це атака повтору, запит скидається. Якщо ні — nonce записується на поточну позицію голови буфера.
   - **Крок 3.4 (Перевірка знання секрету):** Сервер дістає з бази даних секретний ключ клієнта `K_client` за його `client_id`, склеює отриманий `token` із очікуваним контекстом операції та обчислює еталонний клієнтський MAC. Фінальне порівняння за сталий час гарантує, що клієнт володіє правильним секретом і підтверджує саме ту дію, яку очікує сервер.

## Захист від атаки віддзеркалення (Reflection Attack)

Якщо протокол передбачає двосторонню автентифікацію (клієнт перевіряє сервер, а сервер перевіряє клієнта) з використанням однакового алгоритму, виникає вразливість **атаки віддзеркалення**:

1. Сервер надсилає клієнту виклик `Challenge_S`.
2. Зловмисник (Eve) паралельно відкриває друге підключення до того самого сервера, видаючи себе за клієнта.
3. Сервер у другій сесії надсилає виклик `Challenge_S2`.
4. Зловмисник у другій сесії надсилає серверу `Challenge_S` як клієнтський челендж. Сервер обчислює відповідь `Resp(Challenge_S)` і повертає її зловмиснику.
5. Зловмисник бере цю готову відповідь від сервера і відправляє її назад у першу сесію як доказ своєї автентичності. Сервер успішно пускає зловмисника, не здогадуючись, що відповів сам собі.

### Розділення напрямків (Domain Separation)
Щоб унеможливити атаку віддзеркалення, у геш-функцію обов'язково вводять несиметричний префікс ролі (*Role-based Domain Separator*):
- Відповідь клієнта серверу підписує дані з рядком `"CLIENT_AUTH:"`.
- Відповідь сервера клієнту підписує дані з рядком `"SERVER_AUTH:"`.

Оскільки `HMAC(K, "CLIENT_AUTH:" || Challenge)` ніколи не дорівнює `HMAC(K, "SERVER_AUTH:" || Challenge)`, відповідь сервера з другої сесії буде негайно відхилена в першій як некоректний підпис.

## Аналіз бічних каналів та часових атак (Timing Attacks)

Однією з найпідступніших атак на протоколи виклику-відповіді є атака на основі вимірювання часу відповіді перевіряльника.

### Чому стандартний memcmp є смертельним
Стандартна функція бібліотеки C `memcmp(const void *s1, const void *s2, size_t n)` оптимізована для максимальної продуктивності. Вона порівнює байти по порядку і негайно завершує виконання, щойно знайде перший незбіг.

:::tabs
```c
/* Вразлива реалізація: вихід за першим незбігом */
int naive_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        if (a[i] != b[i]) {
            return a[i] - b[i]; /* Час повернення залежить від позиції i */
        }
    }
    return 0;
}
```
```cpp
/* Вразлива реалізація на C++: вихід за першим незбігом */
[[nodiscard]] int naive_memcmp(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    const size_t len = std::min(a.size(), b.size());
    for (size_t i = 0; i < len; ++i) {
        if (a[i] != b[i]) {
            return static_cast<int>(a[i]) - static_cast<int>(b[i]);
        }
    }
    return static_cast<int>(a.size()) - static_cast<int>(b.size());
}
```
:::

Нехай правильний HMAC-SHA256 починається з байта `0x8F`.
- Якщо атакуючий надішле випадкову здогадку `0x00...`, функція поверне помилку вже на нульовому байті (час роботи ~5 наносекунд).
- Якщо атакуючий надішле здогадку `0x8F...`, функція успішно порівняє нульовий байт і вийде лише на першому байті (час роботи ~12 наносекунд).

Виконуючи тисячі замірів часу через локальну мережу або з сусіднього процесу на тому самому сервері (застосовуючи методики статистичного усереднення та фільтрації шуму), зловмисник може перебрати всі 256 значень для першого байта. Знайшовши варіант із найбільшим часом відгуку, він фіксує перший байт і переходить до перебору другого.

Замість експоненційного простору складності `256^32 = 2^256` підбір скорочується до лінійної складності:

```
Складність атаки = 32 · 256 = 8 192 спроби
```

Зловмисник здатен зламати 256-бітний криптографічний підпис за кілька секунд звичайним перебором 8 тисяч запитів.

### Механіка constant_time_memcmp
Правильна функція порівняння за сталий час зобов'язана прочитати всі без винятку `len` байтів пам'яті незалежно від того, де виникла розбіжність:

:::tabs
```c
static int constant_time_memcmp_snippet(const void *a, const void *b, size_t len) {
    const uint8_t *ua = (const uint8_t *)a;
    const uint8_t *ub = (const uint8_t *)b;
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (ua[i] ^ ub[i]);
    }
    return result == 0 ? 0 : -1;
}
```
```cpp
[[nodiscard]] bool constant_time_equal_snippet(std::span<const uint8_t> a,
                                              std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}
```
:::

У цій реалізації:
1. Побітова операція `XOR` (`ua[i] ^ ub[i]`) дає нуль тоді й тільки тоді, коли байти повністю збігаються.
2. Побітова операція `OR` (`result |= ...`) накопичує будь-які відмінності. Якщо хоча б один біт у будь-якому байті різниться, змінна `result` стане ненульовою.
3. Цикл завжди виконує рівно `len` ітерацій без умовних переходів `if` всередині тіла, що усуває будь-яку залежність часу виконання та роботи конвеєра передбачення переходів процесора (*Branch Predictor*) від вмісту секретних даних.

## Захист від оптимізацій компілятора та очищення пам'яті

Навіть бездоганно написаний криптографічний алгоритм може бути скомпрометований агресивними оптимізаціями сучасних компіляторів (GCC, Clang, MSVC).

### Проблема усунення мертвого коду (Dead Store Elimination)
Коли функція завершує роботу з секретними ключами або паролями в локальному буфері на стеку, програміст зазвичай викликає `memset(secret_buf, 0, sizeof(secret_buf))`. Проте компілятор бачить, що після виклику `memset` масив `secret_buf` більше ніколи не читається до виходу з функції. Оптимізатор розцінює такий запис як «мертвий» (*dead store*) і повністю викидає виклик `memset` з фінального асемблерного коду.

У результаті секретний ключ лишається лежати на стеку пам'яті процесу. Якщо наступна функція або обробник помилок виділить стек у тій самій області та допустить переповнення буфера або витік через логування (*core dump / uninitialized read*), пароль опиниться у відкритому доступі.

Для гарантованого занулення секретів у пам'яті слід використовувати спеціалізовані бар'єри:
- У C/OpenSSL: функцію `OPENSSL_cleanse(ptr, len)`.
- У стандарті C23 / POSIX: функцію `memset_explicit()` або `explicit_bzero()`.
- У чистому коді C/C++: вказівник із кваліфікатором `volatile`, запис через який компілятор не має права видаляти:

:::tabs
```c
static void secure_zero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0;
    }
}
```
```cpp
void secure_zero(std::span<uint8_t> buffer) noexcept {
    volatile auto* p = buffer.data();
    for (size_t i = 0; i < buffer.size(); ++i) {
        p[i] = 0;
    }
}
```
:::

## Часовий дрейф годинників і розподілені системи

У реальних дата-центрах фізичні годинники серверів ніколи не йдуть абсолютно синхронно. Навіть при активній службі NTP (*Network Time Protocol*) різниця між вузлами в різних стійках може складати від кількох мілісекунд до кількох секунд.

### Обробка годинникового дрейфу (Clock Skew)
Якщо клієнт звернувся за викликом до сервера A з часом `T_A = 12:00:05`, а відповідь надіслав на сервер B, у якого годинник відстає і показує `T_B = 12:00:02`, проста перевірка `now < token->timestamp_sec` розцінить виклик як такий, що прийшов «з майбутнього», і скине з'єднання.

Коректна перевірка часового вікна завжди враховує допустимий дрейф `MAX_CLOCK_SKEW_SEC` (зазвичай 2–5 секунд):

:::tabs
```c
#define MAX_CLOCK_SKEW_SEC 5

int is_timestamp_valid(uint64_t token_time, uint64_t now_time, uint64_t max_age) {
    if (token_time > now_time) {
        if ((token_time - now_time) > MAX_CLOCK_SKEW_SEC) {
            return 0; /* Надто далеко в майбутньому */
        }
        return 1; /* У межах допустимого дрейфу */
    }
    if ((now_time - token_time) > max_age) {
        return 0; /* Виклик протермінований */
    }
    return 1;
}
```
```cpp
constexpr std::chrono::seconds MaxClockSkew{5};

[[nodiscard]] bool is_timestamp_valid(std::chrono::seconds token_time,
                                      std::chrono::seconds now_time,
                                      std::chrono::seconds max_age) noexcept {
    if (token_time > now_time) {
        return (token_time - now_time) <= MaxClockSkew;
    }
    return (now_time - token_time) <= max_age;
}
```
:::

### Масштабування кешу повторів на Redis
У великих горизонтально масштабованих сервісах локального буфера пам'яті процесу недостатньо, оскільки повторний запит може потрапити на інший фізичний сервер. У такому разі локальний масив `replay_cache_t` замінюють атомарною операцією в розподіленому кеші Redis:

```
SET nonce:<hex_nonce> 1 NX EX 30
```

Команда встановлює прапорець `1` для ключа nonce з опцією `NX` (*Not eXists — встановити лише якщо не існує*) та часом життя `EX 30` секунд. Якщо Redis повертає `OK`, виклик є свіжим і позначається як використаний. Якщо Redis повертає `nil`, це свідчить про спробу повторного проходження автентифікації з тим самим викликом, і запит миттєво відхиляється.

## Продуктивність та асиметричне масштабування (Ed25519)

Коли кількість одночасних з'єднань зростає до сотень тисяч, обчислювальна вартість автентифікації стає визначальним фактором для вибору архітектури:

- **Симетричний HMAC-SHA256:** Вимагає близько 1200 тактів CPU на генерацію та перевірку. Один сучасний процесорний потік x86-64 здатен обробляти понад 2 500 000 верифікацій HMAC на секунду. Це ідеальний вибір для високошвидкісних мікросервісів, API-шлюзів та вбудованих контролерів (IoT).
- **Асиметричний Ed25519:** Вимагає близько 65 000 тактів CPU на підпис та близько 180 000 тактів CPU на верифікацію. Продуктивність одного ядра становить близько 15 000 операцій на секунду. Перевага асиметрії — повна відсутність довготривалих секретів на сервері (сервер зберігає лише 32 байти відкритого ключа клієнта), що робить злам серверної бази абсолютно безпечним для користувачів.

## Чекліст аудиту протоколу виклику-відповіді

Перед виведенням протоколу виклику-відповіді у промислову експлуатацію необхідно перевірити дотримання восьми критичних інваріантів:

1. **Непередбачуваність виклику:** Виклики генеруються суто через системний CSPRNG. Використання лінійних конгруентних генераторів (`rand()`, `random()`) повністю заборонено.
2. **Незмінність довжини (Zero-Padding Safe):** Усі структури даних серіалізуються у фіксованому двійковому форматі без використання розділювачів, які можна підробити (наприклад, захист від атак розширення рядка `user=admin` та `user=ad` + `min`).
3. **Повнота контексту:** Хеш-функція відповіді накриває не лише сам виклик, а й ідентифікатор клієнта, ідентифікатор сесії, метод та параметри виконуваної дії.
4. **Сталий час порівняння:** Усі перевірки MAC-підписів, хешів та токенів виконуються за сталий час (`constant_time_memcmp` або `CRYPTO_memcmp`).
5. **Контроль часового вікна:** Термін дії виклику обмежений коротким вікном (не більше 30–60 секунд). Запити з мітками часу з майбутнього за межами дрейфу відхиляються.
6. **Одноразовість перевірки:** Використаний виклик або відразу інвалідується в кеші повторів, або талон прив'язується до унікального інкрементного лічильника сесії.
7. **Розділення ролей (Domain Separation):** Запити клієнта і відповіді сервера мають різні префікси гешування для запобігання атакам віддзеркалення.
8. **Очищення секретів:** Усі проміжні буфери з паролями, спільними секретами та сесійними ключами занулюються функціями `OPENSSL_cleanse` або `explicit_bzero` одразу після обчислення згортки.

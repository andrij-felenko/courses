# ⚙️ Реалізація рушія автентифікації SASL на стороні клієнта та сервера

Цей інженерний проєкт розбирає архітектуру та програмну реалізацію під'єднуваного рушія автентифікації SASL (RFC 4422) мовами C та C++. У ньому показано розділення протокольного транспорту та криптографічної логіки, реалізацію рушія скінченного автомата станів, роботу з механізмом PLAIN (RFC 4616), формування GS2-заголовків для SCRAM-SHA-256, інтеграцію з подієвими неблоківними сокетами, обробку асинхронного введення-виведення, потокове кодування Base64 та безпечне очищення секретних облікових даних у пам'яті.

## Архітектурний шаблон під'єднуваних модулів

Під час розробки високопродуктивних мережевих систем (брокерів повідомлень, шлюзів баз даних, корпоративних поштових серверів) пряме вбудовування логіки автентифікації в мережевий цикл обробки подій створює монолітний спагеті-код. Якщо процедура перевірки пароля або обчислення криптографічних підписів жорстко прив'язана до системних викликів `read()` та `write()`, підтримка нового методу ідентифікації (наприклад, перехід із відкритих паролів на Kerberos або токени OAuth 2.0) вимагає переписування та повторного тестування всього мережевого демона.

Каркас SASL розв'язує цю проблему через архітектурне розділення на три незалежні програмні шари:

1. **Транспортний адаптер (Transport Layer Adapter):** Відповідає за сокетне введення-виведення, взаємодію з подієвим циклом (Reactor / Proactor на базі `epoll`, `kqueue` чи `io_uring`), кадрування протоколу та перекодування блоків Base64. Транспортний шар не знає структури внутрішніх полів механізму і сприймає криптографічні дані як непрозорі масиви байтів.
2. **Диспетчер стану SASL (SASL Core Engine):** Керує життєвим циклом сесії, валідує черговість переходів між станами скінченного автомата, зберігає облікові дані користувача (`authcid`, `authzid`, пароль) та передає виклики віддаленої сторони до відповідного плагіна.
3. **Криптографічний плагін механізму (Mechanism Plugin):** Реалізує чистий математичний алгоритм автентифікації. Він не виконує жодних системних викликів сокетів і не виділяє глобальних ресурсів. На вхід плагін приймає вхідний масив байтів виклику (*Challenge*), а на виході повертає обчислений масив байтів доказу (*Response*).

```
+-------------------------------------------------------------------+
|               Прикладний рівень (IMAP / SMTP / Kafka)             |
+-------------------------------------------------------------------+
                                  │
                                  ▼
+-------------------------------------------------------------------+
|               Універсальний диспетчер стану SASL                  |
|     (Керування життєвим циклом: Init -> Step -> Done / Fail)      |
+-------------------------------------------------------------------+
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
+-----------------+      +-----------------+      +-----------------+
|  Модуль PLAIN   |      |  Модуль SCRAM   |      |  Модуль GSSAPI  |
|   (RFC 4616)    |      |  (RFC 7677)     |      |   (RFC 4752)    |
+-----------------+      +-----------------+      +-----------------+
```

### Скінченний автомат станів автентифікації

Сесія SASL на стороні як клієнта, так і сервера моделюється детермінованим скінченним автоматом (*Finite State Machine*, FSM):

1. `SASL_STATE_INIT`: Початковий стан сесії. Клієнт аналізує список можливостей сервера, вибирає найбільш стійкий механізм та ініціалізує внутрішній контекст плагіна. Якщо механізм підтримує відправку даних без попереднього серверного виклику (як PLAIN або перший крок SCRAM), рушій генерує початкову відповідь клієнта (*Initial Client Response*).
2. `SASL_STATE_STEP`: Проміжний стан циклу «виклик-відповідь». Рушій отримав черговий виклик від віддаленої сторони, передав його до плагіна механізму та згенерував наступний блок відповіді. Сесія може перебувати у цьому стані довільну кількість ітерацій (від 0 для простих схем до 3–4 для складних протоколів на кшталт GSSAPI/SPNEGO).
3. `SASL_STATE_DONE`: Успішне завершення. Сервер перевірив криптографічний доказ, клієнт (у схемах із взаємною автентифікацією) верифікував серверний підпис. Контекст сесії фіксує авторизованого користувача, а сокет переходить у режим передачі прикладних команд або активує рівень захисту Security Layer.
4. `SASL_STATE_FAIL`: Термінальний стан помилки. Виникає у разі невірного пароля, порушення синтаксису повідомлень або невідповідності параметрів прив'язки до каналу. Усі тимчасові криптографічні контексти та ключі у пам'яті негайно знищуються.

## Управління пам'яттю та захист від витоку секретів

Обробка довготривалих паролів, симетричних ключів та сесійних маркерів у пам'яті процесу створює суттєві ризики інформаційної безпеки:

- **Оптимізація компілятора (Dead Store Elimination):** Якщо розробник викликає стандартну функцію `memset(buffer, 0, sizeof(buffer))` безпосередньо перед викликом `free(buffer)` або перед виходом із функції, оптимізувальний компілятор (GCC з прапорцем `-O2` або Clang) розпізнає, що до очищеного буфера більше не буде звернень. Компільований машинний код повністю викидає інструкції запису нулів, залишаючи відкритий пароль у динамічній пам'яті (Heap) або на стеку (Stack).
- **Витік через аварійні дампи:** У разі збою програми операційна система скидає образ пам'яті процесу у файл дампу (*Core Dump*). Якщо буфери не були примусово затерті, конфіденційні дані користувачів стають доступними персоналу, що аналізує журнал збоїв.

Для гарантованого затирання пам'яті застосовуються спеціальні системні бар'єри:
- У стандарті C23 та сучасних POSIX-системах (Linux, FreeBSD) використовується функція `explicit_bzero()`, або функція C11 `memset_s()`.
- В операційній системі Windows використовується виклик `SecureZeroMemory()`.
- У мові C++ створюються спеціалізовані RAII-класи (наприклад, `SecureByteVector`), деструктор яких гарантовано занулює пам'ять за допомогою системного виклику до повернення блоку пам'яті менеджеру виділення.

## Інтерфейс механізму та структури даних

У наведеній нижче реалізації інтерфейс плагіна визначається структурою `sasl_mech_t` у мові C та чистою абстрактною базовою клясою `ISaslMechanism` у мові C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#if defined(_WIN32)
#include <windows.h>
#define SECURE_ZERO(ptr, sz) SecureZeroMemory((ptr), (sz))
#else
#define SECURE_ZERO(ptr, sz) explicit_bzero((ptr), (sz))
#endif

typedef enum {
    SASL_OK = 0,
    SASL_CONTINUE = 1,
    SASL_ERR_AUTH = -1,
    SASL_ERR_SYNTAX = -2,
    SASL_ERR_NOMEM = -3
} sasl_result_t;

typedef enum {
    SASL_STATE_INIT = 0,
    SASL_STATE_STEP,
    SASL_STATE_DONE,
    SASL_STATE_FAIL
} sasl_state_t;

/* Безпечний буфер для передавання бінарних блоків SASL */
typedef struct {
    uint8_t *data;
    size_t len;
} sasl_buffer_t;

/* Структура облікових даних клієнта */
typedef struct {
    const char *authzid;  /* Ідентифікатор авторизації (може бути NULL) */
    const char *authcid;  /* Логін користувача (обов'язковий) */
    const char *password; /* Пароль користувача (обов'язковий) */
} sasl_credentials_t;

/* Інтерфейс під'єднуваного криптографічного механізму */
struct sasl_mech_s;
typedef struct sasl_mech_s sasl_mech_t;

struct sasl_mech_s {
    const char *name;
    sasl_result_t (*client_start)(void **ctx, const sasl_credentials_t *cred, sasl_buffer_t *out);
    sasl_result_t (*client_step)(void *ctx, const sasl_buffer_t *in, sasl_buffer_t *out);
    void (*client_destroy)(void *ctx);

    sasl_result_t (*server_start)(void **ctx, sasl_buffer_t *out);
    sasl_result_t (*server_step)(void *ctx, const sasl_buffer_t *in, sasl_buffer_t *out,
                                char *auth_user, size_t user_max);
    void (*server_destroy)(void *ctx);
};

/* Контекст клієнтської сесії */
typedef struct {
    const sasl_mech_t *mech;
    void *mech_ctx;
    sasl_state_t state;
    sasl_credentials_t cred;
} sasl_client_session_t;

/* Звільнення буфера з обов'язковим зануленням пам'яті */
void sasl_buffer_free(sasl_buffer_t *buf) {
    if (buf && buf->data) {
        SECURE_ZERO(buf->data, buf->len);
        free(buf->data);
        buf->data = NULL;
        buf->len = 0;
    }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <optional>
#include <span>
#include <cstring>

#if defined(_WIN32)
#include <windows.h>
inline void secure_zero(void* ptr, std::size_t sz) noexcept {
    SecureZeroMemory(ptr, sz);
}
#else
inline void secure_zero(void* ptr, std::size_t sz) noexcept {
    explicit_bzero(ptr, sz);
}
#endif

/* Безпечний контейнер пам'яті: автоматичне занулення в деструкторі */
class SecureByteVector {
public:
    SecureByteVector() = default;
    explicit SecureByteVector(std::size_t size) : data_(size) {}
    SecureByteVector(const uint8_t* ptr, std::size_t len) : data_(ptr, ptr + len) {}
    
    ~SecureByteVector() {
        if (!data_.empty()) {
            secure_zero(data_.data(), data_.size());
        }
    }
    
    SecureByteVector(const SecureByteVector& other) = default;
    SecureByteVector& operator=(const SecureByteVector& other) = default;
    SecureByteVector(SecureByteVector&& other) noexcept = default;
    SecureByteVector& operator=(SecureByteVector&& other) noexcept = default;

    [[nodiscard]] std::span<const uint8_t> span() const noexcept { return data_; }
    [[nodiscard]] std::span<uint8_t> span() noexcept { return data_; }
    [[nodiscard]] const uint8_t* data() const noexcept { return data_.data(); }
    [[nodiscard]] uint8_t* data() noexcept { return data_.data(); }
    [[nodiscard]] std::size_t size() const noexcept { return data_.size(); }
    [[nodiscard]] bool empty() const noexcept { return data_.empty(); }

    void resize(std::size_t sz) { data_.resize(sz); }
    void push_back(uint8_t b) { data_.push_back(b); }
    void append(std::span<const uint8_t> s) { data_.insert(data_.end(), s.begin(), s.end()); }

private:
    std::vector<uint8_t> data_;
};

enum class SaslStatus {
    Ok,
    Continue,
    ErrorAuth,
    ErrorSyntax,
    ErrorMemory
};

enum class SaslState {
    Init,
    Step,
    Done,
    Fail
};

struct SaslCredentials {
    std::optional<std::string> authzid;
    std::string authcid;
    std::string password;
};

/* Поліморфний інтерфейс під'єднуваного механізму SASL */
class ISaslMechanism {
public:
    virtual ~ISaslMechanism() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;

    virtual SaslStatus client_start(const SaslCredentials& cred, SecureByteVector& out) = 0;
    virtual SaslStatus client_step(std::span<const uint8_t> in, SecureByteVector& out) = 0;

    virtual SaslStatus server_start(SecureByteVector& out) = 0;
    virtual SaslStatus server_step(std::span<const uint8_t> in, SecureByteVector& out,
                                  std::string& authenticated_user) = 0;
};
```
:::

## Безпечний синтаксичний аналіз механізму PLAIN (RFC 4616)

Специфікація RFC 4616 вимагає об'єднання трьох рядкових елементів в один двійковий масив: `[authzid] \0 authcid \0 password`. 

Головна небезпека під час розбору цього формату на стороні сервера полягає в тому, що некоректно сформований або навмисно обрізаний клієнтський пакет може не містити одного або обох розділювачів `\0`. Якщо парсер спробує прочитати пароль через стандартний `strcpy()`, відбудеться вихід за межі виділеного буфера (*Buffer Over-read*).

Для усунення цієї вразливості парсер виконує такі кроки:
1. Використовує виклик `memchr()` для пошуку першого символу `\0` виключно в межах фактично прийнятого розміру `in->len`.
2. Виділяє підрядок `authzid` (якщо довжина більша за нуль) або фіксує його відсутність.
3. Шукає другий розділювач `\0` у залишку буфера `rem`.
4. Витягує `authcid` та `password`, перевіряючи, що логін не є порожнім.
5. Порівнює пароль із базою даних за допомогою функції постійного часу або криптографічного верифікатора.

:::tabs
```c
/* Формування корисного навантаження клієнта PLAIN */
static sasl_result_t plain_client_start(void **ctx, const sasl_credentials_t *cred, sasl_buffer_t *out) {
    if (!cred || !cred->authcid || !cred->password) {
        return SASL_ERR_SYNTAX;
    }

    size_t authzid_len = cred->authzid ? strlen(cred->authzid) : 0;
    size_t authcid_len = strlen(cred->authcid);
    size_t pass_len = strlen(cred->password);

    /* Загальний розмір: len(authzid) + 1 + len(authcid) + 1 + len(passwd) */
    size_t total_len = authzid_len + 1 + authcid_len + 1 + pass_len;
    out->data = (uint8_t *)malloc(total_len);
    if (!out->data) return SASL_ERR_NOMEM;
    out->len = total_len;

    uint8_t *p = out->data;
    if (authzid_len > 0) {
        memcpy(p, cred->authzid, authzid_len);
        p += authzid_len;
    }
    *p++ = '\0';

    memcpy(p, cred->authcid, authcid_len);
    p += authcid_len;
    *p++ = '\0';

    memcpy(p, cred->password, pass_len);
    *ctx = NULL;

    return SASL_OK; /* Механізм PLAIN завершується за 1 крок клієнта */
}

/* Безпечний серверний розбір повідомлення PLAIN */
static sasl_result_t plain_server_step(void *ctx, const sasl_buffer_t *in, sasl_buffer_t *out,
                                      char *auth_user, size_t user_max) {
    (void)ctx;
    (void)out;
    if (!in || in->len == 0 || !in->data) return SASL_ERR_SYNTAX;

    const char *payload = (const char *)in->data;
    size_t len = in->len;

    /* Пошук першого розділювача NUL */
    const char *first_nul = (const char *)memchr(payload, '\0', len);
    if (!first_nul) return SASL_ERR_SYNTAX;

    size_t authzid_len = first_nul - payload;
    const char *authcid = first_nul + 1;
    size_t rem = len - (authzid_len + 1);

    /* Пошук другого розділювача NUL */
    const char *second_nul = (const char *)memchr(authcid, '\0', rem);
    if (!second_nul) return SASL_ERR_SYNTAX;

    size_t authcid_len = second_nul - authcid;
    const char *password = second_nul + 1;
    size_t pass_len = rem - (authcid_len + 1);

    if (authcid_len == 0) return SASL_ERR_SYNTAX;

    /* Демонстраційна перевірка (у промисловій системі: виклик PAM / запит до БД) */
    bool valid = false;
    if (authcid_len == 5 && memcmp(authcid, "alice", 5) == 0 &&
        pass_len == 14 && memcmp(password, "SecretPass_42!", 14) == 0) {
        valid = true;
    }

    if (!valid) return SASL_ERR_AUTH;

    /* Визначаємо підсумкового суб'єкта авторизації */
    if (authzid_len > 0) {
        if (authzid_len >= user_max) return SASL_ERR_NOMEM;
        memcpy(auth_user, payload, authzid_len);
        auth_user[authzid_len] = '\0';
    } else {
        if (authcid_len >= user_max) return SASL_ERR_NOMEM;
        memcpy(auth_user, authcid, authcid_len);
        auth_user[authcid_len] = '\0';
    }

    return SASL_OK;
}

const sasl_mech_t sasl_mech_plain = {
    .name = "PLAIN",
    .client_start = plain_client_start,
    .client_step = NULL,
    .client_destroy = NULL,
    .server_start = NULL,
    .server_step = plain_server_step,
    .server_destroy = NULL
};
```
```cpp
class SaslPlainMechanism final : public ISaslMechanism {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "PLAIN";
    }

    SaslStatus client_start(const SaslCredentials& cred, SecureByteVector& out) override {
        if (cred.authcid.empty() || cred.password.empty()) {
            return SaslStatus::ErrorSyntax;
        }

        std::size_t authzid_len = cred.authzid ? cred.authzid->size() : 0;
        std::size_t total = authzid_len + 1 + cred.authcid.size() + 1 + cred.password.size();
        
        out.resize(total);
        uint8_t* ptr = out.data();

        if (cred.authzid && !cred.authzid->empty()) {
            std::memcpy(ptr, cred.authzid->data(), authzid_len);
            ptr += authzid_len;
        }
        *ptr++ = '\0';

        std::memcpy(ptr, cred.authcid.data(), cred.authcid.size());
        ptr += cred.authcid.size();
        *ptr++ = '\0';

        std::memcpy(ptr, cred.password.data(), cred.password.size());

        return SaslStatus::Ok;
    }

    SaslStatus client_step(std::span<const uint8_t>, SecureByteVector&) override {
        return SaslStatus::ErrorSyntax;
    }

    SaslStatus server_start(SecureByteVector&) override {
        return SaslStatus::Ok;
    }

    SaslStatus server_step(std::span<const uint8_t> in, SecureByteVector&,
                          std::string& authenticated_user) override {
        if (in.empty()) return SaslStatus::ErrorSyntax;

        auto span_str = std::string_view(reinterpret_cast<const char*>(in.data()), in.size());
        auto first_nul = span_str.find('\0');
        if (first_nul == std::string_view::npos) return SaslStatus::ErrorSyntax;

        auto authzid = span_str.substr(0, first_nul);
        auto rem = span_str.substr(first_nul + 1);

        auto second_nul = rem.find('\0');
        if (second_nul == std::string_view::npos) return SaslStatus::ErrorSyntax;

        auto authcid = rem.substr(0, second_nul);
        auto password = rem.substr(second_nul + 1);

        if (authcid.empty()) return SaslStatus::ErrorSyntax;

        if (authcid == "alice" && password == "SecretPass_42!") {
            authenticated_user = authzid.empty() ? std::string(authcid) : std::string(authzid);
            return SaslStatus::Ok;
        }

        return SaslStatus::ErrorAuth;
    }
};
```
:::

## Формування кадру GS2 для механізму SCRAM-SHA-256

Механізми сімейства SCRAM формують перше повідомлення клієнта (`client-first-message`) на основі стандартизованого префікса GS2 (RFC 5801). Префікс містить інформацію про режим підтримки прив'язки до каналу TLS:
- `n,,`: Клієнт стверджує, що прив'язка до каналу не використовується (незахищене TCP-з'єднання або звичайний `SCRAM-SHA-256`).
- `p=tls-server-end-point,,`: Клієнт зв'язує доказ із поточним TLS-сеансом через відбиток сертифіката сервера (`SCRAM-SHA-256-PLUS`).

Після префікса записуються ім'я користувача `n=username` та випадковий клієнтський виклик `r=client_nonce`. Для генерації виклику обов'язково використовується системний криптографічний генератор випадкових чисел (CSPRNG, такий як `/dev/urandom` або `getrandom()` у Linux, `BCryptGenRandom()` у Windows).

:::tabs
```c
/* Формування GS2-заголовка та початкового виклику SCRAM */
sasl_result_t scram_client_first(const char *username, const char *client_nonce,
                                bool channel_binding, sasl_buffer_t *out) {
    if (!username || !client_nonce || !out) return SASL_ERR_SYNTAX;

    const char *gs2_hdr = channel_binding ? "p=tls-server-end-point,," : "n,,";
    size_t needed = strlen(gs2_hdr) + strlen("n=") + strlen(username) +
                    strlen(",r=") + strlen(client_nonce) + 1;

    out->data = (uint8_t *)malloc(needed);
    if (!out->data) return SASL_ERR_NOMEM;

    int written = snprintf((char *)out->data, needed, "%sn=%s,r=%s",
                           gs2_hdr, username, client_nonce);
    if (written < 0 || (size_t)written >= needed) {
        free(out->data);
        out->data = NULL;
        return SASL_ERR_SYNTAX;
    }
    out->len = (size_t)written;
    return SASL_CONTINUE;
}
```
```cpp
class ScramClientHelper {
public:
    static SecureByteVector build_client_first(std::string_view username,
                                               std::string_view client_nonce,
                                               bool use_channel_binding) {
        std::string gs2_hdr = use_channel_binding ? "p=tls-server-end-point,," : "n,,";
        std::string payload = gs2_hdr + "n=" + std::string(username) + ",r=" + std::string(client_nonce);

        SecureByteVector out(payload.size());
        std::memcpy(out.data(), payload.data(), payload.size());
        return out;
    }
};
```
:::

## Диспетчер сеансу та протокольний цикл

Диспетчер сеансу забезпечує строгу валідацію переходів між станами. Якщо прикладний протокол передає виклик, коли сесія вже перебуває у термінальному стані `SASL_STATE_DONE` або `SASL_STATE_FAIL`, диспетчер миттєво повертає помилку `SASL_ERR_SYNTAX`, унеможливлюючи атаки підміни пакетів.

Така організація дозволяє легко інтегрувати SASL у подієві неблоківні реактори (*Non-blocking Event Loops*). Коли сокет отримує подію `POLLIN`, прикладний протокол зчитує черговий PDU, передає його у `sasl_client_evaluate()` або `server_step()`, а отриману відповідь буферизує для відправки за подією `POLLOUT`.

:::tabs
```c
/* Диспетчер клієнтської сесії */
sasl_result_t sasl_client_init(sasl_client_session_t *sess, const sasl_mech_t *mech,
                               const sasl_credentials_t *cred) {
    if (!sess || !mech || !cred) return SASL_ERR_SYNTAX;
    sess->mech = mech;
    sess->cred = *cred;
    sess->mech_ctx = NULL;
    sess->state = SASL_STATE_INIT;
    return SASL_OK;
}

sasl_result_t sasl_client_evaluate(sasl_client_session_t *sess, const sasl_buffer_t *server_challenge,
                                   sasl_buffer_t *client_response) {
    if (!sess || !sess->mech) return SASL_ERR_SYNTAX;

    sasl_result_t res;
    switch (sess->state) {
    case SASL_STATE_INIT:
        res = sess->mech->client_start(&sess->mech_ctx, &sess->cred, client_response);
        if (res == SASL_OK) {
            sess->state = SASL_STATE_DONE;
        } else if (res == SASL_CONTINUE) {
            sess->state = SASL_STATE_STEP;
        } else {
            sess->state = SASL_STATE_FAIL;
        }
        return res;

    case SASL_STATE_STEP:
        if (!sess->mech->client_step) {
            sess->state = SASL_STATE_FAIL;
            return SASL_ERR_SYNTAX;
        }
        res = sess->mech->client_step(sess->mech_ctx, server_challenge, client_response);
        if (res == SASL_OK) {
            sess->state = SASL_STATE_DONE;
        } else if (res == SASL_CONTINUE) {
            sess->state = SASL_STATE_STEP;
        } else {
            sess->state = SASL_STATE_FAIL;
        }
        return res;

    default:
        return SASL_ERR_SYNTAX;
    }
}
```
```cpp
class SaslClientSession {
public:
    SaslClientSession(std::shared_ptr<ISaslMechanism> mech, SaslCredentials cred)
        : mech_(std::move(mech)), cred_(std::move(cred)), state_(SaslState::Init) {}

    SaslStatus process(std::span<const uint8_t> challenge, SecureByteVector& response) {
        switch (state_) {
        case SaslState::Init: {
            auto status = mech_->client_start(cred_, response);
            if (status == SaslStatus::Ok) {
                state_ = SaslState::Done;
            } else if (status == SaslStatus::Continue) {
                state_ = SaslState::Step;
            } else {
                state_ = SaslState::Fail;
            }
            return status;
        }
        case SaslState::Step: {
            auto status = mech_->client_step(challenge, response);
            if (status == SaslStatus::Ok) {
                state_ = SaslState::Done;
            } else if (status == SaslStatus::Continue) {
                state_ = SaslState::Step;
            } else {
                state_ = SaslState::Fail;
            }
            return status;
        }
        default:
            return SaslStatus::ErrorSyntax;
        }
    }

    [[nodiscard]] SaslState state() const noexcept { return state_; }

private:
    std::shared_ptr<ISaslMechanism> mech_;
    SaslCredentials cred_;
    SaslState state_;
};
```
:::

## Демонстрація протокольного обміну (симуляція клієнт-сервер)

Нижче наведено повний автономний приклад виконання автентифікації клієнта перед сервером:

:::tabs
```c
int main(void) {
    printf("=== Демонстрація роботи каркаса SASL (C) ===\n");

    /* 1. Ініціалізація облікових даних */
    sasl_credentials_t alice_cred = {
        .authzid = NULL,
        .authcid = "alice",
        .password = "SecretPass_42!"
    };

    /* 2. Створення клієнтської сесії з механізмом PLAIN */
    sasl_client_session_t client_sess;
    sasl_client_init(&client_sess, &sasl_mech_plain, &alice_cred);

    sasl_buffer_t initial_response = {NULL, 0};
    sasl_result_t c_res = sasl_client_evaluate(&client_sess, NULL, &initial_response);

    if (c_res == SASL_OK) {
        printf("[Клієнт] Згенеровано початковий кадр PLAIN, розмір: %zu байтів\n", initial_response.len);
    }

    /* 3. Серверна обробка вхідного кадру */
    char authenticated_user[128] = {0};
    sasl_buffer_t server_out = {NULL, 0};
    sasl_result_t s_res = sasl_mech_plain.server_step(NULL, &initial_response, &server_out,
                                                     authenticated_user, sizeof(authenticated_user));

    if (s_res == SASL_OK) {
        printf("[Сервер] Автентифікацію успішно пройдено! Суб'єкт: %s\n", authenticated_user);
    } else {
        printf("[Сервер] Помилка автентифікації: код %d\n", s_res);
    }

    /* 4. Безпечне очищення виділених буферів */
    sasl_buffer_free(&initial_response);
    sasl_buffer_free(&server_out);

    return 0;
}
```
```cpp
int main() {
    std::cout << "=== Демонстрація роботи каркаса SASL (C++) ===\n";

    // 1. Налаштування облікових даних
    SaslCredentials creds{
        .authzid = std::nullopt,
        .authcid = "alice",
        .password = "SecretPass_42!"
    };

    auto plain_mech = std::make_shared<SaslPlainMechanism>();
    SaslClientSession client(plain_mech, creds);

    // 2. Клієнт генерує початкову відповідь
    SecureByteVector client_output;
    auto status = client.process({}, client_output);

    if (status == SaslStatus::Ok) {
        std::cout << "[Клієнт] Згенеровано Initial Response, розмір: " << client_output.size() << " байтів\n";
    }

    // 3. Сервер обробляє отримані байти
    std::string auth_user;
    SecureByteVector server_output;
    auto s_status = plain_mech->server_step(client_output.span(), server_output, auth_user);

    if (s_status == SaslStatus::Ok) {
        std::cout << "[Сервер] Успіх! Авторизовано користувача: " << auth_user << "\n";
    } else {
        std::cout << "[Сервер] Відмова в автентифікації!\n";
    }

    return 0;
}
```
:::

## Інтеграція в неблоківний сокетний цикл реактора

У реальних серверах (наприклад, поштовому демоні Dovecot або брокері Kafka) операції введення-виведення є строго неблоківними. Коли сокет переводиться в режим `O_NONBLOCK`, виклики `read()` та `write()` можуть повернути помилку `EAGAIN` або `EWOULDBLOCK`, що означає відсутність готових даних у системному буфері сокета.

Транспортний адаптер SASL у подієвому циклі (`epoll` у Linux) організовується за такими правилами:

1. **Буферизація вхідного потоку:** Адаптер накопичує байти з мережі у проміжний буфер до моменту отримання повного PDU (наприклад, рядка, що завершується символами `\r\n` в IMAP, або фрейму із 4-байтовою довжиною в Kafka).
2. **Передача цілісного кадру:** Лише після повного отримання PDU блок декодується з Base64 і передається в `sasl_server_step()`.
3. **Черга вихідних повідомлень:** Згенерована відповідь шифрується (якщо активний Security Layer), кодується в Base64 та поміщається у чергу відправки. Сокет реєструється в `epoll` із прапорцем `EPOLLOUT`. Якщо системний буфер заповнений, адаптер відправляє дані частинами під час наступних спрацьовувань події готовності сокета до запису.
4. **Ізоляція сесій у пулі потоків:** Оскільки структури стану SASL (`sasl_client_session_t`) містять змінювані криптографічні контексти, вони не є потокобезпечними (*Not Thread-Safe*). Один контекст сесії категорично заборонено одночасно обробляти з кількох робочих потоків. У багатопотокових серверах контекст жорстко прив'язується до одного дескриптора сокета або захищається ексклюзивним м'ютексом.
5. **Векторизоване виведення (`writev`):** Під час відправки протокольних відповідей транспортний адаптер компонує символьний тег протоколу, розділювальні пробіли, закодований блок Base64 та термінальні символи `\r\n` у масив структур `struct iovec`. Системний виклик `writev()` відправляє цілісний кадр за одну атомарну операцію ядра, уникаючи створення проміжних буферів та зайвого копіювання пам'яті.

## Аудит безпеки та санітизація журналів подій

У промислових середовищах протоколювання мережевого трафіку є обов'язковою вимогою відповідності стандартам безпеки (PCI DSS, ISO/IEC 27001, GDPR). Однак пряме логування сирих пакетів або відладкових повідомлень SASL несе критичну загрозу:

1. **Небезпека витоку паролів у журналі:** Текстовий рядок кадру `PLAIN` у кодуванні Base64 містить відкритий пароль користувача. Якщо мережевий шлюз записує у лог вхідні команди клієнтів (наприклад, `AUTH PLAIN AGFsaWNl...`), паролі співробітників потрапляють у відкриті файли журналів, централізовані системи збору логів (Elasticsearch, Loki, Splunk) та стають доступними персоналу моніторингу.
2. **Санітизація повідомлень перед логуванням:** Програмний шар протокольного аудиту зобов'язаний здійснювати делікатне очищення (*Log Redaction*). Для команд `AUTH` корисне навантаження замінюється на фіксовану маску: `AUTH PLAIN [REDACTED_CREDENTIALS]`.
3. **Структурований аудит спроб доступу:** Кожна подія автентифікації повинна фіксуватися структурованим записом у системному журналі аудиту без збереження секретів:
   - IP-адреса та порт віддаленого клієнта (`peer_addr`).
   - Назва використаного механізму SASL (`mech = "SCRAM-SHA-256"`).
   - Запитані ідентифікатори `authcid` та `authzid`.
   - Результат операції (`status = "SUCCESS"` або `status = "AUTH_FAILED"`).
   - Час виконання криптографічного діалогу в мікросекундах (`latency_us`).

## Апаратне прискорення та продуктивність обчислень

У навантажених системах (наприклад, кластерах Kafka з десятками тисяч підключень) обчислення геш-функцій у механізмах SCRAM (PBKDF2 з 4096 ітераціями) може створювати суттєве навантаження на процесор:

- **Інструкції SHA Extensions (SHA-NI) та AVX-512:** Сучасні процесори x86-64 та ARM містять апаратні інструкції для паралельного обчислення раундів SHA-256 (`_mm_sha256rnds2_epu32`). Використання оптимізованих бібліотек криптографії (OpenSSL 3.x, BoringSSL) скорочує час виконання PBKDF2 в 4–6 разів порівняно з наївною програмною реалізацією.
- **Вирівнювання пам'яті:** Буфери, що передаються у функції гешування, повинні вирівнюватися за межею 64 байтів (розмір рядка кешу L1), що запобігає перетинанню меж кеш-ліній та знижує затримки звернення до пам'яті.
- **Кешування серверних ключів:** Для запобігання повторному виконанню дорогого алгоритму PBKDF2 для кожного нового TCP-з'єднання сервер повинен один раз обчислити та зберегти в базі даних готові пари `StoredKey` та `ServerKey`. Тоді серверний крок SCRAM вимагає лише двох легковагових операцій `HMAC` замість 4096 ітерацій.

## Інженерні пастки та правила безпечної експлуатації

Під час практичного проєктування бібліотек, проксі-серверів та мережевих шлюзів SASL інженери повинні враховувати такі крайові випадки та правила безпеки:

1. **Небезпека функцій форматування рядків:** Спроба вивести або обробити повідомлення PLAIN через `printf("%s")`, `std::string` чи `strlen()` призводить до читання лише першого поля `authzid`, оскільки перший символ `\0` розпізнається як кінець C-рядка. Увесь код обробки SASL-повідомлень повинен оперувати виключно масивами байтів із явною довжиною (`uint8_t*` + `size_t` або `std::span<const uint8_t>`).
2. **Захист від спуфінгу та десинхронізації станів:** Клієнтська бібліотека не повинна приймати серверний виклик після переходу в стан `SASL_STATE_DONE`. Будь-який пакет, отриманий після фінального підтвердження автентифікації, свідчить про спробу зловмисника десинхронізувати потік TCP або здійснити ін'єкцію фальшивого кадру (*TCP Session Hijacking*).
3. **Лімітування розміру вхідних буферів:** Для запобігання атакам вичерпання оперативної пам'яті (*DoS*) сервер зобов'язаний встановлювати жорсткий ліміт на максимальний розмір вхідного блоку Base64 (зазвичай від 4096 до 8192 байтів). Якщо клієнт надсилає блок, що перевищує цей ліміт, сервер зобов'язаний негайно розірвати з'єднання до виділення пам'яті під криптографічні структури.
4. **Таймаути протокольного діалогу:** Процес автентифікації повинен обмежуватися жорстким таймером очікування (наприклад, 10–15 секунд на весь обмін). Якщо зловмисник відкриває TCP-з'єднання, обирає складний механізм і зависає без відправки відповідей на виклики (*Slowloris SASL attack*), сервер зобов'язаний аварійно закрити сокет та звільнити дескриптор.
5. **Запобігання витоку інформації про помилки:** Під час відхилення автентифікації серверний демон не повинен повідомляти, чи існує даний логін у системі. Відповідь завжди повинна бути узагальненою (`Authentication failed`), щоб унеможливити автоматизоване сканування імен користувачів.
6. **Захист від вичерпання дескрипторів сокетів:** У разі виникнення помилки `SASL_ERR_AUTH` сервер повинен застосовувати прогресивну затримку (*Rate Limiting / Exponential Backoff*), щоб захистити сховище користувачів від атак повного перебору паролів (*Brute-force Attacks*).
7. **Коректне завершення сесії при помилках:** Якщо з'єднання розривається посеред багатоетапного обміну, деструктор `client_destroy()` або `server_destroy()` повинен викликатися безумовно. Невиконання цієї вимоги призводить до витоку контекстів GSS-API та пам'яті пулів OpenSSL.
8. **Обробка неблоківного виводу:** При відправці великих токенів Kerberos або сертифікатів функція запису в сокет може повернути помилку `EAGAIN` або `EWOULDBLOCK`. Транспортний адаптер повинен буферизувати невідправлений залишок блоку SASL і відновлювати запис лише після готовності дескриптора за подією `POLLOUT`.
9. **Запобігання фіксації сесії (Session Fixation):** Після успішного завершення SASL сервер повинен повністю скидати всі попередні неавтентифіковані стани сесії та генерувати новий унікальний сесійний ідентифікатор.
10. **Повна ізоляція пам'яті плагінів:** Плагіни механізмів не повинні зберігати стан між різними підключеннями у статичних або глобальних змінних. Кожен сеанс отримує незалежний контекст `mech_ctx`, виділений у динамічній пам'яті, який знищується відразу після закриття з'єднання.


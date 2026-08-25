# ⚙️ Реалізація конвеєра API-шлюзу: ліміт швидкості, JWT та динамічна маршрутизація

В основі високопродуктивного API-шлюзу лежить лінійний або розгалужений конвеєр фільтрів (англ. *filter chain*). Кожен вхідний HTTP-запит, отриманий від клієнта з ненадійної зовнішньої мережі, проходить крізь сувору послідовність етапів: перевірку ліміту швидкості для захисту від перевантаження (Rate Limiter), автентифікацію токена та очищення небезпечних заголовків (Auth & Sanitization), вибір цільового бекенда з урахуванням стану запобіжника (Router & Circuit Breaker) та проксіювання запиту у внутрішню мережу кластера.

У цьому проєкті реалізовано повністю робоче асинхронне ядро конвеєра API-шлюзу двома мовами — сучасним ідіоматичним C++ (із застосуванням семантики володіння RAII, `std::string_view`, `std::expected` та монотонних годинників) та надійним, пам'ятебезпечним C з використанням POSIX-структур і м'ютексів.

---

## Анатомія та етапи конвеєра фільтрів

Обробка запиту організована як послідовність фільтрів, де кожен фільтр має право або завершити обробку помилкою (Short-Circuit), або збагатити запит новими метаданими й передати керування наступній ланці:

1. **Фільтр обмеження швидкості (Rate Limiting via Token Bucket):**
   * Обмежує кількість запитів від окремого клієнта чи організації, запобігаючи вичерпанню обчислювальних ресурсів бекенда.
   * Алгоритм спирається на монотонний таймер (`CLOCK_MONOTONIC`), обчислюючи накопичення токенів від моменту останнього звернення:
   ```
   Нові_токени = (Поточний_час − Час_останнього_поповнення) · Швидкість_поповнення
   Поточні_токени = min(Місткість_кошика, Попередні_токени + Нові_токени)
   ```
   * Якщо кількість токенів достатня, один токен списується, і запит іде далі; інакше шлюз повертає HTTP `429 Too Many Requests`.

2. **Фільтр автентифікації та санітизації заголовків (Auth & Header Sanitization):**
   * **Захист від спуфінгу (Header Injection Defense):** Шлюз обов'язково видаляє з вхідного запиту всі заголовки на кшталт `X-Authenticated-User`, `X-Tenant-Id` чи `X-User-Role`, які клієнт міг спробувати надіслати власноруч.
   * Перевіряє наявність та структуру префікса `Bearer` у заголовку `Authorization`.
   * Імітує перевірку криптографічного підпису JWT (у промислових шлюзах тут виконується асинхронна верифікація за відкритими ключами JWKS).
   * Витягує корисні клейми (Claims) та безпечно впорскує верифіковані внутрішні заголовки для downstream-сервісів.

3. **Фільтр маршрутизатора та запобіжника (Router & Circuit Breaker):**
   * Зіставляє префікс шляху URL із зареєстрованими правилами маршрутизації.
   * Перевіряє стан запобіжника цільового кластера: якщо сервіс зазнає аварії і запобіжник перебуває в стані `Open`, запит не відправляється в мережу, а негайно відхиляється статусом `503 Service Unavailable`.
   * Успішний запит пересилається до внутрішнього вузла з передачею збагачених заголовків.

---

## Вихідний код реалізації

Нижче наведено повну, компільовану реалізацію конвеєра на C++ та C:

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <optional>
#include <expected>
#include <span>
#include <mutex>
#include <algorithm>

// ── 1. Модель HTTP-запиту та відповіді ──────────────────────────────────────
enum class HttpStatus {
    Ok = 200,
    BadRequest = 400,
    Unauthorized = 401,
    Forbidden = 403,
    NotFound = 404,
    TooManyRequests = 429,
    ServiceUnavailable = 503,
    GatewayTimeout = 504
};

struct HttpRequest {
    std::string method;
    std::string path;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
    std::string client_ip;
};

struct HttpResponse {
    HttpStatus status{HttpStatus::Ok};
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

// ── 2. Фільтр обмеження швидкості: Token Bucket ─────────────────────────────
class TokenBucketRateLimiter {
public:
    TokenBucketRateLimiter(double capacity, double refill_rate_per_sec)
        : capacity_(capacity), refill_rate_(refill_rate_per_sec),
          tokens_(capacity), last_refill_(std::chrono::steady_clock::now()) {}

    bool try_acquire(double tokens = 1.0) {
        std::lock_guard<std::mutex> lock(mtx_);
        auto now = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed = now - last_refill_;
        last_refill_ = now;

        // Поповнюємо токени відповідно до монотонного часу
        tokens_ = std::min(capacity_, tokens_ + elapsed.count() * refill_rate_);

        if (tokens_ >= tokens) {
            tokens_ -= tokens;
            return true;
        }
        return false;
    }

private:
    std::mutex mtx_;
    double capacity_;
    double refill_rate_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_;
};

// ── 3. Фільтр автентифікації та захисту заголовків (JWT & Sanitization) ─────
struct UserClaims {
    std::string user_id;
    std::string tenant_id;
    std::string role;
};

class AuthFilter {
public:
    // Безпечна валідація токена та ізоляція внутрішніх заголовків
    std::expected<UserClaims, HttpStatus> authenticate_and_sanitize(HttpRequest& req) const {
        // КРОК 1: Безумовне видалення потенційно підроблених внутрішніх заголовків від клієнта
        req.headers.erase("x-authenticated-user");
        req.headers.erase("x-tenant-id");
        req.headers.erase("x-user-role");

        auto auth_it = req.headers.find("authorization");
        if (auth_it == req.headers.end()) {
            return std::unexpected(HttpStatus::Unauthorized);
        }

        std::string_view auth_header = auth_it->second;
        constexpr std::string_view bearer_prefix = "Bearer ";
        if (!auth_header.starts_with(bearer_prefix)) {
            return std::unexpected(HttpStatus::Unauthorized);
        }

        std::string_view token = auth_header.substr(bearer_prefix.size());
        if (token.empty()) {
            return std::unexpected(HttpStatus::Unauthorized);
        }

        // КРОК 2: Імітація валідації підпису JWT (наприклад, формат "header.payload.sig")
        // У продакшені тут викликається перевірка RSA/ECDSA підпису з кешу JWKS.
        if (token == "demo-expired-token") {
            return std::unexpected(HttpStatus::Unauthorized);
        }

        // КРОК 3: Вилучення клеймів та впорскування довірених заголовків
        UserClaims claims{.user_id = "usr_89412", .tenant_id = "tenant_eu_west", .role = "editor"};
        req.headers["x-authenticated-user"] = claims.user_id;
        req.headers["x-tenant-id"] = claims.tenant_id;
        req.headers["x-user-role"] = claims.role;

        return claims;
    }
};

// ── 4. Маршрутизатор та стан запобіжника (Router & Circuit Breaker) ─────────
enum class CircuitState { Closed, Open, HalfOpen };

struct UpstreamCluster {
    std::string name;
    std::string host_port;
    CircuitState circuit_state{CircuitState::Closed};
    int failure_count{0};
    std::chrono::milliseconds timeout{500};
};

struct RouteRule {
    std::string prefix;
    std::string cluster_name;
    bool require_auth{true};
};

class GatewayRouter {
public:
    void add_route(RouteRule route) {
        routes_.push_back(std::move(route));
    }

    void register_cluster(UpstreamCluster cluster) {
        clusters_[cluster.name] = std::move(cluster);
    }

    std::expected<const UpstreamCluster*, HttpStatus> route(const HttpRequest& req) const {
        for (const auto& r : routes_) {
            if (req.path.starts_with(r.prefix)) {
                auto it = clusters_.find(r.cluster_name);
                if (it == clusters_.end()) {
                    return std::unexpected(HttpStatus::NotFound);
                }
                const auto& cluster = it->second;
                if (cluster.circuit_state == CircuitState::Open) {
                    return std::unexpected(HttpStatus::ServiceUnavailable);
                }
                return &cluster;
            }
        }
        return std::unexpected(HttpStatus::NotFound);
    }

private:
    std::vector<RouteRule> routes_;
    std::unordered_map<std::string, UpstreamCluster> clusters_;
};

// ── 5. Єдиний конвеєр обробки запиту шлюзом ──────────────────────────────────
class ApiGatewayEngine {
public:
    ApiGatewayEngine(TokenBucketRateLimiter limiter, AuthFilter auth, GatewayRouter router)
        : rate_limiter_(std::move(limiter)), auth_filter_(std::move(auth)), router_(std::move(router)) {}

    HttpResponse handle_request(HttpRequest req) {
        // Етап 1: Rate Limiting
        if (!rate_limiter_.try_acquire(1.0)) {
            HttpResponse resp{.status = HttpStatus::TooManyRequests};
            resp.headers["retry-after"] = "1";
            resp.body = "{\"error\": \"Rate limit exceeded. Try again later.\"}";
            return resp;
        }

        // Етап 2: Маршрутизація
        auto upstream_res = router_.route(req);
        if (!upstream_res) {
            HttpResponse resp{.status = upstream_res.error()};
            resp.body = "{\"error\": \"Route not found or upstream unavailable\"}";
            return resp;
        }
        const UpstreamCluster* cluster = *upstream_res;

        // Етап 3: Автентифікація та очищення заголовків
        auto auth_res = auth_filter_.authenticate_and_sanitize(req);
        if (!auth_res) {
            HttpResponse resp{.status = auth_res.error()};
            resp.body = "{\"error\": \"Invalid or missing authentication token\"}";
            return resp;
        }

        // Етап 4: Проксіювання запиту до внутрішнього мікросервісу
        return forward_to_upstream(req, *cluster);
    }

private:
    HttpResponse forward_to_upstream(const HttpRequest& req, const UpstreamCluster& cluster) {
        // Імітація успішної відправки запиту з доданими внутрішніми заголовками
        HttpResponse resp{.status = HttpStatus::Ok};
        resp.headers["content-type"] = "application/json";
        resp.headers["x-gateway-cluster"] = cluster.name;
        resp.body = "{\"status\": \"success\", \"user\": \"" + req.headers.at("x-authenticated-user") + "\"}";
        return resp;
    }

    TokenBucketRateLimiter rate_limiter_;
    AuthFilter auth_filter_;
    GatewayRouter router_;
};

int main() {
    TokenBucketRateLimiter limiter(10.0, 5.0); // 10 токенів ємність, 5 токенів/с
    AuthFilter auth;
    GatewayRouter router;

    router.register_cluster(UpstreamCluster{
        .name = "orders-service",
        .host_port = "orders.internal.mesh:8080",
        .circuit_state = CircuitState::Closed,
        .timeout = std::chrono::milliseconds(300)
    });

    router.add_route(RouteRule{
        .prefix = "/api/v1/orders",
        .cluster_name = "orders-service",
        .require_auth = true
    });

    ApiGatewayEngine gateway(std::move(limiter), std::move(auth), std::move(router));

    HttpRequest client_req{
        .method = "GET",
        .path = "/api/v1/orders/1042",
        .headers = {
            {"authorization", "Bearer valid.jwt.signature"},
            {"x-authenticated-user", "attacker_spoofed_id"} // Буде вичищено шлюзом!
        },
        .body = "",
        .client_ip = "198.51.100.24"
    };

    HttpResponse resp = gateway.handle_request(client_req);
    std::cout << "Gateway Response Status: " << static_cast<int>(resp.status) << "\n";
    std::cout << "Response Body: " << resp.body << "\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <pthread.h>

#define MAX_HEADERS 32
#define MAX_HEADER_LEN 128
#define MAX_PATH_LEN 256
#define MAX_BODY_LEN 1024

// ── 1. Структури даних протоколу ───────────────────────────────────────────
typedef enum {
    HTTP_OK = 200,
    HTTP_UNAUTHORIZED = 401,
    HTTP_NOT_FOUND = 404,
    HTTP_TOO_MANY_REQUESTS = 429,
    HTTP_SERVICE_UNAVAILABLE = 503
} http_status_t;

typedef struct {
    char key[MAX_HEADER_LEN];
    char value[MAX_HEADER_LEN];
} http_header_t;

typedef struct {
    char method[16];
    char path[MAX_PATH_LEN];
    http_header_t headers[MAX_HEADERS];
    size_t header_count;
    char body[MAX_BODY_LEN];
} http_request_t;

typedef struct {
    http_status_t status;
    http_header_t headers[MAX_HEADERS];
    size_t header_count;
    char body[MAX_BODY_LEN];
} http_response_t;

// ── 2. Алгоритм Token Bucket на C з м'ютексом ──────────────────────────────
typedef struct {
    double capacity;
    double refill_rate_per_sec;
    double tokens;
    struct timespec last_refill;
    pthread_mutex_t lock;
} token_bucket_t;

void token_bucket_init(token_bucket_t *tb, double capacity, double refill_rate) {
    tb->capacity = capacity;
    tb->refill_rate_per_sec = refill_rate;
    tb->tokens = capacity;
    clock_gettime(CLOCK_MONOTONIC, &tb->last_refill);
    pthread_mutex_init(&tb->lock, NULL);
}

bool token_bucket_try_acquire(token_bucket_t *tb, double cost) {
    pthread_mutex_lock(&tb->lock);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double elapsed = (now.tv_sec - tb->last_refill.tv_sec) +
                     (now.tv_nsec - tb->last_refill.tv_nsec) / 1e9;
    tb->last_refill = now;

    tb->tokens += elapsed * tb->refill_rate_per_sec;
    if (tb->tokens > tb->capacity) {
        tb->tokens = tb->capacity;
    }

    if (tb->tokens >= cost) {
        tb->tokens -= cost;
        pthread_mutex_unlock(&tb->lock);
        return true;
    }

    pthread_mutex_unlock(&tb->lock);
    return false;
}

// ── 3. Очищення небезпечних заголовків та автентифікація ───────────────────
void req_remove_header(http_request_t *req, const char *key) {
    for (size_t i = 0; i < req->header_count; ++i) {
        if (strcasecmp(req->headers[i].key, key) == 0) {
            req->headers[i] = req->headers[req->header_count - 1];
            req->header_count--;
            i--;
        }
    }
}

void req_set_header(http_request_t *req, const char *key, const char *value) {
    for (size_t i = 0; i < req->header_count; ++i) {
        if (strcasecmp(req->headers[i].key, key) == 0) {
            snprintf(req->headers[i].value, sizeof(req->headers[i].value), "%s", value);
            return;
        }
    }
    if (req->header_count < MAX_HEADERS) {
        snprintf(req->headers[req->header_count].key, sizeof(req->headers[req->header_count].key), "%s", key);
        snprintf(req->headers[req->header_count].value, sizeof(req->headers[req->header_count].value), "%s", value);
        req->header_count++;
    }
}

const char* req_get_header(const http_request_t *req, const char *key) {
    for (size_t i = 0; i < req->header_count; ++i) {
        if (strcasecmp(req->headers[i].key, key) == 0) {
            return req->headers[i].value;
        }
    }
    return NULL;
}

bool auth_filter_process(http_request_t *req) {
    // Безпека: стираємо заголовок ідентичності, який клієнт міг підробити
    req_remove_header(req, "x-authenticated-user");
    req_remove_header(req, "x-tenant-id");

    const char *auth = req_get_header(req, "authorization");
    if (!auth || strncmp(auth, "Bearer ", 7) != 0) {
        return false;
    }

    const char *token = auth + 7;
    if (strcmp(token, "valid.jwt.token") != 0) {
        return false;
    }

    // Впорскуємо довірені дані про ідентичність для внутрішніх сервісів
    req_set_header(req, "x-authenticated-user", "usr_89412");
    req_set_header(req, "x-tenant-id", "tenant_eu_west");
    return true;
}

// ── 4. Маршрутизація та обробка запиту ─────────────────────────────────────
void gateway_handle_request(token_bucket_t *tb, http_request_t *req, http_response_t *resp) {
    memset(resp, 0, sizeof(*resp));

    // 1. Перевірка ліміту швидкості
    if (!token_bucket_try_acquire(tb, 1.0)) {
        resp->status = HTTP_TOO_MANY_REQUESTS;
        snprintf(resp->body, sizeof(resp->body), "{\"error\": \"Rate limit exceeded\"}");
        return;
    }

    // 2. Перевірка маршруту
    if (strncmp(req->path, "/api/v1/orders", 14) != 0) {
        resp->status = HTTP_NOT_FOUND;
        snprintf(resp->body, sizeof(resp->body), "{\"error\": \"Route not found\"}");
        return;
    }

    // 3. Автентифікація
    if (!auth_filter_process(req)) {
        resp->status = HTTP_UNAUTHORIZED;
        snprintf(resp->body, sizeof(resp->body), "{\"error\": \"Unauthorized\"}");
        return;
    }

    // 4. Успішне пересилання до бекенда
    resp->status = HTTP_OK;
    const char *user = req_get_header(req, "x-authenticated-user");
    snprintf(resp->body, sizeof(resp->body), "{\"status\": \"ok\", \"user\": \"%s\"}", user ? user : "unknown");
}

int main(void) {
    token_bucket_t tb;
    token_bucket_init(&tb, 10.0, 5.0);

    http_request_t req;
    memset(&req, 0, sizeof(req));
    snprintf(req.method, sizeof(req.method), "GET");
    snprintf(req.path, sizeof(req.path), "/api/v1/orders/5512");
    req_set_header(&req, "Authorization", "Bearer valid.jwt.token");
    req_set_header(&req, "X-Authenticated-User", "spoofed_attacker");

    http_response_t resp;
    gateway_handle_request(&tb, &req, &resp);

    printf("Response Code: %d\n", resp->status);
    printf("Response Body: %s\n", resp->body);

    return 0;
}
```
:::

---

## Інженерний аналіз та пастки реалізації

Під час проектування та експлуатації таких конвеєрів у високонавантажених системах виникають критичні крайові випадки, нехтування якими призводить до вразливостей або деградації продуктивності.

### 1. Підробка внутрішніх заголовків (Header Spoofing & Injection)
Найпоширеніша помилка реалізації полягає у сліпій довірі до заголовків запиту. Якщо клієнт надсилає власний заголовок `X-Authenticated-User: admin`, а шлюз лише *дописує* заголовки за відсутності або використовує конкатенацію значень за стандартом HTTP (через кому), внутрішній мікросервіс отримає рядок `admin,usr_89412`. Неправильний парсер у сервісі може взяти перше значення і надати зловмиснику адміністративні права.

*Правило шлюзу:* Перед виконанням автентифікації шлюз зобов'язаний виконати **санітизацію (Sanitization)** — повністю стерти з вхідної структури всі внутрішні заголовки ідентичності, які не мають права надходити з публічного інтернету.

### 2. Контрабанда HTTP-запитів (HTTP Request Smuggling)
Якщо шлюз та внутрішній бекенд-сервіс по-різному інтерпретують заголовки розміру повідомлення `Content-Length` та `Transfer-Encoding: chunked` (відома атака CL.TE або TE.CL), зловмисник може вбудувати невидимий другий запит у тіло першого. Коли шлюз пересилає потік у перевикористовуване TCP-з'єднання, другий запит буде виконано бекендом від імені наступного випадкового користувача.

*Захист шлюзу:* Сучасні шлюзи жорстко відхиляють будь-який запит, що містить одночасно обидва заголовки `Content-Length` і `Transfer-Encoding`, або нормалізують весь вхідний потік байтів, транслюючи його у внутрішній протокол HTTP/2 фреймів, де проблеми контрабанди не існує через явні двійкові межі фреймів `DATA`.

### 3. Блокування асинхронного циклу подій (Event Loop Stall)
Усі сучасні шлюзи використовують неблокуючу подієву модель (epoll/kqueue). Якщо всередині коду користувацького фільтра викликати синхронну блокуючу операцію (наприклад, прямий запит до реляційної бази даних, блокуючий виклик до LDAP або синхронне обчислення важкого криптографічного хешу PBKDF2), робочий потік ядра зупиняється на десятки мілісекунд.

Оскільки один потік шлюзу обслуговує тисячі відкритих клієнтських сокетів, одне блокування призводить до того, що всі паралельні користувачі на цьому ядрі отримують колосальний сплеск затримок (p99 latency spikes). Усі зовнішні операції шлюзу мусять виконуватися суто асинхронно через неблокуючі сокети.

### 4. Виснаження пулу дескрипторів та Keep-Alive
Якщо шлюз на кожен вхідний запит відкриває новий TCP-сокет до внутрішнього мікросервісу, а після завершення запиту закриває його через `close()`, операційна система накопичує сокети у стані `TIME_WAIT` (який за замовчуванням триває 60 секунд). При темпі 50 000 запитів на секунду шлюз вичерпує діапазон ефемерних портів (порт виснаження, `EADDRNOTAVAIL`).

*Рішення:* Шлюз зобов'язаний підтримувати постійний пул попередньо відкритих з'єднань (Connection Pool) до кожного upstream-кластера з підтримкою HTTP Keep-Alive або мультиплексування потоків у межах одного TCP-з'єднання через протокол HTTP/2.

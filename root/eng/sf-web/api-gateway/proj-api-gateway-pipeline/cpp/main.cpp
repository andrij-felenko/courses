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

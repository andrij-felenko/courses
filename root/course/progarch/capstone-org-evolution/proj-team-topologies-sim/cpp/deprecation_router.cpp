// deprecation_router.cpp — HTTP Middleware керування Sunset і Deprecation заголовками у C++20
#include <iostream>
#include <string>
#include <unordered_map>
#include <chrono>
#include <memory>
#include <optional>
#include <iomanip>
#include <sstream>

struct DeprecationPolicy {
    std::string endpoint_path;
    std::chrono::system_clock::time_point deprecation_time;
    std::chrono::system_clock::time_point sunset_time;
    std::string doc_url;
    std::string successor_path;
};

struct HttpRequest {
    std::string path;
    std::string method;
};

struct HttpResponse {
    int status_code;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

class DeprecationMiddleware {
public:
    void register_policy(const DeprecationPolicy& policy) {
        policies_[policy.endpoint_path] = policy;
    }

    HttpResponse handle_request(const HttpRequest& req) const {
        auto it = policies_.find(req.path);
        if (it == policies_.end()) {
            return {200, {}, "{\"status\": \"active_v2_ok\"}"};
        }

        const auto& policy = it->second;
        auto now = std::chrono::system_clock::now();

        // 1. Перевірка настання кінцевої дати (Sunset Period Expired)
        if (now >= policy.sunset_time) {
            return {
                410,
                {{"Content-Type", "application/json"}},
                "{\"error\": \"Gone\", \"message\": \"Цей API ендпоінт остаточно вимкнено згідно з політикою Sunset. Використовуйте " + policy.successor_path + "\"}"
            };
        }

        // 2. Ендпоінт у стані Deprecated — формування заголовків
        HttpResponse resp{200, {}, "{\"status\": \"deprecated_v1_ok\"}"};
        
        auto deprecation_epoch = std::chrono::duration_cast<std::chrono::seconds>(
            policy.deprecation_time.time_since_epoch()).count();
        
        resp.headers["Deprecation"] = "@" + std::to_string(deprecation_epoch);
        resp.headers["Sunset"] = format_http_date(policy.sunset_time);
        resp.headers["Link"] = "<" + policy.doc_url + ">; rel=\"deprecation\"; type=\"text/html\", <" 
                               + policy.successor_path + ">; rel=\"successor-version\"";

        return resp;
    }

private:
    std::unordered_map<std::string, DeprecationPolicy> policies_;

    static std::string format_http_date(std::chrono::system_clock::time_point tp) {
        std::time_t t = std::chrono::system_clock::to_time_t(tp);
        std::stringstream ss;
        ss << std::put_time(std::gmtime(&t), "%a, %d %b %Y %H:%M:%S GMT");
        return ss.str();
    }
};

int main() {
    DeprecationMiddleware router;

    auto now = std::chrono::system_clock::now();
    auto past_dep = now - std::chrono::hours(24 * 30); // 30 днів тому
    auto future_sunset = now + std::chrono::hours(24 * 60); // через 60 днів
    auto expired_sunset = now - std::chrono::hours(24 * 5); // 5 днів тому

    // Активна політика деприкації v1
    router.register_policy({
        "/api/v1/telemetry",
        past_dep,
        future_sunset,
        "https://developer.dh.io/docs/v1-sunset",
        "/api/v2/telemetry"
    });

    // Однозначно вимкнений ендпоінт v0
    router.register_policy({
        "/api/v0/legacy-auth",
        past_dep,
        expired_sunset,
        "https://developer.dh.io/docs/v0-gone",
        "/api/v2/auth"
    });

    // Сценарій 1: Запит до застарілого, але робочого API
    HttpRequest req1{"/api/v1/telemetry", "GET"};
    auto resp1 = router.handle_request(req1);
    std::cout << "=== Сценарій 1: Deprecated API (HTTP " << resp1.status_code << ") ===" << std::endl;
    for (const auto& [k, v] : resp1.headers) {
        std::cout << k << ": " << v << std::endl;
    }
    std::cout << "Body: " << resp1.body << "\n" << std::endl;

    // Сценарій 2: Запит після настання Sunset
    HttpRequest req2{"/api/v0/legacy-auth", "POST"};
    auto resp2 = router.handle_request(req2);
    std::cout << "=== Сценарій 2: Expired Sunset API (HTTP " << resp2.status_code << ") ===" << std::endl;
    std::cout << "Body: " << resp2.body << std::endl;

    return 0;
}

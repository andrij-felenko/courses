#include <string>
#include <string_view>
#include <unordered_set>
#include <vector>
#include <regex>
#include <optional>
#include <memory>
#include <algorithm>
#include <cctype>

struct CorsConfig {
    std::unordered_set<std::string> allowed_origins;
    std::vector<std::regex> origin_patterns;
    std::string allowed_methods = "GET, POST, PUT, PATCH, DELETE, OPTIONS";
    std::string allowed_headers = "Content-Type, Authorization, X-Requested-With, X-Request-Id";
    std::string exposed_headers = "X-Total-Count, X-RateLimit-Remaining";
    bool allow_credentials = true;
    int max_age_seconds = 86400;
};

// Абстракції HTTP-запиту та відповіді для вбудовування в асинхронні веб-сервери
struct HttpRequest {
    std::string_view method;
    std::string_view path;
    std::vector<std::pair<std::string_view, std::string_view>> headers;

    [[nodiscard]] std::optional<std::string_view> get_header(std::string_view key) const {
        for (const auto& [k, v] : headers) {
            if (k.size() == key.size() && 
                std::equal(k.begin(), k.end(), key.begin(), [](char a, char b) {
                    return std::tolower(static_cast<unsigned char>(a)) == 
                           std::tolower(static_cast<unsigned char>(b));
                })) {
                return v;
            }
        }
        return std::nullopt;
    }
};

struct HttpResponse {
    int status_code = 200;
    std::vector<std::pair<std::string, std::string>> headers;
    std::string body;

    void set_header(std::string key, std::string value) {
        headers.emplace_back(std::move(key), std::move(value));
    }
};

class CorsMiddleware {
public:
    explicit CorsMiddleware(CorsConfig config) 
        : config_(std::move(config)), 
          max_age_str_(std::to_string(config_.max_age_seconds)) {}

    template <typename NextHandler>
    HttpResponse handle(const HttpRequest& req, NextHandler&& next) const {
        const auto origin_opt = req.get_header("origin");
        if (!origin_opt.has_value() || origin_opt->empty()) {
            return next(req);
        }

        const std::string_view origin = *origin_opt;
        if (is_origin_allowed(origin)) {
            if (req.method == "OPTIONS") {
                HttpResponse preflight_res;
                preflight_res.status_code = 204;
                preflight_res.set_header("Access-Control-Allow-Origin", std::string(origin));
                preflight_res.set_header("Vary", "Origin");
                preflight_res.set_header("Access-Control-Allow-Methods", config_.allowed_methods);
                preflight_res.set_header("Access-Control-Allow-Headers", config_.allowed_headers);
                preflight_res.set_header("Access-Control-Max-Age", max_age_str_);
                preflight_res.set_header("Content-Length", "0");
                
                if (config_.allow_credentials) {
                    preflight_res.set_header("Access-Control-Allow-Credentials", "true");
                }
                return preflight_res;
            }

            HttpResponse res = next(req);
            res.set_header("Access-Control-Allow-Origin", std::string(origin));
            res.set_header("Vary", "Origin");

            if (config_.allow_credentials) {
                res.set_header("Access-Control-Allow-Credentials", "true");
            }
            if (!config_.exposed_headers.empty()) {
                res.set_header("Access-Control-Expose-Headers", config_.exposed_headers);
            }
            return res;
        }

        if (req.method == "OPTIONS") {
            HttpResponse forbidden_res;
            forbidden_res.status_code = 403;
            return forbidden_res;
        }

        return next(req);
    }

private:
    [[nodiscard]] bool is_origin_allowed(std::string_view origin) const {
        const std::string origin_str(origin);
        if (config_.allowed_origins.contains(origin_str)) {
            return true;
        }
        for (const auto& pattern : config_.origin_patterns) {
            if (std::regex_match(origin_str, pattern)) {
                return true;
            }
        }
        return false;
    }

    CorsConfig config_;
    std::string max_age_str_;
};

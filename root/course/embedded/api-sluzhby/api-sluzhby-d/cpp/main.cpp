#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <format>
#include <optional>

// Метадані депрекації версії API
struct VersionConfig {
    bool deprecated{false};
    std::string sunset_http_date;
    std::string migration_guide_url;
};

// HTTP відповідь
struct HttpResponse {
    int status_code{200};
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

// HTTP запит
struct HttpRequest {
    std::string method;
    std::string path;
    std::unordered_map<std::string, std::string> headers;
    std::string body;
};

// Високопродуктивний маршрутизатор API з підтримкою життєвого циклу версій
class ApiRouter {
public:
    ApiRouter() {
        // Реєстрація політик версіонування
        versions_["v1"] = VersionConfig{
            .deprecated = true,
            .sunset_http_date = "Sun, 15 Nov 2026 00:00:00 GMT",
            .migration_guide_url = "https://api.iot-corp.com/docs/v1-to-v2"
        };
        versions_["v2"] = VersionConfig{
            .deprecated = false,
            .sunset_http_date = "",
            .migration_guide_url = ""
        };
    }

    HttpResponse dispatch(const HttpRequest& req) {
        std::string_view version = extract_version(req);
        HttpResponse resp;

        // Збір аналітики викликів
        record_metric(version, req.method, req.path);

        // Маршрутизація за шляхами
        if (req.path == "/v1/devices/dev-101/telemetry" && req.method == "GET") {
            resp.status_code = 200;
            resp.body = R"({"id":"dev-101","v":230.2,"a":5.1,"ts":1773446400})";
            resp.headers["Content-Type"] = "application/json";
        } else if (req.path == "/v2/devices/dev-101/telemetry" && req.method == "GET") {
            resp.status_code = 200;
            resp.body = R"({"device_id":"dev-101","metrics":{"voltage_mv":230200,"current_ma":5100},"ts_us":1773446400000000})";
            resp.headers["Content-Type"] = "application/json";
        } else if (req.path == "/v2/devices/dev-101/commands" && req.method == "POST") {
            // Асинхронний прийом команди: повертаємо 202 Accepted
            resp.status_code = 202;
            std::string cmd_id = "cmd_98214";
            resp.headers["Location"] = "/v2/devices/dev-101/commands/" + cmd_id;
            resp.headers["Content-Type"] = "application/json";
            resp.body = R"({"id":")" + cmd_id + R"(","status":"PENDING","device_id":"dev-101"})";
        } else {
            resp.status_code = 404;
            resp.body = R"({"error":"Endpoint not found"})";
            resp.headers["Content-Type"] = "application/json";
        }

        // Інжекція заголовків депрекації за стандартом RFC 8594
        auto it = versions_.find(std::string(version));
        if (it != versions_.end() && it->second.deprecated) {
            resp.headers["Deprecation"] = "true";
            if (!it->second.sunset_http_date.empty()) {
                resp.headers["Sunset"] = it->second.sunset_http_date;
            }
            if (!it->second.migration_guide_url.empty()) {
                resp.headers["Link"] = "<" + it->second.migration_guide_url + ">; rel=\"deprecation\"; type=\"text/html\"";
            }
        }

        return resp;
    }

private:
    std::unordered_map<std::string, VersionConfig> versions_;
    std::unordered_map<std::string, uint64_t> metrics_counter_;

    std::string_view extract_version(const HttpRequest& req) const {
        if (req.path.starts_with("/v1/")) return "v1";
        if (req.path.starts_with("/v2/")) return "v2";
        auto it = req.headers.find("X-API-Version");
        if (it != req.headers.end()) return it->second;
        return "v2"; // Версія за замовчуванням
    }

    void record_metric(std::string_view version, std::string_view method, std::string_view path) {
        std::string key = std::string(version) + ":" + std::string(method) + ":" + std::string(path);
        metrics_counter_[key]++;
    }
};

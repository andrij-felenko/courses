#pragma once

#include "temperature_core.hpp"

#include <algorithm>
#include <cctype>
#include <chrono>
#include <iomanip>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <string_view>

// ============================================================================
// СТРУКТУРИ HTTP-ПРОТОКОЛУ (ТРАНСПОРТНИЙ РІВЕНЬ)
// ============================================================================

/// @brief Модель вхідного HTTP-запиту до REST-контролера.
struct HttpRequest {
    std::string method;  ///< "POST", "PUT" тощо
    std::string path;    ///< Шлях URL, наприклад "/api/v1/temperature"
    std::string body;    ///< Тіло запиту у форматі JSON
};

/// @brief Модель вихідної HTTP-відповіді.
struct HttpResponse {
    int status_code{200};
    std::string content_type{"application/json"};
    std::string body;
};

// ============================================================================
// ТОНКИЙ REST-КОНТРОЛЕР (DRIVING ADAPTER)
// ============================================================================

/// @brief Драйвуючий адаптер HTTP REST API: ізолює ядро від деталей HTTP.
/// Відповідає виключно за десеріалізацію JSON, виклик вхідного порту ISetTemperatureUseCase
/// та двосторонню трансляцію результатів і доменних помилок у відповідні HTTP-статуси.
class HttpTemperatureController {
public:
    explicit HttpTemperatureController(std::shared_ptr<ISetTemperatureUseCase> use_case)
        : use_case_(std::move(use_case)) {}

    /// @brief Обробка HTTP-запиту з трансляцією результату в HTTP-статуси (200, 400, 403, 404, 422, 503).
    [[nodiscard]] HttpResponse handle_request(const HttpRequest& request) const {
        // Перевірка допустимого методу
        if (request.method != "POST" && request.method != "PUT") {
            return HttpResponse{
                .status_code = 405,
                .body = R"({"error":"MethodNotAllowed","message":"Очікується метод POST або PUT"})"
            };
        }

        // 1. Десеріалізація та первинна перевірка формату JSON-корисного навантаження
        auto payload = parse_json_payload(request.body);
        if (!payload.has_value()) {
            return HttpResponse{
                .status_code = 400,
                .body = R"({"error":"BadRequest","message":"Некоректний формат JSON або відсутні обов'язкові поля ('zone_id', 'temperature', 'user_id')"})"
            };
        }

        // 2. Трансляція HTTP-структури в незмінний Command DTO ядра
        SetTemperatureCommand command(payload->zone_id, payload->temperature, payload->user_id);

        // 3. Виклик вхідного порту прикладного ядра
        auto result = use_case_->execute(command);

        // 4. Двостороння трансляція результату виконання або доменної помилки в HTTP-відповідь
        if (result) {
            return map_success_to_http(result.value());
        }

        return map_domain_error_to_http(result.error());
    }

private:
    struct ParsedPayload {
        std::string zone_id;
        double temperature{0.0};
        std::string user_id;
    };

    /// @brief Легковажний розбір JSON для вилучення полів zone_id, temperature, user_id.
    [[nodiscard]] static std::optional<ParsedPayload> parse_json_payload(std::string_view json) {
        auto trim = [](std::string_view s) {
            while (!s.empty() && std::isspace(static_cast<unsigned char>(s.front()))) s.remove_prefix(1);
            while (!s.empty() && std::isspace(static_cast<unsigned char>(s.back()))) s.remove_suffix(1);
            return s;
        };

        json = trim(json);
        if (json.empty() || json.front() != '{' || json.back() != '}') {
            return std::nullopt;
        }

        auto extract_string_field = [&](std::string_view key) -> std::optional<std::string> {
            std::string needle = "\"" + std::string(key) + "\"";
            auto pos = json.find(needle);
            if (pos == std::string_view::npos) return std::nullopt;
            auto colon = json.find(':', pos + needle.size());
            if (colon == std::string_view::npos) return std::nullopt;
            auto first_quote = json.find('"', colon + 1);
            if (first_quote == std::string_view::npos) return std::nullopt;
            auto second_quote = json.find('"', first_quote + 1);
            if (second_quote == std::string_view::npos) return std::nullopt;
            return std::string(json.substr(first_quote + 1, second_quote - first_quote - 1));
        };

        auto extract_number_field = [&](std::string_view key) -> std::optional<double> {
            std::string needle = "\"" + std::string(key) + "\"";
            auto pos = json.find(needle);
            if (pos == std::string_view::npos) return std::nullopt;
            auto colon = json.find(':', pos + needle.size());
            if (colon == std::string_view::npos) return std::nullopt;
            auto val_start = colon + 1;
            while (val_start < json.size() && std::isspace(static_cast<unsigned char>(json[val_start]))) {
                val_start++;
            }
            if (val_start >= json.size()) return std::nullopt;
            auto val_end = val_start;
            while (val_end < json.size() && 
                   (std::isdigit(static_cast<unsigned char>(json[val_end])) || 
                    json[val_end] == '.' || json[val_end] == '-')) {
                val_end++;
            }
            if (val_end == val_start) return std::nullopt;
            try {
                return std::stod(std::string(json.substr(val_start, val_end - val_start)));
            } catch (...) {
                return std::nullopt;
            }
        };

        auto zone_id = extract_string_field("zone_id");
        auto user_id = extract_string_field("user_id");
        auto temp = extract_number_field("temperature");

        if (!zone_id || !user_id || !temp || zone_id->empty() || user_id->empty()) {
            return std::nullopt;
        }

        return ParsedPayload{
            .zone_id = std::move(*zone_id),
            .temperature = *temp,
            .user_id = std::move(*user_id)
        };
    }

    /// @brief Форматування ISO 8601 мітки часу для вихідного JSON.
    [[nodiscard]] static std::string format_iso_time(std::chrono::system_clock::time_point tp) {
        auto time_t_val = std::chrono::system_clock::to_time_t(tp);
        std::tm tm_buf{};
#if defined(_WIN32)
        gmtime_s(&tm_buf, &time_t_val);
#else
        gmtime_r(&time_t_val, &tm_buf);
#endif
        std::ostringstream oss;
        oss << std::put_time(&tm_buf, "%Y-%m-%dT%H:%M:%SZ");
        return oss.str();
    }

    /// @brief Трансляція успішного доменного результату в HTTP 200 OK.
    [[nodiscard]] static HttpResponse map_success_to_http(const TemperatureResult& res) {
        std::ostringstream oss;
        oss << std::fixed << std::setprecision(1);
        oss << "{"
            << "\"status\":\"success\","
            << "\"zone_id\":\"" << res.zone_id << "\","
            << "\"new_temperature\":" << res.new_temperature << ","
            << "\"previous_temperature\":" << res.previous_temperature << ","
            << "\"updated_at\":\"" << format_iso_time(res.timestamp) << "\""
            << "}";

        return HttpResponse{
            .status_code = 200,
            .body = oss.str()
        };
    }

    /// @brief Двостороння трансляція доменних помилок у специфічні HTTP-статуси.
    [[nodiscard]] static HttpResponse map_domain_error_to_http(DomainError err) {
        switch (err) {
            case DomainError::InvalidCommand:
                return HttpResponse{
                    .status_code = 400,
                    .body = R"({"error":"InvalidCommand","message":"Параметри команди порушують базові інваріанти"})"
                };
            case DomainError::AccessDenied:
                return HttpResponse{
                    .status_code = 403,
                    .body = R"({"error":"Forbidden","message":"Користувач не має дозволу на керування цією зоною"})"
                };
            case DomainError::ZoneNotFound:
                return HttpResponse{
                    .status_code = 404,
                    .body = R"({"error":"NotFound","message":"Запитану кліматичну зону не знайдено в системі"})"
                };
            case DomainError::TemperatureOutOfRange:
                return HttpResponse{
                    .status_code = 422,
                    .body = R"({"error":"UnprocessableEntity","message":"Цільова температура виходить за допустимі межі безпеки зони"})"
                };
            case DomainError::DeviceBusy:
                return HttpResponse{
                    .status_code = 503,
                    .body = R"({"error":"ServiceUnavailable","message":"Апаратний регулятор тимчасово зайнятий"})"
                };
        }
        return HttpResponse{
            .status_code = 500,
            .body = R"({"error":"InternalServerError","message":"Невідома помилка ядра"})"
        };
    }

    std::shared_ptr<ISetTemperatureUseCase> use_case_;
};

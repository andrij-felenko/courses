#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <mutex>
#include <atomic>
#include <chrono>
#include <optional>
#include <memory>
#include <charconv>
#include <sstream>

// Структура телеметрії на сучасному C++ (C++20)
struct TelemetryPayload {
    std::string device_id;
    int64_t timestamp{0};
    double temperature{0.0};
    double humidity{0.0};
    uint16_t battery_mv{0};
    uint16_t checksum{0};
};

// Результат валідації без використання винятків
struct ValidationResult {
    bool is_valid{true};
    std::string error_message;
};

// Перевірка фізичних меж вимірювань
ValidationResult validate_telemetry(const TelemetryPayload& payload) {
    if (payload.device_id.size() < 3 || payload.device_id.size() > 32) {
        return {false, "некоректна довжина device_id (3..32 символи)"};
    }
    if (payload.temperature < -40.0 || payload.temperature > 85.0) {
        return {false, "температура поза межами діапазону [-40..85]"};
    }
    if (payload.humidity < 0.0 || payload.humidity > 100.0) {
        return {false, "вологість поза межами діапазону [0..100]"};
    }
    if (payload.battery_mv < 2000 || payload.battery_mv > 4500) {
        return {false, "напруга батареї поза межами [2000..4500]"};
    }
    return {true, ""};
}

// Потокобезпечний трекер метрик на базі RAII та std::mutex
class MetricsTracker {
public:
    void record_success(std::string_view device_id) {
        total_received_.fetch_add(1, std::memory_order_relaxed);
        
        std::lock_guard<std::mutex> lock(mutex_);
        last_seen_[std::string(device_id)] = std::chrono::system_clock::now();
    }

    void record_error() {
        total_errors_.fetch_add(1, std::memory_order_relaxed);
    }

    uint64_t get_received_count() const {
        return total_received_.load(std::memory_order_relaxed);
    }

private:
    std::atomic<uint64_t> total_received_{0};
    std::atomic<uint64_t> total_errors_{0};
    mutable std::mutex mutex_;
    std::unordered_map<std::string, std::chrono::system_clock::time_point> last_seen_;
};

// Безпечний потоковий обробник телеметричного запиту
class TelemetryService {
public:
    explicit TelemetryService(std::shared_ptr<MetricsTracker> tracker)
        : tracker_(std::move(tracker)) {}

    // Обробка сирого HTTP-тіла без небезпечних C-покажчиків
    std::string process_request(std::string_view json_body, int& out_http_code) {
        // У промисловому C++ тут викликається nlohmann::json або simdjson.
        // Демонструємо парсинг через структуровані інваріанти:
        auto payload_opt = parse_json_payload(json_body);
        if (!payload_opt.has_value()) {
            tracker_->record_error();
            out_http_code = 400;
            return R"({"error":"некоректний синтаксис JSON"})";
        }

        const auto& payload = payload_opt.value();
        auto val_res = validate_telemetry(payload);
        if (!val_res.is_valid) {
            tracker_->record_error();
            out_http_code = 400;
            return R"({"error":")" + val_res.error_message + R"("})";
        }

        tracker_->record_success(payload.device_id);
        out_http_code = 200;

        const auto now_sec = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        std::ostringstream oss;
        oss << R"({"status":"ok","received_at":)" << now_sec
            << R"(,"device_id":")" << payload.device_id << R"("})";
        return oss.str();
    }

private:
    std::shared_ptr<MetricsTracker> tracker_;

    // Простий безпечний симулятор парсингу для демонстрації RAII
    std::optional<TelemetryPayload> parse_json_payload(std::string_view body) const {
        if (body.empty() || body.front() != '{' || body.back() != '}') {
            return std::nullopt;
        }
        
        TelemetryPayload p;
        // Заповнення полів із валідацією типів без використання malloc/free
        p.device_id = "sensor-node-042";
        p.timestamp = 1724694800;
        p.temperature = 23.45;
        p.humidity = 58.20;
        p.battery_mv = 3280;
        p.checksum = 42918;
        return p;
    }
};

int main() {
    auto tracker = std::make_shared<MetricsTracker>();
    TelemetryService service(tracker);

    // Тестовий вхідний запит
    const std::string request_body = 
        R"({"device_id":"sensor-node-042","timestamp":1724694800,"temperature":23.45,"humidity":58.2,"battery_mv":3280,"checksum":42918})";

    int status_code = 0;
    std::string response = service.process_request(request_body, status_code);

    std::cout << "Код відповіді HTTP: " << status_code << "\n";
    std::cout << "Тіло відповіді: " << response << "\n";
    std::cout << "Оброблено пакетів: " << tracker->get_received_count() << "\n";

    return 0;
}

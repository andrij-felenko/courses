// C++17: Ідіоматична реалізація Branch by Abstraction та Strangler Router (RAII, Polymorphism, std::expected)
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <variant>
#include <system_error>

struct TelemetryPayload {
    long device_id;
    double temperature;
    double humidity;
    long timestamp;
};

struct ProcessError {
    int status_code;
    std::string message;
};

// Простий аналог std::expected для демонстрації обробки помилок без винятків
template <typename T, typename E>
class Expected {
    std::variant<T, E> data_;
public:
    Expected(T val) : data_(std::move(val)) {}
    Expected(E err) : data_(std::move(err)) {}
    
    bool has_value() const { return std::holds_alternative<T>(data_); }
    const T& value() const { return std::get<T>(data_); }
    const E& error() const { return std::get<E>(data_); }
};

// 1. Абстрактний інтерфейс шва (Branch by Abstraction)
class ITelemetryProvider {
public:
    virtual ~ITelemetryProvider() = default;
    virtual Expected<bool, ProcessError> process(const TelemetryPayload& data) = 0;
};

// --- Стара монолітна реалізація ---
class LegacyMonolithProvider final : public ITelemetryProvider {
    std::string db_connection_str_;
public:
    explicit LegacyMonolithProvider(std::string db_conn)
        : db_connection_str_(std::move(db_conn)) {}
        
    Expected<bool, ProcessError> process(const TelemetryPayload& data) override {
        std::cout << "[LEGACY MONOLITH] Direct DB write (" << db_connection_str_ 
                  << "): Device=" << data.device_id << ", Temp=" << data.temperature << " C\n";
        return true;
    }
};

// --- Нова мікросервісна реалізація ---
class RemoteServiceProvider final : public ITelemetryProvider {
    std::string service_endpoint_;
    int timeout_ms_;
public:
    RemoteServiceProvider(std::string endpoint, int timeout_ms)
        : service_endpoint_(std::move(endpoint)), timeout_ms_(timeout_ms) {}
        
    Expected<bool, ProcessError> process(const TelemetryPayload& data) override {
        std::cout << "[NEW MICROSERVICE] RPC POST " << service_endpoint_ 
                  << " (timeout=" << timeout_ms_ << "ms): Device=" << data.device_id 
                  << ", Temp=" << data.temperature << " C\n";
        return true;
    }
};

// --- Strangler Router з підтримкою Canary та Shadow Write ---
class StranglerRouter final : public ITelemetryProvider {
    std::unique_ptr<ITelemetryProvider> legacy_;
    std::unique_ptr<ITelemetryProvider> remote_;
    int canary_percent_;
    bool shadow_read_enabled_;
public:
    StranglerRouter(std::unique_ptr<ITelemetryProvider> legacy,
                    std::unique_ptr<ITelemetryProvider> remote,
                    int canary_percent,
                    bool shadow_read)
        : legacy_(std::move(legacy)),
          remote_(std::move(remote)),
          canary_percent_(canary_percent),
          shadow_read_enabled_(shadow_read) {}

    Expected<bool, ProcessError> process(const TelemetryPayload& data) override {
        int bucket = static_cast<int>(data.device_id % 100);
        bool use_new_service = (bucket < canary_percent_);

        if (use_new_service) {
            std::cout << "[ROUTER] Device " << data.device_id 
                      << " -> NEW SERVICE (Canary bucket " << bucket << " < " << canary_percent_ << "%)\n";
            auto result = remote_->process(data);
            
            if (shadow_read_enabled_ && result.has_value()) {
                std::cout << "[ROUTER] Executing Shadow Write to Legacy for reconciliation verification...\n";
                [[maybe_unused]] auto shadow_res = legacy_->process(data);
            }
            return result;
        } else {
            std::cout << "[ROUTER] Device " << data.device_id 
                      << " -> LEGACY MONOLITH (Canary bucket " << bucket << " >= " << canary_percent_ << "%)\n";
            return legacy_->process(data);
        }
    }
};

int main() {
    std::cout << "=== STRANGLER MIGRATION DEMO (C++17) ===\n";
    
    auto legacy = std::make_unique<LegacyMonolithProvider>("postgres://localhost:5432/monolith");
    auto remote = std::make_unique<RemoteServiceProvider>("http://telemetry-service.internal/api/v1", 200);
    
    // Створюємо роутер: 20% канарейка, увімкнений shadow write
    auto router = std::make_unique<StranglerRouter>(std::move(legacy), std::move(remote), 20, true);
    
    std::vector<TelemetryPayload> batch = {
        {105, 22.4, 45.0, 1700000001}, // 5% -> NEW
        {142, 19.8, 50.1, 1700000002}, // 42% -> LEGACY
        {119, 25.1, 40.2, 1700000003}  // 19% -> NEW
    };
    
    for (const auto& item : batch) {
        auto res = router->process(item);
        if (!res.has_value()) {
            std::cerr << "Processing failed: " << res.error().message << "\n";
        }
    }
    
    return 0; // RAII автоматично звільняє всі ресурси
}

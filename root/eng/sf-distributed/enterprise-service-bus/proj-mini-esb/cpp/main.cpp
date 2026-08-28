#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>
#include <memory>
#include <format>

/* Статуси обробки повідомлення */
enum class StageStatus {
    Continue,
    Filtered,
    Fault
};

/* Нормалізований конверт повідомлення */
struct NormalizedMessage {
    std::string message_id;
    std::string correlation_id;
    std::unordered_map<std::string, std::string> headers;
    std::string payload;

    [[nodiscard]] std::string_view get_header(std::string_view key) const {
        if (auto it = headers.find(std::string(key)); it != headers.end()) {
            return it->second;
        }
        return {};
    }

    void set_header(std::string key, std::string value) {
        headers.insert_or_assign(std::move(key), std::move(value));
    }
};

/* Контекст обміну повідомленнями (Exchange) */
struct Exchange {
    NormalizedMessage request;
    NormalizedMessage response;
    std::string target_endpoint;
    std::string fault_reason;
    bool is_fault{false};
};

/* Інтерфейс стадії конвеєра */
class IPipelineStage {
public:
    virtual ~IPipelineStage() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    virtual StageStatus process(Exchange& exchange) = 0;
};

/* 1. Стадія автентифікації */
class AuthValidatorStage final : public IPipelineStage {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "AuthValidator";
    }

    StageStatus process(Exchange& exchange) override {
        auto token = exchange.request.get_header("X-Auth-Token");
        if (token != "secret-token-123") {
            exchange.fault_reason = "AUTH_REJECTED: Invalid or missing token";
            exchange.is_fault = true;
            return StageStatus::Fault;
        }
        return StageStatus::Continue;
    }
};

/* 2. Стадія маршрутизації за змістом */
class ContentBasedRouterStage final : public IPipelineStage {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "ContentBasedRouter";
    }

    StageStatus process(Exchange& exchange) override {
        auto type = exchange.request.get_header("X-Message-Type");
        if (type == "ORDER_PAYMENT") {
            exchange.target_endpoint = "billing.service.v1";
        } else if (type == "INVENTORY_SYNC") {
            exchange.target_endpoint = "warehouse.service.v2";
        } else {
            exchange.fault_reason = "ROUTING_FAILED: Unknown message type";
            exchange.is_fault = true;
            return StageStatus::Fault;
        }
        return StageStatus::Continue;
    }
};

/* 3. Стадія трансформації канонічної моделі */
class JsonTransformerStage final : public IPipelineStage {
public:
    [[nodiscard]] std::string_view name() const noexcept override {
        return "JsonTransformer";
    }

    StageStatus process(Exchange& exchange) override {
        exchange.response = exchange.request;
        exchange.response.payload = std::format(
            "{{\"target\":\"{}\",\"id\":\"{}\",\"data\":\"{}\"}}",
            exchange.target_endpoint,
            exchange.request.message_id,
            exchange.request.payload
        );
        exchange.response.set_header("Content-Type", "application/json");
        return StageStatus::Continue;
    }
};

/* Ядро інтеграційного конвеєра (ESB Core) */
class MediationPipeline {
public:
    void add_stage(std::unique_ptr<IPipelineStage> stage) {
        stages_.push_back(std::move(stage));
    }

    void dispatch(Exchange& exchange) const {
        std::cout << std::format("[BUS-CPP] Обробка ID={}\n", exchange.request.message_id);
        for (const auto& stage : stages_) {
            StageStatus status = stage->process(exchange);
            if (status == StageStatus::Fault) {
                std::cout << std::format("[BUS-CPP] Збій на '{}': {} -> Направлено в DLQ\n",
                                         stage->name(), exchange.fault_reason);
                return;
            }
            if (status == StageStatus::Filtered) {
                std::cout << std::format("[BUS-CPP] Повідомлення відфільтровано на '{}'\n", stage->name());
                return;
            }
        }
        std::cout << std::format("[BUS-CPP] Успіх -> Ендпоінт '{}': payload={}\n",
                                 exchange.target_endpoint, exchange.response.payload);
    }

private:
    std::vector<std::unique_ptr<IPipelineStage>> stages_;
};

int main() {
    MediationPipeline bus;
    bus.add_stage(std::make_unique<AuthValidatorStage>());
    bus.add_stage(std::make_unique<ContentBasedRouterStage>());
    bus.add_stage(std::make_unique<JsonTransformerStage>());

    /* Тест 1: Успішний платіж */
    Exchange ex1;
    ex1.request.message_id = "CPP-MSG-101";
    ex1.request.set_header("X-Auth-Token", "secret-token-123");
    ex1.request.set_header("X-Message-Type", "ORDER_PAYMENT");
    ex1.request.payload = "order_id=4590;total=89.50";
    bus.dispatch(ex1);

    /* Тест 2: Відмова в автентифікації */
    Exchange ex2;
    ex2.request.message_id = "CPP-MSG-102";
    ex2.request.set_header("X-Auth-Token", "bad-token");
    ex2.request.set_header("X-Message-Type", "ORDER_PAYMENT");
    ex2.request.payload = "order_id=9999";
    bus.dispatch(ex2);

    return 0;
}

#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <functional>
#include <memory>
#include <optional>
#include <span>
#include <chrono>
#include <stdexcept>

// Структура транспортного конверта повідомлення
struct MessageEnvelope {
    std::string id;
    std::string topic;
    std::unordered_map<std::string, std::string> headers;
    std::vector<uint8_t> payload;
    std::vector<std::string> routing_slip; // Послідовність кроків
    std::chrono::system_clock::time_point timestamp;

    [[nodiscard]] std::string_view payload_as_string() const noexcept {
        return {reinterpret_cast<const char*>(payload.data()), payload.size()};
    }

    [[nodiscard]] std::optional<std::string_view> get_header(std::string_view key) const noexcept {
        auto it = headers.find(std::string(key));
        if (it != headers.end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

// Абстракція вихідного каналу призначення
class IMessageSink {
public:
    virtual ~IMessageSink() = default;
    virtual bool deliver(const MessageEnvelope& msg) = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
};

// Конкретна черга для доставки повідомлень
class QueueSink final : public IMessageSink {
public:
    explicit QueueSink(std::string queue_name) : name_(std::move(queue_name)) {}

    bool deliver(const MessageEnvelope& msg) override {
        std::cout << "  [Черга " << name_ << "] Отримано msg_id=" << msg.id 
                  << " payload: " << msg.payload_as_string() << "\n";
        delivered_count_++;
        return true;
    }

    [[nodiscard]] std::string_view name() const noexcept override { return name_; }
    [[nodiscard]] size_t count() const noexcept { return delivered_count_; }

private:
    std::string name_;
    size_t delivered_count_{0};
};

// Мертва черга для немаршрутизованих і битих повідомлень
class DeadLetterSink final : public IMessageSink {
public:
    explicit DeadLetterSink(std::string name = "DLQ.UNROUTED") : name_(std::move(name)) {}

    bool deliver(const MessageEnvelope& msg) override {
        std::cerr << "  ⚠️ [МЕРТВА ЧЕРГА " << name_ << "] Ізольовано непридатне msg_id=" 
                  << msg.id << " (немає маршруту або збій валідації)\n";
        dlq_count_++;
        return true;
    }

    [[nodiscard]] std::string_view name() const noexcept override { return name_; }
    [[nodiscard]] size_t count() const noexcept { return dlq_count_; }

private:
    std::string name_;
    size_t dlq_count_{0};
};

// Правило маршрутизації: предикат перевірки та список цільових каналів
struct RoutingRule {
    std::string rule_name;
    std::function<bool(const MessageEnvelope&)> predicate;
    std::vector<std::shared_ptr<IMessageSink>> destinations;
};

// Ядро маршрутизатора повідомлень
class MessageRouter {
public:
    explicit MessageRouter(std::shared_ptr<DeadLetterSink> dlq_sink)
        : dlq_(std::move(dlq_sink)) {
        if (!dlq_) {
            throw std::invalid_argument("Dead letter sink cannot be null");
        }
    }

    void add_rule(RoutingRule rule) {
        rules_.push_back(std::move(rule));
    }

    void set_wire_tap(std::shared_ptr<IMessageSink> tap_sink) {
        wire_tap_ = std::move(tap_sink);
    }

    void register_named_sink(std::shared_ptr<IMessageSink> sink) {
        named_sinks_[std::string(sink->name())] = sink;
    }

    // Головний конвеєр обробки вхідного повідомлення
    void route(MessageEnvelope msg) {
        // 1. Wire Tap: Неінвазивний відвід копії на аудит
        if (wire_tap_) {
            try {
                wire_tap_->deliver(msg);
            } catch (const std::exception& ex) {
                std::cerr << "Wire tap audit failed: " << ex.what() << "\n";
            }
        }

        // 2. Routing Slip: Якщо є супровідний маршрут — беремо перший крок
        if (!msg.routing_slip.empty()) {
            std::string next_hop = msg.routing_slip.front();
            msg.routing_slip.erase(msg.routing_slip.begin()); // Вилучаємо поточний крок

            auto it = named_sinks_.find(next_hop);
            if (it != named_sinks_.end()) {
                std::cout << "-> [Routing Slip] Передача на вузол '" << next_hop << "'\n";
                it->second->deliver(msg);
                return;
            } else {
                std::cerr << "-> [Routing Slip Помилка] Вузол '" << next_hop << "' недоступний!\n";
                dlq_->deliver(msg);
                return;
            }
        }

        // 3. Content-Based Router & Recipient List: Перевірка предикатів правил
        bool routed = false;
        for (const auto& rule : rules_) {
            bool matches = false;
            try {
                matches = rule.predicate(msg);
            } catch (const std::exception& e) {
                std::cerr << "Predicate error in rule '" << rule.rule_name << "': " << e.what() << "\n";
                matches = false;
            }

            if (matches) {
                for (const auto& dest : rule.destinations) {
                    dest->deliver(msg);
                    routed = true;
                }
            }
        }

        // 4. Якщо жодне правило не спрацювало — скидаємо в DLQ
        if (!routed) {
            dlq_->deliver(msg);
        }
    }

private:
    std::vector<RoutingRule> rules_;
    std::unordered_map<std::string, std::shared_ptr<IMessageSink>> named_sinks_;
    std::shared_ptr<IMessageSink> wire_tap_{nullptr};
    std::shared_ptr<DeadLetterSink> dlq_;
};

int main() {
    auto dlq = std::make_shared<DeadLetterSink>("DLQ.PRIMARY");
    auto audit_tap = std::make_shared<QueueSink>("AUDIT.STREAM");

    auto queue_eu = std::make_shared<QueueSink>("ORDERS.EU");
    auto queue_us = std::make_shared<QueueSink>("ORDERS.US");
    auto queue_fraud = std::make_shared<QueueSink>("FRAUD.EVALUATION");
    auto queue_kyc = std::make_shared<QueueSink>("KYC.VALIDATION");
    auto queue_billing = std::make_shared<QueueSink>("BILLING.SETTLEMENT");

    MessageRouter router(dlq);
    router.set_wire_tap(audit_tap);

    router.register_named_sink(queue_kyc);
    router.register_named_sink(queue_fraud);
    router.register_named_sink(queue_billing);

    // Правило 1: Регіональна маршрутизація (Content-Based)
    router.add_rule({
        "Region_EU_Rule",
        [](const MessageEnvelope& msg) {
            auto reg = msg.get_header("region");
            return reg.has_value() && *reg == "EU";
        },
        {queue_eu}
    });

    // Правило 2: Мультивекторне розсилання для великих сум (Recipient List)
    router.add_rule({
        "High_Value_VIP_Rule",
        [](const MessageEnvelope& msg) {
            auto amount = msg.get_header("amount");
            if (!amount.has_value()) return false;
            try {
                return std::stod(std::string(*amount)) >= 10000.0;
            } catch (...) {
                return false;
            }
        },
        {queue_us, queue_fraud}
    });

    std::cout << "=== 1. Звичайне замовлення з ЄС ===\n";
    MessageEnvelope msg1{
        .id = "msg_001",
        .topic = "orders",
        .headers = {{"region", "EU"}, {"amount", "250.0"}},
        .payload = {'{', '"', 'i', 't', 'e', 'm', '"', ':', '"', 'B', 'o', 'o', 'k', '"', '}'},
        .routing_slip = {},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg1);

    std::cout << "\n=== 2. VIP замовлення великої суми (Мультивектор) ===\n";
    MessageEnvelope msg2{
        .id = "msg_002",
        .topic = "orders",
        .headers = {{"region", "US"}, {"amount", "50000.0"}},
        .payload = {'{', '"', 'i', 't', 'e', 'm', '"', ':', '"', 'S', 'e', 'r', 'v', 'e', 'r', '"', '}'},
        .routing_slip = {},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg2);

    std::cout << "\n=== 3. Повідомлення з Routing Slip ===\n";
    MessageEnvelope msg3{
        .id = "msg_003",
        .topic = "onboarding",
        .headers = {{"user", "usr_99"}},
        .payload = {'{', '"', 'a', 'c', 't', 'i', 'o', 'n', '"', ':', '"', 'v', 'e', 'r', 'i', 'f', 'y', '"', '}'},
        .routing_slip = {"KYC.VALIDATION", "FRAUD.EVALUATION", "BILLING.SETTLEMENT"},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg3);

    std::cout << "\n=== 4. Немаршрутизоване повідомлення (падає в DLQ) ===\n";
    MessageEnvelope msg4{
        .id = "msg_004",
        .topic = "telemetry",
        .headers = {{"sensor", "temp_01"}},
        .payload = {'2', '4', '.', '5'},
        .routing_slip = {},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg4);

    return 0;
}

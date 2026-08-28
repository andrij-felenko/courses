#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <queue>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <chrono>
#include <expected>
#include <format>
#include <cstdint>
#include <atomic>

namespace bridge {

// Константи конфігурації конвеєра мосту
inline constexpr size_t kBufferCapacity = 16;
inline constexpr size_t kHighWatermark  = 12;
inline constexpr size_t kLowWatermark   = 4;
inline constexpr uint32_t kMaxHops      = 3;

// Типізовані коди помилок обробки
enum class BridgeError {
    BufferFull,
    LoopDetected,
    HopLimitExceeded,
    EgressBrokerFailure,
    CorruptedPayload
};

// Незмінна структура повідомлення з метаданими трасування
struct Message {
    uint64_t    id;
    uint32_t    hop_count;
    std::string origin_bus;
    std::string payload;
    uint64_t    delivery_tag;

    [[nodiscard]] bool has_loop(std::string_view current_bus) const noexcept {
        return (hop_count >= kMaxHops) || (origin_bus == current_bus);
    }
};

// Потокобезпечний буфер з керуванням водяними знаками протитиску (RAII)
class ResilientQueue {
public:
    explicit ResilientQueue(size_t capacity = kBufferCapacity)
        : capacity_(capacity), paused_(false), closed_(false) {}

    std::expected<void, BridgeError> push(Message msg) {
        std::unique_lock lock(mutex_);
        not_full_cv_.wait(lock, [this]() {
            return queue_.size() < capacity_ || closed_;
        });

        if (closed_) {
            return std::unexpected(BridgeError::EgressBrokerFailure);
        }

        queue_.push(std::move(msg));

        // Активація протитиску при досягненні високого порогу
        if (queue_.size() >= kHighWatermark && !paused_) {
            paused_ = true;
            std::cout << std::format("[ПРОТИТИСК] Буфер досяг {}/{}. Вхідний потік призупинено.\n",
                                     queue_.size(), capacity_);
        }

        not_empty_cv_.notify_one();
        return {};
    }

    std::expected<Message, BridgeError> pop() {
        std::unique_lock lock(mutex_);
        not_empty_cv_.wait(lock, [this]() {
            return !queue_.empty() || closed_;
        });

        if (queue_.empty() && closed_) {
            return std::unexpected(BridgeError::EgressBrokerFailure);
        }

        Message msg = std::move(queue_.front());
        queue_.pop();

        // Зняття протитиску при досягненні низького порогу
        if (queue_.size() <= kLowWatermark && paused_) {
            paused_ = false;
            std::cout << std::format("[ПРОТИТИСК] Буфер розвантажено до {}/{}. Вхід відновлено.\n",
                                     queue_.size(), capacity_);
        }

        not_full_cv_.notify_one();
        return msg;
    }

    void close() {
        std::lock_guard lock(mutex_);
        closed_ = true;
        not_empty_cv_.notify_all();
        not_full_cv_.notify_all();
    }

    [[nodiscard]] size_t size() const {
        std::lock_guard lock(mutex_);
        return queue_.size();
    }

private:
    const size_t            capacity_;
    std::queue<Message>     queue_;
    bool                    paused_;
    bool                    closed_;
    mutable std::mutex      mutex_;
    std::condition_variable not_empty_cv_;
    std::condition_variable not_full_cv_;
};

// Інтерфейс вихідної шини з підтвердженням доставки
class IEgressPublisher {
public:
    virtual ~IEgressPublisher() = default;
    [[nodiscard]] virtual std::expected<void, BridgeError> publish(const Message& msg) = 0;
};

// Реалізація вихідного адаптера для хмарного Kafka-кластера
class CloudKafkaPublisher : public IEgressPublisher {
public:
    [[nodiscard]] std::expected<void, BridgeError> publish(const Message& msg) override {
        // Імітація мережевого RTT
        std::this_thread::sleep_for(std::chrono::milliseconds(15));

        if (msg.payload.contains("CORRUPT")) {
            return std::unexpected(BridgeError::CorruptedPayload);
        }

        std::cout << std::format("[EGRESS -> Cloud_Kafka] Записано id={} (hops={}, payload=\"{}\")\n",
                                 msg.id, msg.hop_count, msg.payload);
        return {};
    }
};

// Головний рушій мосту повідомлень (Message Bus Bridge Engine)
class MessageBusBridge {
public:
    MessageBusBridge(std::string current_bus, std::shared_ptr<IEgressPublisher> egress)
        : current_bus_(std::move(current_bus)),
          egress_(std::move(egress)),
          forwarded_count_(0),
          quarantine_count_(0),
          running_(true) {
        worker_thread_ = std::jthread([this](std::stop_token st) {
            process_pipeline(st);
        });
    }

    ~MessageBusBridge() {
        stop();
    }

    std::expected<void, BridgeError> ingress_receive(Message msg) {
        if (msg.has_loop(current_bus_)) {
            return std::unexpected(BridgeError::LoopDetected);
        }
        return buffer_.push(std::move(msg));
    }

    void stop() {
        if (running_.exchange(false)) {
            buffer_.close();
            if (worker_thread_.joinable()) {
                worker_thread_.request_stop();
            }
        }
    }

    [[nodiscard]] uint64_t forwarded_count() const noexcept { return forwarded_count_.load(); }
    [[nodiscard]] uint64_t quarantine_count() const noexcept { return quarantine_count_.load(); }

private:
    void process_pipeline(std::stop_token st) {
        while (!st.stop_requested() && running_) {
            auto msg_opt = buffer_.pop();
            if (!msg_opt) {
                break; // Буфер закрито і спустошено
            }

            Message msg = std::move(*msg_opt);
            msg.hop_count++;

            // Спроба публікації з координацією Dual-Ack
            auto result = egress_->publish(msg);
            if (result.has_value()) {
                // Коміт у джерело здійснюється ЛИШЕ після підтвердження Egress
                commit_ingress_ack(msg.delivery_tag);
                forwarded_count_++;
            } else {
                // Ізоляція в мертву чергу (DLQ)
                quarantine_dlq(msg, "Egress ACK timeout or schema validation error");
                commit_ingress_ack(msg.delivery_tag);
                quarantine_count_++;
            }
        }
    }

    static void commit_ingress_ack(uint64_t delivery_tag) {
        std::cout << std::format("[INGRESS-ACK] Квитанцію delivery_tag={} підтверджено у вхідній шині.\n",
                                 delivery_tag);
    }

    static void quarantine_dlq(const Message& msg, std::string_view reason) {
        std::cout << std::format("[МЕРТВА ЧЕРГА / DLQ] Ізольовано id={}, причина: {}\n",
                                 msg.id, reason);
    }

    std::string                       current_bus_;
    std::shared_ptr<IEgressPublisher> egress_;
    ResilientQueue                    buffer_;
    std::atomic<uint64_t>             forwarded_count_;
    std::atomic<uint64_t>             quarantine_count_;
    std::atomic<bool>                 running_;
    std::jthread                      worker_thread_;
};

} // namespace bridge

int main() {
    std::cout << "=== Запуск тесту відмовостійкого мосту шин (C++23) ===\n\n";

    auto publisher = std::make_shared<bridge::CloudKafkaPublisher>();
    bridge::MessageBusBridge bridge("Factory_Floor_Edge_MQTT", publisher);

    // Тест 1: Успішна реплікація
    auto res1 = bridge.ingress_receive({
        .id = 101, .hop_count = 0, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "SensorData{temp: 24.5C, humidity: 45%}", .delivery_tag = 1
    });

    // Тест 2: Виявлення петлі маршрутизації
    auto res2 = bridge.ingress_receive({
        .id = 102, .hop_count = 1, .origin_bus = "Factory_Floor_Edge_MQTT",
        .payload = "BillingEvent{tx_id: 9942}", .delivery_tag = 2
    });
    if (!res2) {
        std::cout << "[ЗАХИСТ ВІД ЗАЦИКЛЕННЯ] Повідомлення id=102 відхилено (петля маршрутизації)!\n";
    }

    // Тест 3: Отруйний пакет для DLQ
    auto res3 = bridge.ingress_receive({
        .id = 103, .hop_count = 0, .origin_bus = "Robotics_CAN_Bus",
        .payload = "Telemetry{CORRUPT_CRC32}", .delivery_tag = 3
    });

    // Тест 4: Сплеск трафіку для перевірки протитиску
    for (int i = 0; i < 14; ++i) {
        bridge.ingress_receive({
            .id = static_cast<uint64_t>(200 + i),
            .hop_count = 0,
            .origin_bus = std::format("PLC_Node_{}", i % 3),
            .payload = std::format("Vibration{{rpm: {}, amp: 0.14}}", 1500 + i * 15),
            .delivery_tag = static_cast<uint64_t>(10 + i)
        });
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(450));
    bridge.stop();

    std::cout << "\n=== Результати роботи мосту ===\n";
    std::cout << std::format("Успішно репліковано: {}\n", bridge.forwarded_count());
    std::cout << std::format("Ізольовано в DLQ:    {}\n", bridge.quarantine_count());
    std::cout << "Конвеєр мосту зупинено коректно.\n";

    return 0;
}

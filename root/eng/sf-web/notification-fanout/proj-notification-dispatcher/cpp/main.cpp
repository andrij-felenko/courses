#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <thread>
#include <mutex>
#include <queue>
#include <optional>
#include <span>
#include <algorithm>

// Статус доставки окремого пристрою від зовнішнього шлюзу
enum class DeliveryStatus {
    Success,
    TokenExpired,    // HTTP 410 Gone / NotRegistered -> у Feedback Service
    RateLimited,     // HTTP 429 Too Many Requests -> повторити з backoff
    InvalidPayload,  // HTTP 400 BadPayload -> у Dead Letter Queue
    NetworkError     // Тимчасовий збій з'єднання
};

struct DeviceNotification {
    std::string device_token;
    std::string title;
    std::string body;
    std::string payload_json;
};

struct DeliveryResult {
    std::string device_token;
    DeliveryStatus status;
    std::string error_message;
};

// Потокобезпечний обмежувач темпу (Token Bucket)
class TokenBucketRateLimiter {
public:
    TokenBucketRateLimiter(double rate_per_second, double capacity)
        : rate_(rate_per_second), capacity_(capacity), tokens_(capacity),
          last_refill_(std::chrono::steady_clock::now()) {}

    bool try_acquire(double tokens = 1.0) {
        std::lock_guard<std::mutex> lock(mutex_);
        refill();
        if (tokens_ >= tokens) {
            tokens_ -= tokens;
            return true;
        }
        return false;
    }

    void acquire(double tokens = 1.0) {
        while (!try_acquire(tokens)) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

private:
    void refill() {
        auto now = std::chrono::steady_clock::now();
        double elapsed = std::chrono::duration<double>(now - last_refill_).count();
        tokens_ = std::min(capacity_, tokens_ + elapsed * rate_);
        last_refill_ = now;
    }

    const double rate_;
    const double capacity_;
    double tokens_;
    std::chrono::steady_clock::time_point last_refill_;
    std::mutex mutex_;
};

// Абстрактний транспортний адаптер (APNs HTTP/2 або FCM v1)
class IPushProviderAdapter {
public:
    virtual ~IPushProviderAdapter() = default;
    virtual std::vector<DeliveryResult> send_batch(std::span<const DeviceNotification> batch) = 0;
};

// Симулятор мережевого адаптера APNs / FCM з обробкою статус-кодів
class MockPushProviderAdapter : public IPushProviderAdapter {
public:
    std::vector<DeliveryResult> send_batch(std::span<const DeviceNotification> batch) override {
        std::vector<DeliveryResult> results;
        results.reserve(batch.size());

        for (const auto& item : batch) {
            // Симуляція різних статусів провайдера на основі патерну токена
            if (item.device_token.rfind("invalid_", 0) == 0) {
                results.push_back({item.device_token, DeliveryStatus::TokenExpired, "410 Unregistered token"});
            } else if (item.device_token.rfind("bad_", 0) == 0) {
                results.push_back({item.device_token, DeliveryStatus::InvalidPayload, "400 Malformed JSON"});
            } else {
                results.push_back({item.device_token, DeliveryStatus::Success, ""});
            }
        }
        return results;
    }
};

// Ядро конвеєра диспетчера розсилки
class NotificationDispatcher {
public:
    NotificationDispatcher(std::shared_ptr<IPushProviderAdapter> adapter,
                           double max_rps, size_t batch_size)
        : adapter_(std::move(adapter)),
          rate_limiter_(max_rps, max_rps * 2.0),
          batch_size_(batch_size) {}

    void dispatch_fanout(const std::vector<std::string>& target_tokens,
                         std::string_view title, std::string_view body) {
        if (target_tokens.empty()) return;

        // 1. Формування повного списку нотифікацій
        std::vector<DeviceNotification> notifications;
        notifications.reserve(target_tokens.size());
        for (const auto& token : target_tokens) {
            notifications.push_back({token, std::string(title), std::string(body), "{}"});
        }

        // 2. Розбиття на батчі (Chunking) та відправка через rate limiter
        size_t total = notifications.size();
        for (size_t offset = 0; offset < total; offset += batch_size_) {
            size_t current_chunk = std::min(batch_size_, total - offset);
            std::span<const DeviceNotification> chunk(&notifications[offset], current_chunk);

            // Очікування доступного токена пропускної здатності
            rate_limiter_.acquire(static_cast<double>(current_chunk));

            // Відправка батча в провайдер
            auto results = adapter_->send_batch(chunk);

            // 3. Маршрутизація результатів за категоріями
            process_results(results);
        }
    }

    std::vector<std::string> drain_expired_tokens() {
        std::lock_guard<std::mutex> lock(feedback_mutex_);
        std::vector<std::string> out = std::move(expired_tokens_feedback_);
        expired_tokens_feedback_.clear();
        return out;
    }

    std::vector<DeviceNotification> drain_dead_letter_queue() {
        std::lock_guard<std::mutex> lock(dlq_mutex_);
        std::vector<DeviceNotification> out = std::move(dead_letter_queue_);
        dead_letter_queue_.clear();
        return out;
    }

private:
    void process_results(const std::vector<DeliveryResult>& results) {
        for (const auto& res : results) {
            switch (res.status) {
                case DeliveryStatus::Success:
                    // Успішно доставлено
                    break;
                case DeliveryStatus::TokenExpired: {
                    std::lock_guard<std::mutex> lock(feedback_mutex_);
                    expired_tokens_feedback_.push_back(res.device_token);
                    break;
                }
                case DeliveryStatus::InvalidPayload:
                case DeliveryStatus::RateLimited:
                case DeliveryStatus::NetworkError: {
                    std::lock_guard<std::mutex> lock(dlq_mutex_);
                    dead_letter_queue_.push_back({res.device_token, "Alert", "Error occurred", "{}"});
                    break;
                }
            }
        }
    }

    std::shared_ptr<IPushProviderAdapter> adapter_;
    TokenBucketRateLimiter rate_limiter_;
    const size_t batch_size_;

    std::vector<std::string> expired_tokens_feedback_;
    std::mutex feedback_mutex_;

    std::vector<DeviceNotification> dead_letter_queue_;
    std::mutex dlq_mutex_;
};

int main() {
    auto adapter = std::make_shared<MockPushProviderAdapter>();
    // Ліміт: 1000 повідомлень/с, розмір батча: 500
    NotificationDispatcher dispatcher(adapter, 1000.0, 500);

    std::vector<std::string> tokens = {
        "valid_token_001",
        "invalid_token_002", // Повинен потрапити у Feedback Service
        "valid_token_003",
        "bad_token_004"      // Повинен потрапити у DLQ
    };

    dispatcher.dispatch_fanout(tokens, "Термінова новина", "Сервіс оновлено успішно.");

    auto expired = dispatcher.drain_expired_tokens();
    auto dlq = dispatcher.drain_dead_letter_queue();

    std::cout << "Очищено застарілих токенів: " << expired.size() << "\n";
    std::cout << "Направлено у Dead Letter Queue: " << dlq.size() << "\n";

    return 0;
}

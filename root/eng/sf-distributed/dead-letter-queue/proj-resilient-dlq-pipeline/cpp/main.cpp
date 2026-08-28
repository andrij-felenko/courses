#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <queue>
#include <optional>
#include <expected>
#include <chrono>
#include <thread>
#include <memory>
#include <format>

namespace messaging {

enum class ErrorSeverity {
    Transient,
    PoisonPill
};

struct ProcessingError {
    ErrorSeverity severity;
    std::string exception_class;
    std::string message;
};

struct Message {
    std::string id;
    std::string payload;
    uint32_t attempts{0};
    uint32_t redrive_count{0};
    std::chrono::steady_clock::time_point next_retry_at{};
    std::string trace_id;
};

struct DeadLetterEnvelope {
    Message original_message;
    std::string original_queue;
    ProcessingError error;
    std::chrono::system_clock::time_point dead_lettered_at;
    uint32_t total_attempts{0};
};

class ResilientMessagePipeline {
public:
    static constexpr uint32_t MaxRetries = 3;
    static constexpr uint32_t MaxRedrives = 2;

    void publish_primary(Message msg) {
        primary_queue_.push(std::move(msg));
    }

    void process_cycle() {
        const auto now = std::chrono::steady_clock::now();

        // 1. Обробка черги повторів із затримкою
        if (!retry_queue_.empty()) {
            auto msg = std::move(retry_queue_.front());
            retry_queue_.pop();

            if (msg.next_retry_at <= now) {
                msg.attempts++;
                std::cout << std::format("  [RETRY-EXEC] Retrying message {} (attempt {})...\n",
                                         msg.id, msg.attempts);

                auto result = execute_business_logic(msg);
                if (result.has_value()) {
                    std::cout << std::format("  [SUCCESS] Message {} succeeded on retry!\n", msg.id);
                } else if (result.error().severity == ErrorSeverity::PoisonPill || msg.attempts >= MaxRetries) {
                    route_to_dlq(std::move(msg), result.error());
                } else {
                    msg.next_retry_at = now + std::chrono::milliseconds(msg.attempts * 250);
                    retry_queue_.push(std::move(msg));
                }
                return;
            }
            retry_queue_.push(std::move(msg));
        }

        // 2. Обробка основної черги
        if (!primary_queue_.empty()) {
            auto msg = std::move(primary_queue_.front());
            primary_queue_.pop();

            std::cout << std::format("  [CONSUME] Processing message {}: '{}'\n", msg.id, msg.payload);
            msg.attempts = 1;

            auto result = execute_business_logic(msg);
            if (result.has_value()) {
                std::cout << std::format("  [SUCCESS] Message {} completed successfully.\n", msg.id);
            } else if (result.error().severity == ErrorSeverity::PoisonPill) {
                route_to_dlq(std::move(msg), result.error());
            } else {
                msg.next_retry_at = now + std::chrono::milliseconds(200);
                std::cout << std::format("  [RETRY-SCHEDULE] Transient fail: {}. Delaying 200ms.\n",
                                         result.error().message);
                retry_queue_.push(std::move(msg));
            }
        }
    }

    // Безпечний Redrive з DLQ з бар'єрами
    void redrive_dlq(size_t batch_size) {
        std::cout << "\n=== Запуск Redrive Контролера (C++ Pipeline) ===\n";
        size_t processed = 0;

        while (processed < batch_size && !dlq_.empty()) {
            auto env = std::move(dlq_.front());
            dlq_.pop();

            // Бар'єр 1: Захист від зациклення (Loop Breaker)
            if (env.original_message.redrive_count >= MaxRedrives) {
                std::cout << std::format("  [PARKING-LOT] Message {} exceeded redrive limit. Discarded to archive.\n",
                                         env.original_message.id);
                continue;
            }

            // Бар'єр 2: Патчинг схеми даних
            auto to_reinject = std::move(env.original_message);
            if (to_reinject.payload.contains("POISON")) {
                std::cout << std::format("  [PATCH] Fixing schema bug for message {}\n", to_reinject.id);
                to_reinject.payload = "ORDER_VALID_DATA_AFTER_PATCH";
            }

            to_reinject.attempts = 0;
            to_reinject.redrive_count++;
            to_reinject.next_retry_at = {};

            primary_queue_.push(std::move(to_reinject));
            processed++;
            std::cout << std::format("  [REDRIVE-OK] Re-injected message to primary queue.\n");
        }
        std::cout << std::format("=== Відновлено {} повідомлень ===\n\n", processed);
    }

    [[nodiscard]] size_t primary_count() const noexcept { return primary_queue_.size(); }
    [[nodiscard]] size_t retry_count() const noexcept { return retry_queue_.size(); }
    [[nodiscard]] size_t dlq_count() const noexcept { return dlq_.size(); }

private:
    std::expected<void, ProcessingError> execute_business_logic(const Message& msg) const {
        if (msg.payload.contains("POISON")) {
            return std::unexpected(ProcessingError{
                .severity = ErrorSeverity::PoisonPill,
                .exception_class = "InvalidSchemaFormatException",
                .message = "Binary garbage inside JSON address field"
            });
        }
        if (msg.payload.contains("TIMEOUT") && msg.attempts < 2) {
            return std::unexpected(ProcessingError{
                .severity = ErrorSeverity::Transient,
                .exception_class = "NetworkTimeoutException",
                .message = "Downstream bank service unavailable"
            });
        }
        return {};
    }

    void route_to_dlq(Message msg, ProcessingError err) {
        std::cout << std::format("  [DLQ ALERT] Diverting message {} to DLQ. Error: {}\n",
                                 msg.id, err.message);
        dlq_.push(DeadLetterEnvelope{
            .original_message = std::move(msg),
            .original_queue = "primary-orders",
            .error = std::move(err),
            .dead_lettered_at = std::chrono::system_clock::now(),
            .total_attempts = 1
        });
    }

    std::queue<Message> primary_queue_;
    std::queue<Message> retry_queue_;
    std::queue<DeadLetterEnvelope> dlq_;
};

} // namespace messaging

int main() {
    messaging::ResilientMessagePipeline pipeline;

    pipeline.publish_primary({"msg-01", "ORDER_TIMEOUT_SERVICE", 0, 0, {}, "trace-111"});
    pipeline.publish_primary({"msg-02", "ORDER_POISON_BINARY", 0, 0, {}, "trace-222"});
    pipeline.publish_primary({"msg-03", "ORDER_CLEAN_VALID", 0, 0, {}, "trace-333"});

    std::cout << "=== Обробка асинхронного потоку ===\n";
    for (int i = 0; i < 6; ++i) {
        pipeline.process_cycle();
        std::this_thread::sleep_for(std::chrono::milliseconds(80));
    }

    std::cout << std::format("\nСтан: Primary={}, Retry={}, DLQ={}\n",
                             pipeline.primary_count(), pipeline.retry_count(), pipeline.dlq_count());

    // Відновлення
    pipeline.redrive_dlq(10);

    while (pipeline.primary_count() > 0 || pipeline.retry_count() > 0) {
        pipeline.process_cycle();
    }

    std::cout << std::format("\nУсі повідомлення завершено успішно. DLQ={}\n", pipeline.dlq_count());
    return 0;
}

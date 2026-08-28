#include <iostream>
#include <string>
#include <string_view>
#include <memory>
#include <atomic>
#include <chrono>
#include <expected>
#include <variant>
#include <random>
#include <vector>

// Перелік класів пріоритетів
enum class PriorityClass {
    P0_Critical = 0,
    P1_High = 1,
    P2_Medium = 2,
    P3_Low = 3,
    P4_Background = 4
};

// Рівні деградації Brownout
enum class BrownoutLevel {
    L0_Normal = 0,
    L1_Shed_P4 = 1,
    L2_Shed_P3 = 2,
    L3_Shed_P2 = 3,
    L4_Shed_P1 = 4
};

// Стани Circuit Breaker
enum class CircuitState {
    Closed,
    Open,
    HalfOpen
};

// Конверт помилки відмови
struct ResilienceError {
    int http_status;
    std::string code;
    std::string message;
    uint32_t retry_after_ms;
};

// Структура запиту
struct RequestContext {
    std::string request_id;
    std::string tenant_id;
    PriorityClass priority;
    std::string payload;
};

// Автомат станів Circuit Breaker
class CircuitBreaker {
private:
    std::atomic<CircuitState> state_{CircuitState::Closed};
    std::atomic<size_t> failure_count_{0};
    std::atomic<size_t> success_count_{0};
    const size_t failure_threshold_{5};
    std::chrono::steady_clock::time_point last_state_change_;

public:
    CircuitBreaker() : last_state_change_(std::chrono::steady_clock::now()) {}

    bool allow_execution() {
        auto now = std::chrono::steady_clock::now();
        if (state_ == CircuitState::Open) {
            if (now - last_state_change_ > std::chrono::seconds(10)) {
                state_ = CircuitState::HalfOpen;
                last_state_change_ = now;
                return true; // Пробуємо один тестовий запит
            }
            return false;
        }
        return true;
    }

    void record_result(bool success) {
        if (success) {
            if (state_ == CircuitState::HalfOpen) {
                state_ = CircuitState::Closed;
                failure_count_ = 0;
            }
        } else {
            size_t fails = ++failure_count_;
            if (fails >= failure_threshold_) {
                state_ = CircuitState::Open;
                last_state_change_ = std::chrono::steady_clock::now();
            }
        }
    }

    CircuitState get_state() const { return state_.load(); }
};

// Повний пайплайн стійкості
class ResiliencePipeline {
private:
    std::atomic<BrownoutLevel> current_brownout_{BrownoutLevel::L0_Normal};
    std::atomic<int32_t> in_flight_requests_{0};
    const int32_t max_concurrency_{100};
    CircuitBreaker circuit_breaker_;

public:
    void set_brownout_level(BrownoutLevel level) {
        current_brownout_.store(level);
    }

    // Перевірка пріоритету проти поточного рівня Brownout
    bool should_shed_priority(PriorityClass priority) const {
        auto b = current_brownout_.load();
        switch (b) {
            case BrownoutLevel::L0_Normal:  return false;
            case BrownoutLevel::L1_Shed_P4: return priority >= PriorityClass::P4_Background;
            case BrownoutLevel::L2_Shed_P3: return priority >= PriorityClass::P3_Low;
            case BrownoutLevel::L3_Shed_P2: return priority >= PriorityClass::P2_Medium;
            case BrownoutLevel::L4_Shed_P1: return priority >= PriorityClass::P1_High;
        }
        return false;
    }

    // Головний метод перехоплення та обробки запиту
    std::expected<std::string, ResilienceError> execute(
        const RequestContext& ctx,
        auto primary_handler,
        auto fallback_handler
    ) {
        // Бар'єр 1: Priority Shedding на межі
        if (should_shed_priority(ctx.priority)) {
            return std::unexpected(ResilienceError{
                503,
                "LOAD_SHEDDED",
                "Request shed due to elevated system load (Brownout active)",
                5000
            });
        }

        // Бар'єр 2: Adaptive Concurrency Limiter
        if (in_flight_requests_.load() >= max_concurrency_) {
            return std::unexpected(ResilienceError{
                429,
                "CONCURRENCY_LIMIT_EXCEEDED",
                "Worker concurrency limit reached. Please backoff.",
                2000
            });
        }

        // RAII-обгортка для автоматичного зменшення лічильника активних запитів
        struct ConcurrencyGuard {
            std::atomic<int32_t>& counter;
            ConcurrencyGuard(std::atomic<int32_t>& c) : counter(c) { counter++; }
            ~ConcurrencyGuard() { counter--; }
        } guard(in_flight_requests_);

        // Бар'єр 3: Circuit Breaker
        if (!circuit_breaker_.allow_execution()) {
            // Ланцюг розімкнено -> Швидкий перехід на Fallback
            return fallback_handler(ctx, "Circuit breaker OPEN: dependency down");
        }

        // Бар'єр 4: Виконання первинного обробника
        try {
            auto result = primary_handler(ctx);
            circuit_breaker_.record_result(true);
            return result;
        } catch (const std::exception& ex) {
            circuit_breaker_.record_result(false);
            // При збої первинного обробника пробуємо Fallback
            return fallback_handler(ctx, std::string("Primary execution failed: ") + ex.what());
        }
    }
};

// Демонстрація використання
int main() {
    ResiliencePipeline pipeline;
    pipeline.set_brownout_level(BrownoutLevel::L2_Shed_P3);

    auto primary_fn = [](const RequestContext& ctx) -> std::string {
        if (ctx.payload == "poison") {
            throw std::runtime_error("Poison message encountered!");
        }
        return "SUCCESS: Processed " + ctx.request_id;
    };

    auto fallback_fn = [](const RequestContext& ctx, std::string_view reason) -> std::string {
        return "FALLBACK_OK: Returned safe default for " + ctx.request_id + " (Reason: " + std::string(reason) + ")";
    };

    // Тест 1: P3 запит під Brownout L2 (має бути скинутий на вході)
    RequestContext req_p3{"req-101", "t-1", PriorityClass::P3_Low, "data"};
    auto res1 = pipeline.execute(req_p3, primary_fn, fallback_fn);
    if (!res1) {
        std::cout << "[Test 1] Rejected as expected: " << res1.error().code 
                  << " (Status " << res1.error().http_status << ")\n";
    }

    // Тест 2: P0 критичний запит (має пройти успішно)
    RequestContext req_p0{"req-102", "t-1", PriorityClass::P0_Critical, "unlock_door"};
    auto res2 = pipeline.execute(req_p0, primary_fn, fallback_fn);
    if (res2) {
        std::cout << "[Test 2] Result: " << *res2 << "\n";
    }

    // Тест 3: Отруйне повідомлення (має викликати Fallback)
    RequestContext req_poison{"req-103", "t-1", PriorityClass::P0_Critical, "poison"};
    auto res3 = pipeline.execute(req_poison, primary_fn, fallback_fn);
    if (res3) {
        std::cout << "[Test 3] Result: " << *res3 << "\n";
    }

    return 0;
}

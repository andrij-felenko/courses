#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <thread>
#include <future>
#include <atomic>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <random>

// Атомарний бюджет токенів для захисту від шторму дублюючих запитів
class TokenBucket {
public:
    explicit TokenBucket(double max_tokens, double refill_ratio)
        : max_tokens_(max_tokens),
          tokens_(max_tokens),
          refill_ratio_(refill_ratio) {}

    // Спроба списати 1 токен для запуску гедж-запиту
    bool try_consume() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (tokens_ >= 1.0) {
            tokens_ -= 1.0;
            return true;
        }
        return false;
    }

    // Поповнення бюджету при успішному виконанні основного запиту
    void record_primary_success() {
        std::lock_guard<std::mutex> lock(mutex_);
        tokens_ = std::min(max_tokens_, tokens_ + refill_ratio_);
    }

    double current_tokens() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return tokens_;
    }

private:
    mutable std::mutex mutex_;
    double max_tokens_;
    double tokens_;
    double refill_ratio_; // наприклад, 0.1 (10% квота геджування)
};

// Стан виконання одного геджованого запиту
template <typename T>
class HedgedRequestContext {
public:
    void set_result(T value) {
        std::unique_lock<std::mutex> lock(mutex_);
        if (!has_result_) {
            result_ = std::move(value);
            has_result_ = true;
            cv_.notify_all();
        }
    }

    bool is_completed() const {
        return has_result_.load(std::memory_order_relaxed);
    }

    std::optional<T> wait_result(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait_for(lock, timeout, [this] { return has_result_; });
        return result_;
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    std::atomic<bool> has_result_{false};
    std::optional<T> result_;
};

// Симуляція мережевого запиту до віддаленої репліки
std::string call_replica(const std::string& endpoint,
                         std::stop_token stop_tok,
                         int simulated_delay_ms) {
    auto start = std::chrono::steady_clock::now();
    while (true) {
        if (stop_tok.stop_requested()) {
            return ""; // Операцію скасовано, звільняємо сокет/потік
        }
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count();
        if (elapsed >= simulated_delay_ms) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    return "Response from " + endpoint;
}

// Функція геджованого виклику
std::string execute_hedged_request(
    const std::vector<std::string>& replicas,
    std::chrono::milliseconds hedge_delay,
    std::chrono::milliseconds overall_timeout,
    TokenBucket& budget)
{
    if (replicas.empty()) {
        throw std::invalid_argument("Empty replica list");
    }

    auto ctx = std::make_shared<HedgedRequestContext<std::string>>();
    std::stop_source stop_source;

    // 1. Запуск першого запиту (Репліка 1)
    std::jthread thread_primary([ctx, stop_tok = stop_source.get_token(), endpoint = replicas[0]]() {
        // Умовна затримка: 80 мс (зависла в хвості)
        std::string res = call_replica(endpoint, stop_tok, 80);
        if (!res.empty()) {
            ctx->set_result(res);
        }
    });

    // 2. Очікування на порозі геджування
    auto primary_res = ctx->wait_result(hedge_delay);
    if (primary_res.has_value()) {
        budget.record_primary_success();
        stop_source.request_stop();
        return *primary_res;
    }

    // 3. Відкладений гедж (якщо дозволяє бюджет)
    std::unique_ptr<std::jthread> thread_hedge;
    if (replicas.size() > 1 && budget.try_consume()) {
        thread_hedge = std::make_unique<std::jthread>(
            [ctx, stop_tok = stop_source.get_token(), endpoint = replicas[1]]() {
                // Швидка друга репліка: 10 мс
                std::string res = call_replica(endpoint, stop_tok, 10);
                if (!res.empty()) {
                    ctx->set_result(res);
                }
            });
    }

    // 4. Очікування залишкового дедлайну
    auto final_res = ctx->wait_result(overall_timeout - hedge_delay);
    stop_source.request_stop(); // Скасовуємо того, хто ще виконується

    if (final_res.has_value()) {
        return *final_res;
    }

    throw std::runtime_error("Deadline exceeded for all hedged replicas");
}

int main() {
    TokenBucket budget(10.0, 0.1); // Макс 10 токенів, 10% квота
    std::vector<std::string> replicas = {"replica-1.internal:50051", "replica-2.internal:50051"};

    try {
        std::string result = execute_hedged_request(
            replicas,
            std::chrono::milliseconds(25),  // P95 поріг
            std::chrono::milliseconds(200), // загальний дедлайн
            budget
        );
        std::cout << "Успіх: " << result << std::endl;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
    }
    return 0;
}

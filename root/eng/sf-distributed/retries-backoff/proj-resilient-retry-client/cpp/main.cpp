#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <random>
#include <atomic>
#include <mutex>
#include <optional>
#include <expected>
#include <functional>
#include <format>
#include <cmath>

namespace net {

using namespace std::chrono_literals;

// Структура відповіді транспортного рівня
struct Response {
    int status_code{200};
    std::string body;
    std::chrono::milliseconds latency{0};
};

// Семантична класифікація результату виклику
enum class ErrorKind {
    Transient,  // Тимчасовий збій (503, 429, 504, скидання TCP, timeout сокета)
    Permanent   // Фатальна помилка (400, 401, 403, 404, 422)
};

struct RequestError {
    ErrorKind kind;
    int status_code;
    std::string message;
};

// Повна конфігурація політики стійкості
struct RetryPolicy {
    int max_attempts{4};                         // Максимум 4 спроби (1 первинна + 3 повтори)
    std::chrono::milliseconds base_backoff{100ms}; // Початковий інтервал відступу t0
    std::chrono::milliseconds max_backoff{3000ms}; // Верхня межа зрізання інтервалу t_max
    double backoff_multiplier{2.0};              // Експоненційний множник b
    double budget_deposit_per_success{0.10};     // Поповнення бюджету (+0.1 за успіх -> 10% квота)
    double budget_withdraw_per_retry{1.00};      // Списання за кожну повторну спробу
    double max_budget_tokens{100.0};             // Максимальна ємність токенного кошика
};

// Потокобезпечний токенний кошик бюджету повторних спроб
class TokenBucketRetryBudget {
public:
    explicit TokenBucketRetryBudget(double max_tokens = 100.0, double initial_tokens = 20.0)
        : max_tokens_(max_tokens), tokens_(initial_tokens) {}

    // Поповнення кошика при отриманні успішної відповіді 2xx
    void record_success(double deposit = 0.10) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        tokens_ = std::min(max_tokens_, tokens_ + deposit);
    }

    // Спроба списання токена перед виконанням повтору (Fast-Fail перевірка)
    bool try_withdraw_retry(double cost = 1.00) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        if (tokens_ >= cost) {
            tokens_ -= cost;
            return true;
        }
        return false; // Токени закінчилися: лавинне блокування повторів
    }

    double current_balance() const noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        return tokens_;
    }

private:
    mutable std::mutex mutex_;
    double max_tokens_;
    double tokens_;
};

// Калькулятор затримки за алгоритмом Full Jitter
class BackoffCalculator {
public:
    explicit BackoffCalculator(const RetryPolicy& policy)
        : policy_(policy), rng_(std::random_device{}()) {}

    std::chrono::milliseconds calculate(int retry_index) {
        // Детерміністична експоненційна стеля: v(i) = min(t_max, t0 * b^i)
        double factor = std::pow(policy_.backoff_multiplier, retry_index);
        double max_ms = policy_.base_backoff.count() * factor;
        double ceiling_ms = std::min(static_cast<double>(policy_.max_backoff.count()), max_ms);

        // Full Jitter: рівномірний випадковий вибір на інтервалі [0, ceiling_ms]
        std::uniform_real_distribution<double> dist(0.0, ceiling_ms);
        std::lock_guard<std::mutex> lock(rng_mutex_);
        return std::chrono::milliseconds(static_cast<long long>(dist(rng_)));
    }

private:
    RetryPolicy policy_;
    std::mutex rng_mutex_;
    std::mt19937 rng_;
};

// Класифікатор кодів помилок протоколу HTTP
class HttpErrorClassifier {
public:
    static ErrorKind classify(int status_code) noexcept {
        switch (status_code) {
            case 408: // Request Timeout (клієнтський сокет відвалився)
            case 429: // Too Many Requests (сервер сигналізує про обмеження швидкості)
            case 502: // Bad Gateway (проміжний проксі втратив зв'язок)
            case 503: // Service Unavailable (бекенд перевантажений або перезавантажується)
            case 504: // Gateway Timeout (вихідний шлюз не дочекався бекенда)
                return ErrorKind::Transient;
            default:
                if (status_code >= 400 && status_code < 500) {
                    // Клієнтські помилки (400, 401, 403, 404, 422) ніколи не лікуються повтором
                    return ErrorKind::Permanent;
                }
                if (status_code >= 500) {
                    // Інші серверні помилки (наприклад, 500 Internal Server Error) вважаємо тимчасовими
                    return ErrorKind::Transient;
                }
                return ErrorKind::Permanent;
        }
    }
};

// Контекст запиту з монотонним дедлайном та ключем ідемпотентності
struct RequestContext {
    std::string idempotency_key;
    std::chrono::steady_clock::time_point deadline;

    bool is_expired() const noexcept {
        return std::chrono::steady_clock::now() >= deadline;
    }

    std::chrono::milliseconds time_remaining() const noexcept {
        auto now = std::chrono::steady_clock::now();
        if (now >= deadline) return 0ms;
        return std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now);
    }
};

// Головний стійкий клієнт
class ResilientClient {
public:
    explicit ResilientClient(RetryPolicy policy = RetryPolicy{})
        : policy_(policy),
          budget_(policy.max_budget_tokens, 15.0),
          backoff_(policy) {}

    using TransportFn = std::function<std::expected<Response, int>(const std::string& url, 
                                                                  const std::string& key)>;

    // Виконання стійкого виклику із захистом від штормів
    std::expected<Response, RequestError> execute(const std::string& url,
                                                  RequestContext ctx,
                                                  TransportFn transport) {
        for (int attempt = 0; attempt < policy_.max_attempts; ++attempt) {
            // Крок 1: Перевірка глобального дедлайну транзакції
            if (ctx.is_expired()) {
                return std::unexpected(RequestError{
                    ErrorKind::Permanent,
                    504,
                    "Глобальний дедлайн транзакції вичерпано до відправки запиту"
                });
            }

            // Крок 2: Якщо це повторна спроба (attempt > 0) — перевіряємо бюджет і робимо паузу
            if (attempt > 0) {
                // Перевірка наявності токенів у токенному кошику
                if (!budget_.try_withdraw_retry(policy_.budget_withdraw_per_retry)) {
                    return std::unexpected(RequestError{
                        ErrorKind::Transient,
                        429,
                        "Бюджет повторів вичерпано (Retry Budget Exhausted, Fast-Fail захист)"
                    });
                }

                // Розрахунок паузи за алгоритмом Full Jitter
                auto backoff_duration = backoff_.calculate(attempt - 1);

                // Перевірка: чи не перевищує обчислений відступ залишок дедлайну
                if (backoff_duration >= ctx.time_remaining()) {
                    return std::unexpected(RequestError{
                        ErrorKind::Permanent,
                        504,
                        "Залишок дедлайну менший за розраховану тривалість відступу"
                    });
                }

                // Очікування розрахованої затримки
                std::this_thread::sleep_for(backoff_duration);
            }

            // Крок 3: Виконання фізичного виклику через мережевий транспорт
            auto result = transport(url, ctx.idempotency_key);

            if (result.has_value()) {
                const auto& resp = result.value();
                if (resp.status_code >= 200 && resp.status_code < 300) {
                    // Успіх: поповнюємо бюджет повторів новими токенами
                    budget_.record_success(policy_.budget_deposit_per_success);
                    return resp;
                }

                // Аналіз коду помилки класифікатором
                auto kind = HttpErrorClassifier::classify(resp.status_code);
                if (kind == ErrorKind::Permanent) {
                    return std::unexpected(RequestError{
                        ErrorKind::Permanent,
                        resp.status_code,
                        std::format("Постійна помилка HTTP {}, повтори скасовано", resp.status_code)
                    });
                }

                // Тимчасова помилка бекенда (503, 429) — переходимо до наступної ітерації циклу
                std::cout << std::format("  [Спроба {}] Тимчасова помилка HTTP {} -> планування повтору\n",
                                         attempt + 1, resp.status_code);
            } else {
                // Мережевий збій транспорту (скидання з'єднання TCP RST, timeout)
                int net_err = result.error();
                std::cout << std::format("  [Спроба {}] Мережевий збій сокета errno={} -> планування повтору\n",
                                         attempt + 1, net_err);
            }
        }

        return std::unexpected(RequestError{
            ErrorKind::Transient,
            503,
            "Вичерпано максимальний ліміт спроб (Max Retries Exceeded)"
        });
    }

    double get_budget_balance() const noexcept {
        return budget_.current_balance();
    }

private:
    RetryPolicy policy_;
    TokenBucketRetryBudget budget_;
    BackoffCalculator backoff_;
};

} // namespace net

int main() {
    using namespace std::chrono_literals;

    net::ResilientClient client;
    net::RequestContext ctx{
        .idempotency_key = "req-uuid-9874-aefc",
        .deadline = std::chrono::steady_clock::now() + 5000ms
    };

    int call_counter = 0;

    // Емулятор віддаленого сервера з тимчасовим збоєм
    auto mock_transport = [&call_counter](const std::string& url, 
                                          const std::string& key) -> std::expected<net::Response, int> {
        ++call_counter;
        if (call_counter <= 2) {
            // Перші 2 виклики завершуються тимчасовим збоєм 503 Service Unavailable
            return net::Response{.status_code = 503, .body = "Service Overloaded"};
        }
        // Третій виклик завершується успішно
        return net::Response{.status_code = 200, .body = "{\"status\":\"order_created\"}"};
    };

    std::cout << "Запуск стійкого клієнта з експоненційним відступом та джитером:\n";
    auto outcome = client.execute("https://api.payments.internal/v1/charge", ctx, mock_transport);

    if (outcome.has_value()) {
        std::cout << "Успішна відповідь: " << outcome.value().body << "\n";
        std::cout << "Баланс бюджету повторів: " << client.get_budget_balance() << " токенів\n";
    } else {
        std::cout << "Запит провалено: " << outcome.error().message << "\n";
    }

    return 0;
}

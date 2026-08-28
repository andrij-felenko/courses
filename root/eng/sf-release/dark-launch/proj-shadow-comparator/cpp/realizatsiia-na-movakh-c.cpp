#include <iostream>
#include <string>
#include <string_view>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <chrono>
#include <cmath>
#include <optional>
#include <format>
#include <utility>

namespace shadow {

constexpr double kEpsilon = 1e-6;

/* Структури предметної області */
struct TransactionRequest {
    uint64_t account_id{0};
    double amount{0.0};
    uint32_t currency_code{980};
    uint64_t timestamp_ms{0};
};

struct TransactionResult {
    double base_fee{0.0};
    double tax_fee{0.0};
    double total_charged{0.0};
    uint32_t execution_node_id{0};
    bool is_successful{false};

    /* Канонічне порівняння з маскуванням службових полів */
    [[nodiscard]] bool matches(const TransactionResult& other) const noexcept {
        if (is_successful != other.is_successful) return false;
        if (std::abs(base_fee - other.base_fee) > kEpsilon) return false;
        if (std::abs(tax_fee - other.tax_fee) > kEpsilon) return false;
        if (std::abs(total_charged - other.total_charged) > kEpsilon) return false;
        return true;
    }
};

/* Шаблонний диспетчер експериментів на сучасному C++20 */
template <typename Request, typename Response>
class ScientistEngine {
public:
    using Handler = std::function<Response(const Request&)>;
    using Comparator = std::function<bool(const Response&, const Response&)>;

    explicit ScientistEngine(size_t max_queue_size = 512)
        : max_capacity_(max_queue_size),
          worker_thread_([this](std::stop_token st) { worker_loop(st); }) {}

    ~ScientistEngine() {
        worker_thread_.request_stop();
        cv_.notify_all();
    }

    ScientistEngine(const ScientistEngine&) = delete;
    ScientistEngine& operator=(const ScientistEngine&) = delete;

    /* Виконання темного запуску: синхронний контроль і асинхронний кандидат */
    Response evaluate(std::string_view name,
                      const Request& req,
                      Handler control_fn,
                      Handler candidate_fn,
                      Comparator comparator = [](const Response& a, const Response& b) {
                          return a.matches(b);
                      }) {
        // 1. Синхронний запуск контрольного рушія
        const auto t0 = std::chrono::steady_clock::now();
        Response control_res = control_fn(req);
        const auto t1 = std::chrono::steady_clock::now();
        const auto ctrl_us = std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count();

        // 2. Неблокуюче планування тіньового завдання
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            if (task_queue_.size() < max_capacity_) {
                task_queue_.push(ShadowTask{
                    .experiment_name = std::string(name),
                    .request = req,
                    .control_res = control_res,
                    .control_duration_us = static_cast<uint64_t>(ctrl_us),
                    .candidate_fn = std::move(candidate_fn),
                    .comparator = std::move(comparator)
                });
                cv_.notify_one();
            } else {
                dropped_count_++;
            }
        }

        // 3. Негайне повернення контрольного результату клієнту
        return control_res;
    }

    [[nodiscard]] size_t dropped_count() const noexcept {
        return dropped_count_.load();
    }

private:
    struct ShadowTask {
        std::string experiment_name;
        Request request;
        Response control_res;
        uint64_t control_duration_us;
        Handler candidate_fn;
        Comparator comparator;
    };

    void worker_loop(std::stop_token stop_token) {
        while (!stop_token.stop_requested()) {
            ShadowTask current_task;
            {
                std::unique_lock<std::mutex> lock(queue_mutex_);
                cv_.wait(lock, [this, &stop_token] {
                    return !task_queue_.empty() || stop_token.stop_requested();
                });

                if (stop_token.stop_requested() && task_queue_.empty()) {
                    break;
                }

                current_task = std::move(task_queue_.front());
                task_queue_.pop();
            }

            // Безпечне ізольоване виконання кандидата
            try {
                const auto t_start = std::chrono::steady_clock::now();
                Response candidate_res = current_task.candidate_fn(current_task.request);
                const auto t_end = std::chrono::steady_clock::now();
                const auto cand_us = std::chrono::duration_cast<std::chrono::microseconds>(
                    t_end - t_start).count();

                if (current_task.comparator(current_task.control_res, candidate_res)) {
                    std::cout << "[ЗБІГ] Експеримент '" << current_task.experiment_name
                              << "' | Час: ctrl=" << current_task.control_duration_us
                              << "us, cand=" << cand_us << "us\n";
                } else {
                    std::cerr << "[РОЗБІЖНІСТЬ] Експеримент '" << current_task.experiment_name
                              << "': дані відповідей не збігаються!\n";
                }
            } catch (const std::exception& ex) {
                std::cerr << "[ЗБІЙ КАНДИДАТА] Експеримент '" << current_task.experiment_name
                          << "' викинув виняток: " << ex.what() << "\n";
            } catch (...) {
                std::cerr << "[КРИТИЧНИЙ ЗБІЙ] Невідомий виняток у тіньовому кандидаті\n";
            }
        }
    }

    size_t max_capacity_;
    std::atomic<size_t> dropped_count_{0};
    std::queue<ShadowTask> task_queue_;
    std::mutex queue_mutex_;
    std::condition_variable cv_;
    std::jthread worker_thread_;
};

} // namespace shadow

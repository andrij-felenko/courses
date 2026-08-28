#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <thread>
#include <future>
#include <mutex>
#include <condition_variable>
#include <stop_token>
#include <expected>
#include <format>
#include <random>

using namespace std::chrono_literals;

// Результат виконання окремої гілки віяла
struct BranchResponse {
    std::string branch_id;
    std::string data;
    std::chrono::milliseconds latency;
    bool was_hedged{false};
};

enum class AggregationStatus {
    SUCCESS,
    DEGRADED_PARTIAL,
    TIMEOUT_CRITICAL_FAILURE
};

struct GatherResult {
    AggregationStatus status;
    std::vector<BranchResponse> responses;
    std::vector<std::string> failed_branches;
    std::chrono::milliseconds total_duration;
};

// Завдання для окремої гілки віяла
struct ShardTask {
    std::string branch_id;
    std::string primary_url;
    std::string backup_url;
    bool is_critical{true};
};

// Імітація виклику віддаленого RPC із підтримкою stop_token
std::expected<BranchResponse, std::string> execute_single_rpc(
    const std::string& branch_id,
    const std::string& endpoint,
    std::stop_token stoken,
    bool is_hedged_call) 
{
    auto start_time = std::chrono::steady_clock::now();
    
    // Імітація мережевої затримки з випадковим сплеском
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(10, 120); // 10..120 мс
    int simulated_latency_ms = dis(gen);

    for (int elapsed = 0; elapsed < simulated_latency_ms; elapsed += 5) {
        if (stoken.stop_requested()) {
            return std::unexpected("Запит скасовано токеном зупинки");
        }
        std::this_thread::sleep_for(5ms);
    }

    if (stoken.stop_requested()) {
        return std::unexpected("Запит скасовано перед поверненням");
    }

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start_time);

    return BranchResponse{
        .branch_id = branch_id,
        .data = std::format("Payload from {}", endpoint),
        .latency = duration,
        .was_hedged = is_hedged_call
    };
}

// Виконання однієї гілки з геджуванням
std::expected<BranchResponse, std::string> execute_branch_with_hedging(
    const ShardTask& task,
    std::chrono::milliseconds hedge_delay,
    std::stop_token parent_stop_token)
{
    std::stop_source branch_stop_source;
    std::stop_callback parent_callback(parent_stop_token, [&]() {
        branch_stop_source.request_stop();
    });

    std::mutex mtx;
    std::condition_variable cv;
    std::expected<BranchResponse, std::string> result = std::unexpected("Немає відповіді");
    bool completed = false;

    // Запуск первинного виклику
    std::jthread primary_worker([&, st = branch_stop_source.get_token()]() {
        auto resp = execute_single_rpc(task.branch_id, task.primary_url, st, false);
        std::lock_guard<std::mutex> lock(mtx);
        if (!completed && resp.has_value()) {
            result = resp;
            completed = true;
            branch_stop_source.request_stop(); // Скасовуємо дублера, якщо запущено
            cv.notify_one();
        }
    });

    // Очікування завершення або вичерпання порогу геджування
    {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait_for(lock, hedge_delay, [&]() { 
            return completed || parent_stop_token.stop_requested(); 
        });
    }

    // Якщо первинний виклик не вклався в hedge_delay — запускаємо геджований запит
    std::unique_ptr<std::jthread> hedge_worker;
    if (!completed && !parent_stop_token.stop_requested()) {
        hedge_worker = std::make_unique<std::jthread>([&, st = branch_stop_source.get_token()]() {
            auto resp = execute_single_rpc(task.branch_id, task.backup_url, st, true);
            std::lock_guard<std::mutex> lock(mtx);
            if (!completed && resp.has_value()) {
                result = resp;
                completed = true;
                branch_stop_source.request_stop(); // Скасовуємо первинний
                cv.notify_one();
            }
        });
    }

    // Чекаємо фінального результату гілки
    {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&]() { 
            return completed || parent_stop_token.stop_requested(); 
        });
    }

    branch_stop_source.request_stop();
    return result;
}

// Головний координатор Scatter-Gather
GatherResult scatter_gather_execute(
    const std::vector<ShardTask>& tasks,
    std::chrono::milliseconds hedge_delay,
    std::chrono::milliseconds global_deadline)
{
    auto start_all = std::chrono::steady_clock::now();
    std::stop_source global_stop_source;

    std::vector<std::future<std::expected<BranchResponse, std::string>>> futures;
    futures.reserve(tasks.size());

    // Scatter-фаза: паралельний запуск усіх завдань
    for (const auto& task : tasks) {
        futures.push_back(std::async(std::launch::async, [&task, hedge_delay, st = global_stop_source.get_token()]() {
            return execute_branch_with_hedging(task, hedge_delay, st);
        }));
    }

    // Очікування завершення або настання глобального дедлайну
    GatherResult final_result;
    bool has_critical_failure = false;

    for (size_t i = 0; i < tasks.size(); ++i) {
        auto remaining_time = global_deadline - std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start_all);

        if (remaining_time <= 0ms) {
            global_stop_source.request_stop(); // Зупиняємо решту
            final_result.failed_branches.push_back(tasks[i].branch_id);
            if (tasks[i].is_critical) has_critical_failure = true;
            continue;
        }

        if (futures[i].wait_for(remaining_time) == std::future_status::ready) {
            auto res = futures[i].get();
            if (res.has_value()) {
                final_result.responses.push_back(std::move(res.value()));
            } else {
                final_result.failed_branches.push_back(tasks[i].branch_id);
                if (tasks[i].is_critical) has_critical_failure = true;
            }
        } else {
            global_stop_source.request_stop();
            final_result.failed_branches.push_back(tasks[i].branch_id);
            if (tasks[i].is_critical) has_critical_failure = true;
        }
    }

    final_result.total_duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start_all);

    if (has_critical_failure) {
        final_result.status = AggregationStatus::TIMEOUT_CRITICAL_FAILURE;
    } else if (!final_result.failed_branches.empty()) {
        final_result.status = AggregationStatus::DEGRADED_PARTIAL;
    } else {
        final_result.status = AggregationStatus::SUCCESS;
    }

    return final_result;
}

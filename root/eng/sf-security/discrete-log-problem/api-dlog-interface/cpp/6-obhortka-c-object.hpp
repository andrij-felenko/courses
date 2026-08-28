#pragma once
#include <cstdint>
#include <optional>
#include <chrono>
#include <string>
#include <stdexcept>

namespace dlog::api {

// Виняток для помилок конфігурації або арифметики
class Exception : public std::runtime_error {
public:
    explicit Exception(const std::string& msg, dlog_status_t status)
        : std::runtime_error(msg), status_(status) {}

    [[nodiscard]] dlog_status_t status() const noexcept { return status_; }
private:
    dlog_status_t status_;
};

struct SolverOptions {
    Method method = Method::Auto;
    std::size_t max_memory_bytes = 1024 * 1024 * 512; // 512 MiB
    std::uint64_t max_steps = 10000000000ULL;
    std::uint32_t num_threads = 0;
    bool verbose = false;
};

struct ExecutionReport {
    std::uint64_t exponent = 0;
    bool success = false;
    std::uint64_t steps = 0;
    std::chrono::duration<double, std::milli> execution_time{0};
    std::size_t memory_bytes = 0;
    std::string error_message;
};

class DiscreteLogEngine {
public:
    explicit DiscreteLogEngine(SolverOptions options = {}) 
        : opts_(std::move(options)) {}

    [[nodiscard]] ExecutionReport solve(
        std::uint64_t g, 
        std::uint64_t y, 
        std::uint64_t p, 
        std::uint64_t group_order
    ) const {
        dlog_config_t cfg;
        dlog_config_init_default(&cfg);
        cfg.method = static_cast<dlog_method_t>(opts_.method);
        cfg.max_memory_bytes = opts_.max_memory_bytes;
        cfg.max_steps = opts_.max_steps;
        cfg.num_threads = opts_.num_threads;
        cfg.verbose_logging = opts_.verbose;

        void* ctx = nullptr;
        if (dlog_context_create(&cfg, &ctx) != DLOG_SUCCESS) {
            throw Exception("Failed to create dlog context", DLOG_OUT_OF_MEMORY);
        }

        dlog_result_t res;
        dlog_status_t st = dlog_solve_uint64(ctx, g, y, p, group_order, &res);
        dlog_context_destroy(ctx);

        ExecutionReport report;
        report.success = (st == DLOG_SUCCESS);
        report.exponent = res.exponent;
        report.steps = res.steps_executed;
        report.execution_time = std::chrono::duration<double, std::milli>(res.time_elapsed_ms);
        report.memory_bytes = res.memory_used_bytes;
        
        if (!report.success) {
            report.error_message = "Status code: " + std::to_string(static_cast<int>(st));
        }

        return report;
    }

    void update_options(const SolverOptions& opts) { opts_ = opts; }
    [[nodiscard]] const SolverOptions& options() const noexcept { return opts_; }

private:
    SolverOptions opts_;
};

} // namespace dlog::api

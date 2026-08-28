// task_profiler.hpp - C++20 API профілювальника з RAII Scope
#pragma once

#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <algorithm>

namespace RealTime {

struct TaskStats {
    std::string_view name{"Unnamed"};
    uint32_t expected_period_cyc{0};
    uint32_t min_cyc{UINT32_MAX};
    uint32_t max_cyc{0};
    uint64_t total_cyc{0};
    uint32_t call_count{0};
    uint32_t max_jitter_cyc{0};
    uint32_t last_start_cyc{0};
    uint32_t last_duration_cyc{0};
};

template <size_t MaxTasks = 8>
class TaskProfiler {
public:
    explicit TaskProfiler(uint32_t cpu_freq_hz) noexcept : cpu_freq_hz_(cpu_freq_hz) {
        init_hardware();
    }

    void register_task(uint8_t id, std::string_view name, uint32_t expected_period_us) noexcept {
        if (id >= MaxTasks) return;
        tasks_[id].name = name;
        tasks_[id].expected_period_cyc = (expected_period_us * (cpu_freq_hz_ / 1'000'000U));
        tasks_[id].min_cyc = UINT32_MAX;
        tasks_[id].max_cyc = 0;
        tasks_[id].total_cyc = 0;
        tasks_[id].call_count = 0;
        tasks_[id].max_jitter_cyc = 0;
        tasks_[id].last_start_cyc = 0;
    }

    void enter(uint8_t id) noexcept {
        if (id >= MaxTasks) return;
        const uint32_t now = read_cyccnt();
        auto& t = tasks_[id];

        if (t.expected_period_cyc > 0 && t.last_start_cyc > 0) {
            const uint32_t actual_period = now - t.last_start_cyc;
            const uint32_t jitter = (actual_period > t.expected_period_cyc)
                ? (actual_period - t.expected_period_cyc)
                : (t.expected_period_cyc - actual_period);
            if (jitter > t.max_jitter_cyc) {
                t.max_jitter_cyc = jitter;
            }
        }
        t.last_start_cyc = now;
    }

    void exit(uint8_t id) noexcept {
        const uint32_t stop = read_cyccnt();
        if (id >= MaxTasks) return;
        auto& t = tasks_[id];
        
        uint32_t elapsed = stop - t.last_start_cyc;
        if (elapsed >= overhead_cyc_) {
            elapsed -= overhead_cyc_;
        }

        t.last_duration_cyc = elapsed;
        t.total_cyc += elapsed;
        t.call_count++;

        if (elapsed < t.min_cyc) t.min_cyc = elapsed;
        if (elapsed > t.max_cyc) t.max_cyc = elapsed;
    }

    [[nodiscard]] const TaskStats& get_stats(uint8_t id) const noexcept {
        static constexpr TaskStats empty_stats{};
        return (id < MaxTasks) ? tasks_[id] : empty_stats;
    }

    [[nodiscard]] uint32_t cyc_to_us(uint32_t cyc) const noexcept {
        return static_cast<uint32_t>((static_cast<uint64_t>(cyc) * 1'000'000ULL) / cpu_freq_hz_);
    }

    // RAII Guard для автоматичного вимірювання області видимості
    class ScopeGuard {
    public:
        ScopeGuard(TaskProfiler& profiler, uint8_t id) noexcept
            : profiler_(profiler), id_(id) {
            profiler_.enter(id_);
        }
        ~ScopeGuard() noexcept {
            profiler_.exit(id_);
        }
        ScopeGuard(const ScopeGuard&) = delete;
        ScopeGuard& operator=(const ScopeGuard&) = delete;
    private:
        TaskProfiler& profiler_;
        uint8_t id_;
    };

    [[nodiscard]] ScopeGuard make_scope(uint8_t id) noexcept {
        return ScopeGuard(*this, id);
    }

private:
    void init_hardware() noexcept;
    static inline uint32_t read_cyccnt() noexcept;

    uint32_t cpu_freq_hz_{168'000'000U};
    uint32_t overhead_cyc_{0};
    std::array<TaskStats, MaxTasks> tasks_{};
};

} // namespace RealTime

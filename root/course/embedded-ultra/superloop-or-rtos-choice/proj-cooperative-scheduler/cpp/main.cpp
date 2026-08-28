#include <cstdint>
#include <array>
#include <span>
#include <functional>
#include <algorithm>

enum class TaskPriority : uint8_t {
    Low = 0,
    Medium = 1,
    High = 2,
    Realtime = 3
};

struct TaskMetrics {
    uint32_t max_duration_us{0};
    uint32_t total_duration_us{0};
    uint32_t execution_count{0};
    uint32_t overrun_count{0};
};

template <size_t MaxTasks>
class CooperativeScheduler {
public:
    using TaskCallback = void (*)(uint32_t now_us);

    struct Task {
        TaskCallback callback{nullptr};
        uint32_t period_us{0};
        uint32_t next_execution_us{0};
        TaskPriority priority{TaskPriority::Low};
        volatile uint8_t event_flags{0};
        bool enabled{false};
        TaskMetrics metrics{};
    };

    constexpr CooperativeScheduler() = default;

    bool add_task(TaskCallback fn, uint32_t period_us, TaskPriority priority = TaskPriority::Medium) noexcept {
        if (task_count_ >= MaxTasks || fn == nullptr) {
            return false;
        }

        const uint32_t now = get_platform_micros();
        tasks_[task_count_] = Task{
            .callback = fn,
            .period_us = period_us,
            .next_execution_us = now + period_us,
            .priority = priority,
            .event_flags = 0,
            .enabled = true,
            .metrics = {}
        };
        ++task_count_;
        return true;
    }

    void trigger_event(size_t task_index, uint8_t flag) noexcept {
        if (task_index < task_count_) {
            tasks_[task_index].event_flags |= flag;
        }
    }

    void dispatch() noexcept {
        const uint32_t now = get_platform_micros();
        int32_t best_index = -1;
        TaskPriority highest_priority = TaskPriority::Low;
        int32_t max_overdue = 0;
        bool event_active = false;

        for (size_t i = 0; i < task_count_; ++i) {
            auto& t = tasks_[i];
            if (!t.enabled) continue;

            if (t.event_flags != 0) {
                best_index = static_cast<int32_t>(i);
                highest_priority = t.priority;
                event_active = true;
                break;
            }

            const int32_t delta = static_cast<int32_t>(now - t.next_execution_us);
            if (delta >= 0) {
                if (best_index == -1 || t.priority > highest_priority ||
                   (t.priority == highest_priority && delta > max_overdue)) {
                    best_index = static_cast<int32_t>(i);
                    highest_priority = t.priority;
                    max_overdue = delta;
                }
            }
        }

        if (best_index >= 0) {
            auto& task = tasks_[static_cast<size_t>(best_index)];
            const uint32_t start_us = get_platform_micros();

            if (event_active) {
                task.event_flags = 0;
            }

            task.callback(start_us);

            const uint32_t duration_us = get_platform_micros() - start_us;
            task.metrics.total_duration_us += duration_us;
            task.metrics.max_duration_us = std::max(task.metrics.max_duration_us, duration_us);
            ++task.metrics.execution_count;

            if (task.period_us > 0) {
                task.next_execution_us += task.period_us;

                const uint32_t post_exec_now = get_platform_micros();
                if (static_cast<int32_t>(post_exec_now - task.next_execution_us) >= static_cast<int32_t>(task.period_us)) {
                    ++task.metrics.overrun_count;
                    ++global_overruns_;
                    task.next_execution_us = post_exec_now + task.period_us;
                }
            }
        } else {
            enter_sleep_mode();
        }
    }

    [[nodiscard]] std::span<const Task> tasks() const noexcept {
        return std::span<const Task>(tasks_.data(), task_count_);
    }

    [[nodiscard]] uint32_t total_overruns() const noexcept {
        return global_overruns_;
    }

private:
    static uint32_t get_platform_micros() noexcept;
    static void enter_sleep_mode() noexcept;

    std::array<Task, MaxTasks> tasks_{};
    size_t task_count_{0};
    uint32_t global_overruns_{0};
};

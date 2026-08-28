#include <cstdint>
#include <array>
#include <algorithm>

class FlightTaskScheduler {
public:
    using Callback = void (*)(uint32_t now_us);

    struct TaskDescriptor {
        Callback execute{nullptr};
        uint32_t period_us{0};
        uint32_t next_run_us{0};
        uint8_t priority{0};
    };

    template <size_t N>
    static void dispatch(std::array<TaskDescriptor, N>& tasks) noexcept {
        const uint32_t now = get_system_micros();
        int32_t selected_index = -1;
        uint8_t highest_prio = 0;

        for (size_t i = 0; i < N; ++i) {
            const auto& task = tasks[i];
            if (static_cast<int32_t>(now - task.next_run_us) >= 0) {
                if (selected_index == -1 || task.priority > highest_prio) {
                    selected_index = static_cast<int32_t>(i);
                    highest_prio = task.priority;
                }
            }
        }

        if (selected_index >= 0) {
            auto& ready_task = tasks[static_cast<size_t>(selected_index)];
            ready_task.execute(now);
            ready_task.next_run_us += ready_task.period_us;
        }
    }

private:
    static uint32_t get_system_micros() noexcept;
};

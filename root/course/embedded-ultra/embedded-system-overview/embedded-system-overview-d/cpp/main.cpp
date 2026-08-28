// Ідіоматичний еквівалент неблокуючого диспетчера на C++
#include <cstdint>
#include <array>

namespace scheduler {

struct Task {
    void (*handler)();
    uint32_t interval_us;
    uint32_t last_run_us;
};

extern uint32_t get_system_micros() noexcept;
extern void fast_loop_gyro_and_motors_1khz() noexcept;
extern void medium_loop_attitude_250hz() noexcept;
extern void slow_loop_telemetry_10hz() noexcept;

class Dispatcher {
public:
    void init() noexcept {
        const uint32_t now = get_system_micros();
        tasks_[0] = {fast_loop_gyro_and_motors_1khz, 1000, now};
        tasks_[1] = {medium_loop_attitude_250hz, 4000, now};
        tasks_[2] = {slow_loop_telemetry_10hz, 100000, now};
    }

    void poll() noexcept {
        const uint32_t now = get_system_micros();
        for (auto& task : tasks_) {
            if ((now - task.last_run_us) >= task.interval_us) {
                task.last_run_us += task.interval_us;
                task.handler();
            }
        }
    }

private:
    std::array<Task, 3> tasks_{};
};

} // namespace scheduler

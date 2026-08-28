#include <iostream>
#include <chrono>
#include <system_error>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched.h>
#include <sched.h>

struct SchedAttrNative {
    std::uint32_t size;
    std::uint32_t sched_policy;
    std::uint64_t sched_flags;
    std::int32_t  sched_nice;
    std::uint32_t sched_priority;
    std::uint64_t sched_runtime;
    std::uint64_t sched_deadline;
    std::uint64_t sched_period;
};

class DeadlineTask {
public:
    static void configure(std::chrono::nanoseconds runtime,
                          std::chrono::nanoseconds deadline,
                          std::chrono::nanoseconds period) {
        SchedAttrNative attr{};
        attr.size = sizeof(attr);
        attr.sched_policy = SCHED_DEADLINE;
        attr.sched_flags = SCHED_FLAG_RECLAIM;
        attr.sched_runtime = static_cast<std::uint64_t>(runtime.count());
        attr.sched_deadline = static_cast<std::uint64_t>(deadline.count());
        attr.sched_period = static_cast<std::uint64_t>(period.count());

        if (syscall(__NR_sched_setattr, 0, &attr, 0) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити SCHED_DEADLINE");
        }
    }

    static void yield_period() noexcept {
        ::sched_yield();
    }
};

int main() {
    using namespace std::chrono_literals;

    try {
        DeadlineTask::configure(10ms, 30ms, 30ms);
        std::cout << "Потік SCHED_DEADLINE успішно ініціалізовано.\n";

        for (int step = 0; step < 5; ++step) {
            /* Обробка циклу реального часу */
            DeadlineTask::yield_period();
        }
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}

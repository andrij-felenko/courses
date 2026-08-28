#include <pthread.h>
#include <sched.h>
#include <system_error>
#include <expected>

std::expected<void, std::error_code> configure_thread_rt_and_affinity(pthread_t thread, int priority, int cpu_id) noexcept {
    // 1. Встановлення RT-пріоритету SCHED_FIFO
    struct sched_param param{};
    param.sched_priority = priority;
    if (int res = pthread_setschedparam(thread, SCHED_FIFO, &param); res != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(res)));
    }

    // 2. Прив'язка до конкретного ядра CPU
    cpu_set_t cpuset{};
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (int res = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset); res != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(res)));
    }

    return {};
}

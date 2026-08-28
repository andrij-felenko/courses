#include <iostream>
#include <vector>
#include <chrono>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>

class ThreadIsolator {
public:
    static void isolate_current_thread(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);

        if (int err = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset); err != 0) {
            throw std::system_error(err, std::generic_category(), "pthread_setaffinity_np failed");
        }

        sched_param param{.sched_priority = 99};
        if (int err = pthread_setschedparam(pthread_self(), SCHED_FIFO, &param); err != 0) {
            throw std::system_error(err, std::generic_category(), "pthread_setschedparam failed (потрібні права root)");
        }

        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }
    }
};

int main() {
    constexpr int target_cpu = 1;
    constexpr uint64_t iterations = 10000000;
    constexpr int64_t jitter_threshold_ns = 1000;

    try {
        std::cout << "Ініціалізація ізоляції для CPU " << target_cpu << "...\n";
        ThreadIsolator::isolate_current_thread(target_cpu);

        // RAII-буфер з попередньою ініціалізацією (запобігає page faults)
        std::vector<uint8_t> warm_buffer(1024 * 1024, 0);
        volatile uint8_t sink = warm_buffer[0];
        (void)sink;

        std::cout << "Запуск гарячого циклу вимірювання затримок...\n";

        uint64_t max_jitter_ns = 0;
        auto prev_time = std::chrono::steady_clock::now();

        for (uint64_t i = 0; i < iterations; ++i) {
            auto current_time = std::chrono::steady_clock::now();
            auto delta_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(current_time - prev_time).count();
            prev_time = current_time;

            if (i > 0 && delta_ns > jitter_threshold_ns) {
                const auto jitter = static_cast<uint64_t>(delta_ns);
                if (jitter > max_jitter_ns) {
                    max_jitter_ns = jitter;
                }
            }
        }

        std::cout << "Вимірювання завершено.\n";
        std::cout << "Максимальний OS jitter: " << max_jitter_ns << " наносекунд\n";

    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

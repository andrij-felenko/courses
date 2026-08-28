#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <chrono>
#include <system_error>
#include <expected>
#include <memory>
#include <cstring>
#include <cstdint>
#include <cstdlib>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>
#include <time.h>

// RAII для блокування пам'яті
class ScopedMemoryLock {
public:
    ScopedMemoryLock() {
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }
    }
    ~ScopedMemoryLock() {
        munlockall();
    }
    ScopedMemoryLock(const ScopedMemoryLock&) = delete;
    ScopedMemoryLock& operator=(const ScopedMemoryLock&) = delete;
};

// RAII для керування C-states через /dev/cpu_dma_latency
class ScopedCStateControl {
private:
    int fd_{-1};
public:
    ScopedCStateControl() {
        fd_ = open("/dev/cpu_dma_latency", O_WRONLY);
        if (fd_ >= 0) {
            int32_t latency = 0;
            if (write(fd_, &latency, sizeof(latency)) != sizeof(latency)) {
                close(fd_);
                fd_ = -1;
            }
        }
    }
    ~ScopedCStateControl() {
        if (fd_ >= 0) {
            close(fd_);
        }
    }
    [[nodiscard]] bool is_active() const noexcept { return fd_ >= 0; }
    ScopedCStateControl(const ScopedCStateControl&) = delete;
    ScopedCStateControl& operator=(const ScopedCStateControl&) = delete;
};

static void stack_prefault() noexcept {
    constexpr std::size_t stack_size = 64 * 1024; // 64 КБ, із запасом менше за межу стека
    constexpr std::size_t page_size = 4096;
    volatile unsigned char dummy[stack_size];
    // Саме масив на стеку, а не vector: купа тут не допомогла б — прогріваємо сторінки стека
    for (std::size_t i = 0; i < stack_size; i += page_size) {
        dummy[i] = 0;
    }
}

static std::expected<void, std::error_code> set_realtime_priority_and_affinity(int priority, int cpu_id) noexcept {
    // 1. Встановлення RT пріоритету
    sched_param param{};
    param.sched_priority = priority;
    if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }

    // 2. Прив'язка до CPU: pthread_* повертає код помилки, errno не чіпає
    cpu_set_t cpuset{};
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (int res = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset); res != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(res)));
    }

    return {};
}

int main(int argc, char* argv[]) {
    try {
        int target_cpu = 1;
        if (argc > 1) {
            target_cpu = std::atoi(argv[1]);
        }

        std::cout << "Запуск C++ тесту затримки на CPU " << target_cpu << "...\n";

        ScopedMemoryLock mem_lock;
        stack_prefault();
        ScopedCStateControl cstate_ctrl;

        if (!cstate_ctrl.is_active()) {
            std::clog << "Попередження: не вдалося заблокувати C-states через /dev/cpu_dma_latency\n";
        }

        if (auto res = set_realtime_priority_and_affinity(80, target_cpu); !res) {
            std::cerr << "Не вдалося ініціалізувати RT/Affinity: " << res.error().message() 
                      << " (потрібні права root / CAP_SYS_NICE)\n";
            return 1;
        }

        constexpr int iterations = 10000;
        std::vector<long long> latencies_us;
        latencies_us.reserve(iterations);

        timespec t_next{};
        clock_gettime(CLOCK_MONOTONIC, &t_next);

        for (int i = 0; i < iterations; ++i) {
            t_next.tv_nsec += 1'000'000L; // +1 мілісекунда
            if (t_next.tv_nsec >= 1'000'000'000L) {
                t_next.tv_nsec -= 1'000'000'000L;
                t_next.tv_sec += 1;
            }

            if (int ret = clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &t_next, nullptr); ret != 0) {
                std::cerr << "clock_nanosleep помилка: " << ret << "\n";
                break;
            }

            timespec t_actual{};
            clock_gettime(CLOCK_MONOTONIC, &t_actual);

            long long diff_ns = (t_actual.tv_sec - t_next.tv_sec) * 1'000'000'000LL +
                                (t_actual.tv_nsec - t_next.tv_nsec);
            latencies_us.push_back(diff_ns / 1000);
        }

        if (latencies_us.empty()) {           // цикл обірвало на першій же ітерації
            std::cerr << "Жодної ітерації не виміряно.\n";
            return 1;
        }

        auto [min_it, max_it] = std::minmax_element(latencies_us.begin(), latencies_us.end());
        double avg = std::accumulate(latencies_us.begin(), latencies_us.end(), 0.0) / latencies_us.size();

        std::cout << "Результати тестування затримки (" << latencies_us.size() << " ітерацій):\n"
                  << "  Мінімальна затримка: " << *min_it << " мкс\n"
                  << "  Максимальна затримка: " << *max_it << " мкс\n"
                  << "  Середня затримка:    " << avg << " мкс\n";

    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << "\n";
        return 1;
    }

    return 0;
}

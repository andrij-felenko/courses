#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <chrono>
#include <thread>
#include <fstream>
#include <system_error>
#include <format>
#include <sched.h>
#include <pthread.h>
#include <sys/mman.h>

class RealTimeSession {
public:
    explicit RealTimeSession(int cpu_id, int priority) {
        // 1. Блокування пам'яті через RAII
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }

        // 2. Встановлення CPU Affinity
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
            throw std::system_error(errno, std::generic_category(), "pthread_setaffinity_np failed");
        }

        // 3. Налаштування SCHED_FIFO
        sched_param param{.sched_priority = priority};
        if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
            throw std::system_error(errno, std::generic_category(), "sched_setscheduler failed");
        }
    }

    ~RealTimeSession() {
        munlockall();
    }
};

class FtraceControl {
public:
    static void stop_tracing(std::string_view reason, long latency_us) {
        std::ofstream ofs("/sys/kernel/tracing/tracing_on");
        if (ofs.is_open()) {
            ofs << "0";
            std::cout << std::format("[CRITICAL] ftrace stopped! Reason: {} (latency: {} us)\n",
                                     reason, latency_us);
        }
    }
};

int main(int argc, char* argv[]) {
    int cpu_id = 1;
    long threshold_us = 20;
    constexpr int iterations = 10000;
    constexpr std::chrono::microseconds period{1000};

    if (argc > 1) cpu_id = std::stoi(argv[1]);
    if (argc > 2) threshold_us = std::stol(argv[2]);

    std::cout << std::format("=== Real-Time Latency Harness (C++20) ===\n"
                             "Target CPU: {}, Priority: SCHED_FIFO 95, Period: 1000 us, Threshold: {} us\n",
                             cpu_id, threshold_us);

    try {
        RealTimeSession rt_session(cpu_id, 95);

        std::vector<long> latencies;
        latencies.reserve(iterations);

        auto next_wakeup = std::chrono::steady_clock::now();

        // Прогрів стеку
        std::vector<uint8_t> stack_warmup(8192, 0);

        for (int i = 0; i < iterations; ++i) {
            next_wakeup += period;
            std::this_thread::sleep_until(next_wakeup);

            auto now = std::chrono::steady_clock::now();
            auto latency_us = std::chrono::duration_cast<std::chrono::microseconds>(now - next_wakeup).count();

            latencies.push_back(latency_us);

            if (latency_us > threshold_us) {
                FtraceControl::stop_tracing("Latency threshold exceeded", latency_us);
                break;
            }
        }

        if (!latencies.empty()) {
            auto [min_it, max_it] = std::minmax_element(latencies.begin(), latencies.end());
            double sum = std::accumulate(latencies.begin(), latencies.end(), 0.0);
            double avg = sum / latencies.size();

            double sq_sum = std::accumulate(latencies.begin(), latencies.end(), 0.0,
                [avg](double acc, long val) { return acc + (val - avg) * (val - avg); });
            double stddev = std::sqrt(sq_sum / latencies.size());

            std::cout << std::format("\n=== Результати вимірювання затримок ===\n"
                                     "Ітерацій виконано: {}\n"
                                     "Мінімальна затримка:  {} us\n"
                                     "Середня затримка:     {:.2f} us\n"
                                     "Максимальна затримка: {} us\n"
                                     "Стандартне відхилення: {:.2f} us\n",
                                     latencies.size(), *min_it, avg, *max_it, stddev);
        }

    } catch (const std::exception& e) {
        std::cerr << std::format("Error: {}\n", e.what());
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

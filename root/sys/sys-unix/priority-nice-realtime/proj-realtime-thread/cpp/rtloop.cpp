/* rtloop.cpp — періодичний C++20 потік на SCHED_FIFO з вимірюванням запізнення.
 * g++ -O2 -Wall -std=c++20 -pthread -Wl,-z,now -o rtloop_cpp rtloop.cpp             */
#define _GNU_SOURCE
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <memory>
#include <vector>
#include <thread>
#include <fcntl.h>
#include <malloc.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>

constexpr std::chrono::nanoseconds PERIOD{1'000'000}; // 1 кГц
constexpr uint64_t RUN_SECONDS = 60;
constexpr uint64_t ITERATIONS = (RUN_SECONDS * 1'000'000'000ULL) / PERIOD.count();
constexpr int RT_PRIORITY = 60;
constexpr size_t STACK_BYTES = 512 * 1024;
constexpr size_t PREFAULT = 256 * 1024;
constexpr size_t BUCKETS = 2000;

struct Stats {
    std::vector<uint32_t> hist{std::vector<uint32_t>(BUCKETS, 0)};
    uint64_t samples{0}, sum_ns{0}, worst_ns{0};
    long minflt_before{0}, minflt_after{0};
};

static void prefault_stack() {
    volatile unsigned char deep[PREFAULT];
    long page = sysconf(_SC_PAGESIZE);
    for (size_t i = 0; i < PREFAULT; i += static_cast<size_t>(page))
        deep[i] = 0;
}

int main() {
    prefault_stack();
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        std::perror("mlockall");
        std::cerr << "Попередження: запуск без CAP_IPC_LOCK\n";
    }

    auto stats = std::make_unique<Stats>();

    struct rusage ru;
    getrusage(RUSAGE_THREAD, &ru);
    stats->minflt_before = ru.ru_minflt;

    struct sched_param param{};
    param.sched_priority = RT_PRIORITY;
    if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
        std::perror("pthread_setschedparam");
        std::cerr << "Помилка: потрібні CAP_SYS_NICE або запуск від root\n";
        return 1;
    }

    auto next = std::chrono::steady_clock::now() + PERIOD;

    for (uint64_t i = 0; i < ITERATIONS; ++i) {
        std::this_thread::sleep_until(next);
        auto now = std::chrono::steady_clock::now();

        if (now > next) {
            auto latency_ns = static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(now - next).count());
            stats->samples++;
            stats->sum_ns += latency_ns;
            if (latency_ns > stats->worst_ns) stats->worst_ns = latency_ns;
            size_t bucket = latency_ns / 1000;
            if (bucket >= BUCKETS) bucket = BUCKETS - 1;
            stats->hist[bucket]++;
        }

        next += PERIOD;
    }

    getrusage(RUSAGE_THREAD, &ru);
    stats->minflt_after = ru.ru_minflt;

    std::cout << "Зразків: " << stats->samples << ", Середнє: " 
              << (stats->samples ? stats->sum_ns / stats->samples : 0) 
              << " нс, Найгірше: " << stats->worst_ns << " нс, Page faults: " 
              << (stats->minflt_after - stats->minflt_before) << "\n";

    return 0;
}

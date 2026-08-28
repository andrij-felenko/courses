// latency.cpp — вимірювач затримки планування мовою C++
// збірка:  g++ -O2 -Wall -pthread latency.cpp -o latency_cpp
// запуск:  sudo ./latency_cpp [період_мкс] [секунд] [ядро]

#include <array>
#include <cerrno>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

class ScopedMlockall {
public:
    ScopedMlockall() {
        if (::mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            throw std::system_error(errno, std::generic_category(), "mlockall failed");
        }
    }
};

static void warm_stack() {
    constexpr std::size_t warm_bytes = 256 * 1024;
    std::array<std::uint8_t, warm_bytes> pad{};   /* саме на стеку: vector дав би купу */
    asm volatile("" :: "r"(pad.data()) : "memory");
}

int main(int argc, char **argv) {
    long period_us = (argc > 1) ? std::stol(argv[1]) : 200;
    long run_sec   = (argc > 2) ? std::stol(argv[2]) : 600;
    int  cpu_id    = (argc > 3) ? std::stoi(argv[3]) : 3;

    try {
        ScopedMlockall memory_lock;

        constexpr std::size_t buckets_count = 2000;
        std::vector<unsigned long> hist(buckets_count, 0);
        unsigned long over = 0;
        unsigned long total = 0;
        long worst = 0;

        cpu_set_t set;
        CPU_ZERO(&set);
        CPU_SET(cpu_id, &set);

        sched_param sp{ .sched_priority = 80 };
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        pthread_attr_setstacksize(&attr, 1024 * 1024);
        pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
        pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
        pthread_attr_setschedparam(&attr, &sp);
        pthread_attr_setaffinity_np(&attr, sizeof(set), &set);

        auto worker = [&]() {
            warm_stack();

            struct timespec next{}, now{};
            clock_gettime(CLOCK_MONOTONIC, &next);
            next.tv_nsec = 0;
            next.tv_sec += 1;

            const long period_ns = period_us * 1000L;
            const long cycles = run_sec * (1'000'000'000L / period_ns);

            for (long i = 0; i < cycles; ++i) {
                next.tv_nsec += period_ns;
                while (next.tv_nsec >= 1'000'000'000L) {
                    next.tv_nsec -= 1'000'000'000L;
                    next.tv_sec += 1;
                }

                while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, nullptr) == EINTR) {}

                clock_gettime(CLOCK_MONOTONIC, &now);

                long late_us = ((now.tv_sec - next.tv_sec) * 1'000'000'000L + (now.tv_nsec - next.tv_nsec)) / 1000L;
                if (late_us < 0) late_us = 0;
                if (late_us > worst) worst = late_us;
                if (static_cast<std::size_t>(late_us) < buckets_count) {
                    hist[static_cast<std::size_t>(late_us)]++;
                } else {
                    over++;
                }
                total++;
            }
        };

        pthread_t th;
        if (pthread_create(&th, &attr, [](void *arg) -> void* {
            (*static_cast<decltype(worker)*>(arg))();
            return nullptr;
        }, &worker) != 0) {
            std::cerr << "pthread_create: немає прав на SCHED_FIFO?\n";
            return 1;
        }
        pthread_join(th, nullptr);
        pthread_attr_destroy(&attr);

        unsigned long long acc = 0;
        long p50 = -1, p999 = -1, p99999 = -1;
        for (std::size_t i = 0; i < hist.size(); ++i) {
            if (hist[i] == 0) continue;
            acc += hist[i];
            if (p50 < 0 && acc * 2 >= total) p50 = static_cast<long>(i);
            if (p999 < 0 && acc * 1000 >= total * 999) p999 = static_cast<long>(i);
            if (p99999 < 0 && acc * 100000 >= total * 99999) p99999 = static_cast<long>(i);
            std::cout << i << " мкс: " << hist[i] << "\n";
        }

        std::cout << "\nобертів " << total << ", поза гістограмою " << over << "\n"
                  << "медіана " << p50 << " мкс · 99.9% " << p999 << " мкс · 99.999% " << p99999
                  << " мкс · максимум " << worst << " мкс\n";
    } catch (const std::exception &e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}

#include <iostream>
#include <vector>
#include <thread>
#include <chrono>
#include <span>
#include <numeric>
#include <stdexcept>
#include <pthread.h>
#include <sched.h>

constexpr size_t L1_TEST_SIZE = 24 * 1024; // 24 КБ на потік
constexpr size_t ITERATIONS   = 25000000;

// Встановлення спорідненості потоку до логічного CPU
void set_thread_affinity(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        throw std::runtime_error("Не вдалося встановити CPU affinity");
    }
}

// Робоче навантаження: інтенсивне читання й модифікація робочого набору в L1D
void cache_thrashing_worker(int cpu_id, std::span<uint8_t> buffer, size_t iterations, double &elapsed_ms) {
    set_thread_affinity(cpu_id);

    const size_t mask = buffer.size() - 1;
    const auto start = std::chrono::high_resolution_clock::now();

    uint32_t val = 0x12345678;
    size_t idx = 0;
    for (size_t i = 0; i < iterations; ++i) {
        idx = (idx * 1103515245 + 12345) & mask;
        buffer[idx] ^= static_cast<uint8_t>(val & 0xFF);
        val = (val >> 1) | (val << 31);
    }

    const auto end = std::chrono::high_resolution_clock::now();
    elapsed_ms = std::chrono::duration<double, std::milli>(end - start).count();
}

int main(int argc, char **argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <cpu_id_0> <cpu_id_1>
";
        std::cerr << "  Спільне ядро SMT:   " << argv[0] << " 0 1
";
        std::cerr << "  Окремі ядра:        " << argv[0] << " 0 2
";
        return 1;
    }

    const int cpu0 = std::stoi(argv[1]);
    const int cpu1 = std::stoi(argv[2]);

    std::vector<uint8_t> buffer0(L1_TEST_SIZE);
    std::vector<uint8_t> buffer1(L1_TEST_SIZE);

    std::iota(buffer0.begin(), buffer0.end(), static_cast<uint8_t>(0));
    std::iota(buffer1.begin(), buffer1.end(), static_cast<uint8_t>(42));

    double time0 = 0.0, time1 = 0.0;

    std::cout << "=== Запуск тесту на CPU " << cpu0 << " та CPU " << cpu1 << " ===
";
    const auto global_start = std::chrono::high_resolution_clock::now();

    {
        // std::jthread автоматично очікує завершення (join) при виході з області видимості
        std::jthread t0(cache_thrashing_worker, cpu0, std::span{buffer0}, ITERATIONS, std::ref(time0));
        std::jthread t1(cache_thrashing_worker, cpu1, std::span{buffer1}, ITERATIONS, std::ref(time1));
    }

    const auto global_end = std::chrono::high_resolution_clock::now();
    const double total_time = std::chrono::duration<double, std::milli>(global_end - global_start).count();

    std::cout << "Нитка 0 (CPU " << cpu0 << "): " << time0 << " мс
";
    std::cout << "Нитка 1 (CPU " << cpu1 << "): " << time1 << " мс
";
    std::cout << "Загальний час виконання: " << total_time << " мс
";

    return 0;
}

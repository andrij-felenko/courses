#include <iostream>
#include <vector>
#include <thread>
#include <numeric>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <new>

// Розмір кеш-лінії більшості сучасних процесорів x86/ARM
constexpr size_t CACHE_LINE_SIZE = 64;
constexpr size_t ARRAY_SIZE = 32 * 1024 * 1024; // 32 млн елементів
constexpr int REPEAT_COUNT = 4;

// Структура результату потоку з апаратним вирівнюванням проти false sharing
struct alignas(CACHE_LINE_SIZE) ThreadResult {
    double local_sum{0.0};
};

// Паралельне обчислювальне навантаження над відрізком масиву
void worker_task(double* data, size_t start_idx, size_t end_idx, ThreadResult& result) {
    double sum = 0.0;
    for (size_t i = start_idx; i < end_idx; ++i) {
        double v = data[i];
        for (int r = 0; r < REPEAT_COUNT; ++r) {
            v = std::sin(v) * std::cos(v) + std::sqrt(std::abs(v) + 1.0);
        }
        data[i] = v;
        sum += v;
    }
    result.local_sum = sum;
}

// Послідовна фаза редукції (виконується в один потік)
double serial_reduction(const double* data, size_t size, double partial_sum) {
    double acc = partial_sum;
    for (size_t i = 0; i < size; i += 64) {
        acc += std::log(std::abs(data[i]) + 1.0);
    }
    return acc;
}

// Запуск тесту з автоматичним керуванням життєвим циклом потоків (RAII)
double run_experiment(double* data, size_t size, size_t num_threads) {
    std::vector<ThreadResult> results(num_threads);
    std::vector<std::thread> workers;
    workers.reserve(num_threads);

    const size_t chunk_size = size / num_threads;
    const auto t_start = std::chrono::steady_clock::now();

    // 1. Паралельна фаза
    for (size_t i = 0; i < num_threads; ++i) {
        size_t start_idx = i * chunk_size;
        size_t end_idx = (i == num_threads - 1) ? size : start_idx + chunk_size;
        workers.emplace_back(worker_task, data, start_idx, end_idx, std::ref(results[i]));
    }

    // Бар'єрне очікування завершення (Join)
    for (auto& w : workers) {
        if (w.joinable()) {
            w.join();
        }
    }

    double parallel_sum = 0.0;
    for (const auto& res : results) {
        parallel_sum += res.local_sum;
    }

    // 2. Послідовна фаза
    [[maybe_unused]] volatile double final_result = serial_reduction(data, size, parallel_sum);

    const auto t_end = std::chrono::steady_clock::now();
    return std::chrono::duration<double>(t_end - t_start).count();
}

int main() {
    std::cout << "=== Бенчмарк закону Амдала (Modern C++ / std::thread) ===\n";
    std::cout << "Розмір масиву: " << ARRAY_SIZE << " елементів ("
              << (ARRAY_SIZE * sizeof(double)) / (1024.0 * 1024.0) << " МБ)\n\n";

    std::vector<double> data(ARRAY_SIZE);
    auto reset_data = [&data]() {
        for (size_t i = 0; i < data.size(); ++i) {
            data[i] = static_cast<double>(i % 1000) * 0.001 + 0.1;
        }
    };

    reset_data();
    const std::vector<size_t> test_threads = {1, 2, 4, 8, 16};

    std::cout << std::left
              << std::setw(8)  << "Потоки"
              << std::setw(12) << "Час (с)"
              << std::setw(14) << "Speedup S(N)"
              << std::setw(16) << "Efficiency E(N)"
              << std::setw(16) << "Karp-Flatt (e)" << "\n";
    std::cout << std::string(66, '-') << "\n";

    double t1 = run_experiment(data.data(), data.size(), 1);
    std::cout << std::left
              << std::setw(8)  << 1
              << std::setw(12) << std::fixed << std::setprecision(4) << t1
              << std::setw(14) << std::fixed << std::setprecision(2) << 1.0
              << std::setw(16) << std::fixed << std::setprecision(2) << 1.0
              << std::setw(16) << "—" << "\n";

    for (size_t idx = 1; idx < test_threads.size(); ++idx) {
        size_t n = test_threads[idx];
        reset_data();

        double tn = run_experiment(data.data(), data.size(), n);
        double speedup = t1 / tn;
        double efficiency = speedup / static_cast<double>(n);
        double e_metric = (1.0 / speedup - 1.0 / static_cast<double>(n)) / (1.0 - 1.0 / static_cast<double>(n));

        std::cout << std::left
                  << std::setw(8)  << n
                  << std::setw(12) << std::fixed << std::setprecision(4) << tn
                  << std::setw(14) << std::fixed << std::setprecision(2) << speedup
                  << std::setw(16) << std::fixed << std::setprecision(2) << efficiency
                  << std::setw(16) << std::fixed << std::setprecision(4) << e_metric << "\n";
    }

    return 0;
}

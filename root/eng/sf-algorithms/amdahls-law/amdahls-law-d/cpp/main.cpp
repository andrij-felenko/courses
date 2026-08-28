#include <iostream>
#include <vector>
#include <thread>
#include <cmath>
#include <numeric>
#include <span>

constexpr size_t N = 10'000'000;
constexpr size_t NUM_THREADS = 4;

struct WorkerTask {
    double partial_sum{0.0};
};

void parallel_worker(std::span<double> chunk, WorkerTask& task) {
    double sum = 0.0;
    // Паралельна фаза: важкі математичні перетворення
    for (auto& val : chunk) {
        val = std::sqrt(val) * 1.5;
        sum += val;
    }
    task.partial_sum = sum;
}

int main() {
    std::vector<double> array(N);
    std::iota(array.begin(), array.end(), 1.0);

    std::vector<std::thread> workers;
    std::vector<WorkerTask> tasks(NUM_THREADS);
    const size_t chunk_size = N / NUM_THREADS;

    // 1. Паралельна фаза Tp
    workers.reserve(NUM_THREADS);
    for (size_t i = 0; i < NUM_THREADS; ++i) {
        size_t start = i * chunk_size;
        size_t count = (i == NUM_THREADS - 1) ? (N - start) : chunk_size;
        workers.emplace_back(parallel_worker, std::span<double>(&array[start], count), std::ref(tasks[i]));
    }

    double total_sum = 0.0;
    for (size_t i = 0; i < NUM_THREADS; ++i) {
        if (workers[i].joinable()) {
            workers[i].join();
        }
        total_sum += tasks[i].partial_sum;
    }

    // 2. Послідовна фаза Ts: фінальна агрегація та верифікація
    double serial_check = 0.0;
    for (size_t i = 0; i < N; i += 100) {
        serial_check += std::log(array[i]);
    }

    std::cout << "Результат: sum = " << total_sum << ", check = " << serial_check << "\n";
    return 0;
}

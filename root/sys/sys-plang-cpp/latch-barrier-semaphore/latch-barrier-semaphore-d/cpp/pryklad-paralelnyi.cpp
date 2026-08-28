#include <iostream>
#include <barrier>
#include <vector>
#include <thread>
#include <span>
#include <numeric>

void run_simulation() {
    constexpr int num_threads = 4;
    constexpr int num_steps = 3;

    std::vector<float> buffer_a(1024, 1.0f);
    std::vector<float> buffer_b(1024, 0.0f);
    std::vector<float>* current_in = &buffer_a;
    std::vector<float>* current_out = &buffer_b;

    int current_step = 0;

    // Completion callback: викликається один раз у кінці кожної фази
    auto on_phase_complete = [&]() noexcept {
        std::swap(current_in, current_out);
        ++current_step;
        std::cout << "[Бар'єр] Фаза " << current_step << " завершена. Буфери обміняно.\n";
    };

    std::barrier sync_point(num_threads, on_phase_complete);
    std::vector<std::jthread> workers;
    workers.reserve(num_threads);

    for (int id = 0; id < num_threads; ++id) {
        workers.emplace_back([id, &sync_point, &current_in, &current_out, num_steps]() {
            for (int step = 0; step < num_steps; ++step) {
                // 1. Обчислювальна частина для потоку id
                const size_t chunk_size = 1024 / 4;
                const size_t start = id * chunk_size;
                const size_t end = start + chunk_size;

                for (size_t i = start; i < end; ++i) {
                    (*current_out)[i] = (*current_in)[i] * 0.95f;
                }

                // 2. Очікування решти потоків та виконання swap у callback
                sync_point.arrive_and_wait();
            }
        });
    }
}

int main() {
    run_simulation();
    return 0;
}

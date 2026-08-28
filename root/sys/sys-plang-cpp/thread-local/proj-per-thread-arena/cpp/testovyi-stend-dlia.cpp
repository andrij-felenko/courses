#include <chrono>
#include <thread>
#include <vector>
#include <mutex>
#include <iostream>

constexpr std::size_t TOTAL_OPS = 10'000'000;
constexpr std::size_t NUM_THREADS = 16;
constexpr std::size_t OPS_PER_THREAD = TOTAL_OPS / NUM_THREADS;

struct Payload {
    uint64_t data[8]; // 64 байти
};

void bench_global_new() {
    std::vector<std::jthread> threads;
    auto start = std::chrono::high_resolution_clock::now();

    for (std::size_t t = 0; t < NUM_THREADS; ++t) {
        threads.emplace_back([]() {
            for (std::size_t i = 0; i < OPS_PER_THREAD; ++i) {
                auto* p = new Payload();
                p->data[0] = i;
                delete p;
            }
        });
    }
    threads.clear(); // Очікування завершення всіх потоків

    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "Глобальний new: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() 
              << " ms\n";
}

void bench_thread_local_arena() {
    std::vector<std::jthread> threads;
    auto start = std::chrono::high_resolution_clock::now();

    for (std::size_t t = 0; t < NUM_THREADS; ++t) {
        threads.emplace_back([]() {
            auto& arena = g_per_thread_arena;
            for (std::size_t i = 0; i < OPS_PER_THREAD; ++i) {
                auto* p = arena.create<Payload>();
                p->data[0] = i;
                if ((i & 0xFF) == 0) {
                    arena.reset(); // Скидання кожні 256 аллокацій
                }
            }
            arena.reset();
        });
    }
    threads.clear();

    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "thread_local арена: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() 
              << " ms\n";
}

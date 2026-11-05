#include <iostream>
#include <atomic>
#include <new>

// Погано: атомарні лічильники ділять один кеш-рядок
struct BadState {
    std::atomic<uint64_t> thread1_count{0};
    std::atomic<uint64_t> thread2_count{0};
};

// Оптимально: ізоляція змінних за допомогою стандартної константи вирівнювання
struct GoodState {
    alignas(std::hardware_destructive_interference_size) std::atomic<uint64_t> thread1_count{0};
    alignas(std::hardware_destructive_interference_size) std::atomic<uint64_t> thread2_count{0};
};

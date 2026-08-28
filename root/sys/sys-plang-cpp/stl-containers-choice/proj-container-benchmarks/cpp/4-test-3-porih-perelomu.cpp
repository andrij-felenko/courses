// C++20: Порівняння вставки в середину std::vector та std::list
#include <iostream>
#include <vector>
#include <list>
#include <chrono>

void bench_middle_insert(size_t container_size) {
    std::vector<int32_t> vec(container_size, 42);
    std::list<int32_t> lst(container_size, 42);

    constexpr size_t INSERTS = 1000;

    // Вставка у вектор
    auto t1 = std::chrono::high_resolution_clock::now();
    for (size_t i = 0; i < INSERTS; ++i) {
        auto it = vec.begin() + vec.size() / 2;
        vec.insert(it, 100);
    }
    auto t2 = std::chrono::high_resolution_clock::now();

    // Вставка у список (включаючи час знаходження середини за O(N/2))
    for (size_t i = 0; i < INSERTS; ++i) {
        auto it = lst.begin();
        std::advance(it, lst.size() / 2);
        lst.insert(it, 100);
    }
    auto t3 = std::chrono::high_resolution_clock::now();

    double ms_vec = std::chrono::duration<double, std::milli>(t2 - t1).count();
    double ms_lst = std::chrono::duration<double, std::milli>(t3 - t2).count();

    std::cout << "Розмір N=" << container_size 
              << " | Vector insert: " << ms_vec << " ms"
              << " | List insert: " << ms_lst << " ms\n";
}

int main() {
    bench_middle_insert(100);
    bench_middle_insert(1'000);
    bench_middle_insert(10'000);
    bench_middle_insert(100'000);
}

#include <iostream>
#include <list>
#include <memory_resource>
#include <chrono>

int main() {
    constexpr size_t N = 1'000'000;
    
    // Попередньо виділений буфер на 32 МБ
    std::vector<std::byte> buffer(32 * 1024 * 1024);
    std::pmr::monotonic_buffer_resource pool(buffer.data(), buffer.size());

    auto t1 = std::chrono::high_resolution_clock::now();
    
    // Список, що використовує арений алокатор пам'яті
    std::pmr::list<int32_t> pmr_lst(&pool);
    for (size_t i = 0; i < N; ++i) {
        pmr_lst.push_back(static_cast<int32_t>(i));
    }
    
    auto t2 = std::chrono::high_resolution_clock::now();
    
    double ms = std::chrono::duration<double, std::milli>(t2 - t1).count();
    std::cout << "Створення 1,000,000 вузлів std::pmr::list у арені: " << ms << " мс\n";
}

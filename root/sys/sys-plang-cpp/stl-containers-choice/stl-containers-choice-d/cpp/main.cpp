#include <memory_resource>
#include <vector>
#include <string>

void pmr_example() {
    // Виділяємо арену на 64 КіБ прямо на стеку
    std::array<std::byte, 65536> stack_buffer;
    std::pmr::monotonic_buffer_resource pool(stack_buffer.data(), stack_buffer.size());

    // Вектор використовує арений алокатор: ЖОДНОГО виклику malloc!
    std::pmr::vector<std::pmr::string> vec(&pool);
    vec.push_back("Hello, PMR Arena Allocation!");
}

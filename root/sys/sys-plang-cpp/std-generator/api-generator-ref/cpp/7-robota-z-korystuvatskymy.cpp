#include <generator>
#include <memory_resource>
#include <iostream>

// Корутинна функція з користувацьким PMR розподілювачем
std::generator<int, void, std::pmr::polymorphic_allocator<char>>
custom_allocated_sequence(std::allocator_arg_t, std::pmr::polymorphic_allocator<char> alloc, int count) {
    for (int i = 0; i < count; ++i) {
        co_yield i;
    }
}

int main() {
    // Створюємо логічну арену пам'яті на стеку
    char buffer[1024];
    std::pmr::monotonic_buffer_resource pool(buffer, sizeof(buffer));
    std::pmr::polymorphic_allocator<char> alloc(&pool);

    // Передаємо розподілювач першим аргументом через std::allocator_arg
    auto gen = custom_allocated_sequence(std::allocator_arg, alloc, 5);

    for (int v : gen) {
        std::cout << v << " "; // Виділення кадру відбувається в буфері 'buffer'
    }
}

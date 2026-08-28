#include <future>
#include <memory_resource>
#include <iostream>

void pmr_allocator_example() {
    // Буфер на стеку для уникнення викликів new у купі
    std::array<std::byte, 1024> buffer;
    std::pmr::monotonic_buffer_resource pool(buffer.data(), buffer.size());
    std::pmr::polymorphic_allocator<int> alloc(&pool);

    // Конструюємо promise з використанням PMR-алокатора
    std::promise<int> p(std::allocator_arg, alloc);
    std::future<int> f = p.get_future();

    p.set_value(42);
    std::cout << "Значення з PMR promise: " << f.get() << std::endl;
}

#include <memory_resource>
#include <vector>
#include <array>

// Використання статичного буфера на стеку без викликів глобального malloc:
std::array<std::byte, 1024> stack_buffer;
std::pmr::monotonic_buffer_resource arena(stack_buffer.data(), stack_buffer.size());

// Тип std::pmr::vector<int> єдиний для будь-яких стратегій виділення пам'яті:
std::pmr::vector<int> numbers(&arena);
numbers.push_back(10);
numbers.push_back(20);

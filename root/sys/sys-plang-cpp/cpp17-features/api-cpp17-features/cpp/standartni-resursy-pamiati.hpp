#include <memory_resource>
#include <vector>
#include <array>

// Використання монотонної арени на стеку для вкладених контейнерів
std::array<std::byte, 4096> stack_arena;
std::pmr::monotonic_buffer_resource pool(stack_arena.data(), stack_arena.size());

std::pmr::vector<std::pmr::string> words(&pool);
words.emplace_back("high-performance");
words.emplace_back("stack-allocated"); // Пам'ять для рядка та вектора береться зі stack_arena

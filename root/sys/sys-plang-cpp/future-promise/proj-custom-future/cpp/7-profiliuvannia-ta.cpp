#include <new>

template <typename T>
struct alignas(std::hardware_destructive_interference_size) shared_state_optimized {
    std::mutex mtx;
    std::condition_variable cv;
    
    // Вирівнюємо прапор на окрему кеш-лінію
    alignas(std::hardware_destructive_interference_size) bool ready = false;
    
    std::variant<std::monostate, T, std::exception_ptr> storage;
};

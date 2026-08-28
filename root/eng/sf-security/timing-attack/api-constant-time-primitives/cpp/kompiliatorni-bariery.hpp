#include <concepts>

namespace ct {

// Шаблонна функція приховування значення від компілятора у C++
template <typename T>
inline void hide_value(T& var) noexcept {
    asm volatile("" : "+r"(var) : : "memory");
}

// Повний бар'єр пам'яті
inline void memory_barrier() noexcept {
    asm volatile("" : : "memory");
}

} // namespace ct

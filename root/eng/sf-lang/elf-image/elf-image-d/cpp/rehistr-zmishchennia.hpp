#include <cstdint>

namespace system {

inline volatile auto* const ScbVtor = reinterpret_cast<volatile std::uint32_t*>(0xE000ED08);
extern "C" extern std::uint32_t _isr_vector_start;

void relocate_vector_table_cpp() noexcept {
    #if defined(__arm__) || defined(__thumb__)
    asm volatile("cpsid i" ::: "memory"); // Вимкнення переривань
    #endif

    *ScbVtor = reinterpret_cast<std::uintptr_t>(&_isr_vector_start);

    #if defined(__arm__) || defined(__thumb__)
    asm volatile("dsb 0xF\nisb 0xF" ::: "memory");
    asm volatile("cpsie i" ::: "memory"); // Увімкнення переривань
    #endif
}

} // namespace system

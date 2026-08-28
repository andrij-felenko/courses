#ifndef HARDENED_PRIMITIVES_HPP
#define HARDENED_PRIMITIVES_HPP

#include <cstdint>
#include <concepts>
#include <span>

namespace security {

enum class Bool : uint32_t {
    True    = 0x5555AAAAU,
    False   = 0xAAAA5555U,
    Invalid = 0x00000000U,
    Fault   = 0xFFFFFFFFU
};

enum class Status : uint32_t {
    Ok      = 0x3C3C5A5AU,
    Error   = 0xC3C3A5A5U,
    Fault   = 0xFFFFFFFFU
};

/**
 * @brief Бар'єр пам'яті для запобігання оптимізаціям мертвого коду (Dead Code Elimination).
 */
inline void memory_barrier() noexcept {
    asm volatile("" ::: "memory");
}

/**
 * @brief Шаблонне безпечне порівняння скалярних цілочисельних типів.
 */
template <std::integral T>
[[nodiscard]] inline Bool safe_compare_equal(T a, T b) noexcept {
    memory_barrier();
    const auto ua = static_cast<uint32_t>(a);
    const auto ub = static_cast<uint32_t>(b);
    const auto diff = ua ^ ub;
    memory_barrier();
    
    if (diff == 0U) {
        memory_barrier();
        if ((ua ^ ~ub) == 0xFFFFFFFFU) {
            return Bool::True;
        }
    }
    return Bool::False;
}

/**
 * @brief Клас захисту графа виконання програми (Flow Integrity Guard).
 */
class ExecutionGuard {
public:
    constexpr explicit ExecutionGuard(uint32_t seed) noexcept 
        : accumulated_token_(seed), initial_seed_(seed) {}

    void record_step(uint32_t step_signature) noexcept {
        memory_barrier();
        accumulated_token_ ^= step_signature;
        memory_barrier();
    }

    [[nodiscard]] bool verify_path(uint32_t expected_final_mask) const noexcept {
        memory_barrier();
        const uint32_t expected = initial_seed_ ^ expected_final_mask;
        const uint32_t current = accumulated_token_;
        memory_barrier();
        return (current == expected) && ((current ^ ~expected) == 0xFFFFFFFFU);
    }

private:
    volatile uint32_t accumulated_token_;
    uint32_t initial_seed_;
};

[[noreturn]] void panic_lockout() noexcept;

} // namespace security

#endif /* HARDENED_PRIMITIVES_HPP */

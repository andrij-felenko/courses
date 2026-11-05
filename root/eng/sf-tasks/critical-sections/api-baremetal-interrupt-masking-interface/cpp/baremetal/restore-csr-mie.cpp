#include <cstdint>
#include <atomic>

// Оболочка RAII для апаратного маскування переривань
class [[nodiscard]] HardwareCriticalSection {
public:
    HardwareCriticalSection() noexcept {
#if defined(__ARM_ARCH)
        m_saved_mask = __get_PRIMASK();
        asm volatile ("cpsid i" ::: "memory");
        asm volatile ("dsb\nisb" ::: "memory");
#elif defined(__riscv)
        m_saved_mask = clear_csr_mie();
        asm volatile ("fence" ::: "memory");
#endif
    }

    ~HardwareCriticalSection() noexcept {
#if defined(__ARM_ARCH)
        asm volatile ("dsb" ::: "memory");
        __set_PRIMASK(m_saved_mask);
        asm volatile ("isb" ::: "memory");
#elif defined(__riscv)
        asm volatile ("fence" ::: "memory");
        restore_csr_mie(m_saved_mask);
#endif
    }

    // Видалення конструкторів копіювання та переміщення
    HardwareCriticalSection(const HardwareCriticalSection&) = delete;
    HardwareCriticalSection& operator=(const HardwareCriticalSection&) = delete;
    HardwareCriticalSection(HardwareCriticalSection&&) = delete;
    HardwareCriticalSection& operator=(HardwareCriticalSection&&) = delete;

private:
    uint32_t m_saved_mask{0};

#if defined(__riscv)
    static inline uint32_t clear_csr_mie() noexcept {
        uint32_t res;
        asm volatile ("csrrci %0, mstatus, 8" : "=r"(res) :: "memory");
        return res;
    }

    static inline void restore_csr_mie(uint32_t mask) noexcept {
        if (mask & 8) {
            asm volatile ("csrrs x0, mstatus, 8" ::: "memory");
        }
    }
#endif
};

// Приклад використання C++ оболонки для захисту лічильника системних подій
void increment_system_counter(volatile uint64_t &counter) {
    HardwareCriticalSection guard;
    counter++; // Атомарне інкрементування 64-бітного значення на 32-бітній архітектурі
}

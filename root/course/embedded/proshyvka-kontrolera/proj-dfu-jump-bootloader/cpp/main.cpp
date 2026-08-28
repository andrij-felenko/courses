#include <cstdint>
#include <span>
#include <concepts>

namespace fc::boot {

inline constexpr std::uintptr_t sram_begin = 0x20000000U;
inline constexpr std::uintptr_t sram_end   = 0x20080000U;

struct ArmVectorTable {
    std::uint32_t initial_msp;
    std::uint32_t reset_handler;
};

class CortexDeinitializer {
public:
    CortexDeinitializer() noexcept {
        disable_interrupts();
        stop_systick();
        disable_caches();
        clear_nvic();
        reset_clocks();
        memory_barrier();
    }

    ~CortexDeinitializer() = default;
    CortexDeinitializer(const CortexDeinitializer&) = delete;
    CortexDeinitializer& operator=(const CortexDeinitializer&) = delete;

private:
    static void disable_interrupts() noexcept {
        asm volatile("cpsid i" ::: "memory");
    }

    static void memory_barrier() noexcept {
        asm volatile("dsb\n\tisb" ::: "memory");
    }

    static void stop_systick() noexcept {
        auto* const systick_ctrl = reinterpret_cast<volatile std::uint32_t*>(0xE000E010U);
        auto* const systick_load = reinterpret_cast<volatile std::uint32_t*>(0xE000E014U);
        auto* const systick_val  = reinterpret_cast<volatile std::uint32_t*>(0xE000E018U);

        *systick_ctrl = 0U;
        *systick_load = 0U;
        *systick_val  = 0U;
    }

    static void disable_caches() noexcept {
        auto* const scb_ccr = reinterpret_cast<volatile std::uint32_t*>(0xE000ED14U);
        constexpr std::uint32_t dcache_mask = (1U << 16);
        constexpr std::uint32_t icache_mask = (1U << 17);

        *scb_ccr &= ~(dcache_mask | icache_mask);
    }

    static void clear_nvic() noexcept {
        auto* const icer = reinterpret_cast<volatile std::uint32_t*>(0xE000E180U);
        auto* const icpr = reinterpret_cast<volatile std::uint32_t*>(0xE000E280U);

        for (std::size_t i = 0; i < 8; ++i) {
            icer[i] = 0xFFFFFFFFU;
            icpr[i] = 0xFFFFFFFFU;
        }
    }

    static void reset_clocks() noexcept {
        auto* const rcc_cr   = reinterpret_cast<volatile std::uint32_t*>(0x40023800U);
        auto* const rcc_cfgr = reinterpret_cast<volatile std::uint32_t*>(0x40023808U);

        *rcc_cr |= 0x00000001U; // Увімкнення внутрішнього HSI
        while (!(*rcc_cr & 0x00000002U)) {
            // Очікування стабілізації тактування
        }
        *rcc_cfgr = 0x00000000U;
        *rcc_cr &= 0xFEF6FFFFU; // Вимкнення PLL, HSE
    }
};

[[nodiscard]] constexpr bool is_valid_stack_pointer(std::uint32_t msp) noexcept {
    return (msp >= sram_begin) && (msp <= sram_end);
}

[[nodiscard]] constexpr bool is_valid_thumb_address(std::uint32_t addr) noexcept {
    return (addr & 0x00000001U) == 1U;
}

[[noreturn]] void execute_jump(std::uintptr_t target_vector_addr) noexcept {
    const auto* const vectors = reinterpret_cast<const ArmVectorTable*>(target_vector_addr);

    if (!is_valid_stack_pointer(vectors->initial_msp) || 
        !is_valid_thumb_address(vectors->reset_handler)) {
        while (true) {
            // Аварійна пастка: хибний вектор, передачу керування заблоковано
        }
    }

    {
        // RAII деініціалізація ядра, тактування та кешів
        const CortexDeinitializer deinit_guard;

        auto* const scb_vtor = reinterpret_cast<volatile std::uint32_t*>(0xE000ED08U);
        *scb_vtor = static_cast<std::uint32_t>(target_vector_addr);

        asm volatile("dsb\n\tisb" ::: "memory");
        asm volatile("msr msp, %0" :: "r"(vectors->initial_msp) : "memory");
    }

    using EntryPoint = void (*)() noexcept;
    auto entry = reinterpret_cast<EntryPoint>(vectors->reset_handler);
    entry();

    while (true) {}
}

} // namespace fc::boot

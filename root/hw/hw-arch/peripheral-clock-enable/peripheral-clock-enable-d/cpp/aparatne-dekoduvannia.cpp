#include <cstdint>
#include <concepts>
#include <span>

struct exception_stack_frame {
    std::uint32_t r0;
    std::uint32_t r1;
    std::uint32_t r2;
    std::uint32_t r3;
    std::uint32_t r12;
    std::uint32_t lr;
    std::uint32_t pc;
    std::uint32_t xpsr;
};

struct fault_diagnostics {
    std::uint32_t cfsr_value;
    std::uint8_t  bfsr_value;
    std::uint32_t fault_address;
    bool          is_precise;
    bool          is_peripheral_access;
};

class bus_fault_inspector {
public:
    static consteval std::uintptr_t scb_cfsr_addr() noexcept { return 0xE000ED28; }
    static consteval std::uintptr_t scb_bfar_addr() noexcept { return 0xE000ED38; }

    [[nodiscard]] static fault_diagnostics analyze(const exception_stack_frame& frame) noexcept {
        const auto cfsr = *reinterpret_cast<const volatile std::uint32_t*>(scb_cfsr_addr());
        const auto bfsr = static_cast<std::uint8_t>((cfsr >> 8) & 0xFF);
        const auto bfar = *reinterpret_cast<const volatile std::uint32_t*>(scb_bfar_addr());

        const bool has_address = (bfsr & (1U << 7)) != 0;
        const auto addr = has_address ? bfar : 0x00000000U;
        const bool is_periph = (addr >= 0x40000000U && addr < 0x60000000U);

        return fault_diagnostics{
            .cfsr_value = cfsr,
            .bfsr_value = bfsr,
            .fault_address = addr,
            .is_precise = (bfsr & (1U << 1)) != 0,
            .is_peripheral_access = is_periph
        };
    }
};

extern "C" void bus_fault_analyzer_cpp(const exception_stack_frame* frame) {
    if (frame != nullptr) {
        [[maybe_unused]] const auto diag = bus_fault_inspector::analyze(*frame);
    }
    while (true) {
        asm volatile("BKPT #0");
    }
}

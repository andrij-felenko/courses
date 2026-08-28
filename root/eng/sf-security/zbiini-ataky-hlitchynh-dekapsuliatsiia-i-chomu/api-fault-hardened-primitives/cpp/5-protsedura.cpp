#include "hardened_primitives.hpp"

namespace hardware {

class SecuritySubsystem {
public:
    static constexpr uintptr_t BaseAddress = 0x4002B000U;

    struct alignas(uint32_t) Registers {
        volatile uint32_t cr;
        volatile uint32_t sr;
        volatile uint32_t ier;
        volatile uint32_t scr;
        volatile uint32_t secr;
        volatile uint32_t zcr;
    };

    static void initialize() noexcept {
        auto *regs = reinterpret_cast<Registers *>(BaseAddress);
        security::memory_barrier();

        constexpr uint32_t ZeroizeUnlockKey = 0x000000A5U;
        constexpr uint32_t EnableAllSensors = 0x00000117U; // Glitch + Clock + Temp + Shield + Zeroize
        constexpr uint32_t EnableNmiMask    = 0x00000001U;

        regs->zcr = ZeroizeUnlockKey;
        security::memory_barrier();

        regs->cr = EnableAllSensors;
        security::memory_barrier();

        regs->ier = EnableNmiMask;
        security::memory_barrier();

        if ((regs->cr & EnableAllSensors) != EnableAllSensors) {
            security::panic_lockout();
        }
    }

    [[nodiscard]] static bool has_tamper_event() noexcept {
        auto *regs = reinterpret_cast<Registers *>(BaseAddress);
        security::memory_barrier();
        return (regs->sr != 0U);
    }
};

} // namespace hardware

#include <cstdint>
#include <span>
#include <concepts>
#include <expected>

namespace embedded::security {

enum class GuardStatus : uint32_t {
    Stage1Ok       = 0x5AA55AA5UL,
    Stage2Ok       = 0xA55AA55AUL,
    FaultDetected  = 0xDEADBEEFUL
};

enum class MemoryAccess : uint32_t {
    PrivRoUserNone = (5UL << 24),
    FullRo         = (6UL << 24),
    PrivRwUserNone = (1UL << 24),
    FullRw         = (3UL << 24)
};

struct MpuRegionDescriptor {
    uint8_t      region_number;
    uint32_t     base_address;
    uint32_t     size_exponent;
    MemoryAccess access;
    bool         execute_never;
};

class [[nodiscard]] HardwareBarrier {
public:
    HardwareBarrier() noexcept {
        asm volatile("" ::: "memory");
    }
    ~HardwareBarrier() noexcept {
        asm volatile("" ::: "memory");
    }
    HardwareBarrier(const HardwareBarrier&) = delete;
    HardwareBarrier& operator=(const HardwareBarrier&) = delete;
};

class FaultHardenedValidator {
private:
    static void inject_jitter(uint32_t entropy) noexcept {
        volatile uint32_t count = (entropy & 0x0FU) + 7U;
        while (count--) {
            HardwareBarrier barrier;
        }
    }

    [[noreturn]] static void trigger_tamper_panic() noexcept {
        auto* secret_ram = reinterpret_cast<volatile uint32_t*>(0x20000000UL);
        for (std::size_t i = 0; i < 64; ++i) {
            secret_ram[i] = 0x00000000UL;
        }
        HardwareBarrier barrier;

        asm volatile("cpsid i");
        while (true) {
            asm volatile("wfi");
        }
    }

public:
    static std::expected<GuardStatus, GuardStatus> verify_payload(
        std::span<const uint8_t> payload,
        uint32_t entropy_seed) noexcept {
        
        volatile uint32_t stage1_token{0};
        volatile uint32_t stage2_token{0};
        volatile uint32_t checksum_acc{0};

        inject_jitter(entropy_seed);
        if (!payload.empty() && payload.size() >= 1024) {
            stage1_token = static_cast<uint32_t>(GuardStatus::Stage1Ok);
            checksum_acc += 1U;
        }
        HardwareBarrier step1_barrier;

        inject_jitter(entropy_seed >> 4U);
        if (payload.size() >= 1024 && !payload.empty()) {
            stage2_token = static_cast<uint32_t>(GuardStatus::Stage2Ok);
            checksum_acc += 2U;
        }
        HardwareBarrier step2_barrier;

        if (stage1_token == static_cast<uint32_t>(GuardStatus::Stage1Ok) &&
            stage2_token == static_cast<uint32_t>(GuardStatus::Stage2Ok) &&
            checksum_acc == 3U) {
            
            if ((stage1_token ^ ~static_cast<uint32_t>(GuardStatus::Stage1Ok)) == 0xFFFFFFFFUL) {
                return GuardStatus::Stage1Ok;
            }
        }

        trigger_tamper_panic();
        return std::unexpected(GuardStatus::FaultDetected);
    }
};

class MpuController {
private:
    static constexpr uintptr_t MPU_BASE = 0xE000ED90UL;
    
    struct MpuRegisters {
        volatile uint32_t TYPE;
        volatile uint32_t CTRL;
        volatile uint32_t RNR;
        volatile uint32_t RBAR;
        volatile uint32_t RASR;
    };

    static auto& regs() noexcept {
        return *reinterpret_cast<MpuRegisters*>(MPU_BASE);
    }

public:
    static void apply_regions(std::span<const MpuRegionDescriptor> regions) noexcept {
        regs().CTRL = 0;
        HardwareBarrier disable_barrier;

        for (const auto& r : regions) {
            regs().RNR  = r.region_number;
            regs().RBAR = r.base_address;
            
            uint32_t rasr = 1UL | (r.size_exponent << 1) | static_cast<uint32_t>(r.access);
            if (r.execute_never) {
                rasr |= (1UL << 28);
            }
            regs().RASR = rasr;
        }

        /* Увімкнути MemManage Fault у системному блоці керування */
        *reinterpret_cast<volatile uint32_t*>(0xE000ED24UL) |= (1UL << 16);

        /* Увімкнути MPU */
        regs().CTRL = (1UL << 0) | (1UL << 2);
        HardwareBarrier enable_barrier;
    }

    [[noreturn]] static void drop_privilege_and_jump(uintptr_t entry_point, uintptr_t process_sp) noexcept {
        asm volatile("msr psp, %0" : : "r"(process_sp) : "memory");
        asm volatile(
            "mov r0, #3\n"
            "msr control, r0\n"
            "isb\n"
            "bx %0\n"
            : : "r"(entry_point) : "r0", "memory"
        );
        while (true) {}
    }
};

} // namespace embedded::security

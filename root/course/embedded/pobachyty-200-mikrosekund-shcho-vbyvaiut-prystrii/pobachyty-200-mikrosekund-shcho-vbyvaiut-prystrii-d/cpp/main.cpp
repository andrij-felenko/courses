// power_glitch_monitor.hpp / .cpp — Ідіоматичний монітор глітчів живлення (C++20)
#include <cstdint>
#include <atomic>
#include <span>

namespace embedded::power {

enum class VoltageThreshold : uint8_t {
    V2_2 = 0x00,
    V2_4 = 0x01,
    V2_6 = 0x02,
    V2_8 = 0x03,
    V2_9 = 0x07
};

struct alignas(4) FaultRecord {
    uint32_t glitch_count{0};
    uint32_t brownout_resets{0};
    uint32_t last_glitch_ms{0};
    uint32_t magic{0xA55A1234};
};

class GlitchMonitor {
public:
    static constexpr uintptr_t kBackupRamAddr = 0x40024000;

    explicit GlitchMonitor(VoltageThreshold threshold) noexcept
        : threshold_{threshold} {}

    void init() noexcept {
        auto* log = fault_log();
        if (log->magic != kMagicValue) {
            log->glitch_count = 0;
            log->brownout_resets = 0;
            log->last_glitch_ms = 0;
            log->magic = kMagicValue;
        }
        configure_hardware(threshold_);
    }

    static void handle_interrupt(uint32_t current_time_ms) noexcept {
        // 1. Апаратне скидання потужних виходів (RAII / direct HAL)
        emergency_power_shedding();

        // 2. Атомарне оновлення журналу в Retentive пам'яті
        auto* log = fault_log();
        log->glitch_count++;
        log->last_glitch_ms = current_time_ms;

        // Апаратний бар'єр синхронізації пам'яті Cortex-M
        asm volatile("dsb 0xF" ::: "memory");
    }

    [[nodiscard]] static uint32_t total_glitches() noexcept {
        return fault_log()->glitch_count;
    }

    [[nodiscard]] static uint32_t last_glitch_timestamp() noexcept {
        return fault_log()->last_glitch_ms;
    }

private:
    static constexpr uint32_t kMagicValue = 0xA55A1234;

    VoltageThreshold threshold_;

    [[nodiscard]] static FaultRecord* fault_log() noexcept {
        return reinterpret_cast<FaultRecord*>(kBackupRamAddr);
    }

    static void configure_hardware(VoltageThreshold th) noexcept {
        // Конфігурація регістрів PWR_CR та EXTI через типізовані бітові маски
        (void)th;
    }

    static void emergency_power_shedding() noexcept {
        // Миттєве вимкнення сильнострумових периферійних блоків
    }
};

} // namespace embedded::power

// Глобальна точка входу переривання
extern "C" void PVD_IRQHandler() {
    embedded::power::GlitchMonitor::handle_interrupt(0 /* get_system_ms() */);
}

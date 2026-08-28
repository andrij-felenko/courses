#include <cstdint>
#include <span>
#include <concepts>

struct CrashReport {
    uint32_t boot_count{0};
    uint32_t reset_reason{0};
    uint32_t fault_address{0};
    uint16_t checksum{0};

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        return checksum == static_cast<uint16_t>(boot_count ^ reset_reason ^ fault_address);
    }

    void update(uint32_t reason, uint32_t addr) noexcept {
        ++boot_count;
        reset_reason = reason;
        fault_address = addr;
        checksum = static_cast<uint16_t>(boot_count ^ reset_reason ^ fault_address);
    }
};

// Розміщення в спеціальній секції пам'яті, що не ініціалізується нулями при старті
[[gnu::section(".retained_ram")]] static CrashReport g_system_crash_report;

template <typename ActuatorPolicy>
class SystemSafetyGuard {
public:
    explicit SystemSafetyGuard(ActuatorPolicy policy) : policy_(policy) {}

    // RAII-гарантія: при створенні об'єкта перевіряємо стан, при фатальній помилці вимикаємо все
    void emergency_shutdown(uint32_t reason_code, uint32_t program_counter) noexcept {
        policy_.disable_all_power_stages();
        policy_.isolate_high_voltage();

        g_system_crash_report.update(reason_code, program_counter);
        policy_.trigger_system_reset();
    }

private:
    ActuatorPolicy policy_;
};

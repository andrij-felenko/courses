#include <cstdint>
#include <array>
#include <expected>
#include <string_view>

namespace embedded::diagnostics {

inline constexpr size_t kMaxMonitoredTasks = 4;

struct SystemBudgetAudit {
    uint32_t flash_free_bytes{0};
    uint32_t ram_heap_free_bytes{0};
    std::array<uint32_t, kMaxMonitoredTasks> task_stack_min_bytes{};
    int16_t  core_temperature_c{0};   // Десяті долі градуса Цельсія (°C * 10)
    uint16_t vdd_millivolts{0};
    bool     ota_slot_available{false};
};

enum class BudgetFault : uint8_t {
    MemoryDepleted,
    ThermalLimitExceeded,
    VoltageSagCritical
};

[[nodiscard]] constexpr std::expected<void, BudgetFault> 
validate_budgets(const SystemBudgetAudit& audit) noexcept {
    // 1. Контроль просідання шини живлення
    if (audit.vdd_millivolts < 2900) {
        return std::unexpected(BudgetFault::VoltageSagCritical);
    }

    // 2. Контроль температури кремнієвого переходу
    if (audit.core_temperature_c > 850) {
        return std::unexpected(BudgetFault::ThermalLimitExceeded);
    }

    // 3. Контроль запасу динамічної пам'яті та слота OTA
    if (audit.ram_heap_free_bytes < 8192 || !audit.ota_slot_available) {
        return std::unexpected(BudgetFault::MemoryDepleted);
    }

    // 4. Аудит мінімального залишку стеків задач
    for (const auto stack_free : audit.task_stack_min_bytes) {
        if (stack_free < 256) {
            return std::unexpected(BudgetFault::MemoryDepleted);
        }
    }

    return {};
}

} // namespace embedded::diagnostics

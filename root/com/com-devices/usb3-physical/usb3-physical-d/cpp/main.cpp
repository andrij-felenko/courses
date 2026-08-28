#include <cstdint>
#include <string_view>
#include <iostream>
#include <format>

enum class LtssmState : uint8_t {
    U0            = 0, // Робочий активний стан передачі даних
    U1            = 1, // Енергозбереження (швидкий вихід)
    U2            = 2, // Енергозбереження (повільний вихід)
    U3            = 3, // Стан сну (Suspend)
    SsDisabled   = 4, // SuperSpeed вимкнено
    RxDetect     = 5, // Виявлення приймача через RC-заряд
    SsInactive   = 6, // Неактивний стан
    Polling       = 7, // Тренування лінії (LFPS + екземпляри TS1/TS2)
    Recovery      = 8, // Відновлення синхронізації
    HotReset     = 9, // Гаряче скидання
    Compliance    = 10,// Тестовий режим перевірки стандартів
    Loopback      = 11 // Режим зворотного замикання петлі
};

struct PortStatus {
    bool connected{false};
    bool enabled{false};
    LtssmState link_state{LtssmState::SsDisabled};
    uint8_t speed_id{0};

    [[nodiscard]] static constexpr PortStatus from_raw(uint32_t raw) noexcept {
        constexpr uint32_t mask_ccs   = 1U << 0;
        constexpr uint32_t mask_ped   = 1U << 1;
        constexpr uint32_t mask_pls   = 0xFU << 5;
        constexpr uint32_t mask_speed = 0xFU << 10;

        return PortStatus{
            .connected  = (raw & mask_ccs) != 0,
            .enabled    = (raw & mask_ped) != 0,
            .link_state = static_cast<LtssmState>((raw & mask_pls) >> 5),
            .speed_id   = static_cast<uint8_t>((raw & mask_speed) >> 10)
        };
    }

    [[nodiscard]] constexpr std::string_view state_name() const noexcept {
        switch (link_state) {
            case LtssmState::U0:        return "U0 (Active SuperSpeed)";
            case LtssmState::RxDetect:  return "Rx.Detect (Testing RC charge)";
            case LtssmState::Polling:   return "Polling (LFPS link training)";
            case LtssmState::Recovery:  return "Recovery (Resynchronizing)";
            case LtssmState::U3:        return "U3 (Suspended)";
            default:                    return "Other LTSSM State";
        }
    }
};

int main() {
    // Регістр PORTSC: CCS=1, PED=1, PLS=0 (U0), Speed=4 (SuperSpeed 5 Gbps)
    constexpr uint32_t sample_portsc = 0x00001023U;
    const auto status = PortStatus::from_raw(sample_portsc);

    std::cout << "SuperSpeed USB Physical Layer Diagnostics (C++20)\n";
    std::cout << std::format("  Physical Connection : {}\n", status.connected ? "Attached" : "Open");
    std::cout << std::format("  Port Enabled        : {}\n", status.enabled ? "Yes" : "No");
    std::cout << std::format("  LTSSM State         : {}\n", status.state_name());
    std::cout << std::format("  Speed Protocol ID   : {} (4 = 5Gbps, 5 = 10Gbps)\n", status.speed_id);

    return 0;
}

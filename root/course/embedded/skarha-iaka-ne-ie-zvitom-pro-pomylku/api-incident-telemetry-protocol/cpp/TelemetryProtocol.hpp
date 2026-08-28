/* TelemetryProtocol.hpp */
#pragma once
#include <cstdint>
#include <span>
#include <string_view>

namespace Telemetry {

inline constexpr std::uint32_t MagicTag = 0xDEADBEEFUL;
inline constexpr std::uint16_t ProtocolV1_0 = 0x0100U;

enum class FaultCategory : std::uint32_t {
    None              = 0x00000000UL,
    HardfaultPrecise  = 0x01010001UL,
    HardfaultImprec   = 0x01010002UL,
    MemManage         = 0x01020001UL,
    UsageDiv0         = 0x01030001UL,
    WdtTaskStall      = 0x02010001UL,
    WdtIsrFlood       = 0x02010002UL,
    PwrBrownout       = 0x03010001UL,
    PwrOvertemp       = 0x03020001UL,
    BusI2cStuck       = 0x04010001UL,
    BusSpiLock        = 0x04020001UL
};

[[nodiscard]] constexpr std::string_view getFaultCategoryName(FaultCategory category) noexcept {
    switch (category) {
        case FaultCategory::HardfaultPrecise: return "HardFault (Precise Data Access Violation)";
        case FaultCategory::HardfaultImprec:  return "HardFault (Imprecise Asynchronous Bus Error)";
        case FaultCategory::MemManage:        return "Memory Management Fault (MPU Violation)";
        case FaultCategory::UsageDiv0:        return "UsageFault (Divide by Zero / Undefined Op)";
        case FaultCategory::WdtTaskStall:     return "Watchdog Reset (RTOS Task Deadlock/Stall)";
        case FaultCategory::WdtIsrFlood:      return "Watchdog Reset (Interrupt Handler Lockup)";
        case FaultCategory::PwrBrownout:      return "Power Brown-out Reset (Supply Voltage Drop)";
        case FaultCategory::PwrOvertemp:      return "Thermal Shutdown (Over-temperature Protection)";
        case FaultCategory::BusI2cStuck:      return "Bus Lockup (I2C SDA Line Held Low by Sensor)";
        case FaultCategory::BusSpiLock:       return "Bus Lockup (SPI Slave Ready Timeout)";
        case FaultCategory::None:
        default:                              return "No Fault / Unknown Event";
    }
}

#pragma pack(push, 1)
struct IncidentFrame {
    std::uint32_t magic_tag{MagicTag};
    std::uint16_t protocol_version{ProtocolV1_0};
    std::uint16_t payload_length{sizeof(IncidentFrame) - 8};
    std::uint64_t device_uid{0};
    std::uint32_t boot_count{0};
    std::uint32_t uptime_seconds{0};
    std::uint32_t reset_flags_raw{0};
    FaultCategory fault_code{FaultCategory::None};
    std::uint32_t fault_pc{0};
    std::uint32_t fault_lr{0};
    std::uint32_t fault_cfsr{0};
    std::int16_t  v_bat_mv{0};
    std::int16_t  v_core_mv{0};
    std::int16_t  temp_die_c{0};
    std::int16_t  temp_pcb_c{0};
    std::uint16_t bus_err_i2c{0};
    std::uint16_t bus_err_spi{0};
    std::uint32_t task_active_id{0};
    std::uint32_t task_min_stack_words{0};
    std::uint32_t crc32{0};
};
#pragma pack(pop)

} // namespace Telemetry

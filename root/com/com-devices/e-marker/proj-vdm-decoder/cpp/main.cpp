#include <cstdint>
#include <span>
#include <expected>
#include <string_view>

namespace usbpd {

inline constexpr uint16_t SVID_STANDARD = 0xFF00U;

enum class ParseError {
    BufferTooShort,
    InvalidSvid,
    NotStructuredVdm,
    WrongCommand,
    NotAck,
    NotACable,
    InvalidCurrentField
};

enum class Speed : uint8_t {
    Usb2Only,
    Usb32Gen1,
    Usb32Gen2OrUsb4Gen2,
    Usb4Gen3,
    Usb4Gen4,
    Unknown
};

struct CableDescriptor {
    uint16_t vid{0};
    uint16_t pid{0};
    uint32_t xid{0};
    uint8_t  hw_version{0};
    uint8_t  fw_version{0};
    bool     is_active{false};
    bool     is_epr_capable{false};
    uint16_t max_voltage_mv{20000};
    uint16_t max_current_ma{3000};
    Speed    speed{Speed::Usb2Only};
    uint8_t  max_temperature_c{0};
    bool     has_thermal_sensor{false};

    [[nodiscard]] constexpr std::string_view speed_string() const noexcept {
        switch (speed) {
            case Speed::Usb2Only:             return "USB 2.0 (480 Mbps)";
            case Speed::Usb32Gen1:            return "USB 3.2 Gen1 (5 Gbps)";
            case Speed::Usb32Gen2OrUsb4Gen2:  return "USB 3.2 Gen2 / USB4 Gen2 (10 Gbps)";
            case Speed::Usb4Gen3:             return "USB4 Gen3 (40 Gbps)";
            case Speed::Usb4Gen4:             return "USB4 Gen4 (80/120 Gbps)";
            default:                          return "Unknown";
        }
    }
};

[[nodiscard]] constexpr std::expected<CableDescriptor, ParseError> decode_cable_identity(
    std::span<const uint32_t> vdo_buffer
) noexcept {
    if (vdo_buffer.size() < 5) {
        return std::unexpected(ParseError::BufferTooShort);
    }

    const uint32_t vdm_header = vdo_buffer[0];
    const auto svid = static_cast<uint16_t>(vdm_header >> 16);
    const auto vdm_type = static_cast<uint8_t>((vdm_header >> 15) & 0x01U);
    const auto cmd_type = static_cast<uint8_t>((vdm_header >> 6) & 0x03U);
    const auto cmd_code = static_cast<uint8_t>(vdm_header & 0x1FU);

    if (svid != SVID_STANDARD) {
        return std::unexpected(ParseError::InvalidSvid);
    }
    if (vdm_type != 1U) {
        return std::unexpected(ParseError::NotStructuredVdm);
    }
    if (cmd_code != 0x01U) {
        return std::unexpected(ParseError::WrongCommand);
    }
    if (cmd_type != 0x01U) {
        return std::unexpected(ParseError::NotAck);
    }

    const uint32_t id_header = vdo_buffer[1];
    const auto prod_type = static_cast<uint8_t>((id_header >> 27) & 0x07U);
    if (prod_type != 0x03U && prod_type != 0x04U) {
        return std::unexpected(ParseError::NotACable);
    }

    CableDescriptor desc{};
    desc.vid = static_cast<uint16_t>(id_header & 0xFFFFU);
    desc.is_active = (prod_type == 0x04U);
    desc.xid = vdo_buffer[2];

    const uint32_t prod_vdo = vdo_buffer[3];
    desc.pid = static_cast<uint16_t>(prod_vdo >> 16);

    const uint32_t cable_vdo1 = vdo_buffer[4];
    desc.hw_version = static_cast<uint8_t>((cable_vdo1 >> 28) & 0x0FU);
    desc.fw_version = static_cast<uint8_t>((cable_vdo1 >> 24) & 0x0FU);

    const auto volt_bits = static_cast<uint8_t>((cable_vdo1 >> 17) & 0x03U);
    switch (volt_bits) {
        case 0x00: desc.max_voltage_mv = 20000; break;
        case 0x01: desc.max_voltage_mv = 30000; break;
        case 0x02: desc.max_voltage_mv = 40000; break;
        case 0x03: desc.max_voltage_mv = 50000; break;
    }

    const auto curr_bits = static_cast<uint8_t>((cable_vdo1 >> 5) & 0x03U);
    if (curr_bits == 0x01) {
        desc.max_current_ma = 3000;
    } else if (curr_bits == 0x02) {
        desc.max_current_ma = 5000;
    } else {
        return std::unexpected(ParseError::InvalidCurrentField);
    }

    const auto speed_bits = static_cast<uint8_t>(cable_vdo1 & 0x07U);
    switch (speed_bits) {
        case 0x00: desc.speed = Speed::Usb2Only; break;
        case 0x01: desc.speed = Speed::Usb32Gen1; break;
        case 0x02: desc.speed = Speed::Usb32Gen2OrUsb4Gen2; break;
        case 0x03: desc.speed = Speed::Usb4Gen3; break;
        case 0x04: desc.speed = Speed::Usb4Gen4; break;
        default:   desc.speed = Speed::Unknown; break;
    }

    desc.is_epr_capable = (desc.max_voltage_mv >= 50000 && desc.max_current_ma == 5000);

    if (vdo_buffer.size() >= 6) {
        const uint32_t cable_vdo2 = vdo_buffer[5];
        desc.max_temperature_c = static_cast<uint8_t>((cable_vdo2 >> 24) & 0xFFU);
        const auto thermal_sensor = static_cast<uint8_t>((cable_vdo2 >> 12) & 0x0FU);
        desc.has_thermal_sensor = (thermal_sensor != 0);

        const auto epr_flag = static_cast<uint8_t>((cable_vdo2 >> 8) & 0x0FU);
        if (epr_flag == 0x01) {
            desc.is_epr_capable = true;
            desc.max_voltage_mv = 50000;
        }
    }

    return desc;
}

} // namespace usbpd

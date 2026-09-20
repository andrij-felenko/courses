#include <cstdint>
#include <array>
#include <cstring>

#pragma pack(push, 1)
struct TeachPendantFrame {
    static constexpr std::uint16_t PREAMBLE = 0x55AA;

    std::uint16_t preamble{PREAMBLE};
    std::uint8_t  frame_type{0x01};
    std::uint8_t  sequence_id{0};
    std::uint16_t payload_len{16};
    std::uint16_t safety_status{0};
    std::uint16_t keypad_mask{0};
    std::array<std::int16_t, 6> joystick_axes{};
    std::uint16_t crc16{0};

    [[nodiscard]] bool validate_crc() const {
        std::size_t crc_len = sizeof(TeachPendantFrame) - sizeof(std::uint16_t);
        auto calculated = calculate_crc16_modbus({reinterpret_cast<const std::uint8_t*>(this), crc_len});
        return calculated == crc16;
    }
};
#pragma pack(pop)

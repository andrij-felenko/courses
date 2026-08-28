#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <numeric>

class SmartServoPacketBuilder {
public:
    static constexpr uint8_t Header = 0xFF;
    static constexpr uint8_t InstWriteData = 0x03;
    static constexpr uint8_t RegGoalPosition = 0x2A;

    struct Packet {
        std::array<uint8_t, 16> data{};
        size_t size{0};

        [[nodiscard]] std::span<const uint8_t> bytes() const noexcept {
            return std::span<const uint8_t>(data.data(), size);
        }
    };

    [[nodiscard]] static constexpr Packet makePositionCommand(uint8_t id, uint16_t position, uint16_t speed) noexcept {
        Packet pkt{};
        pkt.data[0] = Header;
        pkt.data[1] = Header;
        pkt.data[2] = id;
        pkt.data[3] = 7; // Length: Inst(1) + Reg(1) + Pos(2) + Speed(2) + Checksum(1)
        pkt.data[4] = InstWriteData;
        pkt.data[5] = RegGoalPosition;
        pkt.data[6] = static_cast<uint8_t>(position & 0xFF);
        pkt.data[7] = static_cast<uint8_t>((position >> 8) & 0xFF);
        pkt.data[8] = static_cast<uint8_t>(speed & 0xFF);
        pkt.data[9] = static_cast<uint8_t>((speed >> 8) & 0xFF);

        uint32_t sum = 0;
        for (size_t i = 2; i <= 9; ++i) {
            sum += pkt.data[i];
        }
        pkt.data[10] = static_cast<uint8_t>(~sum & 0xFF);
        pkt.size = 11;
        return pkt;
    }
};

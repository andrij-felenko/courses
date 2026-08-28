#include <cstdint>
#include <array>
#include <span>

namespace dshot {

constexpr uint32_t TimerArr = 280;
constexpr uint32_t CcrBit0 = 93;
constexpr uint32_t CcrBit1 = 187;
constexpr size_t FrameSize = 17;

class DShotEncoder {
public:
    [[nodiscard]] static constexpr uint16_t makePacket(uint16_t throttle, bool tlmReq, bool bidir) noexcept {
        const uint16_t clamped = (throttle > 2047) ? 2047 : throttle;
        const uint16_t packet = (clamped << 1) | (tlmReq ? 1 : 0);

        uint16_t csum = 0;
        uint16_t temp = packet;
        for (int i = 0; i < 3; ++i) {
            csum ^= (temp & 0x0F);
            temp >>= 4;
        }

        csum = bidir ? ((~csum) & 0x0F) : (csum & 0x0F);
        return (packet << 4) | csum;
    }

    static void fillDmaBuffer(uint16_t packet, std::span<uint32_t, FrameSize> buffer) noexcept {
        for (size_t i = 0; i < 16; ++i) {
            buffer[i] = (packet & (1 << (15 - i))) ? CcrBit1 : CcrBit0;
        }
        buffer[16] = 0;
    }
};

} // namespace dshot

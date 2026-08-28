#include <cstdint>
#include <array>
#include <span>
#include <expected>

namespace drone::rc {

inline constexpr uint16_t kChannelMinUs    = 988U;
inline constexpr uint16_t kChannelMaxUs    = 2012U;
inline constexpr uint16_t kChannelCenterUs = 1500U;
inline constexpr size_t   kTotalChannels   = 16U;
inline constexpr size_t   kPayloadBytes    = 22U;

enum class ChannelMap : uint8_t {
    AETR = 0,
    TAER = 1,
    RETA = 2
};

enum class SwitchPosition : uint8_t {
    Low    = 0,
    Center = 1,
    High   = 2
};

struct AuxChannelState {
    uint16_t raw_us{kChannelCenterUs};
    SwitchPosition position{SwitchPosition::Low};
    bool valid{false};
};

class ChannelDecoder {
public:
    [[nodiscard]] static std::array<uint16_t, kTotalChannels> unpack11Bit(
        std::span<const uint8_t, kPayloadBytes> payload) noexcept {
        
        std::array<uint16_t, kTotalChannels> raw{};

        raw[0]  = static_cast<uint16_t>((payload[0]       | (payload[1] << 8))                      & 0x07FF);
        raw[1]  = static_cast<uint16_t>(((payload[1] >> 3) | (payload[2] << 5))                      & 0x07FF);
        raw[2]  = static_cast<uint16_t>(((payload[2] >> 6) | (payload[3] << 2) | (payload[4] << 10)) & 0x07FF);
        raw[3]  = static_cast<uint16_t>(((payload[4] >> 1) | (payload[5] << 7))                      & 0x07FF);
        raw[4]  = static_cast<uint16_t>(((payload[5] >> 4) | (payload[6] << 4))                      & 0x07FF);
        raw[5]  = static_cast<uint16_t>(((payload[6] >> 7) | (payload[7] << 1) | (payload[8] << 9))  & 0x07FF);
        raw[6]  = static_cast<uint16_t>(((payload[8] >> 2) | (payload[9] << 6))                      & 0x07FF);
        raw[7]  = static_cast<uint16_t>(((payload[9] >> 5) | (payload[10] << 3))                     & 0x07FF);
        raw[8]  = static_cast<uint16_t>((payload[11]      | (payload[12] << 8))                     & 0x07FF);
        raw[9]  = static_cast<uint16_t>(((payload[12] >> 3)| (payload[13] << 5))                     & 0x07FF);
        raw[10] = static_cast<uint16_t>(((payload[13] >> 6)| (payload[14] << 2)| (payload[15] << 10))& 0x07FF);
        raw[11] = static_cast<uint16_t>(((payload[15] >> 1)| (payload[16] << 7))                     & 0x07FF);
        raw[12] = static_cast<uint16_t>(((payload[16] >> 4)| (payload[17] << 4))                     & 0x07FF);
        raw[13] = static_cast<uint16_t>(((payload[17] >> 7)| (payload[18] << 1)| (payload[19] << 9)) & 0x07FF);
        raw[14] = static_cast<uint16_t>(((payload[19] >> 2)| (payload[20] << 6))                     & 0x07FF);
        raw[15] = static_cast<uint16_t>(((payload[20] >> 5)| (payload[21] << 3))                     & 0x07FF);

        std::array<uint16_t, kTotalChannels> channels_us{};
        for (size_t i = 0; i < kTotalChannels; ++i) {
            if (raw[i] < 172U) {
                channels_us[i] = kChannelMinUs;
            } else if (raw[i] > 1811U) {
                channels_us[i] = kChannelMaxUs;
            } else {
                channels_us[i] = static_cast<uint16_t>(988U + ((static_cast<uint32_t>(raw[i] - 172U) * 1024U) / 1640U));
            }
        }
        return channels_us;
    }
};

} // namespace drone::rc

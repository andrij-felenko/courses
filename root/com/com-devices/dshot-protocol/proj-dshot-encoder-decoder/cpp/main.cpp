#include <cstdint>
#include <array>
#include <span>
#include <optional>

namespace dshot {

constexpr uint16_t DisarmValue = 0;
constexpr uint16_t MinThrottle = 48;
constexpr uint16_t MaxThrottle = 2047;
constexpr size_t DmaBufferSize = 17;

struct Config {
    uint32_t timerArr{0};
    uint32_t ccrBit0{0};
    uint32_t ccrBit1{0};
    uint8_t motorPolePairs{7};
    bool bidirectional{true};

    constexpr Config(uint32_t arr, uint8_t polePairs = 7, bool bidir = true) noexcept
        : timerArr(arr),
          ccrBit0((arr * 33) / 100),
          ccrBit1((arr * 67) / 100),
          motorPolePairs(polePairs > 0 ? polePairs : 7),
          bidirectional(bidir) {}
};

struct Telemetry {
    uint32_t erpm{0};
    uint32_t rpm{0};
    uint8_t rawType{0};
    uint8_t rawPayload{0};
};

class ProtocolEngine {
public:
    explicit constexpr ProtocolEngine(Config config) noexcept : cfg_(config) {}

    [[nodiscard]] constexpr uint16_t createPacket(uint16_t throttle, bool requestTlm) const noexcept {
        const uint16_t clamped = (throttle > MaxThrottle) ? MaxThrottle : throttle;
        const uint16_t packet = (clamped << 1) | (requestTlm ? 1 : 0);
        
        uint16_t csum = 0;
        uint16_t csumData = packet;
        for (int i = 0; i < 3; ++i) {
            csum ^= (csumData & 0x0F);
            csumData >>= 4;
        }

        csum = cfg_.bidirectional ? ((~csum) & 0x0F) : (csum & 0x0F);
        return (packet << 4) | csum;
    }

    void fillDmaBuffer(uint16_t packet, std::span<uint32_t, DmaBufferSize> buffer) const noexcept {
        for (size_t i = 0; i < 16; ++i) {
            buffer[i] = (packet & (1 << (15 - i))) ? cfg_.ccrBit1 : cfg_.ccrBit0;
        }
        buffer[16] = 0;
    }

    [[nodiscard]] std::optional<Telemetry> decodeTelemetry(uint32_t rawGcr) const noexcept {
        const uint8_t gcr[4] = {
            static_cast<uint8_t>((rawGcr >> 15) & 0x1F),
            static_cast<uint8_t>((rawGcr >> 10) & 0x1F),
            static_cast<uint8_t>((rawGcr >> 5) & 0x1F),
            static_cast<uint8_t>(rawGcr & 0x1F)
        };

        int8_t nibbles[4];
        for (size_t i = 0; i < 4; ++i) {
            nibbles[i] = GcrTable[gcr[i]];
            if (nibbles[i] < 0) {
                return std::nullopt;
            }
        }

        const uint16_t val12 = (static_cast<uint16_t>(nibbles[0]) << 8) |
                               (static_cast<uint16_t>(nibbles[1]) << 4) |
                                static_cast<uint16_t>(nibbles[2]);
        const uint8_t rxCrc = static_cast<uint8_t>(nibbles[3]);

        const uint8_t expectedCrc = (~(val12 ^ (val12 >> 4) ^ (val12 >> 8))) & 0x0F;
        if (expectedCrc != rxCrc) {
            return std::nullopt;
        }

        Telemetry tlm{};
        tlm.rawType = (val12 >> 8) & 0x0F;
        tlm.rawPayload = static_cast<uint8_t>(val12 & 0xFF);

        const uint8_t exponent = (val12 >> 9) & 0x07;
        const uint16_t mantissa = val12 & 0x01FF;

        if (mantissa == 0) {
            return tlm;
        }

        const uint32_t periodUs = static_cast<uint32_t>(mantissa) << exponent;
        if (periodUs > 0) {
            tlm.erpm = 10000000UL / periodUs;
            tlm.rpm = tlm.erpm / cfg_.motorPolePairs;
        }

        return tlm;
    }

private:
    Config cfg_;

    static constexpr std::array<int8_t, 32> GcrTable = {
        -1,   -1,   -1,   -1,   -1,   -1,   -1,   -1,
        -1,   -1,   -1,   -1,   -1, 0x0D, 0x0E, 0x0F,
        -1,   -1, 0x08, 0x09,   -1, 0x05, 0x0A, 0x0B,
        -1, 0x00, 0x0C, 0x01,   -1, 0x04, 0x02, 0x03
    };
};

} // namespace dshot

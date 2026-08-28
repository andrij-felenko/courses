#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <system_error>

namespace quic {

struct VarintResult {
    uint64_t value;
    size_t length;
};

class VarintCodec {
public:
    static std::optional<size_t> encode(uint64_t val, std::span<uint8_t> out) noexcept {
        if (val <= 63) {
            if (out.size() < 1) return std::nullopt;
            out[0] = static_cast<uint8_t>(val & 0x3F);
            return 1;
        } else if (val <= 16383) {
            if (out.size() < 2) return std::nullopt;
            out[0] = static_cast<uint8_t>(((val >> 8) & 0x3F) | 0x40);
            out[1] = static_cast<uint8_t>(val & 0xFF);
            return 2;
        } else if (val <= 1073741823) {
            if (out.size() < 4) return std::nullopt;
            out[0] = static_cast<uint8_t>(((val >> 24) & 0x3F) | 0x80);
            out[1] = static_cast<uint8_t>((val >> 16) & 0xFF);
            out[2] = static_cast<uint8_t>((val >> 8) & 0xFF);
            out[3] = static_cast<uint8_t>(val & 0xFF);
            return 4;
        } else if (val <= 4611686018427387903ULL) {
            if (out.size() < 8) return std::nullopt;
            out[0] = static_cast<uint8_t>(((val >> 56) & 0x3F) | 0xC0);
            out[1] = static_cast<uint8_t>((val >> 48) & 0xFF);
            out[2] = static_cast<uint8_t>((val >> 40) & 0xFF);
            out[3] = static_cast<uint8_t>((val >> 32) & 0xFF);
            out[4] = static_cast<uint8_t>((val >> 24) & 0xFF);
            out[5] = static_cast<uint8_t>((val >> 16) & 0xFF);
            out[6] = static_cast<uint8_t>((val >> 8) & 0xFF);
            out[7] = static_cast<uint8_t>(val & 0xFF);
            return 8;
        }
        return std::nullopt;
    }

    static std::optional<VarintResult> decode(std::span<const uint8_t> in) noexcept {
        if (in.empty()) return std::nullopt;

        const uint8_t prefix = (in[0] >> 6) & 0x03;
        const size_t len = 1ULL << prefix;

        if (in.size() < len) return std::nullopt;

        uint64_t result = in[0] & 0x3F;
        for (size_t i = 1; i < len; ++i) {
            result = (result << 8) | in[i];
        }

        return VarintResult{result, len};
    }
};

} // namespace quic

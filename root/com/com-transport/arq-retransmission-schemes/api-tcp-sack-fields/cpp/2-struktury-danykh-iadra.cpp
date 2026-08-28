#include <cstdint>
#include <vector>
#include <array>
#include <optional>
#include <span>

namespace net {

struct SackBlock {
    uint32_t start_seq{0}; // Left Edge
    uint32_t end_seq{0};   // Right Edge

    [[nodiscard]] constexpr uint32_t length() const noexcept {
        return end_seq - start_seq;
    }

    [[nodiscard]] constexpr bool contains(uint32_t seq) const noexcept {
        return seq >= start_seq && seq < end_seq;
    }
};

class TcpSackParser {
public:
    static constexpr uint8_t KIND_SACK_PERMITTED = 4;
    static constexpr uint8_t KIND_SACK           = 5;
    static constexpr size_t  MAX_SACK_BLOCKS     = 4;

    struct ParseResult {
        std::vector<SackBlock> blocks;
        bool is_dsack{false};
    };

    static std::optional<ParseResult> parse(std::span<const uint8_t> opt, uint32_t cumulative_ack) {
        if (opt.size() < 10 || opt[0] != KIND_SACK || ((opt[1] - 2) % 8) != 0) {
            return std::nullopt;
        }

        const size_t len = opt[1];
        if (opt.size() < len) return std::nullopt;

        const size_t num_blocks = std::min<size_t>((len - 2) / 8, MAX_SACK_BLOCKS);
        ParseResult result;
        result.blocks.reserve(num_blocks);

        const uint8_t* p = opt.data() + 2;
        for (size_t i = 0; i < num_blocks; ++i) {
            const uint32_t left = (static_cast<uint32_t>(p[0]) << 24) |
                                  (static_cast<uint32_t>(p[1]) << 16) |
                                  (static_cast<uint32_t>(p[2]) << 8)  |
                                  static_cast<uint32_t>(p[3]);

            const uint32_t right = (static_cast<uint32_t>(p[4]) << 24) |
                                   (static_cast<uint32_t>(p[5]) << 16) |
                                   (static_cast<uint32_t>(p[6]) << 8)  |
                                   static_cast<uint32_t>(p[7]);

            result.blocks.push_back({left, right});
            p += 8;
        }

        if (!result.blocks.empty()) {
            const auto& first = result.blocks.front();
            if (first.start_seq < cumulative_ack ||
               (result.blocks.size() > 1 && 
                first.start_seq >= result.blocks[1].start_seq &&
                first.end_seq <= result.blocks[1].end_seq)) {
                result.is_dsack = true;
            }
        }
        return result;
    }
};

} // namespace net

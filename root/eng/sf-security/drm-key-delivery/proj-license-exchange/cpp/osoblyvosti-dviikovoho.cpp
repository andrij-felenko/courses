#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <optional>
#include <cstdint>
#include <cstring>

#if defined(_WIN32)
  #include <winsock2.h>
#else
  #include <arpa/inet.h>
#endif

namespace drm {

struct PsshBox {
    uint8_t version{0};
    std::array<uint8_t, 16> system_id{};
    std::vector<std::array<uint8_t, 16>> kids;
    std::vector<uint8_t> data;
};

class PsshParser {
public:
    static std::optional<PsshBox> parse(std::span<const uint8_t> bytes) {
        if (bytes.size() < 32) {
            return std::nullopt;
        }

        size_t offset = 0;
        uint32_t box_size = read_be32(bytes.subspan(offset, 4));
        offset += 4;

        if (box_size > bytes.size() || box_size < 32) {
            return std::nullopt;
        }

        // Перевірка FourCC: 'pssh'
        if (std::memcmp(bytes.data() + offset, "pssh", 4) != 0) {
            return std::nullopt;
        }
        offset += 4;

        PsshBox box;
        box.version = bytes[offset++];
        offset += 3; // flags

        std::memcpy(box.system_id.data(), bytes.data() + offset, 16);
        offset += 16;

        if (box.version == 1) {
            if (offset + 4 > box_size) return std::nullopt;
            uint32_t kid_count = read_be32(bytes.subspan(offset, 4));
            offset += 4;

            if (offset + (static_cast<size_t>(kid_count) * 16) > box_size) {
                return std::nullopt;
            }

            box.kids.resize(kid_count);
            for (uint32_t i = 0; i < kid_count; ++i) {
                std::memcpy(box.kids[i].data(), bytes.data() + offset, 16);
                offset += 16;
            }
        }

        if (offset + 4 > box_size) return std::nullopt;
        uint32_t data_size = read_be32(bytes.subspan(offset, 4));
        offset += 4;

        if (offset + data_size > box_size) return std::nullopt;

        box.data.resize(data_size);
        if (data_size > 0) {
            std::memcpy(box.data.data(), bytes.data() + offset, data_size);
        }

        return box;
    }

private:
    static inline uint32_t read_be32(std::span<const uint8_t, 4> s) {
        return (static_cast<uint32_t>(s[0]) << 24) |
               (static_cast<uint32_t>(s[1]) << 16) |
               (static_cast<uint32_t>(s[2]) <<  8) |
               (static_cast<uint32_t>(s[3]));
    }
};

} // namespace drm

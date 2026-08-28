#include <string_view>
#include <charconv>
#include <optional>
#include <cstdint>
#include <algorithm>

struct ByteRange {
    uint64_t start{0};
    uint64_t end{0};

    [[nodiscard]] constexpr uint64_t length() const noexcept {
        return end - start + 1;
    }
};

class RangeHeaderParser {
public:
    [[nodiscard]] static std::optional<ByteRange> parseSingle(
        std::string_view header,
        uint64_t fileSize) noexcept
    {
        if (fileSize == 0 || !header.starts_with("bytes=")) {
            return std::nullopt;
        }
        header.remove_prefix(6);

        auto dashPos = header.find('-');
        if (dashPos == std::string_view::npos) {
            return std::nullopt;
        }

        auto startStr = header.substr(0, dashPos);
        auto endStr = header.substr(dashPos + 1);

        if (startStr.empty()) {
            // Формат -suffix
            uint64_t suffix = 0;
            if (auto [p, ec] = std::from_chars(endStr.data(), endStr.data() + endStr.size(), suffix);
                ec == std::errc{} && suffix > 0) {
                uint64_t start = (suffix >= fileSize) ? 0 : (fileSize - suffix);
                return ByteRange{start, fileSize - 1};
            }
            return std::nullopt;
        }

        uint64_t start = 0;
        if (auto [p, ec] = std::from_chars(startStr.data(), startStr.data() + startStr.size(), start);
            ec != std::errc{} || start >= fileSize) {
            return std::nullopt;
        }

        if (endStr.empty()) {
            // Формат start-
            return ByteRange{start, fileSize - 1};
        }

        // Формат start-end
        uint64_t end = 0;
        if (auto [p, ec] = std::from_chars(endStr.data(), endStr.data() + endStr.size(), end);
            ec == std::errc{} && start <= end) {
            return ByteRange{start, std::min(end, fileSize - 1)};
        }

        return std::nullopt;
    }
};

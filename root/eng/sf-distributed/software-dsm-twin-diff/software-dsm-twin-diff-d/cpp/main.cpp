#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <vector>

constexpr size_t PageSize = 4096;

struct DiffSegment {
    uint16_t offset{0};
    std::vector<std::byte> payload;
};

class DiffGenerator {
public:
    static std::vector<DiffSegment> compute(std::span<const std::byte, PageSize> page,
                                           std::span<const std::byte, PageSize> twin) noexcept {
        std::vector<DiffSegment> segments;
        const auto* p64 = reinterpret_cast<const uint64_t*>(page.data());
        const auto* t64 = reinterpret_cast<const uint64_t*>(twin.data());
        constexpr size_t numWords = PageSize / sizeof(uint64_t);

        size_t i = 0;
        while (i < numWords) {
            if (p64[i] == t64[i]) {
                ++i;
                continue;
            }

            size_t startByte = i * sizeof(uint64_t);
            while (startByte < PageSize && page[startByte] == twin[startByte]) {
                ++startByte;
            }

            size_t endByte = (i + 1) * sizeof(uint64_t);
            if (endByte > PageSize) endByte = PageSize;

            while (endByte < PageSize && page[endByte] != twin[endByte]) {
                ++endByte;
            }

            size_t runLen = endByte - startByte;
            DiffSegment seg;
            seg.offset = static_cast<uint16_t>(startByte);
            seg.payload.resize(runLen);
            std::memcpy(seg.payload.data(), page.data() + startByte, runLen);

            segments.push_back(std::move(seg));
            i = (endByte / sizeof(uint64_t)) + 1;
        }

        return segments;
    }
};

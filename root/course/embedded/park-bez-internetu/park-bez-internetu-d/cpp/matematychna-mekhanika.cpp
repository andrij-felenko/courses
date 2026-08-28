/* C++20 алгоритм узгодження чанків із використанням std::span */
#include <span>
#include <optional>
#include <cstdint>

std::optional<uint32_t> findNextMissingChunk(
    std::span<const uint8_t> local_bitmask,
    std::span<const uint8_t> remote_bitmask) 
{
    const std::size_t len = std::min(local_bitmask.size(), remote_bitmask.size());
    for (std::size_t byte_idx = 0; byte_idx < len; ++byte_idx) {
        uint8_t needed = remote_bitmask[byte_idx] & static_cast<uint8_t>(~local_bitmask[byte_idx]);
        if (needed != 0) {
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if ((needed & (1u << bit)) != 0) {
                    return static_cast<uint32_t>((byte_idx * 8) + bit);
                }
            }
        }
    }
    return std::nullopt;
}

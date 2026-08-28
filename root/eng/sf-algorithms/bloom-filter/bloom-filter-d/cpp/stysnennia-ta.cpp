#include <cstdint>
#include <vector>
#include <cstddef>

namespace sys {

// RLE-стиснення для ущільнення бітового масиву у C++
std::vector<std::uint8_t> compress_rle_bitset(std::span<const std::uint8_t> input) {
    std::vector<std::uint8_t> compressed;
    compressed.reserve(input.size());

    for (std::size_t i = 0; i < input.size(); ) {
        if (input[i] == 0x00) {
            std::size_t zero_count = 0;
            while (i < input.size() && input[i] == 0x00 && zero_count < 255) {
                ++zero_count;
                ++i;
            }
            compressed.push_back(0x00);
            compressed.push_back(static_cast<std::uint8_t>(zero_count));
        } else {
            compressed.push_back(input[i++]);
        }
    }
    return compressed;
}

} // namespace sys

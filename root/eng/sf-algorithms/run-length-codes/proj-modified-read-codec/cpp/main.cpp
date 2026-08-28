#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <array>
#include <stdexcept>
#include <algorithm>

namespace compression::mr {

class BitWriter {
public:
    explicit BitWriter(std::vector<uint8_t>& buffer)
        : buffer_(buffer), bit_pos_(0) {}

    void put(uint32_t code, uint32_t length) {
        for (int32_t i = static_cast<int32_t>(length) - 1; i >= 0; --i) {
            size_t byte_idx = bit_pos_ >> 3;
            uint32_t bit_idx = 7 - (bit_pos_ & 7);

            if (byte_idx >= buffer_.size()) {
                buffer_.push_back(0);
            }
            if ((code >> i) & 1) {
                buffer_[byte_idx] |= static_cast<uint8_t>(1 << bit_idx);
            }
            bit_pos_++;
        }
    }

    [[nodiscard]] size_t bit_count() const noexcept { return bit_pos_; }
    [[nodiscard]] size_t byte_count() const noexcept { return (bit_pos_ + 7) >> 3; }

private:
    std::vector<uint8_t>& buffer_;
    size_t bit_pos_;
};

struct CodeEntry {
    uint16_t code;
    uint8_t length;
};

// Термінальні коди Гаффмана для довжин серій 0..15
constexpr std::array<CodeEntry, 16> kWhiteMHTable = {{
    {0x0035, 8}, {0x0007, 6}, {0x0007, 4}, {0x0008, 4},
    {0x000B, 4}, {0x000C, 4}, {0x000E, 4}, {0x000F, 4},
    {0x0013, 5}, {0x0014, 5}, {0x0007, 5}, {0x0008, 5},
    {0x0008, 6}, {0x0003, 6}, {0x0034, 6}, {0x0035, 6}
}};

class ModifiedReadCodec {
public:
    static std::vector<uint8_t> encode_scanline(std::span<const uint8_t> ref,
                                                std::span<const uint8_t> curr,
                                                int width) {
        std::vector<uint8_t> output;
        BitWriter writer(output);

        int a0 = -1;
        int a0_color = 0; // 0 = білий, 1 = чорний

        while (a0 < width) {
            int a1 = find_next_transition(curr, a0, width);
            int b1 = find_b1(ref, a0, width, a0_color);
            int b2 = find_b2(ref, b1, width);

            if (b2 < a1) {
                // Pass Mode
                writer.put(0x0001, 4);
                a0 = b2;
            } else {
                int diff = a1 - b1;
                if (diff >= -3 && diff <= 3) {
                    // Vertical Mode
                    encode_vertical(writer, diff);
                    a0 = a1;
                    a0_color = 1 - a0_color;
                } else {
                    // Horizontal Mode
                    int a2 = find_next_transition(curr, a1, width);
                    writer.put(0x0001, 3); // Префікс '001'

                    int run1 = a1 - ((a0 < 0) ? 0 : a0);
                    int run2 = a2 - a1;
                    encode_run(writer, run1);
                    encode_run(writer, run2);
                    a0 = a2;
                }
            }
        }
        return output;
    }

private:
    static int get_pixel(std::span<const uint8_t> row, int x, int width) noexcept {
        if (x < 0 || x >= width) return 0;
        return (row[static_cast<size_t>(x >> 3)] >> (7 - (x & 7))) & 1;
    }

    static int find_next_transition(std::span<const uint8_t> row, int x, int width) noexcept {
        int base_color = get_pixel(row, x, width);
        int curr = (x < 0) ? 0 : x + 1;

        while ((curr & 7) != 0 && curr < width) {
            if (get_pixel(row, curr, width) != base_color) return curr;
            ++curr;
        }
        uint8_t skip_byte = base_color ? 0xFF : 0x00;
        while (curr + 8 <= width && row[static_cast<size_t>(curr >> 3)] == skip_byte) {
            curr += 8;
        }
        while (curr < width) {
            if (get_pixel(row, curr, width) != base_color) return curr;
            ++curr;
        }
        return width;
    }

    static int find_b1(std::span<const uint8_t> ref, int a0, int width, int a0_color) noexcept {
        int target = 1 - a0_color;
        int b1 = (a0 < 0) ? 0 : a0 + 1;
        while (b1 < width) {
            int color = get_pixel(ref, b1, width);
            int prev = get_pixel(ref, b1 - 1, width);
            if (color == target && color != prev) {
                return b1;
            }
            ++b1;
        }
        return width;
    }

    static int find_b2(std::span<const uint8_t> ref, int b1, int width) noexcept {
        if (b1 >= width) return width;
        int b1_color = get_pixel(ref, b1, width);
        int b2 = b1 + 1;
        while (b2 < width) {
            if (get_pixel(ref, b2, width) != b1_color) {
                return b2;
            }
            ++b2;
        }
        return width;
    }

    static void encode_vertical(BitWriter& writer, int diff) {
        switch (diff) {
            case  0: writer.put(0x0001, 1); break;
            case  1: writer.put(0x0003, 3); break;
            case -1: writer.put(0x0002, 3); break;
            case  2: writer.put(0x0003, 6); break;
            case -2: writer.put(0x0002, 6); break;
            case  3: writer.put(0x0003, 7); break;
            case -3: writer.put(0x0002, 7); break;
            default: break;
        }
    }

    static void encode_run(BitWriter& writer, int run) {
        if (run >= 0 && run < static_cast<int>(kWhiteMHTable.size())) {
            const auto& entry = kWhiteMHTable[static_cast<size_t>(run)];
            writer.put(entry.code, entry.length);
        } else {
            writer.put(static_cast<uint32_t>(run), 12);
        }
    }
};

} // namespace compression::mr

// RSS Toeplitz Hash & RETA Simulator (C++20 Edition)

#include <iostream>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>
#include <algorithm>

namespace rss {

constexpr std::size_t KeySize = 40;
constexpr std::size_t RetaSize = 128;

// Стандартний секретний ключ NDIS RSS
constexpr std::array<std::uint8_t, KeySize> DefaultRssKey = {
    0x6d, 0x5a, 0x56, 0xda, 0x25, 0x5b, 0x0e, 0xc2,
    0x41, 0x67, 0x25, 0x3d, 0x43, 0xa3, 0x8f, 0x00,
    0xd0, 0x29, 0x4b, 0x7d, 0x3d, 0x14, 0x4e, 0x69,
    0x9f, 0xac, 0xe5, 0x42, 0x1d, 0x64, 0x52, 0x72,
    0x0f, 0x4c, 0xf7, 0xad, 0x55, 0x54, 0x03, 0xb9
};

struct FlowTupleV4 {
    std::uint32_t src_ip;
    std::uint32_t dst_ip;
    std::uint16_t src_port;
    std::uint16_t dst_port;

    // Конвертація кортежу у байтовий послідовний буфер
    [[nodiscard]] std::array<std::uint8_t, 12> to_bytes() const noexcept {
        std::array<std::uint8_t, 12> buf{};
        buf[0] = static_cast<std::uint8_t>(src_ip >> 24);
        buf[1] = static_cast<std::uint8_t>(src_ip >> 16);
        buf[2] = static_cast<std::uint8_t>(src_ip >> 8);
        buf[3] = static_cast<std::uint8_t>(src_ip);
        
        buf[4] = static_cast<std::uint8_t>(dst_ip >> 24);
        buf[5] = static_cast<std::uint8_t>(dst_ip >> 16);
        buf[6] = static_cast<std::uint8_t>(dst_ip >> 8);
        buf[7] = static_cast<std::uint8_t>(dst_ip);

        buf[8] = static_cast<std::uint8_t>(src_port >> 8);
        buf[9] = static_cast<std::uint8_t>(src_port);

        buf[10] = static_cast<std::uint8_t>(dst_port >> 8);
        buf[11] = static_cast<std::uint8_t>(dst_port);
        return buf;
    }
};

class RssEngine {
public:
    explicit RssEngine(std::span<const std::uint8_t, KeySize> key = DefaultRssKey)
        : key_(key) {
        init_reta_equal(4); // За замовчуванням 4 черги
    }

    void init_reta_equal(std::uint8_t num_queues) noexcept {
        for (std::size_t i = 0; i < RetaSize; ++i) {
            reta_[i] = static_cast<std::uint8_t>(i % num_queues);
        }
    }

    [[nodiscard]] std::uint32_t calculate_hash(std::span<const std::uint8_t> input) const noexcept {
        std::uint32_t hash = 0;
        for (std::size_t byte_idx = 0; byte_idx < input.size(); ++byte_idx) {
            const std::uint8_t byte = input[byte_idx];
            for (int bit = 7; bit >= 0; --bit) {
                if ((byte >> bit) & 1) {
                    const std::size_t key_byte_idx = byte_idx + (7 - bit) / 8;
                    const int key_bit_shift = (7 - bit) % 8;

                    std::uint32_t key_window =
                        (static_cast<std::uint32_t>(key_[key_byte_idx]) << (24 + key_bit_shift)) |
                        (static_cast<std::uint32_t>(key_[key_byte_idx + 1]) << (16 + key_bit_shift)) |
                        (static_cast<std::uint32_t>(key_[key_byte_idx + 2]) << (8 + key_bit_shift)) |
                        (static_cast<std::uint32_t>(key_[key_byte_idx + 3]) << key_bit_shift);

                    if (key_bit_shift > 0) {
                        key_window |= (static_cast<std::uint32_t>(key_[key_byte_idx + 4]) >> (8 - key_bit_shift));
                    }

                    hash ^= key_window;
                }
            }
        }
        return hash;
    }

    [[nodiscard]] std::uint8_t route_flow(const FlowTupleV4& tuple) const noexcept {
        const auto bytes = tuple.to_bytes();
        const std::uint32_t hash = calculate_hash(bytes);
        const std::size_t reta_idx = hash & (RetaSize - 1);
        return reta_[reta_idx];
    }

private:
    std::span<const std::uint8_t, KeySize> key_;
    std::array<std::uint8_t, RetaSize> reta_{};
};

} // namespace rss

int main() {
    rss::RssEngine engine;

    const rss::FlowTupleV4 fwd{0xC0A80132, 0x0A000001, 49152, 80};
    const rss::FlowTupleV4 rev{0x0A000001, 0xC0A80132, 80, 49152};

    const auto fwd_bytes = fwd.to_bytes();
    const auto rev_bytes = rev.to_bytes();

    const std::uint32_t hash_fwd = engine.calculate_hash(fwd_bytes);
    const std::uint32_t hash_rev = engine.calculate_hash(rev_bytes);

    std::cout << std::hex << std::uppercase;
    std::cout << "[C++20] FWD Hash: 0x" << std::setw(8) << std::setfill('0') << hash_fwd 
              << " -> Queue: " << std::dec << static_cast<int>(engine.route_flow(fwd)) << "\n";
    std::cout << std::hex << std::uppercase;
    std::cout << "[C++20] REV Hash: 0x" << std::setw(8) << std::setfill('0') << hash_rev 
              << " -> Queue: " << std::dec << static_cast<int>(engine.route_flow(rev)) << "\n";

    return 0;
}

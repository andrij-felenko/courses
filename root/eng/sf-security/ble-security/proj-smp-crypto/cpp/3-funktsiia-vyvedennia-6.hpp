#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;
using Coordinate256 = std::array<uint8_t, 32>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Block128 f4(const Coordinate256& u, const Coordinate256& v,
                          const Block128& x, uint8_t z) noexcept {
    std::array<uint8_t, 65> msg{};
    std::memcpy(msg.data(), u.data(), 32);
    std::memcpy(msg.data() + 32, v.data(), 32);
    msg[64] = z;

    Block128 confirm{};
    aes_cmac(x, msg, confirm);
    return confirm;
}

[[nodiscard]] uint32_t g2(const Coordinate256& u, const Coordinate256& v,
                          const Block128& x, const Block128& y) noexcept {
    std::array<uint8_t, 80> msg{};
    std::memcpy(msg.data(), u.data(), 32);
    std::memcpy(msg.data() + 32, v.data(), 32);
    std::memcpy(msg.data() + 64, y.data(), 16);

    Block128 mac{};
    aes_cmac(x, msg, mac);

    const uint32_t raw_val = static_cast<uint32_t>(mac[0]) |
                             (static_cast<uint32_t>(mac[1]) << 8) |
                             (static_cast<uint32_t>(mac[2]) << 16) |
                             (static_cast<uint32_t>(mac[3]) << 24);

    return raw_val % 1000000;
}

} // namespace ble::crypto

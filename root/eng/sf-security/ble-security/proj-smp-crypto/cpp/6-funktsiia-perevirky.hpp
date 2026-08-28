#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Block128 f6(const Block128& mackey,
                          const Block128& n1, const Block128& n2,
                          const Block128& r,
                          std::span<const uint8_t, 3> iocap,
                          uint8_t a1_type, std::span<const uint8_t, 6> a1_addr,
                          uint8_t a2_type, std::span<const uint8_t, 6> a2_addr) noexcept {
    std::array<uint8_t, 65> msg{};
    std::memcpy(msg.data(), n1.data(), 16);
    std::memcpy(msg.data() + 16, n2.data(), 16);
    std::memcpy(msg.data() + 32, r.data(), 16);
    std::memcpy(msg.data() + 48, iocap.data(), 3);
    msg[51] = a1_type;
    std::memcpy(msg.data() + 52, a1_addr.data(), 6);
    msg[58] = a2_type;
    std::memcpy(msg.data() + 59, a2_addr.data(), 6);

    Block128 check{};
    aes_cmac(mackey, msg, check);
    return check;
}

} // namespace ble::crypto

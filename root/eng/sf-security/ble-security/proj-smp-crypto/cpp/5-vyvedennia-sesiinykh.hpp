#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;
using Secret256 = std::array<uint8_t, 32>;

struct DerivedKeys {
    Block128 mac_key;
    Block128 ltk;
};

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] DerivedKeys f5(const Secret256& dhkey,
                            const Block128& na, const Block128& nb,
                            uint8_t a1_type, std::span<const uint8_t, 6> a1_addr,
                            uint8_t a2_type, std::span<const uint8_t, 6> a2_addr) noexcept {
    constexpr std::array<uint8_t, 16> salt = {
        0xBE, 0x83, 0x60, 0x5A, 0xDB, 0x0B, 0x37, 0x60,
        0x38, 0xA5, 0xF5, 0xAA, 0x91, 0x83, 0x88, 0x6C
    };

    Block128 w{};
    aes_cmac(salt, dhkey, w);

    std::array<uint8_t, 53> msg{};
    msg[1] = 'b'; msg[2] = 't'; msg[3] = 'l'; msg[4] = 'e';
    std::memcpy(msg.data() + 5, na.data(), 16);
    std::memcpy(msg.data() + 21, nb.data(), 16);
    msg[37] = a1_type;
    std::memcpy(msg.data() + 38, a1_addr.data(), 6);
    msg[44] = a2_type;
    std::memcpy(msg.data() + 45, a2_addr.data(), 6);
    msg[51] = 0x00;
    msg[52] = 0x01;

    DerivedKeys keys{};

    msg[0] = 0x00;
    aes_cmac(w, msg, keys.mac_key);

    msg[0] = 0x01;
    aes_cmac(w, msg, keys.ltk);

    return keys;
}

} // namespace ble::crypto

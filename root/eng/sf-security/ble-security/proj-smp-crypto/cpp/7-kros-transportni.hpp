#include <array>
#include <span>
#include <cstdint>

namespace ble::crypto {

using Block128 = std::array<uint8_t, 16>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Block128 h6(const Block128& w, std::span<const uint8_t, 4> key_id) noexcept {
    Block128 out{};
    aes_cmac(w, key_id, out);
    return out;
}

[[nodiscard]] Block128 h7(const Block128& salt, const Block128& w) noexcept {
    Block128 out{};
    aes_cmac(salt, w, out);
    return out;
}

} // namespace ble::crypto

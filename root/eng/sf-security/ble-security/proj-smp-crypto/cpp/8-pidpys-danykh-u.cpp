#include <array>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>

namespace ble::att {

using Signature12 = std::array<uint8_t, 12>;
using Key128 = std::array<uint8_t, 16>;

void aes_cmac(std::span<const uint8_t, 16> key,
              std::span<const uint8_t> msg,
              std::span<uint8_t, 16> mac_out) noexcept;

[[nodiscard]] Signature12 sign_data(const Key128& csrk,
                                    std::span<const uint8_t> att_pdu,
                                    uint32_t sign_counter) {
    std::vector<uint8_t> buffer(att_pdu.size() + 4);
    std::memcpy(buffer.data(), att_pdu.data(), att_pdu.size());

    const size_t offset = att_pdu.size();
    buffer[offset + 0] = static_cast<uint8_t>(sign_counter & 0xFF);
    buffer[offset + 1] = static_cast<uint8_t>((sign_counter >> 8) & 0xFF);
    buffer[offset + 2] = static_cast<uint8_t>((sign_counter >> 16) & 0xFF);
    buffer[offset + 3] = static_cast<uint8_t>((sign_counter >> 24) & 0xFF);

    std::array<uint8_t, 16> mac_full{};
    aes_cmac(csrk, buffer, mac_full);

    Signature12 signature{};
    std::memcpy(signature.data(), mac_full.data(), 8);
    std::memcpy(signature.data() + 8, buffer.data() + offset, 4);

    return signature;
}

} // namespace ble::att

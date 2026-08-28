#include <array>
#include <span>
#include <cstdint>
#include <cstring>

namespace ble::ll {

using Nonce13 = std::array<uint8_t, 13>;

[[nodiscard]] Nonce13 build_nonce(uint64_t packet_counter,
                                  bool is_master_to_slave,
                                  std::span<const uint8_t, 8> iv) noexcept {
    Nonce13 nonce{};

    nonce[0] = static_cast<uint8_t>(packet_counter & 0xFF);
    nonce[1] = static_cast<uint8_t>((packet_counter >> 8) & 0xFF);
    nonce[2] = static_cast<uint8_t>((packet_counter >> 16) & 0xFF);
    nonce[3] = static_cast<uint8_t>((packet_counter >> 24) & 0xFF);
    nonce[4] = static_cast<uint8_t>((packet_counter >> 32) & 0x7F);

    if (is_master_to_slave) {
        nonce[4] |= 0x80;
    }

    std::memcpy(nonce.data() + 5, iv.data(), 8);
    return nonce;
}

} // namespace ble::ll

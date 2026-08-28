#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <stdexcept>
#include <cstring>

namespace mavlink_sec {

void aesGcmEncrypt(
    std::span<const uint8_t, 32> key,
    std::span<const uint8_t, 12> iv,
    std::span<const uint8_t> plaintext,
    std::span<uint8_t> ciphertext,
    std::span<uint8_t, 16> tag
);

class TunnelEncryptor {
public:
    explicit TunnelEncryptor(std::span<const uint8_t, 32> aes_key) {
        std::copy(aes_key.begin(), aes_key.end(), aes_key_.begin());
    }

    ~TunnelEncryptor() {
        secureZeroize(aes_key_);
    }

    [[nodiscard]] MavlinkTunnel encryptFrame(
        uint8_t target_sys,
        uint8_t target_comp,
        std::span<const uint8_t> plain_packet
    ) {
        if (plain_packet.size() > 100) {
            throw std::length_error("Payload exceeds maximum TUNNEL buffer capacity (100 bytes)");
        }

        MavlinkTunnel tunnel{};
        tunnel.payload_type = 100; // Custom AES-GCM
        tunnel.target_system = target_sys;
        tunnel.target_component = target_comp;

        // Генерація унікального Nonce
        nonce_counter_++;
        std::array<uint8_t, 12> iv{};
        std::memcpy(iv.data(), &nonce_counter_, sizeof(nonce_counter_));
        std::copy(iv.begin(), iv.end(), tunnel.payload.begin());

        // Шифрування
        std::array<uint8_t, 16> tag{};
        aesGcmEncrypt(
            aes_key_,
            iv,
            plain_packet,
            std::span{tunnel.payload.data() + 12, plain_packet.size()},
            tag
        );

        std::copy(tag.begin(), tag.end(), tunnel.payload.begin() + 12 + plain_packet.size());
        tunnel.payload_length = static_cast<uint8_t>(12 + plain_packet.size() + 16);

        return tunnel;
    }

private:
    std::array<uint8_t, 32> aes_key_{};
    uint64_t                nonce_counter_{0};
};

} // namespace mavlink_sec

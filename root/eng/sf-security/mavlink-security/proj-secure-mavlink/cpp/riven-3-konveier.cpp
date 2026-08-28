#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <cstring>

namespace mavlink_sec {

void sha256Compute(std::span<const uint8_t> input, std::span<uint8_t, 32> output) noexcept;
uint16_t calculateCrc(std::span<const uint8_t> data, uint8_t crc_extra) noexcept;

class PacketSigner {
public:
    explicit PacketSigner(std::span<const uint8_t, 32> secret_key, uint8_t link_id = 0)
        : link_id_(link_id) {
        std::copy(secret_key.begin(), secret_key.end(), secret_key_.begin());
    }

    ~PacketSigner() {
        secureZeroize(secret_key_);
    }

    [[nodiscard]] std::vector<uint8_t> signPacket(
        std::span<const uint8_t> header_and_payload,
        uint8_t crc_extra
    ) {
        const size_t payload_len = header_and_payload.size() - 10;
        std::vector<uint8_t> packet(header_and_payload.size() + 2 + 13);

        // Копіюємо заголовок та корисні дані
        std::copy(header_and_payload.begin(), header_and_payload.end(), packet.begin());

        // Встановлюємо прапорець підпису MAVLINK_IFLAG_SIGNED
        packet[2] |= 0x01;
        timestamp_++;

        // Розрахунок CRC-16
        const uint16_t crc = calculateCrc(std::span{packet.data() + 1, 9 + payload_len}, crc_extra);
        packet[10 + payload_len]     = static_cast<uint8_t>(crc & 0xFF);
        packet[10 + payload_len + 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        // Трейлер підпису: Link ID + 48-бітний Timestamp
        const size_t trailer_pos = 12 + payload_len;
        packet[trailer_pos] = link_id_;
        for (size_t i = 0; i < 6; ++i) {
            packet[trailer_pos + 1 + i] = static_cast<uint8_t>((timestamp_ >> (8 * i)) & 0xFF);
        }

        // Вхідний масив для SHA-256
        std::vector<uint8_t> hash_input(51 + payload_len);
        std::copy(secret_key_.begin(), secret_key_.end(), hash_input.begin());
        std::copy(packet.begin(), packet.begin() + 10 + payload_len + 2 + 7, hash_input.begin() + 32);

        std::array<uint8_t, 32> digest{};
        sha256Compute(hash_input, digest);

        // Копіюємо перші 6 байтів дайджесту
        std::copy(digest.begin(), digest.begin() + 6, packet.begin() + trailer_pos + 7);

        secureZeroize(hash_input);
        secureZeroize(digest);

        return packet;
    }

private:
    std::array<uint8_t, 32> secret_key_{};
    uint8_t                 link_id_{0};
    uint64_t                timestamp_{1000000ULL};
};

} // namespace mavlink_sec

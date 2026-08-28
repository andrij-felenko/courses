#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <algorithm>

namespace secure_radio {

inline constexpr uint8_t  ProtocolMagic     = 0x53; // 'S'
inline constexpr uint8_t  ProtocolVersion   = 0x01;
inline constexpr size_t   AuthTagLength     = 16;
inline constexpr size_t   NonceLength       = 12;
inline constexpr size_t   HeaderLength      = 10;
inline constexpr size_t   MaxPayloadLength  = 64;
inline constexpr size_t   ReplayWindowSize  = 64;

enum class Error {
    InvalidLength,
    BadMagic,
    BadVersion,
    NotForMe,
    ReplayDetected,
    AuthFailed
};

#pragma pack(push, 1)
struct Header {
    uint8_t  magic;
    uint8_t  version;
    uint8_t  frame_type;
    uint8_t  reserved;
    uint16_t src_id;
    uint16_t dst_id;
    uint32_t seq_num;
};
#pragma pack(pop)

static_assert(sizeof(Header) == HeaderLength, "Header struct must be exactly 10 bytes");

// Зовнішні криптопримітиви (ChaCha20-Poly1305)
extern "C" {
    void chacha20_poly1305_encrypt(
        const uint8_t key[32], const uint8_t nonce[12],
        const uint8_t *aad, size_t aad_len,
        const uint8_t *plaintext, size_t len,
        uint8_t *ciphertext, uint8_t tag[16]
    );

    void chacha20_poly1305_decrypt(
        const uint8_t key[32], const uint8_t nonce[12],
        const uint8_t *aad, size_t aad_len,
        const uint8_t *ciphertext, size_t len,
        uint8_t *plaintext
    );
}

// Порівняння за сталий час
[[nodiscard]] inline bool constant_time_equals(
    std::span<const uint8_t, AuthTagLength> a,
    std::span<const uint8_t, AuthTagLength> b
) noexcept {
    uint8_t diff = 0;
    for (size_t i = 0; i < AuthTagLength; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

// Побудова 12-байтного Nonce
[[nodiscard]] inline std::array<uint8_t, NonceLength> make_nonce(
    uint16_t src, uint16_t dst, uint32_t epoch, uint32_t seq
) noexcept {
    return {
        static_cast<uint8_t>(src & 0xFF),
        static_cast<uint8_t>((src >> 8) & 0xFF),
        static_cast<uint8_t>(dst & 0xFF),
        static_cast<uint8_t>((dst >> 8) & 0xFF),
        static_cast<uint8_t>(epoch & 0xFF),
        static_cast<uint8_t>((epoch >> 8) & 0xFF),
        static_cast<uint8_t>((epoch >> 16) & 0xFF),
        static_cast<uint8_t>((epoch >> 24) & 0xFF),
        static_cast<uint8_t>(seq & 0xFF),
        static_cast<uint8_t>((seq >> 8) & 0xFF),
        static_cast<uint8_t>((seq >> 16) & 0xFF),
        static_cast<uint8_t>((seq >> 24) & 0xFF)
    };
}

class Sender {
public:
    constexpr Sender(std::span<const uint8_t, 32> key, uint16_t node_id, uint32_t epoch) noexcept
        : node_id_(node_id), epoch_(epoch), tx_seq_(1) {
        std::ranges::copy(key, key_.begin());
    }

    [[nodiscard]] std::optional<size_t> build_packet(
        uint16_t dst_id,
        uint8_t frame_type,
        std::span<const uint8_t> payload,
        std::span<uint8_t> out_buffer
    ) noexcept {
        if (payload.size() > MaxPayloadLength) return std::nullopt;
        const size_t total_len = HeaderLength + payload.size() + AuthTagLength;
        if (out_buffer.size() < total_len) return std::nullopt;

        Header hdr{
            .magic = ProtocolMagic,
            .version = ProtocolVersion,
            .frame_type = frame_type,
            .reserved = 0,
            .src_id = node_id_,
            .dst_id = dst_id,
            .seq_num = tx_seq_++
        };

        auto nonce = make_nonce(hdr.src_id, hdr.dst_id, epoch_, hdr.seq_num);

        // Копіюємо AAD на початок
        auto *hdr_ptr = reinterpret_cast<const uint8_t *>(&hdr);
        std::copy_n(hdr_ptr, HeaderLength, out_buffer.data());

        uint8_t *out_cipher = out_buffer.data() + HeaderLength;
        uint8_t *out_tag    = out_buffer.data() + HeaderLength + payload.size();

        chacha20_poly1305_encrypt(
            key_.data(), nonce.data(),
            hdr_ptr, HeaderLength,
            payload.data(), payload.size(),
            out_cipher, out_tag
        );

        return total_len;
    }

private:
    std::array<uint8_t, 32> key_{};
    uint16_t node_id_;
    uint32_t epoch_;
    uint32_t tx_seq_;
};

class Receiver {
public:
    struct DecryptedMessage {
        uint8_t frame_type;
        size_t  payload_size;
    };

    constexpr Receiver(
        std::span<const uint8_t, 32> key,
        uint16_t my_id,
        uint16_t peer_id,
        uint32_t epoch
    ) noexcept
        : my_id_(my_id), peer_id_(peer_id), epoch_(epoch), last_seq_(0), replay_mask_(0) {
        std::ranges::copy(key, key_.begin());
    }

    [[nodiscard]] std::expected<DecryptedMessage, Error> process_packet(
        std::span<const uint8_t> in_packet,
        std::span<uint8_t> out_payload
    ) noexcept {
        if (in_packet.size() < (HeaderLength + AuthTagLength)) {
            return std::unexpected(Error::InvalidLength);
        }

        const auto *hdr = reinterpret_cast<const Header *>(in_packet.data());

        // Швидка перевірка AAD
        if (hdr->magic != ProtocolMagic) return std::unexpected(Error::BadMagic);
        if (hdr->version != ProtocolVersion) return std::unexpected(Error::BadVersion);
        if (hdr->dst_id != my_id_ && hdr->dst_id != 0xFFFF) return std::unexpected(Error::NotForMe);
        if (hdr->src_id != peer_id_) return std::unexpected(Error::NotForMe);

        const size_t payload_len = in_packet.size() - HeaderLength - AuthTagLength;
        if (payload_len > out_payload.size() || payload_len > MaxPayloadLength) {
            return std::unexpected(Error::InvalidLength);
        }

        const uint32_t seq = hdr->seq_num;
        bool is_ahead = false;
        uint32_t shift = 0;
        uint32_t delta = 0;

        // Перевірка ковзного вікна Anti-Replay (без мутації)
        if (seq > last_seq_) {
            is_ahead = true;
            shift = seq - last_seq_;
        } else {
            delta = last_seq_ - seq;
            if (delta >= ReplayWindowSize) {
                return std::unexpected(Error::ReplayDetected);
            }
            if ((replay_mask_ & (1ULL << delta)) != 0) {
                return std::unexpected(Error::ReplayDetected);
            }
        }

        auto nonce = make_nonce(hdr->src_id, hdr->dst_id, epoch_, seq);
        const uint8_t *ciphertext = in_packet.data() + HeaderLength;
        
        std::span<const uint8_t, AuthTagLength> rx_tag(
            in_packet.data() + HeaderLength + payload_len, AuthTagLength
        );

        std::array<uint8_t, AuthTagLength> calc_tag{};
        uint8_t dummy_plain[MaxPayloadLength];

        // Розрахунок тегу над AAD + Ciphertext
        chacha20_poly1305_encrypt(
            key_.data(), nonce.data(),
            in_packet.data(), HeaderLength,
            dummy_plain, 0,
            nullptr, calc_tag.data()
        );

        // Constant-time верифікація тегу
        if (!constant_time_equals(calc_tag, rx_tag)) {
            return std::unexpected(Error::AuthFailed);
        }

        // Фіксація стану Anti-Replay вікна
        if (is_ahead) {
            if (shift < ReplayWindowSize) {
                replay_mask_ = (replay_mask_ << shift) | 1ULL;
            } else {
                replay_mask_ = 1ULL;
            }
            last_seq_ = seq;
        } else {
            replay_mask_ |= (1ULL << delta);
        }

        // Розшифрування перевіреного тіла
        chacha20_poly1305_decrypt(
            key_.data(), nonce.data(),
            in_packet.data(), HeaderLength,
            ciphertext, payload_len,
            out_payload.data()
        );

        return DecryptedMessage{
            .frame_type = hdr->frame_type,
            .payload_size = payload_len
        };
    }

private:
    std::array<uint8_t, 32> key_{};
    uint16_t my_id_;
    uint16_t peer_id_;
    uint32_t epoch_;
    uint32_t last_seq_;
    uint64_t replay_mask_;
};

} // namespace secure_radio

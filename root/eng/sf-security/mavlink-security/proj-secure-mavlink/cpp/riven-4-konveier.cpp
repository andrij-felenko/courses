#include <expected>
#include <span>
#include <functional>

namespace mavlink_sec {

enum class VerifyError {
    BadCrc,
    UnsignedRejected,
    ReplayDetected,
    BadSignature,
    StreamOverflow
};

class PacketVerifier {
public:
    using AcceptUnsignedPredicate = std::function<bool(uint32_t msgid)>;

    explicit PacketVerifier(std::span<const uint8_t, 32> secret_key, AcceptUnsignedPredicate unsigned_filter = nullptr)
        : unsigned_filter_(std::move(unsigned_filter)) {
        std::copy(secret_key.begin(), secret_key.end(), secret_key_.begin());
    }

    ~PacketVerifier() {
        secureZeroize(secret_key_);
    }

    [[nodiscard]] std::expected<void, VerifyError> verifyPacket(
        std::span<const uint8_t> frame,
        uint8_t crc_extra
    ) {
        if (frame.size() < 12) return std::unexpected(VerifyError::BadCrc);

        const uint8_t payload_len = frame[1];
        const uint8_t incompat_flags = frame[2];
        const uint8_t sysid = frame[5];
        const uint8_t compid = frame[6];
        const uint32_t msgid = frame[7] | (uint32_t(frame[8]) << 8) | (uint32_t(frame[9]) << 16);

        // 1. CRC
        const uint16_t expected_crc = frame[10 + payload_len] | (uint16_t(frame[11 + payload_len]) << 8);
        const uint16_t calc_crc = calculateCrc(frame.subspan(1, 9 + payload_len), crc_extra);
        if (calc_crc != expected_crc) return std::unexpected(VerifyError::BadCrc);

        // 2. Непідписані повідомлення
        if (!(incompat_flags & 0x01)) {
            if (unsigned_filter_ && unsigned_filter_(msgid)) {
                return {};
            }
            return std::unexpected(VerifyError::UnsignedRejected);
        }

        if (frame.size() < 10 + payload_len + 2 + 13) {
            return std::unexpected(VerifyError::BadSignature);
        }

        const size_t trailer_offset = 12 + payload_len;
        const uint8_t link_id = frame[trailer_offset];

        uint64_t incoming_ts = 0;
        for (size_t i = 0; i < 6; ++i) {
            incoming_ts |= (uint64_t(frame[trailer_offset + 1 + i]) << (8 * i));
        }

        // 3. Перевірка Replay
        auto* stream = streams_.getOrCreate({sysid, compid, link_id});
        if (!stream) return std::unexpected(VerifyError::StreamOverflow);

        if (stream->last_timestamp != 0 && incoming_ts <= stream->last_timestamp) {
            return std::unexpected(VerifyError::ReplayDetected);
        }

        // 4. Обчислення SHA-256
        std::vector<uint8_t> hash_input(51 + payload_len);
        std::copy(secret_key_.begin(), secret_key_.end(), hash_input.begin());
        std::copy(frame.begin(), frame.begin() + 10 + payload_len + 2 + 7, hash_input.begin() + 32);

        std::array<uint8_t, 32> digest{};
        sha256Compute(hash_input, digest);

        const int match = secureMemcmp(frame.subspan(trailer_offset + 7, 6), std::span{digest.data(), 6});
        secureZeroize(hash_input);
        secureZeroize(digest);

        if (match != 0) return std::unexpected(VerifyError::BadSignature);

        stream->last_timestamp = incoming_ts;
        return {};
    }

private:
    std::array<uint8_t, 32> secret_key_{};
    AcceptUnsignedPredicate unsigned_filter_{};
    StreamTable             streams_{};
};

} // namespace mavlink_sec

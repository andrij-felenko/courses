#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <cstring>

constexpr std::uint16_t SECURE_FRAME_MAGIC = 0xA55A;
constexpr std::size_t TAG_SIZE = 16;
constexpr std::size_t MAX_PAYLOAD_SIZE = 128;

#pragma pack(push, 1)
struct SecureHeader {
    std::uint16_t magic{SECURE_FRAME_MAGIC};
    std::uint32_t sequence_num{0};
    std::uint16_t payload_len{0};
};
#pragma pack(pop)

// Прототипи верифікованих криптопримітивів
extern void crypto_aead_encrypt(std::uint8_t *cipher, std::uint8_t *tag,
                                const std::uint8_t *key, const std::uint8_t *nonce,
                                const std::uint8_t *aad, std::size_t aad_len,
                                const std::uint8_t *plain, std::size_t plain_len);

extern void crypto_aead_decrypt(std::uint8_t *plain,
                                const std::uint8_t *key, const std::uint8_t *nonce,
                                const std::uint8_t *aad, std::size_t aad_len,
                                const std::uint8_t *cipher, std::size_t cipher_len);

[[nodiscard]] bool crypto_verify_ct(std::span<const std::uint8_t> a, 
                                    std::span<const std::uint8_t> b) noexcept;

class SecureChannelSession {
public:
    explicit SecureChannelSession(std::span<const std::uint8_t, 32> key) noexcept {
        std::memcpy(session_key_.data(), key.data(), 32);
    }

    [[nodiscard]] std::optional<std::size_t> encode_frame(
        std::span<const std::uint8_t> plaintext,
        std::span<std::uint8_t> out_buffer) noexcept 
    {
        if (plaintext.size() > MAX_PAYLOAD_SIZE) {
            return std::nullopt;
        }

        const std::size_t total_size = sizeof(SecureHeader) + plaintext.size() + TAG_SIZE;
        if (out_buffer.size() < total_size) {
            return std::nullopt;
        }

        SecureHeader header{};
        header.magic = SECURE_FRAME_MAGIC;
        header.sequence_num = ++tx_counter_;
        header.payload_len = static_cast<std::uint16_t>(plaintext.size());

        std::array<std::uint8_t, 12> nonce{};
        std::memcpy(nonce.data(), &header.sequence_num, sizeof(header.sequence_num));

        std::memcpy(out_buffer.data(), &header, sizeof(header));

        auto ciphertext_span = out_buffer.subspan(sizeof(SecureHeader), plaintext.size());
        auto tag_span = out_buffer.subspan(sizeof(SecureHeader) + plaintext.size(), TAG_SIZE);

        crypto_aead_encrypt(
            ciphertext_span.data(), tag_span.data(),
            session_key_.data(), nonce.data(),
            reinterpret_cast<const std::uint8_t*>(&header), sizeof(header),
            plaintext.data(), plaintext.size()
        );

        return total_size;
    }

    [[nodiscard]] std::optional<std::size_t> decode_frame(
        std::span<const std::uint8_t> frame_bytes,
        std::span<std::uint8_t> out_plaintext) noexcept 
    {
        if (frame_bytes.size() < sizeof(SecureHeader) + TAG_SIZE) {
            return std::nullopt;
        }

        SecureHeader header{};
        std::memcpy(&header, frame_bytes.data(), sizeof(header));

        if (header.magic != SECURE_FRAME_MAGIC) {
            return std::nullopt;
        }

        const std::size_t expected_payload_len = header.payload_len;
        if (frame_bytes.size() != sizeof(SecureHeader) + expected_payload_len + TAG_SIZE) {
            return std::nullopt;
        }

        // Захист від атак повторного відтворення (Replay Attack)
        if (header.sequence_num <= rx_last_counter_) {
            return std::nullopt;
        }

        if (out_plaintext.size() < expected_payload_len) {
            return std::nullopt;
        }

        std::array<std::uint8_t, 12> nonce{};
        std::memcpy(nonce.data(), &header.sequence_num, sizeof(header.sequence_num));

        auto ciphertext_span = frame_bytes.subspan(sizeof(SecureHeader), expected_payload_len);
        auto received_tag_span = frame_bytes.subspan(sizeof(SecureHeader) + expected_payload_len, TAG_SIZE);

        std::array<std::uint8_t, TAG_SIZE> calculated_tag{};
        std::array<std::uint8_t, MAX_PAYLOAD_SIZE> dummy_buffer{};

        crypto_aead_encrypt(
            dummy_buffer.data(), calculated_tag.data(),
            session_key_.data(), nonce.data(),
            reinterpret_cast<const std::uint8_t*>(&header), sizeof(header),
            ciphertext_span.data(), expected_payload_len
        );

        // ПЕРЕВІРКА В КОНСТАНТНОМУ ЧАСІ
        if (!crypto_verify_ct(calculated_tag, received_tag_span)) {
            return std::nullopt; // Тег недійсний — кадр відхилено без розшифрування
        }

        crypto_aead_decrypt(
            out_plaintext.data(),
            session_key_.data(), nonce.data(),
            reinterpret_cast<const std::uint8_t*>(&header), sizeof(header),
            ciphertext_span.data(), expected_payload_len
        );

        rx_last_counter_ = header.sequence_num;
        return expected_payload_len;
    }

private:
    std::array<std::uint8_t, 32> session_key_{};
    std::uint32_t tx_counter_{0};
    std::uint32_t rx_last_counter_{0};
};

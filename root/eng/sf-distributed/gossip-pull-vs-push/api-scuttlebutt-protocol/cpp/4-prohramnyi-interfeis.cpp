#include <expected>
#include <memory>
#include <string_view>

enum class ScuttlebuttError {
    TruncatedPayload,
    ChecksumMismatch,
    UnsupportedVersion,
    BufferOverflow
};

class IScuttlebuttEngine {
public:
    virtual ~IScuttlebuttEngine() = default;

    /* Формування первинного повідомлення SYN (Крок 1) */
    virtual std::expected<std::vector<uint8_t>, ScuttlebuttError> build_syn(
        uint32_t self_id,
        std::span<const DigestEntry> local_digests
    ) = 0;

    /* Обробка SYN на стороні відповідача та формування ACK (Крок 2) */
    virtual std::expected<std::vector<uint8_t>, ScuttlebuttError> process_syn_build_ack(
        uint32_t self_id,
        std::span<const uint8_t> syn_payload,
        std::span<const DigestEntry> local_digests
    ) = 0;

    /* Обробка ACK на стороні ініціатора та формування ACK2 (Крок 3) */
    virtual std::expected<std::vector<uint8_t>, ScuttlebuttError> process_ack_build_ack2(
        uint32_t self_id,
        std::span<const uint8_t> ack_payload
    ) = 0;

    /* Застосування фінального повідомлення ACK2 відповідачем */
    virtual std::expected<void, ScuttlebuttError> apply_ack2(
        uint32_t self_id,
        std::span<const uint8_t> ack2_payload
    ) = 0;
};

#ifndef FIAT_SHAMIR_TRANSCRIPT_HPP
#define FIAT_SHAMIR_TRANSCRIPT_HPP

#include <span>
#include <string_view>
#include <vector>
#include <array>
#include <expected>
#include <cstdint>

namespace crypto::fiat_shamir {

enum class TranscriptError {
    InvalidParameter,
    StateCorrupted,
    SequenceMismatch
};

class Transcript {
public:
    explicit Transcript(std::string_view protocol_label) noexcept;
    ~Transcript() noexcept;

    Transcript(const Transcript&) = delete;
    Transcript& operator=(const Transcript&) = delete;
    Transcript(Transcript&&) noexcept = default;
    Transcript& operator=(Transcript&&) noexcept = default;

    /**
     * @brief Додати публічний контекст або комітмент до транскрипту.
     */
    std::expected<void, TranscriptError> absorb(
        std::string_view label,
        std::span<const uint8_t> data
    ) noexcept;

    /**
     * @brief Згенерувати випадковий виклик фіксованої довжини.
     */
    template <size_t N>
    std::expected<std::array<uint8_t, N>, TranscriptError> squeeze(
        std::string_view label
    ) noexcept;

    /**
     * @brief Згенерувати скалярний виклик у формі вектору байтів.
     */
    std::expected<std::vector<uint8_t>, TranscriptError> squeeze_bytes(
        std::string_view label,
        size_t count
    ) noexcept;

private:
    std::array<uint8_t, 32> state_{0};
    uint64_t counter_{0};
    bool initialized_{false};

    void update_hash(std::span<const uint8_t> input) noexcept;
};

} // namespace crypto::fiat_shamir

#endif // FIAT_SHAMIR_TRANSCRIPT_HPP

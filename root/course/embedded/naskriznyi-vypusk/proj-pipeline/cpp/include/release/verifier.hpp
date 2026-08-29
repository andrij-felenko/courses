// Криптографічні ворота завантажувача. Контексти mbedTLS живуть під RAII,
// тож жодна гілка виходу не забуває їх звільнити.
#pragma once

#include <functional>

#include "release/header.hpp"

namespace release {

class Verifier {
public:
    // Гладити сторожовий таймер між блоками хешування.
    using WatchdogKick = std::function<void()>;

    Verifier(std::span<const std::uint8_t> rootPublicKey,
             WatchdogKick watchdogKick = {}) noexcept;

    // Структура → хеш тіла → підпис. Усі троє або жодного.
    [[nodiscard]] std::expected<ImageView, Error> verify(
        std::span<const std::uint8_t> image, const Policy& policy) const;

private:
    using Digest = std::array<std::uint8_t, kDigestSize>;

    [[nodiscard]] std::expected<Digest, Error> sha256(
        std::span<const std::uint8_t> head,
        std::span<const std::uint8_t> tail) const;

    [[nodiscard]] std::expected<void, Error> checkSignature(
        const Digest& digest,
        std::span<const std::uint8_t, kSignatureSize> signature) const;

    void kick() const;

    std::span<const std::uint8_t> rootKey_;
    WatchdogKick watchdogKick_;
};

}  // namespace release

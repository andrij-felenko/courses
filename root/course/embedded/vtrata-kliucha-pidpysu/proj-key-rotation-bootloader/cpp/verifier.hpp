#pragma once

#include <cstdint>
#include <expected>
#include <span>

#include "boot_status.hpp"
#include "efuse.hpp"
#include "manifest.hpp"

namespace boot {

// Віддає mbedTLS статичний пул пам'яті замість купи. Викликати один раз,
// до першої перевірки образу.
void initCryptoArena() noexcept;

// Порівняння за сталий час: завжди проходить усі байти, накопичуючи різницю
// через XOR. Час виконання не залежить від позиції розбіжності, тож
// вимірювання осцилографом не видає зловмиснику еталонний хеш побайтово.
[[nodiscard]] constexpr bool constantTimeEqual(std::span<const std::uint8_t> a,
                                               std::span<const std::uint8_t> b) noexcept
{
    if (a.size() != b.size()) {
        return false;
    }

    std::uint8_t difference = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        difference |= static_cast<std::uint8_t>(a[i] ^ b[i]);
    }

    return difference == 0;
}

// Ланцюг перевірок образу. Тіньова копія перемичок прив'язана до об'єкта:
// один корінь довіри на весь прогін завантажувача.
class SecureBootVerifier {
public:
    explicit SecureBootVerifier(const EfuseMirror& efuse) noexcept : efuse_{efuse} {}

    // Кроки: відкликання слота → звірка з коренем довіри → анти-відкат →
    // математична перевірка підпису над заголовком і тілом.
    [[nodiscard]] std::expected<void, Status>
    verify(const Manifest& manifest, std::span<const std::uint8_t> payload) const noexcept;

private:
    const EfuseMirror& efuse_;
};

} // namespace boot

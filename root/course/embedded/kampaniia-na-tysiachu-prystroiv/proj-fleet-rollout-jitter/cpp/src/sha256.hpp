// SHA-256 для номера когорти й дайджесту образу.
// На кристалі з блоком HASH клас замінюється драйвером прискорювача — інтерфейс
// лишається той самий.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace fleet {

class Sha256 {
public:
    using Digest = std::array<std::byte, 32>;

    void update(std::span<const std::byte> data) noexcept;
    [[nodiscard]] Digest finish() noexcept;

    // Разовий підрахунок над кількома частинами: саме так рахується
    // hw_id || campaign_salt, без склеювання їх у проміжний буфер.
    [[nodiscard]] static Digest of(std::span<const std::byte> first,
                                   std::span<const std::byte> second = {}) noexcept;

private:
    void compress(const std::byte* block) noexcept;

    std::array<std::uint32_t, 8> h_{0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                                    0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
    std::array<std::byte, 64> buf_{};
    std::size_t buffered_{0};
    std::uint64_t bits_{0};
};

} // namespace fleet

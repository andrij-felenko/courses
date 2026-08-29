#pragma once

// Потоковий SHA-256. Потоковий принципово: образ на кілька мегабайтів
// у SRAM не влазить, тому хеш усього образу накопичується по секторах,
// поки вони летять на Flash.

#include <array>
#include <cstdint>
#include <span>

namespace upkg {

class Sha256 {
public:
    static constexpr std::size_t kDigestSize = 32;
    static constexpr std::size_t kBlockSize = 64;

    using Digest = std::array<std::uint8_t, kDigestSize>;

    Sha256() = default;

    void update(std::span<const std::uint8_t> data) noexcept;

    // Завершує обчислення й очищає стан: далі об'єкт непридатний.
    [[nodiscard]] Digest finish() noexcept;

    // Разовий хеш одного сектора — ним звіряють чанк із таблицею.
    [[nodiscard]] static Digest of(std::span<const std::uint8_t> data) noexcept {
        Sha256 h;
        h.update(data);
        return h.finish();
    }

private:
    void compress(const std::uint8_t* block) noexcept;

    std::array<std::uint32_t, 8> state_{
        0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
        0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
    std::array<std::uint8_t, kBlockSize> block_{};
    std::uint64_t bit_len_ = 0;
    std::size_t fill_ = 0;
};

}  // namespace upkg

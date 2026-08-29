#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace secure {

/*
 * Затирання секрету на виході зі скоупа. Замість того щоб пам'ятати про
 * ручне прибирання в кожній гілці виходу, вішаємо страж на буфер один раз:
 * деструктор відпрацює й на ранньому return, і на будь-якій новій гілці,
 * яку хтось допише через рік.
 */
class ScopedWipe {
public:
    explicit ScopedWipe(std::span<std::uint8_t> secret) noexcept : secret_(secret) {}
    ~ScopedWipe() noexcept { wipe(secret_); }

    ScopedWipe(const ScopedWipe&) = delete;
    ScopedWipe& operator=(const ScopedWipe&) = delete;

    /* volatile не дає компілятору викинути запис у буфер, який далі не читають. */
    static void wipe(std::span<std::uint8_t> data) noexcept {
        for (auto& byte : data) {
            const_cast<volatile std::uint8_t&>(byte) = 0;
        }
    }

private:
    std::span<std::uint8_t> secret_;
};

/*
 * Потокове SHA-256. Стан живе в самому обʼєкті — ні динамічної памʼяті, ні
 * глобальних буферів, тож два завдання RTOS рахують хеш паралельно.
 * Деструктор затирає стан: у ньому лишався б слід ключа.
 */
class Sha256 {
public:
    static constexpr std::size_t kDigestSize = 32;
    static constexpr std::size_t kBlockSize  = 64;
    using Digest = std::array<std::uint8_t, kDigestSize>;

    Sha256() noexcept { reset(); }
    ~Sha256() noexcept;

    /* Копія контексту — це друга копія секретного стану. Забороняємо. */
    Sha256(const Sha256&) = delete;
    Sha256& operator=(const Sha256&) = delete;

    void reset() noexcept;
    void update(std::span<const std::uint8_t> data) noexcept;
    [[nodiscard]] Digest finish() noexcept;

    [[nodiscard]] static Digest hash(std::span<const std::uint8_t> data) noexcept;

private:
    void compress(const std::uint8_t* block) noexcept;

    std::array<std::uint32_t, 8> h_{};
    std::array<std::uint8_t, kBlockSize> buf_{};
    std::uint64_t total_len_{0};
    std::size_t   buf_len_{0};
};

/* HMAC-SHA256 за RFC 2104: коротший ключ доповнюємо нулями до блоку,
 * довший за 64 байти спершу згортаємо хешем. */
[[nodiscard]] Sha256::Digest hmac_sha256(std::span<const std::uint8_t> key,
                                         std::span<const std::uint8_t> msg) noexcept;

}  // namespace secure

#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <string_view>

#include "platform.hpp"

namespace prov {

using platform::KeySize;
using platform::NonceSize;
using platform::ProofSize;
using platform::SaltSize;
using platform::TagSize;

inline constexpr std::size_t MaxPopLen = 32;

void secure_wipe(std::span<std::uint8_t> bytes) noexcept;

/*
 * Порівняння за константний час. std::equal і memcmp виходять на першому
 * незбіжному байті, і час відповіді BLE-пакета видає, скільки байтів
 * PIN-коду вгадано. Довжина — величина публічна, її порівнюємо звичайно.
 */
[[nodiscard]] bool constant_time_equal(std::span<const std::uint8_t> a,
                                       std::span<const std::uint8_t> b) noexcept;

/*
 * Буфер із секретом, який затирає себе сам. Копіювати заборонено:
 * друга копія ключа на стеку — це другий шанс його звідти вичитати.
 */
template <std::size_t N>
class Secret {
public:
    Secret() = default;
    ~Secret() { wipe(); }

    Secret(const Secret&) = delete;
    Secret& operator=(const Secret&) = delete;

    [[nodiscard]] std::span<const std::uint8_t, N> bytes() const noexcept { return data_; }
    [[nodiscard]] std::span<std::uint8_t, N> mutable_bytes() noexcept { return data_; }

    void wipe() noexcept { secure_wipe(data_); }

private:
    std::array<std::uint8_t, N> data_{};
};

using PublicKey = std::array<std::uint8_t, KeySize>;
using Salt = std::array<std::uint8_t, SaltSize>;

// Суцільні нулі, суцільні одиниці й точки малого порядку (1, 2, 4, 8) — геть.
[[nodiscard]] bool public_key_acceptable(std::span<const std::uint8_t, KeySize> pub) noexcept;

// Маскування бітів скаляра (clamping) за RFC 7748 §5.
void clamp_scalar(std::span<std::uint8_t, KeySize> priv) noexcept;

// Ефемерна пара: випадковий скаляр → clamping → публічний ключ.
void generate_keypair(Secret<KeySize>& priv, PublicKey& pub);

/*
 * Доказ володіння: клієнт надсилає HMAC-SHA256(pop, client_pub).
 * Знати PoP — означає бачити наліпку на корпусі.
 */
[[nodiscard]] bool pop_proof_valid(std::string_view pop,
                                   std::span<const std::uint8_t, KeySize> client_pub,
                                   std::span<const std::uint8_t, ProofSize> proof);

// ECDH + HKDF-SHA256: спільний секрет → сесійний ключ AES-256-GCM.
[[nodiscard]] bool derive_session_key(const Secret<KeySize>& our_priv,
                                      std::span<const std::uint8_t, KeySize> client_pub,
                                      std::span<const std::uint8_t, KeySize> device_pub,
                                      std::span<const std::uint8_t, SaltSize> salt,
                                      std::string_view pop,
                                      Secret<KeySize>& out_key);

}  // namespace prov

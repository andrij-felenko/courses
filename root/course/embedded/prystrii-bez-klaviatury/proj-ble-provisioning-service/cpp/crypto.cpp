#include "crypto.hpp"

#include <algorithm>
#include <cstring>
#include <vector>

namespace prov {
namespace {

/*
 * Точки малого порядку Curve25519 (порядок 1, 2, 4 і 8) плюс канонічні
 * представлення p-1, p, p+1. Спільний секрет із такою точкою вироджується,
 * і атакуючий наперед знає ключ сесії.
 */
constexpr std::array<std::array<std::uint8_t, KeySize>, 7> kSmallOrder{{
    // 0 — порядок 4
    {},
    // 1 — порядок 1
    {0x01},
    // порядок 8
    {0xe0, 0xeb, 0x7a, 0x7c, 0x3b, 0x41, 0xb8, 0xae, 0x16, 0x56, 0xe3,
     0xfa, 0xf1, 0x9f, 0xc4, 0x6a, 0xda, 0x09, 0x8d, 0xeb, 0x9c, 0x32,
     0xb1, 0xfd, 0x86, 0x62, 0x05, 0x16, 0x5f, 0x49, 0xb8, 0x00},
    // порядок 8
    {0x5f, 0x9c, 0x95, 0xbc, 0xa3, 0x50, 0x8c, 0x24, 0xb1, 0xd0, 0xb1,
     0x55, 0x9c, 0x83, 0xef, 0x5b, 0x04, 0x44, 0x5c, 0xc4, 0x58, 0x1c,
     0x8e, 0x86, 0xd8, 0x22, 0x4e, 0xdd, 0xd0, 0x9f, 0x11, 0x57},
    // p-1 — порядок 2
    {0xec, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
     0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
     0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f},
    // p — порядок 4
    {0xed, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
     0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
     0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f},
    // p+1 — порядок 1
    {0xee, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
     0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
     0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f},
}};

constexpr std::string_view kLabel = "prov-v1-aes256gcm";

[[nodiscard]] bool is_small_order(std::span<const std::uint8_t, KeySize> pub) noexcept
{
    std::uint8_t hit = 0;
    for (const auto& point : kSmallOrder) {
        std::uint8_t diff = 0;
        for (std::size_t i = 0; i + 1 < KeySize; ++i) {
            diff |= static_cast<std::uint8_t>(pub[i] ^ point[i]);
        }
        // Старший біт u-координати ігнорується (RFC 7748 §5): без цього
        // та сама точка з піднятим бітом пройшла б повз таблицю.
        diff |= static_cast<std::uint8_t>((pub[KeySize - 1] & 0x7F) ^ point[KeySize - 1]);
        hit |= static_cast<std::uint8_t>((static_cast<std::uint32_t>(diff) - 1u) >> 31);
    }
    return hit != 0;
}

std::span<const std::uint8_t> as_bytes_view(std::string_view text) noexcept
{
    return {reinterpret_cast<const std::uint8_t*>(text.data()), text.size()};
}

}  // namespace

void secure_wipe(std::span<std::uint8_t> bytes) noexcept
{
    // volatile тримає запис живим: інакше оптимізатор викине його як мертвий.
    volatile std::uint8_t* p = bytes.data();
    for (std::size_t i = 0; i < bytes.size(); ++i) {
        p[i] = 0;
    }
}

bool constant_time_equal(std::span<const std::uint8_t> a,
                         std::span<const std::uint8_t> b) noexcept
{
    if (a.size() != b.size()) {
        return false;
    }
    std::uint8_t diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<std::uint8_t>(a[i] ^ b[i]);
    }
    return diff == 0;
}

bool public_key_acceptable(std::span<const std::uint8_t, KeySize> pub) noexcept
{
    std::uint8_t any_bit = 0x00;
    std::uint8_t all_bits = 0xFF;
    for (std::uint8_t byte : pub) {
        any_bit |= byte;
        all_bits &= byte;
    }
    if (any_bit == 0x00 || all_bits == 0xFF) {
        return false;   // суцільні нулі або суцільні одиниці
    }
    return !is_small_order(pub);
}

void clamp_scalar(std::span<std::uint8_t, KeySize> priv) noexcept
{
    priv[0] &= 248;              // три молодші біти геть — кофактор h = 8
    priv[KeySize - 1] &= 127;    // старший біт u-координати не наш
    priv[KeySize - 1] |= 64;     // фіксуємо порядок скаляра
}

void generate_keypair(Secret<KeySize>& priv, PublicKey& pub)
{
    platform::random_bytes(priv.mutable_bytes());
    clamp_scalar(priv.mutable_bytes());
    platform::x25519_public(priv.bytes(), std::span<std::uint8_t, KeySize>(pub));
}

bool pop_proof_valid(std::string_view pop,
                     std::span<const std::uint8_t, KeySize> client_pub,
                     std::span<const std::uint8_t, ProofSize> proof)
{
    Secret<ProofSize> expected;
    platform::hmac_sha256(as_bytes_view(pop), client_pub, expected.mutable_bytes());
    return constant_time_equal(expected.bytes(), proof);
}

bool derive_session_key(const Secret<KeySize>& our_priv,
                        std::span<const std::uint8_t, KeySize> client_pub,
                        std::span<const std::uint8_t, KeySize> device_pub,
                        std::span<const std::uint8_t, SaltSize> salt,
                        std::string_view pop,
                        Secret<KeySize>& out_key)
{
    if (pop.size() > MaxPopLen) {
        return false;
    }

    Secret<KeySize> shared;
    if (!platform::x25519(our_priv.bytes(), client_pub, shared.mutable_bytes())) {
        return false;
    }

    // RFC 7748 §6.1: нульовий спільний секрет означає, що точка малого
    // порядку все ж прослизнула. Друга лінія оборони після таблиці.
    std::uint8_t any_bit = 0;
    for (std::uint8_t byte : shared.bytes()) {
        any_bit |= byte;
    }
    if (any_bit == 0) {
        return false;
    }

    // info звʼязує ключ із PoP і з обома публічними ключами: підміна
    // будь-якого з них дає інший ключ, і тег GMAC перестане сходитися.
    std::vector<std::uint8_t> info;
    info.reserve(kLabel.size() + pop.size() + 2 * KeySize);
    info.insert(info.end(), kLabel.begin(), kLabel.end());
    info.insert(info.end(), pop.begin(), pop.end());
    info.insert(info.end(), client_pub.begin(), client_pub.end());
    info.insert(info.end(), device_pub.begin(), device_pub.end());

    platform::hkdf_sha256(salt, shared.bytes(), info, out_key.mutable_bytes());
    secure_wipe(info);
    return true;   // shared затирає власний деструктор
}

}  // namespace prov

#pragma once

#include <chrono>
#include <cstdint>
#include <span>
#include <string_view>

/*
 * Контракт порту: усе, чого диспетчер провізіонування вимагає від прошивки.
 * Реалізацію дає конкретна платформа — крипто-бібліотека МК, BLE-стек,
 * драйвер станції Wi-Fi, енергонезалежна памʼять NVS.
 */
namespace prov::platform {

inline constexpr std::size_t KeySize   = 32;
inline constexpr std::size_t SaltSize  = 16;
inline constexpr std::size_t NonceSize = 12;
inline constexpr std::size_t TagSize   = 16;
inline constexpr std::size_t ProofSize = 32;

// --- Апаратне джерело випадковості ---
void random_bytes(std::span<std::uint8_t> out);

// --- Криптографічні примітиви ---
void x25519_public(std::span<const std::uint8_t, KeySize> priv,
                   std::span<std::uint8_t, KeySize> pub);

[[nodiscard]] bool x25519(std::span<const std::uint8_t, KeySize> priv,
                          std::span<const std::uint8_t, KeySize> peer_pub,
                          std::span<std::uint8_t, KeySize> shared);

void hmac_sha256(std::span<const std::uint8_t> key,
                 std::span<const std::uint8_t> message,
                 std::span<std::uint8_t, ProofSize> out);

void hkdf_sha256(std::span<const std::uint8_t> salt,
                 std::span<const std::uint8_t> ikm,
                 std::span<const std::uint8_t> info,
                 std::span<std::uint8_t> okm);

// false — тег GMAC не зійшовся, відкритому тексту вірити не можна.
[[nodiscard]] bool aes_gcm_decrypt(std::span<const std::uint8_t, KeySize> key,
                                   std::span<const std::uint8_t, NonceSize> nonce,
                                   std::span<const std::uint8_t, TagSize> tag,
                                   std::span<const std::uint8_t> ciphertext,
                                   std::span<std::uint8_t> plaintext);

// --- BLE-стек ---
void ble_notify(std::uint16_t char_uuid, std::span<const std::uint8_t> data);
void ble_advertise();
void ble_shutdown();      // радіо геть, RAM стека — застосунку

// --- Станція Wi-Fi: асинхронна, результат приходить подією ---
enum class WifiEvent : std::uint8_t {
    Connected,        // асоціація + DHCP пройшли
    AuthFailed,       // невірний пароль або AUTH_EXPIRED від точки доступу
    NoAccessPoint,    // SSID не знайдено в ефірі
    Timeout           // асоціація не завершилася вчасно
};

void wifi_connect(std::string_view ssid, std::string_view passphrase);
void wifi_stop();

// --- Енергонезалежна памʼять ---
[[nodiscard]] bool nvs_store_credentials(std::string_view ssid, std::string_view passphrase);
// PoP пристрою: рядок із наліпки або QR-коду, зашитий на виробництві.
[[nodiscard]] std::string_view pop_secret();

// --- Час і одноразовий таймер ---
[[nodiscard]] std::chrono::milliseconds uptime();
void timer_once(std::chrono::milliseconds delay, void (*callback)());

}  // namespace prov::platform

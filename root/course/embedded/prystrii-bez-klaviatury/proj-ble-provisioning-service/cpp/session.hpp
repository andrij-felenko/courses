#pragma once

#include <chrono>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string>
#include <string_view>

#include "crypto.hpp"

namespace prov {

inline constexpr std::size_t MaxSsidLen = 32;
inline constexpr std::size_t MaxPassLen = 64;
inline constexpr std::uint8_t MaxPopFailures = 3;
inline constexpr auto LockoutDuration = std::chrono::milliseconds{30'000};

// Запис у prov-session: [client_pub 32][proof 32].
inline constexpr std::size_t SessionRequestSize = KeySize + ProofSize;

enum class Status : std::uint8_t {
    Success = 0,
    InvalidLength,
    CryptoFailure,
    AuthenticationFailed,
    StationTimeout,
    Locked,
    Replay,
    StorageFailure
};

struct WifiCredentials {
    std::string ssid;
    std::string password;
};

// Пароль у std::string себе не затирає — робимо це руками там, де він відпрацював.
void wipe_credentials(WifiCredentials& creds) noexcept;

class ProvisioningSession {
public:
    struct HandshakeResponse {
        PublicKey device_public_key{};
        Salt salt{};
    };

    explicit ProvisioningSession(std::string_view proof_of_possession)
        : pop_{proof_of_possession} {}

    [[nodiscard]] std::expected<HandshakeResponse, Status> handshake(
        std::span<const std::uint8_t> request);

    [[nodiscard]] std::expected<WifiCredentials, Status> decrypt_config(
        std::span<const std::uint8_t> payload);

    // Розрив зʼєднання чи таймаут нагляду: ефемерні ключі геть,
    // блокування за перебір PoP лишається — інакше брутфорс зводився б
    // до перепідключення після кожної спроби.
    void reset() noexcept;

    [[nodiscard]] bool established() const noexcept { return established_; }

private:
    [[nodiscard]] bool locked() noexcept;
    void lock() noexcept;

    std::string_view pop_;

    Secret<KeySize> priv_key_;
    Secret<KeySize> session_key_;
    PublicKey device_pub_{};
    Salt salt_{};
    bool established_{false};

    // Захист від повтору: nonce клієнта — [префікс 4][лічильник BE 8].
    std::array<std::uint8_t, 4> nonce_prefix_{};
    std::optional<std::uint64_t> last_counter_;

    std::uint8_t pop_failures_{0};
    std::optional<std::chrono::milliseconds> locked_until_;
};

}  // namespace prov

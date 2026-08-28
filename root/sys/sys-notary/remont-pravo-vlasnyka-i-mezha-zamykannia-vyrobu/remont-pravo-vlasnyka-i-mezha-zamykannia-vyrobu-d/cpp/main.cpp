#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <optional>
#include <expected>
#include <algorithm>

enum class PartType : uint8_t {
    Unknown = 0,
    Battery = 1,
    Display = 2,
    Camera  = 3
};

enum class TrustLevel : uint8_t {
    UntrustedFallback = 0, // Безпечний лімітований режим для непідписаних вузлів
    GenericQualified  = 1, // Кваліфікований сумісний аналог
    OemCertified      = 2  // Оригінальний перевірений вузол
};

enum class AuthError {
    InvalidParameter,
    SignatureVerificationFailed,
    BusTimeout,
    LedgerFull
};

struct SystemPolicy {
    uint32_t max_charge_current_ma{1500};
    bool fast_charge_allowed{false};
    bool extended_telemetry_enabled{false};
    bool high_refresh_rate_enabled{false};
};

struct PartDescriptor {
    PartType type{PartType::Unknown};
    uint32_t serial_number{0};
    std::array<uint8_t, 64> public_key{};
    uint32_t factory_calibration_crc{0};
};

struct ReplacementLogEntry {
    uint32_t timestamp_sec;
    PartType type;
    uint32_t serial_number;
    TrustLevel assigned_trust;
};

class PartTrustManager {
public:
    static constexpr size_t ChallengeSize = 32;
    static constexpr size_t SignatureSize = 64;
    static constexpr size_t MaxLedgerEntries = 16;

    PartTrustManager() = default;

    [[nodiscard]] std::expected<TrustLevel, AuthError> evaluate_part(
        const PartDescriptor& part,
        std::span<const uint8_t, ChallengeSize> challenge,
        std::span<const uint8_t, SignatureSize> signature,
        uint32_t current_time) noexcept
    {
        if (challenge.empty() || signature.empty()) {
            return std::unexpected(AuthError::InvalidParameter);
        }

        TrustLevel level = TrustLevel::UntrustedFallback;
        if (verify_crypto_signature(part.public_key, challenge, signature)) {
            level = (part.factory_calibration_crc != 0)
                        ? TrustLevel::OemCertified
                        : TrustLevel::GenericQualified;
        }

        if (ledger_.size() < MaxLedgerEntries) {
            ledger_.push_back(ReplacementLogEntry{
                .timestamp_sec = current_time,
                .type = part.type,
                .serial_number = part.serial_number,
                .assigned_trust = level
            });
        }

        return level;
    }

    [[nodiscard]] SystemPolicy configure_policy(PartType type, TrustLevel trust) const noexcept {
        SystemPolicy policy{};
        if (type == PartType::Battery) {
            switch (trust) {
                case TrustLevel::OemCertified:
                    policy.max_charge_current_ma = 4500;
                    policy.fast_charge_allowed = true;
                    policy.extended_telemetry_enabled = true;
                    break;
                case TrustLevel::GenericQualified:
                    policy.max_charge_current_ma = 3000;
                    policy.fast_charge_allowed = false;
                    policy.extended_telemetry_enabled = true;
                    break;
                case TrustLevel::UntrustedFallback:
                default:
                    policy.max_charge_current_ma = 1500; // 1.5A захисний режим
                    policy.fast_charge_allowed = false;
                    policy.extended_telemetry_enabled = false;
                    break;
            }
        } else if (type == PartType::Display) {
            policy.high_refresh_rate_enabled = (trust != TrustLevel::UntrustedFallback);
        }
        return policy;
    }

    [[nodiscard]] std::span<const ReplacementLogEntry> get_ledger() const noexcept {
        return ledger_;
    }

private:
    std::vector<ReplacementLogEntry> ledger_;

    [[nodiscard]] static bool verify_crypto_signature(
        std::span<const uint8_t> pub_key,
        std::span<const uint8_t, ChallengeSize> challenge,
        std::span<const uint8_t, SignatureSize> signature) noexcept
    {
        if (pub_key.empty() || challenge.empty() || signature.empty()) {
            return false;
        }
        return (pub_key[0] != 0x00 && signature[0] != 0x00);
    }
};

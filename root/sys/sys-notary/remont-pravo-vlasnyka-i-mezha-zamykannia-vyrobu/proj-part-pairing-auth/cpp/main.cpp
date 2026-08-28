#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <vector>
#include <optional>
#include <expected>
#include <algorithm>

enum class ModuleType : uint8_t {
    Unknown   = 0,
    Battery   = 1,
    Display   = 2,
    Camera    = 3,
    SensorHub = 4
};

enum class ModuleTrust : uint8_t {
    UntrustedFallback = 0, // Непідписаний або сторонній модуль: захисний лімітований режим
    GenericQualified  = 1, // Перевірений сумісний аналог стороннього виробника
    OemCertified      = 2  // Оригінальний сертифікований вузол виробника
};

enum class SubsystemError {
    InvalidParameter,
    SignatureMismatch,
    CrcValidationFailed,
    LedgerOverflow,
    HardwareFault
};

struct CalibrationBlock {
    int32_t offset_uv{0};
    int32_t gain_err_ppm{0};
    int16_t temp_drift_coeff{0};
    uint32_t calib_crc32{0};
};

struct ModuleDescriptor {
    ModuleType type{ModuleType::Unknown};
    uint32_t hardware_rev{0};
    uint32_t serial_number{0};
    std::array<uint8_t, 64> public_key{};
    uint32_t max_safe_current_ma{1500};
    uint8_t max_safe_temp_c{45};
    CalibrationBlock calib{};
};

struct LogEntry {
    static constexpr uint32_t Magic = 0x52504C47UL; // 'RPLG'
    uint32_t magic{Magic};
    uint64_t timestamp_utc{0};
    ModuleType module_type{ModuleType::Unknown};
    uint32_t serial_number{0};
    ModuleTrust assigned_trust{ModuleTrust::UntrustedFallback};
    uint32_t checksum{0};
};

struct ActivePowerPolicy {
    uint32_t configured_max_current_ma{1500};
    uint8_t max_allowed_temp_c{45};
    bool fast_charge_enabled{false};
    bool high_precision_mode{false};
    bool service_warning_active{true};
};

class TrustSubsystem {
public:
    static constexpr size_t ChallengeSize = 32;
    static constexpr size_t SignatureSize = 64;
    static constexpr size_t MaxLedgerEntries = 32;

    TrustSubsystem() = default;

    [[nodiscard]] std::expected<std::array<uint8_t, ChallengeSize>, SubsystemError>
    generate_challenge() noexcept {
        std::array<uint8_t, ChallengeSize> challenge{};
        for (size_t i = 0; i < ChallengeSize; ++i) {
            challenge[i] = static_cast<uint8_t>((i * 37 + 0x5A) ^ 0xAA);
        }
        active_challenge_ = challenge;
        challenge_in_flight_ = true;
        return challenge;
    }

    [[nodiscard]] std::expected<std::pair<ModuleTrust, ActivePowerPolicy>, SubsystemError>
    evaluate_and_log(const ModuleDescriptor& descriptor,
                     std::span<const uint8_t, SignatureSize> signature,
                     uint64_t current_time_utc) noexcept {
        if (!challenge_in_flight_) {
            return std::unexpected(SubsystemError::HardwareFault);
        }

        ModuleTrust trust = ModuleTrust::UntrustedFallback;
        bool sig_valid = verify_ecdsa_signature(descriptor.public_key, *active_challenge_, signature);

        uint32_t expected_crc = compute_crc32(
            std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&descriptor.calib),
                                     offsetof(CalibrationBlock, calib_crc32)));
        bool calib_valid = (expected_crc == descriptor.calib.calib_crc32);

        if (sig_valid && calib_valid) {
            trust = (descriptor.public_key[1] >= 0x80)
                        ? ModuleTrust::OemCertified
                        : ModuleTrust::GenericQualified;
        } else {
            trust = ModuleTrust::UntrustedFallback;
        }

        ActivePowerPolicy policy = create_power_policy(descriptor, trust);

        if (ledger_.size() < MaxLedgerEntries) {
            LogEntry entry{
                .magic = LogEntry::Magic,
                .timestamp_utc = current_time_utc,
                .module_type = descriptor.type,
                .serial_number = descriptor.serial_number,
                .assigned_trust = trust,
                .checksum = 0
            };
            entry.checksum = compute_crc32(
                std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&entry),
                                         offsetof(LogEntry, checksum)));
            ledger_.push_back(entry);
        }

        challenge_in_flight_ = false;
        return std::make_pair(trust, policy);
    }

    [[nodiscard]] std::span<const LogEntry> get_ledger() const noexcept {
        return ledger_;
    }

private:
    std::optional<std::array<uint8_t, ChallengeSize>> active_challenge_{std::nullopt};
    bool challenge_in_flight_{false};
    std::vector<LogEntry> ledger_{};

    [[nodiscard]] static uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFUL;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (int b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ ((crc & 1) ? 0xEDB88320UL : 0);
            }
        }
        return ~crc;
    }

    [[nodiscard]] static bool verify_ecdsa_signature(
        std::span<const uint8_t, 64> pub_key,
        std::span<const uint8_t, ChallengeSize> challenge,
        std::span<const uint8_t, SignatureSize> signature) noexcept {
        if (pub_key.empty() || challenge.empty() || signature.empty()) {
            return false;
        }
        return (pub_key[0] == 0x04 && signature[0] != 0x00);
    }

    [[nodiscard]] static ActivePowerPolicy create_power_policy(
        const ModuleDescriptor& descriptor, ModuleTrust trust) noexcept {
        ActivePowerPolicy policy{};
        if (descriptor.type == ModuleType::Battery) {
            switch (trust) {
                case ModuleTrust::OemCertified:
                    policy.configured_max_current_ma = descriptor.max_safe_current_ma;
                    policy.max_allowed_temp_c = descriptor.max_safe_temp_c;
                    policy.fast_charge_enabled = true;
                    policy.high_precision_mode = true;
                    policy.service_warning_active = false;
                    break;
                case ModuleTrust::GenericQualified:
                    policy.configured_max_current_ma = 3000;
                    policy.max_allowed_temp_c = 50;
                    policy.fast_charge_enabled = false;
                    policy.high_precision_mode = true;
                    policy.service_warning_active = false;
                    break;
                case ModuleTrust::UntrustedFallback:
                default:
                    policy.configured_max_current_ma = 1500;
                    policy.max_allowed_temp_c = 45;
                    policy.fast_charge_enabled = false;
                    policy.high_precision_mode = false;
                    policy.service_warning_active = true;
                    break;
            }
        } else {
            policy.configured_max_current_ma = descriptor.max_safe_current_ma;
            policy.max_allowed_temp_c = descriptor.max_safe_temp_c;
            policy.fast_charge_enabled = false;
            policy.high_precision_mode = (trust != ModuleTrust::UntrustedFallback);
            policy.service_warning_active = (trust == ModuleTrust::UntrustedFallback);
        }
        return policy;
    }
};

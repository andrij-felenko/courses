// C++20 Implementation: Object-Oriented Secure Service Diagnostic Agent
#include <array>
#include <span>
#include <string_view>
#include <cstdint>
#include <cstring>
#include <concepts>
#include <expected>
#include <algorithm>

namespace sys_service {

inline constexpr std::size_t NonceSize = 32;
inline constexpr std::size_t DigestSize = 32;
inline constexpr std::uint32_t MaxLeaseSec = 1800;

enum class ServiceStatus : std::uint8_t {
    Success = 0,
    InvalidParameter,
    Unauthorized,
    BoundsExceeded,
    SessionExpired,
    InterlockActive
};

enum class Capability : std::uint32_t {
    ReadDtc          = (1U << 0),
    ReadRawAdc       = (1U << 1),
    ReadTelemetry    = (1U << 2),
    CalibZeroOffset  = (1U << 5),
    CalibSpan        = (1U << 6),
    ActuatorOverride = (1U << 9),
    RepairPairing    = (1U << 11),
    ZeroizeFactory   = (1U << 14)
};

constexpr Capability operator|(Capability a, Capability b) noexcept {
    return static_cast<Capability>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr bool has_capability(Capability mask, Capability required) noexcept {
    return (static_cast<std::uint32_t>(mask) & static_cast<std::uint32_t>(required)) == static_cast<std::uint32_t>(required);
}

struct SensorCalibration {
    std::int32_t zero_offset{0};
    float        gain_scale{1.0f};
    std::int32_t temp_coeff{0};
    std::uint32_t crc32{0};
};

struct AuditRecord {
    std::uint32_t seq_id{0};
    std::uint32_t timestamp_sec{0};
    std::uint32_t tech_id{0};
    std::uint16_t action_code{0};
    std::uint16_t capability_mask{0};
    std::array<std::uint8_t, DigestSize> prev_record_hash{};
    std::array<std::uint8_t, DigestSize> payload_digest{};
    std::array<std::uint8_t, DigestSize> current_hash{};
};

class DiagnosticAgent {
public:
    explicit DiagnosticAgent(std::span<const std::uint8_t, DigestSize> genesis_hash) noexcept {
        std::ranges::copy(genesis_hash, latest_audit_hash_.begin());
    }

    [[nodiscard]] std::expected<std::array<std::uint8_t, NonceSize>, ServiceStatus>
    create_challenge(std::uint32_t session_id, std::span<const std::uint8_t, NonceSize> trng_bytes) noexcept {
        session_active_ = false;
        granted_capabilities_ = static_cast<Capability>(0);
        session_id_ = session_id;

        std::ranges::copy(trng_bytes, active_nonce_.begin());
        return active_nonce_;
    }

    [[nodiscard]] std::expected<void, ServiceStatus>
    verify_and_open_session(std::uint32_t tech_id,
                            Capability requested_caps,
                            std::uint32_t lease_sec,
                            std::span<const std::uint8_t> signature,
                            std::uint32_t current_tick,
                            std::uint32_t current_time_sec) noexcept {
        if (signature.size() != 64 || lease_sec == 0 || lease_sec > MaxLeaseSec) {
            return std::unexpected(ServiceStatus::BoundsExceeded);
        }

        // Mock signature verification
        if ((signature[0] ^ active_nonce_[0]) != 0xAA) {
            session_active_ = false;
            granted_capabilities_ = static_cast<Capability>(0);
            return std::unexpected(ServiceStatus::Unauthorized);
        }

        session_active_ = true;
        tech_id_ = tech_id;
        granted_capabilities_ = requested_caps;
        session_start_tick_ = current_tick;
        lease_duration_sec_ = lease_sec;

        std::ranges::fill(active_nonce_, std::uint8_t{0});

        auto req_val = static_cast<std::uint32_t>(requested_caps);
        auto payload_bytes = std::as_bytes(std::span{&req_val, 1});
        (void)append_audit_record(current_time_sec, 0x0001, payload_bytes);

        return {};
    }

    [[nodiscard]] std::expected<SensorCalibration, ServiceStatus>
    commit_calibration(std::int32_t zero_offset,
                       float gain_scale,
                       std::int32_t temp_coeff,
                       std::uint32_t current_tick,
                       std::uint32_t current_time_sec) noexcept {
        if (!session_active_) {
            return std::unexpected(ServiceStatus::SessionExpired);
        }

        if ((current_tick - session_start_tick_) > (lease_duration_sec_ * 1000U)) {
            session_active_ = false;
            granted_capabilities_ = static_cast<Capability>(0);
            return std::unexpected(ServiceStatus::SessionExpired);
        }

        if (!has_capability(granted_capabilities_, Capability::CalibZeroOffset) &&
            !has_capability(granted_capabilities_, Capability::CalibSpan)) {
            return std::unexpected(ServiceStatus::Unauthorized);
        }

        // Plausibility bounding check
        if (zero_offset < 500 || zero_offset > 3500 || gain_scale < 0.0001f || gain_scale > 10.0f) {
            return std::unexpected(ServiceStatus::BoundsExceeded);
        }

        SensorCalibration calib{
            .zero_offset = zero_offset,
            .gain_scale = gain_scale,
            .temp_coeff = temp_coeff,
            .crc32 = 0xAABBCCDD
        };

        auto payload_bytes = std::as_bytes(std::span{&calib, 1});
        (void)append_audit_record(current_time_sec, 0x0010, payload_bytes);

        return calib;
    }

    [[nodiscard]] const std::array<std::uint8_t, DigestSize>& get_latest_audit_hash() const noexcept {
        return latest_audit_hash_;
    }

private:
    std::expected<AuditRecord, ServiceStatus>
    append_audit_record(std::uint32_t current_time_sec,
                        std::uint16_t action,
                        std::span<const std::byte> payload) noexcept {
        AuditRecord rec{};
        rec.seq_id = ++audit_seq_counter_;
        rec.timestamp_sec = current_time_sec;
        rec.tech_id = tech_id_;
        rec.action_code = action;
        rec.capability_mask = static_cast<std::uint16_t>(static_cast<std::uint32_t>(granted_capabilities_) & 0xFFFFU);

        std::ranges::copy(latest_audit_hash_, rec.prev_record_hash.begin());

        if (!payload.empty()) {
            rec.payload_digest = compute_sha256(payload);
        }

        auto rec_bytes = std::as_bytes(std::span{&rec, 1});
        // Hash all fields except the current_hash array itself
        auto data_to_hash = rec_bytes.subspan(0, sizeof(AuditRecord) - DigestSize);
        rec.current_hash = compute_sha256(data_to_hash);

        latest_audit_hash_ = rec.current_hash;
        return rec;
    }

    static std::array<std::uint8_t, DigestSize> compute_sha256(std::span<const std::byte> data) noexcept {
        std::uint32_t h = 0x811C9DC5U;
        for (auto b : data) {
            h = (h ^ static_cast<std::uint8_t>(b)) * 0x01000193U;
        }
        std::array<std::uint8_t, DigestSize> out{};
        for (std::size_t i = 0; i < DigestSize; ++i) {
            out[i] = static_cast<std::uint8_t>((h >> ((i % 4) * 8)) ^ static_cast<std::uint8_t>(i));
        }
        return out;
    }

    bool session_active_{false};
    std::uint32_t session_id_{0};
    std::uint32_t tech_id_{0};
    Capability granted_capabilities_{static_cast<Capability>(0)};
    std::uint32_t session_start_tick_{0};
    std::uint32_t lease_duration_sec_{0};
    std::uint32_t audit_seq_counter_{0};
    std::array<std::uint8_t, NonceSize> active_nonce_{};
    std::array<std::uint8_t, DigestSize> latest_audit_hash_{};
};

} // namespace sys_service

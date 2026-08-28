#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <chrono>
#include <expected>

namespace safety {

constexpr float MaxAllowedForceN = 150.0f;
constexpr float MaxAllowedVelocityMps = 1.2f;
constexpr std::chrono::milliseconds MaxTokenTtl{300};
constexpr std::size_t AuditCapacity = 128;

enum class InterlockError : std::uint8_t {
    TokenExpired,
    TokenInvalidSignature,
    PermissionDenied,
    ForceLimitExceeded,
    VelocityLimitExceeded,
    EStopTriggered,
    AuditLogFull
};

enum class PermissionFlags : std::uint32_t {
    None           = 0x00,
    MotionArm      = 0x01,
    ToolActivate   = 0x02,
    OverrideSpeed  = 0x04
};

constexpr PermissionFlags operator|(PermissionFlags a, PermissionFlags b) noexcept {
    return static_cast<PermissionFlags>(static_cast<std::uint32_t>(a) | static_cast<std::uint32_t>(b));
}

constexpr bool has_flag(PermissionFlags mask, PermissionFlags flag) noexcept {
    return (static_cast<std::uint32_t>(mask) & static_cast<std::uint32_t>(flag)) == static_cast<std::uint32_t>(flag);
}

struct OperatorToken {
    std::uint32_t operator_id{0};
    PermissionFlags permissions{PermissionFlags::None};
    std::chrono::milliseconds timestamp{0};
    std::chrono::milliseconds ttl{0};
    std::uint32_t signature_crc32{0};

    [[nodiscard]] std::uint32_t compute_crc() const noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        auto bytes = std::as_bytes(std::span{this, 1});
        for (std::size_t i = 0; i < bytes.size() - sizeof(signature_crc32); ++i) {
            crc ^= static_cast<std::uint8_t>(bytes[i]);
            for (int b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<std::int32_t>(crc & 1U))));
            }
        }
        return ~crc;
    }
};

struct ActuationProposal {
    std::uint32_t action_id{0};
    PermissionFlags required_permission{PermissionFlags::None};
    float requested_force_n{0.0f};
    float requested_velocity_mps{0.0f};
    float ml_confidence{0.0f};
    std::uint32_t model_weights_hash{0};
};

struct AuditRecord {
    std::chrono::milliseconds log_time{0};
    std::uint32_t action_id{0};
    std::uint32_t operator_id{0};
    float applied_force_n{0.0f};
    float ml_confidence{0.0f};
};

class SafetyInterlock {
public:
    constexpr SafetyInterlock() noexcept = default;

    [[nodiscard]] std::expected<void, InterlockError> evaluate(
        const ActuationProposal& proposal,
        const OperatorToken& token,
        std::chrono::milliseconds current_time,
        bool hardware_estop_pin_active
    ) noexcept {
        if (!hardware_estop_pin_active) {
            return std::unexpected(InterlockError::EStopTriggered);
        }

        if (token.compute_crc() != token.signature_crc32) {
            return std::unexpected(InterlockError::TokenInvalidSignature);
        }

        const auto elapsed = current_time - token.timestamp;
        if (elapsed > token.ttl || token.ttl > MaxTokenTtl || elapsed < std::chrono::milliseconds{0}) {
            return std::unexpected(InterlockError::TokenExpired);
        }

        if (!has_flag(token.permissions, proposal.required_permission)) {
            return std::unexpected(InterlockError::PermissionDenied);
        }

        if (proposal.requested_force_n > MaxAllowedForceN || proposal.requested_force_n < 0.0f) {
            return std::unexpected(InterlockError::ForceLimitExceeded);
        }

        if (proposal.requested_velocity_mps > MaxAllowedVelocityMps || proposal.requested_velocity_mps < 0.0f) {
            return std::unexpected(InterlockError::VelocityLimitExceeded);
        }

        if (log_count_ >= AuditCapacity) {
            return std::unexpected(InterlockError::AuditLogFull);
        }

        audit_log_[log_count_++] = AuditRecord{
            .log_time = current_time,
            .action_id = proposal.action_id,
            .operator_id = token.operator_id,
            .applied_force_n = proposal.requested_force_n,
            .ml_confidence = proposal.ml_confidence
        };

        return {};
    }

    [[nodiscard]] std::span<const AuditRecord> get_audit_records() const noexcept {
        return std::span<const AuditRecord>(audit_log_.data(), log_count_);
    }

private:
    std::array<AuditRecord, AuditCapacity> audit_log_{};
    std::size_t log_count_{0};
};

} // namespace safety

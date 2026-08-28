#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <chrono>
#include <expected>

namespace audit {

constexpr std::size_t MaxFeaturesDim = 16;

enum class AuditError : std::uint8_t {
    InvalidInput,
    FeaturesOverflow,
    StorageFailure
};

struct DecisionAuditRecord {
    std::chrono::microseconds timestamp{0};
    std::uint32_t model_hash_crc32{0};
    std::uint32_t operator_id{0};
    std::uint16_t action_code{0};
    float confidence_score{0.0f};
    float threshold_used{0.0f};
    std::array<float, MaxFeaturesDim> input_features{};
    std::uint32_t record_checksum{0};

    [[nodiscard]] std::uint32_t compute_checksum() const noexcept {
        std::uint32_t crc = 0xFFFFFFFFU;
        auto bytes = std::as_bytes(std::span{this, 1});
        for (std::size_t i = 0; i < bytes.size() - sizeof(record_checksum); ++i) {
            crc ^= static_cast<std::uint8_t>(bytes[i]);
            for (int b = 0; b < 8; ++b) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(static_cast<std::int32_t>(crc & 1U))));
            }
        }
        return ~crc;
    }
};

class AuditLogger {
public:
    [[nodiscard]] static std::expected<DecisionAuditRecord, AuditError> create_record(
        std::chrono::microseconds timestamp,
        std::uint32_t model_hash,
        std::uint32_t operator_id,
        std::uint16_t action_code,
        float confidence,
        float threshold,
        std::span<const float> features
    ) noexcept {
        if (features.size() > MaxFeaturesDim) {
            return std::unexpected(AuditError::FeaturesOverflow);
        }

        DecisionAuditRecord rec{
            .timestamp = timestamp,
            .model_hash_crc32 = model_hash,
            .operator_id = operator_id,
            .action_code = action_code,
            .confidence_score = confidence,
            .threshold_used = threshold
        };

        for (std::size_t i = 0; i < features.size(); ++i) {
            rec.input_features[i] = features[i];
        }

        rec.record_checksum = rec.compute_checksum();
        return rec;
    }
};

} // namespace audit

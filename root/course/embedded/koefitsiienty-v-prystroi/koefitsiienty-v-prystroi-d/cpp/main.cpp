#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <concepts>
#include <algorithm>

namespace embedded::calibration {

inline constexpr uint32_t CAL_MAGIC = 0x43414C42U; // 'CALB'
inline constexpr uint16_t CAL_SCHEMA_VERSION = 1U;
inline constexpr size_t CAL_SLOT_COUNT = 2U;

enum class CalFlags : uint16_t {
    None         = 0,
    FactoryValid = 1U << 0,
    UserTared    = 1U << 1,
    Degraded     = 1U << 2
};

enum class CalError : uint8_t {
    StorageIoError,
    CorruptedData,
    DegradedFallback,
    OutOfBounds
};

// Фізичні коефіцієнти аналогового тракту
struct alignas(4) CalibrationPayload {
    float offset_x{0.0f};
    float offset_y{0.0f};
    float offset_z{0.0f};
    float gain_x{1.0f};
    float gain_y{1.0f};
    float gain_z{1.0f};
    float poly_temp_a{0.0f};
    float poly_temp_b{0.0f};
    float poly_temp_c{0.0f};
    float ref_temp_celsius{25.0f};
    uint32_t sensor_serial_id{0};
    uint32_t reserved_zero{0};

    [[nodiscard]] constexpr bool is_sane() const noexcept {
        if (gain_x < 0.5f || gain_x > 1.5f) return false;
        if (gain_y < 0.5f || gain_y > 1.5f) return false;
        if (gain_z < 0.5f || gain_z > 1.5f) return false;
        if (offset_x < -500.0f || offset_x > 500.0f) return false;
        if (offset_y < -500.0f || offset_y > 500.0f) return false;
        if (offset_z < -500.0f || offset_z > 500.0f) return false;
        return true;
    }
};

// Повна бінарна структура блоку у пам'яті
struct alignas(4) CalibrationBlock {
    uint32_t magic{CAL_MAGIC};
    uint16_t schema_version{CAL_SCHEMA_VERSION};
    CalFlags flags{CalFlags::Degraded};
    uint32_t sequence_id{0};
    uint32_t timestamp{0};
    CalibrationPayload data{};
    uint32_t crc32{0};
};

// Compile-time & runtime CRC-32 (IEEE 802.3)
[[nodiscard]] constexpr uint32_t calculate_crc32(std::span<const std::byte> bytes) noexcept {
    uint32_t crc = 0xFFFFFFFFU;
    for (std::byte b : bytes) {
        crc ^= static_cast<uint32_t>(b);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            uint32_t mask = -(static_cast<int32_t>(crc & 1U));
            crc = (crc >> 1) ^ (0xEDB88320U & mask);
        }
    }
    return ~crc;
}

// Концепт носія енергонезалежної пам'яті
template <typename T>
concept StorageDevice = requires(T dev, uint8_t slot, std::span<std::byte> dst, std::span<const std::byte> src) {
    { dev.read_slot(slot, dst) } -> std::same_as<bool>;
    { dev.write_slot(slot, src) } -> std::same_as<bool>;
    { dev.read_otp(dst) } -> std::same_as<bool>;
};

template <StorageDevice Storage>
class CalibrationManager {
public:
    explicit constexpr CalibrationManager(Storage& driver) noexcept : driver_(driver) {}

    [[nodiscard]] std::expected<void, CalError> init() noexcept {
        std::array<CalibrationBlock, CAL_SLOT_COUNT> slots{};
        std::array<bool, CAL_SLOT_COUNT> valid{};

        for (uint8_t i = 0; i < CAL_SLOT_COUNT; ++i) {
            auto span = std::as_writable_bytes(std::span{std::addressof(slots[i]), 1});
            if (driver_.read_slot(i, span)) {
                valid[i] = validate_block(slots[i]);
            }
        }

        if (valid[0] && valid[1]) {
            active_slot_ = (slots[1].sequence_id > slots[0].sequence_id) ? 1 : 0;
            active_block_ = slots[active_slot_];
            is_initialized_ = true;
            return {};
        }
        if (valid[0]) {
            active_slot_ = 0;
            active_block_ = slots[0];
            is_initialized_ = true;
            return {};
        }
        if (valid[1]) {
            active_slot_ = 1;
            active_block_ = slots[1];
            is_initialized_ = true;
            return {};
        }

        // Fallback 1: спроба читання з OTP
        CalibrationBlock otp_block{};
        auto otp_span = std::as_writable_bytes(std::span{std::addressof(otp_block), 1});
        if (driver_.read_otp(otp_span) && validate_block(otp_block)) {
            active_block_ = otp_block;
            active_slot_ = 0;
            is_initialized_ = true;
            is_degraded_ = true;
            return std::unexpected(CalError::DegradedFallback);
        }

        // Fallback 2: номінальні константи за замовчуванням
        active_block_ = CalibrationBlock{};
        active_slot_ = 0;
        is_initialized_ = true;
        is_degraded_ = true;
        return std::unexpected(CalError::DegradedFallback);
    }

    [[nodiscard]] std::expected<void, CalError> update(const CalibrationPayload& payload, uint32_t timestamp) noexcept {
        if (!is_initialized_) return std::unexpected(CalError::StorageIoError);
        if (!payload.is_sane()) return std::unexpected(CalError::OutOfBounds);

        uint8_t target_slot = (active_slot_ == 0) ? 1 : 0;
        CalibrationBlock next_block{
            .magic = CAL_MAGIC,
            .schema_version = CAL_SCHEMA_VERSION,
            .flags = CalFlags::FactoryValid | CalFlags::UserTared,
            .sequence_id = active_block_.sequence_id + 1,
            .timestamp = timestamp,
            .data = payload,
            .crc32 = 0
        };

        // Обчислення CRC32 над областю Header + Payload
        constexpr size_t crc_coverage = offsetof(CalibrationBlock, crc32);
        auto src_bytes = std::as_bytes(std::span{std::addressof(next_block), 1}).subspan(0, crc_coverage);
        next_block.crc32 = calculate_crc32(src_bytes);

        auto full_span = std::as_bytes(std::span{std::addressof(next_block), 1});
        if (!driver_.write_slot(target_slot, full_span)) {
            return std::unexpected(CalError::StorageIoError);
        }

        // Перевірка зворотного читання
        CalibrationBlock readback{};
        auto read_span = std::as_writable_bytes(std::span{std::addressof(readback), 1});
        if (!driver_.read_slot(target_slot, read_span) || !validate_block(readback)) {
            return std::unexpected(CalError::CorruptedData);
        }

        active_block_ = next_block;
        active_slot_ = target_slot;
        is_degraded_ = false;
        return {};
    }

    [[nodiscard]] constexpr const CalibrationPayload& get_payload() const noexcept {
        return active_block_.data;
    }

    [[nodiscard]] constexpr bool is_degraded() const noexcept {
        return is_degraded_;
    }

    [[nodiscard]] static constexpr float apply_axis(float raw, float offset, float gain,
                                                    float poly_a, float poly_b,
                                                    float t_curr, float t_ref) noexcept {
        float dt = t_curr - t_ref;
        float temp_drift = (poly_a * dt * dt) + (poly_b * dt);
        float corrected_offset = offset + temp_drift;
        return (raw - corrected_offset) * gain;
    }

private:
    [[nodiscard]] static bool validate_block(const CalibrationBlock& blk) noexcept {
        if (blk.magic != CAL_MAGIC) return false;
        if (blk.schema_version != CAL_SCHEMA_VERSION) return false;
        
        constexpr size_t crc_coverage = offsetof(CalibrationBlock, crc32);
        auto bytes = std::as_bytes(std::span{std::addressof(blk), 1}).subspan(0, crc_coverage);
        if (calculate_crc32(bytes) != blk.crc32) return false;
        
        return blk.data.is_sane();
    }

    Storage& driver_;
    CalibrationBlock active_block_{};
    uint8_t active_slot_{0};
    bool is_initialized_{false};
    bool is_degraded_{false};
};

} // namespace embedded::calibration

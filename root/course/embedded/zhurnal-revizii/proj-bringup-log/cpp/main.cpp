#include <cstdint>
#include <array>
#include <span>
#include <string_view>
#include <expected>

namespace telemetry {

struct CalibrationPoints {
    static constexpr std::uintptr_t uid_base        = 0x1FFF7A10U;
    static constexpr std::uintptr_t vrefint_cal_ptr = 0x1FFF7A2AU;
    static constexpr std::uintptr_t ts_cal1_ptr     = 0x1FFF7A2CU;
    static constexpr std::uintptr_t ts_cal2_ptr     = 0x1FFF7A2EU;

    static constexpr std::uint32_t cal_vref_mv      = 3300U;
    static constexpr std::int32_t  ts_cal1_temp_c   = 30;
    static constexpr std::int32_t  ts_cal2_temp_c   = 110;
};

struct BoardMetrics {
    std::array<std::uint32_t, 3> uid{};
    std::uint16_t vrefint_cal{0};
    std::uint16_t ts_cal1{0};
    std::uint16_t ts_cal2{0};
    std::uint32_t vdda_mv{0};
    std::int32_t  core_temperature_c{0};
};

enum class TelemetryError : std::uint8_t {
    invalid_raw_adc,
    calibration_corrupted,
    buffer_overflow
};

class TelemetryCollector {
public:
    static BoardMetrics collect_device_identity() noexcept {
        BoardMetrics metrics{};
        const auto* uid_raw = reinterpret_cast<const std::uint32_t*>(CalibrationPoints::uid_base);
        metrics.uid[0] = uid_raw[0];
        metrics.uid[1] = uid_raw[1];
        metrics.uid[2] = uid_raw[2];

        metrics.vrefint_cal = *reinterpret_cast<const std::uint16_t*>(CalibrationPoints::vrefint_cal_ptr);
        metrics.ts_cal1     = *reinterpret_cast<const std::uint16_t*>(CalibrationPoints::ts_cal1_ptr);
        metrics.ts_cal2     = *reinterpret_cast<const std::uint16_t*>(CalibrationPoints::ts_cal2_ptr);
        return metrics;
    }

    static std::expected<BoardMetrics, TelemetryError> process_samples(
        BoardMetrics metrics,
        std::uint16_t raw_vref,
        std::uint16_t raw_temp) noexcept
    {
        if (raw_vref == 0) {
            return std::unexpected(TelemetryError::invalid_raw_adc);
        }

        metrics.vdda_mv = (CalibrationPoints::cal_vref_mv * static_cast<std::uint32_t>(metrics.vrefint_cal)) / raw_vref;

        if (metrics.ts_cal2 <= metrics.ts_cal1) {
            return std::unexpected(TelemetryError::calibration_corrupted);
        }

        const auto num = (static_cast<std::int32_t>(raw_temp) * static_cast<std::int32_t>(metrics.vdda_mv) / 
                          static_cast<std::int32_t>(CalibrationPoints::cal_vref_mv)) - static_cast<std::int32_t>(metrics.ts_cal1);
        const auto den = static_cast<std::int32_t>(metrics.ts_cal2) - static_cast<std::int32_t>(metrics.ts_cal1);
        
        metrics.core_temperature_c = CalibrationPoints::ts_cal1_temp_c + 
            (num * (CalibrationPoints::ts_cal2_temp_c - CalibrationPoints::ts_cal1_temp_c)) / den;

        return metrics;
    }

    static std::expected<std::size_t, TelemetryError> serialize_json(
        const BoardMetrics& metrics,
        std::string_view serial_id,
        std::span<char> out_buffer) noexcept
    {
        std::size_t offset = 0;

        auto append_sv = [&](std::string_view sv) -> bool {
            if (offset + sv.size() >= out_buffer.size()) {
                return false;
            }
            for (char ch : sv) {
                out_buffer[offset++] = ch;
            }
            return true;
        };

        auto append_hex32 = [&](std::uint32_t val) -> bool {
            constexpr char digits[] = "0123456789ABCDEF";
            if (offset + 8 >= out_buffer.size()) return false;
            for (int i = 7; i >= 0; --i) {
                out_buffer[offset + i] = digits[val & 0x0F];
                val >>= 4;
            }
            offset += 8;
            return true;
        };

        auto append_int = [&](std::int64_t val) -> bool {
            char tmp[24];
            int idx = 0;
            bool neg = val < 0;
            if (neg) val = -val;
            if (val == 0) tmp[idx++] = '0';
            while (val > 0) {
                tmp[idx++] = static_cast<char>('0' + (val % 10));
                val /= 10;
            }
            if (neg) tmp[idx++] = '-';
            if (offset + idx >= out_buffer.size()) return false;
            while (idx > 0) {
                out_buffer[offset++] = tmp[--idx];
            }
            return true;
        };

        if (!append_sv("{\"serial\":\"")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv(serial_id)) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("\",\"uid\":\"")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_hex32(metrics.uid[0])) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("-")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_hex32(metrics.uid[1])) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("-")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_hex32(metrics.uid[2])) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("\",\"vdda_mv\":")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_int(metrics.vdda_mv)) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv(",\"temp_c\":")) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_int(metrics.core_temperature_c)) return std::unexpected(TelemetryError::buffer_overflow);
        if (!append_sv("}\r\n")) return std::unexpected(TelemetryError::buffer_overflow);

        out_buffer[offset] = '\0';
        return offset;
    }
};

} // namespace telemetry

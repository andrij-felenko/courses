#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>

namespace telemetry {

inline constexpr uint8_t BatchMagic = 0xD0;
inline constexpr size_t  MaxBatchCapacity = 16;

struct SamplePoint {
    uint32_t timestamp{0};
    int16_t  temperature{0};
    uint16_t voltage_mv{0};
};

class BatchCompressor {
private:
    std::array<SamplePoint, MaxBatchCapacity> samples_{};
    size_t count_{0};

public:
    constexpr BatchCompressor() noexcept = default;

    constexpr bool add(uint32_t ts, int16_t temp, uint16_t mv) noexcept {
        if (count_ >= MaxBatchCapacity) {
            return false;
        }
        samples_[count_++] = SamplePoint{ts, temp, mv};
        return true;
    }

    [[nodiscard]] constexpr size_t count() const noexcept { return count_; }
    constexpr void clear() noexcept { count_ = 0; }

    [[nodiscard]] size_t serialize_delta(std::span<uint8_t> out) const noexcept {
        if (count_ == 0 || out.size() < 9 + (count_ - 1) * 3) {
            return 0;
        }

        out[0] = static_cast<uint8_t>((BatchMagic & 0xF0) | (count_ & 0x0F));

        const auto& base = samples_[0];
        out[1] = static_cast<uint8_t>(base.timestamp >> 24);
        out[2] = static_cast<uint8_t>(base.timestamp >> 16);
        out[3] = static_cast<uint8_t>(base.timestamp >> 8);
        out[4] = static_cast<uint8_t>(base.timestamp);

        out[5] = static_cast<uint8_t>(base.temperature >> 8);
        out[6] = static_cast<uint8_t>(base.temperature);

        out[7] = static_cast<uint8_t>(base.voltage_mv >> 8);
        out[8] = static_cast<uint8_t>(base.voltage_mv);

        size_t offset = 9;
        for (size_t i = 1; i < count_; ++i) {
            const auto& curr = samples_[i];
            const auto& prev = samples_[i - 1];

            const uint32_t dt = curr.timestamp - prev.timestamp;
            const int16_t dtemp = curr.temperature - prev.temperature;
            const int32_t dv = static_cast<int32_t>(curr.voltage_mv) - static_cast<int32_t>(prev.voltage_mv);

            const auto dt_byte = static_cast<int8_t>(std::clamp<uint32_t>(dt / 10, 0, 255));
            const auto dtemp_byte = static_cast<int8_t>(std::clamp<int16_t>(dtemp, -128, 127));
            const auto dv_byte = static_cast<int8_t>(std::clamp<int32_t>(dv / 10, -128, 127));

            out[offset++] = static_cast<uint8_t>(dt_byte);
            out[offset++] = static_cast<uint8_t>(dtemp_byte);
            out[offset++] = static_cast<uint8_t>(dv_byte);
        }

        return offset;
    }
};

} // namespace telemetry

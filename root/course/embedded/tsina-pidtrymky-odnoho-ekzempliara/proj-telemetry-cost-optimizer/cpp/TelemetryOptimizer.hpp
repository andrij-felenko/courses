/* TelemetryOptimizer.hpp — Ідіоматичний C++20 */
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <string_view>
#include <optional>
#include <expected>
#include <algorithm>
#include <bit>

namespace embedded::telemetry {

enum class Status {
    Ok,
    DroppedNoise,
    Buffered,
    BatchReady
};

enum class Error {
    BufferOverflow,
    BufferTooSmall,
    InvalidParameter,
    NoData
};

struct Sample {
    uint32_t timestampSec{0};
    int32_t  valueFixed{0};     // Фіксована кома (наприклад, одиниці × 100)
};

struct FilterConfig {
    int32_t  deadbandAbs{10};    // Мінімальний поріг відхилення
    uint32_t maxIntervalSec{3600}; // Максимальний інтервал Heartbeat
};

template <size_t MaxSamples = 32>
class TelemetryOptimizer {
public:
    explicit constexpr TelemetryOptimizer(FilterConfig cfg) noexcept
        : config_{cfg} {}

    void setHealthFlag(uint16_t flagMask, bool active) noexcept {
        if (active) {
            healthFlags_ |= flagMask;
        } else {
            healthFlags_ &= static_cast<uint16_t>(~flagMask);
        }
    }

    [[nodiscard]] std::expected<Status, Error> pushSample(uint32_t timestamp, int32_t value) noexcept {
        Sample current{timestamp, value};

        if (!shouldSave(current)) {
            return Status::DroppedNoise;
        }

        if (sampleCount_ >= MaxSamples) {
            return std::unexpected(Error::BufferOverflow);
        }

        buffer_[sampleCount_++] = current;
        lastSaved_ = current;
        hasBaseline_ = true;

        if (sampleCount_ >= MaxSamples) {
            return Status::BatchReady;
        }

        return Status::Buffered;
    }

    [[nodiscard]] std::expected<size_t, Error> serializeBatch(std::span<uint8_t> output) noexcept {
        if (sampleCount_ == 0) {
            return std::unexpected(Error::NoData);
        }

        const size_t requiredSize = 6 + sizeof(uint32_t) + sizeof(int32_t) + (sampleCount_ - 1) * 4;
        if (output.size() < requiredSize) {
            return std::unexpected(Error::BufferTooSmall);
        }

        size_t offset = 0;

        // 1. Заголовок
        output[offset++] = 0xAA; // Magic
        output[offset++] = 0x01; // Version
        output[offset++] = static_cast<uint8_t>(sampleCount_);
        output[offset++] = static_cast<uint8_t>(healthFlags_ & 0xFF);
        output[offset++] = static_cast<uint8_t>((healthFlags_ >> 8) & 0xFF);
        output[offset++] = 0x00; // Reserved

        // 2. Базова точка
        const auto& base = buffer_[0];
        writeBytes(output, offset, base.timestampSec);
        writeBytes(output, offset, base.valueFixed);

        // 3. Дельта-точки (uint16_t dt, int16_t dv)
        for (size_t i = 1; i < sampleCount_; ++i) {
            const uint32_t dt = buffer_[i].timestampSec - base.timestampSec;
            const int32_t  dv = buffer_[i].valueFixed - base.valueFixed;

            const auto dtClamped = static_cast<uint16_t>(std::min<uint32_t>(dt, 0xFFFF));
            const auto dvClamped = static_cast<int16_t>(std::clamp<int32_t>(dv, -32768, 32767));

            writeBytes(output, offset, dtClamped);
            writeBytes(output, offset, dvClamped);
        }

        sampleCount_ = 0; // Скидання буфера після успішного пакування
        return offset;
    }

    [[nodiscard]] size_t currentBatchSize() const noexcept { return sampleCount_; }
    [[nodiscard]] bool empty() const noexcept { return sampleCount_ == 0; }

private:
    template <typename T>
    static void writeBytes(std::span<uint8_t> dst, size_t& offset, T value) noexcept {
        auto rawBytes = std::bit_cast<std::array<uint8_t, sizeof(T)>>(value);
        std::copy(rawBytes.begin(), rawBytes.end(), dst.begin() + offset);
        offset += sizeof(T);
    }

    [[nodiscard]] bool shouldSave(const Sample& current) const noexcept {
        if (!hasBaseline_) return true;

        if ((current.timestampSec - lastSaved_.timestampSec) >= config_.maxIntervalSec) {
            return true;
        }

        const int32_t diff = std::abs(current.valueFixed - lastSaved_.valueFixed);
        return diff >= config_.deadbandAbs;
    }

    FilterConfig                 config_;
    Sample                       lastSaved_{};
    bool                         hasBaseline_{false};
    std::array<Sample, MaxSamples> buffer_{};
    size_t                       sampleCount_{0};
    uint16_t                     healthFlags_{0};
};

} // namespace embedded::telemetry

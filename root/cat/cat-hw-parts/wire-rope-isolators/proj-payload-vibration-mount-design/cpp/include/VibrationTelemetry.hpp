#pragma once

#include <cstddef>
#include <deque>
#include <vector>
#include <cmath>
#include <algorithm>

/**
 * @brief Вибірка вимірювання тривісного акселерометра в одиницях G.
 */
struct AccelSample {
    double timestamp_s;
    double ax;
    double ay;
    double az;

    [[nodiscard]] double getMagnitude() const noexcept {
        return std::sqrt(ax * ax + ay * ay + az * az);
    }
};

/**
 * @brief Кільцевий неблокуючий буфер часових рядів прискорень з обчисленням діючого значення.
 */
class TelemetryBuffer {
public:
    explicit TelemetryBuffer(std::size_t capacity = 128) : capacity_(capacity) {}

    void push(double timestamp_s, double ax, double ay, double az) {
        if (buffer_.size() >= capacity_) {
            buffer_.pop_front();
        }
        buffer_.push_back({timestamp_s, ax, ay, az});
    }

    [[nodiscard]] std::size_t size() const noexcept { return buffer_.size(); }
    [[nodiscard]] bool empty() const noexcept { return buffer_.empty(); }

    [[nodiscard]] double calculateRms() const noexcept {
        if (buffer_.empty()) return 0.0;
        double sum_sq = 0.0;
        for (const auto& s : buffer_) {
            double mag = s.getMagnitude();
            sum_sq += mag * mag;
        }
        return std::sqrt(sum_sq / static_cast<double>(buffer_.size()));
    }

    [[nodiscard]] double getPeakMagnitude() const noexcept {
        if (buffer_.empty()) return 0.0;
        double peak = 0.0;
        for (const auto& s : buffer_) {
            peak = std::max(peak, s.getMagnitude());
        }
        return peak;
    }

    [[nodiscard]] const std::deque<AccelSample>& getSamples() const noexcept {
        return buffer_;
    }

    void clear() noexcept { buffer_.clear(); }

private:
    std::size_t capacity_;
    std::deque<AccelSample> buffer_;
};

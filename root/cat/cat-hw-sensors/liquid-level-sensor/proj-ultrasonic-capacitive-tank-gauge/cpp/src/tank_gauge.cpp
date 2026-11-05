#include "tank_gauge.hpp"
#include <cmath>

namespace TankMonitoring {

MedianFilter::MedianFilter(size_t windowSize)
    : windowSize_(windowSize ? windowSize : 5)
{
    buffer_.reserve(windowSize_);
}

float MedianFilter::process(float sample) {
    if (buffer_.size() < windowSize_) {
        buffer_.push_back(sample);
    } else {
        buffer_[head_] = sample;
        head_ = (head_ + 1) % windowSize_;
    }

    std::vector<float> sorted = buffer_;
    std::sort(sorted.begin(), sorted.end());

    size_t n = sorted.size();
    if (n % 2 == 1) {
        return sorted[n / 2];
    } else {
        return (sorted[(n / 2) - 1] + sorted[n / 2]) * 0.5f;
    }
}

void MedianFilter::reset() {
    buffer_.clear();
    head_ = 0;
    full_ = false;
}

TankGaugeController::TankGaugeController(TankConfig config, size_t filterWindow)
    : config_(std::move(config))
    , filter_(filterWindow)
{
}

float TankGaugeController::calculateSoundSpeed(float temperatureC) {
    // c(T) = 331.3 + 0.606 * T (м/с)
    return 331.3f + 0.606f * temperatureC;
}

void TankGaugeController::update(uint32_t echoDurationUs, float ambientTempC) {
    float speed = calculateSoundSpeed(ambientTempC);
    // d = (c * t) / 2
    rawDistanceMm_ = speed * static_cast<float>(echoDurationUs) * 0.0005f;
    filteredDistanceMm_ = filter_.process(rawDistanceMm_);

    liquidLevelMm_ = config_.sensorHeightMm - filteredDistanceMm_;
    if (liquidLevelMm_ < 0.0f) liquidLevelMm_ = 0.0f;
    if (liquidLevelMm_ > config_.sensorHeightMm) liquidLevelMm_ = config_.sensorHeightMm;

    currentVolumeLiters_ = interpolateVolume(liquidLevelMm_);
    if (config_.maxVolumeLiters > 0.0f) {
        currentPercentage_ = (currentVolumeLiters_ / config_.maxVolumeLiters) * 100.0f;
        if (currentPercentage_ > 100.0f) currentPercentage_ = 100.0f;
        if (currentPercentage_ < 0.0f) currentPercentage_ = 0.0f;
    } else {
        currentPercentage_ = 0.0f;
    }
}

void TankGaugeController::setCalibrationTable(const std::vector<CalibPoint>& table) {
    config_.calibrationTable = table;
}

float TankGaugeController::interpolateVolume(float heightMm) const {
    const auto& table = config_.calibrationTable;
    if (table.empty()) return 0.0f;

    if (heightMm <= table.front().height_mm) {
        return table.front().volume_liters;
    }
    if (heightMm >= table.back().height_mm) {
        return table.back().volume_liters;
    }

    for (size_t i = 0; i < table.size() - 1; ++i) {
        float h0 = table[i].height_mm;
        float h1 = table[i + 1].height_mm;
        if (heightMm >= h0 && heightMm <= h1) {
            float v0 = table[i].volume_liters;
            float v1 = table[i + 1].volume_liters;
            float t = (heightMm - h0) / (h1 - h0);
            return v0 + t * (v1 - v0);
        }
    }

    return 0.0f;
}

} // namespace TankMonitoring

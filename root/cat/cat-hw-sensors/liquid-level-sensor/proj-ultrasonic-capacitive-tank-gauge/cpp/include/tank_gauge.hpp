#pragma once

#include <cstdint>
#include <cstddef>
#include <vector>
#include <array>
#include <algorithm>

namespace TankMonitoring {

struct CalibPoint {
    float height_mm;
    float volume_liters;
};

struct TankConfig {
    float sensorHeightMm{2000.0f};
    float maxVolumeLiters{1000.0f};
    std::vector<CalibPoint> calibrationTable;
};

class MedianFilter {
public:
    explicit MedianFilter(size_t windowSize = 5);
    float process(float sample);
    void reset();

private:
    size_t windowSize_;
    std::vector<float> buffer_;
    size_t head_{0};
    bool full_{false};
};

class TankGaugeController {
public:
    explicit TankGaugeController(TankConfig config, size_t filterWindow = 5);

    // Розрахунок швидкості звуку за температурою навколишнього середовища (м/с)
    static float calculateSoundSpeed(float temperatureC);

    // Оновлення стану контролера новим виміром часу прольоту ехо-імпульсу (ToF) та температури
    void update(uint32_t echoDurationUs, float ambientTempC);

    // Отримання результатів
    float getRawDistanceMm() const { return rawDistanceMm_; }
    float getFilteredDistanceMm() const { return filteredDistanceMm_; }
    float getLiquidLevelMm() const { return liquidLevelMm_; }
    float getVolumeLiters() const { return currentVolumeLiters_; }
    float getPercentage() const { return currentPercentage_; }

    // Конфігурація та EEPROM калібрування
    const TankConfig& getConfig() const { return config_; }
    void setCalibrationTable(const std::vector<CalibPoint>& table);

private:
    float interpolateVolume(float heightMm) const;

    TankConfig config_;
    MedianFilter filter_;
    float rawDistanceMm_{0.0f};
    float filteredDistanceMm_{0.0f};
    float liquidLevelMm_{0.0f};
    float currentVolumeLiters_{0.0f};
    float currentPercentage_{0.0f};
};

} // namespace TankMonitoring

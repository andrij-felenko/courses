#include "adc_current_sensor.hpp"
#include <algorithm>
#include <cmath>

namespace towerpro {

bool AdcCurrentSensor::begin(const AdcSensorConfig& config) {
    if (config.adcResolution == 0 || config.shuntResistanceOhm <= 0.0f || config.ampGain <= 0.0f) {
        return false;
    }
    config_ = config;
    resetFilter();
    return true;
}

void AdcCurrentSensor::resetFilter() {
    sampleBuffer_.fill(0.0f);
    bufferIndex_ = 0;
    sampleCount_ = 0;
    accumulatedSum_ = 0.0f;
    filteredCurrentmA_ = 0.0f;
    lastSampleMicros_ = 0;
}

void AdcCurrentSensor::setSimulatedRawAdc(uint16_t rawAdcValue) {
    simulatedRawAdc_ = rawAdcValue;
    simulatedMode_ = true;
}

float AdcCurrentSensor::rawAdcToCurrentmA(uint16_t adcVal) const {
    float clampedAdc = static_cast<float>(std::min(adcVal, static_cast<uint16_t>(config_.adcResolution - 1)));
    float voltageV = (clampedAdc / static_cast<float>(config_.adcResolution)) * config_.referenceVoltageV;
    
    float senseVoltageV = voltageV - config_.zeroCurrentOffsetV;
    if (senseVoltageV < 0.0f) {
        senseVoltageV = 0.0f;
    }
    
    float currentAmps = senseVoltageV / (config_.shuntResistanceOhm * config_.ampGain);
    return currentAmps * 1000.0f; // Перетворення А -> мА
}

void AdcCurrentSensor::update(uint32_t currentMicros) {
    if (lastSampleMicros_ != 0 && (currentMicros - lastSampleMicros_ < config_.sampleIntervalUs)) {
        return;
    }
    lastSampleMicros_ = currentMicros;

    uint16_t rawAdc = 0;
    if (simulatedMode_) {
        rawAdc = simulatedRawAdc_;
    } else {
        // Симуляція або апаратне аналогове зчитування (analogRead(config_.adcPin))
        rawAdc = 0;
    }

    float currentmA = rawAdcToCurrentmA(rawAdc);

    // Алгоритм згладжування Moving Average
    accumulatedSum_ -= sampleBuffer_[bufferIndex_];
    sampleBuffer_[bufferIndex_] = currentmA;
    accumulatedSum_ += currentmA;

    bufferIndex_ = (bufferIndex_ + 1) % FILTER_WINDOW_SIZE;
    if (sampleCount_ < FILTER_WINDOW_SIZE) {
        sampleCount_++;
    }

    filteredCurrentmA_ = accumulatedSum_ / static_cast<float>(sampleCount_);
}

float AdcCurrentSensor::readCurrentmA() const {
    return filteredCurrentmA_;
}

float AdcCurrentSensor::getRawVoltage() const {
    float currentAmps = filteredCurrentmA_ / 1000.0f;
    float senseVoltageV = currentAmps * (config_.shuntResistanceOhm * config_.ampGain);
    return senseVoltageV + config_.zeroCurrentOffsetV;
}

} // namespace towerpro

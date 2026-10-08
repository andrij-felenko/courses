// Зчитування показників драйвера (C++)
float LiquidLevelSensor::getPercent() const {
    float filteredAdc = getFilteredAdc();
    return calculatePercent(filteredAdc);
}

float LiquidLevelSensor::getHeightMm() const {
    return (getPercent() / 100.0f) * config_.maxHeightMm;
}

float LiquidLevelSensor::getVolumeLiters(float tankRadiusMm) const {
    float heightMm = getHeightMm();
    float areaSqMm = 3.14159f * tankRadiusMm * tankRadiusMm;
    return (areaSqMm * heightMm) / 1000000.0f;
}

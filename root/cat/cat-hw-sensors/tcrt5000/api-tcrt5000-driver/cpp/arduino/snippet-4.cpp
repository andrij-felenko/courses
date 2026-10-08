uint16_t Tcrt5000Driver::readAnalogRaw() {
    if (!isInitialized_) return 0;
    lastRawValue_ = analogRead(config_.analogPin);
    return lastRawValue_;
}

float Tcrt5000Driver::readNormalized(float vRef = 3.3f, uint8_t adcBits = 10) {
    uint16_t raw = readAnalogRaw();
    float maxAdc = (float)((1 << adcBits) - 1);
    return (float)raw / maxAdc;
}

bool Tcrt5000Driver::readDigital() {
    if (!isInitialized_ || config_.digitalPin < 0) return false;
    return digitalRead(config_.digitalPin) == LOW;
}

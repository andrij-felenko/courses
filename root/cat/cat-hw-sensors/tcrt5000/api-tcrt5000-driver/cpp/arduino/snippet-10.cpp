Tcrt5000Driver::Status readDifferentialSignal(Tcrt5000Driver& driver, uint8_t emitterPin, uint16_t& diffVal) {
    if (emitterPin == 255) return Tcrt5000Driver::ERR_INVALID_ARG;

    // Фаза 1: Фоновий відлік (LED OFF)
    digitalWrite(emitterPin, LOW);
    delayMicroseconds(50);
    uint16_t vOff = driver.readAnalogRaw();

    if (vOff > 980) { // Для 10-бітного АЦП
        return Tcrt5000Driver::ERR_SATURATION;
    }

    // Фаза 2: Активний відлік (LED ON)
    digitalWrite(emitterPin, HIGH);
    delayMicroseconds(50);
    uint16_t vOn = driver.readAnalogRaw();
    digitalWrite(emitterPin, LOW);

    if (vOn < 5 && vOff < 5) {
        return Tcrt5000Driver::ERR_DISCONNECTED;
    }

    diffVal = (vOn > vOff) ? (vOn - vOff) : 0;
    return Tcrt5000Driver::OK;
}

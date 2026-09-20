uint16_t ThumbwheelDriver::readRawShiftReg() {
    uint16_t rawData = 0;
    
    gpioWrite(config_.pinPl, false);
    delayNs(20);
    gpioWrite(config_.pinPl, true);
    
    const uint8_t totalBits = config_.decadesCount * 4;
    for (uint8_t i = 0; i < totalBits; ++i) {
        rawData <<= 1;
        if (gpioRead(config_.pinData)) {
            rawData |= 0x0001;
        }
        gpioWrite(config_.pinClk, true);
        delayNs(50);
        gpioWrite(config_.pinClk, false);
        delayNs(50);
    }
    
    if (config_.activeLowLogic) {
        rawData = ~rawData;
    }
    
    return rawData;
}

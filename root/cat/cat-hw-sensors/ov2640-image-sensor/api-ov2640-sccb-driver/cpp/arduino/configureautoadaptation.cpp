bool configureAutoAdaptation(OV2640Driver& driver) {
    // 1. Активація автоекспозиції AEC та підсилення AGC у банку Sensor
    if (!driver.setBank(OV2640Driver::Bank::Sensor)) return false;
    
    bool ok = true;
    ok &= driver.writeRegister(OV2640Driver::Bank::Sensor, 0x24, 0x40); // AEW target high
    ok &= driver.writeRegister(OV2640Driver::Bank::Sensor, 0x25, 0x38); // AEB target low
    ok &= driver.writeRegister(OV2640Driver::Bank::Sensor, 0x13, 0xE7); // Enable Auto algorithms
    
    // 2. Встановлення тонової кривої у банку DSP
    if (!driver.setBank(OV2640Driver::Bank::DSP)) return false;
    
    const uint8_t gammaLUT[15] = {
        0x04, 0x0E, 0x1A, 0x31, 0x5A, 0x69, 0x75, 0x7E,
        0x88, 0x8F, 0x96, 0xA3, 0xAF, 0xC4, 0xD7
    };
    
    for (uint8_t i = 0; i < 15; ++i) {
        ok &= driver.writeRegister(OV2640Driver::Bank::DSP, 0x7A + i, gammaLUT[i]);
    }
    return ok;
}

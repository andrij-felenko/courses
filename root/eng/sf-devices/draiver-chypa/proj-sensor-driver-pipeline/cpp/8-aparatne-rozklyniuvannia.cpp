template <typename GpioDriver>
void recoverI2cBus(GpioDriver& gpio) noexcept {
    gpio.setOpenDrain();
    gpio.setSdaHigh();

    for (uint8_t i = 0; i < 9; ++i) {
        gpio.toggleSclPulse();
        if (gpio.readSda()) {
            break;
        }
    }

    gpio.generateStopCondition();
    gpio.restorePeripheralMode();
}

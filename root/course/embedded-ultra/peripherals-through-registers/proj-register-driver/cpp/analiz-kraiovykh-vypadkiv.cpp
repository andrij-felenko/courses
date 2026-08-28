/* Обробник переривання таймера TIM6 на мові C++ */
extern "C" void TIM6_DAC_IRQHandler() noexcept {
    auto* timer = reinterpret_cast<TimerRegisters*>(MemoryMap::Tim6Base);
    auto* gpio  = reinterpret_cast<GpioRegisters*>(MemoryMap::GpioABase);

    if (timer->SR & 0x01UL) {
        timer->SR &= ~0x01UL;
        (void)timer->SR; // Синхронізація шини APB

        gpio->BSRR = (1UL << 5);
    }
}

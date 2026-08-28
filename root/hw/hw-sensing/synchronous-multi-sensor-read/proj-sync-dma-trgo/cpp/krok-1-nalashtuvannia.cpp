namespace hardware {

struct MasterTimerInit {
    static constexpr std::uint32_t BusClockHz = 168'000'000;
    static constexpr std::uint32_t CounterClockHz = 1'000'000;
    static constexpr std::uint32_t SampleRateHz = 1'000;
    static constexpr std::uint32_t SyncPulseUs = 10;

    static void setup(TIM_TypeDef* tim) noexcept {
        tim->PSC = (BusClockHz / CounterClockHz) - 1;
        tim->ARR = (CounterClockHz / SampleRateHz) - 1;

        // Подія Update виводиться на тригер TRGO
        tim->CR2 = (tim->CR2 & ~TIM_CR2_MMS) | TIM_CR2_MMS_1;

        tim->CCR1 = SyncPulseUs;
        tim->CCMR1 |= (6U << TIM_CCMR1_OC1M_Pos); // PWM1
        tim->CCER |= TIM_CCER_CC1E;
        tim->CR1 |= TIM_CR1_CEN;
    }
};

} // namespace hardware

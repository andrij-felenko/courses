namespace hardware {

struct TimestampCaptureTimer {
    static constexpr std::uint32_t ApbClockHz = 84'000'000;
    static constexpr std::uint32_t TimerFreqHz = 1'000'000;

    static void setup(TIM_TypeDef* tim) noexcept {
        tim->PSC = (ApbClockHz / TimerFreqHz) - 1;
        tim->ARR = 0xFFFFFFFF; // 32-бітний вільний лічильник

        tim->CCMR1 |= TIM_CCMR1_CC1S_0; // Прив'язка до входу TI1
        tim->CCER &= ~TIM_CCER_CC1P;    // Наростаючий фронт
        tim->CCER |= TIM_CCER_CC1E;     // Дозвіл захоплення
        tim->CR1 |= TIM_CR1_CEN;
    }

    [[nodiscard]] static std::uint32_t get_captured_timestamp(const TIM_TypeDef* tim) noexcept {
        return tim->CCR1;
    }
};

} // namespace hardware

#include "stm32f4xx.h"

class HardwareEncoderDecoder {
public:
    explicit HardwareEncoderDecoder(TIM_TypeDef* timer) : timer_(timer) {}

    void init() {
        // Увімкнення тактування периферії
        if (timer_ == TIM2) {
            RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
            RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

            // PA0 -> TIM2_CH1, PA1 -> TIM2_CH2 (AF1)
            GPIOA->MODER &= ~(GPIO_MODER_MODE0 | GPIO_MODER_MODE1);
            GPIOA->MODER |= (GPIO_MODER_MODE0_1 | GPIO_MODER_MODE1_1);
            GPIOA->PUPDR &= ~(GPIO_PUPDR_PUPD0 | GPIO_PUPDR_PUPD1);
            GPIOA->PUPDR |= (GPIO_PUPDR_PUPD0_0 | GPIO_PUPDR_PUPD1_0);

            GPIOA->AFR[0] &= ~(GPIO_AFRL_AFSEL0 | GPIO_AFRL_AFSEL1);
            GPIOA->AFR[0] |= (1 << 0) | (1 << 4);
        }

        // Конфігурація каналів вводу (CC1S=01, CC2S=01)
        timer_->CCMR1 &= ~(TIM_CCMR1_CC1S | TIM_CCMR1_CC2S);
        timer_->CCMR1 |= (TIM_CCMR1_CC1S_0 | TIM_CCMR1_CC2S_0);

        // Встановлення фільтра завад (IC1F = 0011, IC2F = 0011)
        timer_->CCMR1 &= ~(TIM_CCMR1_IC1F | TIM_CCMR1_IC2F);
        timer_->CCMR1 |= (TIM_CCMR1_IC1F_0 | TIM_CCMR1_IC1F_1) |
                         (TIM_CCMR1_IC2F_0 | TIM_CCMR1_IC2F_1);

        // Полярність за замовчуванням (пряма)
        timer_->CCER &= ~(TIM_CCER_CC1P | TIM_CCER_CC1NP | TIM_CCER_CC2P | TIM_CCER_CC2NP);

        // Конфігурація режиму Encoder 3 (x4)
        timer_->SMCR &= ~TIM_SMCR_SMS;
        timer_->SMCR |= (TIM_SMCR_SMS_0 | TIM_SMCR_SMS_1);

        // Встановлення межі лічильника та запуск
        timer_->ARR = 0xFFFFFFFFU;
        timer_->CNT = 0;
        timer_->CR1 |= TIM_CR1_CEN;
    }

    [[nodiscard]] uint32_t get_raw_count() const {
        return timer_->CNT;
    }

    [[nodiscard]] bool is_counting_down() const {
        return (timer_->CR1 & TIM_CR1_DIR) != 0;
    }

private:
    TIM_TypeDef* timer_;
};

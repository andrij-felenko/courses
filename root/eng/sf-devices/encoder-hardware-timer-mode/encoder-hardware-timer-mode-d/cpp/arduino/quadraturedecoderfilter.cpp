// Конфігурація регістрів цифрового фільтра таймера STM32/Arduino HAL на прямому рівні регістрів
#include <Arduino.h>

class QuadratureDecoderFilter {
private:
    TIM_TypeDef* _timer;

public:
    QuadratureDecoderFilter(TIM_TypeDef* timer) : _timer(timer) {}

    void configureFilter(uint8_t filter_code) {
        // filter_code = 0x03: f_SAMPLING = f_CK_INT, N = 8 вибірок
        // Очищення та запис конфігурації фільтрів каналів IC1F та IC2F у регістрі CCMR1
        uint32_t ccmr1 = _timer->CCMR1;
        ccmr1 &= ~(TIM_CCMR1_IC1F | TIM_CCMR1_IC2F);
        ccmr1 |= ((uint32_t)filter_code << TIM_CCMR1_IC1F_Pos);
        ccmr1 |= ((uint32_t)filter_code << TIM_CCMR1_IC2F_Pos);
        _timer->CCMR1 = ccmr1;

        // Встановлення дільника частоти DTS у регістрі контролю CR1 (CKD[1:0] = 00 -> t_DTS = t_CK_INT)
        _timer->CR1 &= ~TIM_CR1_CKD;
    }

    void enableEncoderMode() {
        _timer->SMCR &= ~TIM_SMCR_SMS;
        _timer->SMCR |= TIM_ENCODERMODE_TI12; // Режим x4
        _timer->CR1 |= TIM_CR1_CEN;            // Ввімкнення апаратного лічильника
    }
};

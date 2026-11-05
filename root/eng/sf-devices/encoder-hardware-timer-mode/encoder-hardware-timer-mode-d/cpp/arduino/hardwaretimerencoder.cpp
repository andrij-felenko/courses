// ОПТИМАЛЬНИЙ ПІДХІД: Апаратне зчитування енкодера через периферійний таймер мікроконтролера
#include <Arduino.h>

// Клас обгортки для роботи з апаратним квадратурним декодером таймера
class HardwareTimerEncoder {
private:
    TIM_TypeDef* _timer;

public:
    HardwareTimerEncoder(TIM_TypeDef* timer) : _timer(timer) {}

    void begin() {
        // Конфігурація периферійного таймера в апаратний режим квадратурного декодера (Mode x4)
        // Процесор взагалі не бере участі в підрахунку імпульсів!
        __HAL_RCC_TIM2_CLK_ENABLE();
        
        _timer->SMCR &= ~TIM_SMCR_SMS;
        _timer->SMCR |= (TIM_ENCODERMODE_TI12); // Режим x4: лічба по обидвох каналах TI1 та TI2
        
        // Налаштування цифрового фільтра шуму (IC1F = 0x06: 8 тактів стабільності)
        _timer->CCMR1 &= ~(TIM_CCMR1_IC1F | TIM_CCMR1_IC2F);
        _timer->CCMR1 |= (0x06 << TIM_CCMR1_IC1F_Pos) | (0x06 << TIM_CCMR1_IC2F_Pos);
        
        _timer->ARR = 0xFFFF; // Максимальний діапазон 16-бітного лічильника
        _timer->CNT = 0;      // Скидання поточного значення
        _timer->CR1 |= TIM_CR1_CEN; // Запуск таймера
    }

    inline int16_t getRawPosition() const {
        return static_cast<int16_t>(_timer->CNT); // Миттєве зчитування позиції без затримок ISR
    }
};

// БЕЗПЕЧНО: апаратний комплементарний ШІМ із мертвим часом (STM32, TIM1).
// Залізо саме формує HO і LO з паузою — процесор лише задає шпаруватість.
void halfbridge_init(uint32_t pwm_hz, uint8_t dead_ticks) {
    TIM1->PSC = 0;                          // без передільника: лічимо такти ядра
    TIM1->ARR = (SystemCoreClock / pwm_hz) - 1;   // період ШІМ

    // Канал 1 у режимі ШІМ; основний вихід — OC1 (HO), комплементарний — OC1N (LO).
    TIM1->CCMR1 = (6 << 4);                 // OC1M = 110: PWM mode 1
    TIM1->CCER  = TIM_CCER_CC1E             // увімкнути основний вихід (HO)
                | TIM_CCER_CC1NE;           // і комплементарний (LO) — апаратна інверсія

    // Регістр мертвого часу: DTG задає паузу між HO і LO у тактах таймера.
    TIM1->BDTR = (dead_ticks & 0xFF)        // DTG[7:0] — ширина мертвого часу
                | TIM_BDTR_MOE;             // Main Output Enable: пустити сигнали на ніжки

    TIM1->CR1 = TIM_CR1_CEN;                // запустити таймер
}

// Зміна швидкості зводиться до однієї цифри — решту (інверсію + паузу) робить залізо.
void halfbridge_set_duty(uint16_t duty) {   // duty: 0..ARR
    TIM1->CCR1 = duty;
}

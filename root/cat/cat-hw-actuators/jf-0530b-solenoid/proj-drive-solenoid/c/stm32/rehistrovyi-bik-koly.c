// STM32, прямо в регістрах TIM3: 25 кГц, 8-бітна шкала (такт таймера 64 МГц)
void Solenoid_Setup(void) {
    __HAL_RCC_TIM3_CLK_ENABLE();                    // такт на таймер
    TIM3->PSC   = 9;                                // 64 МГц / 10 = 6.4 МГц
    TIM3->ARR   = 255;                              // 6.4 МГц / 256 = 25 кГц, шкала 0..255
    TIM3->CCR1  = 0;
    TIM3->CCMR1 |= (6 << TIM_CCMR1_OC1M_Pos)        // PWM mode 1 на каналі 1
                 | TIM_CCMR1_OC1PE;                 // CCR перезавантажується атомарно
    TIM3->CCER  |= TIM_CCER_CC1E;                   // вихід каналу 1 увімкнено
    TIM3->EGR   |= TIM_EGR_UG;                      // підхопити нові PSC/ARR
    TIM3->CR1   |= TIM_CR1_CEN;                     // пуск лічильника
}

void Solenoid_Peak(void) { TIM3->CCR1 = 256; }  // > ARR → суцільний рівень: повний струм
void Solenoid_Hold(void) { TIM3->CCR1 = 90;  }  // ≈35% — тихе утримання
void Solenoid_Off (void) { TIM3->CCR1 = 0;   }  // відпустити

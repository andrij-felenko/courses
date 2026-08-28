volatile dtmf_bank_t bank;          // volatile: міняється в ISR, читається в main
volatile uint8_t     block_ready = 0;

// ISR готовності АЦП: один відлік готовий
void ADC_IRQHandler(void)
{
    int16_t raw = ADC_READ();                 // сире 12-бітне значення
    float   x   = (float)(raw - 2048);        // зняти зміщення середини шкали
    if (dtmf_feed_sample((dtmf_bank_t *)&bank, x))
        block_ready = 1;                      // лише прапорець — рішення в main
}

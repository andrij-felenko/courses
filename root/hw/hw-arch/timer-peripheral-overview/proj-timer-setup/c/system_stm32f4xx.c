extern const uint8_t APBPrescTable[8];   /* {0,0,0,0,1,2,3,4} — із system_stm32f4xx.c */

static uint32_t tim_clk_hz(void)
{
    uint32_t ppre1 = (RCC->CFGR & RCC_CFGR_PPRE1) >> RCC_CFGR_PPRE1_Pos;  /* біти 12:10 */
    uint32_t pclk1 = SystemCoreClock >> APBPrescTable[ppre1];
    return (ppre1 < 4u) ? pclk1 : pclk1 * 2u;   /* подільник 1 → як є, інакше ×2 */
}

/* період у наносекундах — з тих самих чисел, які реально лежать у залізі */
uint32_t tim3_period_ns(void)
{
    uint64_t ticks = (uint64_t)(TIM3->PSC + 1u) * (TIM3->ARR + 1u);
    return (uint32_t)(ticks * 1000000000ull / tim_clk_hz());
}

uint32_t micros_since_start(void)
{
    uint32_t hi, cnt, pending;

    do {
        hi      = ms_ticks;                  /* старша половина  */
        cnt     = TIM3->CNT;                 /* молодша половина */
        pending = TIM3->SR & TIM_SR_UIF;     /* перескок стався, обробник ще ні? */
    } while (hi != ms_ticks);                /* обробник утрутився — перечитати */

    if (pending && cnt < (ARR_VAL / 2u))     /* знімок узято вже після нуля */
        hi++;

    return hi * 1000u + cnt;
}

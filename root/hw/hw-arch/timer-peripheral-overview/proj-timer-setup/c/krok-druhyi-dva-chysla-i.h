#define TIMCLK_HZ   84000000u   /* частота, що доходить до TIM3 (не PCLK1!) */
#define TICK_HZ      1000000u   /* хочемо тік 1 мкс */
#define PERIOD_HZ       1000u   /* хочемо період 1 мс */

#define PSC_VAL  (TIMCLK_HZ / TICK_HZ   - 1u)   /* 84   − 1 = 83  */
#define ARR_VAL  (TICK_HZ  / PERIOD_HZ  - 1u)   /* 1000 − 1 = 999 */
#define CCR_VAL  250u                            /* 250 тіків високого рівня */

_Static_assert(TIMCLK_HZ % TICK_HZ  == 0u, "передільник не цілий — тік поїде");
_Static_assert(TICK_HZ % PERIOD_HZ  == 0u, "межа не ціла — період поїде");
_Static_assert(PSC_VAL <= 0xFFFFu,         "PSC не влазить у 16 бітів");
_Static_assert(ARR_VAL <= 0xFFFFu,         "TIM3 шістнадцятибітний, ARR завеликий");
_Static_assert(CCR_VAL <= ARR_VAL + 1u,    "поріг за межею періоду — збігу не буде");

// Тік щомілісекунди при тактовій 48 МГц:
SysTick->LOAD = 48000u - 1u;          // рахуємо 48000 тактів = 1 мс
SysTick->VAL  = 0u;                    // обнулити поточний лічильник
SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk   // джерело — тактова ядра
              | SysTick_CTRL_TICKINT_Msk     // дозволити виняток на нулі
              | SysTick_CTRL_ENABLE_Msk;     // пуск

// Далі лишається лічильник тіків:
volatile uint32_t g_ms = 0;
void SysTick_Handler(void) { g_ms++; }       // викликається рівно щомс

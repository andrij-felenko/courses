// Увімкнути зовнішній високочастотний генератор (HSE) і дочекатися старту.
// Скорочений приклад у стилі STM32; регістри названо узагальнено.

#define HSE_TIMEOUT  5000u            // запобіжник від нескінченного чекання

static int clock_start_hse(void)
{
    RCC->CR |= RCC_CR_HSEON;          // подати живлення на інвертор генератора

    uint32_t guard = 0;
    while (!(RCC->CR & RCC_CR_HSERDY)) {   // чекаємо прапорець "кварц завівся"
        if (++guard >= HSE_TIMEOUT)
            return -1;               // не стартував — fallback на внутрішній RC
    }

    // Кварц стабільний — лише тепер можна вести від нього шину тактів.
    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_SW) | RCC_CFGR_SW_HSE;
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_HSE)
        ;                            // дочекатися, що джерело справді перемкнулось
    return 0;
}

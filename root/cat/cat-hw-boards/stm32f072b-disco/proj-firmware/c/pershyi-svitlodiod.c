static void delay_crude(volatile uint32_t n) {   // груба затримка циклом
    while (n--) { __asm volatile("nop"); }
}

int main(void) {
    clock_48mhz();

    // 1. Тактування порту GPIOC. ЦЕ ЗАБУВАЮТЬ НАЙЧАСТІШЕ: без такту порт німий.
    RCC->AHBENR |= RCC_AHBENR_GPIOCEN;

    // 2. PC6 як цифровий вихід. Кожен вивід у F0 має 2 біти режиму в MODER:
    //    01 = вихід. Для виводу 6 це біти [13:12].
    GPIOC->MODER &= ~(3u << (6 * 2));            // очистити обидва біти виводу 6
    GPIOC->MODER |=  (1u << (6 * 2));            // 01 = загальний вихід

    // 3. Блимати: перемикати біт 6 у регістрі виходу ODR.
    for (;;) {
        GPIOC->ODR ^= (1u << 6);                 // інвертувати стан LD3
        delay_crude(400000);
    }
}

/* STM32F103: PC13 — стандартний LED.
   Ті самі принципи memory-mapped IO і read-modify-write,
   лише інші адреси й інша назва регістра конфігурації (CRH замість MODER).
   delay_rough() — лише для демонстрації; у реальній прошивці — таймер. */

#define RCC_APB2ENR   (*(volatile uint32_t *)0x40021018UL)  /* тактування */
#define GPIOC_CRH     (*(volatile uint32_t *)0x40011004UL)  /* конфіг PC8-15 */
#define GPIOC_ODR     (*(volatile uint32_t *)0x4001100CUL)  /* вихід */

void delay_rough(volatile uint32_t n) { while (n--); }

int main(void) {
    RCC_APB2ENR |= (1UL << 4);          /* увімкнути тактування GPIOC */

    GPIOC_CRH &= ~(0xFUL << 20);       /* скинути поле PC13 [23:20] */
    GPIOC_CRH |=  (0x2UL << 20);       /* MODE13=10 (вихід 2 МГц), CNF=00 (push-pull) */

    while (1) {
        GPIOC_ODR ^= (1UL << 13);      /* toggle PC13 */
        delay_rough(400000);
    }
}

#include <stdint.h>

/* Регістр конфігурації тактів (адреси/поля умовні, з даташита STM32-класу) */
#define RCC_CFGR  (*(volatile uint32_t *)0x40023808)

/* Дільники доменів: AHB на повну, APB1 ділимо на 4, APB2 — на 2 */
#define HPRE_DIV1   (0u  << 4)    /* AHB = SYSCLK (повна частота ядра й пам'яті) */
#define PPRE1_DIV4  (5u  << 10)   /* APB1 = HCLK / 4  — повільна периферія */
#define PPRE2_DIV2  (4u  << 13)   /* APB2 = HCLK / 2  — швидша периферія */

void clocks_setup(void) {
    /* Ядро, SRAM і DMA — на повній HCLK; дві APB навмисно повільніші,
       щоб не палити струм там, де швидкість периферії ні до чого. */
    RCC_CFGR = HPRE_DIV1 | PPRE1_DIV4 | PPRE2_DIV2;
}

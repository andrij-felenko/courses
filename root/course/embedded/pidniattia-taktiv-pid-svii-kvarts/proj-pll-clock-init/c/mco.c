#include "mco.h"
#include "clock.h"
#include "stm32f4_regs.h"

#define MCO1_PIN        8U
#define MCO1_DIVISOR    4U

void mco1_enable_pll_div4(void)
{
    /* 1. Джерело й дільник обираємо ДО того, як вивід стане альтернативною
       функцією: інакше на пін вилізе перехідний процес мультиплексора */
    RCC->CFGR = (RCC->CFGR & ~(RCC_CFGR_MCO1_MASK | RCC_CFGR_MCO1PRE_MASK))
              | RCC_CFGR_MCO1_PLL | RCC_CFGR_MCO1PRE_DIV4;

    /* 2. Тактування порту GPIOA */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    (void)RCC->AHB1ENR;   /* запис на AHB доходить із затримкою в такт */

    /* 3. PA8 у режим альтернативної функції (MODER = 10b) */
    GPIOA->MODER = (GPIOA->MODER & ~(3UL << (MCO1_PIN * 2U)))
                 | (2UL << (MCO1_PIN * 2U));

    /* 4. AF0 = MCO1; пін 8 живе в AFR[1], поле 0 */
    GPIOA->AFR[1] &= ~(0xFUL << ((MCO1_PIN - 8U) * 4U));

    /* 5. Push-pull без підтяжок: на 42 МГц підтяжка не встигне перезарядити ємність */
    GPIOA->OTYPER &= ~(1UL << MCO1_PIN);
    GPIOA->PUPDR  &= ~(3UL << (MCO1_PIN * 2U));

    /* 6. Найшвидший драйвер виходу (OSPEEDR = 11b), інакше фронти завалить
       і замість прямокутника осцилограф покаже трикутник */
    GPIOA->OSPEEDR |= (3UL << (MCO1_PIN * 2U));
}

uint32_t mco1_expected_hz(void)
{
    return clock_sysclk_hz() / MCO1_DIVISOR;
}

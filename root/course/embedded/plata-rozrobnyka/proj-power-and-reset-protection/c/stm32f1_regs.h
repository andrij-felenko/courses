/* Мінімальна карта регістрів STM32F103 (Cortex-M3) — рівно ті блоки, яких
   вимагає обв'язка плати: тактування, порти A і C, лінії зовнішніх переривань
   EXTI, таймер TIM3 і системний лічильник SysTick. Замість повного CMSIS тут
   кілька макросів: так видно, що за кожним гарним іменем стоїть звичайний
   запис у комірку пам'яті. */
#ifndef STM32F1_REGS_H
#define STM32F1_REGS_H

#include <stdint.h>

#define REG32(addr) (*(volatile uint32_t *)(addr))

/* --- Тактування периферії -------------------------------------------------- */
#define RCC_BASE            0x40021000UL
#define RCC_APB2ENR         REG32(RCC_BASE + 0x18UL)
#define RCC_APB1ENR         REG32(RCC_BASE + 0x1CUL)

#define RCC_APB2ENR_AFIOEN  (1UL << 0)
#define RCC_APB2ENR_IOPAEN  (1UL << 2)
#define RCC_APB2ENR_IOPCEN  (1UL << 4)
#define RCC_APB1ENR_TIM3EN  (1UL << 1)

/* --- Порти вводу-виводу ---------------------------------------------------- */
#define GPIOA_BASE          0x40010800UL
#define GPIOC_BASE          0x40011000UL

#define GPIO_CRL(base)      REG32((base) + 0x00UL)  /* конфігурація виводів 0..7  */
#define GPIO_CRH(base)      REG32((base) + 0x04UL)  /* конфігурація виводів 8..15 */
#define GPIO_IDR(base)      REG32((base) + 0x08UL)  /* вхідні рівні               */
#define GPIO_ODR(base)      REG32((base) + 0x0CUL)  /* вихідні защіпки            */
#define GPIO_BSRR(base)     REG32((base) + 0x10UL)  /* атомарна установка біта    */
#define GPIO_BRR(base)      REG32((base) + 0x14UL)  /* атомарне скидання біта     */

/* Тетради конфігурації: CNF (старші два біти) + MODE (молодші два). */
#define GPIO_CFG_IN_PULL    0x8UL  /* вхід із підтяжкою, напрям задає ODR        */
#define GPIO_CFG_OUT_PP_2M  0x2UL  /* вихід push-pull, 2 МГц                     */
#define GPIO_CFG_OUT_OD_2M  0x6UL  /* вихід з відкритим стоком, 2 МГц            */

/* --- Альтернативні функції та зовнішні переривання -------------------------- */
#define AFIO_BASE           0x40010000UL
#define AFIO_EXTICR1        REG32(AFIO_BASE + 0x08UL)  /* джерела ліній EXTI0..3 */

#define EXTI_BASE           0x40010400UL
#define EXTI_IMR            REG32(EXTI_BASE + 0x00UL)  /* маска переривань        */
#define EXTI_RTSR           REG32(EXTI_BASE + 0x08UL)  /* фронт угору             */
#define EXTI_FTSR           REG32(EXTI_BASE + 0x0CUL)  /* фронт униз              */
#define EXTI_PR             REG32(EXTI_BASE + 0x14UL)  /* прапорці; знімає одиниця */

/* --- Таймер загального призначення TIM3 ------------------------------------- */
#define TIM3_BASE           0x40000400UL
#define TIM3_CR1            REG32(TIM3_BASE + 0x00UL)
#define TIM3_DIER           REG32(TIM3_BASE + 0x0CUL)
#define TIM3_SR             REG32(TIM3_BASE + 0x10UL)
#define TIM3_EGR            REG32(TIM3_BASE + 0x14UL)
#define TIM3_CNT            REG32(TIM3_BASE + 0x24UL)
#define TIM3_PSC            REG32(TIM3_BASE + 0x28UL)
#define TIM3_ARR            REG32(TIM3_BASE + 0x2CUL)

#define TIM_CR1_CEN         (1UL << 0)  /* пуск лічильника                        */
#define TIM_CR1_URS         (1UL << 2)  /* подію дає лише переповнення            */
#define TIM_CR1_OPM         (1UL << 3)  /* один прохід: сам зупиниться            */
#define TIM_DIER_UIE        (1UL << 0)
#define TIM_SR_UIF          (1UL << 0)
#define TIM_EGR_UG          (1UL << 0)  /* примусове завантаження PSC/ARR         */

/* --- Системний лічильник ядра ----------------------------------------------- */
#define SYSTICK_BASE        0xE000E010UL
#define SYSTICK_CTRL        REG32(SYSTICK_BASE + 0x00UL)
#define SYSTICK_LOAD        REG32(SYSTICK_BASE + 0x04UL)
#define SYSTICK_VAL         REG32(SYSTICK_BASE + 0x08UL)

#define SYSTICK_CTRL_ENABLE     (1UL << 0)
#define SYSTICK_CTRL_TICKINT    (1UL << 1)
#define SYSTICK_CTRL_CLKSOURCE  (1UL << 2)  /* без ділення на 8: тактує HCLK      */

/* --- Контролер переривань --------------------------------------------------- */
#define NVIC_ISER0          REG32(0xE000E100UL)
#define EXTI0_IRQn          6U
#define TIM3_IRQn           29U

#endif /* STM32F1_REGS_H */

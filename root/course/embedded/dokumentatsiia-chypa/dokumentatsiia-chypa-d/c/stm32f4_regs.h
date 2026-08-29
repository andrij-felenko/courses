/* stm32f4_regs.h — регістрова карта, набрана ВРУЧНУ з документації.
 *
 * Джерела, з яких узято кожне число (саме так це й робиться на практиці):
 *   RM0090  Reference Manual STM32F405/407/415/417 — блок-схеми, зміщення
 *           регістрів, бітові поля, типи доступу;
 *   ES0182  Errata Sheet тих самих чипів — перелік дефектів кремнію;
 *   PM0214  Programming Manual Cortex-M4 — NVIC, бар'єри пам'яті DSB/ISB;
 *   DS8626  Datasheet STM32F407xx — розпіновка й альтернативні функції.
 *
 * Кожне поле структури — це рядок з карти регістрів довідника. Пропущені
 * (Reserved) слова НЕ можна викидати: структура кладеться на адресний
 * простір, і зайвий чи забутий uint32_t зсуває всі наступні регістри.
 * Тому наприкінці файла стоять _Static_assert — механічна звірка з RM0090.
 */
#ifndef STM32F4_REGS_H
#define STM32F4_REGS_H

#include <stddef.h>
#include <stdint.h>

/* ---------------------------------------------------------------------------
 * Базові адреси (RM0090, табл. 1 «Register boundary addresses»).
 * Physical_Address = Peripheral_Base_Address + Register_Offset
 * ------------------------------------------------------------------------ */
#define PERIPH_BASE     0x40000000UL
#define APB1_BASE       (PERIPH_BASE + 0x00000UL)
#define AHB1_BASE       (PERIPH_BASE + 0x20000UL)

#define TIM2_BASE       (APB1_BASE + 0x0000UL)   /* 0x40000000 */
#define I2C1_BASE       (APB1_BASE + 0x5400UL)   /* 0x40005400 */
#define GPIOB_BASE      (AHB1_BASE + 0x0400UL)   /* 0x40020400 */
#define RCC_BASE        (AHB1_BASE + 0x3800UL)   /* 0x40023800 */

/* Приватна периферія ядра — описана не в RM0090, а в PM0214 */
#define DBGMCU_BASE     0xE0042000UL
#define NVIC_ISER_BASE  0xE000E100UL
#define NVIC_IPR_BASE   0xE000E400UL

/* ---------------------------------------------------------------------------
 * Блок керування скиданням і тактуванням (RM0090 §6.3)
 * ------------------------------------------------------------------------ */
typedef struct {
    volatile uint32_t CR;           /* 0x00  R/W  керування генераторами     */
    volatile uint32_t PLLCFGR;      /* 0x04  R/W  конфігурація PLL           */
    volatile uint32_t CFGR;         /* 0x08  R/W  дільники шин AHB/APB       */
    volatile uint32_t CIR;          /* 0x0C  R/W  переривання тактування     */
    volatile uint32_t AHB1RSTR;     /* 0x10  R/W  скидання блоків AHB1       */
    volatile uint32_t AHB2RSTR;     /* 0x14  R/W                             */
    volatile uint32_t AHB3RSTR;     /* 0x18  R/W                             */
    volatile uint32_t RESERVED0;    /* 0x1C       must be kept at reset value*/
    volatile uint32_t APB1RSTR;     /* 0x20  R/W  скидання блоків APB1       */
    volatile uint32_t APB2RSTR;     /* 0x24  R/W                             */
    volatile uint32_t RESERVED1[2]; /* 0x28..0x2C                            */
    volatile uint32_t AHB1ENR;      /* 0x30  R/W  тактування блоків AHB1     */
    volatile uint32_t AHB2ENR;      /* 0x34  R/W                             */
    volatile uint32_t AHB3ENR;      /* 0x38  R/W                             */
    volatile uint32_t RESERVED2;    /* 0x3C                                  */
    volatile uint32_t APB1ENR;      /* 0x40  R/W  тактування блоків APB1     */
    volatile uint32_t APB2ENR;      /* 0x44  R/W                             */
} rcc_regs_t;

#define RCC_AHB1ENR_GPIOBEN   (1UL << 1)
#define RCC_APB1ENR_TIM2EN    (1UL << 0)
#define RCC_APB1ENR_I2C1EN    (1UL << 21)
#define RCC_APB1RSTR_TIM2RST  (1UL << 0)
#define RCC_APB1RSTR_I2C1RST  (1UL << 21)

/* ---------------------------------------------------------------------------
 * Порт введення-виведення (RM0090 §8.4)
 * ------------------------------------------------------------------------ */
typedef struct {
    volatile uint32_t MODER;    /* 0x00  R/W  режим виводу, 2 біти на ніжку  */
    volatile uint32_t OTYPER;   /* 0x04  R/W  push-pull або open-drain       */
    volatile uint32_t OSPEEDR;  /* 0x08  R/W  крутизна фронту                */
    volatile uint32_t PUPDR;    /* 0x0C  R/W  підтяжка вгору/вниз            */
    volatile uint32_t IDR;      /* 0x10  RO   реальний рівень на ніжці       */
    volatile uint32_t ODR;      /* 0x14  R/W  засувка вихідних даних         */
    volatile uint32_t BSRR;     /* 0x18  WO   W1S у [15:0], W1C у [31:16]    */
    volatile uint32_t LCKR;     /* 0x1C  R/W  замок конфігурації             */
    volatile uint32_t AFR[2];   /* 0x20  R/W  номер альтернативної функції   */
} gpio_regs_t;

/* Режими поля MODER (по 2 біти на ніжку) */
#define GPIO_MODE_INPUT   0UL
#define GPIO_MODE_OUTPUT  1UL
#define GPIO_MODE_AF      2UL
#define GPIO_MODE_ANALOG  3UL

/* Підтяжка (PUPDR, по 2 біти) */
#define GPIO_PULL_NONE    0UL
#define GPIO_PULL_UP      1UL
#define GPIO_PULL_DOWN    2UL

/* ---------------------------------------------------------------------------
 * Таймер загального призначення TIM2..TIM5 (RM0090 §18.4)
 * ------------------------------------------------------------------------ */
typedef struct {
    volatile uint32_t CR1;          /* 0x00  R/W                             */
    volatile uint32_t CR2;          /* 0x04  R/W                             */
    volatile uint32_t SMCR;         /* 0x08  R/W  режим ведомого             */
    volatile uint32_t DIER;         /* 0x0C  R/W  дозволи DMA та переривань  */
    volatile uint32_t SR;           /* 0x10  rc_w0  прапорці стану           */
    volatile uint32_t EGR;          /* 0x14  WO   генерація подій            */
    volatile uint32_t CCMR1;        /* 0x18  R/W                             */
    volatile uint32_t CCMR2;        /* 0x1C  R/W                             */
    volatile uint32_t CCER;         /* 0x20  R/W                             */
    volatile uint32_t CNT;          /* 0x24  R/W  поточний рахунок           */
    volatile uint32_t PSC;          /* 0x28  R/W  предільник (буферований)   */
    volatile uint32_t ARR;          /* 0x2C  R/W  поріг переповнення         */
    volatile uint32_t RESERVED0;    /* 0x30                                  */
    volatile uint32_t CCR[4];       /* 0x34..0x40  R/W  канали порівняння    */
    volatile uint32_t RESERVED1;    /* 0x44                                  */
    volatile uint32_t DCR;          /* 0x48  R/W                             */
    volatile uint32_t DMAR;         /* 0x4C  R/W                             */
    volatile uint32_t OR;           /* 0x50  R/W                             */
} tim_regs_t;

#define TIM_CR1_CEN    (1UL << 0)   /* Counter Enable                        */
#define TIM_CR1_UDIS   (1UL << 1)   /* Update Disable                        */
#define TIM_CR1_URS    (1UL << 2)   /* Update Request Source: лише переповнення */
#define TIM_CR1_ARPE   (1UL << 7)   /* Auto-Reload Preload Enable            */
#define TIM_DIER_UIE   (1UL << 0)   /* Update Interrupt Enable               */
#define TIM_SR_UIF     (1UL << 0)   /* Update Interrupt Flag, доступ rc_w0    */
#define TIM_EGR_UG     (1UL << 0)   /* Update Generation (програмна подія)   */

/* ---------------------------------------------------------------------------
 * Контролер шини I2C (RM0090 §27.6)
 * ------------------------------------------------------------------------ */
typedef struct {
    volatile uint32_t CR1;      /* 0x00  R/W                                 */
    volatile uint32_t CR2;      /* 0x04  R/W  поле FREQ — частота шини APB1  */
    volatile uint32_t OAR1;     /* 0x08  R/W                                 */
    volatile uint32_t OAR2;     /* 0x0C  R/W                                 */
    volatile uint32_t DR;       /* 0x10  R/W  регістр даних                  */
    volatile uint32_t SR1;      /* 0x14  змішаний доступ, частина rc_w0      */
    volatile uint32_t SR2;      /* 0x18  RO                                  */
    volatile uint32_t CCR;      /* 0x1C  R/W  дільник тактової частоти шини  */
    volatile uint32_t TRISE;    /* 0x20  R/W  максимальний час наростання    */
    volatile uint32_t FLTR;     /* 0x24  R/W  цифровий та аналоговий фільтри */
} i2c_regs_t;

#define I2C_CR1_PE       (1UL << 0)    /* Peripheral Enable                  */
#define I2C_CR1_START    (1UL << 8)
#define I2C_CR1_STOP     (1UL << 9)
#define I2C_CR1_ACK      (1UL << 10)
#define I2C_CR1_SWRST    (1UL << 15)   /* програмне скидання кінцевого автомата */
#define I2C_CR2_FREQ_MSK (0x3FUL)
#define I2C_SR2_BUSY     (1UL << 1)    /* RO: шина зайнята                   */
#define I2C_FLTR_ANOFF   (1UL << 4)    /* Analog Noise Filter OFF            */

#define I2C1_AF          4UL           /* DS8626, таблиця альтернативних функцій */
#define I2C1_SCL_PIN     6UL           /* PB6 */
#define I2C1_SDA_PIN     7UL           /* PB7 */

/* ---------------------------------------------------------------------------
 * Ідентифікація кристала (RM0090 §38.6.1, DBGMCU_IDCODE)
 * REV_ID  [31:16] — ревізія кремнію; DEV_ID [11:0] — номер сімейства.
 * ------------------------------------------------------------------------ */
typedef struct {
    volatile uint32_t IDCODE;   /* 0x00  RO                                  */
    volatile uint32_t CR;       /* 0x04  R/W                                 */
    volatile uint32_t APB1FZ;   /* 0x08  R/W                                 */
    volatile uint32_t APB2FZ;   /* 0x0C  R/W                                 */
} dbgmcu_regs_t;

/* ---------------------------------------------------------------------------
 * Указівники на блоки. volatile у полях структур — не прикраса: без нього
 * компілятор має право прибрати «зайве» читання прапорця в циклі очікування.
 * ------------------------------------------------------------------------ */
#define RCC     ((rcc_regs_t    *)RCC_BASE)
#define GPIOB   ((gpio_regs_t   *)GPIOB_BASE)
#define TIM2    ((tim_regs_t    *)TIM2_BASE)
#define I2C1    ((i2c_regs_t    *)I2C1_BASE)
#define DBGMCU  ((dbgmcu_regs_t *)DBGMCU_BASE)

/* NVIC: масиви регістрів дозволу та пріоритету переривань (PM0214 §4.2).
 * ISER — Write 1 to Set Enable, ICER — Write 1 to Clear Enable: обидва W1S,
 * тож дозвіл окремого вектора не читає й не переписує сусідні. */
#define NVIC_ISER ((volatile uint32_t *)NVIC_ISER_BASE)
#define NVIC_ICER ((volatile uint32_t *)0xE000E180UL)
#define NVIC_IPR  ((volatile uint8_t  *)NVIC_IPR_BASE)
#define TIM2_IRQn 28U               /* RM0090, таблиця векторів переривань */

/* Бар'єри пам'яті ядра (PM0214 §3.4). memory у clobber-списку забороняє
 * компілятору переставляти звернення до пам'яті через цю точку. */
#define DSB() __asm__ volatile ("dsb 0xF" ::: "memory")
#define ISB() __asm__ volatile ("isb 0xF" ::: "memory")
#define NOP() __asm__ volatile ("nop")

/* ---------------------------------------------------------------------------
 * Звірка набраної карти з довідником. Помилка в одному Reserved-слові
 * зсуває решту регістрів і виявляється лише на живій платі — краще
 * зловити її компілятором.
 * ------------------------------------------------------------------------ */
_Static_assert(offsetof(rcc_regs_t, APB1RSTR) == 0x20, "RCC_APB1RSTR має зміщення 0x20");
_Static_assert(offsetof(rcc_regs_t, AHB1ENR)  == 0x30, "RCC_AHB1ENR має зміщення 0x30");
_Static_assert(offsetof(rcc_regs_t, APB1ENR)  == 0x40, "RCC_APB1ENR має зміщення 0x40");
_Static_assert(offsetof(gpio_regs_t, BSRR)    == 0x18, "GPIOx_BSRR має зміщення 0x18");
_Static_assert(offsetof(gpio_regs_t, AFR)     == 0x20, "GPIOx_AFRL має зміщення 0x20");
_Static_assert(offsetof(tim_regs_t, SR)       == 0x10, "TIMx_SR має зміщення 0x10");
_Static_assert(offsetof(tim_regs_t, PSC)      == 0x28, "TIMx_PSC має зміщення 0x28");
_Static_assert(offsetof(tim_regs_t, ARR)      == 0x2C, "TIMx_ARR має зміщення 0x2C");
_Static_assert(offsetof(i2c_regs_t, SR2)      == 0x18, "I2C_SR2 має зміщення 0x18");
_Static_assert(offsetof(i2c_regs_t, FLTR)     == 0x24, "I2C_FLTR має зміщення 0x24");

#endif /* STM32F4_REGS_H */

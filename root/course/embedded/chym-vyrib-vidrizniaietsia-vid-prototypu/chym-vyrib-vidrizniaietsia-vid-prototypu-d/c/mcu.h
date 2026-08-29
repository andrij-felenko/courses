/* mcu.h — мінімальна карта регістрів STM32F4, потрібних цьому прикладу.
 *
 * Свідомо без CMSIS-заголовків виробника: тут видно кожну адресу й кожен біт,
 * а саме вони й є предметом розмови про перехід у безпечний стан. */
#ifndef MCU_H
#define MCU_H

#include <stdint.h>

#define REG32(addr) (*(volatile uint32_t *)(addr))

/* ---- RCC: тактування й регістр причини скидання ---------------------- */
#define RCC_BASE        0x40023800UL
#define RCC_AHB1ENR     REG32(RCC_BASE + 0x30UL)
#define RCC_APB1ENR     REG32(RCC_BASE + 0x40UL)
#define RCC_APB2ENR     REG32(RCC_BASE + 0x44UL)
#define RCC_CSR         REG32(RCC_BASE + 0x74UL)

#define RCC_AHB1ENR_GPIOAEN (1UL << 0)
#define RCC_APB1ENR_PWREN   (1UL << 28)
#define RCC_APB1ENR_USART2EN (1UL << 17)
#define RCC_APB2ENR_TIM1EN  (1UL << 0)

/* Прапорці причини останнього скидання. Тримаються до явного RMVF. */
#define RCC_CSR_LPWRRSTF (1UL << 31) /* вихід зі stop/standby зі збоєм */
#define RCC_CSR_WWDGRSTF (1UL << 30) /* віконний сторож */
#define RCC_CSR_IWDGRSTF (1UL << 29) /* незалежний сторож */
#define RCC_CSR_SFTRSTF  (1UL << 28) /* програмний рестарт */
#define RCC_CSR_PORRSTF  (1UL << 27) /* подача живлення */
#define RCC_CSR_PINRSTF  (1UL << 26) /* зовнішній вивід NRST */
#define RCC_CSR_BORRSTF  (1UL << 25) /* просідання живлення (BOR) */
#define RCC_CSR_RMVF     (1UL << 24) /* скинути прапорці */

/* ---- PWR: програмований монітор живлення (PVD) ----------------------- */
#define PWR_BASE        0x40007000UL
#define PWR_CR          REG32(PWR_BASE + 0x00UL)
#define PWR_CSR         REG32(PWR_BASE + 0x04UL)

#define PWR_CR_PVDE     (1UL << 4)
#define PWR_CR_PLS_Pos  5
#define PWR_CSR_PVDO    (1UL << 2)   /* 1 = Vdd нижче обраного порога */

/* ---- GPIOA ------------------------------------------------------------ */
#define GPIOA_BASE      0x40020000UL
#define GPIOA_MODER     REG32(GPIOA_BASE + 0x00UL)
#define GPIOA_OTYPER    REG32(GPIOA_BASE + 0x04UL)
#define GPIOA_OSPEEDR   REG32(GPIOA_BASE + 0x08UL)
#define GPIOA_PUPDR     REG32(GPIOA_BASE + 0x0CUL)
#define GPIOA_IDR       REG32(GPIOA_BASE + 0x10UL)
#define GPIOA_BSRR      REG32(GPIOA_BASE + 0x18UL)
#define GPIOA_AFRL      REG32(GPIOA_BASE + 0x20UL)

/* ---- TIM1: силовий ШІМ мостового драйвера ---------------------------- */
#define TIM1_BASE       0x40010000UL
#define TIM1_CR1        REG32(TIM1_BASE + 0x00UL)
#define TIM1_EGR        REG32(TIM1_BASE + 0x14UL)
#define TIM1_CCMR1      REG32(TIM1_BASE + 0x18UL)
#define TIM1_CCER       REG32(TIM1_BASE + 0x20UL)
#define TIM1_PSC        REG32(TIM1_BASE + 0x28UL)
#define TIM1_ARR        REG32(TIM1_BASE + 0x2CUL)
#define TIM1_CCR1       REG32(TIM1_BASE + 0x34UL)
#define TIM1_BDTR       REG32(TIM1_BASE + 0x44UL)

#define TIM1_CR1_CEN    (1UL << 0)
#define TIM1_BDTR_MOE   (1UL << 15) /* головний дозвіл виходів */
#define TIM1_CCER_CC1E  (1UL << 0)
#define TIM1_CCER_CC1NE (1UL << 2)

/* ---- IWDG: незалежний сторож на власному RC-генераторі ~32 кГц -------- */
#define IWDG_BASE       0x40003000UL
#define IWDG_KR         REG32(IWDG_BASE + 0x00UL)
#define IWDG_PR         REG32(IWDG_BASE + 0x04UL)
#define IWDG_RLR        REG32(IWDG_BASE + 0x08UL)
#define IWDG_SR         REG32(IWDG_BASE + 0x0CUL)

#define IWDG_KEY_FEED   0x0000AAAAUL
#define IWDG_KEY_UNLOCK 0x00005555UL
#define IWDG_KEY_START  0x0000CCCCUL

/* ---- USART2: діагностичний канал -------------------------------------- */
#define USART2_BASE     0x40004400UL
#define USART2_SR       REG32(USART2_BASE + 0x00UL)
#define USART2_DR       REG32(USART2_BASE + 0x04UL)
#define USART2_BRR      REG32(USART2_BASE + 0x08UL)
#define USART2_CR1      REG32(USART2_BASE + 0x0CUL)

#define USART_SR_TXE    (1UL << 7)
#define USART_SR_TC     (1UL << 6)
#define USART_CR1_UE    (1UL << 13)
#define USART_CR1_TE    (1UL << 3)

/* ---- Ядро Cortex-M4: SysTick та блок керування ------------------------ */
#define SYSTICK_BASE    0xE000E010UL
#define SYST_CSR        REG32(SYSTICK_BASE + 0x00UL)
#define SYST_RVR        REG32(SYSTICK_BASE + 0x04UL)
#define SYST_CVR        REG32(SYSTICK_BASE + 0x08UL)

#define SCB_BASE        0xE000ED00UL
#define SCB_AIRCR       REG32(SCB_BASE + 0x0CUL)
#define SCB_SHCSR       REG32(SCB_BASE + 0x24UL)
#define SCB_CFSR        REG32(SCB_BASE + 0x28UL)
#define SCB_HFSR        REG32(SCB_BASE + 0x2CUL)

#define SCB_AIRCR_KEY   0x05FA0000UL
#define SCB_AIRCR_SYSRESETREQ (1UL << 2)

static inline void mcu_dsb(void) { __asm volatile("dsb 0xF" ::: "memory"); }
static inline void mcu_isb(void) { __asm volatile("isb 0xF" ::: "memory"); }

static inline uint32_t mcu_get_msp(void)
{
    uint32_t sp;
    __asm volatile("mrs %0, msp" : "=r"(sp));
    return sp;
}

static inline void mcu_disable_irq(void) { __asm volatile("cpsid i" ::: "memory"); }

/* Програмний рестарт через блок керування ядром. Не повертається. */
static inline void mcu_system_reset(void)
{
    mcu_dsb();
    SCB_AIRCR = SCB_AIRCR_KEY | SCB_AIRCR_SYSRESETREQ;
    mcu_dsb();
    for (;;) {
        /* ядро вже перезапускається */
    }
}

#endif /* MCU_H */

#ifndef MCU_REGS_H
#define MCU_REGS_H

#include <stdint.h>

/* 32-бітний регістр, відображений у пам'ять, за абсолютною адресою */
#define MCU_REG32(addr) (*(volatile uint32_t *)(addr))

/* ---- System Control Block ядра Cortex-M (база 0xE000ED00) ---- */
#define SCB_VTOR        MCU_REG32(0xE000ED08UL) /* зсув таблиці векторів */
#define SCB_AIRCR       MCU_REG32(0xE000ED0CUL) /* скидання й пріоритети */
#define SCB_SHCSR       MCU_REG32(0xE000ED24UL) /* дозвіл системних винятків */
#define SCB_CPACR       MCU_REG32(0xE000ED88UL) /* доступ до співпроцесорів */
#define COREDEBUG_DHCSR MCU_REG32(0xE000EDF0UL) /* стан налагоджувача */

#define SCB_CPACR_CP10_FULL   (3UL << 20)  /* одинарна точність, повний доступ */
#define SCB_CPACR_CP11_FULL   (3UL << 22)  /* подвійна точність, повний доступ */
#define SCB_SHCSR_MEMFAULTENA (1UL << 16)
#define SCB_SHCSR_BUSFAULTENA (1UL << 17)
#define SCB_SHCSR_USGFAULTENA (1UL << 18)
#define DHCSR_C_DEBUGEN       (1UL << 0)   /* до ядра причеплений налагоджувач */

/* ---- RCC: дерево тактування STM32F4 (база 0x40023800) ---- */
#define RCC_CR      MCU_REG32(0x40023800UL)
#define RCC_PLLCFGR MCU_REG32(0x40023804UL)
#define RCC_CFGR    MCU_REG32(0x40023808UL)
#define RCC_CIR     MCU_REG32(0x4002380CUL)
#define RCC_AHB1ENR MCU_REG32(0x40023830UL)
#define RCC_APB2ENR MCU_REG32(0x40023844UL)

#define RCC_CR_HSION  (1UL << 0)
#define RCC_CR_HSEON  (1UL << 16)
#define RCC_CR_HSERDY (1UL << 17)
#define RCC_CR_HSEBYP (1UL << 18)
#define RCC_CR_CSSON  (1UL << 19)  /* сторож зриву кварцу */
#define RCC_CR_PLLON  (1UL << 24)
#define RCC_CR_PLLRDY (1UL << 25)

#define RCC_PLLCFGR_RESET   0x24003010UL /* заводське значення після скидання */
#define RCC_PLLCFGR_SRC_HSE (1UL << 22)

#define RCC_CFGR_SW_MASK    (3UL << 0)
#define RCC_CFGR_SW_PLL     (2UL << 0)
#define RCC_CFGR_SWS_MASK   (3UL << 2)
#define RCC_CFGR_SWS_PLL    (2UL << 2)
#define RCC_CFGR_HPRE_DIV1  (0UL << 4)   /* AHB  = SYSCLK      */
#define RCC_CFGR_PPRE1_DIV4 (5UL << 10)  /* APB1 = SYSCLK / 4  */
#define RCC_CFGR_PPRE2_DIV2 (4UL << 13)  /* APB2 = SYSCLK / 2  */

/* ---- Контролер Flash (база 0x40023C00) ---- */
#define FLASH_ACR             MCU_REG32(0x40023C00UL)
#define FLASH_ACR_LATENCY_5WS (5UL << 0)
#define FLASH_ACR_PRFTEN      (1UL << 8)
#define FLASH_ACR_ICEN        (1UL << 9)
#define FLASH_ACR_DCEN        (1UL << 10)

#endif /* MCU_REGS_H */

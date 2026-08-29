/* regs.h — карта регістрів STM32L4, потрібна для аудиту струму спокою.
 *
 * Тримаємо тут тільки те, що реально чіпаємо в цій темі: GPIO, тактування,
 * блок живлення (PWR), RTC з таймером пробудження, I2C1 і налагоджувальну
 * інфраструктуру ядра (DBGMCU, DEMCR, ITM, DWT).
 */
#ifndef REGS_H
#define REGS_H

#include <stdint.h>

#define MMIO32(addr) (*(volatile uint32_t *)(addr))

/* ---------------- GPIO ---------------- */

typedef struct {
    volatile uint32_t MODER;   /* 0x00 режим виводу: 00 вхід, 01 вихід, 10 AF, 11 аналог */
    volatile uint32_t OTYPER;  /* 0x04 */
    volatile uint32_t OSPEEDR; /* 0x08 */
    volatile uint32_t PUPDR;   /* 0x0C 00 без підтяжки, 01 pull-up, 10 pull-down */
    volatile uint32_t IDR;     /* 0x10 */
    volatile uint32_t ODR;     /* 0x14 */
    volatile uint32_t BSRR;    /* 0x18 біти 0..15 — set, 16..31 — reset */
    volatile uint32_t LCKR;    /* 0x1C */
    volatile uint32_t AFR[2];  /* 0x20/0x24 */
    volatile uint32_t BRR;     /* 0x28 */
    volatile uint32_t ASCR;    /* 0x2C аналоговий комутатор (L4) */
} gpio_t;

#define GPIOA ((gpio_t *)0x48000000UL)
#define GPIOB ((gpio_t *)0x48000400UL)
#define GPIOC ((gpio_t *)0x48000800UL)

#define MODE_INPUT   0u
#define MODE_OUTPUT  1u
#define MODE_AF      2u
#define MODE_ANALOG  3u

#define PULL_NONE    0u
#define PULL_UP      1u
#define PULL_DOWN    2u

/* ---------------- Тактування ---------------- */

#define RCC_BASE      0x40021000UL
#define RCC_CFGR      MMIO32(RCC_BASE + 0x08)
#define RCC_AHB2ENR   MMIO32(RCC_BASE + 0x4C)
#define RCC_APB1ENR1  MMIO32(RCC_BASE + 0x58)
#define RCC_BDCR      MMIO32(RCC_BASE + 0x90)

#define RCC_AHB2ENR_GPIOAEN  (1u << 0)
#define RCC_AHB2ENR_GPIOBEN  (1u << 1)
#define RCC_AHB2ENR_GPIOCEN  (1u << 2)
#define RCC_APB1ENR1_I2C1EN  (1u << 21)
#define RCC_APB1ENR1_PWREN   (1u << 28)

#define RCC_BDCR_LSEON       (1u << 0)
#define RCC_BDCR_LSERDY      (1u << 1)
#define RCC_BDCR_RTCSEL_LSE  (1u << 8)
#define RCC_BDCR_RTCEN       (1u << 15)

/* ---------------- Живлення ---------------- */

#define PWR_BASE   0x40007000UL
#define PWR_CR1    MMIO32(PWR_BASE + 0x00)
#define PWR_CR2    MMIO32(PWR_BASE + 0x04)
#define PWR_CR3    MMIO32(PWR_BASE + 0x08)
#define PWR_CR4    MMIO32(PWR_BASE + 0x0C)
#define PWR_SR1    MMIO32(PWR_BASE + 0x10)
#define PWR_SCR    MMIO32(PWR_BASE + 0x18)
#define PWR_PUCRA  MMIO32(PWR_BASE + 0x20)
#define PWR_PDCRA  MMIO32(PWR_BASE + 0x24)
#define PWR_PUCRB  MMIO32(PWR_BASE + 0x28)
#define PWR_PDCRB  MMIO32(PWR_BASE + 0x2C)
#define PWR_PUCRC  MMIO32(PWR_BASE + 0x30)
#define PWR_PDCRC  MMIO32(PWR_BASE + 0x34)

#define PWR_CR1_LPMS_MASK    (7u << 0)
#define PWR_CR1_LPMS_STOP2   (2u << 0)
#define PWR_CR1_LPMS_STANDBY (3u << 0)
#define PWR_CR1_DBP          (1u << 8)

#define PWR_CR2_PVDE         (1u << 0)   /* детектор напруги — постійний струм bandgap */

#define PWR_CR3_EWUP1        (1u << 0)   /* дозвіл виводу пробудження WKUP1 (PA0) */
#define PWR_CR3_ENULP        (1u << 9)   /* BOR/PVD опитуються імпульсно, а не безперервно */
#define PWR_CR3_APC          (1u << 10)  /* підтяжки в Standby бере з PWR_PUCRx/PDCRx */

#define PWR_CR4_WP1          (1u << 0)   /* WKUP1 спрацьовує за спадом */

#define PWR_SR1_WUF1         (1u << 0)
#define PWR_SR1_SBF          (1u << 8)
#define PWR_SCR_CWUF_ALL     (0x1Fu)
#define PWR_SCR_CSBF         (1u << 8)

/* ---------------- RTC ---------------- */

#define RTC_BASE   0x40002800UL
#define RTC_CR     MMIO32(RTC_BASE + 0x08)
#define RTC_ISR    MMIO32(RTC_BASE + 0x0C)
#define RTC_WUTR   MMIO32(RTC_BASE + 0x14)
#define RTC_WPR    MMIO32(RTC_BASE + 0x24)
#define RTC_BKP0R  MMIO32(RTC_BASE + 0x50)
#define RTC_BKP1R  MMIO32(RTC_BASE + 0x54)

#define RTC_CR_WUCKSEL_SPRE  (4u << 0)   /* такт таймера пробудження = 1 Гц */
#define RTC_CR_WUTE          (1u << 10)
#define RTC_CR_WUTIE         (1u << 14)
#define RTC_ISR_WUTWF        (1u << 2)
#define RTC_ISR_WUTF         (1u << 10)

/* ---------------- EXTI та NVIC ---------------- */

#define EXTI_BASE  0x40010400UL
#define EXTI_IMR1  MMIO32(EXTI_BASE + 0x00)
#define EXTI_RTSR1 MMIO32(EXTI_BASE + 0x08)
#define EXTI_PR1   MMIO32(EXTI_BASE + 0x14)

#define EXTI_LINE_RTC_WAKEUP (1u << 20)

#define NVIC_ISER0 MMIO32(0xE000E100UL)
#define NVIC_ICPR0 MMIO32(0xE000E280UL)
#define IRQ_RTC_WKUP 3u

/* ---------------- Ядро й налагодження ---------------- */

#define SCB_SCR          MMIO32(0xE000ED10UL)
#define SCB_SCR_SLEEPDEEP (1u << 2)

#define CORE_DHCSR       MMIO32(0xE000EDF0UL)
#define DHCSR_C_DEBUGEN  (1u << 0)   /* читається як «налагоджувач приєднаний» */
#define CORE_DEMCR       MMIO32(0xE000EDFCUL)
#define DEMCR_TRCENA     (1u << 24)

#define DWT_CTRL         MMIO32(0xE0001000UL)
#define DWT_CTRL_CYCCNTENA (1u << 0)

#define ITM_TER          MMIO32(0xE0000E00UL)
#define ITM_TCR          MMIO32(0xE0000E80UL)
#define ITM_LAR          MMIO32(0xE0000FB0UL)
#define ITM_LAR_UNLOCK   0xC5ACCE55UL
#define ITM_TCR_ITMENA   (1u << 0)

#define DBGMCU_CR        MMIO32(0xE0042004UL)
#define DBGMCU_APB1FZR1  MMIO32(0xE0042008UL)
#define DBGMCU_APB1FZR2  MMIO32(0xE004200CUL)
#define DBGMCU_APB2FZR   MMIO32(0xE0042010UL)

/* ---------------- I2C1 ---------------- */

#define I2C1_BASE    0x40005400UL
#define I2C1_CR1     MMIO32(I2C1_BASE + 0x00)
#define I2C1_CR2     MMIO32(I2C1_BASE + 0x04)
#define I2C1_TIMINGR MMIO32(I2C1_BASE + 0x10)
#define I2C1_ISR     MMIO32(I2C1_BASE + 0x18)
#define I2C1_ICR     MMIO32(I2C1_BASE + 0x1C)
#define I2C1_RXDR    MMIO32(I2C1_BASE + 0x24)
#define I2C1_TXDR    MMIO32(I2C1_BASE + 0x28)

#define I2C_CR1_PE       (1u << 0)
#define I2C_CR2_RD_WRN   (1u << 10)
#define I2C_CR2_START    (1u << 13)
#define I2C_CR2_STOP     (1u << 14)
#define I2C_CR2_AUTOEND  (1u << 25)
#define I2C_CR2_NBYTES_SHIFT 16

#define I2C_ISR_TXIS   (1u << 1)
#define I2C_ISR_RXNE   (1u << 2)
#define I2C_ISR_NACKF  (1u << 4)
#define I2C_ISR_STOPF  (1u << 5)
#define I2C_ISR_TC     (1u << 6)
#define I2C_ISR_BERR   (1u << 8)
#define I2C_ISR_ARLO   (1u << 9)
#define I2C_ISR_BUSY   (1u << 15)

#define I2C_ICR_CLEAR_ALL 0x00003F38UL

#endif /* REGS_H */

/* Карта регістрів STM32F4 (F405/F407/F411) — рівно ті блоки, які чіпає
   діагностична прошивка: RCC, GPIO, I2C1, ADC1. Адреси й розкладка бітів —
   з довідника RM0090. Нічого зайвого тут немає навмисно: bring-up-прошивка
   не має тягнути за собою чужий HAL, який сам може не завестися. */
#ifndef STM32F4_REGS_H
#define STM32F4_REGS_H

#include <stdint.h>

#define REG32(addr) (*(volatile uint32_t *)(uintptr_t)(addr))

/* ---------------- RCC: тактування ---------------- */
#define RCC_BASE        0x40023800U
#define RCC_CR          REG32(RCC_BASE + 0x00U)
#define RCC_PLLCFGR     REG32(RCC_BASE + 0x04U)
#define RCC_CFGR        REG32(RCC_BASE + 0x08U)
#define RCC_AHB1ENR     REG32(RCC_BASE + 0x30U)
#define RCC_APB1ENR     REG32(RCC_BASE + 0x40U)
#define RCC_APB2ENR     REG32(RCC_BASE + 0x44U)

#define RCC_CR_HSION    (1U << 0)
#define RCC_CR_HSIRDY   (1U << 1)
#define RCC_CR_HSEON    (1U << 16)
#define RCC_CR_HSERDY   (1U << 17)
#define RCC_CR_PLLON    (1U << 24)
#define RCC_CR_PLLRDY   (1U << 25)

/* CFGR: SW[1:0] — що просимо, SWS[3:2] — що реально працює */
#define RCC_CFGR_SW_MASK    (3U << 0)
#define RCC_CFGR_SWS_MASK   (3U << 2)

/* PLLCFGR: M[5:0], N[14:6], P[17:16], SRC[22], Q[27:24] */
#define RCC_PLLCFGR_SRC_HSE (1U << 22)

#define RCC_AHB1ENR_GPIOAEN (1U << 0)
#define RCC_AHB1ENR_GPIOBEN (1U << 1)
#define RCC_APB1ENR_I2C1EN  (1U << 21)
#define RCC_APB2ENR_ADC1EN  (1U << 8)

/* ---------------- GPIO ---------------- */
#define GPIOA_BASE          0x40020000U
#define GPIOB_BASE          0x40020400U

#define GPIO_MODER(port)    REG32((port) + 0x00U)
#define GPIO_OTYPER(port)   REG32((port) + 0x04U)
#define GPIO_OSPEEDR(port)  REG32((port) + 0x08U)
#define GPIO_PUPDR(port)    REG32((port) + 0x0CU)
#define GPIO_IDR(port)      REG32((port) + 0x10U)
#define GPIO_BSRR(port)     REG32((port) + 0x18U)
#define GPIO_AFRL(port)     REG32((port) + 0x20U)
#define GPIO_AFRH(port)     REG32((port) + 0x24U)

#define GPIO_MODE_INPUT     0U
#define GPIO_MODE_OUTPUT    1U
#define GPIO_MODE_AF        2U
#define GPIO_MODE_ANALOG    3U

#define GPIO_PULL_NONE      0U
#define GPIO_PULL_UP        1U
#define GPIO_SPEED_HIGH     2U

/* ---------------- I2C1: SCL = PB6, SDA = PB7, альтернативна функція AF4 --- */
#define I2C1_BASE       0x40005400U
#define I2C1_CR1        REG32(I2C1_BASE + 0x00U)
#define I2C1_CR2        REG32(I2C1_BASE + 0x04U)
#define I2C1_DR         REG32(I2C1_BASE + 0x10U)
#define I2C1_SR1        REG32(I2C1_BASE + 0x14U)
#define I2C1_SR2        REG32(I2C1_BASE + 0x18U)
#define I2C1_CCR        REG32(I2C1_BASE + 0x1CU)
#define I2C1_TRISE      REG32(I2C1_BASE + 0x20U)

#define I2C_CR1_PE      (1U << 0)
#define I2C_CR1_START   (1U << 8)
#define I2C_CR1_STOP    (1U << 9)
#define I2C_CR1_ACK     (1U << 10)
#define I2C_CR1_SWRST   (1U << 15)

#define I2C_SR1_SB      (1U << 0)   /* виставлено умову START */
#define I2C_SR1_ADDR    (1U << 1)   /* адресу підтверджено (ACK) */
#define I2C_SR1_AF      (1U << 10)  /* Acknowledge Failure — прийшов NACK */

#define I2C_SR2_BUSY    (1U << 1)

/* ---------------- ADC1 і спільний блок АЦП ---------------- */
#define ADC1_BASE       0x40012000U
#define ADC1_SR         REG32(ADC1_BASE + 0x00U)
#define ADC1_CR1        REG32(ADC1_BASE + 0x04U)
#define ADC1_CR2        REG32(ADC1_BASE + 0x08U)
#define ADC1_SMPR1      REG32(ADC1_BASE + 0x0CU)  /* канали 10..18 */
#define ADC1_SQR1       REG32(ADC1_BASE + 0x2CU)
#define ADC1_SQR3       REG32(ADC1_BASE + 0x34U)
#define ADC1_DR         REG32(ADC1_BASE + 0x4CU)
#define ADC_CCR         REG32(0x40012300U + 0x04U)

#define ADC_SR_EOC          (1U << 1)
#define ADC_CR2_ADON        (1U << 0)
#define ADC_CR2_SWSTART     (1U << 30)
#define ADC_CCR_ADCPRE_MASK (3U << 16)
#define ADC_CCR_ADCPRE_DIV4 (1U << 16)
#define ADC_CCR_TSVREFE     (1U << 23)

#define ADC_CHANNEL_VREFINT 17U

/* Заводська константа VREFINT: сире значення каналу 17 при VDDA = 3.30 В,
   12 біт. Адреса — для STM32F42x/F43x; на F405/F407 комірка часто не
   запрограмована, і тоді там 0x0000 або 0xFFFF (обробляємо окремо). */
#define VREFINT_CAL_ADDR    0x1FFF7A2AU

#endif /* STM32F4_REGS_H */

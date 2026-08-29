/* Регістрова мапа STM32L4 і дрібні примітиви ядра.
 *
 * HAL тут навмисно немає: уся стаття про те, які саме біти лишають плату
 * ввімкненою, а HAL ці біти й ховає за іменами на кшталт HAL_GPIO_DeInit().
 */
#ifndef MCU_H
#define MCU_H

#include <stdbool.h>
#include <stdint.h>

/* Після скидання ядро тактується від MSI 4 МГц — на ній працює приклад. */
#define CPU_HZ 4000000UL

/* ======================= порти введення-виведення ======================= */

typedef struct {
    volatile uint32_t MODER;   /* режим виводу, 2 біти на вивід */
    volatile uint32_t OTYPER;  /* 0 — двотактний, 1 — відкритий стік */
    volatile uint32_t OSPEEDR; /* швидкість фронтів */
    volatile uint32_t PUPDR;   /* внутрішні підтяжки, 2 біти на вивід */
    volatile uint32_t IDR;     /* вхідні рівні */
    volatile uint32_t ODR;     /* засувка виходу */
    volatile uint32_t BSRR;    /* атомарна установка/скидання */
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];  /* номер альтернативної функції, 4 біти на вивід */
    volatile uint32_t BRR;
} gpio_t;

#define GPIOA ((gpio_t *)0x48000000UL)
#define GPIOB ((gpio_t *)0x48000400UL)
#define GPIOC ((gpio_t *)0x48000800UL)

#define MODE_INPUT  0x0U
#define MODE_OUTPUT 0x1U
#define MODE_AF     0x2U
#define MODE_ANALOG 0x3U /* вхідний тригер Шмітта фізично від'єднано від ніжки */

#define PULL_NONE 0x0U
#define PULL_UP   0x1U
#define PULL_DOWN 0x2U

static inline void gpio_mode(gpio_t *p, unsigned pin, uint32_t mode)
{
    p->MODER = (p->MODER & ~(3UL << (pin * 2U))) | (mode << (pin * 2U));
}

static inline void gpio_pull(gpio_t *p, unsigned pin, uint32_t pull)
{
    p->PUPDR = (p->PUPDR & ~(3UL << (pin * 2U))) | (pull << (pin * 2U));
}

static inline void gpio_open_drain(gpio_t *p, unsigned pin, bool od)
{
    if (od) {
        p->OTYPER |= (1UL << pin);
    } else {
        p->OTYPER &= ~(1UL << pin);
    }
}

static inline void gpio_af(gpio_t *p, unsigned pin, uint32_t af)
{
    unsigned half = pin >> 3U;          /* AFR[0] — виводи 0..7, AFR[1] — 8..15 */
    unsigned shift = (pin & 7U) * 4U;
    p->AFR[half] = (p->AFR[half] & ~(0xFUL << shift)) | (af << shift);
    gpio_mode(p, pin, MODE_AF);
}

/* Запис через BSRR, а не через ODR: читання-модифікація-запис ODR можна
 * перервати обробником, який чіпає сусідній вивід того ж порту. */
static inline void gpio_write(gpio_t *p, unsigned pin, bool level)
{
    p->BSRR = level ? (1UL << pin) : (1UL << (pin + 16U));
}

static inline bool gpio_read(gpio_t *p, unsigned pin)
{
    return (p->IDR & (1UL << pin)) != 0U;
}

/* ============================ тактування ============================== */

typedef struct {
    volatile uint32_t CR, ICSCR, CFGR, PLLCFGR, PLLSAI1CFGR, PLLSAI2CFGR;
    volatile uint32_t CIER, CIFR, CICR, RESERVED0;
    volatile uint32_t AHB1RSTR, AHB2RSTR, AHB3RSTR, RESERVED1;
    volatile uint32_t APB1RSTR1, APB1RSTR2, APB2RSTR, RESERVED2;
    volatile uint32_t AHB1ENR, AHB2ENR, AHB3ENR, RESERVED3;
    volatile uint32_t APB1ENR1, APB1ENR2, APB2ENR, RESERVED4;
    volatile uint32_t AHB1SMENR, AHB2SMENR, AHB3SMENR, RESERVED5;
    volatile uint32_t APB1SMENR1, APB1SMENR2, APB2SMENR, RESERVED6;
    volatile uint32_t CCIPR, RESERVED7;
    volatile uint32_t BDCR, CSR;
} rcc_t;

#define RCC ((rcc_t *)0x40021000UL)

#define RCC_AHB2ENR_GPIOAEN  (1UL << 0)
#define RCC_AHB2ENR_GPIOBEN  (1UL << 1)
#define RCC_AHB2ENR_GPIOCEN  (1UL << 2)
#define RCC_APB1ENR1_USART2  (1UL << 17)
#define RCC_APB1ENR1_I2C1EN  (1UL << 21)
#define RCC_APB1ENR1_PWREN   (1UL << 28)
#define RCC_APB1ENR1_RTCAPB  (1UL << 10)
#define RCC_APB2ENR_SYSCFGEN (1UL << 0)
#define RCC_APB2ENR_SPI1EN   (1UL << 12)

#define RCC_BDCR_LSEON  (1UL << 0)
#define RCC_BDCR_LSERDY (1UL << 1)
#define RCC_BDCR_RTCSEL_LSE (1UL << 8)
#define RCC_BDCR_RTCEN  (1UL << 15)

/* ========================= керування живленням ========================= */

typedef struct {
    volatile uint32_t CR1, CR2, CR3, CR4;
    volatile uint32_t SR1, SR2, SCR, RESERVED0;
    volatile uint32_t PUCRA, PDCRA, PUCRB, PDCRB, PUCRC, PDCRC;
} pwr_t;

#define PWR ((pwr_t *)0x40007000UL)

#define PWR_CR1_LPMS_MASK  0x7UL
#define PWR_CR1_LPMS_STOP2 0x2UL
#define PWR_CR1_DBP        (1UL << 8)  /* доступ до домену резервного живлення */
#define PWR_CR3_APC        (1UL << 10) /* застосувати PUCRx/PDCRx у Standby */
#define PWR_SCR_CWUF       0x1FUL      /* скидання прапорців пробудження */

/* ============================ USART / SPI / I2C ======================== */

typedef struct {
    volatile uint32_t CR1, CR2, CR3, BRR, GTPR, RTOR, RQR, ISR, ICR, RDR, TDR;
} usart_t;

#define USART2 ((usart_t *)0x40004400UL)

#define USART_CR1_UE   (1UL << 0)
#define USART_CR1_TE   (1UL << 3)
#define USART_ISR_TXE  (1UL << 7)  /* буферний регістр вільний */
#define USART_ISR_TC   (1UL << 6)  /* кадр ПОВНІСТЮ вийшов на лінію */
#define USART_ISR_BUSY (1UL << 16)

typedef struct {
    volatile uint32_t CR1, CR2, SR, DR;
} spi_t;

#define SPI1 ((spi_t *)0x40013000UL)

#define SPI_CR1_SPE   (1UL << 6)
#define SPI_SR_BSY    (1UL << 7)
#define SPI_SR_FTLVL  (3UL << 11) /* скільки байтів іще лежить у черзі передачі */

typedef struct {
    volatile uint32_t CR1, CR2, OAR1, OAR2, TIMINGR, TIMEOUTR;
    volatile uint32_t ISR, ICR, PECR, RXDR, TXDR;
} i2c_t;

#define I2C1 ((i2c_t *)0x40005400UL)

#define I2C_CR1_PE      (1UL << 0)
#define I2C_CR2_RD_WRN  (1UL << 10)
#define I2C_CR2_START   (1UL << 13)
#define I2C_CR2_STOP    (1UL << 14)
#define I2C_CR2_AUTOEND (1UL << 25)
#define I2C_ISR_TXIS    (1UL << 1)
#define I2C_ISR_RXNE    (1UL << 2)
#define I2C_ISR_TC      (1UL << 6)
#define I2C_CR2_SADD(a7)   (((uint32_t)(a7) << 1) & 0x3FFUL)
#define I2C_CR2_NBYTES(n)  (((uint32_t)(n) & 0xFFUL) << 16)
#define I2C_ISR_NACKF   (1UL << 4)
#define I2C_ISR_STOPF   (1UL << 5)
#define I2C_ISR_BUSY    (1UL << 15)
#define I2C_ICR_NACKCF  (1UL << 4)
#define I2C_ICR_STOPCF  (1UL << 5)

/* ======================== EXTI, SYSCFG, RTC, NVIC ====================== */

typedef struct {
    volatile uint32_t IMR1, EMR1, RTSR1, FTSR1, SWIER1, PR1;
} exti_t;

#define EXTI ((exti_t *)0x40010400UL)

typedef struct {
    volatile uint32_t MEMRMP, CFGR1, EXTICR[4];
} syscfg_t;

#define SYSCFG ((syscfg_t *)0x40010000UL)

typedef struct {
    volatile uint32_t TR, DR, CR, ISR, PRER, WUTR, RESERVED0;
    volatile uint32_t ALRMAR, ALRMBR, WPR;
} rtc_t;

#define RTC ((rtc_t *)0x40002800UL)

#define RTC_CR_WUTE      (1UL << 10)
#define RTC_CR_WUTIE     (1UL << 14)
#define RTC_CR_WUCKSEL_1HZ (4UL << 0) /* лічильник від ck_spre = 1 Гц */
#define RTC_ISR_WUTWF    (1UL << 2)   /* WUTR можна переписувати */
#define RTC_ISR_WUTF     (1UL << 10)

#define NVIC_ISER ((volatile uint32_t *)0xE000E100UL)
#define NVIC_ICER ((volatile uint32_t *)0xE000E180UL)
#define NVIC_ICPR ((volatile uint32_t *)0xE000E280UL)

#define IRQ_RTC_WKUP 3U
#define IRQ_EXTI0    6U

static inline void nvic_enable(unsigned irq)
{
    NVIC_ISER[irq >> 5U] = (1UL << (irq & 31U));
}

static inline void nvic_clear_pending(unsigned irq)
{
    NVIC_ICPR[irq >> 5U] = (1UL << (irq & 31U));
}

#define SCB_SCR   (*(volatile uint32_t *)0xE000ED10UL)
#define SCB_SCR_SLEEPDEEP (1UL << 2)

/* Блок налагодження. DBGMCU_CR тримає тактове дерево живим у Stop/Standby —
 * саме він і є той «завжди ввімкнений вузол», який ловлять на столі. */
#define DBGMCU_CR (*(volatile uint32_t *)0xE0042004UL)

#define DBGMCU_CR_DBG_SLEEP   (1UL << 0)
#define DBGMCU_CR_DBG_STOP    (1UL << 1)
#define DBGMCU_CR_DBG_STANDBY (1UL << 2)

/* ========================== примітиви ядра ============================= */

static inline void mcu_dsb(void) { __asm volatile("dsb 0xF" ::: "memory"); }
static inline void mcu_isb(void) { __asm volatile("isb 0xF" ::: "memory"); }
static inline void mcu_wfi(void) { __asm volatile("wfi"); }

static inline void mcu_irq_disable(void) { __asm volatile("cpsid i" ::: "memory"); }
static inline void mcu_irq_enable(void)  { __asm volatile("cpsie i" ::: "memory"); }

/* Затримка порожнім циклом, а не лічильником тактів DWT: щоб DWT рахував,
 * треба лишити ввімкненим TRCENA, тобто той самий блок трасування, який ця
 * стаття вчить вимикати. Точність тут не потрібна — потрібні мілісекунди
 * розряду ємностей, і похибка в чверть їх не зіпсує. */
static inline void mcu_delay_us(uint32_t us)
{
    /* тіло циклу — приблизно чотири такти на ітерацію */
    uint32_t loops = (uint32_t)(((uint64_t)us * (CPU_HZ / 1000000UL)) / 4U);
    while (loops-- != 0U) {
        __asm volatile("nop");
    }
}

static inline void mcu_delay_ms(uint32_t ms)
{
    while (ms-- != 0U) {
        mcu_delay_us(1000U);
    }
}

#endif /* MCU_H */

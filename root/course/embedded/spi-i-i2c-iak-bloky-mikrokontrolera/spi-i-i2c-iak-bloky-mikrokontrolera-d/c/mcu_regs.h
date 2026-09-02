#ifndef MCU_REGS_H
#define MCU_REGS_H

#include <stdint.h>

/* Карта регістрів STM32F4 (RM0090) — рівно стільки, скільки треба блокам
   SPI1, I2C1, GPIO і DMA2. HAL навмисно не беремо: у цій темі важливо
   бачити самі регістри й прапорці, а не обгортку над ними. */

typedef struct {
    volatile uint32_t CR1;   /* MSTR, BR, CPOL, CPHA, SPE, SSM, SSI */
    volatile uint32_t CR2;   /* TXEIE, RXNEIE, ERRIE, TXDMAEN, RXDMAEN */
    volatile uint32_t SR;    /* TXE, RXNE, OVR, MODF, BSY */
    volatile uint32_t DR;    /* вікно у пару буферів Tx/Rx */
    volatile uint32_t CRCPR;
    volatile uint32_t RXCRCR;
    volatile uint32_t TXCRCR;
    volatile uint32_t I2SCFGR;
    volatile uint32_t I2SPR;
} spi_regs_t;

#define SPI_CR1_CPHA      (1U << 0)
#define SPI_CR1_CPOL      (1U << 1)
#define SPI_CR1_MSTR      (1U << 2)
#define SPI_CR1_BR_POS    3U
#define SPI_CR1_BR_MSK    (7U << 3)
#define SPI_CR1_SPE       (1U << 6)
#define SPI_CR1_LSBFIRST  (1U << 7)
#define SPI_CR1_SSI       (1U << 8)
#define SPI_CR1_SSM       (1U << 9)
#define SPI_CR1_DFF       (1U << 11)

#define SPI_CR2_RXDMAEN   (1U << 0)
#define SPI_CR2_TXDMAEN   (1U << 1)
#define SPI_CR2_SSOE      (1U << 2)
#define SPI_CR2_ERRIE     (1U << 5)
#define SPI_CR2_RXNEIE    (1U << 6)
#define SPI_CR2_TXEIE     (1U << 7)

#define SPI_SR_RXNE       (1U << 0)
#define SPI_SR_TXE        (1U << 1)
#define SPI_SR_CRCERR     (1U << 4)
#define SPI_SR_MODF       (1U << 5)
#define SPI_SR_OVR        (1U << 6)
#define SPI_SR_BSY        (1U << 7)

typedef struct {
    volatile uint32_t CR1;   /* PE, START, STOP, ACK, POS, SWRST */
    volatile uint32_t CR2;   /* FREQ, ITERREN, ITEVTEN, DMAEN */
    volatile uint32_t OAR1;  /* власна адреса веденого — апаратний компаратор */
    volatile uint32_t OAR2;
    volatile uint32_t DR;
    volatile uint32_t SR1;   /* SB, ADDR, BTF, RXNE, TXE, BERR, ARLO, AF, TIMEOUT */
    volatile uint32_t SR2;   /* MSL, BUSY, TRA */
    volatile uint32_t CCR;
    volatile uint32_t TRISE;
    volatile uint32_t FLTR;  /* аналоговий і цифровий фільтри сплесків */
} i2c_regs_t;

#define I2C_CR1_PE        (1U << 0)
#define I2C_CR1_NOSTRETCH (1U << 7)
#define I2C_CR1_START     (1U << 8)
#define I2C_CR1_STOP      (1U << 9)
#define I2C_CR1_ACK       (1U << 10)
#define I2C_CR1_POS       (1U << 11)
#define I2C_CR1_SWRST     (1U << 15)

#define I2C_CR2_FREQ_MSK  (0x3FU)
#define I2C_CR2_ITERREN   (1U << 8)
#define I2C_CR2_ITEVTEN   (1U << 9)
#define I2C_CR2_ITBUFEN   (1U << 10)

#define I2C_SR1_SB        (1U << 0)
#define I2C_SR1_ADDR      (1U << 1)
#define I2C_SR1_BTF       (1U << 2)
#define I2C_SR1_STOPF     (1U << 4)
#define I2C_SR1_RXNE      (1U << 6)
#define I2C_SR1_TXE       (1U << 7)
#define I2C_SR1_BERR      (1U << 8)
#define I2C_SR1_ARLO      (1U << 9)
#define I2C_SR1_AF        (1U << 10)
#define I2C_SR1_OVR       (1U << 11)
#define I2C_SR1_TIMEOUT   (1U << 14)

#define I2C_SR2_MSL       (1U << 0)
#define I2C_SR2_BUSY      (1U << 1)
#define I2C_SR2_TRA       (1U << 2)

#define I2C_CCR_DUTY      (1U << 14)
#define I2C_CCR_FS        (1U << 15)

typedef struct {
    volatile uint32_t MODER, OTYPER, OSPEEDR, PUPDR;
    volatile uint32_t IDR, ODR, BSRR, LCKR;
    volatile uint32_t AFR[2];
} gpio_regs_t;

typedef struct {
    volatile uint32_t CR, NDTR, PAR, M0AR, M1AR, FCR;
} dma_stream_t;

typedef struct {
    volatile uint32_t LISR, HISR, LIFCR, HIFCR;
    dma_stream_t S[8];
} dma_regs_t;

#define DMA_CR_EN         (1U << 0)
#define DMA_CR_TEIE       (1U << 2)
#define DMA_CR_TCIE       (1U << 4)
#define DMA_CR_DIR_M2P    (1U << 6)   /* пам'ять -> периферія */
#define DMA_CR_PINC       (1U << 9)
#define DMA_CR_MINC       (1U << 10)
#define DMA_CR_PL_HIGH    (2U << 16)
#define DMA_CR_CHSEL_POS  25U

typedef struct {
    volatile uint32_t CR, PLLCFGR, CFGR, CIR;
    volatile uint32_t AHB1RSTR, AHB2RSTR, AHB3RSTR, RESERVED0;
    volatile uint32_t APB1RSTR, APB2RSTR, RESERVED1[2];
    volatile uint32_t AHB1ENR, AHB2ENR, AHB3ENR, RESERVED2;
    volatile uint32_t APB1ENR, APB2ENR;
} rcc_regs_t;

#define RCC_AHB1ENR_GPIOAEN (1U << 0)
#define RCC_AHB1ENR_GPIOBEN (1U << 1)
#define RCC_AHB1ENR_DMA2EN  (1U << 22)
#define RCC_APB1ENR_I2C1EN  (1U << 21)
#define RCC_APB2ENR_SPI1EN  (1U << 12)

#define RCC   ((rcc_regs_t  *)0x40023800U)
#define GPIOA ((gpio_regs_t *)0x40020000U)
#define GPIOB ((gpio_regs_t *)0x40020400U)
#define SPI1  ((spi_regs_t  *)0x40013000U)
#define I2C1  ((i2c_regs_t  *)0x40005400U)
#define DMA2  ((dma_regs_t  *)0x40026400U)

/* Номери переривань з таблиці векторів STM32F4 */
#define IRQ_SPI1          35U
#define IRQ_DMA2_STREAM2  58U
#define IRQ_DMA2_STREAM3  59U

#define NVIC_ISER ((volatile uint32_t *)0xE000E100U)

static inline void nvic_enable_irq(uint32_t irqn)
{
    NVIC_ISER[irqn >> 5] = 1U << (irqn & 31U);
}

/* Груба затримка холостим циклом: ядро 168 МГц, тіло ~4 такти.
   Для дев'яти тактів відновлення шини точність не потрібна — важливо
   лише не перевищити 100 кГц, тобто не бути ШВИДШИМ за розрахунок. */
static inline void delay_us(uint32_t us)
{
    volatile uint32_t n = us * 42U;
    while (n--) {
        __asm volatile ("nop");
    }
}

#endif /* MCU_REGS_H */

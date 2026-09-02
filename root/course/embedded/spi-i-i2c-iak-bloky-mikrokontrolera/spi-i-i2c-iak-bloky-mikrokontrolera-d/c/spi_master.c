#include "spi_master.h"

/* SPI1 на STM32F4: PA5 = SCK, PA6 = MISO, PA7 = MOSI (усі AF5),
   PA4 = CS звичайним GPIO. Апаратний NSS вимкнено (SSM=1, SSI=1) —
   інакше блок ловив би MODF щоразу, коли рівень на ніжці NSS падає в нуль. */
#define CS_PIN 4U

static void pins_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

    for (unsigned pin = 5U; pin <= 7U; ++pin) {
        GPIOA->MODER   &= ~(3U << (pin * 2U));
        GPIOA->MODER   |=  (2U << (pin * 2U));   /* альтернативна функція */
        GPIOA->OSPEEDR |=  (3U << (pin * 2U));   /* дуже висока швидкість фронтів */
        GPIOA->AFR[0]  &= ~(0xFU << (pin * 4U));
        GPIOA->AFR[0]  |=  (5U << (pin * 4U));   /* AF5 = SPI1 */
    }

    GPIOA->MODER &= ~(3U << (CS_PIN * 2U));
    GPIOA->MODER |=  (1U << (CS_PIN * 2U));      /* вихід push-pull */
    GPIOA->BSRR   =  (1U << CS_PIN);             /* у спокої CS високий */
}

void spi1_master_init(spi_mode_t mode, uint8_t br)
{
    pins_init();
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;

    /* Налаштовувати можна лише вимкнений блок: спершу SPE=0 */
    SPI1->CR1 = 0U;
    SPI1->CR2 = 0U;

    uint32_t cr1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI;
    cr1 |= ((uint32_t)br & 7U) << SPI_CR1_BR_POS;
    if (mode == SPI_MODE1 || mode == SPI_MODE3) {
        cr1 |= SPI_CR1_CPHA;   /* захоплення на другому фронті */
    }
    if (mode == SPI_MODE2 || mode == SPI_MODE3) {
        cr1 |= SPI_CR1_CPOL;   /* у спокої SCK високий */
    }

    SPI1->CR1 = cr1;
    SPI1->CR1 |= SPI_CR1_SPE;
}

void spi1_cs_select(void)
{
    GPIOA->BSRR = (1U << (CS_PIN + 16U));  /* притискаємо CS до землі */
}

void spi1_cs_release(void)
{
    GPIOA->BSRR = (1U << CS_PIN);
}

void spi_clear_overrun(spi_regs_t *spi)
{
    /* Строга послідовність: читання DR, потім читання SR.
       Без неї приймач лишається заблокованим назавжди. */
    (void)spi->DR;
    (void)spi->SR;
}

void spi_recover_mode_fault(spi_regs_t *spi)
{
    /* MODF апаратно скинув SPE й перевів блок у ведені. Прапорець
       знімається читанням SR і подальшим записом у CR1; після цього
       роль ведучого треба відновити руками. */
    (void)spi->SR;
    uint32_t cr1 = spi->CR1;
    spi->CR1 = cr1 & ~SPI_CR1_SPE;
    spi->CR1 = (cr1 | SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI) & ~SPI_CR1_SPE;
    spi->CR1 |= SPI_CR1_SPE;
}

spi_status_t spi_wait_idle(spi_regs_t *spi, uint32_t budget)
{
    while (spi->SR & SPI_SR_BSY) {
        if (--budget == 0U) {
            return SPI_ERR_TIMEOUT;
        }
    }
    return SPI_OK;
}

spi_status_t spi_transfer_byte(spi_regs_t *spi, uint8_t tx, uint8_t *rx, uint32_t budget)
{
    uint32_t left = budget;

    /* 1. Чекаємо, поки звільниться буфер передачі (TXE=1) */
    while (!(spi->SR & SPI_SR_TXE)) {
        if (spi->SR & SPI_SR_MODF) {
            spi_recover_mode_fault(spi);
            return SPI_ERR_MODE_FAULT;
        }
        if (--left == 0U) {
            return SPI_ERR_TIMEOUT;
        }
    }

    /* 2. Запис у DR штовхає байт у зсувний регістр і запускає генератор SCK */
    spi->DR = tx;

    /* 3. Кожен переданий байт означає й прийнятий: чекаємо RXNE */
    left = budget;
    while (!(spi->SR & SPI_SR_RXNE)) {
        uint32_t sr = spi->SR;
        if (sr & SPI_SR_OVR) {
            spi_clear_overrun(spi);
            return SPI_ERR_OVERRUN;
        }
        if (sr & SPI_SR_MODF) {
            spi_recover_mode_fault(spi);
            return SPI_ERR_MODE_FAULT;
        }
        if (--left == 0U) {
            return SPI_ERR_TIMEOUT;
        }
    }

    /* 4. Читання DR забирає байт із буфера прийому й скидає RXNE */
    uint8_t received = (uint8_t)(spi->DR & 0xFFU);
    if (rx != NULL) {
        *rx = received;
    }
    return SPI_OK;
}

spi_status_t spi_transfer(spi_regs_t *spi, const uint8_t *tx, uint8_t *rx,
                          size_t len, uint32_t budget)
{
    if (spi == NULL || len == 0U) {
        return SPI_ERR_ARG;
    }

    for (size_t i = 0; i < len; ++i) {
        /* Немає буфера передачі — женемо 0xFF: багато мікросхем пам'яті
           саме так чекають фазу читання. */
        uint8_t out = (tx != NULL) ? tx[i] : 0xFFU;
        spi_status_t st = spi_transfer_byte(spi, out, (rx != NULL) ? &rx[i] : NULL, budget);
        if (st != SPI_OK) {
            return st;
        }
    }

    /* Знімати CS можна лише після того, як останній біт вийшов у лінію */
    return spi_wait_idle(spi, budget);
}

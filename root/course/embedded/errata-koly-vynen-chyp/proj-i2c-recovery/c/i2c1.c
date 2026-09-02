#include "i2c1.h"

#include "delay.h"
#include "stm32f10x.h"

/* Стеля очікування однієї події. Байт на 100 кГц їде 90 мкс, тож 2 мс — це вже
   явно не «повільно», а «ніхто не відповідає». */
#define EVENT_TIMEOUT_US  2000U

static i2c_status_t wait_sr1(uint16_t flag) {
    uint32_t waited;
    for (waited = 0U; waited < EVENT_TIMEOUT_US; ++waited) {
        const uint16_t sr1 = I2C1->SR1;

        if ((sr1 & I2C_SR1_AF) != 0U) {
            I2C1->SR1 = (uint16_t)(sr1 & ~I2C_SR1_AF);   /* прапорець знімається записом нуля */
            I2C1->CR1 |= I2C_CR1_STOP;
            return I2C_ERR_NACK;
        }
        if ((sr1 & I2C_SR1_BERR) != 0U) {
            I2C1->SR1 = (uint16_t)(sr1 & ~I2C_SR1_BERR);
            I2C1->CR1 |= I2C_CR1_STOP;
            return I2C_ERR_BUS;
        }
        if ((sr1 & flag) != 0U) {
            return I2C_OK;
        }
        delay_us(1U);
    }

    I2C1->CR1 |= I2C_CR1_STOP;   /* спроба звільнити шину по-доброму */
    return I2C_ERR_TIMEOUT;
}

void i2c1_init(uint32_t bus_hz) {
    uint32_t pclk1;
    uint32_t pclk1_mhz;
    uint32_t ccr;

    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* Програмне скидання всередині блоку: після нього всі регістри в нулях */
    I2C1->CR1 = I2C_CR1_SWRST;
    delay_us(2U);
    I2C1->CR1 = 0U;

    SystemCoreClockUpdate();
    pclk1 = SystemCoreClock / 2U;    /* дільник APB1 = 2: 36 МГц при ядрі 72 МГц */
    pclk1_mhz = pclk1 / 1000000U;

    I2C1->CR2 = (uint16_t)pclk1_mhz;             /* модулю треба знати частоту входу */

    ccr = pclk1 / (2U * bus_hz);                 /* стандартний режим: T_low = T_high */
    if (ccr < 4U) {
        ccr = 4U;                                /* нижня межа за RM0008 */
    }
    I2C1->CCR = (uint16_t)ccr;
    I2C1->TRISE = (uint16_t)(pclk1_mhz + 1U);    /* 1000 нс максимального фронту */

    I2C1->CR1 = I2C_CR1_PE;
}

i2c_status_t i2c1_read_register(uint8_t addr7, uint8_t reg, uint8_t *value) {
    i2c_status_t st;
    uint32_t waited;

    /* Той самий BUSY, що о другій ночі стоїть при чистих 3.3 В на обох лініях.
       У нормі він знімається за такт-два, тож довге очікування означає не
       зайнятість, а заклинену шину — і кличе процедуру відновлення. */
    for (waited = 0U; (I2C1->SR2 & I2C_SR2_BUSY) != 0U; ++waited) {
        if (waited >= EVENT_TIMEOUT_US) {
            return I2C_ERR_BUSY;
        }
        delay_us(1U);
    }

    I2C1->CR1 |= I2C_CR1_ACK | I2C_CR1_START;
    st = wait_sr1(I2C_SR1_SB);
    if (st != I2C_OK) {
        return st;
    }

    I2C1->DR = (uint16_t)(addr7 << 1);           /* адреса + біт запису */
    st = wait_sr1(I2C_SR1_ADDR);
    if (st != I2C_OK) {
        return st;
    }
    (void)I2C1->SR1;
    (void)I2C1->SR2;                             /* читання пари знімає ADDR */

    I2C1->DR = reg;                              /* номер регістра всередині чипа */
    st = wait_sr1(I2C_SR1_BTF);
    if (st != I2C_OK) {
        return st;
    }

    /* Повторний START: віддавати шину між записом номера й читанням не можна,
       інакше чужий мастер зіб'є вказівник регістра. */
    I2C1->CR1 |= I2C_CR1_START;
    st = wait_sr1(I2C_SR1_SB);
    if (st != I2C_OK) {
        return st;
    }

    I2C1->DR = (uint16_t)((addr7 << 1) | 1U);    /* адреса + біт читання */
    st = wait_sr1(I2C_SR1_ADDR);
    if (st != I2C_OK) {
        return st;
    }

    /* Один байт: ACK знімаємо ДО зняття ADDR і ставимо STOP одразу після, і все
       це без переривань. Спізнимося на кілька тактів — чип отримає зайве
       підтвердження й почне віддавати другий байт (RM0008, випадок N = 1). */
    I2C1->CR1 &= ~I2C_CR1_ACK;
    __disable_irq();
    (void)I2C1->SR1;
    (void)I2C1->SR2;
    I2C1->CR1 |= I2C_CR1_STOP;
    __enable_irq();

    st = wait_sr1(I2C_SR1_RXNE);
    if (st != I2C_OK) {
        return st;
    }
    *value = (uint8_t)I2C1->DR;

    /* Чекаємо, доки апаратура догенерує STOP: наступний START поверх недоробленого
       STOP — класичний спосіб самому загнати модуль у вічний BUSY. */
    for (waited = 0U; (I2C1->CR1 & I2C_CR1_STOP) != 0U; ++waited) {
        if (waited >= EVENT_TIMEOUT_US) {
            return I2C_ERR_TIMEOUT;
        }
        delay_us(1U);
    }

    I2C1->CR1 |= I2C_CR1_ACK;
    return I2C_OK;
}

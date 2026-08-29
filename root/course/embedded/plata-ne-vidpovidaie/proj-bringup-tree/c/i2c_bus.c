/* Фаза 3: шина I2C — розблокування, ініціалізація, сканування адрес.
   Порядок саме такий: спершу звільняємо лінії руками, і лише потім віддаємо
   виводи периферії. Модуль, який побачив BUSY на старті, стану START не
   виставить ніколи. */
#include "bringup.h"
#include "stm32f4_regs.h"

#define I2C_PORT           GPIOB_BASE
#define PIN_SCL            6U
#define PIN_SDA            7U
#define I2C_AF             4U
#define I2C_SPEED_HZ       100000U
#define BUS_CLEAR_HALF_US  5U      /* ручні такти ~100 кГц */
#define BUS_CLEAR_PULSES   9U      /* рівно байт + біт підтвердження */
#define I2C_EVENT_TRIES    20000U

/* ---- дрібні дії над виводом: у C це просто функції над номером ---- */

static void pin_release_as_open_drain(uint32_t pin)
{
    uint32_t two = pin * 2U;

    /* Спершу відпускаємо лінію в ODR, і лише потім вмикаємо вихід —
       інакше на мить смикнемо шину в нуль і зіпсуємо чужу транзакцію. */
    GPIO_BSRR(I2C_PORT) = (1U << pin);
    GPIO_OTYPER(I2C_PORT) |= (1U << pin);
    GPIO_PUPDR(I2C_PORT) = (GPIO_PUPDR(I2C_PORT) & ~(3U << two))
                         | (GPIO_PULL_UP << two);
    GPIO_OSPEEDR(I2C_PORT) = (GPIO_OSPEEDR(I2C_PORT) & ~(3U << two))
                           | (GPIO_SPEED_HIGH << two);
    GPIO_MODER(I2C_PORT) = (GPIO_MODER(I2C_PORT) & ~(3U << two))
                         | (GPIO_MODE_OUTPUT << two);
}

static void pin_to_i2c_alternate(uint32_t pin)
{
    uint32_t two = pin * 2U;
    uint32_t shift = (pin % 8U) * 4U;

    if (pin < 8U) {
        GPIO_AFRL(I2C_PORT) = (GPIO_AFRL(I2C_PORT) & ~(0xFU << shift))
                            | (I2C_AF << shift);
    } else {
        GPIO_AFRH(I2C_PORT) = (GPIO_AFRH(I2C_PORT) & ~(0xFU << shift))
                            | (I2C_AF << shift);
    }
    GPIO_OTYPER(I2C_PORT) |= (1U << pin);
    GPIO_PUPDR(I2C_PORT) = (GPIO_PUPDR(I2C_PORT) & ~(3U << two))
                         | (GPIO_PULL_UP << two);
    GPIO_MODER(I2C_PORT) = (GPIO_MODER(I2C_PORT) & ~(3U << two))
                         | (GPIO_MODE_AF << two);
}

static bool pin_level(uint32_t pin)
{
    return (GPIO_IDR(I2C_PORT) & (1U << pin)) != 0U;
}

static void pin_drive(uint32_t pin, bool high)
{
    GPIO_BSRR(I2C_PORT) = high ? (1U << pin) : (1U << (pin + 16));
}

/* ---- розблокування завислої шини (Bus Clear) ---- */

bringup_status_t bringup_i2c_bus_clear(bool *was_stuck)
{
    uint32_t pulse;

    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    (void)RCC_AHB1ENR;

    /* Поки модуль увімкнений, виводи належать йому — GPIO ними не покерує. */
    I2C1_CR1 &= ~I2C_CR1_PE;

    pin_release_as_open_drain(PIN_SCL);
    pin_release_as_open_drain(PIN_SDA);
    bringup_delay_us(BUS_CLEAR_HALF_US);

    *was_stuck = !pin_level(PIN_SDA);
    if (!*was_stuck) {
        pin_to_i2c_alternate(PIN_SCL);
        pin_to_i2c_alternate(PIN_SDA);
        return BRINGUP_OK;
    }

    /* Дев'ять тактів на SCL: ведений досилає решту поточного байта, доходить
       до біта ACK/NACK і відпускає SDA. Виходимо раніше, щойно лінія піднялася. */
    for (pulse = 0U; pulse < BUS_CLEAR_PULSES && !pin_level(PIN_SDA); ++pulse) {
        pin_drive(PIN_SCL, false);
        bringup_delay_us(BUS_CLEAR_HALF_US);
        pin_drive(PIN_SCL, true);
        bringup_delay_us(BUS_CLEAR_HALF_US);
    }

    if (!pin_level(PIN_SDA)) {
        /* Лінія тримається навіть після повного байта тактів: це вже не
           зависла транзакція, а закорочена доріжка або мертвий ведений. */
        pin_to_i2c_alternate(PIN_SCL);
        pin_to_i2c_alternate(PIN_SDA);
        return BRINGUP_ERR_I2C_BUS_STUCK;
    }

    /* Коректна умова STOP: SDA переходить 0 → 1 при високому SCL. */
    pin_drive(PIN_SCL, false);
    pin_drive(PIN_SDA, false);
    bringup_delay_us(BUS_CLEAR_HALF_US);
    pin_drive(PIN_SCL, true);
    bringup_delay_us(BUS_CLEAR_HALF_US);
    pin_drive(PIN_SDA, true);
    bringup_delay_us(BUS_CLEAR_HALF_US);

    pin_to_i2c_alternate(PIN_SCL);
    pin_to_i2c_alternate(PIN_SDA);
    return BRINGUP_OK;
}

/* ---- ініціалізація модуля ---- */

void bringup_i2c_init(void)
{
    uint32_t pclk_mhz = BRINGUP_PCLK1_HZ / 1000000U;
    uint32_t ccr = BRINGUP_PCLK1_HZ / (2U * I2C_SPEED_HZ);

    RCC_AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    RCC_APB1ENR |= RCC_APB1ENR_I2C1EN;
    (void)RCC_APB1ENR;

    pin_to_i2c_alternate(PIN_SCL);
    pin_to_i2c_alternate(PIN_SDA);

    /* Програмне скидання модуля: після зависання шини він лишається у стані
       BUSY, і зняти цей стан можна тільки через SWRST. */
    I2C1_CR1 = I2C_CR1_SWRST;
    I2C1_CR1 = 0U;

    if (ccr < 4U) {
        ccr = 4U;  /* межа стандартного режиму */
    }
    I2C1_CR2 = pclk_mhz;        /* FREQ: модуль має знати частоту APB1 */
    I2C1_CCR = ccr;             /* Sm-режим: половина періоду в тактах APB1 */
    I2C1_TRISE = pclk_mhz + 1U; /* максимальний фронт 1000 нс */
    I2C1_CR1 |= I2C_CR1_PE;
}

/* ---- проба однієї адреси ---- */

bringup_status_t bringup_i2c_probe_address(uint8_t addr_7bit)
{
    uint32_t tries;
    uint32_t sr1;

    /* Шина мусить бути вільна: інакше START просто не піде. */
    tries = I2C_EVENT_TRIES;
    while ((I2C1_SR2 & I2C_SR2_BUSY) != 0U && tries > 0U) {
        --tries;
    }
    if (tries == 0U) {
        return BRINGUP_ERR_I2C_TIMEOUT;
    }

    I2C1_CR1 |= I2C_CR1_START;
    tries = I2C_EVENT_TRIES;
    while ((I2C1_SR1 & I2C_SR1_SB) == 0U && tries > 0U) {
        --tries;
    }
    if (tries == 0U) {
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_TIMEOUT;
    }

    /* SB знімається читанням SR1 із наступним записом у DR. */
    (void)I2C1_SR1;
    I2C1_DR = (uint32_t)((uint32_t)addr_7bit << 1);  /* біт напрямку 0 — запис */

    tries = I2C_EVENT_TRIES;
    while (((I2C1_SR1 & (I2C_SR1_ADDR | I2C_SR1_AF)) == 0U) && tries > 0U) {
        --tries;
    }

    sr1 = I2C1_SR1;
    if ((sr1 & I2C_SR1_AF) != 0U) {
        /* NACK: за цією адресою ніхто не притиснув SDA на дев'ятому такті. */
        I2C1_SR1 &= ~I2C_SR1_AF;
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_NACK;
    }
    if ((sr1 & I2C_SR1_ADDR) == 0U) {
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_TIMEOUT;
    }

    /* ADDR знімається парою читань: SR1, потім SR2. */
    (void)I2C1_SR2;
    I2C1_CR1 |= I2C_CR1_STOP;
    return BRINGUP_OK;
}

/* ---- сканування адресного простору ---- */

bringup_status_t bringup_scan_i2c_bus(bringup_report_t *report)
{
    uint32_t addr;

    report->i2c_devices_found = 0U;

    for (addr = 0x08U; addr <= 0x77U; ++addr) {
        bringup_status_t status = bringup_i2c_probe_address((uint8_t)addr);

        if (status == BRINGUP_OK) {
            if (report->i2c_devices_found < BRINGUP_I2C_MAX_FOUND) {
                report->i2c_addresses[report->i2c_devices_found] = (uint8_t)addr;
            }
            ++report->i2c_devices_found;
        } else if (status == BRINGUP_ERR_I2C_TIMEOUT) {
            /* Модуль застряг — далі перебирати адреси немає сенсу. */
            report->i2c_status = BRINGUP_ERR_I2C_TIMEOUT;
            return BRINGUP_ERR_I2C_TIMEOUT;
        }

        bringup_delay_us(100U);  /* пауза між пробами: шина має відпочити */
    }

    report->i2c_status = (report->i2c_devices_found > 0U)
                       ? BRINGUP_OK
                       : BRINGUP_ERR_I2C_NACK;
    return report->i2c_status;
}

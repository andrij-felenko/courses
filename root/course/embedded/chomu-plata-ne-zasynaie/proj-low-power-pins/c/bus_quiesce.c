#include "bus_quiesce.h"

/* Виводи I2C1 на цій платі: PB8 = SCL, PB9 = SDA, альтернативна функція 4. */
#define I2C_SCL_PIN 8U
#define I2C_SDA_PIN 9U
#define I2C_AF      4U

/* Крок ручного такту: 100 кГц дає 10 мкс на період, отже 5 мкс на півперіод. */
#define BITBANG_HALF_US 5U

const char *bus_status_str(bus_status_t st)
{
    switch (st) {
    case BUS_OK:            return "ok";
    case BUS_ERR_UART_TC:   return "uart: TC не виставився";
    case BUS_ERR_SPI_BUSY:  return "spi: BSY не знявся";
    case BUS_ERR_I2C_BUSY:  return "i2c: BUSY не знявся";
    case BUS_ERR_I2C_STUCK: return "i2c: SDA лишилася в нулі";
    default:                return "?";
    }
}

/* Опитування прапорця з грубим таймаутом. Повертає true, якщо дочекалися. */
static bool wait_flag(volatile uint32_t *reg, uint32_t mask, bool want_set,
                      uint32_t timeout_us)
{
    for (;;) {
        bool is_set = ((*reg & mask) != 0U);
        if (is_set == want_set) {
            return true;
        }
        if (timeout_us == 0U) {
            return false;
        }
        mcu_delay_us(1U);
        timeout_us--;
    }
}

bus_status_t bus_quiesce_uart(usart_t *u, uint32_t timeout_us)
{
    if ((u->CR1 & USART_CR1_UE) == 0U) {
        return BUS_OK; /* модуль і так вимкнено */
    }

    /* TXE каже лише те, що байт переїхав з буфера у зсувний регістр. Якщо
     * зупинити тактування тут, приймач дістане обірваний кадр і Framing Error.
     * Чекаємо TC — момент, коли стоповий біт уже на лінії. */
    if ((u->CR1 & USART_CR1_TE) != 0U) {
        if (!wait_flag(&u->ISR, USART_ISR_TC, true, timeout_us)) {
            return BUS_ERR_UART_TC;
        }
    }

    u->CR1 &= ~USART_CR1_UE;
    return BUS_OK;
}

bus_status_t bus_quiesce_spi(spi_t *s, uint32_t timeout_us)
{
    if ((s->CR1 & SPI_CR1_SPE) == 0U) {
        return BUS_OK;
    }

    /* Спершу має спорожніти черга передачі FIFO, і лише потім знімається BSY. */
    if (!wait_flag(&s->SR, SPI_SR_FTLVL, false, timeout_us)) {
        return BUS_ERR_SPI_BUSY;
    }
    if (!wait_flag(&s->SR, SPI_SR_BSY, false, timeout_us)) {
        return BUS_ERR_SPI_BUSY;
    }

    s->CR1 &= ~SPI_CR1_SPE;
    return BUS_OK;
}

bus_status_t bus_quiesce_i2c(i2c_t *i, uint32_t timeout_us)
{
    if ((i->CR1 & I2C_CR1_PE) == 0U) {
        return BUS_OK;
    }

    if (!wait_flag(&i->ISR, I2C_ISR_BUSY, false, timeout_us)) {
        /* Шина зависла: ведений тримає лінію. Знімаємо PE й пробуємо розклинити,
         * інакше після пробудження модуль не зможе видати START. */
        i->CR1 &= ~I2C_CR1_PE;
        bus_status_t rec = bus_recover_i2c();
        return (rec == BUS_OK) ? BUS_ERR_I2C_BUSY : rec;
    }

    /* Зняття PE відпускає обидві лінії у високий імпеданс — це те, що треба
     * перед знеструмленням веденого: підтяжок на боці мікроконтролера немає. */
    i->CR1 &= ~I2C_CR1_PE;
    return BUS_OK;
}

bus_status_t bus_quiesce_all(uint32_t timeout_us)
{
    bus_status_t st = bus_quiesce_uart(USART2, timeout_us);
    if (st != BUS_OK) {
        return st;
    }
    st = bus_quiesce_spi(SPI1, timeout_us);
    if (st != BUS_OK) {
        return st;
    }
    return bus_quiesce_i2c(I2C1, timeout_us);
}

/* --------------------------- розклинення I2C --------------------------- */

static void scl_pulse(void)
{
    gpio_write(GPIOB, I2C_SCL_PIN, true);
    mcu_delay_us(BITBANG_HALF_US);
    gpio_write(GPIOB, I2C_SCL_PIN, false);
    mcu_delay_us(BITBANG_HALF_US);
}

bus_status_t bus_recover_i2c(void)
{
    /* Обидві лінії стають виходами з відкритим стоком: одиниця на такому
     * виході — це відпущена лінія, а не 3.3 В у ведений. */
    gpio_open_drain(GPIOB, I2C_SCL_PIN, true);
    gpio_open_drain(GPIOB, I2C_SDA_PIN, true);
    gpio_write(GPIOB, I2C_SCL_PIN, true);
    gpio_write(GPIOB, I2C_SDA_PIN, true);
    gpio_mode(GPIOB, I2C_SCL_PIN, MODE_OUTPUT);
    gpio_mode(GPIOB, I2C_SDA_PIN, MODE_OUTPUT);
    mcu_delay_us(BITBANG_HALF_US);

    /* Дев'ять тактів: ведений добиває недоказаний байт і відпускає SDA. */
    for (unsigned n = 0U; n < 9U; n++) {
        if (gpio_read(GPIOB, I2C_SDA_PIN)) {
            break; /* лінія вже вільна, доганяти нічого */
        }
        scl_pulse();
    }

    bool freed = gpio_read(GPIOB, I2C_SDA_PIN);

    /* Умова STOP: SDA вниз, SCL вгору, SDA вгору. Без неї ведений лишиться
     * вважати, що транзакція триває. */
    gpio_write(GPIOB, I2C_SDA_PIN, false);
    mcu_delay_us(BITBANG_HALF_US);
    gpio_write(GPIOB, I2C_SCL_PIN, true);
    mcu_delay_us(BITBANG_HALF_US);
    gpio_write(GPIOB, I2C_SDA_PIN, true);
    mcu_delay_us(BITBANG_HALF_US);

    /* Повертаємо виводи апаратному модулю. */
    gpio_af(GPIOB, I2C_SCL_PIN, I2C_AF);
    gpio_af(GPIOB, I2C_SDA_PIN, I2C_AF);

    return freed ? BUS_OK : BUS_ERR_I2C_STUCK;
}

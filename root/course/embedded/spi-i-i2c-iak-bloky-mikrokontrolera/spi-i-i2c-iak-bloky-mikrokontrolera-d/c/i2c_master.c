#include "i2c_master.h"

#define I2C_BUDGET 200000U

/* I2C1 на STM32F4: PB6 = SCL, PB7 = SDA, обидва AF4, обов'язково
   з відкритим стоком. Внутрішня підтяжка ввімкнена як страховка —
   робочі рівні тримають зовнішні резистори 4.7 кОм. */
static void pins_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;

    for (unsigned pin = 6U; pin <= 7U; ++pin) {
        GPIOB->MODER   &= ~(3U << (pin * 2U));
        GPIOB->MODER   |=  (2U << (pin * 2U));
        GPIOB->OTYPER  |=  (1U << pin);            /* open-drain */
        GPIOB->OSPEEDR |=  (3U << (pin * 2U));
        GPIOB->PUPDR   &= ~(3U << (pin * 2U));
        GPIOB->PUPDR   |=  (1U << (pin * 2U));     /* слабка підтяжка вгору */
        GPIOB->AFR[0]  &= ~(0xFU << (pin * 4U));
        GPIOB->AFR[0]  |=  (4U << (pin * 4U));     /* AF4 = I2C1 */
    }
}

void i2c1_master_init(uint32_t pclk1_hz, uint32_t scl_hz)
{
    pins_init();
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* Програмний скид блока: знімає внутрішні засувки автомата,
       зокрема залиплий BUSY після невдалої транзакції. */
    I2C1->CR1 = I2C_CR1_SWRST;
    I2C1->CR1 = 0U;

    uint32_t freq_mhz = pclk1_hz / 1000000U;
    I2C1->CR2 = freq_mhz & I2C_CR2_FREQ_MSK;   /* блоку треба знати свій такт */

    uint32_t ccr;
    if (scl_hz <= 100000U) {
        /* Стандартний режим: половина періоду = CCR тактів PCLK1 */
        ccr = pclk1_hz / (2U * scl_hz);
        if (ccr < 4U) {
            ccr = 4U;
        }
        I2C1->CCR = ccr;
        I2C1->TRISE = freq_mhz + 1U;              /* 1000 нс наростання */
    } else {
        /* Швидкий режим, шпаруватість 1:2 */
        ccr = pclk1_hz / (3U * scl_hz);
        if (ccr < 1U) {
            ccr = 1U;
        }
        I2C1->CCR = I2C_CCR_FS | ccr;
        I2C1->TRISE = (freq_mhz * 300U) / 1000U + 1U;   /* 300 нс наростання */
    }

    I2C1->CR1 = I2C_CR1_PE | I2C_CR1_ACK;
}

/* Опитування прапорця події з паралельним наглядом за аварійними.
   Кожна помилка обробляється тут же: інакше шина лишиться зайнятою. */
static i2c_status_t wait_flag(uint32_t sr1_mask)
{
    uint32_t left = I2C_BUDGET;

    for (;;) {
        uint32_t sr1 = I2C1->SR1;

        if (sr1 & I2C_SR1_AF) {
            /* Ведений не підтвердив: знімаємо прапорець і звільняємо шину */
            I2C1->SR1 &= ~I2C_SR1_AF;
            I2C1->CR1 |= I2C_CR1_STOP;
            return I2C_ERR_NACK;
        }
        if (sr1 & I2C_SR1_ARLO) {
            /* Шина вже не наша — блок сам став веденим, STOP не генеруємо */
            I2C1->SR1 &= ~I2C_SR1_ARLO;
            return I2C_ERR_ARLO;
        }
        if (sr1 & I2C_SR1_BERR) {
            I2C1->SR1 &= ~I2C_SR1_BERR;
            I2C1->CR1 |= I2C_CR1_STOP;
            return I2C_ERR_BERR;
        }
        if (sr1 & sr1_mask) {
            return I2C_OK;
        }
        if (--left == 0U) {
            /* Найімовірніше ведений залип на розтягуванні такту */
            I2C1->CR1 |= I2C_CR1_STOP;
            return I2C_ERR_TIMEOUT;
        }
    }
}

/* Зняття ADDR читанням SR1, потім SR2 — саме воно відпускає притиснуту SCL */
static void clear_addr(void)
{
    (void)I2C1->SR1;
    (void)I2C1->SR2;
}

static i2c_status_t wait_stop_done(void)
{
    uint32_t left = I2C_BUDGET;
    while (I2C1->CR1 & I2C_CR1_STOP) {
        if (--left == 0U) {
            return I2C_ERR_TIMEOUT;
        }
    }
    return I2C_OK;
}

static i2c_status_t send_start(void)
{
    uint32_t left = I2C_BUDGET;
    while (I2C1->SR2 & I2C_SR2_BUSY) {
        if (--left == 0U) {
            return I2C_ERR_BUSY;
        }
    }
    I2C1->CR1 |= I2C_CR1_START;
    return wait_flag(I2C_SR1_SB);            /* подія EV5 */
}

static i2c_status_t send_repeated_start(void)
{
    /* Повторний START видається посеред своєї ж транзакції,
       тому BUSY тут перевіряти не можна — він і має бути піднятим. */
    I2C1->CR1 |= I2C_CR1_START;
    return wait_flag(I2C_SR1_SB);
}

static i2c_status_t send_address(uint8_t addr7, bool read)
{
    /* Запис у DR закриває EV5; біт напрямку — молодший */
    I2C1->DR = (uint32_t)(addr7 << 1) | (read ? 1U : 0U);
    return wait_flag(I2C_SR1_ADDR);          /* подія EV6 */
}

/* Тіло читання: викликається, коли ADDR уже піднявся, але ще не знятий.
   Кількість байтів змінює всю послідовність — так вимагає RM0090. */
static i2c_status_t read_body(uint8_t *data, size_t len)
{
    i2c_status_t st;

    if (len == 1U) {
        /* NACK треба виставити ДО зняття ADDR, інакше ведений устигне
           почати другий байт. */
        I2C1->CR1 &= ~I2C_CR1_ACK;
        clear_addr();
        I2C1->CR1 |= I2C_CR1_STOP;
        st = wait_flag(I2C_SR1_RXNE);        /* подія EV7 */
        if (st != I2C_OK) {
            return st;
        }
        data[0] = (uint8_t)I2C1->DR;
    } else if (len == 2U) {
        /* POS переносить NACK на ДРУГИЙ прийнятий байт */
        I2C1->CR1 &= ~I2C_CR1_ACK;
        I2C1->CR1 |= I2C_CR1_POS;
        clear_addr();
        st = wait_flag(I2C_SR1_BTF);
        if (st != I2C_OK) {
            I2C1->CR1 &= ~I2C_CR1_POS;
            return st;
        }
        I2C1->CR1 |= I2C_CR1_STOP;
        data[0] = (uint8_t)I2C1->DR;
        data[1] = (uint8_t)I2C1->DR;
        I2C1->CR1 &= ~I2C_CR1_POS;
    } else {
        I2C1->CR1 |= I2C_CR1_ACK;
        clear_addr();

        size_t i = 0;
        while ((len - i) > 3U) {
            st = wait_flag(I2C_SR1_RXNE);
            if (st != I2C_OK) {
                return st;
            }
            data[i++] = (uint8_t)I2C1->DR;
        }

        /* Лишилося рівно три байти: N-2 у буфері, N-1 у зсувному регістрі.
           Ця п'ятірка дій має пройти без затримок — інакше автомат устигне
           видати ACK на останній байт. У бойовому драйвері тут маскують
           переривання. */
        st = wait_flag(I2C_SR1_BTF);
        if (st != I2C_OK) {
            return st;
        }
        I2C1->CR1 &= ~I2C_CR1_ACK;
        data[i++] = (uint8_t)I2C1->DR;
        I2C1->CR1 |= I2C_CR1_STOP;
        data[i++] = (uint8_t)I2C1->DR;

        st = wait_flag(I2C_SR1_RXNE);
        if (st != I2C_OK) {
            return st;
        }
        data[i] = (uint8_t)I2C1->DR;
    }

    st = wait_stop_done();
    I2C1->CR1 |= I2C_CR1_ACK;   /* повертаємо стан за замовчуванням */
    return st;
}

static i2c_status_t write_body(const uint8_t *data, size_t len)
{
    for (size_t i = 0; i < len; ++i) {
        i2c_status_t st = wait_flag(I2C_SR1_TXE);   /* подія EV8 */
        if (st != I2C_OK) {
            return st;
        }
        I2C1->DR = data[i];
    }
    /* BTF (EV8_2): і буфер, і зсувний регістр порожні — тепер STOP або
       повторний START не обріже останній байт. */
    return wait_flag(I2C_SR1_BTF);
}

i2c_status_t i2c1_write(uint8_t addr7, const uint8_t *data, size_t len)
{
    if (data == NULL || len == 0U) {
        return I2C_ERR_ARG;
    }

    i2c_status_t st = send_start();
    if (st != I2C_OK) {
        return st;
    }
    st = send_address(addr7, false);
    if (st != I2C_OK) {
        return st;
    }
    clear_addr();

    st = write_body(data, len);
    if (st != I2C_OK) {
        return st;
    }

    I2C1->CR1 |= I2C_CR1_STOP;
    return wait_stop_done();
}

i2c_status_t i2c1_read(uint8_t addr7, uint8_t *data, size_t len)
{
    if (data == NULL || len == 0U) {
        return I2C_ERR_ARG;
    }

    i2c_status_t st = send_start();
    if (st != I2C_OK) {
        return st;
    }
    st = send_address(addr7, true);
    if (st != I2C_OK) {
        return st;
    }
    return read_body(data, len);
}

i2c_status_t i2c1_write_read(uint8_t addr7, const uint8_t *cmd, size_t cmd_len,
                             uint8_t *data, size_t len)
{
    if (cmd == NULL || cmd_len == 0U || data == NULL || len == 0U) {
        return I2C_ERR_ARG;
    }

    i2c_status_t st = send_start();
    if (st != I2C_OK) {
        return st;
    }
    st = send_address(addr7, false);
    if (st != I2C_OK) {
        return st;
    }
    clear_addr();

    st = write_body(cmd, cmd_len);
    if (st != I2C_OK) {
        return st;
    }

    st = send_repeated_start();
    if (st != I2C_OK) {
        return st;
    }
    st = send_address(addr7, true);
    if (st != I2C_OK) {
        return st;
    }
    return read_body(data, len);
}

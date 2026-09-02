/* Три задачі. Кожна пишеться лінійно й має право чекати: те, що в супер-циклі
   довелося б різати на стани, тут лишається послідовним кодом. */
#include "app.h"

#include "stm32g0xx.h"

#define BME280_ADDR   0x76u
#define REG_CALIB_T   0x88u
#define REG_ID        0xD0u
#define REG_CTRL_MEAS 0xF4u
#define REG_TEMP_MSB  0xFAu
#define CHIP_ID       0x60u
#define BUS_GUARD     100000u

#define SENSOR_PERIOD_MS 100u
#define MEAS_TIME_MS     5u

static uint16_t s_dig_t1;
static int16_t  s_dig_t2;
static int16_t  s_dig_t3;

/* ---- шина I2C: короткі блокуючі транзакції ---- */

static bool i2c_wait(uint32_t flag)
{
    uint32_t guard = BUS_GUARD;
    while ((I2C1->ISR & flag) == 0u) {
        if ((I2C1->ISR & I2C_ISR_NACKF) != 0u) {
            I2C1->ICR = I2C_ICR_NACKCF | I2C_ICR_STOPCF;
            return false;
        }
        if (guard-- == 0u) {
            return false;
        }
    }
    return true;
}

static void i2c_finish(void)
{
    uint32_t guard = BUS_GUARD;
    while (((I2C1->ISR & I2C_ISR_STOPF) == 0u) && (guard-- != 0u)) { }
    I2C1->ICR = I2C_ICR_STOPCF | I2C_ICR_NACKCF;
}

static void i2c_reset(void)
{
    I2C1->CR1 &= ~I2C_CR1_PE;
    vTaskDelay(1); /* можемо дозволити собі віддати процесор на такт ядра */
    I2C1->CR1 |= I2C_CR1_PE;
}

static bool i2c_write_reg(uint8_t reg, uint8_t value)
{
    I2C1->CR2 = ((uint32_t)BME280_ADDR << 1) | (2u << I2C_CR2_NBYTES_Pos)
              | I2C_CR2_AUTOEND | I2C_CR2_START;
    if (!i2c_wait(I2C_ISR_TXIS)) { i2c_reset(); return false; }
    I2C1->TXDR = reg;
    if (!i2c_wait(I2C_ISR_TXIS)) { i2c_reset(); return false; }
    I2C1->TXDR = value;
    i2c_finish();
    return true;
}

static bool i2c_read_regs(uint8_t reg, uint8_t *buf, uint8_t len)
{
    I2C1->CR2 = ((uint32_t)BME280_ADDR << 1) | (1u << I2C_CR2_NBYTES_Pos) | I2C_CR2_START;
    if (!i2c_wait(I2C_ISR_TXIS)) { i2c_reset(); return false; }
    I2C1->TXDR = reg;
    if (!i2c_wait(I2C_ISR_TC)) { i2c_reset(); return false; }

    I2C1->CR2 = ((uint32_t)BME280_ADDR << 1) | ((uint32_t)len << I2C_CR2_NBYTES_Pos)
              | I2C_CR2_RD_WRN | I2C_CR2_AUTOEND | I2C_CR2_START;
    for (uint8_t i = 0; i < len; i++) {
        if (!i2c_wait(I2C_ISR_RXNE)) { i2c_reset(); return false; }
        buf[i] = (uint8_t)I2C1->RXDR;
    }
    i2c_finish();
    return true;
}

static bool sensor_begin(void)
{
    uint8_t id = 0u;
    uint8_t cal[6];

    if (!i2c_read_regs(REG_ID, &id, 1u) || (id != CHIP_ID)) {
        return false;
    }
    if (!i2c_read_regs(REG_CALIB_T, cal, sizeof cal)) {
        return false;
    }
    s_dig_t1 = (uint16_t)((uint16_t)cal[1] << 8 | cal[0]);
    s_dig_t2 = (int16_t)((uint16_t)cal[3] << 8 | cal[2]);
    s_dig_t3 = (int16_t)((uint16_t)cal[5] << 8 | cal[4]);
    return true;
}

static bool sensor_measure(int32_t *out_c100)
{
    uint8_t raw[3];
    int32_t adc;
    int32_t var1;
    int32_t var2;
    int32_t d;

    if (!i2c_write_reg(REG_CTRL_MEAS, 0x21u)) { /* forced, oversampling x1 */
        return false;
    }
    /* Ось головна різниця з голим циклом: п'ять мілісекунд перетворення
       ми не крутимо в порожньому очікуванні, а віддаємо процесор іншим. */
    vTaskDelay(pdMS_TO_TICKS(MEAS_TIME_MS));

    if (!i2c_read_regs(REG_TEMP_MSB, raw, sizeof raw)) {
        return false;
    }
    adc = ((int32_t)raw[0] << 12) | ((int32_t)raw[1] << 4) | ((int32_t)raw[2] >> 4);
    if (adc == 0x80000) {
        return false;
    }
    var1 = ((((adc >> 3) - ((int32_t)s_dig_t1 << 1))) * (int32_t)s_dig_t2) >> 11;
    d    = (adc >> 4) - (int32_t)s_dig_t1;
    var2 = (((d * d) >> 12) * (int32_t)s_dig_t3) >> 14;
    *out_c100 = ((var1 + var2) * 5 + 128) >> 8;
    return true;
}

void task_sensor(void *arg)
{
    TickType_t wake = xTaskGetTickCount();
    sample_t sample = {0};
    bool ready;

    (void)arg;
    ready = sensor_begin();

    for (;;) {
        int32_t value;

        if (!ready) {
            ready = sensor_begin(); /* датчик міг просто пізніше подати живлення */
        } else if (sensor_measure(&value)) {
            sample.stamp_ms  = (uint32_t)(xTaskGetTickCount() * portTICK_PERIOD_MS);
            sample.temp_c100 = value;
            sample.seq++;
            /* Черга коротка навмисно: якщо екран не встигає, свіжий вимір
               важливіший за старий — тому чекаємо на місце лише один такт. */
            if (xQueueSend(g_samples, &sample, pdMS_TO_TICKS(1)) != pdTRUE) {
                sample_t dropped;
                (void)xQueueReceive(g_samples, &dropped, 0);
                (void)xQueueSend(g_samples, &sample, 0);
            }
        } else {
            sample.errors++;
            ready = false;
        }

        xTaskNotify(g_supervisor_task, ALIVE_SENSOR, eSetBits);
        /* Період тримається від попереднього пробудження, а не від кінця
           роботи: саме це прибирає накопичення дрейфу, яким слабкий цикл. */
        xTaskDelayUntil(&wake, pdMS_TO_TICKS(SENSOR_PERIOD_MS));
    }
}

/* ---- екран: той самий повільний SPI, але тепер він нікого не тримає ---- */

static uint8_t s_fb[128u * 8u];

static bool spi_write(const uint8_t *buf, uint32_t len)
{
    for (uint32_t i = 0; i < len; i++) {
        uint32_t guard = BUS_GUARD;
        while ((SPI1->SR & SPI_SR_TXE) == 0u) {
            if (guard-- == 0u) {
                return false;
            }
        }
        *(volatile uint8_t *)&SPI1->DR = buf[i];
    }
    while ((SPI1->SR & SPI_SR_BSY) != 0u) { }
    while ((SPI1->SR & SPI_SR_RXNE) != 0u) {
        (void)*(volatile uint8_t *)&SPI1->DR;
    }
    return true;
}

static bool display_cmd(uint8_t c)
{
    GPIOA->BSRR = GPIO_BSRR_BR1; /* D/C = команда */
    GPIOA->BSRR = GPIO_BSRR_BR4; /* CS активний   */
    bool ok = spi_write(&c, 1u);
    GPIOA->BSRR = GPIO_BSRR_BS4;
    return ok;
}

static bool display_begin(void)
{
    static const uint8_t init_seq[] = {
        0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0x8D, 0x14,
        0x20, 0x00, 0xA1, 0xC8, 0xDA, 0x12, 0x81, 0x7F, 0xD9, 0xF1,
        0xDB, 0x40, 0xA4, 0xA6, 0xAF,
    };

    GPIOA->BSRR = GPIO_BSRR_BR2;
    vTaskDelay(pdMS_TO_TICKS(2));
    GPIOA->BSRR = GPIO_BSRR_BS2;
    vTaskDelay(pdMS_TO_TICKS(2));

    for (unsigned i = 0; i < sizeof init_seq; i++) {
        if (!display_cmd(init_seq[i])) {
            return false;
        }
    }
    return true;
}

static void draw_bar(uint8_t page, int32_t value, int32_t lo, int32_t hi)
{
    int32_t span = hi - lo;
    int32_t w;

    if (span <= 0) { return; }
    if (value < lo) { value = lo; }
    if (value > hi) { value = hi; }

    w = ((value - lo) * 128) / span;
    for (int32_t x = 0; x < 128; x++) {
        s_fb[(uint32_t)page * 128u + (uint32_t)x] = (x < w) ? 0x3Cu : 0x00u;
    }
}

static bool display_flush(void)
{
    static const uint8_t window[] = { 0x21, 0x00, 0x7F, 0x22, 0x00, 0x07 };

    for (unsigned i = 0; i < sizeof window; i++) {
        if (!display_cmd(window[i])) {
            return false;
        }
    }
    GPIOA->BSRR = GPIO_BSRR_BS1; /* D/C = дані */
    GPIOA->BSRR = GPIO_BSRR_BR4;
    bool ok = spi_write(s_fb, sizeof s_fb);
    GPIOA->BSRR = GPIO_BSRR_BS4;
    return ok;
}

void task_display(void *arg)
{
    sample_t sample;
    bool ready;

    (void)arg;
    ready = display_begin();

    for (;;) {
        /* Блокуюче очікування: поки даних немає, задача не з'їдає жодного такту. */
        if (xQueueReceive(g_samples, &sample, pdMS_TO_TICKS(500)) == pdTRUE) {
            if (!ready) {
                ready = display_begin();
            }
            if (ready) {
                draw_bar(3u, sample.temp_c100, -1000, 5000);
                /* Кадр висить на шині ≈33 мс — і весь цей час задача датчика
                   спокійно витісняє екран, бо має вищий пріоритет. */
                ready = display_flush();
            }
        }
        xTaskNotify(g_supervisor_task, ALIVE_DISPLAY, eSetBits);
    }
}

void task_supervisor(void *arg)
{
    const UBaseType_t low_water_words = 32u; /* менше — стек уже на межі */
    uint32_t alive = 0u;

    (void)arg;

    for (;;) {
        uint32_t bits = 0u;

        if (xTaskNotifyWait(0u, 0xFFFFFFFFu, &bits, pdMS_TO_TICKS(250)) == pdTRUE) {
            alive |= bits;
        }

        /* Watchdog гладимо лише тоді, коли ОБИДВІ робочі задачі відзвітували.
           Зависла одна — прилад перезавантажиться, і це правильна поведінка. */
        if ((alive & ALIVE_ALL) == ALIVE_ALL) {
            alive = 0u;
            watchdog_kick();
        }

        /* Запас стеків міряємо в тій самій точці: у полі це єдиний спосіб
           дізнатися, що обраний розмір був оптимістичним. */
        if ((uxTaskGetStackHighWaterMark(g_sensor_task) < low_water_words) ||
            (uxTaskGetStackHighWaterMark(g_display_task) < low_water_words)) {
            configASSERT(0); /* у налагоджувальній збірці — зупинка тут */
        }
    }
}

#include <stdint.h>
#include <stdbool.h>

/* Коди помилок шини I2C */
typedef enum {
    I2C_OK = 0,
    I2C_ERR_TIMEOUT = -1,     /* Ведений утримує SCL довше за допустимий таймаут */
    I2C_ERR_NACK_ADDR = -2,    /* Ведений не підтвердив свою адресу */
    I2C_ERR_NACK_DATA = -3,    /* Ведений відхилив байт даних */
    I2C_ERR_BUS_BUSY = -4     /* Лінії шини замкнені або зайняті */
} i2c_status_t;

/* Платформозалежні прототипи функцій низького рівня (HAL) */
extern void hal_gpio_init(void);
extern void hal_scl_drive_low(void);   /* Режим Output, 0V */
extern void hal_scl_release(void);     /* Режим Input (High-Z) */
extern bool hal_scl_read(void);        /* Зчитування логічного рівня піна SCL */
extern void hal_sda_drive_low(void);   /* Режим Output, 0V */
extern void hal_sda_release(void);     /* Режим Input (High-Z) */
extern bool hal_sda_read(void);        /* Зчитування логічного рівня піна SDA */
extern void hal_delay_us(uint32_t us); /* Затримка в мікросекундах */

/* Конфігураційні параметри для швидкості 100 кГц (Standard Mode) */
#define I2C_HALF_CLOCK_US     5
#define I2C_STRETCH_TIMEOUT_US 35000  /* 35 мс за стандартом SMBus */

/* 
 * Відпускання лінії SCL із контролем розтягування (Clock Stretching) 
 * Повертає I2C_OK після підтвердження високого рівня або I2C_ERR_TIMEOUT
 */
static i2c_status_t i2c_scl_release_and_wait(void) {
    hal_scl_release(); /* Відпускаємо лінію в High-Z, резистор Rp тягне її до VDD */

    uint32_t elapsed_us = 0;
    while (!hal_scl_read()) {
        hal_delay_us(1);
        elapsed_us++;
        if (elapsed_us >= I2C_STRETCH_TIMEOUT_US) {
            return I2C_ERR_TIMEOUT; /* Захист від нескінченного зависання шини */
        }
    }
    return I2C_OK;
}

/* Формування сигналу СТАРТ (START condition) */
static i2c_status_t i2c_start(void) {
    hal_sda_release();
    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_BUS_BUSY;
    
    hal_delay_us(I2C_HALF_CLOCK_US);
    hal_sda_drive_low(); /* Спад SDA при високому SCL */
    hal_delay_us(I2C_HALF_CLOCK_US);
    hal_scl_drive_low();
    return I2C_OK;
}

/* Формування сигналу СТОП (STOP condition) */
static i2c_status_t i2c_stop(void) {
    hal_sda_drive_low();
    hal_delay_us(I2C_HALF_CLOCK_US);
    
    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
    hal_delay_us(I2C_HALF_CLOCK_US);
    
    hal_sda_release(); /* Наростання SDA при високому SCL */
    hal_delay_us(I2C_HALF_CLOCK_US);
    return I2C_OK;
}

/* Передача одного байта з контролем підтвердження ACK/NACK */
static i2c_status_t i2c_write_byte(uint8_t byte, bool *ack_received) {
    for (int8_t bit = 7; bit >= 0; bit--) {
        if ((byte >> bit) & 1) {
            hal_sda_release();
        } else {
            hal_sda_drive_low();
        }
        hal_delay_us(I2C_HALF_CLOCK_US);

        /* Підйом SCL з очікуванням веденого */
        if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
        hal_delay_us(I2C_HALF_CLOCK_US);
        hal_scl_drive_low();
    }

    /* 9-й такт: зчитування біта підтвердження (ACK від веденого) */
    hal_sda_release();
    hal_delay_us(I2C_HALF_CLOCK_US);

    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
    hal_delay_us(I2C_HALF_CLOCK_US / 2);

    /* Якщо ведений притягнув SDA до 0, це ACK (успіх) */
    *ack_received = !hal_sda_read();

    hal_delay_us(I2C_HALF_CLOCK_US / 2);
    hal_scl_drive_low();
    return I2C_OK;
}

/* Зчитування одного байта з генерацією ACK або NACK */
static i2c_status_t i2c_read_byte(uint8_t *byte, bool send_ack) {
    uint8_t result = 0;
    hal_sda_release();

    for (int8_t bit = 7; bit >= 0; bit--) {
        hal_delay_us(I2C_HALF_CLOCK_US);

        /* Ведений може розтягувати такт перед виставленням будь-якого біта даних */
        if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
        hal_delay_us(I2C_HALF_CLOCK_US / 2);

        if (hal_sda_read()) {
            result |= (1 << bit);
        }
        hal_delay_us(I2C_HALF_CLOCK_US / 2);
        hal_scl_drive_low();
    }

    /* 9-й такт: надсилання підтвердження від ведучого */
    if (send_ack) {
        hal_sda_drive_low(); /* ACK: ведучий готовий приймати далі */
    } else {
        hal_sda_release();   /* NACK: завершення читання */
    }
    hal_delay_us(I2C_HALF_CLOCK_US);

    if (i2c_scl_release_and_wait() != I2C_OK) return I2C_ERR_TIMEOUT;
    hal_delay_us(I2C_HALF_CLOCK_US);
    hal_scl_drive_low();
    hal_sda_release();

    *byte = result;
    return I2C_OK;
}

/*
 * Процедура аварійного очищення шини (Bus Recovery / Clear):
 * генерує до 9 тактів SCL для виштовхування завислого біта веденого
 */
void i2c_recover_bus(void) {
    hal_sda_release();
    hal_scl_release();
    hal_delay_us(I2C_HALF_CLOCK_US);

    /* Якщо SDA утримується на 0, генеруємо такти доти, доки SDA не звільниться */
    for (uint8_t i = 0; i < 9; i++) {
        if (hal_sda_read()) break;

        hal_scl_drive_low();
        hal_delay_us(I2C_HALF_CLOCK_US);
        hal_scl_release();
        hal_delay_us(I2C_HALF_CLOCK_US);
    }

    /* Завершуємо процедуру примусовим формуванням сигналу STOP */
    i2c_stop();
}

/* Програмний ведучий I2C (Bit-Banging) з точним дотриманням UM10204 (C11) */
#include <stdint.h>
#include <stdbool.h>

/* Низькорівнева апаратна платформа: доступ до GPIO та лічильника тактів */
extern void hw_gpio_sda_low(void);
extern void hw_gpio_sda_hiz(void);
extern uint8_t hw_gpio_sda_read(void);

extern void hw_gpio_scl_low(void);
extern void hw_gpio_scl_hiz(void);
extern uint8_t hw_gpio_scl_read(void);

extern void hw_delay_ns(uint32_t ns);
extern uint32_t hw_get_dwt_cycles(void);

typedef enum {
    I2C_OK           = 0,
    I2C_ERR_TIMEOUT  = -1,
    I2C_ERR_NACK     = -2,
    I2C_ERR_BUS_BUSY = -3
} i2c_status_t;

typedef struct {
    uint32_t t_low_ns;
    uint32_t t_high_ns;
    uint32_t t_su_dat_ns;
    uint32_t t_hd_dat_ns;
    uint32_t t_hd_sta_ns;
    uint32_t t_su_sta_ns;
    uint32_t t_su_sto_ns;
    uint32_t t_buf_ns;
    uint32_t timeout_cycles;
} i2c_bb_timing_t;

/* Нормативні параметри для Fast-mode (400 кГц) */
static const i2c_bb_timing_t TIMING_FAST_400K = {
    .t_low_ns        = 1300,
    .t_high_ns       = 600,
    .t_su_dat_ns     = 100,
    .t_hd_dat_ns     = 300,
    .t_hd_sta_ns     = 600,
    .t_su_sta_ns     = 600,
    .t_su_sto_ns     = 600,
    .t_buf_ns        = 1300,
    .timeout_cycles  = 16800000 /* ~100 мс при тактовій частоті ядра 168 МГц */
};

/* Очікування наростання SCL з апаратним захистом від зависання (Clock Stretching) */
static i2c_status_t wait_scl_high(const i2c_bb_timing_t *t) {
    hw_gpio_scl_hiz();
    const uint32_t start_cycles = hw_get_dwt_cycles();

    while (hw_gpio_scl_read() == 0) {
        if ((hw_get_dwt_cycles() - start_cycles) > t->timeout_cycles) {
            return I2C_ERR_TIMEOUT;
        }
    }
    return I2C_OK;
}

/* Формування умови START: спадний фронт SDA при високому рівні SCL */
i2c_status_t i2c_bb_start(const i2c_bb_timing_t *t) {
    hw_gpio_sda_hiz();
    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_BUS_BUSY;
    }
    hw_delay_ns(t->t_su_sta_ns);

    /* Спадний перепад на лінії даних */
    hw_gpio_sda_low();
    hw_delay_ns(t->t_hd_sta_ns);

    /* Фіксація початку тактування */
    hw_gpio_scl_low();
    hw_delay_ns(t->t_low_ns);
    return I2C_OK;
}

/* Формування умови STOP: наростаючий фронт SDA при високому рівні SCL */
i2c_status_t i2c_bb_stop(const i2c_bb_timing_t *t) {
    hw_gpio_scl_low();
    hw_gpio_sda_low();
    hw_delay_ns(t->t_low_ns);

    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_TIMEOUT;
    }
    hw_delay_ns(t->t_su_sto_ns);

    /* Наростаючий перепад на лінії даних */
    hw_gpio_sda_hiz();
    hw_delay_ns(t->t_buf_ns);
    return I2C_OK;
}

/* Передача 8 бітів даних та зчитування біта підтвердження ACK/NACK */
i2c_status_t i2c_bb_write_byte(const i2c_bb_timing_t *t, uint8_t byte) {
    for (int8_t i = 7; i >= 0; i--) {
        if ((byte >> i) & 1) {
            hw_gpio_sda_hiz();
        } else {
            hw_gpio_sda_low();
        }
        hw_delay_ns(t->t_su_dat_ns);

        if (wait_scl_high(t) != I2C_OK) {
            return I2C_ERR_TIMEOUT;
        }
        hw_delay_ns(t->t_high_ns);

        hw_gpio_scl_low();
        hw_delay_ns(t->t_hd_dat_ns);
    }

    /* 9-й такт: перехід лінії SDA під контроль приймача */
    hw_gpio_sda_hiz();
    hw_delay_ns(t->t_su_dat_ns);

    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_TIMEOUT;
    }
    hw_delay_ns(t->t_high_ns);

    /* Зчитування квитанції: 0 = ACK, 1 = NACK */
    const uint8_t nack = hw_gpio_sda_read();

    hw_gpio_scl_low();
    hw_delay_ns(t->t_low_ns);

    return (nack == 0) ? I2C_OK : I2C_ERR_NACK;
}

/* Прийом 8 бітів даних із генерацією квитанції ACK або NACK ведучим */
i2c_status_t i2c_bb_read_byte(const i2c_bb_timing_t *t, uint8_t *out_byte, bool send_ack) {
    uint8_t byte = 0;
    hw_gpio_sda_hiz();

    for (int8_t i = 7; i >= 0; i--) {
        if (wait_scl_high(t) != I2C_OK) {
            return I2C_ERR_TIMEOUT;
        }
        hw_delay_ns(t->t_high_ns);

        if (hw_gpio_sda_read()) {
            byte |= (uint8_t)(1U << i);
        }

        hw_gpio_scl_low();
        hw_delay_ns(t->t_low_ns);
    }

    /* 9-й такт: видача підтвердження ведучим */
    if (send_ack) {
        hw_gpio_sda_low();  /* ACK = 0 */
    } else {
        hw_gpio_sda_hiz();  /* NACK = 1 */
    }
    hw_delay_ns(t->t_su_dat_ns);

    if (wait_scl_high(t) != I2C_OK) {
        return I2C_ERR_TIMEOUT;
    }
    hw_delay_ns(t->t_high_ns);

    hw_gpio_scl_low();
    hw_gpio_sda_hiz();
    hw_delay_ns(t->t_low_ns);

    *out_byte = byte;
    return I2C_OK;
}

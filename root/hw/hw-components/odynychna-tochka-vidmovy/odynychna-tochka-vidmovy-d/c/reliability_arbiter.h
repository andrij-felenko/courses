/* ============================================================================
 * ФАЙЛ: reliability_arbiter.h / reliability_arbiter.c (C99/C11)
 * Модуль відновлення шини I2C та мажоритарного арбітражу 2oo3 (TMR)
 * ============================================================================ */

#ifndef RELIABILITY_ARBITER_H
#define RELIABILITY_ARBITER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди результатів операції відновлення шини */
typedef enum {
    I2C_RECOVER_OK = 0,
    I2C_RECOVER_SDA_STUCK_LOW,
    I2C_RECOVER_SCL_STUCK_LOW,
    I2C_RECOVER_BUS_CLEARED
} i2c_recover_status_t;

/* Структура абстракції керування пінами GPIO */
typedef struct {
    void (*set_scl_output)(void);
    void (*set_sda_input)(void);
    void (*set_sda_output)(void);
    void (*write_scl)(bool level);
    void (*write_sda)(bool level);
    bool (*read_sda)(void);
    bool (*read_scl)(void);
    void (*delay_us)(uint32_t us);
} i2c_gpio_ops_t;

/* Статус справності каналу TMR */
typedef enum {
    CHANNEL_HEALTHY = 0,
    CHANNEL_DISCREPANCY,
    CHANNEL_FAULTY
} channel_health_t;

/* Результат голосування 2oo3 */
typedef struct {
    float voted_value;
    bool system_healthy;
    channel_health_t ch_status[3];
    uint8_t healthy_channels_count;
    int8_t failed_channel_index; /* -1 якщо всі справні */
} tmr_vote_result_t;

/* Контекст мажоритарного арбітра 2oo3 */
typedef struct {
    float max_tolerance;          /* Максимально допустиме відхилення */
    uint32_t fault_counters[3];   /* Лічильники помилок по кожному каналу */
    uint32_t fault_threshold;     /* Поріг відмов для виведення каналу з ладу */
    bool channel_disabled[3];     /* Прапорець блокування несправного каналу */
} tmr_arbiter_t;

/* Ініціалізація арбітра 2oo3 */
void tmr_arbiter_init(tmr_arbiter_t *arbiter, float max_tolerance, uint32_t fault_threshold);

/* Виконання мажоритарного голосування для трьох аналогових/цифрових вимірів */
tmr_vote_result_t tmr_arbiter_vote(tmr_arbiter_t *arbiter, float ch_a, float ch_b, float ch_c);

/* Процедура відновлення завислої шини I2C (9 тактів SCL + STOP) */
i2c_recover_status_t i2c_recover_bus(const i2c_gpio_ops_t *gpio);

#ifdef __cplusplus
}
#endif

#endif /* RELIABILITY_ARBITER_H */

/* ------------------ РЕАЛІЗАЦІЯ C ------------------ */

#include <math.h>

void tmr_arbiter_init(tmr_arbiter_t *arbiter, float max_tolerance, uint32_t fault_threshold) {
    if (!arbiter) return;
    arbiter->max_tolerance = max_tolerance;
    arbiter->fault_threshold = fault_threshold;
    for (int i = 0; i < 3; ++i) {
        arbiter->fault_counters[i] = 0;
        arbiter->channel_disabled[i] = false;
    }
}

static inline float tmr_abs(float v) {
    return (v < 0.0f) ? -v : v;
}

tmr_vote_result_t tmr_arbiter_vote(tmr_arbiter_t *arbiter, float ch_a, float ch_b, float ch_c) {
    tmr_vote_result_t res;
    res.system_healthy = true;
    res.failed_channel_index = -1;
    res.healthy_channels_count = 3;

    for (int i = 0; i < 3; ++i) {
        res.ch_status[i] = arbiter->channel_disabled[i] ? CHANNEL_FAULTY : CHANNEL_HEALTHY;
        if (arbiter->channel_disabled[i]) {
            res.healthy_channels_count--;
        }
    }

    float vals[3] = {ch_a, ch_b, ch_c};

    /* Перевірка попарної збіжності між каналами */
    bool match_ab = (tmr_abs(vals[0] - vals[1]) <= arbiter->max_tolerance);
    bool match_bc = (tmr_abs(vals[1] - vals[2]) <= arbiter->max_tolerance);
    bool match_ac = (tmr_abs(vals[0] - vals[2]) <= arbiter->max_tolerance);

    if (match_ab && match_bc) {
        /* Усі три канали узгоджені — беремо медіану або середнє */
        res.voted_value = (vals[0] + vals[1] + vals[2]) / 3.0f;
    } else if (match_ab) {
        /* Канал C розходиться з A та B */
        res.voted_value = (vals[0] + vals[1]) / 2.0f;
        res.ch_status[2] = CHANNEL_DISCREPANCY;
        res.failed_channel_index = 2;
        arbiter->fault_counters[2]++;
    } else if (match_bc) {
        /* Канал A розходиться з B та C */
        res.voted_value = (vals[1] + vals[2]) / 2.0f;
        res.ch_status[0] = CHANNEL_DISCREPANCY;
        res.failed_channel_index = 0;
        arbiter->fault_counters[0]++;
    } else if (match_ac) {
        /* Канал B розходиться з A та C */
        res.voted_value = (vals[0] + vals[2]) / 2.0f;
        res.ch_status[1] = CHANNEL_DISCREPANCY;
        res.failed_channel_index = 1;
        arbiter->fault_counters[1]++;
    } else {
        /* Повний розсинхрон: жодна пара не збігається (подвійна аварія) */
        res.voted_value = vals[0];
        res.system_healthy = false;
        res.failed_channel_index = -1;
        for (int i = 0; i < 3; ++i) {
            res.ch_status[i] = CHANNEL_FAULTY;
            arbiter->fault_counters[i]++;
        }
    }

    /* Оновлення статусу деградації каналів */
    for (int i = 0; i < 3; ++i) {
        if (arbiter->fault_counters[i] >= arbiter->fault_threshold) {
            arbiter->channel_disabled[i] = true;
            res.ch_status[i] = CHANNEL_FAULTY;
        }
    }

    return res;
}

i2c_recover_status_t i2c_recover_bus(const i2c_gpio_ops_t *gpio) {
    if (!gpio || !gpio->delay_us) {
        return I2C_RECOVER_SDA_STUCK_LOW;
    }

    /* 1. Перевірка: чи застрягла лінія SCL у нулі (апаратна несправність) */
    gpio->set_sda_input();
    gpio->set_scl_output();
    gpio->write_scl(true);
    gpio->delay_us(5);

    if (!gpio->read_scl()) {
        return I2C_RECOVER_SCL_STUCK_LOW; /* SCL замкнено на GND */
    }

    /* 2. Якщо SDA вже висока — шина вільна */
    if (gpio->read_sda()) {
        return I2C_RECOVER_OK;
    }

    /* 3. Генерація до 9 тактів SCL для звільнення веденого пристрою */
    bool sda_freed = false;
    for (int i = 0; i < 9; ++i) {
        gpio->write_scl(false);
        gpio->delay_us(5);
        gpio->write_scl(true);
        gpio->delay_us(5);

        /* Якщо ведений відпустив SDA, виходимо з циклу */
        if (gpio->read_sda()) {
            sda_freed = true;
            break;
        }
    }

    if (!sda_freed) {
        return I2C_RECOVER_SDA_STUCK_LOW; /* Ведений чіп не відпустив лінію */
    }

    /* 4. Генерація стану STOP: спадний перехід SDA, потім підйом при високому SCL */
    gpio->set_sda_output();
    gpio->write_sda(false);
    gpio->delay_us(5);
    gpio->write_scl(true);
    gpio->delay_us(5);
    gpio->write_sda(true);
    gpio->delay_us(5);

    gpio->set_sda_input();
    return gpio->read_sda() ? I2C_RECOVER_BUS_CLEARED : I2C_RECOVER_SDA_STUCK_LOW;
}

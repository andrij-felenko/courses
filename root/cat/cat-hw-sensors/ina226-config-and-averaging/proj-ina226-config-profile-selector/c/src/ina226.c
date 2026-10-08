/**
 * @file ina226.c
 * @brief Реалізація функцій C-драйвера та кінцевого автомата INA226.
 *
 * Містить обчислення калібрувального регістра, побудову конфігураційного слова (0x00),
 * неблокуючу обробку Conversion Ready (CVRF / ALERT) та конверсію сирих даних у фізичні одиниці.
 */

#include "ina226.h"
#include <math.h>
#include <stddef.h>

/* Таблиці переведення кодів VSHCT/VBUSCT у мікросекунди */
static const uint32_t k_conv_time_us_lut[8] = {
    140U, 204U, 332U, 588U, 1100U, 2116U, 4156U, 8244U
};

/* Таблиця коефіцієнтів усереднення AVG */
static const uint16_t k_avg_count_lut[8] = {
    1U, 4U, 16U, 64U, 128U, 256U, 512U, 1024U
};

/**
 * @brief Обчислення очікуваного часу конверсії в мікросекундах.
 */
uint32_t ina226_calculate_conversion_time_us(const ina226_profile_t *profile)
{
    if (!profile) {
        return 0U;
    }
    
    uint32_t t_sh = k_conv_time_us_lut[profile->vshct & 0x07U];
    uint32_t t_bus = k_conv_time_us_lut[profile->vbusct & 0x07U];
    uint32_t avg = k_avg_count_lut[profile->avg & 0x07U];
    
    uint32_t single_cycle_us = 0U;
    switch (profile->mode) {
        case INA226_MODE_SHUNT_TRIGGERED:
        case INA226_MODE_SHUNT_CONTINUOUS:
            single_cycle_us = t_sh;
            break;
        case INA226_MODE_BUS_TRIGGERED:
        case INA226_MODE_BUS_CONTINUOUS:
            single_cycle_us = t_bus;
            break;
        case INA226_MODE_BOTH_TRIGGERED:
        case INA226_MODE_BOTH_CONTINUOUS:
        default:
            single_cycle_us = t_sh + t_bus;
            break;
    }
    
    return single_cycle_us * avg;
}

/**
 * @brief Ініціалізація чипа та розрахунок калібрування.
 */
ina226_status_t ina226_init(ina226_fsm_t *fsm, uint8_t i2c_addr, float r_shunt, float max_expected_current_a)
{
    if (!fsm || r_shunt <= 0.0f || max_expected_current_a <= 0.0f) {
        return INA226_ERR_PARAM;
    }
    
    fsm->i2c_addr = i2c_addr;
    fsm->r_shunt_ohm = r_shunt;
    fsm->alert_triggered = false;
    fsm->state = INA226_FSM_UNINIT;
    fsm->last_error = INA226_OK;

    /* 1. Перевірка ідентифікаторів виготівника та кристала */
    uint16_t mfg_id = 0, die_id = 0;
    if (i2c_read_reg16(fsm->i2c_addr, INA226_REG_MANUFACTURER_ID, &mfg_id) != I2C_OK ||
        i2c_read_reg16(fsm->i2c_addr, INA226_REG_DIE_ID, &die_id) != I2C_OK) {
        fsm->last_error = INA226_ERR_I2C;
        fsm->state = INA226_FSM_ERROR;
        return INA226_ERR_I2C;
    }

    if (mfg_id != INA226_MANUFACTURER_ID_VAL || (die_id & 0xFFF0U) != INA226_DIE_ID_VAL) {
        fsm->last_error = INA226_ERR_ID;
        fsm->state = INA226_FSM_ERROR;
        return INA226_ERR_ID;
    }

    /* 2. Обчислення дискретності струму Current_LSB = Max_Current / 32768 */
    fsm->current_lsb_a = max_expected_current_a / 32768.0f;

    /* 3. Розрахунок калібрувального регістра: CAL = trunc(0.00512 / (Current_LSB * R_shunt)) */
    float cal_raw = 0.00512f / (fsm->current_lsb_a * fsm->r_shunt_ohm);
    fsm->cal_val = (uint16_t)floorf(cal_raw);

    /* 4. Запис регістра Calibration (0x05) */
    if (i2c_write_reg16(fsm->i2c_addr, INA226_REG_CALIBRATION, fsm->cal_val) != I2C_OK) {
        fsm->last_error = INA226_ERR_I2C;
        fsm->state = INA226_FSM_ERROR;
        return INA226_ERR_I2C;
    }

    /* 5. Налаштування регістра Mask/Enable (0x06): увімкнення CVRF на лінії ALERT */
    uint16_t mask_enable = INA226_MASK_CNVR | INA226_MASK_APOL; /* Active-Low ALERT */
    if (i2c_write_reg16(fsm->i2c_addr, INA226_REG_MASK_ENABLE, mask_enable) != I2C_OK) {
        fsm->last_error = INA226_ERR_I2C;
        fsm->state = INA226_FSM_ERROR;
        return INA226_ERR_I2C;
    }

    fsm->state = INA226_FSM_IDLE;
    return INA226_OK;
}

/**
 * @brief Динамічне відновлення конфігураційного профілю INA226.
 */
ina226_status_t ina226_set_profile(ina226_fsm_t *fsm, const ina226_profile_t *profile)
{
    if (!fsm || !profile) {
        return INA226_ERR_PARAM;
    }

    /* Формування 16-бітного конфігураційного слова (Регістр 0x00) */
    uint16_t config = 0U;
    config |= ((uint16_t)profile->avg << INA226_CONFIG_AVG_SHIFT) & INA226_CONFIG_AVG_MASK;
    config |= ((uint16_t)profile->vbusct << INA226_CONFIG_VBUSCT_SHIFT) & INA226_CONFIG_VBUSCT_MASK;
    config |= ((uint16_t)profile->vshct << INA226_CONFIG_VSHCT_SHIFT) & INA226_CONFIG_VSHCT_MASK;
    config |= ((uint16_t)profile->mode << INA226_CONFIG_MODE_SHIFT) & INA226_CONFIG_MODE_MASK;

    if (i2c_write_reg16(fsm->i2c_addr, INA226_REG_CONFIG, config) != I2C_OK) {
        fsm->last_error = INA226_ERR_I2C;
        return INA226_ERR_I2C;
    }

    /* Запис калібрування заново після зміни конфігурації */
    (void)i2c_write_reg16(fsm->i2c_addr, INA226_REG_CALIBRATION, fsm->cal_val);

    fsm->active_profile = *profile;
    fsm->estimated_conv_us = ina226_calculate_conversion_time_us(profile);
    fsm->alert_triggered = false;

    return INA226_OK;
}

/**
 * @brief Опитування прапорця Conversion Ready (CVRF) у Mask/Enable.
 */
ina226_status_t ina226_is_conversion_ready(ina226_fsm_t *fsm, bool *ready)
{
    if (!fsm || !ready) {
        return INA226_ERR_PARAM;
    }

    uint16_t mask_reg = 0;
    if (i2c_read_reg16(fsm->i2c_addr, INA226_REG_MASK_ENABLE, &mask_reg) != I2C_OK) {
        *ready = false;
        return INA226_ERR_I2C;
    }

    /* CVRF — це біт 3 у регістрі Mask/Enable (0x06). Читання регістра автоматично скидає CVRF */
    *ready = ((mask_reg & INA226_MASK_CVRF) != 0U);
    return INA226_OK;
}

/**
 * @brief Неблокуюче зчитування сирих та розрахованих фізичних даних.
 */
ina226_status_t ina226_read_data(ina226_fsm_t *fsm, ina226_data_t *data)
{
    if (!fsm || !data) {
        return INA226_ERR_PARAM;
    }

    uint16_t bus_raw = 0, power_raw = 0;
    int16_t shunt_raw = 0, current_raw = 0;

    /* 1. Зчитування регістра напруги шини (0x02) */
    if (i2c_read_reg16(fsm->i2c_addr, INA226_REG_BUSVOLT, &bus_raw) != I2C_OK) {
        return INA226_ERR_I2C;
    }

    /* 2. Зчитування регістра падіння напруги на шунті (0x01) */
    if (i2c_read_reg16(fsm->i2c_addr, INA226_REG_SHUNTVOLT, (uint16_t *)&shunt_raw) != I2C_OK) {
        return INA226_ERR_I2C;
    }

    /* 3. Зчитування регістра обчисленого струму (0x04) */
    if (i2c_read_reg16(fsm->i2c_addr, INA226_REG_CURRENT, (uint16_t *)&current_raw) != I2C_OK) {
        return INA226_ERR_I2C;
    }

    /* 4. Зчитування регістра потужності (0x03) */
    if (i2c_read_reg16(fsm->i2c_addr, INA226_REG_POWER, &power_raw) != I2C_OK) {
        return INA226_ERR_I2C;
    }

    /* Перетворення сирих значень у фізичні величини:
     * - Bus Voltage: LSB = 1.25 мВ = 0.00125 В
     * - Shunt Voltage: LSB = 2.5 мкВ = 0.0025 мВ
     * - Current: LSB = Current_LSB
     * - Power: LSB = 25 * Current_LSB
     */
    data->raw_bus = bus_raw;
    data->raw_shunt = shunt_raw;
    data->raw_current = current_raw;
    data->raw_power = power_raw;

    data->bus_voltage_v = ((float)bus_raw) * 0.00125f;
    data->shunt_voltage_mv = ((float)shunt_raw) * 0.0025f;
    data->current_a = ((float)current_raw) * fsm->current_lsb_a;
    data->power_w = ((float)power_raw) * (25.0f * fsm->current_lsb_a);

    return INA226_OK;
}

/**
 * @brief Зовнішній обробник переривання EXTI від сигналу ALERT INA226.
 */
void ina226_on_alert_interrupt(ina226_fsm_t *fsm)
{
    if (fsm) {
        fsm->alert_triggered = true;
    }
}

/**
 * @brief Неблокуючий прохід кінцевого автомата (FSM).
 */
void ina226_fsm_process(ina226_fsm_t *fsm, uint32_t current_tick_ms)
{
    if (!fsm || fsm->state == INA226_FSM_UNINIT) {
        return;
    }

    switch (fsm->state) {
        case INA226_FSM_IDLE:
            fsm->conv_start_ms = current_tick_ms;
            fsm->state = INA226_FSM_WAIT_CONV;
            break;

        case INA226_FSM_CONFIGURING:
            if (ina226_set_profile(fsm, &fsm->active_profile) == INA226_OK) {
                fsm->conv_start_ms = current_tick_ms;
                fsm->state = INA226_FSM_WAIT_CONV;
            } else {
                fsm->state = INA226_FSM_ERROR;
            }
            break;

        case INA226_FSM_WAIT_CONV: {
            bool ready = false;
            
            /* Перевірка або апаратного переривання ALERT, або прапорця CVRF */
            if (fsm->alert_triggered) {
                ready = true;
            } else {
                (void)ina226_is_conversion_ready(fsm, &ready);
            }

            if (ready) {
                fsm->alert_triggered = false;
                fsm->state = INA226_FSM_READ_DATA;
            } else {
                /* Захист від таймауту у разі збою вимірювань (2х від розрахованого часу) */
                uint32_t max_wait_ms = (fsm->estimated_conv_us / 1000U) * 2U + 20U;
                if ((current_tick_ms - fsm->conv_start_ms) > max_wait_ms) {
                    fsm->last_error = INA226_ERR_TIMEOUT;
                    fsm->state = INA226_FSM_ERROR;
                }
            }
            break;
        }

        case INA226_FSM_READ_DATA:
            if (ina226_read_data(fsm, &fsm->latest_data) == INA226_OK) {
                fsm->state = INA226_FSM_IDLE;
            } else {
                fsm->last_error = INA226_ERR_I2C;
                fsm->state = INA226_FSM_ERROR;
            }
            break;

        case INA226_FSM_ERROR:
            /* Спроба автоматичного відновлення: перезапуск ініціалізації */
            if (i2c_write_reg16(fsm->i2c_addr, INA226_REG_CONFIG, INA226_CONFIG_RST_MASK) == I2C_OK) {
                fsm->state = INA226_FSM_IDLE;
            }
            break;

        default:
            fsm->state = INA226_FSM_IDLE;
            break;
    }
}

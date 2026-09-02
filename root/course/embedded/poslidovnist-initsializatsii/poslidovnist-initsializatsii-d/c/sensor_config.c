#include "platform.h"
#include "sensor.h"

/*
 * Ієрархічний порядок: електрика виводів -> шкали -> фільтри -> переривання,
 * і аж потім активація. Кожен запис несе свою маску значущих розрядів, бо в
 * тих самих регістрах живуть RO-прапорці й фабричні константи.
 */
static const reg_verify_entry_t k_config_sequence[] = {
    /* Крок 1: Open-Drain + активний нуль + фіксація прапорця */
    { REG_INT_CFG, INT_CFG_OPEN_DRAIN | INT_CFG_ACTIVE_LOW | INT_CFG_LATCHED,
      INT_CFG_CARE_MASK },
    /* Крок 2: шкала ±8g і три осі — до вмикання цифрового тракту */
    { REG_RANGE, RANGE_FS_8G | RANGE_AXIS_XYZ, RANGE_CARE_MASK },
    /* Крок 3: ODR і смуга DLPF — до першого вимірювання, поки буфер фільтра порожній */
    { REG_FILTER, FILTER_ODR_104HZ | FILTER_DLPF_50HZ, FILTER_CARE_MASK },
    /* Крок 4: переривання за готовністю даних і кільцевий FIFO */
    { REG_INT_EN, INT_EN_DRDY | INT_EN_FIFO_WM | FIFO_MODE_STREAM, INT_EN_CARE_MASK },
};

/*
 * Read-Back: ACK на 9-му такті підтверджує лише прийом байта зсувним регістром,
 * а не запис у комірку конфігурації. Тому пишемо, читаємо назад і порівнюємо
 * ТІЛЬКИ значущі розряди — пряме "==" зламав би перший же апаратний прапорець.
 */
init_result_t sensor_write_verified(uint8_t dev_addr, const reg_verify_entry_t *entry)
{
    if (i2c_write_reg(dev_addr, entry->reg_addr, entry->target_val) != BUS_OK) {
        return INIT_ERR_BUS;
    }

    uint8_t read_val = 0;
    if (i2c_read_reg(dev_addr, entry->reg_addr, &read_val) != BUS_OK) {
        return INIT_ERR_BUS;
    }

    uint8_t target_masked = (uint8_t)(entry->target_val & entry->care_mask);
    uint8_t read_masked = (uint8_t)(read_val & entry->care_mask);
    if (target_masked != read_masked) {
        return INIT_ERR_VERIFY;
    }
    return INIT_OK;
}

init_result_t sensor_apply_config(uint8_t dev_addr, uint8_t *out_failed_reg)
{
    static const reg_verify_entry_t standby = {
        REG_PWR, PWR_MODE_STANDBY, PWR_MODE_CARE_MASK
    };
    static const reg_verify_entry_t activate = {
        REG_PWR, PWR_MODE_NORMAL, PWR_MODE_CARE_MASK
    };

    *out_failed_reg = 0;

    /* Нульовий крок: у робочому режимі конфігураційні регістри заблоковані */
    init_result_t rc = sensor_write_verified(dev_addr, &standby);
    if (rc != INIT_OK) {
        *out_failed_reg = standby.reg_addr;
        return rc;
    }

    for (unsigned i = 0; i < sizeof(k_config_sequence) / sizeof(k_config_sequence[0]); ++i) {
        rc = sensor_write_verified(dev_addr, &k_config_sequence[i]);
        if (rc != INIT_OK) {
            *out_failed_reg = k_config_sequence[i].reg_addr;
            return rc;
        }
    }

    /* Крок 5: переведення у робочий режим — останньою дією */
    rc = sensor_write_verified(dev_addr, &activate);
    if (rc != INIT_OK) {
        *out_failed_reg = activate.reg_addr;
        return rc;
    }

    /* Час прогріву: до його кінця відліки пливуть за нулем */
    delay_ms(T_SETTLING_MS);

    uint8_t filter = 0;
    if (i2c_read_reg(dev_addr, REG_FILTER, &filter) != BUS_OK) {
        *out_failed_reg = REG_FILTER;
        return INIT_ERR_BUS;
    }
    if ((filter & BIT_FILTER_READY) == 0) {
        *out_failed_reg = REG_FILTER; /* фільтр не вийшов на режим у відведений час */
        return INIT_ERR_TIMEOUT;
    }
    return INIT_OK;
}

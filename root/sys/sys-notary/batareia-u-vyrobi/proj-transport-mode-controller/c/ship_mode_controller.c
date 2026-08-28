/* ship_mode_controller.c */
#include "ship_mode_controller.h"

ship_mode_status_t ship_mode_verify_safety(const ship_mode_driver_t *drv) {
    if (!drv || !drv->read_battery_mv || !drv->is_vbus_present) {
        return SHIP_MODE_ERR_I2C_COMM;
    }

    if (drv->is_vbus_present()) {
        return SHIP_MODE_ERR_VBUS_CONNECTED; /* Не можна вимикати при підключеній зарядці */
    }

    uint32_t v_batt = drv->read_battery_mv();
    if (v_batt > SHIP_MODE_MAX_VOLTAGE_MV) {
        return SHIP_MODE_ERR_VOLTAGE_TOO_HIGH; /* Перевищує 30% SoC для UN 3480 */
    }
    if (v_batt < SHIP_MODE_MIN_VOLTAGE_MV) {
        return SHIP_MODE_ERR_VOLTAGE_TOO_LOW;  /* Ризик глибокого розряду на складі */
    }

    return SHIP_MODE_OK;
}

ship_mode_status_t ship_mode_enter(const ship_mode_driver_t *drv) {
    ship_mode_status_t check = ship_mode_verify_safety(drv);
    if (check != SHIP_MODE_OK) {
        return check;
    }

    uint8_t reg_val = 0;
    if (!drv->i2c_read(drv->i2c_address, PMIC_REG_POWER_CONFIG, &reg_val)) {
        return SHIP_MODE_ERR_I2C_COMM;
    }

    /* Налаштовуємо 3-секундний дебаунс на кнопці для захисту від вібрації */
    reg_val |= PMIC_BIT_WAKE_PRESS_TIME_3S;
    /* Встановлюємо біт переходу в Ship Mode */
    reg_val |= PMIC_BIT_SHIP_MODE_ENTER;

    if (!drv->i2c_write(drv->i2c_address, PMIC_REG_POWER_CONFIG, reg_val)) {
        return SHIP_MODE_ERR_I2C_COMM;
    }

    /* Очікування вимкнення живлення ключем PMIC */
    while (1) {
        __asm volatile("wfi"); /* Sleep до знеструмлення */
    }

    return SHIP_MODE_OK;
}

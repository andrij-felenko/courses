/* ship_mode_controller.h - Реалізація контролера транспортного режиму на C */
#ifndef SHIP_MODE_CONTROLLER_H
#define SHIP_MODE_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

#define SHIP_MODE_MAX_VOLTAGE_MV   3800  /* Максимальна напруга 30% SoC (3.80 В) */
#define SHIP_MODE_MIN_VOLTAGE_MV   3500  /* Мінімальна напруга для консервації */
#define PMIC_REG_POWER_CONFIG      0x05  /* Регістр конфігурації живлення PMIC */
#define PMIC_BIT_SHIP_MODE_ENTER   (1 << 6)
#define PMIC_BIT_WAKE_PRESS_TIME_3S (1 << 4)

typedef enum {
    SHIP_MODE_OK = 0,
    SHIP_MODE_ERR_VOLTAGE_TOO_HIGH,
    SHIP_MODE_ERR_VOLTAGE_TOO_LOW,
    SHIP_MODE_ERR_I2C_COMM,
    SHIP_MODE_ERR_VBUS_CONNECTED
} ship_mode_status_t;

typedef struct {
    uint8_t i2c_address;
    uint32_t (*read_battery_mv)(void);
    bool (*is_vbus_present)(void);
    bool (*i2c_write)(uint8_t dev_addr, uint8_t reg_addr, uint8_t value);
    bool (*i2c_read)(uint8_t dev_addr, uint8_t reg_addr, uint8_t *value);
} ship_mode_driver_t;

ship_mode_status_t ship_mode_verify_safety(const ship_mode_driver_t *drv);
ship_mode_status_t ship_mode_enter(const ship_mode_driver_t *drv);

#endif /* SHIP_MODE_CONTROLLER_H */

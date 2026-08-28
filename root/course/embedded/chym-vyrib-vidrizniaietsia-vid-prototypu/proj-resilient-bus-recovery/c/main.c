#include <stdint.h>
#include <stdbool.h>

/* Абстракція апаратної платформи для керування ніжками GPIO */
typedef struct {
    void (*set_scl)(bool high);
    void (*set_sda)(bool high);
    bool (*read_scl)(void);
    bool (*read_sda)(void);
    void (*delay_us)(uint32_t us);
    void (*reinit_i2c_hardware)(void);
} i2c_bus_hal_t;

typedef enum {
    BUS_OK = 0,
    BUS_RECOVERED,
    BUS_ERROR_SCL_STUCK_LOW,
    BUS_ERROR_SDA_STUCK_LOW
} bus_status_t;

/* Виробнича функція вибивання шини з клінчу */
bus_status_t i2c_bus_recover(const i2c_bus_hal_t *hal) {
    if (!hal) {
        return BUS_ERROR_SCL_STUCK_LOW;
    }

    /* 1. Відпускаємо обидві лінії у високий стан */
    hal->set_scl(true);
    hal->set_sda(true);
    hal->delay_us(5);

    /* Якщо SCL притиснутий до землі — це апаратне КЗ або завислий Clock Stretch */
    if (!hal->read_scl()) {
        return BUS_ERROR_SCL_STUCK_LOW;
    }

    /* Якщо лінія SDA вже вільна — відновлення не потрібне */
    if (hal->read_sda()) {
        return BUS_OK;
    }

    /* 2. Генеруємо до 9 тактових імпульсів для завершення передачі веденим */
    bool sda_released = false;
    for (uint8_t i = 0; i < 9; ++i) {
        hal->set_scl(false);
        hal->delay_us(5);
        hal->set_scl(true);
        hal->delay_us(5);

        if (hal->read_sda()) {
            sda_released = true;
            break;
        }
    }

    if (!sda_released) {
        return BUS_ERROR_SDA_STUCK_LOW;
    }

    /* 3. Формуємо коректну умову STOP: перехід SDA 0 -> 1 при SCL = 1 */
    hal->set_sda(false);
    hal->delay_us(5);
    hal->set_scl(true);
    hal->delay_us(5);
    hal->set_sda(true);
    hal->delay_us(5);

    /* 4. Повертаємо виводи під контроль апаратного периферійного блока I2C */
    hal->reinit_i2c_hardware();

    return BUS_RECOVERED;
}

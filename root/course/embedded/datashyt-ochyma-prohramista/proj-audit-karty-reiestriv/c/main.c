#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Оффсети регістрів 3-осьового акселерометра */
#define REG_WHO_AM_I        0x0F
#define REG_CTRL_REG1       0x20
#define REG_CTRL_REG2       0x21
#define REG_STATUS_REG      0x27
#define REG_OUT_X_L         0x28
#define REG_OUT_X_H         0x29
#define REG_OUT_Y_L         0x2A
#define REG_OUT_Y_H         0x2B
#define REG_OUT_Z_L         0x2C
#define REG_OUT_Z_H         0x2D

/* Очікувані константи та бітові маски */
#define CHIP_ID_EXPECTED    0x6A
#define I2C_AUTO_INCREMENT  0x80  /* Старший біт адреси для Burst-читання ST-чипів */

/* CTRL_REG1 біти: [7:4 ODR] [3:2 PowerMode] [1:0 AxesEnable] */
#define CTRL1_ODR_100HZ     (0x04 << 4)
#define CTRL1_AXES_XYZ_EN   (0x07 << 0)

/* CTRL_REG2 біти: [7 BDU] [5:4 FSR] */
#define CTRL2_BDU_ENABLE    (1 << 7)
#define CTRL2_FSR_2G        (0x00 << 4)
#define CTRL2_FSR_4G        (0x01 << 4)

/* STATUS_REG біти (W1C або RO) */
#define STATUS_ZYXDA        (1 << 3)  /* Дані по всіх 3 осях готові */
#define STATUS_FIFO_OVR     (1 << 6)  /* Переповнення буфера FIFO */

/* Коди повернення процедури аудиту */
typedef enum {
    AUDIT_OK = 0,
    AUDIT_ERR_COMM = -1,
    AUDIT_ERR_INVALID_ID = -2,
    AUDIT_ERR_REG_RW_FAIL = -3,
    AUDIT_ERR_TIMEOUT = -4
} audit_status_t;

/* Структура абстракції апаратного транспорту шини */
typedef struct {
    void *bus_ctx;
    uint8_t dev_addr;
    int (*read_reg)(void *ctx, uint8_t dev_addr, uint8_t reg, uint8_t *buf, size_t len);
    int (*write_reg)(void *ctx, uint8_t dev_addr, uint8_t reg, const uint8_t *buf, size_t len);
} sensor_bus_t;

/* Результат вимірювання у фізичних одиницях SI (м/с²) */
typedef struct {
    float x;
    float y;
    float z;
} accel_data_t;

/* 1. Аудит ідентифікатора чипа */
audit_status_t sensor_verify_identity(const sensor_bus_t *bus) {
    uint8_t chip_id = 0;
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, REG_WHO_AM_I, &chip_id, 1) != 0) {
        return AUDIT_ERR_COMM;
    }
    if (chip_id != CHIP_ID_EXPECTED) {
        return AUDIT_ERR_INVALID_ID;
    }
    return AUDIT_OK;
}

/* 2. Аудит доступності запису в R/W регістр без сліпих побічних ефектів */
audit_status_t sensor_audit_rw_register(const sensor_bus_t *bus) {
    uint8_t original_val = 0;
    uint8_t test_val = CTRL1_ODR_100HZ | CTRL1_AXES_XYZ_EN;
    uint8_t readback_val = 0;

    /* Зберігаємо початковий стан регістра */
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &original_val, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    /* Записуємо тестову конфігурацію */
    if (bus->write_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &test_val, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    /* Зчитуємо назад і порівнюємо */
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &readback_val, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    if (readback_val != test_val) {
        return AUDIT_ERR_REG_RW_FAIL;
    }

    return AUDIT_OK;
}

/* 3. Ініціалізація: блокування BDU + шкала FSR + частота ODR */
audit_status_t sensor_init_configuration(const sensor_bus_t *bus) {
    uint8_t ctrl2 = CTRL2_BDU_ENABLE | CTRL2_FSR_2G;
    if (bus->write_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG2, &ctrl2, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    uint8_t ctrl1 = CTRL1_ODR_100HZ | CTRL1_AXES_XYZ_EN;
    if (bus->write_reg(bus->bus_ctx, bus->dev_addr, REG_CTRL_REG1, &ctrl1, 1) != 0) {
        return AUDIT_ERR_COMM;
    }

    return AUDIT_OK;
}

/* 4. Пакетне вичитування даних та перетворення у фізичну величину */
audit_status_t sensor_read_acceleration(const sensor_bus_t *bus, accel_data_t *out_data) {
    uint8_t raw_buf[6];
    uint8_t start_reg = REG_OUT_X_L | I2C_AUTO_INCREMENT;

    /* Пакетне читання 6 регістрів поспіль за одну транзакцію */
    if (bus->read_reg(bus->bus_ctx, bus->dev_addr, start_reg, raw_buf, 6) != 0) {
        return AUDIT_ERR_COMM;
    }

    /* Склеювання байтів Little-Endian у 16-бітні знакові числа */
    int16_t raw_x = (int16_t)((uint16_t)raw_buf[0] | ((uint16_t)raw_buf[1] << 8));
    int16_t raw_y = (int16_t)((uint16_t)raw_buf[2] | ((uint16_t)raw_buf[3] << 8));
    int16_t raw_z = (int16_t)((uint16_t)raw_buf[4] | ((uint16_t)raw_buf[5] << 8));

    /* Масштабування: для FSR = ±2g чутливість становить 0.061 мг/LSB */
    const float sensitivity_g_per_lsb = 0.000061f;
    const float g_to_ms2 = 9.80665f;

    out_data->x = (float)raw_x * sensitivity_g_per_lsb * g_to_ms2;
    out_data->y = (float)raw_y * sensitivity_g_per_lsb * g_to_ms2;
    out_data->z = (float)raw_z * sensitivity_g_per_lsb * g_to_ms2;

    return AUDIT_OK;
}

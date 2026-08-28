// ============================================================================
// C99: Еталонний переносний драйвер цифрового акселерометра
// ============================================================================
#ifndef CHIP_ACCEL_DRIVER_H
#define CHIP_ACCEL_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

// --- Регістрова карта акселерометра ---
#define CHIP_REG_WHO_AM_I       0x0F
#define CHIP_REG_CTRL_REG1      0x20
#define CHIP_REG_CTRL_REG4      0x23
#define CHIP_REG_STATUS_REG     0x27
#define CHIP_REG_OUT_X_L        0x28

// --- Очікуваний ідентифікатор мікросхеми ---
#define CHIP_ID_VALUE           0x33

// --- Бітові маски регістрів ---
#define CTRL1_ODR_100HZ         (0x05 << 4) // Частота опитування 100 Гц
#define CTRL1_ZEN               (1U << 2)   // Дозвіл осі Z
#define CTRL1_YEN               (1U << 1)   // Дозвіл осі Y
#define CTRL1_XEN               (1U << 0)   // Дозвіл осі X
#define CTRL1_XYZ_ENABLE        (CTRL1_XEN | CTRL1_YEN | CTRL1_ZEN)

#define CTRL4_BDU_ENABLE        (1U << 7)   // Блокування оновлень (BDU)
#define CTRL4_FS_MASK           (0x03 << 4) // Маска вибору діапазону

#define STATUS_ZYXDA_FLAG       (1U << 3)   // Нові дані готові по всіх осях
#define I2C_AUTO_INCREMENT      0x80        // Прапорець автоінкременту адреси

#define STANDARD_GRAVITY_SI     9.80665f    // 1g у м/с²

// Коди статусів драйвера
typedef enum {
    CHIP_OK                 =  0,
    CHIP_ERR_INVALID_PARAM  = -1,
    CHIP_ERR_COMM           = -2,
    CHIP_ERR_TIMEOUT        = -3,
    CHIP_ERR_NOT_FOUND      = -4,
    CHIP_ERR_NOT_INIT       = -5,
    CHIP_ERR_NO_DATA        = -6
} chip_status_t;

// Допустимі діапазони вимірювань
typedef enum {
    CHIP_RANGE_2G  = 0, // ±2g  (чутливість 0.061 мг/LSB)
    CHIP_RANGE_4G  = 1, // ±4g  (чутливість 0.122 мг/LSB)
    CHIP_RANGE_8G  = 2, // ±8g  (чутливість 0.244 мг/LSB)
    CHIP_RANGE_16G = 3  // ±16g (чутливість 0.732 мг/LSB)
} chip_range_t;

// Вектор триосьового прискорення у фізичних одиницях SI
typedef struct {
    float x; // Прискорення по осі X у м/с²
    float y; // Прискорення по осі Y у м/с²
    float z; // Прискорення по осі Z у м/с²
} chip_accel_si_t;

// Сигнатури функцій зв'язку платформи
typedef int32_t (*chip_read_fn)(void *user_ctx, uint8_t reg_addr, uint8_t *data, uint16_t len);
typedef int32_t (*chip_write_fn)(void *user_ctx, uint8_t reg_addr, const uint8_t *data, uint16_t len);
typedef void    (*chip_delay_fn)(uint32_t ms);

typedef struct {
    chip_read_fn  read;
    chip_write_fn write;
    chip_delay_fn delay_ms;
} chip_bus_ops_t;

// Дескриптор пристрою
typedef struct {
    const chip_bus_ops_t *bus_ops;
    void                 *user_ctx;
    uint8_t               dev_addr;
    chip_range_t          range;
    float                 scale_factor;
    uint8_t               shadow_ctrl1;
    uint8_t               shadow_ctrl4;
    bool                  is_initialized;
} chip_dev_t;

// Внутрішня функція розрахунку множника чутливості
static inline float calculate_scale_factor(chip_range_t range) {
    float mg_per_lsb;
    switch (range) {
        case CHIP_RANGE_2G:  mg_per_lsb = 0.061f; break;
        case CHIP_RANGE_4G:  mg_per_lsb = 0.122f; break;
        case CHIP_RANGE_8G:  mg_per_lsb = 0.244f; break;
        case CHIP_RANGE_16G: mg_per_lsb = 0.732f; break;
        default:             mg_per_lsb = 0.061f; break;
    }
    return (mg_per_lsb / 1000.0f) * STANDARD_GRAVITY_SI;
}

// Ініціалізація драйвера
chip_status_t chip_init(chip_dev_t *dev, const chip_bus_ops_t *bus_ops, void *user_ctx, uint8_t dev_addr) {
    if (!dev || !bus_ops || !bus_ops->read || !bus_ops->write || !bus_ops->delay_ms) {
        return CHIP_ERR_INVALID_PARAM;
    }

    memset(dev, 0, sizeof(chip_dev_t));
    dev->bus_ops = bus_ops;
    dev->user_ctx = user_ctx;
    dev->dev_addr = dev_addr;

    // Пауза 10 мс для завершення перехідних процесів живлення чипа
    dev->bus_ops->delay_ms(10);

    // Крок 1: Верифікація ідентифікатора чипа (WHO_AM_I)
    uint8_t chip_id = 0;
    int32_t res = dev->bus_ops->read(dev->user_ctx, dev->dev_addr, CHIP_REG_WHO_AM_I, &chip_id, 1);
    if (res != 0) return CHIP_ERR_COMM;
    if (chip_id != CHIP_ID_VALUE) return CHIP_ERR_NOT_FOUND;

    // Крок 2: Налаштування BDU та початкового діапазону ±2g (CTRL_REG4)
    dev->range = CHIP_RANGE_2G;
    dev->scale_factor = calculate_scale_factor(dev->range);
    dev->shadow_ctrl4 = CTRL4_BDU_ENABLE | ((uint8_t)dev->range << 4);

    res = dev->bus_ops->write(dev->user_ctx, dev->dev_addr, CHIP_REG_CTRL_REG4, &dev->shadow_ctrl4, 1);
    if (res != 0) return CHIP_ERR_COMM;

    // Крок 3: Увімкнення осей X/Y/Z та частоти 100 Гц (CTRL_REG1)
    dev->shadow_ctrl1 = CTRL1_ODR_100HZ | CTRL1_XYZ_ENABLE;
    res = dev->bus_ops->write(dev->user_ctx, dev->dev_addr, CHIP_REG_CTRL_REG1, &dev->shadow_ctrl1, 1);
    if (res != 0) return CHIP_ERR_COMM;

    dev->is_initialized = true;
    return CHIP_OK;
}

// Зміна діапазону вимірювань
chip_status_t chip_set_range(chip_dev_t *dev, chip_range_t range) {
    if (!dev || !dev->is_initialized) return CHIP_ERR_NOT_INIT;
    if (range > CHIP_RANGE_16G) return CHIP_ERR_INVALID_PARAM;

    // Оновлення тіньового регістру з ізоляцією бітового поля FS
    dev->shadow_ctrl4 = (uint8_t)((dev->shadow_ctrl4 & ~CTRL4_FS_MASK) | ((uint8_t)range << 4));

    int32_t res = dev->bus_ops->write(dev->user_ctx, dev->dev_addr, CHIP_REG_CTRL_REG4, &dev->shadow_ctrl4, 1);
    if (res != 0) return CHIP_ERR_COMM;

    dev->range = range;
    dev->scale_factor = calculate_scale_factor(range);
    return CHIP_OK;
}

// Зчитування вибірки прискорення у фізичних величинах SI
chip_status_t chip_read_accel_si(chip_dev_t *dev, chip_accel_si_t *accel_si) {
    if (!dev || !dev->is_initialized || !accel_si) return CHIP_ERR_INVALID_PARAM;

    // Перевірка прапорця готовності нових даних (DRDY)
    uint8_t status = 0;
    int32_t res = dev->bus_ops->read(dev->user_ctx, dev->dev_addr, CHIP_REG_STATUS_REG, &status, 1);
    if (res != 0) return CHIP_ERR_COMM;
    if ((status & STATUS_ZYXDA_FLAG) == 0) return CHIP_ERR_NO_DATA;

    // Пакетне зчитування 6 байтів даних з автоінкрементом
    uint8_t raw_buf[6];
    res = dev->bus_ops->read(dev->user_ctx, dev->dev_addr, CHIP_REG_OUT_X_L | I2C_AUTO_INCREMENT, raw_buf, 6);
    if (res != 0) return CHIP_ERR_COMM;

    // Збирання 16-бітних знакових слів (Little-Endian)
    int16_t raw_x = (int16_t)((uint16_t)raw_buf[0] | ((uint16_t)raw_buf[1] << 8));
    int16_t raw_y = (int16_t)((uint16_t)raw_buf[2] | ((uint16_t)raw_buf[3] << 8));
    int16_t raw_z = (int16_t)((uint16_t)raw_buf[4] | ((uint16_t)raw_buf[5] << 8));

    // Масштабування в одиниці SI (м/с²)
    accel_si->x = (float)raw_x * dev->scale_factor;
    accel_si->y = (float)raw_y * dev->scale_factor;
    accel_si->z = (float)raw_z * dev->scale_factor;

    return CHIP_OK;
}

#ifdef __cplusplus
}
#endif

#endif // CHIP_ACCEL_DRIVER_H

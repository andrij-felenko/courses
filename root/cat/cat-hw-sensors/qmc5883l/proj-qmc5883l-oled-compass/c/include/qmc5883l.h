#ifndef QMC5883L_H
#define QMC5883L_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "i2c_driver.h"

/**
 * @file qmc5883l.h
 * @brief Оголошення C-драйвера 3-осьового цифрового магнітометра QMC5883L.
 */

/* Стандартна I2C адреса чипа QMC5883L */
#define QMC5883L_I2C_ADDR             0x0D

/* Адреси регістрів QMC5883L */
#define QMC5883L_REG_DATA_X_LSB       0x00
#define QMC5883L_REG_DATA_X_MSB       0x01
#define QMC5883L_REG_DATA_Y_LSB       0x02
#define QMC5883L_REG_DATA_Y_MSB       0x03
#define QMC5883L_REG_DATA_Z_LSB       0x04
#define QMC5883L_REG_DATA_Z_MSB       0x05
#define QMC5883L_REG_STATUS           0x06
#define QMC5883L_REG_TEMP_LSB         0x07
#define QMC5883L_REG_TEMP_MSB         0x08
#define QMC5883L_REG_CTRL1            0x09
#define QMC5883L_REG_CTRL2            0x0A
#define QMC5883L_REG_SETRST           0x0B

/* Біти статусного регістра (0x06) */
#define QMC5883L_STAT_DRDY            (1U << 0) /**< Data Ready (Дані готові для зчитування) */
#define QMC5883L_STAT_OVL             (1U << 1) /**< Overflow (Переповнення вимірювального діапазону) */
#define QMC5883L_STAT_DOR             (1U << 2) /**< Data Overrun (Пропуск даних) */

/* Режими роботи (Mode) */
typedef enum {
    QMC5883L_MODE_STANDBY    = 0x00, /**< Режим очікування / зниженого споживання */
    QMC5883L_MODE_CONTINUOUS = 0x01  /**< Режим безперервних вимірювань */
} qmc5883l_mode_t;

/* Частота оновлення даних (Output Data Rate - ODR) */
typedef enum {
    QMC5883L_ODR_10HZ  = 0x00, /**< 10 Гц */
    QMC5883L_ODR_50HZ  = 0x01, /**< 50 Гц */
    QMC5883L_ODR_100HZ = 0x02, /**< 100 Гц */
    QMC5883L_ODR_200HZ = 0x03  /**< 200 Гц */
} qmc5883l_odr_t;

/* Вимірювальний діапазон (Full Scale Field Range - RNG) */
typedef enum {
    QMC5883L_RNG_2G = 0x00, /**< ±2 Гаусс (чутливість 12000 LSB/G) */
    QMC5883L_RNG_8G = 0x01  /**< ±8 Гаусс (чутливість 3000 LSB/G) */
} qmc5883l_rng_t;

/* Коефіцієнт передискретизації (Over Sampling Ratio - OSR) */
typedef enum {
    QMC5883L_OSR_512 = 0x00, /**< OSR 512 (найвища точність) */
    QMC5883L_OSR_256 = 0x01, /**< OSR 256 */
    QMC5883L_OSR_128 = 0x02, /**< OSR 128 */
    QMC5883L_OSR_64  = 0x03  /**< OSR 64 (найнижчий рівень шуму/енергоспоживання) */
} qmc5883l_osr_t;

/* Коди помилок драйвера QMC5883L */
typedef enum {
    QMC5883L_OK           =  0, /**< Операцію виконано успішно */
    QMC5883L_ERR_I2C      = -1, /**< Помилка обміну по шині I2C */
    QMC5883L_ERR_PARAM    = -2, /**< Некоректні аргументи */
    QMC5883L_ERR_OVERFLOW = -3, /**< Переповнення датчика (магнітне насичення) */
    QMC5883L_ERR_TIMEOUT  = -4  /**< Таймаут готовності даних */
} qmc5883l_err_t;

/* Структура первинних сирих даних магнітного поля */
typedef struct {
    int16_t x; /**< Сире значення X */
    int16_t y; /**< Сире значення Y */
    int16_t z; /**< Сире значення Z */
} qmc5883l_raw_t;

/* Структура параметрів калібрування (Min-Max екстремуми та зсуви Hard-Iron / Soft-Iron) */
typedef struct {
    int16_t x_min;
    int16_t x_max;
    int16_t y_min;
    int16_t y_max;
    int16_t z_min;
    int16_t z_max;
    float x_offset;     /**< Зсув по осі X (Hard-Iron) */
    float y_offset;     /**< Зсув по осі Y (Hard-Iron) */
    float z_offset;     /**< Зсув по осі Z (Hard-Iron) */
    float x_scale;      /**< Масштабний коефіцієнт по осі X (Soft-Iron) */
    float y_scale;      /**< Масштабний коефіцієнт по осі Y (Soft-Iron) */
    float z_scale;      /**< Масштабний коефіцієнт по осі Z (Soft-Iron) */
    bool is_calibrated; /**< Прапорець завершення первинного калібрування */
} qmc5883l_calib_t;

/* Структура контексту драйвера QMC5883L */
typedef struct {
    uint8_t i2c_addr;
    qmc5883l_mode_t mode;
    qmc5883l_odr_t odr;
    qmc5883l_rng_t rng;
    qmc5883l_osr_t osr;
    qmc5883l_calib_t calib;
    float declination_deg; /**< Магнітне схилення для конкретної місцевості */
} qmc5883l_t;

/**
 * @brief Ініціалізація магнітометра QMC5883L з заданими параметрами.
 */
qmc5883l_err_t qmc5883l_init(qmc5883l_t *dev, uint8_t i2c_addr, qmc5883l_mode_t mode,
                            qmc5883l_odr_t odr, qmc5883l_rng_t rng, qmc5883l_osr_t osr);

/**
 * @brief Виконання програмного скиду (Soft Reset) датчика QMC5883L.
 */
qmc5883l_err_t qmc5883l_reset(qmc5883l_t *dev);

/**
 * @brief Перевірка прапорця готовності нових даних (DRDY).
 */
bool qmc5883l_is_data_ready(qmc5883l_t *dev);

/**
 * @brief Зчитування векторних сирих даних X, Y, Z (Little-Endian).
 */
qmc5883l_err_t qmc5883l_read_raw(qmc5883l_t *dev, qmc5883l_raw_t *raw);

/**
 * @brief Перетворення сирих даних у фізичні величини (Гаусси).
 */
qmc5883l_err_t qmc5883l_read_scaled(qmc5883l_t *dev, float *x_gauss, float *y_gauss, float *z_gauss);

/**
 * @brief Скидання структури калібрування до початкових значень.
 */
void qmc5883l_calib_init(qmc5883l_calib_t *calib);

/**
 * @brief Оновлення екстремумів Min-Max новими сирими показаннями під час обертання.
 */
void qmc5883l_calib_update(qmc5883l_calib_t *calib, const qmc5883l_raw_t *raw);

/**
 * @brief Застосування компенсації Hard-Iron / Soft-Iron до сирих векторних даних.
 */
void qmc5883l_calib_apply(const qmc5883l_calib_t *calib, const qmc5883l_raw_t *raw,
                          float *cal_x, float *cal_y, float *cal_z);

/**
 * @brief Обчислення нормалізованого азимута (курсового кута) у діапазоні [0°, 360°].
 * @param x Відкаліброване значення поля по осі X.
 * @param y Відкаліброване значення поля по осі Y.
 * @param declination_deg Магнітне схилення у градусах.
 * @return Курсовий кут у градусах (0° = Північ, 90° = Схід, 180° = Південь, 270° = Захід).
 */
float qmc5883l_compute_heading(float x, float y, float declination_deg);

#endif /* QMC5883L_H */

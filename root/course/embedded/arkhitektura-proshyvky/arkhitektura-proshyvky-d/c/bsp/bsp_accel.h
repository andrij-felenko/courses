/* bsp/bsp_accel.h — публічний заголовок драйвера акселерометра ADXL345.
 * Патерн непрозорого покажчика: назовні видно ім'я типу й функції, які з ним
 * працюють, а полів структури не видно нікому. Застосунок фізично не може
 * залізти в калібрувальні коефіцієнти чи адресу шини — компілятор навіть не
 * знає розміру структури. Зміна внутрішньої будови не перезбирає застосунок. */
#ifndef BSP_ACCEL_H
#define BSP_ACCEL_H

#include "hal/hal_i2c.h"

/* Неповний тип: клієнтський код бачить лише покажчик. */
typedef struct bsp_accel bsp_accel_t;

/* Пам'ять під дескриптор дає викликач, malloc у прошивці немає.
 * Розмір із запасом; статичне твердження в bsp_accel.c стежить, щоб
 * справжня структура сюди влізла, і ламає збірку, щойно перестане. */
typedef struct {
    _Alignas(8) unsigned char bytes[64];
} bsp_accel_storage_t;

typedef enum {
    BSP_ACCEL_RANGE_2G = 0,
    BSP_ACCEL_RANGE_4G,
    BSP_ACCEL_RANGE_8G,
    BSP_ACCEL_RANGE_16G
} bsp_accel_range_t;

/* Прискорення у фізичних одиницях, а не в кодах АЦП. */
typedef struct {
    float x_g;
    float y_g;
    float z_g;
} bsp_accel_sample_t;

/* Створює дескриптор і піднімає мікросхему: перевіряє ідентифікатор,
 * ставить діапазон, частоту 100 Гц і вмикає вимірювання.
 * NULL — мікросхема не відповіла або аргументи безглузді. */
bsp_accel_t *bsp_accel_create(bsp_accel_storage_t *storage,
                              const hal_i2c_bus_t *bus,
                              uint8_t i2c_addr,
                              bsp_accel_range_t range);

/* Одне вимірювання трьох осей. false — шина або мікросхема відмовили,
 * причину віддає bsp_accel_last_error(). */
bool bsp_accel_read(bsp_accel_t *dev, bsp_accel_sample_t *out_sample);

/* Модуль вектора прискорення без складової тяжіння: саме він цікавий
 * для оцінки вібрації підшипника. */
float bsp_accel_vibration_g(const bsp_accel_sample_t *sample);

hal_i2c_status_t bsp_accel_last_error(const bsp_accel_t *dev);

/* Переводить мікросхему в очікування і робить дескриптор недійсним.
 * Пам'яті не звільняє — вона й не виділялася. */
void bsp_accel_destroy(bsp_accel_t *dev);

#endif /* BSP_ACCEL_H */

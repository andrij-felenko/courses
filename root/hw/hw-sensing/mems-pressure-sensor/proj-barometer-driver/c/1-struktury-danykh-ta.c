#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Калібрувальні коефіцієнти, прочитані з NVM та приведені до чисел з плаваючою комою
typedef struct {
    double t1, t2, t3;
    double p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11;
} BaroCalibData;

// Внутрішній стан та параметри драйвера барометра
typedef struct {
    void *bus_handle;               // Контекст апаратного драйвера шини I2C/SPI
    uint8_t dev_addr;               // I2C-адреса пристрою (зазвичай 0x76 або 0x77)
    BaroCalibData calib;            // Розпаковані коефіцієнти NVM
    double filtered_pressure_pa;    // Поточне згладжене значення тиску (стан IIR)
    double iir_alpha;               // Коефіцієнт експоненційного фільтра (0.05..0.5)
    double qnh_pa;                  // Опорний тиск рівня моря (стандартно 101325.0 Па)
    bool is_initialized;            // Прапорець успішної ініціалізації
} MemsBarometer;

// Статуси повернення функцій драйвера
typedef enum {
    BARO_OK = 0,
    BARO_ERR_COMM = -1,
    BARO_ERR_CHIP_ID = -2,
    BARO_ERR_NOT_READY = -3
} BaroStatus;

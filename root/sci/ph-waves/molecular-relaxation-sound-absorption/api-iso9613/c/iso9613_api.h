/* iso9613_api.h — C-інтерфейс бібліотеки ISO 9613-1 */
#ifndef ISO9613_API_H
#define ISO9613_API_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    ISO9613_SUCCESS = 0,
    ISO9613_ERROR_NULL_POINTER = -1,
    ISO9613_ERROR_INVALID_FREQUENCY = -2,
    ISO9613_ERROR_INVALID_TEMPERATURE = -3,
    ISO9613_ERROR_INVALID_HUMIDITY = -4,
    ISO9613_ERROR_INVALID_PRESSURE = -5
} iso9613_error_t;

/* Вхідна структура атмосферних умов */
typedef struct {
    double temperature_c;    /* Температура повітря у °C */
    double relative_humidity;/* Відносна вологість у % (0.0 .. 100.0) */
    double pressure_kpa;     /* Барометричний тиск у кПа */
} iso9613_atmosphere_t;

/* Деталізований результат розрахунку */
typedef struct {
    double alpha_total_db_km;/* Сумарне поглинання у дБ/км */
    double alpha_total_db_m; /* Сумарне поглинання у дБ/м */
    double alpha_classical;  /* Внесок в'язкості та теплопровідності (дБ/км) */
    double alpha_oxygen;     /* Внесок релаксації кисню O2 (дБ/км) */
    double alpha_nitrogen;   /* Внесок релаксації азоту N2 (дБ/км) */
    double fr_oxygen_hz;     /* Частота релаксації кисню (Гц) */
    double fr_nitrogen_hz;   /* Частота релаксації азоту (Гц) */
} iso9613_result_t;

/* Обчислення поглинання для однієї частоти */
iso9613_error_t iso9613_calculate_single(
    double frequency_hz,
    const iso9613_atmosphere_t* env,
    iso9613_result_t* result
);

/* Пакетне обчислення для масиву частот (векторизоване) */
iso9613_error_t iso9613_calculate_spectrum(
    const double* frequencies_hz,
    double* results_db_km,
    size_t count,
    const iso9613_atmosphere_t* env
);

#ifdef __cplusplus
}
#endif

#endif /* ISO9613_API_H */

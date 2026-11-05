#ifndef TANK_GAUGE_H
#define TANK_GAUGE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define TANK_GAUGE_MEDIAN_WINDOW_MAX 9
#define TANK_GAUGE_MAX_CALIB_POINTS  16

/* Точка калібрувальної кривої: висота рідини (мм) -> об'єм (літри) */
typedef struct {
    float height_mm;
    float volume_liters;
} tank_calib_point_t;

/* Конфігурація калібрування резервуара для збереження в EEPROM */
typedef struct {
    uint16_t magic;                              /* Сигнатура валідності даних */
    uint16_t num_points;                         /* Кількість точок калібрування */
    float sensor_height_mm;                      /* Відстань від давача до дна резервуара */
    float max_volume_liters;                     /* Повний об'єм резервуара */
    tank_calib_point_t points[TANK_GAUGE_MAX_CALIB_POINTS];
    uint16_t crc16;                              /* Контрольна сума */
} tank_gauge_eeprom_config_t;

/* Стан фільтра та контекст вимірювання */
typedef struct {
    float window[TANK_GAUGE_MEDIAN_WINDOW_MAX];
    uint8_t window_size;
    uint8_t head;
    uint8_t count;
    tank_gauge_eeprom_config_t config;
} tank_gauge_t;

/* Ініціалізація структури вимірювача */
bool tank_gauge_init(tank_gauge_t *gauge, uint8_t window_size, float sensor_height_mm, float max_volume_liters);

/* Додавання калібрувальної точки */
bool tank_gauge_add_calib_point(tank_gauge_t *gauge, float height_mm, float volume_liters);

/* Розрахунок швидкості звуку в повітрі за температурою (м/с) */
float tank_gauge_sound_speed(float temperature_c);

/* Перерахунок часу прольоту ехо-сигналу (мікросекунди) у дистанцію до дзеркала води (мм) */
float tank_gauge_calc_distance_mm(uint32_t tof_us, float temperature_c);

/* Оновлення медіанного фільтра новим виміром дистанції та отримання відфільтрованої відстані (мм) */
float tank_gauge_filter_distance(tank_gauge_t *gauge, float new_distance_mm);

/* Розрахунок поточної висоти рідини від дна (мм) */
float tank_gauge_calc_level_height_mm(const tank_gauge_t *gauge, float filtered_distance_mm);

/* Кусочно-лінійна інтерполяція висоти стовпа рідини в об'єм (літри) */
float tank_gauge_height_to_volume(const tank_gauge_t *gauge, float height_mm);

/* Отримання залишку рідини у відсотках (0..100%) */
float tank_gauge_volume_to_percent(const tank_gauge_t *gauge, float volume_liters);

/* Серіалізація/валідація EEPROM конфігурації */
uint16_t tank_gauge_calc_crc16(const uint8_t *data, size_t length);
bool tank_gauge_validate_config(const tank_gauge_eeprom_config_t *cfg);

#ifdef __cplusplus
}
#endif

#endif /* TANK_GAUGE_H */

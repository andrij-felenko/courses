#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

typedef struct {
    double lat1_deg;     /* Стартова широта (-87.5) */
    double lat2_deg;     /* Кінцева широта (+87.5) */
    double dlat_deg;     /* Крок сітки за широтою (2.5) */
    double lon1_deg;     /* Стартова довгота (-180.0) */
    double lon2_deg;     /* Кінцева довгота (+180.0) */
    double dlon_deg;     /* Крок сітки за довготою (5.0) */
    double height_km;    /* Висота іоносферної оболонки (350.0 км) */
    int32_t exponent;    /* Масштабний експоненційний множник (зазвичай -1) */
} ionex_header_t;

typedef struct {
    uint32_t epoch_seconds;   /* Час епохи карти (Unix timestamp) */
    int16_t* grid_data_raw;   /* Одновимірний масив розміру (n_lat * n_lon) */
    size_t   n_lat;
    size_t   n_lon;
} ionex_map_t;

/**
 * Отримує фізичне значення VTEC у TECU для заданого індексу сітки.
 */
static inline double ionex_get_vtec_tecu(const ionex_map_t* map, int32_t exp_val, size_t i_lat, size_t i_lon) {
    if (i_lat >= map->n_lat || i_lon >= map->n_lon) return 0.0;
    size_t idx = i_lat * map->n_lon + i_lon;
    return (double)map->grid_data_raw[idx] * pow(10.0, exp_val);
}

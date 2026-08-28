#pragma once
#include <stdint.h>

// MAVLink message #133: TERRAIN_REQUEST
typedef struct __mavlink_terrain_request_t {
    uint64_t mask;         // Бітова маска необхідних блоків (8х8)
    int32_t  lat;          // Широта центру кластера (град * 1e7)
    int32_t  lon;          // Довгота центру кластера (град * 1e7)
    uint16_t grid_spacing; // Крок сітки між вузлами в метрах
} mavlink_terrain_request_t;

// MAVLink message #134: TERRAIN_DATA
typedef struct __mavlink_terrain_data_t {
    int32_t  lat;          // Широта SW кута блоку (град * 1e7)
    int32_t  lon;          // Довгота SW кута блоку (град * 1e7)
    uint16_t grid_spacing; // Крок сітки в метрах
    uint8_t  gridbit;      // Номер біта в масці кластера (0..63)
    int16_t  data[16];     // Матриця 4x4 висот AMSL у метрах
} mavlink_terrain_data_t;

// MAVLink message #135: TERRAIN_CHECK
typedef struct __mavlink_terrain_check_t {
    int32_t lat;           // Широта точки перевірки (град * 1e7)
    int32_t lon;           // Довгота точки перевірки (град * 1e7)
} mavlink_terrain_check_t;

// MAVLink message #136: TERRAIN_REPORT
typedef struct __mavlink_terrain_report_t {
    int32_t  lat;          // Поточна широта (град * 1e7)
    int32_t  lon;          // Поточна довгота (град * 1e7)
    float    terrain_height;// Висота поверхні землі AMSL (метри)
    float    current_height;// Висота апарата AGL (кліренс, метри)
    uint16_t spacing;      // Крок сітки (метри)
    uint16_t pending;      // Кількість блоків у черзі запитів
    uint16_t loaded;       // Кількість завантажених блоків
} mavlink_terrain_report_t;

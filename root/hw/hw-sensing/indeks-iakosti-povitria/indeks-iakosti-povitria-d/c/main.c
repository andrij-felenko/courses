#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

// Перелік критеріальних забруднювачів
typedef enum {
    POLLUTANT_PM25 = 0,
    POLLUTANT_PM10,
    POLLUTANT_CO,
    POLLUTANT_SO2,
    POLLUTANT_NO2,
    POLLUTANT_O3_8H,
    POLLUTANT_O3_1H,
    POLLUTANT_COUNT
} pollutant_type_t;

// Категорії якості повітря за EPA
typedef enum {
    AQI_CAT_GOOD = 0,
    AQI_CAT_MODERATE,
    AQI_CAT_USG,
    AQI_CAT_UNHEALTHY,
    AQI_CAT_VERY_UNHEALTHY,
    AQI_CAT_HAZARDOUS,
    AQI_CAT_OUT_OF_RANGE
} aqi_category_t;

// Структура порогових точок (Breakpoint)
typedef struct {
    float bp_lo;
    float bp_hi;
    int32_t i_lo;
    int32_t i_hi;
} aqi_breakpoint_t;

// Таблиці порогових точок EPA (редакція 2024 року)
static const aqi_breakpoint_t EPA_PM25_BP[] = {
    {0.0f,   9.0f,    0,  50},
    {9.1f,  35.4f,   51, 100},
    {35.5f, 55.4f,  101, 150},
    {55.5f, 125.4f, 151, 200},
    {125.5f, 225.4f, 201, 300},
    {225.5f, 325.4f, 301, 500}
};

static const aqi_breakpoint_t EPA_PM10_BP[] = {
    {0.0f,   54.0f,   0,  50},
    {55.0f, 154.0f,  51, 100},
    {155.0f, 254.0f, 101, 150},
    {255.0f, 354.0f, 151, 200},
    {355.0f, 424.0f, 201, 300},
    {425.0f, 604.0f, 301, 500}
};

static const aqi_breakpoint_t EPA_CO_BP[] = {
    {0.0f,   4.4f,    0,  50},
    {4.5f,   9.4f,   51, 100},
    {9.5f,  12.4f,  101, 150},
    {12.5f, 15.4f,  151, 200},
    {15.5f, 30.4f,  201, 300},
    {30.5f, 50.4f,  301, 500}
};

static const aqi_breakpoint_t EPA_SO2_BP[] = {
    {0.0f,   35.0f,   0,  50},
    {36.0f,  75.0f,  51, 100},
    {76.0f, 185.0f, 101, 150},
    {186.0f, 304.0f, 151, 200},
    {305.0f, 604.0f, 201, 300},
    {605.0f, 1004.0f, 301, 500}
};

static const aqi_breakpoint_t EPA_NO2_BP[] = {
    {0.0f,    53.0f,   0,  50},
    {54.0f,  100.0f,  51, 100},
    {101.0f, 360.0f, 101, 150},
    {361.0f, 649.0f, 151, 200},
    {650.0f, 1249.0f, 201, 300},
    {1250.0f, 2049.0f, 301, 500}
};

static const aqi_breakpoint_t EPA_O3_8H_BP[] = {
    {0.0f,   54.0f,   0,  50},
    {55.0f,  70.0f,  51, 100},
    {71.0f,  85.0f, 101, 150},
    {86.0f, 105.0f, 151, 200},
    {106.0f, 200.0f, 201, 300}
};

static const aqi_breakpoint_t EPA_O3_1H_BP[] = {
    {125.0f, 164.0f, 101, 150},
    {165.0f, 204.0f, 151, 200},
    {205.0f, 404.0f, 201, 300},
    {405.0f, 604.0f, 301, 500}
};

// Гігроскопічна поправка для оптичних давачів пилу за відносною вологістю
float aqi_compensate_pm_humidity(float raw_pm, float rh_pct, float kappa) {
    if (rh_pct <= 0.0f) return raw_pm;
    if (rh_pct >= 99.0f) rh_pct = 99.0f; // Захист від сингулярності 100%
    float growth_factor = 1.0f + kappa * (rh_pct / (100.0f - rh_pct));
    return raw_pm / growth_factor;
}

// Декупелювання перехресної чутливості O3/NO2 для електрохімічних комірок
void aqi_compensate_cross_sensitivity(float raw_o3, float raw_no2, float k_no2_to_o3,
                                     float *out_o3, float *out_no2) {
    *out_no2 = raw_no2;
    float corrected_o3 = raw_o3 - k_no2_to_o3 * raw_no2;
    *out_o3 = corrected_o3 > 0.0f ? corrected_o3 : 0.0f;
}

// Усічення вхідної концентрації за специфікацією EPA
float aqi_truncate_concentration(pollutant_type_t pollutant, float conc) {
    if (conc < 0.0f) return 0.0f;
    switch (pollutant) {
        case POLLUTANT_PM25:
        case POLLUTANT_CO:
            return floorf(conc * 10.0f) / 10.0f; // 1 десятковий знак
        case POLLUTANT_PM10:
        case POLLUTANT_SO2:
        case POLLUTANT_NO2:
        case POLLUTANT_O3_8H:
        case POLLUTANT_O3_1H:
            return floorf(conc);                 // Ціле число
        default:
            return conc;
    }
}

// Обчислення суб-індексу для конкретного забруднювача
int32_t aqi_calc_subindex(pollutant_type_t pollutant, float conc, bool *out_valid) {
    const aqi_breakpoint_t *table = NULL;
    size_t rows = 0;

    switch (pollutant) {
        case POLLUTANT_PM25:  table = EPA_PM25_BP;  rows = sizeof(EPA_PM25_BP)/sizeof(EPA_PM25_BP[0]); break;
        case POLLUTANT_PM10:  table = EPA_PM10_BP;  rows = sizeof(EPA_PM10_BP)/sizeof(EPA_PM10_BP[0]); break;
        case POLLUTANT_CO:    table = EPA_CO_BP;    rows = sizeof(EPA_CO_BP)/sizeof(EPA_CO_BP[0]); break;
        case POLLUTANT_SO2:   table = EPA_SO2_BP;   rows = sizeof(EPA_SO2_BP)/sizeof(EPA_SO2_BP[0]); break;
        case POLLUTANT_NO2:   table = EPA_NO2_BP;   rows = sizeof(EPA_NO2_BP)/sizeof(EPA_NO2_BP[0]); break;
        case POLLUTANT_O3_8H: table = EPA_O3_8H_BP; rows = sizeof(EPA_O3_8H_BP)/sizeof(EPA_O3_8H_BP[0]); break;
        case POLLUTANT_O3_1H: table = EPA_O3_1H_BP; rows = sizeof(EPA_O3_1H_BP)/sizeof(EPA_O3_1H_BP[0]); break;
        default: *out_valid = false; return -1;
    }

    float c = aqi_truncate_concentration(pollutant, conc);

    // Перевірка нижньої межі
    if (c < table[0].bp_lo) {
        *out_valid = true;
        return 0;
    }

    // Пошук діапазону в таблиці
    for (size_t i = 0; i < rows; ++i) {
        if (c >= table[i].bp_lo && c <= table[i].bp_hi) {
            float slope = (float)(table[i].i_hi - table[i].i_lo) / (table[i].bp_hi - table[i].bp_lo);
            float raw_index = slope * (c - table[i].bp_lo) + (float)table[i].i_lo;
            *out_valid = true;
            return (int32_t)lroundf(raw_index); // Округлення до найближчого цілого
        }
    }

    // Якщо значення перевищує діапазон таблиці
    *out_valid = false;
    return -1;
}

// Структура вихідного результату мультисенсорної агрегації AQI
typedef struct {
    int32_t aqi_value;
    aqi_category_t category;
    pollutant_type_t dominant_pollutant;
    const char *dominant_name;
    const char *category_name;
    int32_t sub_indices[POLLUTANT_COUNT];
    bool sub_valid[POLLUTANT_COUNT];
} aqi_result_t;

// Назви забруднювачів
static const char *POLLUTANT_NAMES[] = {
    "PM2.5", "PM10", "CO", "SO2", "NO2", "O3 (8h)", "O3 (1h)"
};

// Назви категорій AQI
static const char *CATEGORY_NAMES[] = {
    "Добре (Good)",
    "Помірне (Moderate)",
    "Шкідливе для чутливих (USG)",
    "Шкідливе (Unhealthy)",
    "Дуже шкідливе (Very Unhealthy)",
    "Небезпечне (Hazardous)",
    "Поза шкалою (Out of Range)"
};

// Підсумковий розрахунок AQI методом максимізації
aqi_result_t aqi_calculate_overall(const float concentrations[POLLUTANT_COUNT],
                                  const bool has_sensor[POLLUTANT_COUNT]) {
    aqi_result_t res;
    memset(&res, 0, sizeof(res));
    res.aqi_value = -1;
    res.category = AQI_CAT_OUT_OF_RANGE;
    res.dominant_pollutant = POLLUTANT_PM25;
    res.dominant_name = "Невідомо";
    res.category_name = CATEGORY_NAMES[AQI_CAT_OUT_OF_RANGE];

    int32_t max_aqi = -1;
    pollutant_type_t dominant = POLLUTANT_PM25;

    for (int i = 0; i < POLLUTANT_COUNT; ++i) {
        if (!has_sensor[i]) {
            res.sub_valid[i] = false;
            res.sub_indices[i] = -1;
            continue;
        }

        bool valid = false;
        int32_t idx = aqi_calc_subindex((pollutant_type_t)i, concentrations[i], &valid);
        res.sub_indices[i] = idx;
        res.sub_valid[i] = valid;

        if (valid && idx > max_aqi) {
            max_aqi = idx;
            dominant = (pollutant_type_t)i;
        }
    }

    if (max_aqi >= 0) {
        res.aqi_value = max_aqi;
        res.dominant_pollutant = dominant;
        res.dominant_name = POLLUTANT_NAMES[dominant];

        if (max_aqi <= 50) res.category = AQI_CAT_GOOD;
        else if (max_aqi <= 100) res.category = AQI_CAT_MODERATE;
        else if (max_aqi <= 150) res.category = AQI_CAT_USG;
        else if (max_aqi <= 200) res.category = AQI_CAT_UNHEALTHY;
        else if (max_aqi <= 300) res.category = AQI_CAT_VERY_UNHEALTHY;
        else res.category = AQI_CAT_HAZARDOUS;

        res.category_name = CATEGORY_NAMES[res.category];
    }

    return res;
}

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CAL_MAGIC_WORD       0x54524143U /* "TRAC" */
#define CAL_MAX_PIECEWISE    4

/* Метрологічний паспорт калібрування в енергонезалежній пам'яті */
typedef struct {
    uint32_t magic;
    uint32_t cal_timestamp;      /* Час калібрування (UNIX epoch) */
    uint32_t interval_seconds;    /* Інтервал дійсності повірки */
    float    temp_cal_celsius;    /* Температура при калібруванні (°C) */
    float    gain_slope;          /* Калібрувальний нахил (S) */
    float    offset_zero;         /* Зсув нуля (U0, Вольти) */
    float    u_std_volts;         /* Стандартна невизначеність еталона (1-сигма, В) */
    float    tc_ppm_celsius;      /* Температурний коефіцієнт (ppm/°C) */
    float    drift_ppm_year;      /* Швидкість старіння (ppm/рік) */
    uint32_t crc32;               /* Контрольна сума структури */
} MetrologyProfile;

/* Результат вимірювання з метрологічною метрологічною оцінкою */
typedef struct {
    double value_corrected;       /* Справжнє значення у фізичних одиницях (В) */
    double expanded_uncertainty;  /* Розширена невизначеність U (k=2, В) */
    bool   is_valid;              /* Чи дійсне калібрування */
    bool   is_expired;            /* Чи не сплив термін повірки */
} MetrologyReading;

/* Простий генератор CRC32 для валідації EEPROM */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

/* Перевірка цілісності даних калібрування */
bool metrology_is_profile_valid(const MetrologyProfile *prof) {
    if (prof == NULL || prof->magic != CAL_MAGIC_WORD) {
        return false;
    }
    uint32_t stored_crc = prof->crc32;
    uint32_t calc_crc = calculate_crc32((const uint8_t *)prof, 
                                        sizeof(MetrologyProfile) - sizeof(uint32_t));
    return (stored_crc == calc_crc);
}

/* Обробка сирого сигналу АЦП з розрахунком сумарної невизначеності */
MetrologyReading metrology_process_sample(const MetrologyProfile *prof,
                                         float raw_volts,
                                         float current_temp_celsius,
                                         uint32_t current_timestamp) {
    MetrologyReading out = {0};
    
    if (!metrology_is_profile_valid(prof)) {
        out.is_valid = false;
        out.value_corrected = (double)raw_volts;
        out.expanded_uncertainty = 0.0;
        return out;
    }
    
    out.is_valid = true;
    
    /* 1. Перевірка терміну дійсності повірки */
    uint32_t elapsed_seconds = 0;
    if (current_timestamp >= prof->cal_timestamp) {
        elapsed_seconds = current_timestamp - prof->cal_timestamp;
    }
    out.is_expired = (elapsed_seconds > prof->interval_seconds);

    /* 2. Корекція систематичної похибки (зворотне перетворення: Y = (X - U0) * S) */
    double corrected = ((double)raw_volts - (double)prof->offset_zero) * (double)prof->gain_slope;
    out.value_corrected = corrected;

    /* 3. Оцінка складових бюджету невизначеності */
    
    /* а) Невизначеність еталона калібрування */
    double u_std = (double)prof->u_std_volts;

    /* б) Невизначеність від часового старіння (дрейф) */
    double years_elapsed = (double)elapsed_seconds / (365.25 * 86400.0);
    double aging_ppm = (double)prof->drift_ppm_year * years_elapsed;
    double u_aging = fabs(corrected) * (aging_ppm * 1e-6);

    /* в) Температурна невизначеність (прямокутний розподіл у межах градієнта) */
    double delta_t = fabs((double)current_temp_celsius - (double)prof->temp_cal_celsius);
    double temp_ppm = (double)prof->tc_ppm_celsius * delta_t;
    double u_temp = (fabs(corrected) * (temp_ppm * 1e-6)) / sqrt(3.0);

    /* г) Власний шум квантування та шум АЦП (припускаємо 1.5 розряду білого шуму) */
    double u_noise = 2.0e-5; /* 20 мкВ для 16-бітної шкали */

    /* 4. Сумарна стандартна невизначеність (RSS) */
    double u_combined = sqrt(u_std * u_std + 
                             u_aging * u_aging + 
                             u_temp * u_temp + 
                             u_noise * u_noise);

    /* 5. Розширена невизначеність для довірчого рівня 95.45% (k = 2.0) */
    const double coverage_factor_k = 2.0;
    out.expanded_uncertainty = u_combined * coverage_factor_k;

    return out;
}

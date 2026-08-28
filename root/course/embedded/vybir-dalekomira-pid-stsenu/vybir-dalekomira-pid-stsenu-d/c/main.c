#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_SENSORS 4
#define RANGE_INVALID_MM 65535U

typedef enum {
    SENSOR_ULTRASONIC = 0,
    SENSOR_OPTICAL_TOF = 1,
    SENSOR_MMWAVE_RADAR = 2
} SensorType;

typedef struct {
    SensorType type;
    uint32_t raw_value;     /* УЗ: мкс; ToF/Радар: мм */
    uint16_t signal_quality;/* ToF: MCPS або SNR; Радар: дБ */
    uint16_t ambient_noise;  /* ToF: фоновий сонячний рахунок */
    bool hardware_ok;
} RawSensorReading;

typedef struct {
    float temperature_c;    /* Температура повітря для УЗ */
    bool outdoor_sunlight;  /* Ознака прямого сонячного світла */
} EnvironmentalContext;

typedef struct {
    uint16_t safe_distance_mm;
    float relative_velocity_mps;
    bool emergency_stop;
    uint8_t confident_sensors_count;
} FusionResult;

/* Розрахунок швидкості звуку c(T) у мм/мкс (для перерахунку з мікросекунд у мм) */
static inline float get_sound_speed_mm_per_us(float temp_c) {
    float speed_m_per_s = 331.3f + 0.606f * temp_c;
    return speed_m_per_s * 0.001f; /* мм / мкс */
}

/* Обробка та злиття вимірів */
FusionResult range_fusion_process(
    const RawSensorReading readings[MAX_SENSORS],
    uint8_t count,
    const EnvironmentalContext* env
) {
    FusionResult result = {
        .safe_distance_mm = RANGE_INVALID_MM,
        .relative_velocity_mps = 0.0f,
        .emergency_stop = false,
        .confident_sensors_count = 0
    };

    uint16_t valid_ranges[MAX_SENSORS];
    float weights[MAX_SENSORS];
    uint8_t valid_cnt = 0;

    for (uint8_t i = 0; i < count && i < MAX_SENSORS; ++i) {
        if (!readings[i].hardware_ok) continue;

        uint16_t dist_mm = RANGE_INVALID_MM;
        float weight = 0.0f;

        switch (readings[i].type) {
            case SENSOR_ULTRASONIC: {
                /* Перевірка таймауту та мінімальної сліпої зони (30 мм .. 4000 мм) */
                if (readings[i].raw_value >= 180 && readings[i].raw_value <= 24000) {
                    float v_sound = get_sound_speed_mm_per_us(env->temperature_c);
                    dist_mm = (uint16_t)((readings[i].raw_value * v_sound) * 0.5f);
                    weight = 0.70f; /* УЗ надійний на твердих площинах */
                }
                break;
            }

            case SENSOR_OPTICAL_TOF: {
                /* Якщо сонячний шум надто високий (>1500 kcps), знижуємо довіру */
                dist_mm = (uint16_t)readings[i].raw_value;
                if (dist_mm >= 20 && dist_mm <= 4000) {
                    if (env->outdoor_sunlight || readings[i].ambient_noise > 1500) {
                        weight = (readings[i].signal_quality > 500) ? 0.35f : 0.10f;
                    } else {
                        weight = 0.90f; /* У приміщенні ToF надзвичайно точний */
                    }
                }
                break;
            }

            case SENSOR_MMWAVE_RADAR: {
                dist_mm = (uint16_t)readings[i].raw_value;
                if (dist_mm >= 100 && dist_mm <= 15000) {
                    weight = 0.85f; /* Радар всепогодний і стійкий до сонця */
                }
                break;
            }
        }

        if (dist_mm != RANGE_INVALID_MM && weight > 0.0f) {
            valid_ranges[valid_cnt] = dist_mm;
            weights[valid_cnt] = weight;
            valid_cnt++;
        }
    }

    result.confident_sensors_count = valid_cnt;

    if (valid_cnt == 0) {
        /* Жоден сенсор не дав валідних даних — режим аварійної зупинки */
        result.emergency_stop = true;
        result.safe_distance_mm = 0;
        return result;
    }

    /* Консервативний вибір безпечної дистанції:
       Беремо мінімальну дистанцію серед датчиків із вагою довіри > 0.3 */
    uint16_t min_safe = RANGE_INVALID_MM;
    for (uint8_t i = 0; i < valid_cnt; ++i) {
        if (weights[i] >= 0.30f && valid_ranges[i] < min_safe) {
            min_safe = valid_ranges[i];
        }
    }

    if (min_safe == RANGE_INVALID_MM) {
        /* Якщо всі валідні показники мали низьку довіру, беремо найменший */
        min_safe = valid_ranges[0];
        for (uint8_t i = 1; i < valid_cnt; ++i) {
            if (valid_ranges[i] < min_safe) min_safe = valid_ranges[i];
        }
    }

    result.safe_distance_mm = min_safe;
    /* Аварійне спрацювання, якщо перешкода ближче 150 мм */
    result.emergency_stop = (min_safe <= 150);

    return result;
}

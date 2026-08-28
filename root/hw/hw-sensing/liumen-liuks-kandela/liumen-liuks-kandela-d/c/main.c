#include <stdint.h>
#include <stdbool.h>

typedef enum {
    LIGHT_SRC_SUNLIGHT,     /* Сонячне світло (багате на УФ та синє) */
    LIGHT_SRC_INCANDESCENT, /* Лампа розжарювання (величезний ІЧ хвіст) */
    LIGHT_SRC_FLUORESCENT,  /* Люмінесцентна лампа (піки ртуті) */
    LIGHT_SRC_LED_WHITE     /* Білий світлодіод (люмінофорний спектр) */
} LightSourceType;

typedef struct {
    uint32_t raw_visible_plus_ir; /* Канал CH0: сумарний потік */
    uint32_t raw_ir_only;         /* Канал CH1: інфрачервоний потік */
    double integration_time_ms;   /* Час накопичення заряду АЦП */
    double sensor_gain;           /* Коефіцієнт підсилення PGA */
} AlsRawReading;

/* Обчислення освітленості в люксах із відсіканням паразитних ІЧ-фотонів */
bool als_calculate_lux(const AlsRawReading *reading, LightSourceType src, double *out_lux) {
    if (!reading || !out_lux || reading->integration_time_ms <= 0.0 || reading->sensor_gain <= 0.0) {
        return false;
    }

    /* Нормалізація сирих відліків на одиничний час і підсилення */
    double norm_factor = (100.0 / reading->integration_time_ms) * (1.0 / reading->sensor_gain);
    double ch0 = (double)reading->raw_visible_plus_ir * norm_factor;
    double ch1 = (double)reading->raw_ir_only * norm_factor;

    if (ch0 < 1e-6) {
        *out_lux = 0.0;
        return true;
    }

    /* Співвідношення ІЧ/видиме визначає спектральний розподіл */
    double ir_ratio = ch1 / ch0;
    double lux = 0.0;

    /* Поліноміальна корекція спектра під криву V(lambda) */
    if (ir_ratio < 0.50) {
        /* Джерело з малим ІЧ (LED або денне світло) */
        lux = 0.0304 * ch0 - 0.0620 * ch0 * pow(ir_ratio, 1.4);
    } else if (ir_ratio < 0.80) {
        /* Люмінесцентне світло */
        lux = 0.0224 * ch0 - 0.0310 * ch1;
    } else if (ir_ratio < 1.30) {
        /* Лампа розжарювання чи пряме сонце: висока частка ІЧ */
        lux = 0.0128 * ch0 - 0.0153 * ch1;
    } else {
        /* Чисте ІЧ-випромінювання (наприклад, пульт ДК або сонце крізь шторку) */
        lux = 0.0;
    }

    *out_lux = (lux > 0.0) ? lux : 0.0;
    return true;
}

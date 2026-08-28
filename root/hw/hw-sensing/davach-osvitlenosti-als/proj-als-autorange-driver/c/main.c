#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коефіцієнти підсилення PGA аналогового тракту ALS */
typedef enum {
    ALS_GAIN_1X   = 0,
    ALS_GAIN_2X   = 1,
    ALS_GAIN_4X   = 2,
    ALS_GAIN_8X   = 3,
    ALS_GAIN_16X  = 4,
    ALS_GAIN_32X  = 5,
    ALS_GAIN_64X  = 6,
    ALS_GAIN_128X = 7
} als_gain_t;

/* Час інтегрування АЦП (кратний 100 мс для антифлікеру) */
typedef enum {
    ALS_INT_50MS  = 0,  /* Швидкий режим */
    ALS_INT_100MS = 1,  /* Антифлікер 50 Гц / 60 Гц */
    ALS_INT_200MS = 2,  /* Висока чутливість */
    ALS_INT_400MS = 3,  /* Дуже висока чутливість */
    ALS_INT_800MS = 4   /* Максимальна чутливість для темряви */
} als_int_time_t;

/* Структура конфігурації та стану драйвера */
typedef struct {
    als_gain_t gain;
    als_int_time_t int_time;
    float glass_attenuation;    /* Коефіцієнт скла: 1.0 = відкритий, 10.0 = 10% пропускання */
    uint16_t low_threshold;     /* Поріг переходу вгору (зазвичай 10% від FS = 6553) */
    uint16_t high_threshold;    /* Поріг переходу вниз (зазвичай 85% від FS = 55705) */
    bool range_changed;
} als_driver_t;

static const float GAIN_FACTORS[] = {1.0f, 2.0f, 4.0f, 8.0f, 16.0f, 32.0f, 64.0f, 128.0f};
static const float INT_TIME_FACTORS[] = {0.5f, 1.0f, 2.0f, 4.0f, 8.0f};
static const float BASE_LUX_PER_LSB = 0.096f; /* Для Gain=1x та Tint=100ms */

void als_driver_init(als_driver_t *drv, float glass_att) {
    if (!drv) return;
    drv->gain = ALS_GAIN_4X;
    drv->int_time = ALS_INT_100MS; /* 100 мс за замовчуванням для придушення 100/120 Гц */
    drv->glass_attenuation = (glass_att >= 1.0f) ? glass_att : 1.0f;
    drv->low_threshold = 6553;     /* 10% від 65535 */
    drv->high_threshold = 55705;   /* 85% від 65535 */
    drv->range_changed = true;
}

/* Автоматична адаптація шкали за поточним відліком АЦП */
bool als_auto_range_update(als_driver_t *drv, uint16_t raw_ch0, bool is_overflow) {
    if (!drv) return false;
    drv->range_changed = false;

    /* 1. Захист від насичення: негайне зниження чутливості */
    if (is_overflow || raw_ch0 > drv->high_threshold) {
        if (drv->gain > ALS_GAIN_1X) {
            drv->gain = (als_gain_t)(drv->gain - 1);
            drv->range_changed = true;
        } else if (drv->int_time > ALS_INT_50MS) {
            drv->int_time = (als_int_time_t)(drv->int_time - 1);
            drv->range_changed = true;
        }
    }
    /* 2. Збільшення чутливості при занадто слабкому сигналі */
    else if (raw_ch0 < drv->low_threshold) {
        if (drv->gain < ALS_GAIN_128X) {
            drv->gain = (als_gain_t)(drv->gain + 1);
            drv->range_changed = true;
        } else if (drv->int_time < ALS_INT_800MS) {
            drv->int_time = (als_int_time_t)(drv->int_time + 1);
            drv->range_changed = true;
        }
    }

    return drv->range_changed;
}

/* Обчислення освітленості у люксах з двоканальною компенсацією ІЧ */
float als_calculate_lux(const als_driver_t *drv, uint16_t ch0, uint16_t ch1) {
    if (!drv || ch0 == 0) return 0.0f;

    float ratio = (float)ch1 / (float)ch0;
    float a = 1.0f, b = 1.8f;

    /* Кусково-лінійна оптимізація коефіцієнтів під тип освітлення */
    if (ratio <= 0.15f) {
        a = 1.00f; b = 0.40f; /* LED / Люмінесцентне */
    } else if (ratio <= 0.45f) {
        a = 1.00f; b = 1.20f; /* Денне розсіяне світло */
    } else if (ratio <= 0.75f) {
        a = 1.00f; b = 1.75f; /* Галоген / лампи розжарювання */
    } else {
        a = 0.85f; b = 1.95f; /* Пряме сонце / потужне ІЧ */
    }

    float net_counts = a * (float)ch0 - b * (float)ch1;
    if (net_counts < 0.0f) net_counts = 0.0f;

    float gain_div = GAIN_FACTORS[drv->gain];
    float tint_div = INT_TIME_FACTORS[drv->int_time];

    /* Формула перерахунку: LSB_фактичний = LSB_базовий / (Gain * Tint) * Glass */
    float lux = (net_counts * BASE_LUX_PER_LSB / (gain_div * tint_div)) * drv->glass_attenuation;
    return lux;
}

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "tank_gauge.h"

int main(void) {
    printf("=== Контролер моніторингу об'єму резервуара (C) ===\n\n");

    tank_gauge_t gauge;
    /* Резервуар глибиною 2000 мм, повний об'єм 1000 л, вікно медіани 5 */
    tank_gauge_init(&gauge, 5, 2000.0f, 1000.0f);

    /* Нелінійна таблиця калібрування горизонтальної циліндричної цистерни */
    tank_gauge_add_calib_point(&gauge,    0.0f,    0.0f);
    tank_gauge_add_calib_point(&gauge,  200.0f,   45.0f);
    tank_gauge_add_calib_point(&gauge,  500.0f,  180.0f);
    tank_gauge_add_calib_point(&gauge, 1000.0f,  500.0f);
    tank_gauge_add_calib_point(&gauge, 1500.0f,  820.0f);
    tank_gauge_add_calib_point(&gauge, 1800.0f,  955.0f);
    tank_gauge_add_calib_point(&gauge, 2000.0f, 1000.0f);

    /* Симуляція серії вимірів за температури 25.0 °C з поодинокими завадами хвилювання */
    float temp_c = 25.0f;
    uint32_t tof_samples_us[] = {
        5760,  /* ~1000 мм дистанції (рівень 1000 мм) */
        5770,
        5755,
        2800,  /* Викид від бризок/хвилі */
        5765,
        5762,
        9200,  /* Помилковий пропуск луни */
        5758,
        5760
    };
    size_t num_samples = sizeof(tof_samples_us) / sizeof(tof_samples_us[0]);

    printf("Поточна температура повітря: %.1f °C (швидкість звуку: %.2f м/с)\n",
           temp_c, tank_gauge_sound_speed(temp_c));
    printf("--------------------------------------------------------------------------------\n");
    printf("Відлік | ToF (мкс) | Сира дист. (мм) | Фільтр. дист. (мм) | Рівень (мм) | Об'єм (л) | Відсоток\n");
    printf("--------------------------------------------------------------------------------\n");

    for (size_t i = 0; i < num_samples; i++) {
        uint32_t tof = tof_samples_us[i];
        float raw_dist = tank_gauge_calc_distance_mm(tof, temp_c);
        float filt_dist = tank_gauge_filter_distance(&gauge, raw_dist);
        float level_h = tank_gauge_calc_level_height_mm(&gauge, filt_dist);
        float volume = tank_gauge_height_to_volume(&gauge, level_h);
        float pct = tank_gauge_volume_to_percent(&gauge, volume);

        printf("  #%02zu  |   %5u   |     %7.1f     |       %7.1f      |   %7.1f   |   %5.1f   |  %5.1f%%\n",
               i + 1, tof, raw_dist, filt_dist, level_h, volume, pct);
    }

    printf("--------------------------------------------------------------------------------\n");
    printf("Висновок: медіанний фільтр повністю відсік короткі та довгі викиди хвилювання.\n");
    return 0;
}

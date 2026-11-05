#include <stdio.h>
#include "organizer_calc.h"

int main(void) {
    printf("=== Інженерний калькулятор параметрів органайзера деталей ===\n\n");

    /* 1. Розрахунок геометрії комірки для гвинтів М3х12 */
    PartSpec screw_m3 = {
        .length_mm = 14.5,
        .width_mm = 5.5,
        .height_mm = 5.5,
        .count = 100
    };

    double packing_factor = 0.58; /* Випадкове насипне пакування циліндричних тіл */
    double safety = 1.25;         /* Ергономічний запас на закривання кришки та виймання */

    CellCalculation cell = calc_cell_dimensions(&screw_m3, packing_factor, safety);

    printf("[1] Розрахунок місткості комірки (100 шт гвинтів М3х12):\n");
    printf("  Об'єм однієї деталі:           %.1f мм³\n", cell.part_volume_mm3);
    printf("  Насипний об'єм (eta=%.2f):     %.1f мм³\n", packing_factor, cell.bulk_volume_mm3);
    printf("  Необхідний об'єм (із запасом): %.1f мм³\n", cell.required_volume_mm3);
    printf("  Внутрішні розміри (ШхДхВ):     %.1f x %.1f x %.1f мм\n",
           cell.inner_width_mm, cell.inner_length_mm, cell.inner_height_mm);
    printf("  Модуль Gridfinity:             %zu x %zu (крок 42 мм)\n\n",
           cell.grid_units_x, cell.grid_units_y);

    /* 2. Оптимізація матриці для ряду резисторів E24 */
    double wall_thickness = 1.6; /* Рекомендована стінка для друку або лиття */
    MatrixLayout layout_e24 = calc_optimal_matrix(EROW_E24, cell.inner_width_mm, cell.inner_length_mm, wall_thickness);

    printf("[2] Оптимізація матриці касетного блоку під ряд E24:\n");
    printf("  Усього номіналів (комірок):    %zu\n", layout_e24.total_compartments);
    printf("  Конфігурація сітки:            %zu колонок x %zu рядків\n",
           layout_e24.columns, layout_e24.rows);
    printf("  Товщина стінок:                %.1f мм\n", layout_e24.wall_thickness_mm);
    printf("  Габаритний розмір блоку:       %.1f x %.1f мм\n\n",
           layout_e24.total_width_mm, layout_e24.total_length_mm);

    /* 3. Валідація електростатичного розсіювання заряду (ESD) за IEC 61340-5-1 */
    /* Випробовуємо струморозсіювальний пластик: опір 5.0e7 Ом/кв, ємність тіла 100 пФ */
    double r_surface = 5.0e7;
    double c_specimen = 100.0;
    double v_start = 1000.0; /* 1000 В початковий трибоелектричний заряд */
    double v_end = 100.0;    /* 100 В (10% від початкового рівня) */

    EsdCalculation esd = calc_esd_decay(r_surface, c_specimen, v_start, v_end);

    printf("[3] Верифікація антистатичного захисту за IEC 61340-5-1:\n");
    printf("  Поверхневий опір пластику:     %.1e Ом/кв\n", esd.surface_resistivity_ohm_sq);
    printf("  Спад напруги:                  %.0f В -> %.0f В\n",
           esd.initial_voltage_v, esd.target_voltage_v);
    printf("  Розрахований час стікання:     %.4f с\n", esd.decay_time_sec);
    printf("  Норматив IEC 61340-5-1:        <= 2.0000 с\n");
    printf("  Вердикт безпеки:               %s\n",
           esd.is_esd_safe ? "ВІДПОВІДАЄ СТАНДАРТУ (БЕЗПЕЧНО)" : "НЕ ВІДПОВІДАЄ (НЕБЕЗПЕКА ПРОБОЮ)");

    return 0;
}

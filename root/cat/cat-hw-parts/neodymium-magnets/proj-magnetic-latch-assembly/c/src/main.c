#include "magnet_calc.h"
#include <stdio.h>

int main(void) {
    /* Неодимовий дисковий магніт N52: D = 12 мм, товщина h = 3 мм, Br = 1.45 Тл */
    DiscMagnet magnet_n52 = {
        .grade = "NdFeB N52",
        .diameter_mm = 12.0,
        .thickness_mm = 3.0,
        .br_tesla = 1.45
    };

    /* Гніздо під вклеювання епоксидною смолою (допуск на зазор 0.2 мм на радіус) */
    PocketFit pocket = {
        .pocket_dia_mm = 12.4,
        .pocket_depth_mm = 2.8,
        .glue_gap_mm = 0.2,
        .glue_shear_strength_mpa = 14.0 /* Двокомпонентний епоксидний склад */
    };

    /* Геометрія кришки приладового корпусу з магнітним замком */
    CoverLatchConfig latch = {
        .magnet_arm_mm = 180.0,  /* Магніт розташовано біля замкового краю */
        .handle_arm_mm = 200.0,  /* Ручка відкривання трохи далі за магніт */
        .friction_coeff = 0.20   /* Коефіцієнт тертя полірованого нікелю по сталі */
    };

    /* Товщина захисного шару фарби / технологічний повітряний зазор 0.1 мм */
    double air_gap_mm = 0.1;

    LatchReport report;
    if (!evaluate_magnet_latch(&magnet_n52, &pocket, &latch, air_gap_mm, &report)) {
        fprintf(stderr, "Помилка обчислення параметрів магнітного вузла!\n");
        return 1;
    }

    printf("===============================================================\n");
    printf("   Розрахунок магнітного фіксатора кришки: %s\n", magnet_n52.grade);
    printf("===============================================================\n");
    printf("1. Параметри магнітного поля та геометрії:\n");
    printf("   - Діаметр / товщина: %.1f мм / %.1f мм\n", magnet_n52.diameter_mm, magnet_n52.thickness_mm);
    printf("   - Робочий повітряний зазор: %.2f мм\n", air_gap_mm);
    printf("   - Магнітна індукція на полюсі: %.3f Тл\n", report.b_surface_tesla);
    printf("   - Робоча площа полюса: %.1f мм²\n", report.pole_area_mm2);
    printf("\n2. Зусилля утримання та відкривання:\n");
    printf("   - Нормальна сила відриву (Максвелл): %.1f Н (≈ %.2f кгс)\n",
           report.pull_force_n, report.pull_force_n / 9.80665);
    printf("   - Сила зсуву при ковзанні: %.1f Н\n", report.shear_force_n);
    printf("   - Необхідне зусилля руки на ручці: %.1f Н\n", report.opening_force_n);
    printf("\n3. Перевірка міцності клейового шва:\n");
    printf("   - Загальна площа склеювання: %.1f мм²\n", report.glue_area_mm2);
    printf("   - Розрахункове напруження зсуву: %.2f МПа\n", report.glue_shear_stress_mpa);
    printf("   - Допустиме напруження клею: %.1f МПа\n", pocket.glue_shear_strength_mpa);
    printf("   - Коефіцієнт запасу міцності: %.1f (норма >= 2.0)\n", report.safety_factor);
    printf("   - Вердикт надійності посадки: %s\n",
           report.is_glue_safe ? "СХВАЛЕНО (клей тримає надійно)" : "НЕБЕЗПЕКА (магніт вирве з гнізда)");
    printf("===============================================================\n");

    return report.is_glue_safe ? 0 : 2;
}

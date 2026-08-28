#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define COPPER_RHO_20 1.724e-8  /* Питомий опір міді за 20 °C, Ом * м */
#define COPPER_ALPHA  0.00393   /* Температурний коефіцієнт опору, 1 / K */

typedef struct {
    double awg;
    double cross_section_mm2;
    double length_m;
    double current_a;
    double ambient_temp_c;
    double contact_resistance_mohm;
    int    loaded_wires_count;
    double logic_v_il_max;      /* Максимальний поріг логічного нуля приймача (V) */
    double logic_v_ol_max;      /* Максимальний вихідний нуль передавача (V) */
    double harness_outer_dia_mm;
} HarnessSpec;

typedef struct {
    double wire_resistance_ohm;
    double total_loop_drop_v;
    double ground_shift_v;
    double actual_v_il_at_receiver;
    double noise_margin_v;
    bool   logic_level_safe;
    double bundle_derating_factor;
    double min_bend_radius_static_mm;
    double min_bend_radius_dynamic_mm;
} HarnessResult;

bool calculate_harness(const HarnessSpec *spec, HarnessResult *res) {
    if (!spec || !res || spec->cross_section_mm2 <= 0.0 || spec->length_m <= 0.0) {
        return false;
    }

    double area_m2 = spec->cross_section_mm2 * 1e-6;
    double r_20 = (COPPER_RHO_20 * spec->length_m) / area_m2;
    double delta_t = spec->ambient_temp_c - 20.0;
    double r_wire = r_20 * (1.0 + COPPER_ALPHA * delta_t);
    double r_contact = (spec->contact_resistance_mohm * 1e-3);

    res->wire_resistance_ohm = r_wire;

    /* Повне падіння: 2 жили (плюс і земля) + 2 контакти роз'ємів */
    res->total_loop_drop_v = spec->current_a * (2.0 * r_wire + 2.0 * r_contact);

    /* Зсув землі на віддаленому вузлі: падіння на зворотній жилі та контакті */
    res->ground_shift_v = spec->current_a * (r_wire + r_contact);

    /* Рівень нуля на вході головного приймача */
    res->actual_v_il_at_receiver = spec->logic_v_ol_max + res->ground_shift_v;
    res->noise_margin_v = spec->logic_v_il_max - res->actual_v_il_at_receiver;
    res->logic_level_safe = (res->noise_margin_v >= 0.15); /* Запас не менше 150 мВ */

    /* Делейтинг у пучку за MIL-W-5088L */
    if (spec->loaded_wires_count <= 1) {
        res->bundle_derating_factor = 1.0;
    } else if (spec->loaded_wires_count == 2) {
        res->bundle_derating_factor = 0.88;
    } else {
        double k = 1.0 / sqrt((double)spec->loaded_wires_count);
        res->bundle_derating_factor = (k < 0.40) ? 0.40 : k;
    }

    /* Радіуси вигину */
    res->min_bend_radius_static_mm = 6.0 * spec->harness_outer_dia_mm;
    res->min_bend_radius_dynamic_mm = 12.0 * spec->harness_outer_dia_mm;

    return true;
}

int main(void) {
    HarnessSpec spec = {
        .awg = 24.0,
        .cross_section_mm2 = 0.205,      /* 24 AWG */
        .length_m = 1.8,                 /* 1.8 метра */
        .current_a = 1.5,                /* 1.5 А піковий струм вузла */
        .ambient_temp_c = 50.0,          /* Температура всередині корпусу */
        .contact_resistance_mohm = 15.0, /* 2 контакти Micro-Fit */
        .loaded_wires_count = 6,         /* 6 навантажених жил у пучку */
        .logic_v_il_max = 0.80,          /* Поріг логічного нуля 3.3V CMOS */
        .logic_v_ol_max = 0.20,          /* Вихідний нуль передавача */
        .harness_outer_dia_mm = 7.5      /* Зовнішній діаметр джгута */
    };

    HarnessResult res;
    if (!calculate_harness(&spec, &res)) {
        fprintf(stderr, "Помилка вхідних параметрів джгута.\n");
        return EXIT_FAILURE;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ КАБЕЛЬНОГО ДЖГУТА (C) ===\n");
    printf("Опір однієї жили за %0.1f °C:   %0.4f Ом\n", spec.ambient_temp_c, res.wire_resistance_ohm);
    printf("Сумарне падіння в петлі (±V):   %0.3f В\n", res.total_loop_drop_v);
    printf("Перекіс потенціалу землі (GND):  %0.3f В\n", res.ground_shift_v);
    printf("Рівень логічного нуля на вході: %0.3f В (поріг: %0.2f В)\n",
           res.actual_v_il_at_receiver, spec.logic_v_il_max);
    printf("Запас завадостійкості:           %0.3f В [%s]\n",
           res.noise_margin_v, res.logic_level_safe ? "БЕЗПЕЧНО" : "НЕБЕЗПЕЧНИЙ ЗБІЙ");
    printf("Коефіцієнт струму в пучку (K):   %0.2f (струм зменшити до %0.1f%%)\n",
           res.bundle_derating_factor, res.bundle_derating_factor * 100.0);
    printf("Мін. радіус вигину (статика):    %0.1f мм\n", res.min_bend_radius_static_mm);
    printf("Мін. радіус вигину (динаміка):   %0.1f мм\n", res.min_bend_radius_dynamic_mm);

    return EXIT_SUCCESS;
}

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846

/* Фізичні та технологічні константи */
#define DENSITY_PETG_G_CM3      1.27
#define DENSITY_ABS_G_CM3       1.05
#define DENSITY_PA12_G_CM3      1.01
#define DENSITY_AL6061_G_CM3    2.70

#define COST_FILAMENT_KG_USD    24.0
#define COST_MJF_PA12_CM3_USD   0.35
#define COST_AL6061_KG_USD      8.50
#define COST_ABS_GRANULE_KG_USD 3.20

#define RATE_FDM_HOUR_USD       4.50
#define RATE_CNC_HOUR_USD       55.0
#define RATE_LABOR_HOUR_USD     25.0
#define RATE_IM_MACHINE_HOUR    45.0

typedef enum {
    TECH_FDM_3D_PRINT = 0,
    TECH_MJF_PA12_PRINT,
    TECH_CNC_ALUMINUM,
    TECH_OFF_SHELF_MODIFIED,
    TECH_INJECTION_MOLDING,
    TECH_COUNT
} TechType;

static const char *TECH_NAMES[TECH_COUNT] = {
    "3D-друк FDM (PETG/ABS)",
    "3D-друк MJF (PA12 Nylon)",
    "ЧПУ фрезерування (Al 6061-T6)",
    "Готовий корпус з доробкою",
    "Лиття під тиском (Injection)"
};

typedef struct {
    double length_mm;
    double width_mm;
    double height_mm;
    double wall_thickness_mm;
    int num_cutouts;
    int num_threaded_inserts;
    int num_side_sliders;
    double thermal_dissipation_watts;
    bool require_ip67;
} EnclosureSpecs;

typedef struct {
    double nre_cost_usd;
    double setup_cost_usd;
    double unit_raw_cost_usd;
    double unit_machine_cost_usd;
    double unit_post_cost_usd;
    double unit_labor_cost_usd;
    bool technically_feasible;
    char feasibility_note[128];
} TechCostBreakdown;

/* Розрахунок площі зовнішньої поверхні (см2) та об'єму матеріалу стінок (см3) */
static void calc_geometry(const EnclosureSpecs *sp, double *out_surface_cm2, double *out_volume_net_cm3) {
    double l_cm = sp->length_mm / 10.0;
    double w_cm = sp->width_mm / 10.0;
    double h_cm = sp->height_mm / 10.0;
    double t_cm = sp->wall_thickness_mm / 10.0;

    double s_ext = 2.0 * (l_cm * w_cm + l_cm * h_cm + w_cm * h_cm);
    double v_ext = l_cm * w_cm * h_cm;
    double v_int = (l_cm - 2.0 * t_cm) * (w_cm - 2.0 * t_cm) * (h_cm - 2.0 * t_cm);
    if (v_int < 0.0) v_int = 0.0;

    double v_net = v_ext - v_int;
    *out_surface_cm2 = s_ext;
    *out_volume_net_cm3 = v_net;
}

/* 1. Модель FDM 3D-друку */
static TechCostBreakdown eval_fdm(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    double mass_g = v_net_cm3 * DENSITY_PETG_G_CM3;
    b.unit_raw_cost_usd = (mass_g / 1000.0) * COST_FILAMENT_KG_USD;

    /* Об'ємна швидкість друку 12 см3/год */
    double print_hours = v_net_cm3 / 12.0;
    if (print_hours < 0.5) print_hours = 0.5;
    b.unit_machine_cost_usd = print_hours * RATE_FDM_HOUR_USD;

    /* Латунні вставки та зняття підтримок */
    b.unit_post_cost_usd = sp->num_threaded_inserts * 0.25;
    double labor_hours = 0.10 + (sp->num_threaded_inserts * 0.02);
    b.unit_labor_cost_usd = labor_hours * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 0.0;
    b.setup_cost_usd = 10.0;

    if (sp->thermal_dissipation_watts > 8.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Тепловідвід %.1f Вт перевищує ліміт пластику FDM (макс 8 Вт)",
                 sp->thermal_dissipation_watts);
    } else if (sp->require_ip67) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Мікропористість FDM шарів не гарантує герметичність IP67");
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note), "OK для макетів та прототипів");
    }
    return b;
}

/* 2. Модель MJF PA12 3D-друку */
static TechCostBreakdown eval_mjf(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    b.unit_raw_cost_usd = v_net_cm3 * COST_MJF_PA12_CM3_USD;
    b.unit_machine_cost_usd = 5.0; /* Амортизація камери за деталь */
    b.unit_post_cost_usd = (sp->require_ip67 ? 6.50 : 2.00) + sp->num_threaded_inserts * 0.25;
    b.unit_labor_cost_usd = 0.08 * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 0.0;
    b.setup_cost_usd = 35.0;

    if (sp->thermal_dissipation_watts > 12.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Поліамід PA12 не забезпечує розсіювання %.1f Вт",
                 sp->thermal_dissipation_watts);
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 sp->require_ip67 ? "Вимагає парового згладжування (Vapor Polish)" : "OK для серійних корпусів");
    }
    return b;
}

/* 3. Модель ЧПУ-фрезерування (Алюміній 6061-T6) */
static TechCostBreakdown eval_cnc(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    double stock_l_cm = (sp->length_mm + 10.0) / 10.0;
    double stock_w_cm = (sp->width_mm + 10.0) / 10.0;
    double stock_h_cm = (sp->height_mm + 6.0) / 10.0;
    double v_stock_cm3 = stock_l_cm * stock_w_cm * stock_h_cm;
    double mass_stock_kg = (v_stock_cm3 * DENSITY_AL6061_G_CM3) / 1000.0;

    b.unit_raw_cost_usd = mass_stock_kg * COST_AL6061_KG_USD;

    double v_removed_cm3 = v_stock_cm3 - v_net_cm3;
    double mrr_cm3_min = 75.0; /* Швидкість вибірки Al 6061 */
    double t_rough_min = v_removed_cm3 / mrr_cm3_min;
    double t_finish_min = s_cm2 * 0.05;
    double t_holes_min = (sp->num_cutouts * 2.5) + (sp->num_threaded_inserts * 1.0);
    double t_total_min = t_rough_min + t_finish_min + t_holes_min + 8.0;

    b.unit_machine_cost_usd = (t_total_min / 60.0) * RATE_CNC_HOUR_USD;
    /* Анодування Type II + піскоструй: $0.20 за дм2 */
    double area_dm2 = s_cm2 / 100.0;
    b.unit_post_cost_usd = area_dm2 * 0.20 * 100.0;
    if (b.unit_post_cost_usd < 4.0) b.unit_post_cost_usd = 4.0;
    b.unit_labor_cost_usd = 0.10 * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 180.0; /* CAM програмування та нульові точки */
    b.setup_cost_usd = 60.0;

    snprintf(b.feasibility_note, sizeof(b.feasibility_note),
             "Ідеальне тепловідведення (167 Вт/(м·К)) та повне ЕМС екранування");
    return b;
}

/* 4. Модель готового корпусу з доробкою (Gainta / Hammond) */
static TechCostBreakdown eval_off_shelf(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    /* Оцінка вартості стандартного боксу від габаритів */
    double volume_liters = (sp->length_mm * sp->width_mm * sp->height_mm) / 1e6;
    double base_catalog_cost = 6.0 + (volume_liters * 18.0);
    if (sp->require_ip67) base_catalog_cost += 4.50;

    b.unit_raw_cost_usd = base_catalog_cost;

    /* Фрезерування вирізів у кришці/панелях */
    double t_mod_min = (sp->num_cutouts * 1.5) + 3.0;
    b.unit_machine_cost_usd = (t_mod_min / 60.0) * RATE_CNC_HOUR_USD;
    b.unit_post_cost_usd = 1.50; /* Лазерне маркування портів */
    b.unit_labor_cost_usd = 0.05 * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 50.0;
    b.setup_cost_usd = 25.0;

    if (sp->thermal_dissipation_watts > 25.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Стандартний бокс вимагає зовнішнього радіатора для %.1f Вт",
                 sp->thermal_dissipation_watts);
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Оптимальний баланс ціни та швидкості запуску для малих серій");
    }
    return b;
}

/* 5. Модель лиття під тиском (Injection Molding) */
static TechCostBreakdown eval_injection_molding(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    double mass_g = v_net_cm3 * DENSITY_ABS_G_CM3;
    b.unit_raw_cost_usd = (mass_g / 1000.0) * COST_ABS_GRANULE_KG_USD * 1.15; /* +15% ливники */

    /* Цикл лиття залежно від товщини стінки */
    double cycle_sec = 12.0 + (sp->wall_thickness_mm * sp->wall_thickness_mm * 2.5);
    b.unit_machine_cost_usd = (cycle_sec / 3600.0) * RATE_IM_MACHINE_HOUR;
    b.unit_post_cost_usd = sp->num_threaded_inserts * 0.15;
    b.unit_labor_cost_usd = (cycle_sec / 3600.0) * RATE_LABOR_HOUR_USD * 0.3;

    /* Вартість прес-форми */
    double base_mold = 10000.0 + (s_cm2 * 12.0);
    if (sp->num_side_sliders > 0) {
        base_mold += sp->num_side_sliders * 2200.0;
    }
    b.nre_cost_usd = base_mold;
    b.setup_cost_usd = 250.0;

    if (sp->thermal_dissipation_watts > 10.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Лиття пластику не відведе %.1f Вт без внутрішніх металевих тепловідводів",
                 sp->thermal_dissipation_watts);
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Мінімальна ціна деталі для великих серій (>2 000 шт)");
    }
    return b;
}

static double calc_unit_tco(const TechCostBreakdown *b, int batch_size) {
    if (batch_size <= 0) return 0.0;
    double nre_share = b->nre_cost_usd / (double)batch_size;
    double setup_share = b->setup_cost_usd / (double)batch_size;
    double per_unit = b->unit_raw_cost_usd + b->unit_machine_cost_usd +
                      b->unit_post_cost_usd + b->unit_labor_cost_usd;
    return nre_share + setup_share + per_unit;
}

int main(int argc, char **argv) {
    EnclosureSpecs sp = {
        .length_mm = 120.0,
        .width_mm = 80.0,
        .height_mm = 35.0,
        .wall_thickness_mm = 2.5,
        .num_cutouts = 4,
        .num_threaded_inserts = 4,
        .num_side_sliders = 1,
        .thermal_dissipation_watts = 5.0,
        .require_ip67 = true
    };

    printf("================================================================================\n");
    printf("     АНАЛІЗАТОР СОБІВАРТОСТІ ТА ВИБОРУ ТЕХНОЛОГІЇ ВИГОТОВЛЕННЯ КОРПУСУ\n");
    printf("================================================================================\n");
    printf("Параметри корпусу: %.1f x %.1f x %.1f мм, стінка %.1f мм\n",
           sp.length_mm, sp.width_mm, sp.height_mm, sp.wall_thickness_mm);
    printf("Вимоги: Вирізів: %d, Вставок: %d, Тепло: %.1f Вт, IP67: %s\n\n",
           sp.num_cutouts, sp.num_threaded_inserts, sp.thermal_dissipation_watts,
           sp.require_ip67 ? "ТАК" : "НІ");

    TechCostBreakdown breaks[TECH_COUNT];
    breaks[TECH_FDM_3D_PRINT]       = eval_fdm(&sp);
    breaks[TECH_MJF_PA12_PRINT]     = eval_mjf(&sp);
    breaks[TECH_CNC_ALUMINUM]       = eval_cnc(&sp);
    breaks[TECH_OFF_SHELF_MODIFIED] = eval_off_shelf(&sp);
    breaks[TECH_INJECTION_MOLDING]  = eval_injection_molding(&sp);

    /* Друк структури витрат */
    printf("--------------------------------------------------------------------------------\n");
    printf("%-30s | %-8s | %-8s | %-8s | %-8s\n", "Технологічний процес", "NRE ($)", "Raw ($)", "Mach ($)", "Feasible?");
    printf("--------------------------------------------------------------------------------\n");
    for (int i = 0; i < TECH_COUNT; ++i) {
        printf("%-30s | %8.1f | %8.2f | %8.2f | %-8s\n",
               TECH_NAMES[i],
               breaks[i].nre_cost_usd,
               breaks[i].unit_raw_cost_usd,
               breaks[i].unit_machine_cost_usd,
               breaks[i].technically_feasible ? "ТАК" : "НІ");
    }
    printf("--------------------------------------------------------------------------------\n\n");

    /* Аналіз собівартості залежно від тиражу партії */
    int batches[] = { 1, 10, 50, 100, 500, 1000, 5000, 20000 };
    int n_batches = sizeof(batches) / sizeof(batches[0]);

    printf("ПОРІВНЯЛЬНА ТАБЛИЦЯ ПИТОМОЇ СОБІВАРТОСТІ 1 КОРПУСУ (USD / шт):\n");
    printf("--------------------------------------------------------------------------------\n");
    printf("%-26s", "Тираж партії (шт):");
    for (int b = 0; b < n_batches; ++b) {
        printf(" | %6d", batches[b]);
    }
    printf("\n--------------------------------------------------------------------------------\n");

    for (int i = 0; i < TECH_COUNT; ++i) {
        printf("%-26s", TECH_NAMES[i]);
        for (int b = 0; b < n_batches; ++b) {
            double cost = calc_unit_tco(&breaks[i], batches[b]);
            if (!breaks[i].technically_feasible) {
                printf(" |   N/A ");
            } else if (cost > 999.0) {
                printf(" | >$999 ");
            } else {
                printf(" | %6.2f", cost);
            }
        }
        printf("\n");
    }
    printf("--------------------------------------------------------------------------------\n\n");

    /* Визначення оптимальної технології для кожного тиражу */
    printf("РЕКОМЕНДАЦІЇ ТЕХНОЛОГІЧНОГО МАРШРУТУ ЗА РОЗМІРОМ ПАРТІЇ:\n");
    for (int b = 0; b < n_batches; ++b) {
        int best_tech = -1;
        double min_cost = 1e9;

        for (int i = 0; i < TECH_COUNT; ++i) {
            if (!breaks[i].technically_feasible) continue;
            double c = calc_unit_tco(&breaks[i], batches[b]);
            if (c < min_cost) {
                min_cost = c;
                best_tech = i;
            }
        }

        if (best_tech >= 0) {
            printf("  Тираж %5d шт: -> %-30s ($%.2f / шт)\n",
                   batches[b], TECH_NAMES[best_tech], min_cost);
        } else {
            printf("  Тираж %5d шт: -> Жодна технологія не задовольняє вимоги\n", batches[b]);
        }
    }
    printf("================================================================================\n");

    return 0;
}

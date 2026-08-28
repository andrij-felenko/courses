#include <stdio.h>
#include <stdbool.h>

/* Структура параметрів апаратного рішення */
typedef struct {
    const char* name;
    double nre_dev;         /* Вартість інженерної розробки (схема, PCB, BSP), $ */
    double nre_tooling;     /* Виробнича оснастка (трафарети, стенди), $ */
    double cert_cost;       /* Витрати на сертифікаційні лабораторії, $ */
    double bom_cost;        /* Чиста вартість компонентів (BOM), $ */
    double smt_cost;        /* Вартість SMT монтажу за одиницю, $ */
    double test_cost;       /* Вартість тестування за одиницю, $ */
    double scrap_rate;      /* Коефіцієнт браку (наприклад, 0.02 = 2%) */
    int time_to_market_w;   /* Термін запуску у виробництво, тижнів */
} HardwareTier;

/* Обчислення питомої вартості однієї придатної одиниці */
static double calc_unit_variable_cost(const HardwareTier* tier) {
    double base = tier->bom_cost + tier->smt_cost + tier->test_cost;
    if (tier->scrap_rate >= 1.0) {
        return base * 2.0;
    }
    return base / (1.0 - tier->scrap_rate);
}

/* Обчислення сумарного NRE */
static double calc_total_nre(const HardwareTier* tier) {
    return tier->nre_dev + tier->nre_tooling + tier->cert_cost;
}

/* Обчислення сукупної вартості TCO для партії V */
static double calc_tco(const HardwareTier* tier, unsigned int volume) {
    double nre = calc_total_nre(tier);
    double unit_var = calc_unit_variable_cost(tier);
    return nre + (double)volume * unit_var;
}

/* Розрахунок точки беззбитковості між двома рішеннями */
static bool calc_breakeven_point(const HardwareTier* t1, const HardwareTier* t2, double* out_v_star) {
    double nre1 = calc_total_nre(t1);
    double nre2 = calc_total_nre(t2);
    double u1 = calc_unit_variable_cost(t1);
    double u2 = calc_unit_variable_cost(t2);

    /* Якщо рішення з більшим NRE не забезпечує меншої собівартості одиниці, воно не окупиться */
    if (u1 <= u2 || nre2 <= nre1) {
        return false;
    }

    *out_v_star = (nre2 - nre1) / (u1 - u2);
    return (*out_v_star > 0.0);
}

int main(void) {
    HardwareTier tiers[4] = {
        {
            .name = "1. Девборда + макетка",
            .nre_dev = 200.0,
            .nre_tooling = 0.0,
            .cert_cost = 0.0,
            .bom_cost = 45.0,
            .smt_cost = 0.0,
            .test_cost = 5.0,
            .scrap_rate = 0.05,
            .time_to_market_w = 1
        },
        {
            .name = "2. Модуль на платі-носії",
            .nre_dev = 2500.0,
            .nre_tooling = 300.0,
            .cert_cost = 1500.0,
            .bom_cost = 16.50,
            .smt_cost = 2.50,
            .test_cost = 1.00,
            .scrap_rate = 0.02,
            .time_to_market_w = 4
        },
        {
            .name = "3. SoM на платі-носії",
            .nre_dev = 7000.0,
            .nre_tooling = 600.0,
            .cert_cost = 3500.0,
            .bom_cost = 42.00,
            .smt_cost = 3.50,
            .test_cost = 2.00,
            .scrap_rate = 0.02,
            .time_to_market_w = 10
        },
        {
            .name = "4. Повністю своя (Chip-Down)",
            .nre_dev = 35000.0,
            .nre_tooling = 4000.0,
            .cert_cost = 25000.0,
            .bom_cost = 9.80,
            .smt_cost = 1.80,
            .test_cost = 0.80,
            .scrap_rate = 0.04,
            .time_to_market_w = 32
        }
    };

    printf("=== АНАЛІЗ АПАРАТНИХ СХОДИНОК ===\n");
    for (int i = 0; i < 4; ++i) {
        double nre = calc_total_nre(&tiers[i]);
        double unit_c = calc_unit_variable_cost(&tiers[i]);
        printf("%s:\n  Фіксований NRE: $%.2f\n  Змінна собівартість: $%.2f/шт\n  Час запуску: %d тижнів\n\n",
               tiers[i].name, nre, unit_c, tiers[i].time_to_market_w);
    }

    /* Розрахунок точки беззбитковості між Модулем і Chip-Down */
    double v_star_2_4 = 0.0;
    if (calc_breakeven_point(&tiers[1], &tiers[3], &v_star_2_4)) {
        printf("Точка беззбитковості між Модулем і Chip-Down:\n");
        printf("  V* = %.0f шт.\n", v_star_2_4);
        printf("  При тиражі < %.0f шт вигідніший Модуль на носії.\n", v_star_2_4);
        printf("  При тиражі > %.0f шт вигідніший Chip-Down дизайн.\n\n", v_star_2_4);
    }

    /* Приклад оцінки партії в 1 000 шт і 20 000 шт */
    unsigned int test_volumes[2] = {1000, 20000};
    for (int v = 0; v < 2; ++v) {
        unsigned int vol = test_volumes[v];
        printf("--- Порівняння TCO для тиражу V = %u шт ---\n", vol);
        for (int i = 1; i < 4; i += 2) {
            double tco = calc_tco(&tiers[i], vol);
            double effective_unit = tco / (double)vol;
            printf("  %s: TCO = $%.2f (фактично $%.2f/шт)\n",
                   tiers[i].name, tco, effective_unit);
        }
    }

    return 0;
}

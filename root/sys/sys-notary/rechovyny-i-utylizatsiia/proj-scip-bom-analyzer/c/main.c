#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define ROHS_LIMIT_DEFAULT_PPM  1000.0   /* 0.1% w/w */
#define ROHS_LIMIT_CADMIUM_PPM   100.0   /* 0.01% w/w */
#define REACH_SVHC_LIMIT_PPM    1000.0   /* 0.1% w/w */

typedef enum {
    SUBSTANCE_BENIGN = 0,
    SUBSTANCE_ROHS_LEAD,
    SUBSTANCE_ROHS_CADMIUM,
    SUBSTANCE_ROHS_MERCURY,
    SUBSTANCE_ROHS_HEX_CHROMIUM,
    SUBSTANCE_ROHS_PBB_PBDE,
    SUBSTANCE_ROHS_PHTHALATE,
    SUBSTANCE_REACH_SVHC
} SubstanceType;

typedef struct {
    const char *name;
    const char *cas_number;
    SubstanceType type;
    double mass_mg;
    const char *rohs_exemption; /* NULL якщо винятку немає */
} Substance;

typedef struct {
    const char *part_number;
    const char *description;
    double total_mass_mg;
    Substance *substances;
    size_t substance_count;
} Article;

typedef struct {
    const char *product_name;
    Article *articles;
    size_t article_count;
} DeviceBom;

void analyze_compliance(const DeviceBom *bom) {
    printf("=================================================================\n");
    printf("ЗВІТ ЕКОЛОГІЧНОЇ ВІДПОВІДНОСТІ (RoHS / REACH / SCIP)\n");
    printf("Виріб: %s\n", bom->product_name);
    printf("=================================================================\n\n");

    bool rohs_overall_pass = true;
    size_t scip_notifications_required = 0;

    for (size_t i = 0; i < bom->article_count; ++i) {
        const Article *art = &bom->articles[i];
        printf("Компонент [%s]: %s (Маса: %.2f мг)\n",
               art->part_number, art->description, art->total_mass_mg);

        if (art->total_mass_mg <= 0.0) {
            printf("  [ПОМИЛКА]: Некоректна маса компонента!\n");
            continue;
        }

        for (size_t j = 0; j < art->substance_count; ++j) {
            const Substance *sub = &art->substances[j];
            double ppm = (sub->mass_mg / art->total_mass_mg) * 1000000.0;
            double percent = (sub->mass_mg / art->total_mass_mg) * 100.0;

            /* Перевірка вимог RoHS */
            if (sub->type >= SUBSTANCE_ROHS_LEAD && sub->type <= SUBSTANCE_ROHS_PHTHALATE) {
                double limit_ppm = (sub->type == SUBSTANCE_ROHS_CADMIUM) ?
                                   ROHS_LIMIT_CADMIUM_PPM : ROHS_LIMIT_DEFAULT_PPM;

                if (ppm > limit_ppm) {
                    if (sub->rohs_exemption != NULL && strlen(sub->rohs_exemption) > 0) {
                        printf("  · [RoHS EXEMPT]: %s (%.2f ppm / %.3f%%) -> Дозволено за винятком: %s\n",
                               sub->name, ppm, percent, sub->rohs_exemption);
                    } else {
                        printf("  · [RoHS FAIL]: %s (%.2f ppm / %.3f%%) -> Перевищує ліміт %.0f ppm!\n",
                               sub->name, ppm, percent, limit_ppm);
                        rohs_overall_pass = false;
                    }
                } else {
                    printf("  · [RoHS OK]: %s (%.2f ppm / %.4f%%)\n", sub->name, ppm, percent);
                }
            }

            /* Перевірка вимог REACH SVHC за правилом OAOA */
            if (sub->type == SUBSTANCE_REACH_SVHC || sub->type == SUBSTANCE_ROHS_LEAD || sub->type == SUBSTANCE_ROHS_PHTHALATE) {
                if (ppm > REACH_SVHC_LIMIT_PPM) {
                    printf("  · [SCIP MANDATORY]: Речовина SVHC %s [CAS %s] = %.3f%% w/w (> 0.1%%)\n",
                           sub->name, sub->cas_number, percent);
                    scip_notifications_required++;
                }
            }
        }
        printf("\n");
    }

    printf("-----------------------------------------------------------------\n");
    printf("ПІДСУМОК АУДИТУ:\n");
    printf("Статус RoHS: %s\n", rohs_overall_pass ? "ВІДПОВІДАЄ (PASS)" : "НЕ ВІДПОВІДАЄ (FAIL)");
    printf("Кількість обов'язкових нотифікацій у базі SCIP: %zu\n", scip_notifications_required);
    printf("=================================================================\n");
}

int main(void) {
    /* Тестові дані: розбір компонентів виробу */
    Substance r1_substances[] = {
        {"Тетрабромбісфенол А (TBBA)", "79-94-7", SUBSTANCE_REACH_SVHC, 12.0, NULL},
        {"Оксид свинцю у склі резистивного шару", "1317-36-8", SUBSTANCE_ROHS_LEAD, 0.45, "7(c)-I"}
    };

    Substance screw_substances[] = {
        {"Свинець у латунному сплаві CuZn39Pb3", "7439-92-1", SUBSTANCE_ROHS_LEAD, 25.0, "6(c)"}
    };

    Substance seal_substances[] = {
        {"Пластифікатор DEHP у гумі NBR", "117-81-7", SUBSTANCE_ROHS_PHTHALATE, 15.0, NULL}
    };

    Article articles[] = {
        {"R0805-10K", "Чіп-резистор 0805", 15.0, r1_substances, 2},
        {"SCR-M3-10", "Гвинт латунний M3x10", 850.0, screw_substances, 1},
        {"GSK-ORING-5", "Кільце ущільнювача корпусу", 500.0, seal_substances, 1}
    };

    DeviceBom device = {
        "Промисловий контролер IoT Gateway v2.0",
        articles,
        3
    };

    analyze_compliance(&device);
    return 0;
}

#include <stdio.h>
#include <stdbool.h>

typedef struct {
    const char *part_name;
    double total_mass_mg;
    const char *substance_name;
    double substance_mass_mg;
    double rohs_limit_percent;
    bool has_exemption;
    const char *exemption_clause;
} PartAnalysis;

void run_validation(const PartAnalysis *parts, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        const PartAnalysis *p = &parts[i];
        double concentration_percent = (p->substance_mass_mg / p->total_mass_mg) * 100.0;
        double concentration_ppm = concentration_percent * 10000.0;

        printf("Деталь: %s | Речовина: %s\n", p->part_name, p->substance_name);
        printf("  Концентрація: %.4f%% (%.1f ppm) | Ліміт: %.4f%%\n",
               concentration_percent, concentration_ppm, p->rohs_limit_percent);

        if (concentration_percent > p->rohs_limit_percent) {
            if (p->has_exemption) {
                printf("  -> СТАТУС: ВІДПОВІДАЄ ЗА ВИНИТКОМ %s\n", p->exemption_clause);
            } else {
                printf("  -> СТАТУС: КРИТИЧНЕ ПОРУШЕННЯ (FAIL)!\n");
            }
        } else {
            printf("  -> СТАТУС: ВІДПОВІДАЄ НОРМІ (PASS)\n");
        }

        /* Перевірка порогу SVHC для бази SCIP (> 0.1% w/w) */
        if (concentration_percent > 0.1) {
            printf("  -> SCIP: Обов'язкова нотифікація в ECHA (SVHC > 0.1%% w/w)\n");
        }
        printf("\n");
    }
}

int main(void) {
    PartAnalysis sample_parts[] = {
        {"Bolt-M4", 1200.0, "Свинець (Pb)", 33.6, 0.1, true, "6(c)"},
        {"Gasket-EPDM", 400.0, "Фталат DEHP", 0.8, 0.1, false, ""},
        {"Connector-SMA", 2500.0, "Кадмій (Cd)", 0.15, 0.01, false, ""}
    };

    run_validation(sample_parts, 3);
    return 0;
}

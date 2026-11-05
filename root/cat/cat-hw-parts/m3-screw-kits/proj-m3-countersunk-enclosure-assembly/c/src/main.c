#include <stdio.h>
#include <locale.h>
#include "m3_countersink_calc.h"

int main(void) {
    /* Налаштування локалі для коректного виведення символів */
    setlocale(LC_ALL, "");

    printf("==================================================================\n");
    printf(" ВЕРИФІКАЦІЙНИЙ РОЗРАХУНОК ПОТАЙНОГО З'ЄДНАННЯ М3 (DIN 7991 / ISO 10642)\n");
    printf("==================================================================\n\n");

    /* Тестові набори даних для перевірки */
    struct {
        float thickness;
        HousingMaterial material;
        const char *mat_name;
        ScrewClass screw;
        const char *screw_name;
    } test_cases[] = {
        { 2.0f, MATERIAL_ALUMINUM_6061_T6, "Алюміній 6061-T6", SCREW_CLASS_8_8,  "8.8"  },
        { 1.8f, MATERIAL_PLASTIC_ABS,      "Пластик ABS",      SCREW_CLASS_8_8,  "8.8"  },
        { 3.0f, MATERIAL_STEEL_Q235,       "Сталь Q235",       SCREW_CLASS_10_9, "10.9" }
    };

    int num_cases = sizeof(test_cases) / sizeof(test_cases[0]);
    float friction = 0.14f; /* Стандартний коефіцієнт тертя в різьбі з мастилом */

    for (int i = 0; i < num_cases; i++) {
        GeometryResult geom;
        StrengthResult strength;

        printf("--- Тест кейс #%d ---\n", i + 1);
        printf(" Товщина листа (t_plate): %.2f мм\n", test_cases[i].thickness);
        printf(" Матеріал корпусу:         %s\n", test_cases[i].mat_name);
        printf(" Клас міцності гвинта:     %s\n", test_cases[i].screw_name);

        bool status = verify_m3_countersink_joint(
            test_cases[i].thickness,
            test_cases[i].material,
            test_cases[i].screw,
            friction,
            &geom,
            &strength
        );

        printf("\n [Результати геометрії]:\n");
        printf("   Глибина фаски (h_k):      %.2f мм\n", geom.countersink_depth);
        printf("   Залишковий поясок (t_rem): %.2f мм\n", geom.residual_thickness);
        if (geom.knife_edge_risk) {
            printf("   [УВАГА] РИЗИК НОЖОВОГО КРАЮ! Заточена кромка занадто тонка.\n");
        } else {
            printf("   [НОРМА] Ризику ножового краю немає.\n");
        }

        printf("\n [Результати міцності та затягування]:\n");
        printf("   Попереднє зусилля (F_p):  %.1f Н\n", strength.preload_force_n);
        printf("   Момент затягування (M):   %.2f Н*м\n", strength.tightening_torque_nm);
        printf("   Контактний тиск (p_cont): %.1f МПа\n", strength.contact_pressure_mpa);
        printf("   Допустимий тиск (p_all):  %.1f МПа\n", strength.allowable_pressure_mpa);
        
        if (strength.pressure_exceeded) {
            printf("   [УВАГА] ПЕРЕВИЩЕННЯ КОНТАКТНОГО ТИСКУ!\n");
        } else {
            printf("   [НОРМА] Контактний тиск в межах допустимого.\n");
        }

        printf("\n Загальний статус з'єднання: %s\n", status ? "УСПІШНО (Надійне)" : "НЕБЕЗПЕЧНО (Потребує доопрацювання)");
        printf("------------------------------------------------------------------\n\n");
    }

    return 0;
}

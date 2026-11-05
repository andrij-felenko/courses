#include "t8_maintenance.h"
#include <stdio.h>
#include <string.h>

#define MIN_EFFECTIVE_FILM_UM 3.0    /* Мінімальна гідродинамічна плівка до переходу в граничне тертя */
#define CRITICAL_DUST_INDEX   0.8    /* Поріг абразивного забруднення */

void t8_tracker_init(t8_tracker_t *tracker, nut_material_t nut_material, double initial_film_um) {
    if (!tracker) return;

    memset(tracker, 0, sizeof(t8_tracker_t));
    tracker->nut_material = nut_material;

    tracker->grease.initial_film_thickness = (initial_film_um > 0.0) ? initial_film_um : 10.0;
    tracker->grease.film_thickness_um = tracker->grease.initial_film_thickness;
    tracker->grease.contamination_index = 0.0;
    tracker->grease.dynamic_viscosity_cst = 1000.0; /* SI-180 база */

    /* Для пари сталь-POM ресурс мастила довший завдяки низькій адгезії полімеру */
    if (nut_material == NUT_MATERIAL_POM) {
        tracker->service_limit_distance_m = 500.0; /* 500 метрів сумарного ходу Z */
    } else {
        tracker->service_limit_distance_m = 350.0; /* Для латуні вищий контактний тиск */
    }
}

void t8_tracker_log_movement(t8_tracker_t *tracker, double distance_mm, double speed_mm_s, bool is_z_hop, double dust_exposure_factor) {
    if (!tracker || distance_mm <= 0.0) return;

    double dist_m = distance_mm / 1000.0;
    tracker->total_distance_m += dist_m;

    if (speed_mm_s > 0.0) {
        tracker->print_hours += (distance_mm / speed_mm_s) / 3600.0;
    }

    if (is_z_hop) {
        tracker->z_hop_count++;
    }

    /* 1. Розрахунок деградації плівки: витіснення на краях та мікровипаровування */
    /* Z-hop реверси витісняють мастило швидше за плавний підйом на шар */
    double wear_rate = is_z_hop ? 0.000030 : 0.000015;
    double film_loss = dist_m * wear_rate * (speed_mm_s / 10.0);
    
    if (tracker->grease.film_thickness_um > film_loss) {
        tracker->grease.film_thickness_um -= film_loss;
    } else {
        tracker->grease.film_thickness_um = 0.1; /* Граничне сухе/напівсухе тертя */
    }

    /* 2. Накопичення пилу у відкритій трибосистемі ходового гвинта */
    double dust_rate = (dust_exposure_factor > 0.5) ? dust_exposure_factor : 1.0;
    tracker->grease.contamination_index += (dist_m / tracker->service_limit_distance_m) * 0.85 * dust_rate;
    if (tracker->grease.contamination_index > 1.0) {
        tracker->grease.contamination_index = 1.0;
    }

    /* 3. Оцінка механічного зносу нарізі гайки: різко зростає при стоншенні плівки */
    double boundary_friction_penalty = 1.0;
    if (tracker->grease.film_thickness_um < MIN_EFFECTIVE_FILM_UM) {
        boundary_friction_penalty = 4.5; /* Зрив мастильного клину */
    }

    double nut_wear_factor = (tracker->nut_material == NUT_MATERIAL_POM) ? 0.002 : 0.005;
    tracker->accumulated_wear_um += dist_m * nut_wear_factor * boundary_friction_penalty * (1.0 + tracker->grease.contamination_index * 2.0);
}

double t8_tracker_get_grease_health(const t8_tracker_t *tracker) {
    if (!tracker) return 0.0;

    double film_ratio = tracker->grease.film_thickness_um / tracker->grease.initial_film_thickness;
    if (film_ratio > 1.0) film_ratio = 1.0;
    if (film_ratio < 0.0) film_ratio = 0.0;

    double cleanliness = 1.0 - tracker->grease.contamination_index;
    if (cleanliness < 0.0) cleanliness = 0.0;

    /* Ресурс як комбінація товщини плівки (60%) та чистоти мастила (40%) */
    double health = (film_ratio * 0.6 + cleanliness * 0.4) * 100.0;
    return (health > 0.0) ? health : 0.0;
}

bool t8_tracker_needs_maintenance(const t8_tracker_t *tracker) {
    if (!tracker) return false;

    if (tracker->grease.film_thickness_um <= MIN_EFFECTIVE_FILM_UM) {
        return true; /* Плівка тонша за критичні 3 мкм */
    }
    if (tracker->grease.contamination_index >= CRITICAL_DUST_INDEX) {
        return true; /* Небезпечна концентрація пилу */
    }
    if (tracker->total_distance_m >= tracker->service_limit_distance_m) {
        return true; /* Досягнуто граничного пробігу */
    }

    return false;
}

void t8_tracker_perform_service(t8_tracker_t *tracker, double new_film_um) {
    if (!tracker) return;

    tracker->total_distance_m = 0.0;
    tracker->grease.initial_film_thickness = (new_film_um > 0.0) ? new_film_um : 10.0;
    tracker->grease.film_thickness_um = tracker->grease.initial_film_thickness;
    tracker->grease.contamination_index = 0.0;
}

void t8_tracker_print_report(const t8_tracker_t *tracker) {
    if (!tracker) return;

    printf("\n======================================================\n");
    printf("   ЗВІТ ТЕХНІЧНОГО СТАНУ ВУЗЛА ХОДОВОГО ГВИНТА T8    \n");
    printf("======================================================\n");
    printf(" Матеріал гайки              : %s\n", 
           (tracker->nut_material == NUT_MATERIAL_POM) ? "Поліацеталь (POM)" : "Латунь (CW614N)");
    printf(" Сумарний пробіг осі Z       : %.2f м (ліміт: %.1f м)\n", 
           tracker->total_distance_m, tracker->service_limit_distance_m);
    printf(" Напрацювання друку          : %.2f год\n", tracker->print_hours);
    printf(" Кількість переміщень Z-hop  : %u\n", tracker->z_hop_count);
    printf(" Поточна товщина плівки SI-180: %.2f мкм (початкова: %.1f мкм)\n", 
           tracker->grease.film_thickness_um, tracker->grease.initial_film_thickness);
    printf(" Індекс забруднення пилом    : %.1f %%\n", tracker->grease.contamination_index * 100.0);
    printf(" Накопичений знос нарізі     : %.3f мкм\n", tracker->accumulated_wear_um);
    printf(" Залишковий ресурс мастила   : %.1f %%\n", t8_tracker_get_grease_health(tracker));
    printf("------------------------------------------------------\n");

    if (t8_tracker_needs_maintenance(tracker)) {
        printf(" СТАТУС: [ПОТРІБНЕ ТЕХОБСЛУГОВУВАННЯ!]\n");
        printf(" ДІЯ: 1. Промити витки T8 та гайку ізопропіловим спиртом IPA.\n");
        printf("      2. Нанести 0.1-0.2 мл свіжої змазки SI-180.\n");
        printf("      3. Виконати 3 цикли повного переміщення осі Z.\n");
    } else {
        printf(" СТАТУС: [НОРМА] Мастильна плівка стабільна. Вузол готовий до друку.\n");
    }
    printf("======================================================\n");
}

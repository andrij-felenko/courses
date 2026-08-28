#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_COMPONENTS 128
#define MAX_NETS       256

typedef enum {
    KIND_FIXED_MECHANICAL,
    KIND_PROCESSOR_CORE,
    KIND_POWER_HOT,
    KIND_ANALOG_SENSITIVE,
    KIND_DECOUPLING_CAP
} ComponentKind;

typedef struct {
    int id;
    ComponentKind kind;
    double x;      /* координата X в мм */
    double y;      /* координата Y в мм */
    double width;  /* ширина в мм */
    double height; /* висота в мм */
    int assigned_to_ic; /* ID мікросхеми для DECOUPLING_CAP, інакше -1 */
} Component;

typedef struct {
    int comp_a;
    int comp_b;
    double weight;
} NetConnection;

typedef struct {
    Component components[MAX_COMPONENTS];
    int comp_count;
    NetConnection nets[MAX_NETS];
    int net_count;
    double board_width;
    double board_height;
} Floorplan;

/* Обчислення мангеттенської довжини всіх зв'язків */
double calculate_total_manhattan_wirelength(const Floorplan *fp) {
    double total_length = 0.0;
    for (int i = 0; i < fp->net_count; i++) {
        const Component *a = &fp->components[fp->nets[i].comp_a];
        const Component *b = &fp->components[fp->nets[i].comp_b];
        double dx = fabs(a->x - b->x);
        double dy = fabs(a->y - b->y);
        total_length += (dx + dy) * fp->nets[i].weight;
    }
    return total_length;
}

/* Перевірка теплових дистанцій та близькості розв'язки */
bool verify_floorplan_rules(const Floorplan *fp, double min_thermal_dist, double max_decoupling_dist) {
    bool passed = true;

    /* 1. Перевірка теплової ізоляції: Power Hot -> Analog Sensitive */
    for (int i = 0; i < fp->comp_count; i++) {
        if (fp->components[i].kind != KIND_POWER_HOT) continue;
        for (int j = 0; j < fp->comp_count; j++) {
            if (fp->components[j].kind != KIND_ANALOG_SENSITIVE) continue;

            double dx = fp->components[i].x - fp->components[j].x;
            double dy = fp->components[i].y - fp->components[j].y;
            double dist = sqrt(dx * dx + dy * dy);

            if (dist < min_thermal_dist) {
                printf("ПОМИЛКА ТЕПЛА: Гарячий вузол #%d занадто близько до сенсора #%d (%.2f мм < %.2f мм)\n",
                       fp->components[i].id, fp->components[j].id, dist, min_thermal_dist);
                passed = false;
            }
        }
    }

    /* 2. Перевірка близькості блокувальних конденсаторів */
    for (int i = 0; i < fp->comp_count; i++) {
        if (fp->components[i].kind != KIND_DECOUPLING_CAP) continue;
        int target_ic = fp->components[i].assigned_to_ic;
        if (target_ic < 0 || target_ic >= fp->comp_count) continue;

        const Component *ic = &fp->components[target_ic];
        double dx = fp->components[i].x - ic->x;
        double dy = fp->components[i].y - ic->y;
        double dist = sqrt(dx * dx + dy * dy);

        if (dist > max_decoupling_dist) {
            printf("ПОМИЛКА РОЗВ'ЯЗКИ: Конденсатор #%d занадто далеко від IC #%d (%.2f мм > %.2f мм)\n",
                   fp->components[i].id, ic->id, dist, max_decoupling_dist);
            passed = false;
        }
    }

    return passed;
}

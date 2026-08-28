#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_COMPONENTS 128
#define MAX_NETS       256
#define MAX_PINS_PER_NET 32
#define GRID_SIZE      16

typedef enum {
    TYPE_FIXED_CONNECTOR,
    TYPE_PROCESSOR_CORE,
    TYPE_POWER_SUPPLY,
    TYPE_SENSITIVE_ANALOG,
    TYPE_PASSIVE_DECOUPLING
} CompType;

typedef struct {
    int id;
    char name[16];
    CompType type;
    double x, y;          /* Координати центру (мм) */
    double vx, vy;        /* Вектор швидкості для інтегратора */
    double width, height; /* Розміри посадкового місця (мм) */
    bool is_fixed;        /* Прапорець фіксованого положення (Zero DOF) */
    double heat_power;    /* Теплове виділення (Вт) */
    double temp_sens;     /* Коефіцієнт чутливості до температури */
} SimComponent;

typedef struct {
    int id;
    char name[16];
    int pin_comp_ids[MAX_PINS_PER_NET];
    int pin_count;
    double weight;
} SimNet;

typedef struct {
    SimComponent components[MAX_COMPONENTS];
    int comp_count;
    SimNet nets[MAX_NETS];
    int net_count;
    double board_w;
    double board_h;
    double congestion_grid[GRID_SIZE][GRID_SIZE];
} PlacementEngine;

/* Ініціалізація рушія розміщення */
void placement_init(PlacementEngine *pe, double w, double h) {
    pe->comp_count = 0;
    pe->net_count = 0;
    pe->board_w = w;
    pe->board_h = h;
    memset(pe->congestion_grid, 0, sizeof(pe->congestion_grid));
}

/* Додавання компонента */
int placement_add_component(PlacementEngine *pe, const char *name, CompType type,
                            double x, double y, double w, double h,
                            bool is_fixed, double heat, double sens) {
    if (pe->comp_count >= MAX_COMPONENTS) return -1;
    int idx = pe->comp_count++;
    SimComponent *c = &pe->components[idx];
    c->id = idx;
    strncpy(c->name, name, sizeof(c->name) - 1);
    c->type = type;
    c->x = x; c->y = y;
    c->vx = 0.0; c->vy = 0.0;
    c->width = w; c->height = h;
    c->is_fixed = is_fixed;
    c->heat_power = heat;
    c->temp_sens = sens;
    return idx;
}

/* Додавання електричної мережі */
int placement_add_net(PlacementEngine *pe, const char *name, double weight) {
    if (pe->net_count >= MAX_NETS) return -1;
    int idx = pe->net_count++;
    SimNet *n = &pe->nets[idx];
    n->id = idx;
    strncpy(n->name, name, sizeof(n->name) - 1);
    n->pin_count = 0;
    n->weight = weight;
    return idx;
}

void placement_net_add_pin(PlacementEngine *pe, int net_idx, int comp_idx) {
    if (net_idx < 0 || net_idx >= pe->net_count) return;
    SimNet *n = &pe->nets[net_idx];
    if (n->pin_count < MAX_PINS_PER_NET) {
        n->pin_comp_ids[n->pin_count++] = comp_idx;
    }
}

/* Обчислення сумарного HPWL */
double placement_calculate_hpwl(const PlacementEngine *pe) {
    double total_hpwl = 0.0;
    for (int i = 0; i < pe->net_count; i++) {
        const SimNet *net = &pe->nets[i];
        if (net->pin_count < 2) continue;

        double min_x = 1e9, max_x = -1e9;
        double min_y = 1e9, max_y = -1e9;

        for (int p = 0; p < net->pin_count; p++) {
            const SimComponent *c = &pe->components[net->pin_comp_ids[p]];
            if (c->x < min_x) min_x = c->x;
            if (c->x > max_x) max_x = c->x;
            if (c->y < min_y) min_y = c->y;
            if (c->y > max_y) max_y = c->y;
        }

        double net_hpwl = (max_x - min_x) + (max_y - min_y);
        /* Масштабування за коефіцієнтом Альперта */
        double q = (net->pin_count == 2) ? 1.0 : (net->pin_count == 3) ? 1.0 : 1.15;
        total_hpwl += net_hpwl * net->weight * q;
    }
    return total_hpwl;
}

/* Оцінка заторів трасування за сіткою G-cells */
void placement_compute_congestion(PlacementEngine *pe) {
    memset(pe->congestion_grid, 0, sizeof(pe->congestion_grid));
    double cell_w = pe->board_w / GRID_SIZE;
    double cell_h = pe->board_h / GRID_SIZE;

    for (int i = 0; i < pe->net_count; i++) {
        const SimNet *net = &pe->nets[i];
        if (net->pin_count < 2) continue;

        double min_x = 1e9, max_x = -1e9, min_y = 1e9, max_y = -1e9;
        for (int p = 0; p < net->pin_count; p++) {
            const SimComponent *c = &pe->components[net->pin_comp_ids[p]];
            if (c->x < min_x) min_x = c->x;
            if (c->x > max_x) max_x = c->x;
            if (c->y < min_y) min_y = c->y;
            if (c->y > max_y) max_y = c->y;
        }

        int gx0 = (int)(min_x / cell_w); if (gx0 < 0) gx0 = 0; if (gx0 >= GRID_SIZE) gx0 = GRID_SIZE - 1;
        int gx1 = (int)(max_x / cell_w); if (gx1 < 0) gx1 = 0; if (gx1 >= GRID_SIZE) gx1 = GRID_SIZE - 1;
        int gy0 = (int)(min_y / cell_h); if (gy0 < 0) gy0 = 0; if (gy0 >= GRID_SIZE) gy0 = GRID_SIZE - 1;
        int gy1 = (int)(max_y / cell_h); if (gy1 < 0) gy1 = 0; if (gy1 >= GRID_SIZE) gy1 = GRID_SIZE - 1;

        double demand = net->weight / (double)((gx1 - gx0 + 1) * (gy1 - gy0 + 1));
        for (int gy = gy0; gy <= gy1; gy++) {
            for (int gx = gx0; gx <= gx1; gx++) {
                pe->congestion_grid[gy][gx] += demand;
            }
        }
    }
}

/* Виконання однієї ітерації силового розміщення */
double placement_step(PlacementEngine *pe, double k_spring, double k_repulse,
                      double k_thermal, double max_step, double damping) {
    double fx[MAX_COMPONENTS] = {0};
    double fy[MAX_COMPONENTS] = {0};

    /* 1. Пружинні сили зв'язків (клікова модель) */
    for (int n = 0; n < pe->net_count; n++) {
        const SimNet *net = &pe->nets[n];
        if (net->pin_count < 2) continue;
        double scale = 2.0 / (double)net->pin_count;

        for (int i = 0; i < net->pin_count; i++) {
            for (int j = i + 1; j < net->pin_count; j++) {
                int id_a = net->pin_comp_ids[i];
                int id_b = net->pin_comp_ids[j];

                double dx = pe->components[id_b].x - pe->components[id_a].x;
                double dy = pe->components[id_b].y - pe->components[id_a].y;

                double force_x = k_spring * net->weight * scale * dx;
                double force_y = k_spring * net->weight * scale * dy;

                fx[id_a] += force_x;
                fy[id_a] += force_y;
                fx[id_b] -= force_x;
                fy[id_b] -= force_y;
            }
        }
    }

    /* 2. Сили відштовхування перекриттів і теплові сили */
    for (int i = 0; i < pe->comp_count; i++) {
        for (int j = i + 1; j < pe->comp_count; j++) {
            SimComponent *a = &pe->components[i];
            SimComponent *b = &pe->components[j];

            double dx = b->x - a->x;
            double dy = b->y - a->y;
            double dist_sq = dx * dx + dy * dy;
            double dist = sqrt(dist_sq) + 0.001;

            /* Перекриття прямокутників */
            double req_x = (a->width + b->width) * 0.5 + 1.0;
            double req_y = (a->height + b->height) * 0.5 + 1.0;
            double abs_dx = fabs(dx);
            double abs_dy = fabs(dy);

            if (abs_dx < req_x && abs_dy < req_y) {
                double over_x = req_x - abs_dx;
                double over_y = req_y - abs_dy;
                double rep_x = (dx > 0 ? -1.0 : 1.0) * k_repulse * over_x;
                double rep_y = (dy > 0 ? -1.0 : 1.0) * k_repulse * over_y;

                fx[i] += rep_x; fy[i] += rep_y;
                fx[j] -= rep_x; fy[j] -= rep_y;
            }

            /* Теплове відштовхування: гаряче відштовхує чутливе */
            if ((a->heat_power > 0.0 && b->temp_sens > 0.0) ||
                (b->heat_power > 0.0 && a->temp_sens > 0.0)) {
                double p_src = (a->heat_power > b->heat_power) ? a->heat_power : b->heat_power;
                double s_dst = (a->temp_sens > b->temp_sens) ? a->temp_sens : b->temp_sens;
                double f_th = (k_thermal * p_src * s_dst) / (dist_sq + 100.0);

                double th_x = (dx / dist) * f_th;
                double th_y = (dy / dist) * f_th;

                fx[i] -= th_x; fy[i] -= th_y;
                fx[j] += th_x; fy[j] += th_y;
            }
        }
    }

    /* 3. Оновлення координат за методом Ейлера з затуханням */
    double max_movement = 0.0;
    for (int i = 0; i < pe->comp_count; i++) {
        SimComponent *c = &pe->components[i];
        if (c->is_fixed) continue;

        c->vx = (1.0 - damping) * c->vx + fx[i] * 0.01;
        c->vy = (1.0 - damping) * c->vy + fy[i] * 0.01;

        double step_x = c->vx;
        double step_y = c->vy;
        double step_len = sqrt(step_x * step_x + step_y * step_y);

        if (step_len > max_step) {
            step_x = (step_x / step_len) * max_step;
            step_y = (step_y / step_len) * max_step;
        }

        c->x += step_x;
        c->y += step_y;

        /* Обмеження межами плати */
        double pad_x = c->width * 0.5 + 2.0;
        double pad_y = c->height * 0.5 + 2.0;
        if (c->x < pad_x) c->x = pad_x;
        if (c->x > pe->board_w - pad_x) c->x = pe->board_w - pad_x;
        if (c->y < pad_y) c->y = pad_y;
        if (c->y > pe->board_h - pad_y) c->y = pe->board_h - pad_y;

        if (step_len > max_movement) max_movement = step_len;
    }

    return max_movement;
}

/* Запуск повного циклу оптимізації */
void placement_solve(PlacementEngine *pe, int max_iterations) {
    double temp = 5.0; /* Початковий радіус переміщення */
    double decay = 0.985;

    for (int iter = 0; iter < max_iterations; iter++) {
        double max_move = placement_step(pe, 1.2, 45.0, 150.0, temp, 0.25);
        temp *= decay;
        if (temp < 0.05 && max_move < 0.01) {
            printf("Оптимізація зійшлася на ітерації %d. HPWL = %.2f мм\n",
                   iter, placement_calculate_hpwl(pe));
            break;
        }
    }
    placement_compute_congestion(pe);
}

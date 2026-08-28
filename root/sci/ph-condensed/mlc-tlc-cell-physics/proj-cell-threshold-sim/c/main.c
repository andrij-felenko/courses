#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    CELL_SLC = 1,
    CELL_MLC = 2,
    CELL_TLC = 3,
    CELL_QLC = 4
} CellTypeC;

typedef struct {
    double vth;
    int target_state;
} CellC;

// Генератор гауссового розподілу за методом Бокса-Мюллера
static double generate_gaussian(double mean, double stddev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-9) u1 = 1e-9;
    
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return mean + z0 * stddev;
}

// Початкове стирання масиву
void erase_array_c(CellC* cells, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        cells[i].vth = generate_gaussian(-2.5, 0.30);
        cells[i].target_state = 0;
    }
}

// Симуляція ISPP програмування
void program_array_c(CellC* cells, size_t count, CellTypeC type, double delta_vpgm) {
    int states_count = 1 << (int)type;
    double window_step = 6.0 / states_count;

    for (size_t i = 0; i < count; ++i) {
        cells[i].target_state = rand() % states_count;
        if (cells[i].target_state == 0) continue;

        double target_v = -1.5 + cells[i].target_state * window_step;
        while (cells[i].vth < target_v) {
            double noise = generate_gaussian(0.0, 0.05);
            cells[i].vth += delta_vpgm + noise;
        }
    }
}

// Застосування фізичної деградації
void apply_degradation_c(CellC* cells, size_t count, CellTypeC type, double pe_cycles, double retention_hours) {
    double oxide_damage = sqrt(pe_cycles / 1000.0);
    double retention_loss = 0.05 * oxide_damage * log(1.0 + retention_hours);

    for (size_t i = 0; i < count; ++i) {
        double rtn = generate_gaussian(0.0, 0.03 * (1.0 + oxide_damage));
        double disturb = (cells[i].target_state > 0) ? generate_gaussian(0.04 * oxide_damage, 0.02) : 0.01;

        cells[i].vth += rtn + disturb - retention_loss;
    }
}

// Обчислення помилок RBER
double calculate_rber_c(const CellC* cells, size_t count, CellTypeC type) {
    int states_count = 1 << (int)type;
    double window_step = 6.0 / states_count;

    size_t bit_errors = 0;
    size_t total_bits = count * (int)type;

    for (size_t i = 0; i < count; ++i) {
        int detected_state = 0;
        for (int k = 0; k < states_count - 1; ++k) {
            double v_ref = -1.5 + (k + 0.5) * window_step;
            if (cells[i].vth > v_ref) {
                detected_state = k + 1;
            }
        }

        int diff = cells[i].target_state ^ detected_state;
        while (diff > 0) {
            if (diff & 1) bit_errors++;
            diff >>= 1;
        }
    }

    return (double)bit_errors / total_bits;
}

int main() {
    srand(42);
    size_t count = 100000;
    CellC* cells = (CellC*)malloc(count * sizeof(CellC));

    printf("=== C Симуляція фізики порогових напруг NAND (100,000 комірок) ===\n");
    printf("%-15s %-15s %-18s %-15s\n", "Тип комірки", "P/E Цикли", "Час Retention", "RBER");
    printf("---------------------------------------------------------------\n");

    CellTypeC types[] = { CELL_SLC, CELL_MLC, CELL_TLC, CELL_QLC };
    const char* names[] = { "SLC (1 біт)", "MLC (2 біти)", "TLC (3 біти)", "QLC (4 біти)" };
    double pe_list[] = { 10000.0, 3000.0, 1000.0, 500.0 };

    for (int t = 0; t < 4; ++t) {
        erase_array_c(cells, count);
        program_array_c(cells, count, types[t], 0.20);
        apply_degradation_c(cells, count, types[t], pe_list[t], 1000.0);

        double rber = calculate_rber_c(cells, count, types[t]);
        printf("%-15s %-15.0f %-18s %-15.3e\n", names[t], pe_list[t], "1000 год", rber);
    }

    free(cells);
    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SIZE 100
#define DX 1.0e-9       // Просторовий крок: 1 нанометр
#define DT 1.0e-12      // Часовий крок: 1 пікосекунда

// Фізичні константи матеріалу GST-225
const double DENSITY = 6150.0;        // кг/м³
const double SPECIFIC_HEAT = 202.0;   // Дж/(кг·К)
const double T_MELT = 888.0;          // 615 °C (плавлення)
const double T_GLASS = 473.0;         // 200 °C (склування)
const double T_AMB = 300.0;           // Кімнатна температура (300 K)

typedef struct {
    double temp[GRID_SIZE];
    double k_th[GRID_SIZE];
    double rho[GRID_SIZE];
} pcm_cell_t;

void init_cell(pcm_cell_t *cell) {
    for (int i = 0; i < GRID_SIZE; i++) {
        cell->temp[i] = T_AMB;
        cell->k_th[i] = 0.5;          // Кристалічний стан
        cell->rho[i] = 1.0e-5;         // Низький опір (Ом·м)
    }
}

void simulate_pulse(pcm_cell_t *cell, double current_density, double duration_ns) {
    int steps = (int)(duration_ns * 1.0e-9 / DT);
    double next_temp[GRID_SIZE];

    for (int step = 0; step < steps; step++) {
        for (int i = 1; i < GRID_SIZE - 1; i++) {
            double heat_conduction = cell->k_th[i] * (cell->temp[i+1] - 2.0 * cell->temp[i] + cell->temp[i-1]) / (DX * DX);
            double joule_heating = current_density * current_density * cell->rho[i];
            
            double dT = (DT / (DENSITY * SPECIFIC_HEAT)) * (heat_conduction + joule_heating);
            next_temp[i] = cell->temp[i] + dT;
        }
        // Граничні умови (фіксована температура підкладок T_amb)
        next_temp[0] = T_AMB;
        next_temp[GRID_SIZE - 1] = T_AMB;

        for (int i = 0; i < GRID_SIZE; i++) {
            cell->temp[i] = next_temp[i];
        }
    }
}

int main(void) {
    pcm_cell_t cell;
    init_cell(&cell);

    printf("=== Симуляція RESET імпульсу (Плавлення та електротерміка) ===\n");
    simulate_pulse(&cell, 5.0e11, 10.0); // 10 нс високого струму
    
    double max_t = 0.0;
    for (int i = 0; i < GRID_SIZE; i++) {
        if (cell.temp[i] > max_t) max_t = cell.temp[i];
    }
    printf("Максимальна температура в гарячій точці: %.1f K (T_m = %.1f K)\n", max_t, T_MELT);

    if (max_t > T_MELT) {
        printf("Результат: Досягнуто фазового плавлення. Потрібне швидке загартування для RESET.\n");
    } else {
        printf("Результат: Недостатній струм для аморфізації.\n");
    }

    return 0;
}

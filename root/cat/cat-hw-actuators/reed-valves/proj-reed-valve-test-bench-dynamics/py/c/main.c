#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_POINTS 1000

typedef struct {
    double time[NUM_POINTS];
    double pressure[NUM_POINTS];
    double flow[NUM_POINTS];
} WaveformData;

int read_waveforms(WaveformData *data) {
    double f = 100.0;
    for (int i = 0; i < NUM_POINTS; i++) {
        data->time[i] = (double)i / 10000.0;
        data->pressure[i] = 100.0 * sin(2 * 3.1415926535 * f * data->time[i]);
        data->flow[i] = 50.0 * sin(2 * 3.1415926535 * f * data->time[i] - 0.3) - 5.0 * (data->pressure[i] > 0 ? data->pressure[i]/100.0 : 0);
    }
    return 0;
}

double calculate_reverse_flow(const double *flow, int size) {
    double min_f = 0.0;
    for (int i = 0; i < size; i++) {
        if (flow[i] < min_f) {
            min_f = flow[i];
        }
    }
    return min_f < 0 ? -min_f : 0.0;
}

int main() {
    printf("Ініціалізація вимірювального комплексу (C мова)...\n");
    
    WaveformData data;
    if (read_waveforms(&data) != 0) {
        fprintf(stderr, "Помилка зчитування осцилограм.\n");
        return 1;
    }
    
    double rev_flow = calculate_reverse_flow(data.flow, NUM_POINTS);
    printf("Динамічний зворотний потік: %.4f мл/с\n", rev_flow);
    printf("Вимірювальний цикл завершено успішно.\n");
    
    return 0;
}

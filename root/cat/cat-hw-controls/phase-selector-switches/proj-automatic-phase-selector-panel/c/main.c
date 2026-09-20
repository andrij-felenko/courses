#include <stdio.h>
#include "phase_selector.h"

int main(void) {
    phase_selector_config_t cfg = {
        .u_min = 195.0f,
        .u_max = 253.0f,
        .u_hysteresis = 5.0f,
        .dead_time_ms = 50,
        .return_delay_ms = 2000
    };

    phase_selector_t ps;
    phase_selector_init(&ps, &cfg);

    printf("=== Симуляція алгоритму АВФ (Перемикач фаз) ===\n");

    float test_voltages[][3] = {
        { 220.0f, 225.0f, 218.0f },
        { 180.0f, 225.0f, 218.0f },
        { 180.0f, 225.0f, 218.0f },
        { 222.0f, 225.0f, 218.0f },
        { 222.0f, 225.0f, 218.0f }
    };

    uint32_t simulated_time = 0;
    const uint32_t step_ms = 10;

    for (int step = 0; step < 300; step++) {
        float u_l1 = test_voltages[0][0];
        float u_l2 = test_voltages[0][1];
        float u_l3 = test_voltages[0][2];

        if (simulated_time >= 500 && simulated_time < 1000) {
            u_l1 = test_voltages[1][0];
        } else if (simulated_time >= 1000 && simulated_time < 1500) {
            u_l1 = test_voltages[2][0];
        } else if (simulated_time >= 1500) {
            u_l1 = test_voltages[3][0];
        }

        phase_selector_update(&ps, u_l1, u_l2, u_l3, step_ms);

        if (step % 20 == 0 || ps.state == STATE_DEAD_TIME) {
            printf("[%4u мс] U_L1=%.1fV U_L2=%.1fV | Стан=%d, Активна фаза=%d (Ціль=%d)\n",
                   simulated_time, u_l1, u_l2, ps.state, ps.active_phase, ps.target_phase);
        }

        simulated_time += step_ms;
    }

    printf("=== Симуляцію успішно завершено ===\n");
    return 0;
}

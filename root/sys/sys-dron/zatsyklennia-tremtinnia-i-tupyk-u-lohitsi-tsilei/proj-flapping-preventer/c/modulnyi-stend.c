#include <stdio.h>
#include <math.h>

void run_flapping_verification_test(void) {
    flapping_preventer_t filter;
    uint32_t now_us = 0;
    flapping_preventer_init(&filter, 0.60f, 0.40f, 200000, 1000000, 5.0f, 2.0f, now_us);

    printf("--- Тест 1: Зашумлений сигнал біля порогу 0.50 з шумом sigma=0.08 ---\n");
    for (int step = 0; step < 100; ++step) {
        now_us += 20000; /* Крок 20 мс (50 Гц) */
        float noise = ((float)(step % 7) - 3.0f) * 0.03f;
        float signal = 0.50f + noise; /* Коливання 0.41..0.59 (всередині петлі гістерезису) */
        bool state = flapping_preventer_process(&filter, signal, 1, 10.0f, 10.0f, 50.0f, now_us, false);
        (void)state;
    }
    printf("Заблоковано спроб тремтіння: %u, вихідний стан стабільний: %s\n",
           filter.suppressed_switch_count, filter.gate.active_state ? "TRUE" : "FALSE");

    printf("--- Тест 2: 3-фазне просторове зациклення A->B->C->A ---\n");
    uint16_t states[3] = {101, 102, 103};
    float coords[3][3] = {
        {10.0f, 10.0f, 50.0f},
        {30.0f, 10.0f, 50.0f},
        {20.0f, 25.0f, 50.0f}
    };

    for (int cycle = 0; cycle < 4; ++cycle) {
        for (int phase = 0; phase < 3; ++phase) {
            now_us += 500000;
            flapping_preventer_process(&filter, 0.8f, states[phase],
                                       coords[phase][0], coords[phase][1], coords[phase][2],
                                       now_us, false);
        }
    }
    printf("Детектовано цикл довжиною: %u, Рівень ескалації: %d\n",
           filter.detected_cycle_len, (int)filter.current_escalation);
}

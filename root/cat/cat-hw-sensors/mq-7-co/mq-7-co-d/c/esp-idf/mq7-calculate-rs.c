#include <math.h>
#include <stdio.h>

// Електричні параметри кола вимірювання MQ-7
#define V_IN          5.0f     // Напруга живлення дільника, В
#define R_LOAD        10000.0f // Опір навантажувального резистора RL, Ом
#define PARAM_M      -0.77f    // Кутовий коефіцієнт m у log-log координатах
#define PARAM_B       1.33f    // Коефіцієнт зсуву b у log-log координатах

// Обчислення опору сенсора Rs за напругою Vout
float mq7_calculate_rs(float v_out) {
    if (v_out <= 0.0f || v_out >= V_IN) return -1.0f;
    return R_LOAD * (V_IN - v_out) / v_out;
}

// Перерахунок співвідношення Rs/R0 у значення ppm чадного газу
float mq7_calculate_ppm(float rs, float r0) {
    if (rs <= 0.0f || r0 <= 0.0f) return 0.0f;
    float ratio = rs / r0;
    float log_ppm = (log10f(ratio) - PARAM_B) / PARAM_M;
    return powf(10.0f, log_ppm);
}

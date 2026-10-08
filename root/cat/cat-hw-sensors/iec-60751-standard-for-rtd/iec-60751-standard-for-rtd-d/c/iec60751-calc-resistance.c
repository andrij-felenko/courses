#include <stdio.h>

// Коефіцієнти стандарту IEC 60751 для платинових RTD
#define IEC60751_A  3.9083e-3
#define IEC60751_B -5.775e-7
#define IEC60751_C -4.183e-12

/**
 * Обчислює опір платинового RTD за рівнянням Каллендара — Ван Дюзена.
 * @param t Температура у градусах Цельсія (°C)
 * @param r0 Номінальний опір при 0 °C (100.0 для Pt100, 1000.0 для Pt1000)
 * @return Розрахований опір у Омах
 */
double iec60751_calc_resistance(double t, double r0) {
    if (t >= 0.0) {
        return r0 * (1.0 + IEC60751_A * t + IEC60751_B * t * t);
    } else {
        double t_minus_100 = t - 100.0;
        double t_cubed = t * t * t;
        return r0 * (1.0 + IEC60751_A * t + IEC60751_B * t * t + IEC60751_C * t_minus_100 * t_cubed);
    }
}

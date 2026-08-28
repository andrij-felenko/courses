#include <stdio.h>
#include <math.h>
#include <stdbool.h>

// Структура для збереження результатів аналізу траси у точці
typedef struct {
    double r1_meters;          // Радіус 1-ї зони Френеля (м)
    double earth_bulge_m;      // Опуклість Землі у точці (м)
    double los_height_m;       // Висота лінії LOS у точці перешкоди (м)
    double clearance_m;        // Наявний чистий просвіт (м)
    double clearance_ratio;    // Відносний просвіт (c / R1)
    double diff_loss_db;       // Дифракційне загасання (дБ)
    bool is_clear;             // Прапорець виконання критерію 60% R1
} TraceAnalysisResult;

// Оцінка дифракційного загасання за спрощеною формулою Лі
static double calculate_knife_edge_loss(double clearance_ratio) {
    // c/R1 = 0.6 відповідає параметру v = -0.6 * sqrt(2) ≈ -0.85
    double v = -clearance_ratio * 1.41421356;
    
    if (v < -1.0) {
        return 0.0; // Практично нульові втрати при великому просвіті
    }
    
    double v_minus_01 = v - 0.1;
    double term = sqrt(v_minus_01 * v_minus_01 + 1.0) + v_minus_01;
    if (term <= 0.0) return 0.0;
    
    double loss = 6.9 + 20.0 * log10(term);
    return loss < 0.0 ? 0.0 : loss;
}

// Функція розрахунку просвіту траси для однієї точки
TraceAnalysisResult analyze_trace_point(
    double d_total_km,
    double d1_km,
    double f_ghz,
    double h_tx_m,
    double h_rx_m,
    double h_obs_m,
    double k_factor
) {
    TraceAnalysisResult res;
    double d2_km = d_total_km - d1_km;

    // 1. Радіус першої зони Френеля
    res.r1_meters = 17.32 * sqrt((d1_km * d2_km) / (f_ghz * d_total_km));

    // 2. Опуклість Землі (еквівалентний радіус R_eq = k * 6371 км)
    res.earth_bulge_m = (d1_km * d2_km) / (12.74 * k_factor);

    // 3. Висота прямого променя LOS над землею в точці перешкоди
    res.los_height_m = h_tx_m + (h_rx_m - h_tx_m) * (d1_km / d_total_km);

    // 4. Загальна ефективна висота перешкоди з урахуванням опуклості Землі
    double total_obs_height = h_obs_m + res.earth_bulge_m;

    // 5. Просвіт траси та відносний коефіцієнт
    res.clearance_m = res.los_height_m - total_obs_height;
    res.clearance_ratio = res.clearance_m / res.r1_meters;

    // 6. Перевірка критерію 0.6 * R1
    res.is_clear = (res.clearance_ratio >= 0.6);

    // 7. Розрахунок втрат
    res.diff_loss_db = calculate_knife_edge_loss(res.clearance_ratio);

    return res;
}

int main(void) {
    // Приклад: траса 10 км на частоті 5 ГГц, перешкода на 4-му кілометрі
    double d_total = 10.0;
    double d1 = 4.0;
    double f_ghz = 5.0;
    double h_tx = 25.0;
    double h_rx = 25.0;
    double h_obs = 18.0;
    double k_factor = 1.333; // Стандартна атмосфера (4/3)

    TraceAnalysisResult r = analyze_trace_point(d_total, d1, f_ghz, h_tx, h_rx, h_obs, k_factor);

    printf("=== Аналіз просвіту радіолінії (C) ===\n");
    printf("Відстань: %.1f км (d1=%.1f км, d2=%.1f км), Частота: %.2f ГГц\n", d_total, d1, d_total - d1, f_ghz);
    printf("Радіус 1-ї зони Френеля R1: %.2f м\n", r.r1_meters);
    printf("Опуклість Землі (k=%.2f):   %.2f м\n", k_factor, r.earth_bulge_m);
    printf("Висота променя LOS:        %.2f м\n", r.los_height_m);
    printf("Наявний просвіт:           %.2f м (%.1f%% від R1)\n", r.clearance_m, r.clearance_ratio * 100.0);
    printf("Дифракційні втрати:        %.2f дБ\n", r.diff_loss_db);
    printf("Статус просвіту:           %s\n", r.is_clear ? "ВІДКРИТА (OK)" : "ЗАКРИТА (Втрати)");

    return 0;
}

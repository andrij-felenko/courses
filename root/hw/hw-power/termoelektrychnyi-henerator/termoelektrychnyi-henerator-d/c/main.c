#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Фізичні та конструктивні параметри ТЕГ модуля
typedef struct {
    int couples;              // Кількість пар термопар
    double seebeck_couple;    // Коефіцієнт Зеєбека пари (В/К)
    double r_internal;        // Внутрішній електричний опір (Ом)
    double theta_module;      // Тепловий опір модуля (К/Вт)
    double theta_hot_contact; // Тепловий опір гарячої пасти/прокладки (К/Вт)
    double theta_heatsink;    // Тепловий опір радіатора (К/Вт)
} TegSpecs;

// Результат статичного розрахунку робочої точки
typedef struct {
    double q_heat_flow_w;     // Тепловий потік крізь систему (Вт)
    double delta_t_module_k;  // Корисний перепад на кристалі ТЕГ (К)
    double v_open_circuit_v;  // Напруга холостого ходу (В)
    double v_mpp_v;           // Напруга в точці MPP (В)
    double i_mpp_a;           // Струм в точці MPP (А)
    double p_max_w;           // Максимальна електрична потужність (Вт)
    double efficiency_pct;    // Реальний системний ККД (%)
} TegOperatingPoint;

bool teg_calculate_operating_point(const TegSpecs *specs, double t_source_c, 
                                   double t_ambient_c, TegOperatingPoint *out) {
    if (!specs || !out) return false;

    const double delta_t_system = t_source_c - t_ambient_c;
    if (delta_t_system <= 0.0) {
        // Немає позитивного градієнта
        out->q_heat_flow_w = 0.0;
        out->delta_t_module_k = 0.0;
        out->v_open_circuit_v = 0.0;
        out->v_mpp_v = 0.0;
        out->i_mpp_a = 0.0;
        out->p_max_w = 0.0;
        out->efficiency_pct = 0.0;
        return true;
    }

    // 1. Повний тепловий опір ланцюга
    const double theta_total = specs->theta_hot_contact + 
                               specs->theta_module + 
                               specs->theta_heatsink;

    // 2. Тепловий потік та корисний градієнт
    out->q_heat_flow_w = delta_t_system / theta_total;
    out->delta_t_module_k = out->q_heat_flow_w * specs->theta_module;

    // 3. Електричні параметри Тевеніна
    const double s_module = specs->couples * specs->seebeck_couple;
    out->v_open_circuit_v = s_module * out->delta_t_module_k;

    // 4. Точка максимальної потужності (MPP)
    out->v_mpp_v = out->v_open_circuit_v / 2.0;
    out->i_mpp_a = out->v_mpp_v / specs->r_internal;
    out->p_max_w = (out->v_open_circuit_v * out->v_open_circuit_v) / (4.0 * specs->r_internal);

    // 5. Системний ККД перетворення
    if (out->q_heat_flow_w > 0.0) {
        out->efficiency_pct = (out->p_max_w / out->q_heat_flow_w) * 100.0;
    } else {
        out->efficiency_pct = 0.0;
    }

    return true;
}

#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Базові константи міді та діелектрика */
#define COPPER_RHO_20C_OHM_MM   1.72e-5  /* Питомий опір міді при 20 °C (Ом·мм) */
#define COPPER_TCR_PER_C        0.00393  /* Температурний коефіцієнт опору (1/°C) */
#define MILS_PER_MM             39.3701  /* Коефіцієнт переведення мм у mils */

/* Товщина мідної фольги у міліметрах за вагою в унціях (oz) */
#define FOIL_THICKNESS_0_5_OZ   0.0175   /* 0.5 oz ≈ 17.5 мкм */
#define FOIL_THICKNESS_1_0_OZ   0.0350   /* 1.0 oz ≈ 35.0 мкм */
#define FOIL_THICKNESS_2_0_OZ   0.0700   /* 2.0 oz ≈ 70.0 мкм */

typedef enum {
    LAYER_EXTERNAL = 0,  /* Зовнішній шар (Top / Bottom) */
    LAYER_INTERNAL = 1   /* Внутрішній шар (Inner 1 / Inner 2) */
} pcb_layer_type_t;

typedef struct {
    double current_amps;         /* Робочий постійний струм (А) */
    double temp_rise_c;          /* Допустимий перегрів Delta_T (°C) */
    double ambient_temp_c;       /* Температура довкілля (°C) */
    double copper_oz;            /* Вага міді (0.5, 1.0, 2.0 oz) */
    pcb_layer_type_t layer;      /* Тип шару */
    double trace_length_mm;      /* Довжина провідника (мм) */
} pcb_trace_params_t;

typedef struct {
    double drill_diam_mm;        /* Діаметр свердла via (мм) */
    double plating_thickness_mm; /* Товщина стінки металізації (мм, типово 0.025) */
    double board_thickness_mm;   /* Повна товщина плати (мм, типово 1.6) */
    double max_current_per_via;  /* Допустимий струм на 1 via (А, типово 1.5–2.0) */
} pcb_via_params_t;

typedef struct {
    double required_width_mm;    /* Розрахункова ширина доріжки (мм) */
    double required_width_mils;  /* Розрахункова ширина доріжки (mils) */
    double trace_resistance_ohm; /* Опір доріжки при робочій температурі (Ом) */
    double voltage_drop_trace_v; /* Падіння напруги на доріжці (В) */
    double power_loss_trace_w;   /* Втрати потужності на доріжці (Вт) */
    int    required_via_count;   /* Мінімальна кількість via у матриці */
    double via_array_res_ohm;    /* Сумарний опір матриці via (Ом) */
    double voltage_drop_vias_v;  /* Падіння напруги на матриці via (В) */
    double total_voltage_drop_v; /* Загальне падіння напруги (В) */
    double total_power_loss_w;   /* Загальні теплові втрати (Вт) */
} pcb_power_calc_result_t;

/* Розрахунок площі перерізу та ширини за формулами IPC-2152 */
bool calculate_pcb_power_rail(const pcb_trace_params_t* trace,
                              const pcb_via_params_t* via,
                              pcb_power_calc_result_t* result)
{
    if (!trace || !via || !result || trace->current_amps <= 0.0 || trace->temp_rise_c <= 0.0) {
        return false;
    }

    /* Коефіцієнти емпіричної моделі IPC-2152: I = k * (Delta_T)^b * (Area_mils2)^c */
    double k = (trace->layer == LAYER_EXTERNAL) ? 0.048 : 0.024;
    double b = 0.44;
    double c = 0.725;

    /* Площа поперечного перерізу в mils²: Area = (I / (k * Delta_T^b))^(1/c) */
    double area_mils2 = pow(trace->current_amps / (k * pow(trace->temp_rise_c, b)), 1.0 / c);
    double area_mm2 = area_mils2 / (MILS_PER_MM * MILS_PER_MM);

    /* Товщина міді у міліметрах */
    double thickness_mm = trace->copper_oz * FOIL_THICKNESS_1_0_OZ;
    result->required_width_mm = area_mm2 / thickness_mm;
    result->required_width_mils = result->required_width_mm * MILS_PER_MM;

    /* Робоча температура провідника */
    double operating_temp_c = trace->ambient_temp_c + trace->temp_rise_c;
    double temp_delta = operating_temp_c - 20.0;
    double rho_operating = COPPER_RHO_20C_OHM_MM * (1.0 + COPPER_TCR_PER_C * temp_delta);

    /* Електричний опір доріжки */
    result->trace_resistance_ohm = (rho_operating * trace->trace_length_mm) / area_mm2;
    result->voltage_drop_trace_v = trace->current_amps * result->trace_resistance_ohm;
    result->power_loss_trace_w = trace->current_amps * result->voltage_drop_trace_v;

    /* Розрахунок параметрів перехідного отвору */
    double d_drill = via->drill_diam_mm;
    double t_wall = via->plating_thickness_mm;
    double a_via_mm2 = 3.141592653589793 * t_wall * (d_drill - t_wall);

    /* Опір одиничного via при робочій температурі */
    double r_single_via = (rho_operating * via->board_thickness_mm) / a_via_mm2;

    /* Кількість via з урахуванням допустимого струму на один отвір */
    int n_vias = (int)ceil(trace->current_amps / via->max_current_per_via);
    if (n_vias < 1) n_vias = 1;
    result->required_via_count = n_vias;

    /* Паралельний опір матриці via */
    result->via_array_res_ohm = r_single_via / (double)n_vias;
    result->voltage_drop_vias_v = trace->current_amps * result->via_array_res_ohm;

    /* Загальні втрати на всій силовій ланці */
    result->total_voltage_drop_v = result->voltage_drop_trace_v + result->voltage_drop_vias_v;
    result->total_power_loss_w = result->power_loss_trace_w + (trace->current_amps * result->voltage_drop_vias_v);

    return true;
}

int main(void)
{
    pcb_trace_params_t trace = {
        .current_amps = 15.0,
        .temp_rise_c = 20.0,
        .ambient_temp_c = 25.0,
        .copper_oz = 1.0,
        .layer = LAYER_EXTERNAL,
        .trace_length_mm = 60.0
    };

    pcb_via_params_t via = {
        .drill_diam_mm = 0.3,
        .plating_thickness_mm = 0.025,
        .board_thickness_mm = 1.6,
        .max_current_per_via = 1.8
    };

    pcb_power_calc_result_t res;
    if (calculate_pcb_power_rail(&trace, &via, &res)) {
        printf("=== Результати розрахунку силової шини PCB ===\n");
        printf("Струм: %.1f А, Допустимий перегрів: %.1f °C (T_max = %.1f °C)\n",
               trace.current_amps, trace.temp_rise_c, trace.ambient_temp_c + trace.temp_rise_c);
        printf("Необхідна ширина доріжки: %.2f мм (%.1f mils)\n",
               res.required_width_mm, res.required_width_mils);
        printf("Опір доріжки (L = %.0f мм): %.3f мОм\n",
               trace.trace_length_mm, res.trace_resistance_ohm * 1000.0);
        printf("Падіння напруги на доріжці: %.2f мВ, втрати: %.3f Вт\n",
               res.voltage_drop_trace_v * 1000.0, res.power_loss_trace_w);
        printf("Матриця Stitching Vias: %d шт (R_array = %.3f мОм)\n",
               res.required_via_count, res.via_array_res_ohm * 1000.0);
        printf("Сумарне падіння напруги: %.2f мВ\n", res.total_voltage_drop_v * 1000.0);
        printf("Сумарна розсіювана потужність: %.3f Вт\n", res.total_power_loss_w);
    }

    return 0;
}

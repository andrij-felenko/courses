#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define RHO_CU_20C   1.7241e-8   /* Питомий опір міді при 20 °C (Ом·м) */
#define ALPHA_CU     0.00393     /* Температурний коефіцієнт опору міді (1/K) */
#define MIL_TO_MM    0.0254      /* 1 mil = 0.0254 мм */
#define MM_TO_MIL    39.3700787  /* 1 мм = 39.3701 mil */

typedef struct {
    double current_amps;         /* Струм навантаження (А) */
    double temp_rise_c;          /* Допустимий перегрів Delta T (°C) */
    double ambient_temp_c;       /* Температура довкілля (°C) */
    double copper_thickness_oz;  /* Товщина міді (oz, де 1 oz = 35 мкм) */
    double trace_length_mm;      /* Довжина провідника (мм) */
    bool   is_internal;          /* Внутрішній шар (true) чи зовнішній (false) */
    bool   has_ground_plane;     /* Наявність суцільного екрану GND поруч */
} trace_input_t;

typedef struct {
    double width_ipc2221_mm;     /* Ширина за IPC-2221 (мм) */
    double width_ipc2152_mm;     /* Ширина за IPC-2152 (мм) */
    double area_mm2;             /* Площа перерізу (мм²) */
    double resistance_cold_mohm; /* Холодний опір при 20 °C (мОм) */
    double resistance_hot_mohm;  /* Гарячий опір при робочій температурі (мОм) */
    double voltage_drop_mv;      /* Падіння напруги (мВ) */
    double power_loss_watts;     /* Втрати потужності (Вт) */
    int    min_vias_03mm;        /* Мінімальна кількість отворів d=0.3 мм */
} trace_result_t;

trace_result_t calculate_power_trace(const trace_input_t* in) {
    trace_result_t res;
    double t_mils = in->copper_thickness_oz * 1.378; /* Товщина міді в mils */
    double t_mm = in->copper_thickness_oz * 0.035;   /* Товщина міді в мм */
    
    /* 1. Розрахунок за IPC-2221A */
    double k = in->is_internal ? 0.024 : 0.048;
    double b = 0.44;
    double c = 0.725;
    
    /* Area_mils2 = (I / (k * DeltaT^b))^(1 / c) */
    double area_mils2 = pow(in->current_amps / (k * pow(in->temp_rise_c, b)), 1.0 / c);
    double width_mils = area_mils2 / t_mils;
    res.width_ipc2221_mm = width_mils * MIL_TO_MM;
    
    /* 2. Розрахунок за моделлю IPC-2152 з модифікаторами */
    double m_plane = in->has_ground_plane ? 1.35 : 1.00;
    double m_thick = 1.00; /* Стандартна плата 1.6 мм */
    double m_cu = (in->copper_thickness_oz <= 1.0) ? 1.08 : 1.00;
    double total_derating = m_plane * m_thick * m_cu;
    
    /* Зменшуємо необхідну площу завдяки кращому розсіюванню */
    double area_2152_mils2 = area_mils2 / pow(total_derating, 1.0 / c);
    if (in->is_internal && in->has_ground_plane) {
        /* Внутрішній шар з двома екранами GND охолоджується краще за ізольований */
        area_2152_mils2 *= 0.65;
    }
    res.width_ipc2152_mm = (area_2152_mils2 / t_mils) * MIL_TO_MM;
    
    /* Фізичні параметри (беремо за основу геометрію IPC-2152) */
    res.area_mm2 = res.width_ipc2152_mm * t_mm;
    double length_m = in->trace_length_mm / 1000.0;
    double area_m2 = res.area_mm2 * 1e-6;
    
    /* Опори: холодний та гарячий */
    double r_cold = RHO_CU_20C * (length_m / area_m2);
    double t_hot = in->ambient_temp_c + in->temp_rise_c;
    double r_hot = r_cold * (1.0 + ALPHA_CU * (t_hot - 20.0));
    
    res.resistance_cold_mohm = r_cold * 1000.0;
    res.resistance_hot_mohm = r_hot * 1000.0;
    res.voltage_drop_mv = in->current_amps * res.resistance_hot_mohm;
    res.power_loss_watts = in->current_amps * in->current_amps * r_hot;
    
    /* Отвори: розрахунок з ліміту 1.5 А на отвір d=0.3 мм */
    res.min_vias_03mm = (int)ceil(in->current_amps / 1.5);
    if (res.min_vias_03mm < 1) res.min_vias_03mm = 1;
    
    return res;
}

int main(void) {
    trace_input_t input = {
        .current_amps = 15.0,
        .temp_rise_c = 20.0,
        .ambient_temp_c = 25.0,
        .copper_thickness_oz = 1.0,
        .trace_length_mm = 100.0,
        .is_internal = false,
        .has_ground_plane = true
    };
    
    trace_result_t res = calculate_power_trace(&input);
    
    printf("=== Результати розрахунку силового провідника ===\n");
    printf("Струм: %.1f A, Допустимий перегрів: %.1f °C, Фольга: %.1f oz\n",
           input.current_amps, input.temp_rise_c, input.copper_thickness_oz);
    printf("Ширина за IPC-2221: %.2f мм\n", res.width_ipc2221_mm);
    printf("Ширина за IPC-2152 (з полігоном GND): %.2f мм\n", res.width_ipc2152_mm);
    printf("Гарячий опір (при 45 °C): %.2f мОм\n", res.resistance_hot_mohm);
    printf("Падіння напруги: %.2f мВ\n", res.voltage_drop_mv);
    printf("Дисипація потужності: %.2f Вт\n", res.power_loss_watts);
    printf("Мінімальна кількість переходів (d=0.3 мм): %d шт\n", res.min_vias_03mm);
    
    return 0;
}

#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define COPPER_RHO_20C      1.724e-8   /* Ом * м (питомий опір міді за 20 °C) */
#define COPPER_ALPHA_20C    0.00393    /* 1 / °C (ТКО міді) */
#define COPPER_K_CU         5.091e4    /* А^2 * с / мм^4 (константа плавлення) */

typedef enum {
    ELEM_CONNECTOR,
    ELEM_TRACE,
    ELEM_VIA_ARRAY,
    ELEM_MOSFET,
    ELEM_FUSE,
    ELEM_SHUNT
} ElementType;

typedef struct {
    const char *name;
    ElementType type;
    
    /* Базові електричні параметри */
    double nominal_resistance_ohm; /* Опір за 20 °C */
    double temp_coefficient;       /* ТКО (1/°C) */
    
    /* Геометричні параметри для доріжок (тип ELEM_TRACE) */
    double length_mm;
    double width_mm;
    double thickness_um;           /* наприклад, 35 мкм для 1 oz, 70 мкм для 2 oz */
    bool has_ground_plane;         /* наявність опорного полігону (IPC-2152) */
    
    /* Параметри via-масиву (тип ELEM_VIA_ARRAY) */
    int via_count;
    double drill_diameter_mm;
    double plating_thickness_um;
    
    /* Параметри MOSFET (тип ELEM_MOSFET) */
    double r_th_ja;                /* Тепловий опір кристал-довкілля (°C/Вт) */
    
    /* Захисні характеристики */
    double i2t_rating_a2s;         /* I^2 * t елемента */
    
    /* Результати розрахунку (заповнюються рушієм) */
    double op_resistance_ohm;
    double voltage_drop_v;
    double power_loss_w;
    double temp_rise_c;
    double final_temp_c;
    bool is_safe;
} PowerElement;

typedef struct {
    double v_source_nom;
    double v_source_min;
    double i_load_continuous;
    double i_load_peak;
    double t_ambient_c;
    double v_uvlo_threshold;
    
    PowerElement *elements;
    size_t element_count;
    
    /* Підсумки аудиту */
    double total_resistance_nom;
    double total_resistance_hot;
    double total_v_drop_cont;
    double total_v_drop_peak;
    double v_load_min_worst_case;
    double total_power_dissipated_w;
    bool system_pass;
} PowerPathAudit;

/* Розрахунок опору мідної доріжки за 20 °C */
double calc_trace_resistance_20c(double length_mm, double width_mm, double thickness_um) {
    double length_m = length_mm * 1e-3;
    double area_m2 = (width_mm * 1e-3) * (thickness_um * 1e-6);
    if (area_m2 <= 0.0) return 0.0;
    return COPPER_RHO_20C * (length_m / area_m2);
}

/* Розрахунок опору масиву перехідних отворів за 20 °C */
double calc_via_array_resistance_20c(int count, double drill_diam_mm, double plating_um, double board_thickness_mm) {
    if (count <= 0 || drill_diam_mm <= 0.0 || plating_um <= 0.0) return 0.0;
    
    /* Площа мідного кільця стінки via: A ≈ pi * d_drill * t_plating */
    double mean_diam_m = (drill_diam_mm - plating_um * 1e-3) * 1e-3;
    double wall_area_m2 = M_PI * mean_diam_m * (plating_um * 1e-6);
    double single_via_r = COPPER_RHO_20C * (board_thickness_mm * 1e-3 / wall_area_m2);
    
    return single_via_r / (double)count;
}

/* Оцінка перегріву доріжки за моделлю IPC-2152 */
double calc_trace_temp_rise_ipc2152(double current, double width_mm, double thickness_um, bool has_plane) {
    double area_mm2 = width_mm * (thickness_um * 1e-3);
    if (area_mm2 <= 0.0) return 999.0;
    
    /* 
     * Метрична апроксимація IPC-2152 для плати з опорною площиною заземлення:
     * Delta_T = [ I / (k * A^0.725) ]^(1 / 0.44)
     * Для плати з полігоном GND ефективне відведення покращується в 1.6..2.0 раза.
     */
    double k = has_plane ? 14.5 : 9.95;
    double term = current / (k * pow(area_mm2, 0.725));
    if (term <= 0.0) return 0.0;
    return pow(term, 1.0 / 0.44);
}

/* Виконання аудиту силового тракту */
bool run_power_path_audit(PowerPathAudit *audit) {
    audit->total_resistance_nom = 0.0;
    audit->total_resistance_hot = 0.0;
    audit->total_power_dissipated_w = 0.0;
    audit->system_pass = true;
    
    for (size_t i = 0; i < audit->element_count; i++) {
        PowerElement *e = &audit->elements[i];
        
        /* 1. Визначення базового опору за 20 °C */
        if (e->type == ELEM_TRACE) {
            e->nominal_resistance_ohm = calc_trace_resistance_20c(e->length_mm, e->width_mm, e->thickness_um);
            e->temp_coefficient = COPPER_ALPHA_20C;
        } else if (e->type == ELEM_VIA_ARRAY) {
            e->nominal_resistance_ohm = calc_via_array_resistance_20c(e->via_count, e->drill_diameter_mm, e->plating_thickness_um, 1.6);
            e->temp_coefficient = COPPER_ALPHA_20C;
        }
        
        /* 2. Тепловий розрахунок для тривалого струму */
        double current = audit->i_load_continuous;
        double p_est = current * current * e->nominal_resistance_ohm;
        
        if (e->type == ELEM_TRACE) {
            e->temp_rise_c = calc_trace_temp_rise_ipc2152(current, e->width_mm, e->thickness_um, e->has_ground_plane);
        } else if (e->type == ELEM_MOSFET && e->r_th_ja > 0.0) {
            e->temp_rise_c = p_est * e->r_th_ja;
        } else {
            /* Спрощена оцінка для пасивних дискретних компонентів */
            e->temp_rise_c = p_est * 15.0; 
        }
        
        e->final_temp_c = audit->t_ambient_c + e->temp_rise_c;
        
        /* 3. Корекція опору за робочої температури */
        double delta_t_from_20c = e->final_temp_c - 20.0;
        e->op_resistance_ohm = e->nominal_resistance_ohm * (1.0 + e->temp_coefficient * delta_t_from_20c);
        
        /* 4. Втрати потужності та спад напруги */
        e->voltage_drop_v = current * e->op_resistance_ohm;
        e->power_loss_w = current * current * e->op_resistance_ohm;
        
        /* 5. Перевірка безпеки та I^2*t */
        e->is_safe = true;
        if (e->final_temp_c > 105.0) {
            e->is_safe = false; /* Перевищення допустимої температури FR-4 */
        }
        
        if (e->type == ELEM_TRACE) {
            double area_mm2 = e->width_mm * (e->thickness_um * 1e-3);
            double ln_term = log((1.0 + COPPER_ALPHA_20C * (150.0 - 20.0)) / (1.0 + COPPER_ALPHA_20C * (e->final_temp_c - 20.0)));
            double i2t_trace_limit = COPPER_K_CU * area_mm2 * area_mm2 * ln_term;
            
            /* Порівнюємо із захисним запобіжником (якщо є в ланцюзі) */
            for (size_t j = 0; j < audit->element_count; j++) {
                if (audit->elements[j].type == ELEM_FUSE && audit->elements[j].i2t_rating_a2s > 0.0) {
                    if (audit->elements[j].i2t_rating_a2s >= i2t_trace_limit) {
                        e->is_safe = false; /* Запобіжник не захищає цю доріжку від випаровування */
                    }
                }
            }
        }
        
        if (!e->is_safe) {
            audit->system_pass = false;
        }
        
        audit->total_resistance_nom += e->nominal_resistance_ohm;
        audit->total_resistance_hot += e->op_resistance_ohm;
        audit->total_power_dissipated_w += e->power_loss_w;
    }
    
    audit->total_v_drop_cont = audit->i_load_continuous * audit->total_resistance_hot;
    audit->total_v_drop_peak = audit->i_load_peak * audit->total_resistance_hot;
    audit->v_load_min_worst_case = audit->v_source_min - audit->total_v_drop_peak;
    
    if (audit->v_load_min_worst_case < audit->v_uvlo_threshold) {
        audit->system_pass = false; /* Ризик перезавантаження системи від просідання живлення */
    }
    
    return audit->system_pass;
}

void print_power_path_report(const PowerPathAudit *audit) {
    printf("================================================================================\n");
    printf("                  ЗВІТ НАСКРІЗНОГО АУДИТУ СИЛОВОГО ТРАКТУ                       \n");
    printf("================================================================================\n");
    printf("Джерело: %.2f В (мін: %.2f В) | Струм: %.2f А (пік: %.2f А) | T_amb: %.1f °C\n",
           audit->v_source_nom, audit->v_source_min, audit->i_load_continuous, audit->i_load_peak, audit->t_ambient_c);
    printf("--------------------------------------------------------------------------------\n");
    printf("%-20s | %-8s | %-8s | %-8s | %-8s | %-6s\n",
           "Елемент", "R_hot,мОм", "Drop_V", "P_loss,Вт", "T_fin,°C", "Стан");
    printf("--------------------------------------------------------------------------------\n");
    
    for (size_t i = 0; i < audit->element_count; i++) {
        const PowerElement *e = &audit->elements[i];
        printf("%-20s | %8.2f | %8.3f | %8.3f | %8.1f | %-6s\n",
               e->name,
               e->op_resistance_ohm * 1e3,
               e->voltage_drop_v,
               e->power_loss_w,
               e->final_temp_c,
               e->is_safe ? "OK" : "DEFECT");
    }
    printf("--------------------------------------------------------------------------------\n");
    printf("Загальний опір тракту (гарячий):  %.2f мОм\n", audit->total_resistance_hot * 1e3);
    printf("Сумарне падіння напруги (номінал): %.3f В\n", audit->total_v_drop_cont);
    printf("Сумарне падіння напруги (пік):     %.3f В\n", audit->total_v_drop_peak);
    printf("Мінімальна напруга на навантаженні:%.3f В (Поріг UVLO: %.2f В)\n",
           audit->v_load_min_worst_case, audit->v_uvlo_threshold);
    printf("Загальні теплові втрати шини:      %.2f Вт\n", audit->total_power_dissipated_w);
    printf("Підсумковий вердикт:               %s\n",
           audit->system_pass ? "СИСТЕМА ВІДПОВІДАЄ НОРМАМ" : "ПОМИЛКА: ПОТРІБЕН РЕДИЗАЙН");
    printf("================================================================================\n");
}

int main(void) {
    PowerElement elements[] = {
        { .name = "XT30 Роз'єм",       .type = ELEM_CONNECTOR, .nominal_resistance_ohm = 0.005,  .temp_coefficient = 0.002 },
        { .name = "SMD Запобіжник 7A", .type = ELEM_FUSE,      .nominal_resistance_ohm = 0.015,  .temp_coefficient = 0.001, .i2t_rating_a2s = 18.0 },
        { .name = "P-MOS FET Захист",  .type = ELEM_MOSFET,    .nominal_resistance_ohm = 0.008,  .temp_coefficient = 0.006, .r_th_ja = 45.0 },
        { .name = "Шина живлення (2oz)",.type = ELEM_TRACE,     .length_mm = 80.0, .width_mm = 4.0, .thickness_um = 70.0, .has_ground_plane = true },
        { .name = "Масив переходів (4x)",.type = ELEM_VIA_ARRAY,.via_count = 4, .drill_diameter_mm = 0.4, .plating_thickness_um = 25.0 },
        { .name = "Вимірювальний шунт", .type = ELEM_SHUNT,     .nominal_resistance_ohm = 0.010,  .temp_coefficient = 0.0001 }
    };
    
    PowerPathAudit audit = {
        .v_source_nom = 24.0,
        .v_source_min = 18.0,
        .i_load_continuous = 5.0,
        .i_load_peak = 10.0,
        .t_ambient_c = 55.0,
        .v_uvlo_threshold = 17.0,
        .elements = elements,
        .element_count = sizeof(elements) / sizeof(elements[0])
    };
    
    run_power_path_audit(&audit);
    print_power_path_report(&audit);
    return 0;
}

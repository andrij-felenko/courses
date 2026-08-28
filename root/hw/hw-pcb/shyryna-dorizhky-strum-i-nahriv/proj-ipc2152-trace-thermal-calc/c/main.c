#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* ============================================================================
 * Фізичні константи та параметри матеріалів (IPC-2152 / IACS)
 * ============================================================================ */
#define IPC_RHO_CU_20C         1.7241e-8   /* Питомий опір міді при 20 °C (Ом·м) */
#define IPC_ALPHA_CU           0.00393     /* Температурний коефіцієнт опору (1/K) */
#define IPC_CU_DENSITY_KG_M3   8960.0      /* Густина міді (кг/м³) */
#define IPC_CU_SPEC_HEAT_J_KGK 385.0       /* Питома теплоємність міді (Дж/(кг·К)) */
#define IPC_OZ_TO_MM           0.0348      /* Товщина фольги 1 oz у міліметрах */
#define IPC_MIL_TO_MM          0.0254
#define IPC_MM_TO_MIL          39.3700787

/* Константи апроксимації базової кривої IPC-2152 (універсальний вакуумний baseline) */
#define IPC2152_K_BASE         0.0645
#define IPC2152_P_AREA         0.695
#define IPC2152_P_TEMP         0.435

/* Коди статусу виконання розрахунку */
typedef enum {
    IPC_STATUS_OK = 0,
    IPC_STATUS_ERR_INVALID_CURRENT,
    IPC_STATUS_ERR_INVALID_TEMP_RISE,
    IPC_STATUS_ERR_INVALID_COPPER_THICKNESS,
    IPC_STATUS_ERR_NON_CONVERGENCE
} ipc_status_t;

/* Режими охолодження друкованої плати */
typedef enum {
    IPC_COOLING_STILL_AIR_ENCLOSED = 0,  /* Вільна конвекція у закритому корпусі */
    IPC_COOLING_NATURAL_OPEN,            /* Вільна конвекція у відкритому просторі */
    IPC_COOLING_FORCED_AIR_1MS,          /* Примусовий обдув 1.0 м/с */
    IPC_COOLING_FORCED_AIR_2_5MS,        /* Примусовий обдув 2.5 м/с */
    IPC_COOLING_VACUUM                   /* Вакуумне середовище (космос) */
} ipc_cooling_t;

/* Структура вхідних даних для теплового розрахунку */
typedef struct {
    double        current_a;             /* Струм навантаження (Ампери) */
    double        temp_rise_c;           /* Допустимий перегрів Delta T (°C) */
    double        ambient_temp_c;        /* Температура навколишнього середовища (°C) */
    double        copper_oz;             /* Товщина мідної фольги (унції, 1 oz = 35 мкм) */
    double        trace_length_mm;       /* Довжина провідника (мм) */
    double        board_thickness_mm;    /* Загальна товщина друкованої плати (мм) */
    double        distance_to_plane_mm;  /* Відстань до найближчого мідного екрану GND (мм) */
    bool          is_internal;           /* Внутрішній шар (true) чи зовнішній (false) */
    bool          has_ground_plane;      /* Наявність суцільного полігону заземлення поруч */
    ipc_cooling_t cooling_mode;          /* Режим охолодження довкілля */
} ipc_calc_params_t;

/* Структура вихідних інженерних результатів */
typedef struct {
    double width_ipc2152_mm;             /* Розрахована ширина за стандартом IPC-2152 (мм) */
    double width_ipc2152_mils;           /* Розрахована ширина за стандартом IPC-2152 (mils) */
    double width_ipc2221_mm;             /* Порівняльна ширина за старим IPC-2221A (мм) */
    double area_mm2;                     /* Площа поперечного перерізу міді (мм²) */
    double current_density_a_mm2;        /* Фактична густина струму в провіднику (А/мм²) */
    double r_cold_mohm;                  /* Холодний опір лінії при 20 °C (мОм) */
    double r_hot_mohm;                   /* Гарячий опір лінії при робочій температурі (мОм) */
    double voltage_drop_mv;              /* Падіння напруги на всій довжині лінії (мВ) */
    double power_loss_w;                 /* Потужність джоулевих втрат тепла (Вт) */
    double joule_integral_i2t;           /* Тепловий інтеграл імпульсу 10 мс I²t (А²·с) */
    int    min_vias_03mm;                /* Мінімальна кількість отворів d=0.3 мм у матриці */
    int    min_vias_05mm;                /* Мінімальна кількість отворів d=0.5 мм у матриці */
} ipc_calc_result_t;

/* Обчислення комплексного коефіцієнта модифікаторів середовища */
static double calculate_total_derating(const ipc_calc_params_t* p) {
    /* 1. Модифікатор товщини діелектрика плати */
    double h = (p->board_thickness_mm > 0.4) ? p->board_thickness_mm : 1.6;
    double m_thick = pow(h / 1.6, 0.125);

    /* 2. Модифікатор близькості суцільного мідного полігону */
    double m_plane = 1.00;
    if (p->has_ground_plane) {
        double d = (p->distance_to_plane_mm > 0.05) ? p->distance_to_plane_mm : 0.20;
        if (p->is_internal) {
            m_plane = 1.00 + 0.80 * exp(-d / 0.35);
        } else {
            m_plane = 1.00 + 0.50 * exp(-d / 0.35);
        }
    }

    /* 3. Модифікатор геометричного співвідношення сторін фольги */
    double oz = (p->copper_oz > 0.1) ? p->copper_oz : 1.0;
    double m_cu = 1.05 - 0.05 * (log(oz) / log(2.0));
    if (m_cu < 0.90) m_cu = 0.90;
    if (m_cu > 1.15) m_cu = 1.15;

    /* 4. Модифікатор умов охолодження навколишнього середовища */
    double m_env = 1.00;
    switch (p->cooling_mode) {
        case IPC_COOLING_STILL_AIR_ENCLOSED: m_env = 1.00; break;
        case IPC_COOLING_NATURAL_OPEN:       m_env = 1.15; break;
        case IPC_COOLING_FORCED_AIR_1MS:     m_env = 1.45; break;
        case IPC_COOLING_FORCED_AIR_2_5MS:   m_env = 1.85; break;
        case IPC_COOLING_VACUUM:             m_env = 0.70; break;
    }

    return m_thick * m_plane * m_cu * m_env;
}

/* Основна розрахункова функція бібліотеки */
ipc_status_t ipc2152_calculate_trace(const ipc_calc_params_t* p, ipc_calc_result_t* out) {
    if (!p || !out) return IPC_STATUS_ERR_INVALID_CURRENT;
    if (p->current_a <= 0.001) return IPC_STATUS_ERR_INVALID_CURRENT;
    if (p->temp_rise_c < 0.5 || p->temp_rise_c > 150.0) return IPC_STATUS_ERR_INVALID_TEMP_RISE;
    if (p->copper_oz < 0.1 || p->copper_oz > 12.0) return IPC_STATUS_ERR_INVALID_COPPER_THICKNESS;

    double t_cu_mm = p->copper_oz * IPC_OZ_TO_MM;
    double t_cu_mils = p->copper_oz * 1.378;
    double total_derating = calculate_total_derating(p);

    /* Ітераційний пошук площі перерізу методом Ньютона-Рафсона */
    double area = 0.10; /* Початкове наближення площі 0.1 мм² */
    bool converged = false;

    for (int iter = 0; iter < 50; ++iter) {
        /* Обчислюємо модельний струм за поточної площі */
        double i_model = IPC2152_K_BASE * pow(area, IPC2152_P_AREA) *
                         pow(p->temp_rise_c, IPC2152_P_TEMP) * total_derating;
        double f_val = i_model - p->current_a;

        if (fabs(f_val) < 1e-6) {
            converged = true;
            break;
        }

        /* Обчислюємо похідну dI/dA */
        double df_val = IPC2152_K_BASE * IPC2152_P_AREA * pow(area, IPC2152_P_AREA - 1.0) *
                        pow(p->temp_rise_c, IPC2152_P_TEMP) * total_derating;
        
        if (fabs(df_val) < 1e-12) break;

        double delta_a = f_val / df_val;
        area -= delta_a;

        /* Захист від від'ємних та нульових площ */
        if (area <= 1e-6) area = 1e-6;
    }

    if (!converged && area <= 1e-6) {
        return IPC_STATUS_ERR_NON_CONVERGENCE;
    }

    out->area_mm2 = area;
    /* Ширина з технологічною поправкою на трапецієподібне травлення (фактор 0.35) */
    out->width_ipc2152_mm = (area / t_cu_mm) + (0.35 * t_cu_mm);
    out->width_ipc2152_mils = out->width_ipc2152_mm * IPC_MM_TO_MIL;
    out->current_density_a_mm2 = p->current_a / area;

    /* Розрахунок за старою формулою IPC-2221A для порівняння */
    double k_2221 = p->is_internal ? 0.024 : 0.048;
    double area_2221_mils2 = pow(p->current_a / (k_2221 * pow(p->temp_rise_c, 0.44)), 1.0 / 0.725);
    out->width_ipc2221_mm = (area_2221_mils2 / t_cu_mils) * IPC_MIL_TO_MM;

    /* Електричні параметри та опір з температурною компенсацією */
    double len_m = (p->trace_length_mm > 0.1 ? p->trace_length_mm : 100.0) / 1000.0;
    double area_m2 = area * 1e-6;

    double r_20c = IPC_RHO_CU_20C * (len_m / area_m2);
    double t_final = p->ambient_temp_c + p->temp_rise_c;
    double r_hot = r_20c * (1.0 + IPC_ALPHA_CU * (t_final - 20.0));

    out->r_cold_mohm = r_20c * 1000.0;
    out->r_hot_mohm = r_hot * 1000.0;
    out->voltage_drop_mv = p->current_a * out->r_hot_mohm;
    out->power_loss_w = p->current_a * p->current_a * (out->r_hot_mohm / 1000.0);
    out->joule_integral_i2t = p->current_a * p->current_a * 0.010; /* Тепловий інтеграл на 10 мс */

    /* Розрахунок силових перехідних отворів (1.5 А на 0.3 мм та 3.0 А на 0.5 мм) */
    out->min_vias_03mm = (int)ceil(p->current_a / 1.50);
    out->min_vias_05mm = (int)ceil(p->current_a / 3.00);
    if (out->min_vias_03mm < 1) out->min_vias_03mm = 1;
    if (out->min_vias_05mm < 1) out->min_vias_05mm = 1;

    return IPC_STATUS_OK;
}

int main(void) {
    printf("=================================================================\n");
    printf("  ТЕСТУВАННЯ ТА ВЕРИФІКАЦІЯ КАЛЬКУЛЯТОРА IPC-2152 (C99)\n");
    printf("=================================================================\n\n");

    ipc_calc_params_t test_cases[] = {
        {
            .current_a = 5.0,
            .temp_rise_c = 20.0,
            .ambient_temp_c = 25.0,
            .copper_oz = 1.0,
            .trace_length_mm = 100.0,
            .board_thickness_mm = 1.6,
            .distance_to_plane_mm = 0.20,
            .is_internal = false,
            .has_ground_plane = true,
            .cooling_mode = IPC_COOLING_STILL_AIR_ENCLOSED
        },
        {
            .current_a = 15.0,
            .temp_rise_c = 30.0,
            .ambient_temp_c = 25.0,
            .copper_oz = 2.0,
            .trace_length_mm = 150.0,
            .board_thickness_mm = 1.6,
            .distance_to_plane_mm = 0.15,
            .is_internal = true,
            .has_ground_plane = true,
            .cooling_mode = IPC_COOLING_STILL_AIR_ENCLOSED
        },
        {
            .current_a = 30.0,
            .temp_rise_c = 40.0,
            .ambient_temp_c = 30.0,
            .copper_oz = 3.0,
            .trace_length_mm = 80.0,
            .board_thickness_mm = 2.4,
            .distance_to_plane_mm = 0.10,
            .is_internal = false,
            .has_ground_plane = true,
            .cooling_mode = IPC_COOLING_FORCED_AIR_1MS
        }
    };

    const char* names[] = {
        "Тест 1: 5 А, 1 oz, ΔT=20 °C, Зовнішній шар з GND екраном",
        "Тест 2: 15 А, 2 oz, ΔT=30 °C, Внутрішній силовий шар",
        "Тест 3: 30 А, 3 oz, ΔT=40 °C, Силова шина з обдувом 1.0 м/с"
    };

    for (size_t i = 0; i < 3; ++i) {
        ipc_calc_result_t res;
        ipc_status_t st = ipc2152_calculate_trace(&test_cases[i], &res);

        printf("--- %s ---\n", names[i]);
        if (st == IPC_STATUS_OK) {
            printf("  Ширина IPC-2152:           %6.2f мм (%6.1f mils)\n", res.width_ipc2152_mm, res.width_ipc2152_mils);
            printf("  Ширина IPC-2221 (стара):   %6.2f мм\n", res.width_ipc2221_mm);
            printf("  Площа перерізу:            %6.4f мм²\n", res.area_mm2);
            printf("  Густина струму:            %6.2f А/мм²\n", res.current_density_a_mm2);
            printf("  Гарячий опір лінії:        %6.2f мОм\n", res.r_hot_mohm);
            printf("  Падіння напруги:           %6.2f мВ\n", res.voltage_drop_mv);
            printf("  Дисипація тепла:           %6.2f Вт\n", res.power_loss_w);
            printf("  Матриця переходів (d=0.3): %2d шт  (або %2d шт d=0.5 мм)\n\n", res.min_vias_03mm, res.min_vias_05mm);
        } else {
            printf("  ПОМИЛКА РОЗРАХУНКУ: код %d\n\n", st);
        }
    }

    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SIM_TIME_MAX_NS 120.0
#define SIM_TIME_STEP_NS 0.010 /* 10 пікосекунд */
#define SIM_POINTS_COUNT ((int)(SIM_TIME_MAX_NS / SIM_TIME_STEP_NS) + 1)

typedef enum {
    ESD_STD_IEC_61000_4_2 = 0,
    ESD_STD_HBM_JS_001    = 1,
    ESD_STD_CDM_JS_002    = 2
} EsdStandardType;

typedef struct {
    char name[32];
    double v_rwm;          /* Робоча максимальна зворотна напруга, В */
    double v_br;           /* Напруга лавинного пробою (при 1 мА), В */
    double v_hold;         /* Напруга утримання (для snapback), В */
    double v_trigger;      /* Тригерна напруга відкривання, В */
    double r_dyn;          /* Динамічний диференціальний опір, Ом */
    double c_j_pf;         /* Власна бар'єрна ємність переходу, пФ */
    double l_pkg_nh;       /* Внутрішня паразитна індуктивність виводів, нГн */
    bool   is_snapback;    /* Тип структури: true - Snapback SCR, false - Zener */
} TvsParameters;

typedef struct {
    double v_breakdown_oxide; /* Напруга пробою підзатворного діелектрика, В */
    double v_on_internal;     /* Напруга відкривання внутрішніх діодів, В */
    double r_dyn_internal;    /* Динамічний опір внутрішнього захисту, Ом */
    double i_fail_internal;   /* Граничний струм теплового руйнування діодів, А */
} IcTargetParameters;

typedef struct {
    double l_trace_nh;        /* Паразитна індуктивність доріжки роз'єм-TVS-GND, нГн */
    double r_series_ohm;      /* Послідовний захисний резистор між TVS та IC, Ом */
    double z0_line_ohm;       /* Хвильовий імпеданс лінії передачі, Ом */
    double signal_freq_ghz;   /* Робоча частота сигналу (Найквіст), ГГц */
} PcbLayoutParameters;

typedef struct {
    double i_peak_esd;        /* Максимальний струм первинного ESD-імпульсу, А */
    double v_tvs_clamp_peak;  /* Пікова напруга на переході самого TVS, В */
    double v_inductive_peak;  /* Максимальний індуктивний стрибок L*di/dt, В */
    double v_node_total_peak; /* Сумарна напруга на контакті TVS, В */
    double v_ic_pin_peak;     /* Пікова напруга безпосередньо на виводі IC, В */
    double i_ic_max;          /* Максимальний струм крізь внутрішній захист IC, А */
    double energy_tvs_mj;     /* Енергія, поглинута TVS-діодом, мДж */
    double cutoff_freq_ghz;   /* Частота зрізу -3 дБ через ємність C_j, ГГц */
    double s21_loss_db;       /* Втрати вхідного сигналу на робочій частоті, дБ */
    double r_series_min_safe; /* Мінімально необхідний послідовний опір для безпеки SEED, Ом */
    bool   is_oxide_safe;     /* Прапорець безпеки підзатворного оксиду */
    bool   is_current_safe;   /* Прапорець безпеки за внутрішнім струмом чипа */
    bool   is_latchup_safe;   /* Прапорець стійкості до ефекту Latch-up */
} SimulationMetrics;

/* Генерація миттєвого струму розряду IEC 61000-4-2 за формулою 4 експонент */
double calculate_iec_current(double t_ns, double v_kv) {
    if (t_ns <= 0.0) return 0.0;
    
    double scale = v_kv / 8.0; /* Нормування до 8 кВ */
    double i1_base = 16.6 * scale;
    double k1 = 0.925;
    double tau1 = 0.6;
    double tau2 = 1.6;
    double n = 1.8;
    
    double i2_base = 9.3 * scale;
    double k2 = 0.940;
    double tau3 = 12.0;
    double tau4 = 47.0;
    
    double t_tau1_n = pow(t_ns / tau1, n);
    double term1 = (i1_base / k1) * (t_tau1_n / (1.0 + t_tau1_n)) * exp(-t_ns / tau2);
    
    double t_tau3_n = pow(t_ns / tau3, n);
    double term2 = (i2_base / k2) * (t_tau3_n / (1.0 + t_tau3_n)) * exp(-t_ns / tau4);
    
    return term1 + term2;
}

/* Генерація миттєвого струму HBM JS-001 */
double calculate_hbm_current(double t_ns, double v_kv) {
    if (t_ns <= 0.0) return 0.0;
    double v_volts = v_kv * 1000.0;
    double i_peak = v_volts / 1500.0;
    double tau_rise = 2.27; /* t_r ≈ 5.0 нс */
    double tau_decay = 150.0;
    
    return i_peak * (1.0 - exp(-t_ns / tau_rise)) * exp(-t_ns / tau_decay);
}

/* Генерація миттєвого струму CDM JS-002 */
double calculate_cdm_current(double t_ns, double v_kv) {
    if (t_ns <= 0.0) return 0.0;
    double scale = v_kv / 0.500; /* Нормування до 500 В */
    double i_peak = 12.0 * scale;
    double t_peak = 0.25; /* 250 пікосекунд */
    
    return i_peak * (t_ns / t_peak) * exp(1.0 - (t_ns / t_peak));
}

void run_esd_simulation(
    const TvsParameters *tvs,
    const IcTargetParameters *ic,
    const PcbLayoutParameters *pcb,
    EsdStandardType std_type,
    double v_stress_kv,
    double v_supply_line_v,
    SimulationMetrics *out_metrics)
{
    memset(out_metrics, 0, sizeof(SimulationMetrics));
    
    double l_total_h = (tvs->l_pkg_nh + pcb->l_trace_nh) * 1e-9;
    double dt_s = SIM_TIME_STEP_NS * 1e-9;
    
    double prev_current = 0.0;
    double energy_joules = 0.0;
    
    out_metrics->v_tvs_clamp_peak = 0.0;
    out_metrics->v_inductive_peak = 0.0;
    out_metrics->v_node_total_peak = 0.0;
    out_metrics->v_ic_pin_peak = 0.0;
    out_metrics->i_ic_max = 0.0;
    out_metrics->i_peak_esd = 0.0;
    
    for (int step = 0; step < SIM_POINTS_COUNT; ++step) {
        double t_ns = step * SIM_TIME_STEP_NS;
        double i_total = 0.0;
        
        switch (std_type) {
            case ESD_STD_IEC_61000_4_2:
                i_total = calculate_iec_current(t_ns, v_stress_kv);
                break;
            case ESD_STD_HBM_JS_001:
                i_total = calculate_hbm_current(t_ns, v_stress_kv);
                break;
            case ESD_STD_CDM_JS_002:
                i_total = calculate_cdm_current(t_ns, v_stress_kv);
                break;
        }
        
        if (i_total > out_metrics->i_peak_esd) {
            out_metrics->i_peak_esd = i_total;
        }
        
        /* Швидкість зміни струму di/dt */
        double di_dt = (i_total - prev_current) / dt_s;
        prev_current = i_total;
        
        /* Індуктивний стрибок напруги */
        double v_ind = l_total_h * di_dt;
        if (v_ind < 0.0) v_ind = 0.0;
        if (v_ind > out_metrics->v_inductive_peak) {
            out_metrics->v_inductive_peak = v_ind;
        }
        
        /* Розподіл струмів SEED між TVS та внутрішнім ESD кристала */
        double v_base_tvs = tvs->is_snapback ? tvs->v_hold : tvs->v_br;
        
        /* Аналітичний розрахунок струму кристала */
        double num = v_base_tvs + (i_total * tvs->r_dyn) - ic->v_on_internal;
        double den = pcb->r_series_ohm + ic->r_dyn_internal + tvs->r_dyn;
        double i_ic = (num > 0.0) ? (num / den) : 0.0;
        if (i_ic > i_total) i_ic = i_total;
        
        double i_tvs = i_total - i_ic;
        if (i_tvs < 0.0) i_tvs = 0.0;
        
        /* Напруга на переході TVS */
        double v_tvs_semi = (i_tvs > 0.0) ? (v_base_tvs + i_tvs * tvs->r_dyn) : 0.0;
        if (v_tvs_semi > out_metrics->v_tvs_clamp_peak) {
            out_metrics->v_tvs_clamp_peak = v_tvs_semi;
        }
        
        /* Сумарна напруга на вході плати */
        double v_node_total = v_tvs_semi + v_ind;
        if (v_node_total > out_metrics->v_node_total_peak) {
            out_metrics->v_node_total_peak = v_node_total;
        }
        
        /* Напруга на виводі мікросхеми (після послідовного резистора) */
        double v_pin_ic = v_node_total - (i_ic * pcb->r_series_ohm);
        if (v_pin_ic > out_metrics->v_ic_pin_peak) {
            out_metrics->v_ic_pin_peak = v_pin_ic;
        }
        
        if (i_ic > out_metrics->i_ic_max) {
            out_metrics->i_ic_max = i_ic;
        }
        
        /* Інтегрування енергії в TVS: E = ∫ V(t) * I(t) dt */
        energy_joules += (v_tvs_semi * i_tvs) * dt_s;
    }
    
    out_metrics->energy_tvs_mj = energy_joules * 1000.0;
    
    /* Розрахунок частотних характеристик */
    double c_farads = tvs->c_j_pf * 1e-12;
    out_metrics->cutoff_freq_ghz = (1.0 / (M_PI * pcb->z0_line_ohm * c_farads)) * 1e-9;
    
    double f_hz = pcb->signal_freq_ghz * 1e9;
    double omega = 2.0 * M_PI * f_hz;
    double s21_mag_sq = 1.0 / (1.0 + pow(0.5 * omega * c_farads * pcb->z0_line_ohm, 2.0));
    out_metrics->s21_loss_db = 10.0 * log10(s21_mag_sq);
    
    /* Розрахунок мінімально необхідного R_series для безпеки SEED */
    double v_base_tvs = tvs->is_snapback ? tvs->v_hold : tvs->v_br;
    double r_req = ((v_base_tvs + out_metrics->i_peak_esd * tvs->r_dyn - ic->v_on_internal) 
                   / ic->i_fail_internal) - ic->r_dyn_internal - tvs->r_dyn;
    out_metrics->r_series_min_safe = (r_req > 0.0) ? r_req : 0.0;
    
    /* Критерії валідації безпеки */
    out_metrics->is_oxide_safe = (out_metrics->v_ic_pin_peak < ic->v_breakdown_oxide);
    out_metrics->is_current_safe = (out_metrics->i_ic_max < ic->i_fail_internal);
    
    if (tvs->is_snapback) {
        out_metrics->is_latchup_safe = (tvs->v_hold > (1.10 * v_supply_line_v));
    } else {
        out_metrics->is_latchup_safe = true;
    }
}

void print_engineering_report(
    const TvsParameters *tvs,
    const IcTargetParameters *ic,
    const PcbLayoutParameters *pcb,
    EsdStandardType std_type,
    double v_stress_kv,
    double v_supply_v,
    const SimulationMetrics *m)
{
    const char *std_names[] = {
        "IEC 61000-4-2 (Системний рівень)",
        "ANSI/ESDA/JEDEC JS-001 (HBM)",
        "ANSI/ESDA/JEDEC JS-002 (CDM)"
    };
    
    printf("\n======================================================================\n");
    printf("   ЗВІТ СИМУЛЯЦІЇ ESD-ЗАХИСТУ ТА РОЗРАХУНКУ ПАРАМЕТРІВ TVS-ДІОДА      \n");
    printf("======================================================================\n");
    printf(" 1. ПАРАМЕТРИ СТРЕСУ ТА СТАНДАРТУ:\n");
    printf("    • Стандарт випробування:   %s\n", std_names[std_type]);
    printf("    • Напруга випробування:    %.2f кВ\n", v_stress_kv);
    printf("    • Піковий струм розряду:   %.2f А\n", m->i_peak_esd);
    printf("    • Напруга шини живлення:   %.2f В\n", v_supply_v);
    printf("----------------------------------------------------------------------\n");
    printf(" 2. ПАРАМЕТРИ TVS-ДІОДА (%s):\n", tvs->name);
    printf("    • Робоча напруга V_RWM:    %.2f В\n", tvs->v_rwm);
    printf("    • Напруга пробою V_BR:     %.2f В\n", tvs->v_br);
    printf("    • Тип структури:           %s\n", tvs->is_snapback ? "Snapback SCR" : "Standard Zener");
    if (tvs->is_snapback) {
        printf("    • Напруга утримання V_h:   %.2f В (Тригер V_t1 = %.2f В)\n", tvs->v_hold, tvs->v_trigger);
    }
    printf("    • Динамічний опір R_dyn:   %.3f Ом\n", tvs->r_dyn);
    printf("    • Бар'єрна ємність C_j:    %.3f пФ\n", tvs->c_j_pf);
    printf("    • Індуктивність виводів:   %.2f нГн\n", tvs->l_pkg_nh);
    printf("----------------------------------------------------------------------\n");
    printf(" 3. ДРУКОВАНА ПЛАТА ТА ЦІЛЬОВА МІКРОСХЕМА (SEED КООРДИНАЦІЯ):\n");
    printf("    • Індуктивність доріжки:   %.2f нГн (L_trace)\n", pcb->l_trace_nh);
    printf("    • Послідовний резистор:    %.2f Ом (R_series)\n", pcb->r_series_ohm);
    printf("    • Межа пробою оксиду IC:   %.2f В (V_breakdown)\n", ic->v_breakdown_oxide);
    printf("    • Струмова межа чипа:      %.2f А (I_fail_internal)\n", ic->i_fail_internal);
    printf("----------------------------------------------------------------------\n");
    printf(" 4. РЕЗУЛЬТАТИ ДИНАМІЧНОГО РОЗРАХУНКУ НАПРУГ І СТРУМІВ:\n");
    printf("    • Індуктивний стрибок:     +%.2f В  [L * di/dt]\n", m->v_inductive_peak);
    printf("    • Напруга переходу TVS:    %.2f В  [V_semi]\n", m->v_tvs_clamp_peak);
    printf("    • Пікова напруга на платі: %.2f В  [V_node_total]\n", m->v_node_total_peak);
    printf("    • Напруга на виводі чипа:  %.2f В  [V_pin_IC]\n", m->v_ic_pin_peak);
    printf("    • Струм крізь кристал IC:  %.3f А  (%.1f%% від повного струму)\n", 
           m->i_ic_max, (m->i_ic_max / m->i_peak_esd) * 100.0);
    printf("    • Енергія в TVS-діоді:     %.3f мДж\n", m->energy_tvs_mj);
    printf("    • Мінімальний R_ser (SEED):%.2f Ом\n", m->r_series_min_safe);
    printf("----------------------------------------------------------------------\n");
    printf(" 5. СИГНАЛЬНА ЦІЛІСНІСТЬ (HIGH-SPEED SIGNAL INTEGRITY):\n");
    printf("    • Хвильовий імпеданс Z_0:  %.1f Ом\n", pcb->z0_line_ohm);
    printf("    • Частота зрізу (-3 дБ):   %.2f ГГц\n", m->cutoff_freq_ghz);
    printf("    • Втрати на частоті %.2f ГГц: %.3f дБ (S21)\n", pcb->signal_freq_ghz, m->s21_loss_db);
    printf("----------------------------------------------------------------------\n");
    printf(" 6. ПІДСУМКОВИЙ ІНЖЕНЕРНИЙ ВИСНОВОК:\n");
    printf("    [%s] 1. Стійкість діелектрика затвора (%.2f В < %.2f В)\n",
           m->is_oxide_safe ? " УСПІХ " : "ДЕФЕКТ", m->v_ic_pin_peak, ic->v_breakdown_oxide);
    printf("    [%s] 2. Струмове навантаження внутрішнього захисту (%.2f А < %.2f А)\n",
           m->is_current_safe ? " УСПІХ " : "ДЕФЕКТ", m->i_ic_max, ic->i_fail_internal);
    printf("    [%s] 3. Запобігання ефекту замикання Latch-up (%s)\n",
           m->is_latchup_safe ? " УСПІХ " : "ДЕФЕКТ", 
           tvs->is_snapback ? (m->is_latchup_safe ? "V_hold > 1.1*V_supply" : "V_hold <= V_supply!") : "Non-snapback (N/A)");
    printf("======================================================================\n\n");
}

int main(void) {
    /* 1. Конфігурація швидкісного TVS-діода (Snapback для USB 3.2 / HDMI 2.0) */
    TvsParameters tvs_snap = {
        .name = "ESD7383_Snapback",
        .v_rwm = 3.3,
        .v_br = 5.0,
        .v_hold = 3.8,
        .v_trigger = 7.5,
        .r_dyn = 0.22,
        .c_j_pf = 0.28,
        .l_pkg_nh = 0.35, /* DFN0603 */
        .is_snapback = true
    };
    
    /* 2. Конфігурація класичного TVS-діода (Zener для повільних шин / живлення) */
    TvsParameters tvs_zener = {
        .name = "SMAJ5.0A_Zener",
        .v_rwm = 5.0,
        .v_br = 6.4,
        .v_hold = 6.4,
        .v_trigger = 6.4,
        .r_dyn = 0.85,
        .c_j_pf = 15.0,
        .l_pkg_nh = 1.20, /* SMA package */
        .is_snapback = false
    };
    
    /* 3. Цільовий мікроконтролер / швидкісний PHY-трансивер */
    IcTargetParameters mcu_target = {
        .v_breakdown_oxide = 11.5, /* Пробій затвора при 11.5 В */
        .v_on_internal = 0.85,     /* Внутрішній діод відкривається при 0.85 В */
        .r_dyn_internal = 2.40,    /* Динамічний опір захисту кристала 2.4 Ом */
        .i_fail_internal = 1.50    /* Термічне руйнування при струмі понад 1.5 А */
    };
    
    /* 4. Параметри трасування друкованої плати */
    PcbLayoutParameters pcb_highspeed = {
        .l_trace_nh = 1.20,        /* 1.2 мм доріжки до перехідних отворів землі */
        .r_series_ohm = 15.0,      /* Послідовний демпфер 15 Ом */
        .z0_line_ohm = 50.0,       /* 50 Ом несиметрична лінія (90 Ом диференціальна) */
        .signal_freq_ghz = 5.0     /* 5 ГГц для USB 3.2 Gen2 */
    };
    
    SimulationMetrics metrics;
    
    /* Тест 1: Системний розряд 8 кВ IEC 61000-4-2 на швидкісну лінію з TVS Snapback */
    run_esd_simulation(&tvs_snap, &mcu_target, &pcb_highspeed, 
                       ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    print_engineering_report(&tvs_snap, &mcu_target, &pcb_highspeed, 
                             ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    
    /* Тест 2: Модель CDM 500 В на той самий вузол */
    run_esd_simulation(&tvs_snap, &mcu_target, &pcb_highspeed, 
                       ESD_STD_CDM_JS_002, 0.500, 3.3, &metrics);
    print_engineering_report(&tvs_snap, &mcu_target, &pcb_highspeed, 
                             ESD_STD_CDM_JS_002, 0.500, 3.3, &metrics);
    
    /* Тест 3: Порівняння зі звичайним Zener TVS без послідовного резистора (R_ser = 0) */
    pcb_highspeed.r_series_ohm = 0.0;
    run_esd_simulation(&tvs_zener, &mcu_target, &pcb_highspeed, 
                       ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    print_engineering_report(&tvs_zener, &mcu_target, &pcb_highspeed, 
                             ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    
    return 0;
}

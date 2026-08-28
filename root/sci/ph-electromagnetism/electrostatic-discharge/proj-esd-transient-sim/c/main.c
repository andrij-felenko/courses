#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура параметрів еквівалентного RLC-кола ESD */
typedef struct {
    double C_cap;        /* Ємність джерела розряду, Фарад */
    double L_ind;        /* Паразитна індуктивність виводів, Генрі */
    double R_line;       /* Опір провідників та тіла, Ом */
    double V_init;       /* Початкова напруга розряду, Вольт */
} esd_circuit_t;

/* Структура параметрів захисного TVS-діода */
typedef struct {
    double V_br;         /* Пробійна напруга лавинного переходу, Вольт */
    double R_dyn;        /* Динамічний опір діода в режимі пробою, Ом */
    double C_parasitic;  /* Паразитна ємність p-n переходу, Фарад */
} tvs_diode_t;

/* Результати розрахунку симуляції */
typedef struct {
    double peak_current;   /* Піковий струм розряду, Ампер */
    double max_voltage;    /* Максимальна напруга обмеження на виводі, Вольт */
    double tvs_energy;     /* Сумарна енергія, розсіяна TVS-діодом, Джоуль */
    double duration_ns;    /* Тривалість імпульсу до рівня 10% струму, нс */
} simulation_result_t;

/* Обчислення напруги на TVS-діоді залежно від струму */
static double calculate_tvs_voltage(double current, const tvs_diode_t *tvs) {
    double abs_i = fabs(current);
    if (abs_i < 1e-6) {
        return 0.0;
    }
    return tvs->V_br + abs_i * tvs->R_dyn;
}

/* Функція моделювання перехідного процесу розряду */
simulation_result_t simulate_esd_transient(const esd_circuit_t *circuit,
                                           const tvs_diode_t *tvs,
                                           double sim_time_ns,
                                           double dt_ps) {
    simulation_result_t res = {0.0, 0.0, 0.0, 0.0};
    
    double dt = dt_ps * 1e-12;               /* Переведення пікосекунд у секунди */
    double total_time = sim_time_ns * 1e-9;  /* Переведення наносекунд у секунди */
    
    double v_c = circuit->V_init;            /* Початкова напруга на ємності */
    double i_curr = 0.0;                     /* Початковий струм у колі */
    double t = 0.0;
    
    double max_i = 0.0;
    double max_v = 0.0;
    double energy_tvs = 0.0;
    
    while (t < total_time && v_c > 0.1) {
        double v_tvs = calculate_tvs_voltage(i_curr, tvs);
        
        /* Диференціальні рівняння стану */
        double dv_c = -i_curr / circuit->C_cap;
        double di_dt = (v_c - i_curr * circuit->R_line - v_tvs) / circuit->L_ind;
        
        /* Крок інтегрування Ейлера */
        v_c += dv_c * dt;
        i_curr += di_dt * dt;
        t += dt;
        
        if (i_curr < 0.0) {
            i_curr = 0.0;
        }
        
        /* Фіксація максимумів */
        if (i_curr > max_i) {
            max_i = i_curr;
        }
        if (v_tvs > max_v) {
            max_v = v_tvs;
        }
        
        /* Інтегрування потужності TVS-діода: P = V_tvs * I */
        energy_tvs += (v_tvs * i_curr) * dt;
    }
    
    res.peak_current = max_i;
    res.max_voltage = max_v;
    res.tvs_energy = energy_tvs;
    res.duration_ns = t * 1e9;
    
    return res;
}

int main(void) {
    /* Налаштування параметрів IEC 61000-4-2 (8 кВ) */
    esd_circuit_t iec_hbm = {
        .C_cap = 150e-12,     /* 150 пФ */
        .L_ind = 10e-9,       /* 10 нГн паразитної індуктивності */
        .R_line = 330.0,      /* 330 Ом */
        .V_init = 8000.0      /* 8000 Вольт */
    };
    
    /* Параметри ультранизькоємного TVS-діода */
    tvs_diode_t tvs = {
        .V_br = 6.8,          /* Пробій при 6.8 В */
        .R_dyn = 0.25,        /* Динамічний опір 0.25 Ом */
        .C_parasitic = 0.3e-12/* 0.3 пФ */
    };
    
    printf("=== Симуляція перехідного процесу ESD (IEC 61000-4-2, 8 кВ) ===\n");
    simulation_result_t res = simulate_esd_transient(&iec_hbm, &tvs, 100.0, 1.0);
    
    printf("Піковий струм розряду (I_peak):    %.2f А\n", res.peak_current);
    printf("Максимальна напруга (V_clamp):     %.2f В\n", res.max_voltage);
    printf("Енергія розсіяна TVS (E_tvs):       %.4f мДж\n", res.tvs_energy * 1000.0);
    printf("Тривалість перехідного процесу:    %.1f нс\n", res.duration_ns);
    
    return 0;
}

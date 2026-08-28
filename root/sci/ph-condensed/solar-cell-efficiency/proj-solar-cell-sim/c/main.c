#include <stdio.h>
#include <math.h>

/* Фізичні фундаментальні сталі */
#define K_B 1.380649e-23   /* Стала Больцмана, Дж/К */
#define Q_E 1.60217663e-19  /* Заряд електрона, Кл */

/* Параметри сонячного елемента */
typedef struct {
    double temp_k;      /* Температура елемента, К */
    double area_cm2;    /* Площа елемента, см² */
    double i_ph;        /* Фотострум генерації, А */
    double i_0;         /* Струм насичення диода, А */
    double n_ideality;  /* Фактор ідеальності диода (1.0 - 2.0) */
    double r_s;         /* Послідовний опір, Ом */
    double r_sh;        /* Паралельний опір (шунт), Ом */
    double p_in_wm2;    /* Вхідна оптична потужність, Вт/м² */
} solar_cell_params_t;

/* Результати вимірювання IV та ККД */
typedef struct {
    double v_oc;        /* Напруга холостого ходу, В */
    double i_sc;        /* Струм короткого замикання, А */
    double v_mp;        /* Напруга в точці MPP, В */
    double i_mp;        /* Струм в точці MPP, А */
    double p_max;       /* Максимальна потужність, Вт */
    double fill_factor; /* Фактор заповнення FF (0..1) */
    double efficiency;  /* ККД η (0..1) */
} solar_cell_results_t;

/* Чисельне розв'язання неявного рівняння струму методом Ньютона-Рафсона */
static double solve_current(double v, const solar_cell_params_t *p) {
    double v_t = (p->n_ideality * K_B * p->temp_k) / Q_E;
    double i_curr = p->i_ph; /* Початкове наближення */
    
    for (int iter = 0; iter < 100; ++iter) {
        double arg = (v + i_curr * p->r_s) / v_t;
        if (arg > 80.0) arg = 80.0; /* Захист від переповнення exp */
        
        double exp_val = exp(arg);
        double f = p->i_ph - p->i_0 * (exp_val - 1.0) - (v + i_curr * p->r_s) / p->r_sh - i_curr;
        double df = -p->i_0 * (p->r_s / v_t) * exp_val - p->r_s / p->r_sh - 1.0;
        
        double i_next = i_curr - f / df;
        if (fabs(i_next - i_curr) < 1e-9) {
            return (i_next > 0.0) ? i_next : 0.0;
        }
        i_curr = i_next;
    }
    return (i_curr > 0.0) ? i_curr : 0.0;
}

/* Обчислення характеристик та ККД */
solar_cell_results_t analyze_solar_cell(const solar_cell_params_t *p) {
    solar_cell_results_t res = {0};
    
    /* 1. Струм короткого замикання (V = 0) */
    res.i_sc = solve_current(0.0, p);
    
    /* 2. Напруга холостого ходу (бісекція для пошуку V, де I = 0) */
    double v_low = 0.0, v_high = 1.2;
    for (int i = 0; i < 50; ++i) {
        double v_mid = 0.5 * (v_low + v_high);
        double i_mid = solve_current(v_mid, p);
        if (i_mid > 1e-7) {
            v_low = v_mid;
        } else {
            v_high = v_mid;
        }
    }
    res.v_oc = 0.5 * (v_low + v_high);
    
    /* 3. Сканування IV для пошуку точки максимальної потужності (MPP) */
    int steps = 1000;
    double dv = res.v_oc / steps;
    
    for (int k = 0; k <= steps; ++k) {
        double v = k * dv;
        double i = solve_current(v, p);
        double p_val = v * i;
        
        if (p_val > res.p_max) {
            res.p_max = p_val;
            res.v_mp = v;
            res.i_mp = i;
        }
    }
    
    /* 4. Фактор заповнення FF та ККД */
    if (res.v_oc * res.i_sc > 0.0) {
        res.fill_factor = res.p_max / (res.v_oc * res.i_sc);
    }
    
    double p_in_watts = (p->p_in_wm2 * (p->area_cm2 / 10000.0));
    if (p_in_watts > 0.0) {
        res.efficiency = res.p_max / p_in_watts;
    }
    
    return res;
}

int main(void) {
    solar_cell_params_t cell = {
        .temp_k = 298.15,      /* 25 °C STC */
        .area_cm2 = 244.3,      /* Стандартний кремнієвий елемент M10 */
        .i_ph = 10.2,           /* Фотострум 10.2 А */
        .i_0 = 1e-11,           /* Струм насичення диода 10 пА */
        .n_ideality = 1.1,      /* Кремнієвий p-n перехід */
        .r_s = 0.005,           /* Послідовний опір 5 мОм */
        .r_sh = 500.0,          /* Паралельний опір 500 Ом */
        .p_in_wm2 = 1000.0      /* Сонячне випромінювання AM1.5G */
    };

    solar_cell_results_t r = analyze_solar_cell(&cell);

    printf("=== Результати аналізу сонячного елемента ===\n");
    printf("Струм к.з. (I_sc):            %.3f А\n", r.i_sc);
    printf("Напруга х.х. (V_oc):           %.3f В\n", r.v_oc);
    printf("Напруга в точці MPP (V_mp):    %.3f В\n", r.v_mp);
    printf("Струм в точці MPP (I_mp):      %.3f А\n", r.i_mp);
    printf("Максимальна потужність (Pmax): %.3f Вт\n", r.p_max);
    printf("Фактор заповнення (FF):        %.2f %%\n", r.fill_factor * 100.0);
    printf("Розрахунковий ККД (η):         %.2f %%\n", r.efficiency * 100.0);

    return 0;
}

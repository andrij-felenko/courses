#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Параметри тунельного діода (типовий германієвий 3І306Ж / 1N3716) */
typedef struct {
    double ip;      /* Піковий струм, А (0.005 А = 5 мА) */
    double vp;      /* Пікова напруга, В (0.065 В = 65 мВ) */
    double iv;      /* Струм западини, А (0.0005 А = 0.5 мА) */
    double vv;      /* Напруга западини, В (0.350 В = 350 мВ) */
    double vf;      /* Пряма напруга відновлення, В (0.500 В = 500 мВ) */
    double cj;      /* Бар'єрна ємність, Ф (4 пФ = 4e-12 Ф) */
    double rs;      /* Опір втрат, Ом (1.5 Ом) */
    double ls;      /* Індуктивність виводів, Гн (0.4 нГн = 0.4e-9 Гн) */
} TunnelDiodeParams;

/* Параметри електричного кола */
typedef struct {
    double e_bias;  /* Постійна напруга зміщення, В */
    double r_load;  /* Опір навантаження, Ом */
} CircuitParams;

/* Розрахунок нелінійної вольт-амперної характеристики */
double diode_current(double v, const TunnelDiodeParams *d) {
    if (v < 0.0) {
        /* Зворотне міжзонне тунелювання (крута лінійна провідність) */
        return v / (d->vp / d->ip);
    }
    
    /* 1. Міжзонний тунельний струм Есакі */
    double i_tu = d->ip * (v / d->vp) * exp(1.0 - (v / d->vp));
    
    /* 2. Надлишковий струм глибоких рівнів дефектів */
    double a_coeff = 4.0;
    double i_ex = (v < d->vv) ? (d->iv * (v / d->vv))
                              : (d->iv * exp(a_coeff * (v - d->vv)) / (1.0 + exp(a_coeff * (v - d->vv))));
    
    /* 3. Тепловий дифузійний струм інжекції Шоклі */
    double ut = 0.02585; /* Тепловий потенціал kT/q при 300 K */
    double i_diff = 1e-11 * (exp(v / (1.3 * ut)) - 1.0);
    
    return i_tu + i_ex + i_diff;
}

/* Вхідний імпульс запуску: згладжена сходинка з часом наростання 20 пс */
double input_pulse(double t) {
    double t_start = 100e-12; /* 100 пс затримка запуску */
    double t_rise  = 20e-12;  /* 20 пс тривалість фронту запуску */
    double v_step  = 0.050;   /* амплітуда запуску 50 мВ */
    
    if (t < t_start) return 0.0;
    if (t < t_start + t_rise) {
        return v_step * (t - t_start) / t_rise;
    }
    return v_step;
}

/* Праві частини системи диференціальних рівнянь кола */
void system_derivatives(double t, double v_j, double i_l,
                        const TunnelDiodeParams *d, const CircuitParams *c,
                        double *dv_dt, double *di_dt) {
    double v_in = input_pulse(t);
    double v_total = c->e_bias + v_in;
    double i_dio = diode_current(v_j, d);
    
    /* Баланс струмів: C_j * dV_j/dt = I_L - I_dio */
    *dv_dt = (i_l - i_dio) / d->cj;
    
    /* Баланс напруг: L_s * dI_L/dt = V_total - I_L*(R_L + R_s) - V_j */
    *di_dt = (v_total - i_l * (c->r_load + d->rs) - v_j) / d->ls;
}

int main(void) {
    TunnelDiodeParams diode = {
        .ip = 0.005,    /* 5 мА */
        .vp = 0.065,    /* 65 мВ */
        .iv = 0.0005,   /* 0.5 мА */
        .vv = 0.350,    /* 350 мВ */
        .vf = 0.500,    /* 500 мВ */
        .cj = 4.0e-12,  /* 4 пФ */
        .rs = 1.5,      /* 1.5 Ом */
        .ls = 0.4e-9    /* 0.4 нГн */
    };
    
    CircuitParams circuit = {
        .e_bias = 0.220, /* 220 мВ робоче зміщення */
        .r_load = 40.0   /* 40 Ом навантаження (> |R_N| = 35 Ом) */
    };
    
    double t = 0.0;
    double t_end = 800e-12;   /* 800 пс тривалість симуляції */
    double dt = 0.1e-12;      /* 0.1 пс крок інтегрування RK4 */
    
    /* Початкові стаціонарні умови (точка A) */
    double v_j = 0.052;
    double i_l = 0.0042;
    
    double v_10 = 0.052 + 0.10 * (0.480 - 0.052);
    double v_90 = 0.052 + 0.90 * (0.480 - 0.052);
    double t_10 = -1.0, t_90 = -1.0;
    
    printf("# Симуляція перемикання пікосекундного тригера на тунельному діоді\n");
    printf("# Час(пс)\tНапруга(В)\tСтрум(мА)\tВхід(В)\n");
    
    int step = 0;
    while (t <= t_end) {
        if (step % 50 == 0) {
            printf("%.2f\t\t%.4f\t\t%.3f\t\t%.3f\n",
                   t * 1e12, v_j, i_l * 1e3, input_pulse(t));
        }
        
        /* Фіксація часу наростання фронту за рівнями 10% - 90% */
        if (t_10 < 0.0 && v_j >= v_10) t_10 = t;
        if (t_90 < 0.0 && v_j >= v_90) t_90 = t;
        
        /* 4-кроковий метод Рунге-Кутти (RK4) */
        double k1_v, k1_i;
        system_derivatives(t, v_j, i_l, &diode, &circuit, &k1_v, &k1_i);
        
        double k2_v, k2_i;
        system_derivatives(t + 0.5 * dt, v_j + 0.5 * dt * k1_v, i_l + 0.5 * dt * k1_i,
                           &diode, &circuit, &k2_v, &k2_i);
        
        double k3_v, k3_i;
        system_derivatives(t + 0.5 * dt, v_j + 0.5 * dt * k2_v, i_l + 0.5 * dt * k2_i,
                           &diode, &circuit, &k3_v, &k3_i);
        
        double k4_v, k4_i;
        system_derivatives(t + dt, v_j + dt * k3_v, i_l + dt * k3_i,
                           &diode, &circuit, &k4_v, &k4_i);
        
        v_j += (dt / 6.0) * (k1_v + 2.0 * k2_v + 2.0 * k3_v + k4_v);
        i_l += (dt / 6.0) * (k1_i + 2.0 * k2_i + 2.0 * k3_i + k4_i);
        t += dt;
        step++;
    }
    
    if (t_10 > 0.0 && t_90 > 0.0) {
        printf("# Розрахований час наростання фронту t_r (10%%-90%%): %.2f пс\n",
               (t_90 - t_10) * 1e12);
    }
    
    return 0;
}

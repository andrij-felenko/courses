/* 
 * Haynes-Shockley 1D Drift-Diffusion Simulator (C99)
 * Чисельний розв'язувач для германієвого бруска n-типу
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double length_cm;      /* Довжина напівпровідникового бруска (см) */
    int num_points;        /* Кількість вузлів просторової сітки */
    double E_field;        /* Напруженість тягнучого поля (В/см) */
    double mu_p;           /* Рухливість меншинних дірок (см²/В·с) */
    double D_p;            /* Коефіцієнт дифузії дірок (см²/с) */
    double tau_p;          /* Об'ємний час життя дірок (с) */
    double total_time_s;   /* Загальний тривалість симуляції (с) */
} SimParams;

void run_simulation(const SimParams* params) {
    double dx = params->length_cm / (params->num_points - 1);
    double v_drift = params->mu_p * params->E_field;
    
    /* Критерій стабільності CFL */
    double dt_diff = (dx * dx) / (2.0 * params->D_p);
    double dt_adv = (v_drift > 0.0) ? (dx / v_drift) : 1e9;
    double dt = 0.4 * (dt_diff < dt_adv ? dt_diff : dt_adv);
    
    int num_steps = (int)(params->total_time_s / dt);
    
    double* u_curr = (double*)calloc((size_t)params->num_points, sizeof(double));
    double* u_next = (double*)calloc((size_t)params->num_points, sizeof(double));
    
    if (!u_curr || !u_next) {
        fprintf(stderr, "Помилка виділення пам'яті для сітки!\n");
        free(u_curr);
        free(u_next);
        return;
    }
    
    /* Початкова ін'єкція імпульсу в точці x = 0.1 см (гауссів сгусток) */
    double x_inject = 0.1;
    double sigma_0 = 0.01; /* 100 мкм */
    double N0 = 1e12;     /* Початкова кількість дірок */
    
    for (int i = 0; i < params->num_points; ++i) {
        double x = i * dx;
        double arg = (x - x_inject) / sigma_0;
        u_curr[i] = (N0 / (sqrt(2.0 * M_PI) * sigma_0)) * exp(-0.5 * arg * arg);
    }
    
    printf("--- Початок симуляції Гейнса-Шоклі (C99) ---\n");
    printf("Параметри бруска: L = %.2f см, E = %.1f В/см, mu = %.0f cm²/Vs\n",
           params->length_cm, params->E_field, params->mu_p);
    printf("Сітка: %d вузлів, dx = %.4e см, dt = %.4e с (%d кроків)\n\n",
           params->num_points, dx, dt, num_steps);
    
    int print_interval = num_steps / 4;
    for (int step = 0; step <= num_steps; ++step) {
        double t = step * dt;
        
        if (step % print_interval == 0 || step == num_steps) {
            double max_val = 0.0;
            double x_max = 0.0;
            double sum_val = 0.0;
            
            for (int i = 0; i < params->num_points; ++i) {
                sum_val += u_curr[i] * dx;
                if (u_curr[i] > max_val) {
                    max_val = u_curr[i];
                    x_max = i * dx;
                }
            }
            printf("t = %8.2f мкс | x_peak = %6.3f см | Max conc = %8.2e cm⁻³ | Total = %8.2e\n",
                   t * 1e6, x_max, max_val, sum_val);
        }
        
        /* Оновлення сітки FDTD (Upwind advection + Centered diffusion) */
        for (int i = 1; i < params->num_points - 1; ++i) {
            double diff = params->D_p * (u_curr[i+1] - 2.0 * u_curr[i] + u_curr[i-1]) / (dx * dx);
            double adv = v_drift * (u_curr[i] - u_curr[i-1]) / dx;
            double recomp = u_curr[i] / params->tau_p;
            
            u_next[i] = u_curr[i] + dt * (diff - adv - recomp);
        }
        
        /* Граничні умови (Absorbing Boundaries) */
        u_next[0] = 0.0;
        u_next[params->num_points - 1] = 0.0;
        
        /* Обмін вказівників буферів */
        double* temp = u_curr;
        u_curr = u_next;
        u_next = temp;
    }
    
    free(u_curr);
    free(u_next);
}

int main(void) {
    SimParams params = {
        .length_cm = 1.0,      /* 10 мм брусок германію */
        .num_points = 500,     /* 500 вузлів сітки */
        .E_field = 20.0,       /* 20 В/см тягнуче поле */
        .mu_p = 1900.0,        /* 1900 см²/В·с для дірок у Ge */
        .D_p = 49.0,           /* D = mu * kT/q = 1900 * 0.0259 ≈ 49 см²/с */
        .tau_p = 50e-6,        /* 50 мкс час життя */
        .total_time_s = 200e-6 /* 200 мкс загальний час */
    };
    
    run_simulation(&params);
    return 0;
}

/* 
 * 1D Transient Thermal Diffusion & Laser Flash Solver in C (C99)
 * Алгоритм Кранка-Ніколсон та метод Томаса для розрахунку температуропровідності.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int N;             /* Кількість вузлів просторової сітки */
    double L;          /* Товщина зразка, м */
    double a_true;     /* Еталонна температуропровідність, м²/с */
    double dt;         /* Крок за часом, с */
    double t_max;      /* Повний час моделювання, с */
} SimulationConfig;

typedef struct {
    double* x;
    double* T;
    double* T_new;
    double* a_diag;
    double* b_diag;
    double* c_diag;
    double* d_vec;
    double* P;
    double* Q;
} SolverBuffers;

/* Ініціалізація та виділення пам'яті */
SolverBuffers* create_solver_buffers(int N) {
    SolverBuffers* buf = (SolverBuffers*)malloc(sizeof(SolverBuffers));
    if (!buf) return NULL;
    
    buf->x = (double*)malloc(N * sizeof(double));
    buf->T = (double*)malloc(N * sizeof(double));
    buf->T_new = (double*)malloc(N * sizeof(double));
    buf->a_diag = (double*)malloc(N * sizeof(double));
    buf->b_diag = (double*)malloc(N * sizeof(double));
    buf->c_diag = (double*)malloc(N * sizeof(double));
    buf->d_vec = (double*)malloc(N * sizeof(double));
    buf->P = (double*)malloc(N * sizeof(double));
    buf->Q = (double*)malloc(N * sizeof(double));
    
    return buf;
}

void free_solver_buffers(SolverBuffers* buf) {
    if (!buf) return;
    free(buf->x); free(buf->T); free(buf->T_new);
    free(buf->a_diag); free(buf->b_diag); free(buf->c_diag);
    free(buf->d_vec); free(buf->P); free(buf->Q);
    free(buf);
}

/* Розв'язання тридіагональної системи методому Томаса (TDMA) */
void solve_tdma(int N, const double* a, const double* b, const double* c, 
                const double* d, double* P, double* Q, double* x_out) {
    /* Прямий хід */
    P[0] = -c[0] / b[0];
    Q[0] = d[0] / b[0];
    for (int i = 1; i < N; i++) {
        double denom = b[i] + a[i] * P[i - 1];
        if (i < N - 1) {
            P[i] = -c[i] / denom;
        }
        Q[i] = (d[i] - a[i] * Q[i - 1]) / denom;
    }
    
    /* Зворотний хід */
    x_out[N - 1] = Q[N - 1];
    for (int i = N - 2; i >= 0; i--) {
        x_out[i] = P[i] * x_out[i + 1] + Q[i];
    }
}

/* Основний цикл моделювання */
double run_laser_flash_simulation(const SimulationConfig* cfg) {
    int N = cfg->N;
    double dx = cfg->L / (N - 1);
    double r = cfg->a_true * cfg->dt / (2.0 * dx * dx);
    
    SolverBuffers* buf = create_solver_buffers(N);
    if (!buf) return -1.0;
    
    /* Сітка та початкові умови */
    for (int i = 0; i < N; i++) {
        buf->x[i] = i * dx;
        buf->T[i] = 0.0; /* Початкова температура 0 °C */
    }
    
    /* Лазерний імпульс: короткий нагрів першого вузла i = 0 */
    double Q_laser = 100.0; /* Енергія нагріву */
    buf->T[0] += Q_laser / (dx);
    
    double T_initial_rear = buf->T[N - 1];
    double t_half = -1.0;
    double T_max_rear = 0.0;
    
    int steps = (int)(cfg->t_max / cfg->dt);
    
    /* Масив для збереження термограми тильної поверхні */
    double* rear_history = (double*)malloc(steps * sizeof(double));
    double* time_history = (double*)malloc(steps * sizeof(double));
    
    for (int step = 0; step < steps; step++) {
        double current_time = step * cfg->dt;
        time_history[step] = current_time;
        rear_history[step] = buf->T[N - 1];
        if (buf->T[N - 1] > T_max_rear) {
            T_max_rear = buf->T[N - 1];
        }
        
        /* Заповнення СЛАР для Crank-Nicolson */
        for (int i = 1; i < N - 1; i++) {
            buf->a_diag[i] = -r;
            buf->b_diag[i] = 1.0 + 2.0 * r;
            buf->c_diag[i] = -r;
            buf->d_vec[i] = r * buf->T[i - 1] + (1.0 - 2.0 * r) * buf->T[i] + r * buf->T[i + 1];
        }
        
        /* Адіабатична межа i = 0 */
        buf->a_diag[0] = 0.0;
        buf->b_diag[0] = 1.0 + 2.0 * r;
        buf->c_diag[0] = -2.0 * r;
        buf->d_vec[0] = (1.0 - 2.0 * r) * buf->T[0] + 2.0 * r * buf->T[1];
        
        /* Адіабатична межа i = N-1 */
        buf->a_diag[N - 1] = -2.0 * r;
        buf->b_diag[N - 1] = 1.0 + 2.0 * r;
        buf->c_diag[N - 1] = 0.0;
        buf->d_vec[N - 1] = 2.0 * r * buf->T[N - 2] + (1.0 - 2.0 * r) * buf->T[N - 1];
        
        /* Крок за часом через TDMA */
        solve_tdma(N, buf->a_diag, buf->b_diag, buf->c_diag, buf->d_vec, 
                   buf->P, buf->Q, buf->T_new);
        
        /* Оновлення вектора температур */
        for (int i = 0; i < N; i++) {
            buf->T[i] = buf->T_new[i];
        }
    }
    
    /* Знаходження часу напівпідйому t_{1/2} */
    double T_half_target = T_initial_rear + 0.5 * (T_max_rear - T_initial_rear);
    for (int step = 0; step < steps; step++) {
        if (rear_history[step] >= T_half_target) {
            /* Лінійна інтерполяція часу */
            if (step > 0) {
                double t0 = time_history[step - 1];
                double t1 = time_history[step];
                double v0 = rear_history[step - 1];
                double v1 = rear_history[step];
                t_half = t0 + (T_half_target - v0) * (t1 - t0) / (v1 - v0);
            } else {
                t_half = time_history[step];
            }
            break;
        }
    }
    
    /* Обчислення температуропровідності за формулою Паркера */
    double a_calc = (t_half > 0.0) ? (0.1388 * cfg->L * cfg->L / t_half) : -1.0;
    
    free(rear_history);
    free(time_history);
    free_solver_buffers(buf);
    
    return a_calc;
}

int main(void) {
    printf("=== Чисельне моделювання методу LFA (C99) ===\n");
    
    SimulationConfig cfg;
    cfg.N = 101;
    cfg.L = 0.002;             /* 2 мм товщина зразка */
    cfg.a_true = 1.17e-4;       /* Мідь: a = 1.17e-4 м²/с */
    cfg.dt = 1.0e-5;            /* Крок 10 мкс */
    cfg.t_max = 0.02;           /* 20 мс моделювання */
    
    double a_extracted = run_laser_flash_simulation(&cfg);
    double error_pct = fabs(a_extracted - cfg.a_true) / cfg.a_true * 100.0;
    
    printf("Задане значення a:      %.6e м²/с\n", cfg.a_true);
    printf("Екстраговане значення: %.6e м²/с\n", a_extracted);
    printf("Відносна похибка:      %.3f %%\n", error_pct);
    
    return 0;
}

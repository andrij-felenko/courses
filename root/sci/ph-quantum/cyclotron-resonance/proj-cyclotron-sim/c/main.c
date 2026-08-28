#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double m_eff;      /* Ефективна маса (кг) */
    double q;          /* Заряд частинки (Кл) */
    double B;          /* Магнітне поле (Тесла) */
    double E0;         /* Амплітуда НВЧ електричного поля (В/м) */
    double tau;        /* Час між зіткненнями (с) */
    double dt;         /* Крок інтегрування за часом (с) */
    int steps;         /* Кількість кроків у симуляції */
} SimParams;

/* Симуляція траєкторії та обчислення поглинутої потужності для частоти omega */
double simulate_absorption(const SimParams *p, double omega) {
    double x = 0.0, y = 0.0;
    double vx = 0.0, vy = 0.0;
    double total_work = 0.0;
    
    double wc = fabsf(p->q * p->B / p->m_eff);
    double p_coll = 1.0 - exp(-p->dt / p->tau);

    for (int i = 0; i < p->steps; i++) {
        double t = i * p->dt;
        
        /* Компоненти електричного поля */
        double Ex = p->E0 * cos(omega * t);
        double Ey = p->E0 * sin(omega * t);
        
        /* Сила Лоренца та прискорення */
        double ax = (p->q * Ex + p->q * p->B * vy) / p->m_eff;
        double ay = (p->q * Ey - p->q * p->B * vx) / p->m_eff;
        
        /* Оновлення швидкості (Ейлер-Кромер) */
        vx += ax * p->dt;
        vy += ay * p->dt;
        
        /* Обчислення миттєвої потужності джоулева розігріву P = q * (v . E) */
        double power = p->q * (vx * Ex + vy * Ey);
        total_work += power * p->dt;
        
        /* Оновлення координат */
        x += vx * p->dt;
        y += vy * p->dt;
        
        /* Моделювання випадкового розсіювання імпульсу */
        double r = (double)rand() / RAND_MAX;
        if (r < p_coll) {
            /* Хаотична теплова ізотропізація швидкості після зіткнення */
            double theta = 2.0 * PI * ((double)rand() / RAND_MAX);
            double v_thermal = sqrt(2.0 * 1.38e-23 * 4.2 / p->m_eff);
            vx = v_thermal * cos(theta);
            vy = v_thermal * sin(theta);
        }
    }
    
    return total_work / (p->steps * p->dt);
}

int main(void) {
    SimParams p;
    p.m_eff = 0.067 * 9.109e-31; /* GaAs електрона (m* = 0.067 m0) */
    p.q = -1.602e-19;
    p.B = 0.25;                  /* 0.25 Тесла */
    p.E0 = 100.0;                /* 100 В/м */
    p.tau = 1.0e-11;             /* 10 пікосекунд (чистий кристал при 4.2 K) */
    p.dt = 1.0e-14;              /* 10 фемтосекунд */
    p.steps = 500000;
    
    double wc = fabs(p.q * p.B / p.m_eff);
    printf("Циклотронна частота fc = %.3f GHz\n", wc / (2.0 * PI * 1e9));
    printf("Критерій гостроти wc * tau = %.2f\n\n", wc * p.tau);
    
    printf("  f (GHz)   | P_abs (умовн. од.)\n");
    printf("------------+-------------------\n");
    
    for (double f_ghz = 50.0; f_ghz <= 150.0; f_ghz += 5.0) {
        double omega = 2.0 * PI * f_ghz * 1e9;
        double p_abs = simulate_absorption(&p, omega);
        printf("  %7.1f   |   %11.4e\n", f_ghz, p_abs);
    }
    
    return 0;
}

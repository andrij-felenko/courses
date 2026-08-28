#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Конфігураційна структура параметрів осцилятора */
typedef struct {
    double m;       /* маса системи (кг) */
    double k;       /* жорсткість пружини (Н/м) */
    double c;       /* коефіцієнт в'язкого тертя (Н·с/м) */
    double f0;      /* амплітуда зовнішньої збуджувальної сили (Н) */
} OscillatorParams;

/* Структура для збереження однієї точки АЧХ */
typedef struct {
    double omega;   /* колова частота (рад/с) */
    double amp;     /* амплітуда сталого режиму (м) */
} AFCPoint;

/* Обчислення миттєвого прискорення в момент часу t */
static inline double compute_accel(const OscillatorParams *p, double x, double v, double f_ext) {
    return (f_ext - p->c * v - p->k * x) / p->m;
}

/**
 * @brief Провести симуляцію вимушених коливань на фіксованій частоті omega
 * @return Значення амплітуди сталого режиму (м)
 */
static double simulate_frequency(const OscillatorParams *p, 
                                 double omega, 
                                 double dt, 
                                 double t_settle, 
                                 double t_measure) 
{
    double x = 0.0;
    double v = 0.0;
    double t = 0.0;

    /* Початкове прискорення при t = 0 */
    double a = compute_accel(p, x, v, p->f0);

    /* 1. Фаза пропуску перехідного процесу (згасання власних коливань) */
    while (t < t_settle) {
        double f_next = p->f0 * cos(omega * (t + dt));
        
        /* Крок Верле у швидкостях */
        x += v * dt + 0.5 * a * dt * dt;
        double a_next = (f_next - p->c * v - p->k * x) / p->m;
        v += 0.5 * (a + a_next) * dt;
        
        a = a_next;
        t += dt;
    }

    /* 2. Фаза вимірювання максимуму амплітуди сталого режиму */
    double max_x = 0.0;
    double t_end = t_settle + t_measure;

    while (t < t_end) {
        double f_next = p->f0 * cos(omega * (t + dt));

        x += v * dt + 0.5 * a * dt * dt;
        double a_next = (f_next - p->c * v - p->k * x) / p->m;
        v += 0.5 * (a + a_next) * dt;

        a = a_next;
        t += dt;

        double abs_x = fabs(x);
        if (abs_x > max_x) {
            max_x = abs_x;
        }
    }

    return max_x;
}

int main(void) {
    OscillatorParams p = {
        .m = 1.0,     /* 1 кг */
        .k = 100.0,   /* w0 = sqrt(100/1) = 10 рад/с */
        .c = 1.0,     /* gamma = 1/(2*1) = 0.5, Q = 10 / 1 = 10 */
        .f0 = 10.0    /* A_stat = 10 / 100 = 0.1 м */
    };

    double w0_theory = sqrt(p.k / p.m);
    double gamma = p.c / (2.0 * p.m);
    double w_res_theory = sqrt(w0_theory * w0_theory - 2.0 * gamma * gamma);
    double q_theory = w0_theory / (2.0 * gamma);

    printf("=== ТЕОРЕТИЧНІ ЗНАЧЕННЯ ===\n");
    printf("Власна частота w0  : %.4f рад/с\n", w0_theory);
    printf("Резонансна частота : %.4f рад/с\n", w_res_theory);
    printf("Добротність Q      : %.2f\n\n", q_theory);

    /* Параметри сканування АЧХ */
    double w_min = 5.0;
    double w_max = 15.0;
    int num_steps = 100;
    double dw = (w_max - w_min) / num_steps;

    double dt = 0.001;        /* крок інтегрування 1 мс */
    double t_settle = 15.0;   /* 15 секунд на згасання власних коливань */
    double t_measure = 10.0;  /* 10 секунд на вимірювання */

    double best_omega = 0.0;
    double max_amplitude = 0.0;

    printf("=== ЧИСЕЛЬНЕ СКАНУВАННЯ АЧХ ===\n");
    printf("%-12s | %-16s | %-16s\n", "w (рад/с)", "Амплітуда (м)", "Відносна A/A_stat");
    printf("--------------------------------------------------\n");

    for (int i = 0; i <= num_steps; ++i) {
        double w = w_min + i * dw;
        double amp = simulate_frequency(&p, w, dt, t_settle, t_measure);
        double a_stat = p.f0 / p.k;
        
        if (amp > max_amplitude) {
            max_amplitude = amp;
            best_omega = w;
        }

        if (i % 10 == 0) {
            printf("%-12.2f | %-16.6f | %-16.2f\n", w, amp, amp / a_stat);
        }
    }

    printf("\n=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ ===\n");
    printf("Знайдена резонансна частота : %.4f рад/с (похибка: %.2f%%)\n", 
           best_omega, fabs(best_omega - w_res_theory) / w_res_theory * 100.0);
    printf("Максимальна амплітуда      : %.6f м\n", max_amplitude);
    printf("Чисельне підсилення A/A_stat: %.2f (Теорія Q ≈ %.2f)\n", 
           max_amplitude / (p.f0 / p.k), q_theory);

    return 0;
}

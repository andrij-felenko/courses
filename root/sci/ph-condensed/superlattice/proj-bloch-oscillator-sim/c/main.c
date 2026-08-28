#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define HBAR 1.054571817e-34    /* Зведена стала Планка (Дж·с) */
#define ELEMENTARY_CHARGE 1.602176634e-19 /* Заряд електрона (Кл) */

typedef struct {
    double period_d;     /* Період суперґратки (м) */
    double delta_joules; /* Ширина мінізони (Дж) */
    double tau_seconds;  /* Час релаксації імпульсу (с) */
    double dt;           /* Крок інтегрування за часом (с) */
    int num_particles;   /* Кількість частинок в ансамблі */
    int total_steps;     /* Загальна кількість кроків */
} SuperlatticeParams;

/* Обчислення миттєвої групової швидкості електрона */
static inline double get_group_velocity(double kz, double d, double delta) {
    return (delta * d / (2.0 * HBAR)) * sin(kz * d);
}

/* Генерація випадкового числа в інтервалі [0, 1] */
static inline double rand_uniform(void) {
    return (double)rand() / (double)RAND_MAX;
}

/* Моделювання ансамблю та розрахунок середньої швидкості для поля F_dc */
double simulate_drift_velocity(const SuperlatticeParams *p, double F_dc) {
    double total_velocity_sum = 0.0;
    double p_coll = 1.0 - exp(-p->dt / p->tau_seconds);

    /* Виділення пам'яті під масив квазіімпульсів частинок */
    double *kz = (double *)malloc((size_t)p->num_particles * sizeof(double));
    if (!kz) {
        fprintf(stderr, "Помилка виділення пам'яті для частинок.\n");
        return 0.0;
    }

    /* Ініціалізація носіїв біля дна зони */
    for (int i = 0; i < p->num_particles; i++) {
        kz[i] = 0.0;
    }

    double dk_dt = -ELEMENTARY_CHARGE * F_dc / HBAR;

    for (int step = 0; step < p->total_steps; step++) {
        double current_step_v_sum = 0.0;

        for (int i = 0; i < p->num_particles; i++) {
            /* Оновлення квазіімпульсу під дією поля */
            kz[i] += dk_dt * p->dt;

            /* Завернення у першу зону Бріллюена [-pi/d, pi/d] */
            while (kz[i] > PI / p->period_d)  kz[i] -= 2.0 * PI / p->period_d;
            while (kz[i] < -PI / p->period_d) kz[i] += 2.0 * PI / p->period_d;

            /* Перевірка умови Монте-Карло розсіювання */
            if (rand_uniform() < p_coll) {
                kz[i] = 0.0; /* Теплова релаксація */
            }

            current_step_v_sum += get_group_velocity(kz[i], p->period_d, p->delta_joules);
        }

        /* Накопичення даних після згасання перехідних процесів (друга половина симуляції) */
        if (step >= p->total_steps / 2) {
            total_velocity_sum += (current_step_v_sum / p->num_particles);
        }
    }

    free(kz);
    int sample_steps = p->total_steps / 2;
    return total_velocity_sum / (double)sample_steps;
}

int main(void) {
    SuperlatticeParams p;
    p.period_d = 6.0e-9;                           /* 6 нм */
    p.delta_joules = 50.0 * 1.60218e-22;            /* 50 меВ */
    p.tau_seconds = 0.5e-12;                        /* 0.5 пс */
    p.dt = 1.0e-15;                                 /* 1 фс */
    p.num_particles = 1000;                         /* 1000 електронів */
    p.total_steps = 20000;                          /* 20 пс загальний час */

    printf("Field_Vcm,DriftVel_cms,TheoryVel_cms\n");

    double F_c = HBAR / (ELEMENTARY_CHARGE * p.period_d * p.tau_seconds); /* В/м */
    double v_max = (p.delta_joules * p.period_d) / (4.0 * HBAR);            /* м/с */

    for (double F_kVcm = 0.5; F_kVcm <= 35.0; F_kVcm += 1.0) {
        double F_Vm = F_kVcm * 1.0e5; /* Переведення в В/м */
        double v_sim = simulate_drift_velocity(&p, F_Vm);
        
        /* Теоретична формула Есакі-Цо */
        double f_ratio = F_Vm / F_c;
        double v_theory = v_max * (2.0 * f_ratio) / (1.0 + f_ratio * f_ratio);

        printf("%.2f,%.4e,%.4e\n", F_kVcm, v_sim * 100.0, v_theory * 100.0);
    }

    return 0;
}

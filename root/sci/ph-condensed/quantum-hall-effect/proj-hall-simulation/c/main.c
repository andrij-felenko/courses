#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (SI) */
#define CONST_H  6.62607015e-34  /* Стала Планка (Дж·с) */
#define CONST_E  1.602176634e-19 /* Елементарний заряд (Кл) */
#define CONST_KB 1.380649e-23    /* Стала Больцмана (Дж/К) */
#define CONST_ME 9.1093837015e-31/* Маса електрона (кг) */

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для зберігання результатів в одній точці поля B */
typedef struct {
    double B;          /* Індукція магнітного поля (Тесла) */
    double nu;         /* Коефіцієнт заповнення ν */
    int i_filled;      /* Індекс найближчого плато i */
    double R_xy;       /* Розрахований опір Холла (Ом) */
    double R_xx;       /* Розрахований поздовжній опір (Ом) */
} qhe_point_t;

/* Структура фізичних параметрів зразка 2DEG */
typedef struct {
    double n_s;        /* Поверхнева густина носіїв (м^-2) */
    double m_eff;      /* Відносна ефективна маса (m* / m_e) */
    double temp;       /* Температура зразка (Кельвіни) */
    double mobility;   /* Рухливість носіїв (м^2 / В·с) */
} qhe_sample_t;

/* Обчислення транспортних характеристик QHE для однієї точки B */
qhe_point_t calculate_qhe_point(const qhe_sample_t *sample, double B) {
    qhe_point_t pt;
    pt.B = B;
    
    /* Густина станів одного рівня Ландау: n_B = e * B / h */
    double n_B = (CONST_E * B) / CONST_H;
    pt.nu = sample->n_s / n_B;
    
    /* Знайдемо найближче ціле число заповнених рівнів Ландау */
    int i_near = (int)floor(pt.nu + 0.5);
    if (i_near < 1) {
        i_near = 1;
    }
    pt.i_filled = i_near;
    
    /* Відхилення від цілого числа */
    double deviation = fabs(pt.nu - (double)i_near);
    double plateau_threshold = 0.15; /* Відносна ширина області локалізації */
    
    if (deviation < plateau_threshold) {
        /* Знаходимося на квантованому плато */
        pt.R_xy = CONST_H / ((double)i_near * CONST_E * CONST_E);
        
        /* Поздовжній опір експоненціально пригнічений термоактивацією */
        double m_kg = sample->m_eff * CONST_ME;
        double hbar = CONST_H / (2.0 * M_PI);
        double hw_c = (hbar * CONST_E * B) / m_kg;
        double thermal_suppression = exp(-hw_c / (2.0 * CONST_KB * sample->temp));
        pt.R_xx = 500.0 * thermal_suppression;
    } else {
        /* Перехідна область між плато (класичний нахил + пік розсіювання) */
        pt.R_xy = CONST_H / (pt.nu * CONST_E * CONST_E);
        
        /* Дисипативний пік R_xx на межі рівнів Ландау */
        double peak_shape = sin(M_PI * pt.nu);
        pt.R_xx = 1500.0 * (peak_shape * peak_shape);
    }
    
    return pt;
}

/* Проведення сканування за магнітним полем із виділенням динамічного масиву */
qhe_point_t* run_qhe_sweep(const qhe_sample_t *sample, double B_start, double B_end, int steps) {
    if (steps <= 1) return NULL;
    
    qhe_point_t *results = (qhe_point_t*)malloc(sizeof(qhe_point_t) * (size_t)steps);
    if (!results) {
        fprintf(stderr, "Помилка виділення пам'яті під результати симуляції.\n");
        return NULL;
    }
    
    double dB = (B_end - B_start) / (double)(steps - 1);
    for (int k = 0; k < steps; ++k) {
        double B = B_start + (double)k * dB;
        results[k] = calculate_qhe_point(sample, B);
    }
    
    return results;
}

int main(void) {
    qhe_sample_t gaas_sample = {
        .n_s = 3.2e15,     /* 3.2*10^15 м^-2 (GaAs/AlGaAs 2DEG) */
        .m_eff = 0.067,    /* Ефективна маса електрона у GaAs */
        .temp = 1.2,       /* 1.2 Кельвіна */
        .mobility = 60.0   /* Рухливість 60 м^2 / (В·с) */
    };
    
    double B_min = 1.0;
    double B_max = 8.5;
    int num_steps = 16;
    
    qhe_point_t *data = run_qhe_sweep(&gaas_sample, B_min, B_max, num_steps);
    if (!data) {
        return EXIT_FAILURE;
    }
    
    printf("===================================================================\n");
    printf("   СИМУЛЯЦІЯ ТРАНСПОРТУ QHE В ДВОВИМІРНОМУ ЕЛЕКТРОННОМУ ГАЗІ (C)   \n");
    printf("===================================================================\n");
    printf(" B (Тл)  | Factor nu | Index i |   R_xy (Ом)     |   R_xx (Ом)   \n");
    printf("-------------------------------------------------------------------\n");
    
    for (int k = 0; k < num_steps; ++k) {
        printf(" %6.2f  | %9.3f |   %2d    | %13.4f | %11.5f\n",
               data[k].B, data[k].nu, data[k].i_filled, data[k].R_xy, data[k].R_xx);
    }
    
    printf("-------------------------------------------------------------------\n");
    
    free(data);
    return EXIT_SUCCESS;
}

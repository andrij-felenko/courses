#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для збереження дискретної 3D-діаграми спрямованості */
typedef struct {
    int num_theta;       /* Кількість точок по куту theta (0..180 deg) */
    int num_phi;         /* Кількість точок по куту phi (0..360 deg) */
    double delta_theta;  /* Крок по theta в радіанах */
    double delta_phi;    /* Крок по phi в радіанах */
    double *pattern_u;   /* Одномерний розгорнутий масив U(theta, phi) */
} pattern_3d_t;

/* Структура підсумкових результатів 3D-інтегрування */
typedef struct {
    double p_rad;           /* Повна випромінювана потужність (Вт) */
    double u_max;           /* Максимальна інтенсивність (Вт/ср) */
    double directivity;     /* Коефіцієнт спрямованості (лінійний) */
    double directivity_dbi; /* Підсилення у дБі (dBi) */
    double beam_solid_angle;/* Тілесний кут променя (стерадіани) */
} pattern_results_t;

/* Створення та ініціалізація пам'яті під 3D-діаграму */
pattern_3d_t* pattern_create(int num_theta, int num_phi) {
    if (num_theta < 2 || num_phi < 2) return NULL;
    
    pattern_3d_t *p = (pattern_3d_t*)malloc(sizeof(pattern_3d_t));
    if (!p) return NULL;
    
    p->num_theta = num_theta;
    p->num_phi = num_phi;
    p->delta_theta = M_PI / (num_theta - 1);
    p->delta_phi = (2.0 * M_PI) / (num_phi - 1);
    p->pattern_u = (double*)calloc((size_t)num_theta * (size_t)num_phi, sizeof(double));
    
    if (!p->pattern_u) {
        free(p);
        return NULL;
    }
    return p;
}

/* Звільнення пам'яті */
void pattern_free(pattern_3d_t *p) {
    if (p) {
        if (p->pattern_u) free(p->pattern_u);
        free(p);
    }
}

/* Запис значення U(i, j) у масив */
void pattern_set(pattern_3d_t *p, int i, int j, double val) {
    if (p && p->pattern_u && i >= 0 && i < p->num_theta && j >= 0 && j < p->num_phi) {
        p->pattern_u[i * p->num_phi + j] = val;
    }
}

/* Зчитування значення U(i, j) */
double pattern_get(const pattern_3d_t *p, int i, int j) {
    if (!p || !p->pattern_u) return 0.0;
    return p->pattern_u[i * p->num_phi + j];
}

/* Чисельне сферичне інтегрування методом трапецій з вагою sin(theta) */
int pattern_integrate(const pattern_3d_t *p, pattern_results_t *res) {
    if (!p || !p->pattern_u || !res) return -1;
    
    double p_sum = 0.0;
    double max_u = 0.0;
    
    for (int i = 0; i < p->num_theta; ++i) {
        double theta = i * p->delta_theta;
        double sin_th = sin(theta);
        
        /* Вага за методом трапецій по куту theta */
        double w_theta = (i == 0 || i == p->num_theta - 1) ? 0.5 : 1.0;
        
        for (int j = 0; j < p->num_phi; ++j) {
            double u_val = pattern_get(p, i, j);
            if (u_val > max_u) {
                max_u = u_val;
            }
            
            /* Вага по куту phi */
            double w_phi = (j == 0 || j == p->num_phi - 1) ? 0.5 : 1.0;
            
            /* Елемент інтегрування: U(th, ph) * sin(th) * d_th * d_ph */
            double cell_power = u_val * sin_th * (w_theta * p->delta_theta) * (w_phi * p->delta_phi);
            p_sum += cell_power;
        }
    }
    
    res->p_rad = p_sum;
    res->u_max = max_u;
    if (p_sum > 1e-12 && max_u > 0.0) {
        res->directivity = (4.0 * M_PI * max_u) / p_sum;
        res->directivity_dbi = 10.0 * log10(res->directivity);
        res->beam_solid_angle = (4.0 * M_PI) / res->directivity;
    } else {
        res->directivity = 1.0;
        res->directivity_dbi = 0.0;
        res->beam_solid_angle = 4.0 * M_PI;
    }
    return 0;
}

int main(void) {
    int n_th = 181; /* Роздільна здатність 1 градус */
    int n_ph = 361;
    
    pattern_3d_t *pat = pattern_create(n_th, n_ph);
    if (!pat) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }
    
    /* Заповнення масиву тестовою 3D-діаграмою напівхвильового диполя: U(th) = sin^3(th) */
    for (int i = 0; i < n_th; ++i) {
        double theta = i * pat->delta_theta;
        double sin_th = sin(theta);
        double u_val = sin_th * sin_th * sin_th; /* sin^3(theta) */
        for (int j = 0; j < n_ph; ++j) {
            pattern_set(pat, i, j, u_val);
        }
    }
    
    pattern_results_t res;
    if (pattern_integrate(pat, &res) == 0) {
        printf("--- Результати 3D-інтегрування диполя (C) ---\n");
        printf("Повна потужність P_rad: %.4f Вт\n", res.p_rad);
        printf("Макс. інтенсивність U_max: %.4f Вт/ср\n", res.u_max);
        printf("КСД (Directivity):        %.3f (теорія: 1.643)\n", res.directivity);
        printf("Підсилення (dBi):         %.2f дБі (теорія: 2.15 дБі)\n", res.directivity_dbi);
        printf("Тілесний кут Omega_A:     %.3f ср\n", res.beam_solid_angle);
    }
    
    pattern_free(pat);
    return 0;
}

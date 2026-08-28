/* coupled_sim.c — Симплектичний інтегратор ланцюжка зв'язаних осциляторів мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    size_t num_masses;
    double *masses;       /* Масив мас [N] */
    double *pos;          /* Зсуви x_i [N] */
    double *vel;          /* Швидкості v_i [N] */
    double *acc;          /* Прискорення a_i [N] */
    double k_spring;      /* Жорсткість пружин зв'язку */
    double damping;       /* Коефіцієнт загасання */
} CoupledChainC;

/* Створення та ініціалізація структури ланцюжка осциляторів */
CoupledChainC* chain_create(size_t n, double m_val, double k_val, double c_val) {
    if (n == 0 || m_val <= 0.0 || k_val < 0.0) return NULL;
    
    CoupledChainC *c = (CoupledChainC*)malloc(sizeof(CoupledChainC));
    if (!c) return NULL;
    
    c->num_masses = n;
    c->k_spring = k_val;
    c->damping = c_val;
    
    c->masses = (double*)malloc(n * sizeof(double));
    c->pos = (double*)calloc(n, sizeof(double));
    c->vel = (double*)calloc(n, sizeof(double));
    c->acc = (double*)calloc(n, sizeof(double));
    
    if (!c->masses || !c->pos || !c->vel || !c->acc) {
        free(c->masses); free(c->pos); free(c->vel); free(c->acc);
        free(c);
        return NULL;
    }
    
    for (size_t i = 0; i < n; ++i) {
        c->masses[i] = m_val;
    }
    return c;
}

/* Безпечне звільнення пам'яті */
void chain_destroy(CoupledChainC *c) {
    if (!c) return;
    free(c->masses);
    free(c->pos);
    free(c->vel);
    free(c->acc);
    free(c);
}

/* Обчислення векторів прискорень для всіх мас у ланцюжку */
static void compute_accelerations(CoupledChainC *c) {
    size_t n = c->num_masses;
    double k = c->k_spring;
    double gamma = c->damping;
    
    for (size_t i = 0; i < n; ++i) {
        double f_total = 0.0;
        
        /* Пружна сила від лівого сусіда чи лівої стіни */
        double left_pos = (i == 0) ? 0.0 : c->pos[i - 1];
        f_total += -k * (c->pos[i] - left_pos);
        
        /* Пружна сила від правого сусіда чи правої стіни */
        double right_pos = (i == n - 1) ? 0.0 : c->pos[i + 1];
        f_total += -k * (c->pos[i] - right_pos);
        
        /* Демпфування (опір середовища) */
        f_total -= gamma * c->vel[i];
        
        c->acc[i] = f_total / c->masses[i];
    }
}

/* Крок чисельного інтегрування Velocity Verlet */
void chain_step(CoupledChainC *c, double dt) {
    size_t n = c->num_masses;
    
    /* 1. Оновлення координат і проміжних швидкостей */
    for (size_t i = 0; i < n; ++i) {
        c->pos[i] += c->vel[i] * dt + 0.5 * c->acc[i] * dt * dt;
        c->vel[i] += 0.5 * c->acc[i] * dt;
    }
    
    /* 2. Обчислення нових сил у нових позиціях */
    compute_accelerations(c);
    
    /* 3. Остаточне оновлення швидкостей */
    for (size_t i = 0; i < n; ++i) {
        c->vel[i] += 0.5 * c->acc[i] * dt;
    }
}

/* Точне обчислення повної механічної енергії системи (E_kin + E_pot) */
double chain_total_energy(const CoupledChainC *c) {
    size_t n = c->num_masses;
    double e_kin = 0.0;
    double e_pot = 0.0;
    double k = c->k_spring;
    
    for (size_t i = 0; i < n; ++i) {
        e_kin += 0.5 * c->masses[i] * c->vel[i] * c->vel[i];
        
        double left_pos = (i == 0) ? 0.0 : c->pos[i - 1];
        double delta = c->pos[i] - left_pos;
        e_pot += 0.5 * k * delta * delta;
    }
    /* Потенціальна енергія останньої пружини біля правої стіни */
    double delta_last = 0.0 - c->pos[n - 1];
    e_pot += 0.5 * k * delta_last * delta_last;
    
    return e_kin + e_pot;
}

/* lyapunov_lab.h - C API специфікація бібліотеки LyapunovLab */
#ifndef LYAPUNOV_LAB_H
#define LYAPUNOV_LAB_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та помилок */
typedef enum {
    LYAPUNOV_SUCCESS = 0,
    LYAPUNOV_ERROR_INVALID_DIM = -1,
    LYAPUNOV_ERROR_NULL_POINTER = -2,
    LYAPUNOV_ERROR_DIVERGENCE = -3,
    LYAPUNOV_ERROR_NO_MEMORY = -4
} LyapunovStatus;

/* Спосіб інтегрування */
typedef enum {
    LYAPUNOV_INTEGRATOR_RK4 = 0,
    LYAPUNOV_INTEGRATOR_DORMAND_PRINCE8 = 1
} LyapunovIntegratorType;

/* Функція правої частини f(t, x, dxdt, user_data) */
typedef void (*LyapunovRhsFunc)(double t, const double *x, double *dxdt, void *user_data);

/* Функція Якобіана J(t, x, J_flat, user_data) */
typedef void (*LyapunovJacobianFunc)(double t, const double *x, double *J_flat, void *user_data);

/* Конфігураційні параметри */
typedef struct {
    size_t dim;                   /* Розмірність фазового простору */
    double dt;                    /* Крок інтегрування */
    size_t total_steps;           /* Кількість робочих кроків */
    size_t transient_steps;       /* Кількість кроків для виходу на атрактор */
    size_t qr_period;             /* Період проведення QR-розкладу (в кроках) */
    LyapunovIntegratorType method;/* Метод чисельного інтегрування */
} LyapunovConfig;

/* Описувач динамічної системи */
typedef struct {
    LyapunovRhsFunc rhs;
    LyapunovJacobianFunc jacobian;
    void *user_data;
} LyapunovSystem;

/* Результати аналізу */
typedef struct {
    double *spectrum;             /* Масив показників Ляпунова (розмірність dim) */
    double lyapunov_dimension;    /* Розмірність Каплана–Йорке D_L */
    double lyapunov_time;         /* Час Ляпунова tau_L = 1 / lambda_max */
    double ks_entropy;            /* Метрична ентропія Песіна h_KS */
    bool is_chaotic;              /* Прапорець наявності хаосу (lambda_max > 0) */
} LyapunovMetrics;

/* Створення та ініціалізація метрик */
LyapunovMetrics* lyapunov_metrics_create(size_t dim);

/* Звільнення пам'яті метрик */
void lyapunov_metrics_destroy(LyapunovMetrics *metrics);

/* Основний виклик розрахунку спектра */
LyapunovStatus lyapunov_compute_spectrum(
    const LyapunovSystem *sys,
    const LyapunovConfig *cfg,
    const double *initial_state,
    LyapunovMetrics *out_metrics
);

/* Допоміжна функція отримання текстового опису помилки */
const char* lyapunov_status_string(LyapunovStatus status);

#ifdef __cplusplus
}
#endif

#endif /* LYAPUNOV_LAB_H */

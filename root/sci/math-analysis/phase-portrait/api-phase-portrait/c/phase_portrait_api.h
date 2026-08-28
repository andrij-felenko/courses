/* phase_portrait_api.h — Публічний C-інтерфейс бібліотеки libphase */
#ifndef PHASE_PORTRAIT_API_H
#define PHASE_PORTRAIT_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди повернення та статусів помилок */
typedef enum {
    PHASE_SUCCESS               =  0,  /* Успішне виконання операції */
    PHASE_ERROR_NULL_POINTER    = -1,  /* Передано нульовий вказівник */
    PHASE_ERROR_INVALID_PARAM   = -2,  /* Некоректні параметри (наприклад, step <= 0) */
    PHASE_ERROR_DIVERGENCE      = -3,  /* Траєкторія пішла в нескінченність (переповнення) */
    PHASE_ERROR_CONVERGENCE     = -4,  /* Не вдалося знайти особливу точку за макс. кроків */
    PHASE_ERROR_ALLOCATION      = -5   /* Помилка виділення пам'яті */
} PhaseStatus;

/* Точка у двовимірному фазовому просторі (q, p) */
typedef struct {
    double q; /* Узагальнена координата */
    double p; /* Узагальнений імпульс або швидкість */
} PhasePoint;

/* Похідні стану (dq/dt, dp/dt) */
typedef struct {
    double dq_dt;
    double dp_dt;
} PhaseDerivs;

/* Прототип функції правих частин системи: F(t, state, user_data, derivs) */
typedef void (*PhaseVectorFieldFn)(double t, const PhasePoint* state, void* user_data, PhaseDerivs* derivs);

/* Структура опису динамічної системи */
typedef struct {
    PhaseVectorFieldFn field_fn; /* Вказівник на функцію поля */
    void* user_data;             /* Довільні параметри фізичної моделі */
} PhaseSystem;

/* Класифікаційний тип особливої точки */
typedef enum {
    SINGULAR_SADDLE = 0,
    SINGULAR_CENTER,
    SINGULAR_FOCUS_STABLE,
    SINGULAR_FOCUS_UNSTABLE,
    SINGULAR_NODE_STABLE,
    SINGULAR_NODE_UNSTABLE,
    SINGULAR_DEGENERATE
} PhaseSingularType;

/* Детальний опишувач особливої точки */
typedef struct {
    PhasePoint point;           /* Координати особливої точки (q0, p0) */
    double jacobian[2][2];      /* Матриця Якобі J у цій точці */
    double trace;               /* Слід Tr(J) */
    double det;                 /* Детермінант Det(J) */
    double discr;               /* Дискримінант (Tr J)^2 - 4*Det */
    double lambda1_re;          /* Дійсна частина першого власного значення */
    double lambda1_im;          /* Уявна частина першого власного значення */
    double lambda2_re;          /* Дійсна частина другого власного значення */
    double lambda2_im;          /* Уявна частина другого власного значення */
    PhaseSingularType type;     /* Топологічний тип точки */
} SingularPointInfo;

/* Конфігурація сітки фазового поля */
typedef struct {
    double q_min;
    double q_max;
    size_t q_steps;
    double p_min;
    double p_max;
    size_t p_steps;
} PhaseGridConfig;

/* Запис одного вектора сітки */
typedef struct {
    PhasePoint point;
    PhaseDerivs derivs;
    double magnitude;
} PhaseGridVector;

/* === ОСНОВНІ ФУНКЦІЇ АНАЛІТИЧНОГО ТА ЧИСЕЛЬНОГО АПІ === */

/**
 * @brief Обчислити один крок інтегрування методом RK4.
 * @param sys Посилання на систему.
 * @param current Поточний фазовий стан.
 * @param t Поточний час.
 * @param h Крок інтегрування.
 * @param next [out] Результат наступного стану.
 * @return PHASE_SUCCESS або код помилки.
 */
PhaseStatus phase_rk4_step(const PhaseSystem* sys, const PhasePoint* current, double t, double h, PhasePoint* next);

/**
 * @brief Проінтегрувати повну траєкторію та зберегти в масив.
 * @param sys Посилання на систему.
 * @param initial Початковий стан.
 * @param h Крок за часом.
 * @param steps Кількість кроків.
 * @param out_buffer [out] Виділений масив розміром (steps + 1) PhasePoint.
 * @return PHASE_SUCCESS або код помилки.
 */
PhaseStatus phase_integrate_trajectory(const PhaseSystem* sys, const PhasePoint* initial, double h, size_t steps, PhasePoint* out_buffer);

/**
 * @brief Обчислити матрицю Якобі чисельним диференціюванням у заданій точці.
 * @param sys Посилання на систему.
 * @param pt Точка, у якій обчислюється Якобіан.
 * @param eps Приріст для чисельної похідної (наприклад, 1e-6).
 * @param jacobian [out] Матриця 2x2.
 */
PhaseStatus phase_compute_jacobian(const PhaseSystem* sys, const PhasePoint* pt, double eps, double jacobian[2][2]);

/**
 * @brief Проаналізувати та класифікувати особливу точку.
 * @param sys Посилання на систему.
 * @param pt Точка рівноваги (де f=0, g=0).
 * @param info [out] Детальна структура аналізу.
 */
PhaseStatus phase_analyze_singular_point(const PhaseSystem* sys, const PhasePoint* pt, SingularPointInfo* info);

/**
 * @brief Сформувати масив векторів поля на прямокутній сітці.
 * @param sys Посилання на систему.
 * @param config Параметри сітки.
 * @param out_grid [out] Виділений буфер розміром (q_steps * p_steps) PhaseGridVector.
 */
PhaseStatus phase_generate_grid(const PhaseSystem* sys, const PhaseGridConfig* config, PhaseGridVector* out_grid);

#ifdef __cplusplus
}
#endif

#endif /* PHASE_PORTRAIT_API_H */

typedef enum {
    VORTEX_SUCCESS                  =  0,  /* Операція виконана успішно */
    VORTEX_ERR_INVALID_PARAM        = -1,  /* Некоректний параметр (NULL, N <= 0, dt <= 0) */
    VORTEX_ERR_OUT_OF_MEMORY        = -2,  /* Помилка виділення пам'яті */
    VORTEX_ERR_CORE_SINGULARITY     = -3,  /* Відстань між вихорами < ε при вимкненій регуляризації */
    VORTEX_ERR_INTEGRATION_DIVERGED  = -4,  /* Чисельна незбіжність (координати прямують до NaN/Inf) */
    VORTEX_ERR_DIMENSION_MISMATCH   = -5   /* Несумісність виміру домену (очікувалося 2D замість 3D) */
} vortex_status_t;

typedef enum {
    VORTEX_CORE_SINGULAR   = 0,  /* Точковий вихор Біо — Савара без регуляризації (1/r) */
    VORTEX_CORE_KRASNY     = 1,  /* Ядро Красного: 1 / (r² + ε²) */
    VORTEX_CORE_LAMB_OSEEN = 2   /* Ядро Лемба — Осеєна з в'язкою дифузією ядра: 1 - exp(-r²/ε²) */
} vortex_core_type_t;

typedef enum {
    VORTEX_INTEGRATOR_EULER = 0,  /* Метод Ейлера 1-го порядку (лише для тестів) */
    VORTEX_INTEGRATOR_RK4   = 1   /* Метод Рунге — Кутти 4-го порядку */
} vortex_integrator_type_t;

typedef struct {
    double x;         /* Положення за віссю X [м] */
    double y;         /* Положення за віссю Y [м] */
    double z;         /* Положення за віссю Z [м] (0.0 для 2D) */
    double gamma;     /* Інтенсивність вихору (циркуляція Г) [м²/с] */
} vortex_point_t;

typedef struct {
    int num_vortices;                   /* Кількість вихорів у системі */
    double core_radius_eps;             /* Радіус ядра регуляризації ε [м] */
    vortex_core_type_t core_type;       /* Тип ядра регуляризації Біо — Савара */
    vortex_integrator_type_t integrator;/* Схема чисельного інтегрування */
    double dt;                          /* Крок інтегрування за часом [с] */
    int is_3d;                          /* Прапорець 3D системи (1 — 3D нитки, 0 — 2D точки) */
} vortex_solver_config_t;

typedef struct {
    double total_circulation;    /* Сумарна циркуляція ∑ Г_i */
    double center_of_vorticity_x;/* Центр вихореності X_com = ∑(Г_i * x_i) / ∑Г_i */
    double center_of_vorticity_y;/* Центр вихореності Y_com = ∑(Г_i * y_i) / ∑Г_i */
    double angular_momentum;     /* Момент імпульсу M = ∑ Г_i * (x_i² + y_i²) */
    double kinetic_energy;       /* Квазі-енергія взаємодії E = -1/(4π) ∑∑ Г_i Г_j ln(r_ij) */
} vortex_invariants_t;

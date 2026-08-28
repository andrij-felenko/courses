/* C99: Структури параметрів та точок у henon.h */

typedef struct {
    double a; /* Параметр нелінійності згину фазової площини (за замовчуванням 1.4) */
    double b; /* Параметр дисипативності та стискання площі (за замовчуванням 0.3) */
} henon_params_t;

typedef struct {
    double x; /* Координата x фазового стану */
    double y; /* Координата y фазового стану */
} henon_point_t;

typedef struct {
    double lambda_1;     /* Старший показник Ляпунова */
    double lambda_2;     /* Молодший показник Ляпунова */
    double kaplan_yorke; /* Оцінка фрактальної розмірності D_KY */
    bool converged;      /* Прапорець успішної збіжності */
} henon_lyapunov_t;

typedef struct {
    henon_point_t p1;   /* Первинна нерухома точка (головне сідло) */
    henon_point_t p2;   /* Вторинна нерухома точка (граничне сідло) */
    bool is_real;       /* Прапорець дійсності коренів (true при D > 0) */
} henon_fixed_points_t;

typedef enum {
    HENON_OK = 0,                  /* Успішне завершення операції */
    HENON_ERROR_DIVERGED = 1,      /* Траєкторія розбіглася (|x| > 1e4) */
    HENON_ERROR_INVALID_PARAM = 2, /* Вироджені параметри (b == 0) */
    HENON_ERROR_NULL_POINTER = 3   /* Передано нульовий вказівник */
} henon_status_t;

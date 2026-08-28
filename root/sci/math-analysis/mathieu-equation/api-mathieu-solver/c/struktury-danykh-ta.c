/* C ABI переліки та структури даних бібліотеки libmathieu */
typedef enum {
    MATHIEU_SUCCESS               =  0,  /* Успішне виконання */
    MATHIEU_ERR_INVALID_PARAM     = -1,  /* Некоректні вхідні параметри */
    MATHIEU_ERR_NO_CONVERGENCE    = -2,  /* Ланцюговий дріб не збігся */
    MATHIEU_ERR_OUT_OF_MEMORY     = -3,  /* Помилка виділення пам'яті */
    MATHIEU_ERR_DIVERGENCE        = -4   /* Чисельна нестійкість розв'язку */
} MathieuStatus;

typedef enum {
    MATHIEU_METHOD_RK4            = 0,  /* Метод Рунге — Кутти 4-го порядку */
    MATHIEU_METHOD_DORMAND_PRINCE = 1,  /* Метод Дормана — Принса RK45 */
    MATHIEU_METHOD_CONT_FRACTIONS = 2   /* Метод ланцюгових дробів Інса */
} MathieuMethod;

typedef enum {
    MATHIEU_STATE_STABLE          = 0,  /* Область стійкості (|Tr(M)| < 2) */
    MATHIEU_STATE_UNSTABLE        = 1,  /* Область параметричного резонансу */
    MATHIEU_STATE_BOUNDARY        = 2   /* Точна межа стійкості */
} MathieuStabilityState;

typedef struct {
    MathieuMethod method;       /* Вибраний алгоритм обчислення */
    int period_steps;           /* Кількість кроків на період pi */
    double abs_tolerance;       /* Абсолютна точність */
    double rel_tolerance;       /* Відносна точність */
    int max_iterations;         /* Максимальна кількість ітерацій */
} MathieuConfig;

typedef struct {
    double a;                   /* Спектральний параметр a */
    double q;                   /* Параметр модуляції q */
    double monodromy[2][2];     /* Матриця монодромії M = Φ(pi) */
    double trace;               /* Слід Tr(M) */
    double floquet_exponent;    /* Дійсний показник Флоке mu */
    double floquet_nu;          /* Уявний показник nu */
    MathieuStabilityState state;/* Статус стійкості */
} MathieuPointResult;

typedef struct {
    double q_min, q_max;        /* Діапазон параметра q */
    double a_min, a_max;        /* Діапазон параметра a */
    size_t q_res, a_res;        /* Роздільна здатність */
    MathieuStabilityState* grid;/* Динамічний масив сітки */
} MathieuGrid;

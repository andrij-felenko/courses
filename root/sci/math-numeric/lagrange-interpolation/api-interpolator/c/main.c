/**
 * @brief Перелічувальний тип статусів виконання операцій у C-API.
 */
typedef enum {
    INTERP_SUCCESS               =  0,  /**< Операцію виконано успішно */
    INTERP_ERR_NULL_POINTER      = -1,  /**< Передано нульовий вказівник */
    INTERP_ERR_INVALID_SIZE      = -2,  /**< Некоректний розмір масиву (n < 1) */
    INTERP_ERR_DUPLICATE_NODE    = -3,  /**< Знайдено однакові x-вузли (ділення на 0) */
    INTERP_ERR_ALLOC_FAILED      = -4,  /**< Помилка виділення динамічної пам'яті */
    INTERP_ERR_OUT_OF_BOUNDS     = -5,  /**< Точка x виходить за межі інтервалу */
    INTERP_ERR_SINGULAR_MODULO   = -6   /**< Нульовий або непросний модуль u у GF(p) */
} interp_status_t;

/**
 * @brief Дескриптор барицентричного інтерполятора другої родини.
 */
typedef struct {
    double*          x_nodes;   /**< Динамічний масив вузлів x_k */
    double*          y_nodes;   /**< Динамічний масив значень y_k */
    double*          weights;   /**< Попередньо обчислені ваги w_k */
    size_t           count;     /**< Поточна кількість вузлів n */
    size_t           capacity;  /**< Виділена ємність масивів */
    double           eps;       /**< Поріг порівняння вузлів на рівність */
    bool             is_ready;  /**< Прапорець готовності ваг w_k */
} barycentric_interp_t;

/**
 * @brief Дескриптор криптографічного інтерполятора GF(p).
 */
typedef struct {
    int64_t*         x_shares;  /**< Масив x-координат часток */
    int64_t*         y_shares;  /**< Масив y-координат часток */
    size_t           count;     /**< Кількість часток k */
    int64_t          prime_mod; /**< Просте число p (модуль поля) */
} gf_interp_t;

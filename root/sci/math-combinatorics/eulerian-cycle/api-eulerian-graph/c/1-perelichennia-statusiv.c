typedef enum {
    EULER_SUCCESS                 =  0, /* Операція успішно виконана */
    EULER_ERR_NULL_POINTER        = -1, /* Передано нульовий покажчик (NULL) */
    EULER_ERR_INVALID_VERTEX      = -2, /* Індекс вершини виходить за межі [0, V-1] */
    EULER_ERR_OUT_OF_MEMORY       = -3, /* Помилка виділення динамічної пам'яті */
    EULER_ERR_NOT_EULERIAN        = -4, /* Граф не задовольняє умові парності степеней */
    EULER_ERR_DISCONNECTED        = -5, /* Ребра належать кільком компонентам */
    EULER_ERR_NO_PATH_EXISTS      = -6, /* Ейлерів шлях/цикл не існує */
    EULER_ERR_EMPTY_GRAPH         = -7, /* Граф не містить жодного ребра */
    EULER_ERR_FROZEN_GRAPH        = -8  /* Спроба модифікації заклиненого графа */
} euler_status_t;

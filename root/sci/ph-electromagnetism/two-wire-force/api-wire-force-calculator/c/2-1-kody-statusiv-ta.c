typedef enum wf_status {
    WF_SUCCESS                  =  0,  /* Операція виконана успішно */
    WF_ERR_NULL_POINTER         = -1,  /* Передано вказівник NULL */
    WF_ERR_INVALID_CURRENT      = -2,  /* Некоректне значення струму (<= 0) */
    WF_ERR_INVALID_DISTANCE     = -3,  /* Некоректна відстань між осями (<= 0) */
    WF_ERR_INVALID_SPAN         = -4,  /* Довжина прольоту <= 0 */
    WF_ERR_INVALID_GEOMETRY     = -5,  /* Від'ємні або нульові розміри шини */
    WF_ERR_INVALID_SHOCK_FACTOR = -6,  /* Ударний коефіцієнт k_th поза межами [1.0, 2.0] */
    WF_ERR_STRESS_EXCEEDED      = -10, /* Механічне напруження перевищує межу плинності */
    WF_ERR_INSULATOR_OVERLOAD   = -11  /* Навантаження на ізолятор перевищує допустиме */
} wf_status_t;

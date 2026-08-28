/**
 * @brief Типи помилок виконання оцінювача P/poly (C API)
 */
typedef enum {
    P_POLY_OK                  =  0,  /* Успішне виконання */
    P_POLY_ERR_NULL_PTR        = -1,  /* Передано нулевий вказівник */
    P_POLY_ERR_INVALID_CIRCUIT = -2,  /* Некоректна топологія DAG (цикл або битий індекс) */
    P_POLY_ERR_INPUT_MISMATCH  = -3,  /* Невідповідність довжини входу |x| != n */
    P_POLY_ERR_ADVICE_MISMATCH = -4,  /* Довжина підказки перевищує поліноміальний ліміт */
    P_POLY_ERR_OUT_OF_MEMORY   = -5   /* Нестача пам'яті під час виділення буфера */
} PPolyStatus;

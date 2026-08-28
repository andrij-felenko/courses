typedef enum {
    NATURAL_SUCCESS               =  0,  /* Операцію виконано успішно */
    NATURAL_ERROR_NULL_POINTER    = -1,  /* Передано недійсний NULL вказівник */
    NATURAL_ERROR_INVALID_VARS    = -2,  /* Некоректна кількість змінних (допустимо 1..20) */
    NATURAL_ERROR_INVALID_TABLE   = -3,  /* Розмір таблиці істинності не відповідає 2^n */
    NATURAL_ERROR_OUT_OF_MEMORY   = -4,  /* Не вдалося виділити необхідну пам'ять */
    NATURAL_ERROR_TIMEOUT         = -5,  /* Перевищено ліміт часу для конструктивної перевірки */
    NATURAL_ERROR_PRG_FAILURE     = -6,  /* Помилка генерації псевдовипадкових функцій */
    NATURAL_ERROR_INTERNAL        = -7   /* Внутрішній збій обчислювального ядра */
} natural_error_t;

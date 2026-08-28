/* Перелік статусних кодів операцій мовою C */
typedef enum {
    ST_SUCCESS                 =  0, /* Операцію виконано успішно */
    ST_ERROR_NULL_POINTER      = -1, /* Передано нульовий вказівник */
    ST_ERROR_EMPTY_ARRAY       = -2, /* Розмір масиву n дорівнює нулю */
    ST_ERROR_ALLOCATION_FAILED = -3, /* Не вдалося виділити пам'ять */
    ST_ERROR_INVALID_RANGE     = -4, /* Ліва межа більша за праву (L > R) */
    ST_ERROR_OUT_OF_BOUNDS     = -5, /* Межі виходять за розмір масиву */
    ST_ERROR_INTEGER_OVERFLOW  = -6  /* Переповнення розміру буфера */
} st_status_t;

/* Константи кодів завершення */
#define HUNGARIAN_OK                 0
#define HUNGARIAN_ERR_NULL_PTR      -1
#define HUNGARIAN_ERR_INVALID_DIM   -2
#define HUNGARIAN_ERR_NO_MEMORY     -3
#define HUNGARIAN_INF (INT64_MAX / 4)

/* Режим оптимізації */
typedef enum {
    HUNGARIAN_OPT_MINIMIZE = 0,
    HUNGARIAN_OPT_MAXIMIZE = 1
} HungarianOptMode;

/* Структура результату призначення */
typedef struct {
    int64_t total_cost;      /* Сумарна вартість знайденого оптимального розподілу */
    int32_t* assignment;     /* Масив розміром rows: assignment[i] містить індекс стовпця (0..cols-1) */
    int32_t rows;            /* Кількість рядків (виконавців) */
    int32_t cols;            /* Кількість стовпців (завдань) */
    int32_t status;          /* Код завершення (HUNGARIAN_OK або код помилки) */
} HungarianResultC;

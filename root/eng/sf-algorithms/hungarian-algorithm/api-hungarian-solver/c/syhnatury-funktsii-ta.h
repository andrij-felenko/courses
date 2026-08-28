/* Ініціалізація структури результату */
HungarianResultC hungarian_result_init(int32_t rows, int32_t cols);

/* Звільнення динамічної пам'яті результату */
void hungarian_result_free(HungarianResultC* res);

/* Основна функція розв'язання задачі */
int32_t hungarian_solve_c(
    const int64_t* matrix,
    int32_t rows,
    int32_t cols,
    HungarianOptMode mode,
    HungarianResultC* out_result
);

typedef enum {
    TAKENS_OK                     =  0,  /* Успішне виконання операції */
    TAKENS_ERR_NULL_POINTER       = -1,  /* Передано вказівник NULL у критичний параметр */
    TAKENS_ERR_INVALID_PARAM      = -2,  /* Некоректне значення параметрів (наприклад, delay=0 чи n_bins=0) */
    TAKENS_ERR_SIGNAL_TOO_SHORT   = -3,  /* Довжина часового ряду є недостатньою для вказаних m та delay */
    TAKENS_ERR_OUT_OF_MEMORY      = -4,  /* Помилка виділення динамічної пам'яті у купі */
    TAKENS_ERR_NO_MINIMUM_FOUND   = -5,  /* У заданому діапазоні не знайдено локального мінімуму взаємної інформації */
    TAKENS_ERR_FNN_CONVERGENCE    = -6,  /* Дріб FNN не досяг заданого порогу при m <= max_m */
    TAKENS_ERR_ZERO_VARIANCE      = -7   /* Вхідний сигнал має нульову дисперсію (константний сигнал) */
} TakensStatus;

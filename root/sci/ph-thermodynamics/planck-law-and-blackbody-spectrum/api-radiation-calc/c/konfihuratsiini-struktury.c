/* Структура фізичних констант CODATA 2018 */
typedef struct {
    double h;     /* Стала Планка (Дж·с) */
    double c;     /* Швидкість світла (м/с) */
    double k_b;   /* Стала Больцмана (Дж/К) */
    double sigma; /* Стала Стефана-Больцмана (Вт/(м²·К⁴)) */
    double b_wien;/* Стала зміщення Віна (м·К) */
} bb_constants_t;

/* Налаштування чисельного інтегрування */
typedef struct {
    size_t max_subintervals; /* Максимальна кількість підінтервалів */
    double rel_tolerance;    /* Відносна допустима похибка (наприклад, 1e-8) */
    double abs_tolerance;    /* Абсолютна допустима похибка */
    bool use_gauss_legendre; /* true: Гаусс-Лежандр, false: Сімпсон */
} bb_integration_config_t;

/* Результат обчислення спектрального діапазону */
typedef struct {
    double integrated_radiance; /* Інтегральна яскравість (Вт/(м²·ст)) */
    double integrated_emittance;/* Повна випромінювальна здатність (Вт/м²) */
    double peak_wavelength;     /* Довжина хвилі максимуму (м) */
    double estimated_error;     /* Оцінка похибки чисельного інтегрування */
} bb_band_result_t;

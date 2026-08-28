/* Отримання незміщеної вибіркової дисперсії (s²) */
double welford_sample_variance(const welford_acc_t *acc);

/* Отримання генеральної дисперсії (σ²) */
double welford_population_variance(const welford_acc_t *acc);

/* Отримання вибіркового середньоквадратичного відхилення (s) */
double welford_stddev(const welford_acc_t *acc);

/* Отримання коефіцієнта асиметрії вибірки (g1) */
double welford_skewness(const welford_acc_t *acc);

/* Отримання коефіцієнта ексцесу (g2, excess kurtosis) */
double welford_kurtosis(const welford_acc_t *acc);

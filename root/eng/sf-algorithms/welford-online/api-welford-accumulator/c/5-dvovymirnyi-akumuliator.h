typedef struct {
    uint64_t count;      /* Кількість пар спостережень (n) */
    double mean_x;       /* Поточне середнє змінної X */
    double mean_y;       /* Поточне середнє змінної Y */
    double M2_x;         /* Сума квадратів відхилень X: ∑(x - μ_x)² */
    double M2_y;         /* Сума квадратів відхилень Y: ∑(y - μ_y)² */
    double C_xy;         /* Сума добутків відхилень: ∑(x - μ_x)(y - μ_y) */
} welford_cov_acc_t;

void welford_cov_init(welford_cov_acc_t *acc);
void welford_cov_push(welford_cov_acc_t *acc, double x, double y);
double welford_covariance(const welford_cov_acc_t *acc);
double welford_correlation(const welford_cov_acc_t *acc);

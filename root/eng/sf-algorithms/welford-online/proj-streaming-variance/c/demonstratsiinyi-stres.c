int main(void) {
    const double raw_data[5] = {
        1000000001.0, 1000000002.0, 1000000003.0, 1000000004.0, 1000000005.0
    };

    /* 1. Наївний однопрохідний підхід */
    double sum1 = 0.0, sum2 = 0.0;
    for (int i = 0; i < 5; ++i) {
        sum1 += raw_data[i];
        sum2 += raw_data[i] * raw_data[i];
    }
    double naive_var = (sum2 - (sum1 * sum1) / 5.0) / 4.0;

    /* 2. Алгоритм Велфорда */
    welford_acc_t acc;
    welford_init(&acc);
    welford_push_batch(&acc, raw_data, 5);
    double welford_var = welford_sample_variance(&acc);

    printf("Очікувана дисперсія : 2.5000000000\n");
    printf("Наївна формула      : %.10f (похибка катастрофічного скасування!)\n", naive_var);
    printf("Алгоритм Велфорда   : %.10f (ідеальний збіг)\n", welford_var);

    return 0;
}

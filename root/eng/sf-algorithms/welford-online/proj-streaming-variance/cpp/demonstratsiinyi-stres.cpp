int main() {
    const std::vector<double> raw_data = {
        1000000001.0, 1000000002.0, 1000000003.0, 1000000004.0, 1000000005.0
    };

    /* 1. Наївний метод */
    double sum1 = 0.0, sum2 = 0.0;
    for (double x : raw_data) {
        sum1 += x;
        sum2 += x * x;
    }
    const double naive_var = (sum2 - (sum1 * sum1) / 5.0) / 4.0;

    /* 2. Акумулятор Велфорда */
    StreamingAccumulator<double> acc;
    acc.push_batch(raw_data);
    const double welford_var = acc.sample_variance();

    std::cout << "Очікувана дисперсія : 2.5000000000\n";
    std::cout << "Наївна формула      : " << naive_var << " (повна втрата точності!)\n";
    std::cout << "Алгоритм Велфорда   : " << welford_var << " (абсолютна точність)\n";

    return 0;
}

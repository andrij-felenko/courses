// Поріг за процентилем сили: T_high такий, що вище нього — верхні (1-keep) пікселів.
// keep, напр., 0.7 → відсікаємо верхні 30% як «сильні кандидати». Сила в [0..MAXMAG).
static int high_threshold_by_percentile(const int *mag, int n,
                                        int maxmag, double keep) {
    std::vector<int> hist(maxmag, 0);
    for (int i = 0; i < n; i++) {
        int m = mag[i];
        if (m >= maxmag) m = maxmag - 1;     // захист від виходу за гістограму
        hist[m]++;
    }
    long target = static_cast<long>(keep * n);  // стільки лишаємо НИЖЧЕ порога
    long acc = 0;
    int t = 0;
    for (; t < maxmag; t++) {                 // йдемо від слабких угору
        acc += hist[t];
        if (acc >= target) break;             // тут накопичили keep частку
    }
    return t;                                 // T_high; T_low беремо як t/2..t/3
}

// Швидке піднесення a до степеня b за модулем m
long long powerMod(long long a, long long b, long long m) {
    long long result = 1;
    a = a % m;
    while (b > 0) {
        if (b % 2 == 1) {
            result = (result * a) % m;
        }
        b /= 2;
        a = (a * a) % m;
    }
    return result;
}

// Знаходження оберненого елемента за модулем m (m обов'язково має бути простим)
long long modInverseFermat(long long a, long long m) {
    return powerMod(a, m - 2, m);
}

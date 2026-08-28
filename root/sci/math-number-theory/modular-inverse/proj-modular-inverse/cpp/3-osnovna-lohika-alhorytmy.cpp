// Розширений алгоритм Евкліда
// Повертає кортеж (gcd(a, b), x, y) такі, що a*x + b*y = gcd(a, b)
std::tuple<long long, long long, long long> extendedGcd(long long a, long long b) {
    if (b == 0) {
        return {a, 1, 0};
    }
    auto [gcd, x1, y1] = extendedGcd(b, a % b);
    long long x = y1;
    long long y = x1 - y1 * (a / b);
    return {gcd, x, y};
}

// Знаходження оберненого елемента за модулем m через алгоритм Евкліда
long long modInverseGcd(long long a, long long m) {
    auto [gcd, x, y] = extendedGcd(a, m);
    if (gcd != 1) {
        throw std::invalid_argument("Оберненого елемента не існує (числа не взаємно прості)");
    }
    return (x % m + m) % m; // Забезпечення додатного результату
}

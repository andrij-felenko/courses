template <typename T>
    requires std::integral<T> // Концепт: перевірка типу під час компіляції
T fast_gcd(T a, T b)
    pre: a > 0 && b > 0     // Контракт: перевірка числових значень
    post(g): g > 0 && (a % g == 0) && (b % g == 0)
{
    while (b != 0) {
        T t = b;
        b = a % b;
        a = t;
    }
    return a;
}

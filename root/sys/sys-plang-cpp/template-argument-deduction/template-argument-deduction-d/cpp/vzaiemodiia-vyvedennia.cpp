template<typename T>
requires std::integral<T>
T fast_gcd(T a, T b) {
    while (b != 0) {
        T t = b;
        b = a % b;
        a = t;
    }
    return a;
}

// fast_gcd(12, 18); // T = int, обмеження std::integral<int> виконується ⇒ УСПІХ
// fast_gcd(12.0, 18.0); // T = double, std::integral<double> хибний ⇒ відхилення кандидата

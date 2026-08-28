#include <cstdint>

// xⁿ для n ≥ 0; unsigned робить «n ≥ 0» фактом типу, а не обіцянкою в коментарі.
// ПЕРЕДУМОВА: жодне проміжне множення не виходить за межі T (див. пастку нижче).
template <class T>
T power(T x, unsigned n) {
    if (n == 0) return T{1};
    T half = power(x, n / 2);
    return (n % 2 == 0) ? half * half : half * half * x;
}

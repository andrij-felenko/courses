#include <cstdint>

struct Mat { std::uint64_t a, b, c, d; };        // [[a b],[c d]]

Mat mul(const Mat& x, const Mat& y) {
    return { x.a*y.a + x.b*y.c,  x.a*y.b + x.b*y.d,
             x.c*y.a + x.d*y.c,  x.c*y.b + x.d*y.d };
}

std::uint64_t fib_matrix(int n) {
    Mat r{1, 0, 0, 1};                           // одинична матриця
    Mat q{1, 1, 1, 0};                           // матриця кроку Q
    while (n > 0) {
        if (n & 1) r = mul(r, q);                // накопичуємо Q у потрібних розрядах
        q = mul(q, q);                           // Q, Q², Q⁴, Q⁸, …
        n >>= 1;
    }
    return r.b;                                   // верхній-правий елемент Qⁿ — це Fₙ
}

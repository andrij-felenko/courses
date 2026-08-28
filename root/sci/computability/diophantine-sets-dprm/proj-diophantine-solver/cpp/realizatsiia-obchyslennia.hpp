#include <iostream>
#include <vector>
#include <span>
#include <cstdint>

struct JSWWPolynomial {
    static int64_t evaluate(std::span<const int64_t, 26> v) noexcept {
        const int64_t a = v[0],  b = v[1],  c = v[2],  d = v[3],  e = v[4],  f = v[5],
                      g = v[6],  h = v[7],  i = v[8],  j = v[9],  k = v[10], l = v[11],
                      m = v[12], n = v[13], o = v[14], p = v[15], q = v[16], r = v[17],
                      s = v[18], t = v[19], u = v[20], w = v[21], x = v[22], y = v[23],
                      z = v[24], k_val = v[10];

        const int64_t e1  = w * z + h + j - q;
        const int64_t e2  = (g * k + 2 * g + k + 1) * (h + j) + h - z;
        const int64_t e3  = 16 * (k + 1) * (k + 1) * (z + 1) * (z + 1) + 1 - f * f;
        const int64_t e4  = 2 * n + p + q + z - e;
        const int64_t e5  = e * e * e * (e + 2) * (a + 1) * (a + 1) + 1 - o * o;
        const int64_t e6  = (a * a - 1) * y * y + 1 - x * x;
        const int64_t e7  = 16 * r * r * y * y * y * y * (a * a - 1) + 1 - u * u;
        const int64_t term_a = a + u * u * (u * u - a);
        const int64_t e8  = (term_a * term_a - 1) * (n + 4 * d * y) * (n + 4 * d * y) + 1 - (x + c * u) * (x + c * u);
        const int64_t e9  = (a * a - 1) * l * l + 1 - m * m;
        const int64_t e10 = a * i + k + 1 - l - i;
        const int64_t e11 = p + l * (a - n - 1) + b * (2 * a * (n + 1) - (n + 1) * (n + 1) - 1) - m;
        const int64_t e12 = q + y * (a - p - 1) + s * (2 * a * (p + 1) - (p + 1) * (p + 1) - 1) - x;
        const int64_t e13 = z + p * (a - q - 1) + t * (2 * a * (q + 1) - (q + 1) * (q + 1) - 1) - r;

        const int64_t sum_squares = e1*e1 + e2*e2 + e3*e3 + e4*e4 + e5*e5 + e6*e6 + e7*e7 +
                                    e8*e8 + e9*e9 + e10*e10 + e11*e11 + e12*e12 + e13*e13;

        return (k_val + 2) * (1 - sum_squares);
    }
};

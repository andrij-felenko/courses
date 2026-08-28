#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>

namespace berlekamp {

using Poly = uint64_t;

inline int deg(Poly p) {
    if (p == 0) return -1;
#if defined(__GNUC__) || defined(__clang__)
    return 63 - __builtin_clzll(p);
#else
    int d = 0;
    while (p >>= 1) ++d;
    return d;
#endif
}

inline Poly poly_mod(Poly a, Poly b) {
    int deg_b = deg(b);
    if (deg_b < 0) return 0;
    while (true) {
        int shift = deg(a) - deg_b;
        if (shift < 0) break;
        a ^= (b << shift);
    }
    return a;
}

inline Poly poly_gcd(Poly a, Poly b) {
    while (b > 0) {
        Poly rem = poly_mod(a, b);
        a = b;
        b = rem;
    }
    return a;
}

std::vector<Poly> factor(Poly f) {
    int n = deg(f);
    if (n <= 1) return {f};

    // 1. Формування матриці Берлекампа Q розміру n x n
    std::vector<std::vector<uint8_t>> q_mat(n, std::vector<uint8_t>(n, 0));
    Poly rem = 1;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            q_mat[i][j] = static_cast<uint8_t>((rem >> j) & 1);
        }
        rem = poly_mod(rem << 2, f);
    }

    // 2. Формування матриці M = (Q + I)^T для пошуку лівого ядра
    std::vector<std::vector<uint8_t>> m(n, std::vector<uint8_t>(n, 0));
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            m[i][j] = q_mat[j][i] ^ (i == j ? 1 : 0);
        }
    }

    // 3. Метод виключення Гаусса над полем GF(2)
    std::vector<int> pivot_col_to_row(n, -1);
    int row = 0;
    for (int col = 0; col < n; ++col) {
        int sel = -1;
        for (int r = row; r < n; ++r) {
            if (m[r][col] == 1) { sel = r; break; }
        }
        if (sel == -1) continue;

        std::swap(m[row], m[sel]);
        for (int r = 0; r < n; ++r) {
            if (r != row && m[r][col] == 1) {
                for (int c = col; c < n; ++c) {
                    m[r][c] ^= m[row][c];
                }
            }
        }
        pivot_col_to_row[col] = row++;
    }

    // 4. Побудова базису ядра нуль-простору
    std::vector<Poly> basis;
    for (int col = 0; col < n; ++col) {
        if (pivot_col_to_row[col] == -1) {
            Poly vec = (1ULL << col);
            for (int c = 0; c < n; ++c) {
                int pr = pivot_col_to_row[c];
                if (pr != -1 && m[pr][col] == 1) {
                    vec |= (1ULL << c);
                }
            }
            basis.push_back(vec);
        }
    }

    if (basis.size() == 1) {
        return {f}; // Ядро одновимірне — многочлен незвідний
    }

    // 5. Розщеплення за допомогою першого нетривіального базисного вектора
    Poly v = basis[1];
    Poly g1 = poly_gcd(f, v);
    Poly g2 = poly_gcd(f, v ^ 1ULL);

    std::vector<Poly> result;
    for (Poly g : {g1, g2}) {
        if (deg(g) > 0) {
            auto sub = factor(g);
            result.insert(result.end(), sub.begin(), sub.end());
        }
    }
    return result;
}

} // namespace berlekamp

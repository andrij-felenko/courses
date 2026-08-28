#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Обчислення степеня многочлена над GF(2) через апаратний підрахунок провідних нулів */
static int poly_deg(uint64_t p) {
    if (p == 0) return -1;
#if defined(__GNUC__) || defined(__clang__)
    return 63 - __builtin_clzll(p);
#else
    int d = 0;
    while (p >>= 1) d++;
    return d;
#endif
}

/* Ділення з остачею многочленів над GF(2) */
static uint64_t poly_mod(uint64_t a, uint64_t b) {
    int deg_b = poly_deg(b);
    if (deg_b < 0) return 0;
    while (1) {
        int shift = poly_deg(a) - deg_b;
        if (shift < 0) break;
        a ^= (b << shift);
    }
    return a;
}

/* Найбільший спільний дільник за алгоритмом Евкліда */
static uint64_t poly_gcd(uint64_t a, uint64_t b) {
    while (b > 0) {
        uint64_t rem = poly_mod(a, b);
        a = b;
        b = rem;
    }
    return a;
}

/* Побудова матриці Берлекампа Q розміру n x n */
static void build_q_matrix(uint64_t f, int n, uint8_t q_mat[64][64]) {
    uint64_t rem = 1;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            q_mat[i][j] = (uint8_t)((rem >> j) & 1);
        }
        rem = poly_mod(rem << 2, f);
    }
}

/* Знаходження базису ядра матриці (Q + I)^T методом Гаусса */
static int find_null_space(uint8_t q_mat[64][64], int n, uint64_t basis[64]) {
    uint8_t m[64][64];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            m[i][j] = q_mat[j][i] ^ (i == j ? 1 : 0);
        }
    }

    int pivot_col_to_row[64];
    for (int i = 0; i < n; i++) pivot_col_to_row[i] = -1;

    int row = 0;
    for (int col = 0; col < n; col++) {
        int sel = -1;
        for (int r = row; r < n; r++) {
            if (m[r][col] == 1) { sel = r; break; }
        }
        if (sel == -1) continue;

        for (int c = 0; c < n; c++) {
            uint8_t tmp = m[row][c];
            m[row][c] = m[sel][c];
            m[sel][c] = tmp;
        }

        for (int r = 0; r < n; r++) {
            if (r != row && m[r][col] == 1) {
                for (int c = col; c < n; c++) {
                    m[r][c] ^= m[row][c];
                }
            }
        }
        pivot_col_to_row[col] = row++;
    }

    int basis_count = 0;
    for (int col = 0; col < n; col++) {
        if (pivot_col_to_row[col] == -1) {
            uint64_t vec = (1ULL << col);
            for (int c = 0; c < n; c++) {
                int pr = pivot_col_to_row[c];
                if (pr != -1 && m[pr][col] == 1) {
                    vec |= (1ULL << c);
                }
            }
            basis[basis_count++] = vec;
        }
    }
    return basis_count;
}

// Обернути квадратну k×k матрицю A над GF(256) на місці → inv.
// Повертає 0, якщо A вироджена (для валідних рядків не станеться).
int gf_invert(uint8_t *A, uint8_t *inv, int k) {
    for (int i = 0; i < k * k; i++) inv[i] = 0;          // inv ← одинична
    for (int i = 0; i < k; i++)     inv[i * k + i] = 1;

    for (int col = 0; col < k; col++) {
        int piv = col;                                   // шукаємо ненульовий ведучий
        while (piv < k && A[piv * k + col] == 0) piv++;
        if (piv == k) return 0;                          // вироджена
        if (piv != col)                                  // переставляємо рядки в A та inv
            for (int j = 0; j < k; j++) {
                uint8_t t;
                t = A[col*k+j];   A[col*k+j]   = A[piv*k+j];   A[piv*k+j]   = t;
                t = inv[col*k+j]; inv[col*k+j] = inv[piv*k+j]; inv[piv*k+j] = t;
            }
        uint8_t ip = gf_inv(A[col * k + col]);           // нормуємо ведучий рядок: ділимо на ведучий
        for (int j = 0; j < k; j++) {
            A[col*k+j]   = gf_mul(A[col*k+j],   ip);
            inv[col*k+j] = gf_mul(inv[col*k+j], ip);
        }
        for (int r = 0; r < k; r++) {                    // зануляємо стовпець col у решті рядків
            if (r == col) continue;
            uint8_t f = A[r * k + col];
            if (f == 0) continue;
            for (int j = 0; j < k; j++) {
                A[r*k+j]   ^= gf_mul(f, A[col*k+j]);      // віднімання = XOR
                inv[r*k+j] ^= gf_mul(f, inv[col*k+j]);
            }
        }
    }
    return 1;
}

// recv_idx[0..k-1]: номери k пакетів, що дійшли (дані idx → idx; ремонтний t → k+t).
// recv[0..k-1]:     їхні L-байтові навантаження у тому ж порядку.
// C: матриця Коші m×k. Виходить out[0..k-1] — усі k вихідних пакетів даних.
int rs_decode(const int *recv_idx, const uint8_t *recv[], int k, int m, size_t L,
              const uint8_t *C, uint8_t *out[]) {
    uint8_t *A   = malloc((size_t)k * k);
    uint8_t *inv = malloc((size_t)k * k);

    for (int r = 0; r < k; r++) {                        // рядок G для кожного отриманого пакета
        int idx = recv_idx[r];
        if (idx < k)                                     // дані → одиничний вектор e_idx
            for (int j = 0; j < k; j++) A[r*k+j] = (j == idx) ? 1 : 0;
        else                                             // ремонтний → рядок Коші C[idx-k]
            for (int j = 0; j < k; j++) A[r*k+j] = C[(idx - k) * k + j];
    }
    if (!gf_invert(A, inv, k)) { free(A); free(inv); return 0; }

    for (int j = 0; j < k; j++) {                        // dⱼ = Σᵣ inv[j][r] · recv[r]
        for (size_t b = 0; b < L; b++) out[j][b] = 0;
        for (int r = 0; r < k; r++)
            gf_mul_add(out[j], recv[r], inv[j * k + r], L);
    }
    free(A); free(inv);
    return 1;
}

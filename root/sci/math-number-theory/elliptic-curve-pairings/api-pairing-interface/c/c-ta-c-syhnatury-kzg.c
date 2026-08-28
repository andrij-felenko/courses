// Структура довідкової строки (Structured Reference String, SRS / Trusted Setup)
typedef struct {
    bls12_381_g1_affine_t* g1_powers; // [P1, [s]P1, [s^2]P1, ..., [s^d]P1]
    bls12_381_g2_affine_t g2_s;       // [s]P2
    size_t max_degree;
} kzg_srs_t;

/**
 * @brief Обчислює зобов'язання C = [A(s)]P1 до многочлена A(X).
 * @param[out] out_commitment Точка зобов'язання C у групі G1 (48 байтів стиснуто).
 * @param[in] srs Вказівник на структуровані параметри SRS.
 * @param[in] coeffs Масив коефіцієнтів многочлена (скаляри Fr).
 * @param[in] degree Ступінь многочлена d.
 */
bls12_381_status_t kzg_commit(
    uint8_t out_commitment[48],
    const kzg_srs_t* srs,
    const uint8_t* coeffs,
    size_t degree
);

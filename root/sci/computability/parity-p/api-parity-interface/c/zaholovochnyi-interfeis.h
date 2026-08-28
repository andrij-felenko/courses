#ifndef PARITY_ORACLE_H
#define PARITY_ORACLE_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Непрозорий тип контексту оракула парності */
typedef struct parity_oracle_ctx parity_oracle_ctx_t;

/* Структура щільної/ущільненої бітової матриці над GF(2) */
typedef struct {
    size_t rows;         /* Кількість рядків матриці */
    size_t cols;         /* Кількість стовпчиків матриці */
    size_t stride;       /* Кількість 64-бітних слів у одному рядку */
    uint64_t* data;      /* Ущільнений бітовий масив рядків матриці */
} gf2_matrix_t;

/* Структура представлення булевої формули у КНФ */
typedef struct {
    size_t num_vars;            /* Кількість зміних у формулі (1..n) */
    size_t num_clauses;         /* Кількість диз'юнктів */
    const int32_t* clause_data; /* Буфер літералів (0 розділяє диз'юнкти) */
    size_t clause_data_len;     /* Загальна довжина масиву літералів */
} parity_formula_t;

/* Створення та знищення контексту оракула парності */
parity_status_t parity_oracle_create(parity_oracle_ctx_t** ctx_out, uint32_t flags);
void parity_oracle_destroy(parity_oracle_ctx_t* ctx);

/* Атомарний запит парності кількості розв'язків формули */
parity_status_t parity_oracle_query_sat(parity_oracle_ctx_t* ctx,
                                         const parity_formula_t* formula,
                                         uint8_t* parity_out);

/* Пакетний запит парності для масиву формул (Batch Query) */
parity_status_t parity_oracle_query_batch(parity_oracle_ctx_t* ctx,
                                           const parity_formula_t* formulas,
                                           size_t count,
                                           uint8_t* parities_out);

/* Виділення та звільнення пам'яті для бітової матриці над GF(2) */
parity_status_t gf2_matrix_create(gf2_matrix_t** mat_out, size_t rows, size_t cols);
void gf2_matrix_free(gf2_matrix_t* mat);

/* Запис та зчитування окремих бітів матриці */
parity_status_t gf2_matrix_set_bit(gf2_matrix_t* mat, size_t r, size_t c, bool val);
parity_status_t gf2_matrix_get_bit(const gf2_matrix_t* mat, size_t r, size_t c, bool* val_out);

/* Обчислення рангу бітової матриці методом Гаусса над GF(2) */
parity_status_t gf2_matrix_rank(const gf2_matrix_t* mat, size_t* rank_out);

/* Моделювання зрізу Валіанта–Вазірані: додає m випадкових лінійних рівнянь над GF(2) */
parity_status_t parity_apply_valiant_vazirani(const parity_formula_t* in_formula,
                                               size_t num_linear_eqs,
                                               uint64_t seed,
                                               parity_formula_t** out_formula);

#ifdef __cplusplus
}
#endif

#endif /* PARITY_ORACLE_H */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int64_t coeff;
    uint8_t exponents[8]; // Степені для до 8 змінних
} SparseMonomial;

typedef struct {
    size_t num_vars;
    size_t num_terms;
    SparseMonomial terms[32];
} SparsePoly;

int64_t sparse_poly_eval(const SparsePoly* p, const int64_t* v) {
    int64_t total = 0;
    for (size_t t = 0; t < p->num_terms; ++t) {
        int64_t term_val = p->terms[t].coeff;
        for (size_t i = 0; i < p->num_vars; ++i) {
            uint8_t exp = p->terms[t].exponents[i];
            for (uint8_t e = 0; e < exp; ++e) {
                term_val *= v[i];
            }
        }
        total += term_val;
    }
    return total;
}

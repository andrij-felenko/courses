#ifndef TRS_C_API_H
#define TRS_C_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct trs_term_t trs_term_t;
typedef struct trs_subst_t trs_subst_t;
typedef struct trs_system_t trs_system_t;
typedef struct trs_arena_t trs_arena_t;

// Створення та звільнення пулу пам'яті
trs_arena_t* trs_arena_create(size_t initial_capacity_bytes);
void trs_arena_destroy(trs_arena_t* arena);
void trs_arena_reset(trs_arena_t* arena);

// Створення термів у пам'яті арени
trs_term_t* trs_make_var(trs_arena_t* arena, const char* name);
trs_term_t* trs_make_fn(trs_arena_t* arena, const char* name, uint32_t arity, trs_term_t** args);

// Базові операції
bool trs_terms_equal(const trs_term_t* a, const trs_term_t* b);
bool trs_contains_var(const trs_term_t* term, const char* var_name);
size_t trs_term_size(const trs_term_t* term);
size_t trs_term_depth(const trs_term_t* term);

// Уніфікація та підстановки
trs_subst_t* trs_subst_create(trs_arena_t* arena);
bool trs_unify(const trs_term_t* s, const trs_term_t* t, trs_subst_t* out_subst);
trs_term_t* trs_apply_subst(trs_arena_t* arena, const trs_term_t* term, const trs_subst_t* subst);

// Редукція та поповнення
trs_system_t* trs_system_create(trs_arena_t* arena);
void trs_system_add_rule(trs_system_t* sys, const trs_term_t* lhs, const trs_term_t* rhs);
trs_term_t* trs_normalize(trs_arena_t* arena, const trs_term_t* term, const trs_system_t* sys);

int trs_knuth_bendix(trs_arena_t* arena, trs_system_t* sys, size_t max_iterations);

#ifdef __cplusplus
}
#endif

#endif // TRS_C_API_H

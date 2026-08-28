#ifndef SAT_SOLVER_API_H
#define SAT_SOLVER_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    SAT_RESULT_UNKNOWN = 0,
    SAT_RESULT_SAT     = 10,
    SAT_RESULT_UNSAT   = 20
} sat_result_t;

typedef int var_t;
typedef int lit_t;

typedef struct sat_solver sat_solver_t;

/* Створення та знищення екземпляра солвера */
sat_solver_t* sat_solver_new(void);
void          sat_solver_free(sat_solver_t* s);

/* Додавання змінних та дизюнктів */
var_t         sat_solver_new_var(sat_solver_t* s);
bool          sat_solver_add_clause(sat_solver_t* s, const lit_t* lits, size_t num_lits);

/* Запуск розв'язання */
sat_result_t  sat_solver_solve(sat_solver_t* s);

/* Інкрементне розв'язання з допущеннями (Assumptions) */
sat_result_t  sat_solver_solve_assumptions(sat_solver_t* s, const lit_t* assumptions, size_t num_assumptions);

/* Витяг конфліктного ядра (UNSAT Core) після нездійсненного виклику з допущеннями */
size_t        sat_solver_get_unsat_core(sat_solver_t* s, lit_t* out_core, size_t max_size);

/* Зчитування результатів */
int           sat_solver_get_model_value(sat_solver_t* s, var_t var);

#ifdef __cplusplus
}
#endif

#endif /* SAT_SOLVER_API_H */

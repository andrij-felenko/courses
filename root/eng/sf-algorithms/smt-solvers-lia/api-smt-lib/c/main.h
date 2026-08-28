#ifndef SMT_LIA_API_H
#define SMT_LIA_API_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Непрозорі покажчики на об'єкти сольвера
typedef struct SmtContext_T* SmtContext;
typedef struct SmtSolver_T* SmtSolver;
typedef struct SmtAst_T* SmtAst;
typedef struct SmtSort_T* SmtSort;
typedef struct SmtModel_T* SmtModel;

typedef enum {
    SMT_RES_SAT = 1,
    SMT_RES_UNSAT = -1,
    SMT_RES_UNKNOWN = 0
} SmtResult;

// Керування контекстом та життєвим циклом
SmtContext smt_context_create(void);
void smt_context_free(SmtContext ctx);

SmtSolver smt_solver_create(SmtContext ctx, const char* logic);
void smt_solver_free(SmtSolver solver);

// Створення сортів та констант
SmtSort smt_sort_int(SmtContext ctx);
SmtSort smt_sort_bool(SmtContext ctx);

SmtAst smt_mk_const(SmtContext ctx, const char* name, SmtSort sort);
SmtAst smt_mk_int_num(SmtContext ctx, int64_t val);
SmtAst smt_mk_bool(SmtContext ctx, bool val);

// Арифметичні операції LIA
SmtAst smt_mk_add(SmtContext ctx, SmtAst const* args, uint32_t num_args);
SmtAst smt_mk_sub(SmtContext ctx, SmtAst const* args, uint32_t num_args);
SmtAst smt_mk_mul(SmtContext ctx, SmtAst const_val, SmtAst var); // const_val must be numeral
SmtAst smt_mk_div(SmtContext ctx, SmtAst t1, SmtAst t2);
SmtAst smt_mk_mod(SmtContext ctx, SmtAst t1, SmtAst t2);

// Відношення та логіка
SmtAst smt_mk_le(SmtContext ctx, SmtAst t1, SmtAst t2);
SmtAst smt_mk_lt(SmtContext ctx, SmtAst t1, SmtAst t2);
SmtAst smt_mk_ge(SmtContext ctx, SmtAst t1, SmtAst t2);
SmtAst smt_mk_gt(SmtContext ctx, SmtAst t1, SmtAst t2);
SmtAst smt_mk_eq(SmtContext ctx, SmtAst t1, SmtAst t2);
SmtAst smt_mk_and(SmtContext ctx, SmtAst const* args, uint32_t num_args);
SmtAst smt_mk_or(SmtContext ctx, SmtAst const* args, uint32_t num_args);
SmtAst smt_mk_not(SmtContext ctx, SmtAst arg);

// Керування станом та перевірка
void smt_solver_assert(SmtSolver solver, SmtAst formula);
void smt_solver_push(SmtSolver solver);
void smt_solver_pop(SmtSolver solver, uint32_t levels);
void smt_solver_reset(SmtSolver solver);
void smt_solver_interrupt(SmtSolver solver);

SmtResult smt_solver_check(SmtSolver solver);

// Отримання моделі та контрприкладів
SmtModel smt_solver_get_model(SmtSolver solver);
void smt_model_free(SmtModel model);
bool smt_model_eval_int(SmtModel model, SmtAst ast, int64_t* out_val);

#ifdef __cplusplus
}
#endif

#endif // SMT_LIA_API_H

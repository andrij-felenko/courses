/* Оголошення C99 API для Цейтін-кодера */
#include <stdint.h>
#include <stddef.h>

typedef enum {
    TSEYTIN_OP_VAR     = 0,
    TSEYTIN_OP_NOT     = 1,
    TSEYTIN_OP_AND     = 2,
    TSEYTIN_OP_OR      = 3,
    TSEYTIN_OP_IMPLIES = 4,
    TSEYTIN_OP_XOR     = 5,
    TSEYTIN_OP_EQUIV   = 6
} TseytinOpType;

typedef int32_t TseytinLit;
typedef int32_t TseytinVar;

typedef struct {
    TseytinLit* lits;
    size_t size;
} TseytinClause;

typedef struct {
    TseytinVar max_var;
    TseytinClause* clauses;
    size_t clause_count;
    size_t clause_capacity;
} TseytinContext;

TseytinContext* tseytin_context_create(size_t num_input_vars);
void tseytin_context_free(TseytinContext* ctx);
TseytinVar tseytin_var_fresh(TseytinContext* ctx);

void tseytin_add_clause(TseytinContext* ctx, const TseytinLit* lits, size_t size);
void tseytin_encode_and(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1, TseytinVar in2);
void tseytin_encode_or(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1, TseytinVar in2);
void tseytin_encode_not(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1);
void tseytin_encode_xor(TseytinContext* ctx, TseytinVar out_var, TseytinVar in1, TseytinVar in2);

int tseytin_export_dimacs(const TseytinContext* ctx, TseytinVar root_var, const char* filename);

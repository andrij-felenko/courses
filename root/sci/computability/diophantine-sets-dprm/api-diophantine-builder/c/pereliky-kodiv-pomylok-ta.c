#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

typedef enum {
    DIOPH_OK = 0,
    DIOPH_ERR_OUT_OF_MEMORY = 1,
    DIOPH_ERR_INVALID_ARGUMENT = 2,
    DIOPH_ERR_VARIABLE_NOT_FOUND = 3,
    DIOPH_ERR_DEGREE_OVERFLOW = 4,
    DIOPH_ERR_BUFFER_TOO_SMALL = 5,
    DIOPH_ERR_EVAL_OVERFLOW = 6,
    DIOPH_ERR_PARSE_SYNTAX = 7
} DiophStatus;

typedef enum {
    EXPR_CONST,
    EXPR_VAR,
    EXPR_ADD,
    EXPR_SUB,
    EXPR_MUL,
    EXPR_SQR
} DiophExprType;

typedef enum {
    PRED_EQUAL_ZERO,
    PRED_AND,
    PRED_OR,
    PRED_EXISTS,
    PRED_BOUNDED_FORALL
} DiophPredType;

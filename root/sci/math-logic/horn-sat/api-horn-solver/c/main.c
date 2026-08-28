typedef int32_t HornVar;
typedef int32_t HornClauseId;

#define HORN_VAR_NONE ((HornVar)-1)

typedef enum {
    HORN_OK = 0,
    HORN_RESULT_SAT = 1,
    HORN_RESULT_UNSAT = 2,
    HORN_ERR_NULL_POINTER = -1,
    HORN_ERR_INVALID_VAR = -2,
    HORN_ERR_INVALID_STATE = -3,
    HORN_ERR_OUT_OF_MEMORY = -4,
    HORN_ERR_DUPLICATE_LITERAL = -5
} HornErrorCode;

typedef struct HornSolverC HornSolverC;

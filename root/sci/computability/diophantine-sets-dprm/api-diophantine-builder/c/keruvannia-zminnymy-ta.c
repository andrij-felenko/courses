typedef struct DiophExpr DiophExpr;
typedef struct DiophPred DiophPred;

struct DiophExpr {
    DiophExprType type;
    union {
        int64_t const_val;
        uint32_t var_id;
        struct {
            const DiophExpr* lhs;
            const DiophExpr* rhs;
        } binary;
        const DiophExpr* unary_sqr;
    } as;
};

struct DiophPred {
    DiophPredType type;
    union {
        const DiophExpr* eq_zero_expr;
        struct {
            const DiophPred* lhs;
            const DiophPred* rhs;
        } binary;
        struct {
            uint32_t var_id;
            const DiophPred* body;
        } exists;
        struct {
            uint32_t var_id;
            const DiophExpr* limit;
            const DiophPred* body;
        } bounded_forall;
    } as;
};

typedef struct {
    char name[32];
    uint32_t id;
    bool is_existential;
} DiophVar;

typedef struct {
    uint8_t* memory_pool;
    size_t pool_size;
    size_t allocated_bytes;
    DiophVar variables[128];
    size_t var_count;
    DiophStatus last_error;
} DiophContext;

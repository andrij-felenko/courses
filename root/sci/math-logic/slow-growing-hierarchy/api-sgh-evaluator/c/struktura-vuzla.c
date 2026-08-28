typedef struct OrdinalNode OrdinalNode;

struct OrdinalNode {
    OrdinalKind kind;
    union {
        uint64_t constant;
        struct {
            OrdinalNode *exponent;
            uint64_t coefficient;
        } omega_term;
        struct {
            OrdinalNode **terms;
            size_t count;
            size_t capacity;
        } sum;
        struct {
            OrdinalNode *inner;
        } collapse;
    } as;
};

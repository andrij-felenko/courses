typedef struct {
    cyk_symbol_t lhs;
    cyk_symbol_t rhs1;
    cyk_symbol_t rhs2;
    float log_probability; /* Логарифм ймовірності log P(A -> BC) */
} cyk_prob_binary_rule_t;

typedef struct {
    cyk_symbol_t lhs;
    cyk_symbol_t terminal;
    float log_probability; /* Логарифм ймовірності log P(A -> a) */
} cyk_prob_terminal_rule_t;

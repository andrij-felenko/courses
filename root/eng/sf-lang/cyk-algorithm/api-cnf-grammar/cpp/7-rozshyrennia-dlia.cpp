struct ProbBinaryRule {
    cyk_symbol_t lhs;
    cyk_symbol_t rhs1;
    cyk_symbol_t rhs2;
    float log_probability;
};

struct ProbTerminalRule {
    cyk_symbol_t lhs;
    cyk_symbol_t terminal;
    float log_probability;
};

struct BinaryRule {
    cyk_symbol_t lhs;
    cyk_symbol_t rhs1;
    cyk_symbol_t rhs2;
};

struct TerminalRule {
    cyk_symbol_t lhs;
    cyk_symbol_t terminal;
};

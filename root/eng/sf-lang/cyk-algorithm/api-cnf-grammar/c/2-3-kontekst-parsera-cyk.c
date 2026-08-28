typedef struct {
    cyk_symbol_t start_symbol;
    const cyk_binary_rule_t* binary_rules;
    size_t num_binary_rules;
    const cyk_terminal_rule_t* terminal_rules;
    size_t num_terminal_rules;
    
    /* Зворотний індекс пар: lookup[B * max_symbols + C] -> список правил */
    uint32_t* pair_index_offsets;
    cyk_symbol_t* pair_index_rules;
    size_t max_nonterminals;
} cyk_context_t;

typedef struct {
    cyk_symbol_t lhs;   /* Ліва частина: нетермінал A */
    cyk_symbol_t rhs1;  /* Права частина: перший нетермінал B */
    cyk_symbol_t rhs2;  /* Права частина: другий нетермінал C */
} cyk_binary_rule_t;

typedef struct {
    cyk_symbol_t lhs;       /* Ліва частина: нетермінал A */
    cyk_symbol_t terminal;  /* Права частина: термінальний символ a */
} cyk_terminal_rule_t;

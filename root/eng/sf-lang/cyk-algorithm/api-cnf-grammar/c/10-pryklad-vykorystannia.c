/* Приклад компіляції граматики та розбору послідовності токенів */
cyk_context_t* ctx = NULL;
cyk_binary_rule_t bin_rules[] = {
    { 0, 1, 2 }, /* S -> A B */
    { 1, 2, 1 }  /* A -> B A */
};
cyk_terminal_rule_t term_rules[] = {
    { 1, 100 },  /* A -> 'a' */
    { 2, 101 }   /* B -> 'b' */
};

cyk_status_t status = cyk_context_create(0, bin_rules, 2, term_rules, 2, &ctx);
if (status == CYK_STATUS_OK) {
    cyk_symbol_t input_tokens[] = { 101, 100 }; /* "ba" */
    bool accepted = false;
    cyk_tree_node_t* tree = NULL;
    
    if (cyk_parse_tokens(ctx, input_tokens, 2, &accepted, &tree) == CYK_STATUS_OK) {
        if (accepted) {
            /* Обробка синтаксичного дерева */
            cyk_tree_free(tree);
        }
    }
    cyk_context_destroy(ctx);
}

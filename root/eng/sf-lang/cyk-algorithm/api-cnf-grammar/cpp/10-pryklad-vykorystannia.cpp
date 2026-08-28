/* Приклад на C++20 із безпечним керуванням пам'яттю */
std::vector<BinaryRule> bin_rules = {
    { 0, 1, 2 },
    { 1, 2, 1 }
};
std::vector<TerminalRule> term_rules = {
    { 1, 100 },
    { 2, 101 }
};

auto ctx_res = make_grammar_context(0, bin_rules, term_rules);
if (ctx_res.has_value()) {
    std::vector<cyk_symbol_t> input_tokens = { 101, 100 };
    auto parse_res = parse_tokens(*ctx_res.value(), input_tokens);
    if (parse_res.has_value() && parse_res.value().accepted) {
        /* Обробка синтаксичного дерева: parse_res.value().tree */
    }
}

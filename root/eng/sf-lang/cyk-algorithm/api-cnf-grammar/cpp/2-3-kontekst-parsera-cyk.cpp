#include <vector>
#include <span>

class GrammarContext {
public:
    cyk_symbol_t start_symbol;
    std::vector<BinaryRule> binary_rules;
    std::vector<TerminalRule> terminal_rules;
    std::vector<uint32_t> pair_index_offsets;
    std::vector<cyk_symbol_t> pair_index_rules;
    size_t max_nonterminals = 0;
};

#include <optional>
#include <span>

struct ParseResult {
    bool accepted = false;
    std::unique_ptr<TreeNode> tree = nullptr;
};

std::expected<ParseResult, cyk_status_t> parse_tokens(
    const GrammarContext& ctx,
    std::span<const cyk_symbol_t> tokens,
    bool build_tree = true
);

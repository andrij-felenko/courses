#include <memory>
#include <optional>

struct TreeNode {
    cyk_symbol_t symbol;
    std::optional<cyk_symbol_t> terminal_value;
    size_t span_start;
    size_t span_length;
    std::unique_ptr<TreeNode> left_child;
    std::unique_ptr<TreeNode> right_child;
};

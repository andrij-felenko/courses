#include <generator>
#include <ranges>
#include <string>

struct TreeNode {
    std::string value;
    std::vector<TreeNode> children;
};

std::generator<const std::string&> traverse_tree(const TreeNode& node) {
    co_yield node.value;
    for (const auto& child : node.children) {
        // Делегування генерації вкладеному піддереву
        co_yield std::ranges::elements_of(traverse_tree(child));
    }
}

#include <generator>
#include <ranges>

// Оптимізований рекурсивний обхід дерев C++23 (O(1) оверхед на елемент)
std::generator<int> traverse_tree_optimal(const TreeNode* node) {
    if (!node) co_return;

    // 1. Рекурсивне делегування лівого піддерева напряму
    if (node->left) {
        co_yield std::ranges::elements_of(traverse_tree_optimal(node->left));
    }

    // 2. Віддача власних даних
    co_yield node->value;

    // 3. Рекурсивне делегування правого піддерева
    if (node->right) {
        co_yield std::ranges::elements_of(traverse_tree_optimal(node->right));
    }
}

struct TreeNode {
    int value;
    TreeNode* left{nullptr};
    TreeNode* right{nullptr};
};

// Традиційний рекурсивний корутинний обхід (ПРОБЛЕМА ПРОДУКТИВНОСТІ!)
std::generator<int> traverse_eager_yield(const TreeNode* node) {
    if (!node) co_return;

    // Рекурсивний обхід лівого піддерева
    if (node->left) {
        for (int val : traverse_eager_yield(node->left)) {
            co_yield val; // КВАДРАТИЧНИЙ ОВЕРХЕД!
        }
    }

    co_yield node->value;

    // Рекурсивний обхід правого піддерева
    if (node->right) {
        for (int val : traverse_eager_yield(node->right)) {
            co_yield val;
        }
    }
}

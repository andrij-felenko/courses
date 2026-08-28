// Порівневий обхід у C++ з поверненням вектора рівнів
std::vector<std::vector<int>> level_order(const TreeNode* root) {
    std::vector<std::vector<int>> result;
    if (!root) return result;

    std::queue<const TreeNode*> q;
    q.push(root);

    while (!q.empty()) {
        size_t level_size = q.size();
        std::vector<int> current_level;
        current_level.reserve(level_size);

        for (size_t i = 0; i < level_size; ++i) {
            const TreeNode* node = q.front();
            q.pop();
            current_level.push_back(node->data);

            if (node->left)  q.push(node->left.get());
            if (node->right) q.push(node->right.get());
        }
        result.push_back(std::move(current_level));
    }
    return result;
}

// Обчислення кількості вузлів
int count_nodes(const TreeNode* root) {
    if (!root) return 0;
    return 1 + count_nodes(root->left.get()) + count_nodes(root->right.get());
}

// Обчислення висоти дерева (порожнє дерево = -1, корінь = 0)
int tree_height(const TreeNode* root) {
    if (!root) return -1;
    return 1 + std::max(tree_height(root->left.get()), 
                        tree_height(root->right.get()));
}

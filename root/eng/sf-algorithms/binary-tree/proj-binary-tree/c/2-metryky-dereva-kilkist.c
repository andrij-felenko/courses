// Обчислення кількості вузлів
int count_nodes(const Node* root) {
    if (root == NULL) return 0;
    return 1 + count_nodes(root->left) + count_nodes(root->right);
}

// Обчислення висоти дерева (порожнє дерево = -1, корінь = 0)
int tree_height(const Node* root) {
    if (root == NULL) return -1;
    int left_h = tree_height(root->left);
    int right_h = tree_height(root->right);
    return 1 + (left_h > right_h ? left_h : right_h);
}

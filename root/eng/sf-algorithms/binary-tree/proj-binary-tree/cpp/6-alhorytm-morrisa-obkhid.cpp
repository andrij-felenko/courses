// Обхід Морріса (Morris In-order Traversal) мовою C++
std::vector<int> morris_inorder(TreeNode* root) {
    std::vector<int> result;
    TreeNode* current = root;

    while (current != nullptr) {
        if (!current->left) {
            result.push_back(current->data);
            current = current->right.get();
        } else {
            // Знаходимо попередника
            TreeNode* predecessor = current->left.get();
            while (predecessor->right && predecessor->right.get() != current) {
                predecessor = predecessor->right.get();
            }

            if (!predecessor->right) {
                // Створюємо тимчасовий місток
                predecessor->right.reset(current);
                current = current->left.get();
            } else {
                // Знімаємо місток
                predecessor->right.release();
                result.push_back(current->data);
                current = current->right.get();
            }
        }
    }
    return result;
}

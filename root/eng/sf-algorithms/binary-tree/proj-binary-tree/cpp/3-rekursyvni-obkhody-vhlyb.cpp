// Збирання елементів серединного обходу (In-order) у вектор
void collect_inorder(const TreeNode* root, std::vector<int>& result) {
    if (!root) return;
    collect_inorder(root->left.get(), result);
    result.push_back(root->data);
    collect_inorder(root->right.get(), result);
}

// Збирання елементів прямого обходу (Pre-order) у вектор
void collect_preorder(const TreeNode* root, std::vector<int>& result) {
    if (!root) return;
    result.push_back(root->data);
    collect_preorder(root->left.get(), result);
    collect_preorder(root->right.get(), result);
}

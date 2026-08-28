// Інвертування двійкового дерева у C++
std::unique_ptr<TreeNode> invert_tree(std::unique_ptr<TreeNode> root) {
    if (!root) return nullptr;

    auto temp = std::move(root->left);
    root->left = invert_tree(std::move(root->right));
    root->right = invert_tree(std::move(temp));

    return root;
}

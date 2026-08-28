// Перевірка симетрії двійкового дерева у C++
bool is_mirror(const TreeNode* t1, const TreeNode* t2) {
    if (!t1 && !t2) return true;
    if (!t1 || !t2) return false;
    return (t1->data == t2->data) &&
           is_mirror(t1->left.get(), t2->right.get()) &&
           is_mirror(t1->right.get(), t2->left.get());
}

bool is_symmetric(const TreeNode* root) {
    if (!root) return true;
    return is_mirror(root->left.get(), root->right.get());
}

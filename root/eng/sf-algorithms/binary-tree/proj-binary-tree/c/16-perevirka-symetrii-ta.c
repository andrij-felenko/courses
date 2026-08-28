// Перевірка, чи є два піддерева дзеркально симетричними на C
bool is_mirror(const Node* t1, const Node* t2) {
    if (t1 == NULL && t2 == NULL) return true;
    if (t1 == NULL || t2 == NULL) return false;
    return (t1->data == t2->data) &&
           is_mirror(t1->left, t2->right) &&
           is_mirror(t1->right, t2->left);
}

bool is_symmetric(const Node* root) {
    if (root == NULL) return true;
    return is_mirror(root->left, root->right);
}

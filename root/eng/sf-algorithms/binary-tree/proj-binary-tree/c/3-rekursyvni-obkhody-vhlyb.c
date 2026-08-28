// Прямий обхід (Pre-order): Корінь -> Ліве -> Праве
void print_preorder(const Node* root) {
    if (root == NULL) return;
    printf("%d ", root->data);
    print_preorder(root->left);
    print_preorder(root->right);
}

// Серединний обхід (In-order): Ліве -> Корінь -> Праве
void print_inorder(const Node* root) {
    if (root == NULL) return;
    print_inorder(root->left);
    printf("%d ", root->data);
    print_inorder(root->right);
}

// Зворотний обхід (Post-order): Ліве -> Праве -> Корінь
void print_postorder(const Node* root) {
    if (root == NULL) return;
    print_postorder(root->left);
    print_postorder(root->right);
    printf("%d ", root->data);
}

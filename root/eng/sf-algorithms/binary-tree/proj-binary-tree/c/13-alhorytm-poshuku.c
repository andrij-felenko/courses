// Пошук найменшого спільного предка (LCA) мовою C
Node* lowest_common_ancestor(Node* root, Node* p, Node* q) {
    if (root == NULL || root == p || root == q) {
        return root;
    }

    Node* left_lca = lowest_common_ancestor(root->left, p, q);
    Node* right_lca = lowest_common_ancestor(root->right, p, q);

    if (left_lca != NULL && right_lca != NULL) {
        return root;  // Обидва вузли знайдені у різних гілках
    }

    return (left_lca != NULL) ? left_lca : right_lca;
}

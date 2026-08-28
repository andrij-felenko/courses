// Інвертування двійкового дерева на C
Node* invert_tree(Node* root) {
    if (root == NULL) return NULL;

    Node* temp = root->left;
    root->left = invert_tree(root->right);
    root->right = invert_tree(temp);

    return root;
}

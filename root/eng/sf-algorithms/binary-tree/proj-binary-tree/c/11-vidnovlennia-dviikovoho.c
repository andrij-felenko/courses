// Пошук індексу елемента в масиві In-order
int find_index(const int* arr, int start, int end, int val) {
    for (int i = start; i <= end; ++i) {
        if (arr[i] == val) return i;
    }
    return -1;
}

// Рекурсивна відбудова дерева на C
Node* build_tree_helper(const int* preorder, const int* inorder, 
                        int in_start, int in_end, int* pre_idx) 
{
    if (in_start > in_end) return NULL;

    int root_val = preorder[(*pre_idx)++];
    Node* root = create_node(root_val);

    if (in_start == in_end) return root;

    int in_idx = find_index(inorder, in_start, in_end, root_val);

    root->left = build_tree_helper(preorder, inorder, in_start, in_idx - 1, pre_idx);
    root->right = build_tree_helper(preorder, inorder, in_idx + 1, in_end, pre_idx);

    return root;
}

Node* build_tree_from_traversals(const int* preorder, const int* inorder, int size) {
    int pre_idx = 0;
    return build_tree_helper(preorder, inorder, 0, size - 1, &pre_idx);
}

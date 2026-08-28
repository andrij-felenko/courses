int main(void) {
    // Побудова тестового дерева:
    //         1
    //       /   \
    //      2     3
    //     / \
    //    4   5
    Node* root = create_node(1);
    root->left = create_node(2);
    root->right = create_node(3);
    root->left->left = create_node(4);
    root->left->right = create_node(5);

    printf("Кількість вузлів: %d\n", count_nodes(root));
    printf("Висота дерева: %d\n", tree_height(root));

    printf("Pre-order: ");
    print_preorder(root);
    printf("\n");

    printf("In-order (рекурсія):  ");
    print_inorder(root);
    printf("\n");

    printf("In-order (ітеративно): ");
    inorder_iterative(root);
    printf("\n");

    printf("In-order (Морріс):    ");
    morris_inorder(root);
    printf("\n");

    printf("Level-order: ");
    print_level_order(root);
    printf("\n");

    Node* lca = lowest_common_ancestor(root, root->left->left, root->left->right);
    printf("LCA вузлів 4 та 5: %d\n", lca ? lca->data : -1);

    // Обов'язкове звільнення пам'яті!
    destroy_tree(root);
    return 0;
}

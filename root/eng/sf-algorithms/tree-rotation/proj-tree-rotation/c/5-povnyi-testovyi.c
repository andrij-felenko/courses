void print_inorder_tree(const Node* node) {
    if (!node) return;
    print_inorder_tree(node->left);
    printf("Ключ: %2d | Висота: %d | BF: %2d\n", 
           node->key, node->height, get_balance_factor(node));
    print_inorder_tree(node->right);
}

void free_tree_nodes(Node* node) {
    if (!node) return;
    free_tree_nodes(node->left);
    free_tree_nodes(node->right);
    free(node);
}

int main(void) {
    Node* root = NULL;
    int keys[] = {10, 20, 30, 40, 50, 25};
    size_t num_keys = sizeof(keys) / sizeof(keys[0]);

    printf("--- Послідовна вставка елементів 10, 20, 30, 40, 50, 25 ---\n");
    for (size_t i = 0; i < num_keys; ++i) {
        root = insert_avl(root, keys[i], NULL, &root);
    }

    printf("\nПідсумковий центровий обхід дерева:\n");
    print_inorder_tree(root);

    printf("\nКорінь дерева: %d (висота %d)\n", root->key, root->height);
    assert(root->key == 30 && "Корінь мусить бути 30 після балансування");
    assert(root->height == 3 && "Висота збалансованого дерева повинна дорівнювати 3");

    printf("\nТест пройдено успішно: баланс відновлено повертаннями!\n");
    free_tree_nodes(root);
    return 0;
}

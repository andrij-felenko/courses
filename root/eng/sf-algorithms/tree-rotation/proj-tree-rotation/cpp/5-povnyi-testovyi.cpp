template <typename T>
void print_inorder_tree(const Node<T>* node) {
    if (!node) return;
    print_inorder_tree(node->left);
    std::cout << "Ключ: " << node->key << " | Висота: " << node->height 
              << " | BF: " << get_balance_factor(node) << "\n";
    print_inorder_tree(node->right);
}

template <typename T>
void free_tree_nodes(Node<T>* node) {
    if (!node) return;
    free_tree_nodes(node->left);
    free_tree_nodes(node->right);
    delete node;
}

int main() {
    Node<int>* root = nullptr;
    int keys[] = {10, 20, 30, 40, 50, 25};

    std::cout << "--- Послідовна вставка елементів 10, 20, 30, 40, 50, 25 ---\n";
    for (int k : keys) {
        root = insert_avl(root, k, nullptr, root);
    }

    std::cout << "\nПідсумковий центровий обхід дерева:\n";
    print_inorder_tree(root);

    std::cout << "\nКорінь дерева: " << root->key << " (висота " << root->height << ")\n";
    assert(root->key == 30 && "Корінь мусить бути 30 після балансування");
    assert(root->height == 3 && "Висота збалансованого дерева повинна дорівнювати 3");

    std::cout << "\nТест пройдено успішно: баланс відновлено повертаннями!\n";
    free_tree_nodes(root);
    return 0;
}

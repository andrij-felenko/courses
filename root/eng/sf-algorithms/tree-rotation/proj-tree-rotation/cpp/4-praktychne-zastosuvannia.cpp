template <typename T>
Node<T>* rebalance(Node<T>* node, Node<T>*& root) noexcept {
    if (!node) return nullptr;

    update_height(node);
    int bf = get_balance_factor(node);

    // Лівоважка конфігурація
    if (bf <= -2) {
        if (get_balance_factor(node->left) <= 0) {
            return rotate_right(node, root); // LL
        } else {
            return rotate_left_right(node, root); // LR
        }
    }

    // Правоважка конфігурація
    if (bf >= 2) {
        if (get_balance_factor(node->right) >= 0) {
            return rotate_left(node, root); // RR
        } else {
            return rotate_right_left(node, root); // RL
        }
    }

    return node;
}

template <typename T>
Node<T>* insert_avl(Node<T>* node, T key, Node<T>* parent, Node<T>*& root) {
    if (!node) {
        auto* new_node = new Node<T>(std::move(key));
        new_node->parent = parent;
        return new_node;
    }

    if (key < node->key) {
        node->left = insert_avl(node->left, key, node, root);
    } else if (key > node->key) {
        node->right = insert_avl(node->right, key, node, root);
    } else {
        return node;
    }

    return rebalance(node, root);
}

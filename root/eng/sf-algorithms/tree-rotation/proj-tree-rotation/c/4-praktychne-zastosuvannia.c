/* Автоматична підтримка балансу AVL-вузла повертаннями */
Node* rebalance(Node* node, Node** root) {
    if (!node) return NULL;

    update_height(node);
    int bf = get_balance_factor(node);

    /* Лівоважка конфігурація (BF <= -2) */
    if (bf <= -2) {
        if (get_balance_factor(node->left) <= 0) {
            /* Поодинокий правий поворот (LL) */
            return rotate_right(node, root);
        } else {
            /* Подвійний Left-Right поворот (LR) */
            return rotate_left_right(node, root);
        }
    }

    /* Правоважка конфігурація (BF >= +2) */
    if (bf >= 2) {
        if (get_balance_factor(node->right) >= 0) {
            /* Поодинокий лівий поворот (RR) */
            return rotate_left(node, root);
        } else {
            /* Подвійний Right-Left поворот (RL) */
            return rotate_right_left(node, root);
        }
    }

    return node; /* Дерево збалансоване */
}

/* Рекурсивна вставка вузла в AVL-дерево */
Node* insert_avl(Node* node, int key, Node* parent, Node** root) {
    if (node == NULL) {
        Node* new_node = create_node(key);
        if (new_node) new_node->parent = parent;
        return new_node;
    }

    if (key < node->key) {
        node->left = insert_avl(node->left, key, node, root);
    } else if (key > node->key) {
        node->right = insert_avl(node->right, key, node, root);
    } else {
        return node; /* Дублікати не вставляються */
    }

    return rebalance(node, root);
}

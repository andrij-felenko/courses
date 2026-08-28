std::unique_ptr<IntervalNode> remove_rec(std::unique_ptr<IntervalNode> node, Interval target) {
    if (!node) return nullptr;

    if (target.low < node->interval.low) {
        node->left = remove_rec(std::move(node->left), target);
    } else if (target.low > node->interval.low || target.high != node->interval.high) {
        node->right = remove_rec(std::move(node->right), target);
    } else {
        // Знайдено цільовий вузол для видалення
        if (!node->left) return std::move(node->right);
        if (!node->right) return std::move(node->left);

        // Вузол має обох дітей: шукаємо мінімум у правому піддереві
        IntervalNode* min_right = node->right.get();
        while (min_right->left) {
            min_right = min_right->left.get();
        }

        // Копіюємо дані наступника
        node->interval = min_right->interval;

        // Рекурсивно видаляємо наступника з правого піддерева
        node->right = remove_rec(std::move(node->right), min_right->interval);
    }

    node->update_max();
    return node;
}
